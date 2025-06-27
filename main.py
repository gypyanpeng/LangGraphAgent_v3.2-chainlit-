# main.py
"""
LangGraph Agent 主程序 - 严格按照 LangGraph 官方标准实现持久化

参考 WoodenFish 项目的简洁实现方式，完全符合官方标准
"""

import asyncio
import json
import os
import uuid
from typing import Dict, Any, Optional

# 禁用 LangSmith 追踪以避免 TracerException 错误
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
# 额外禁用其他追踪相关环境变量
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["LANGSMITH_TRACING"] = "false"

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# 从我们的模块中导入加载函数
from llm_loader import load_llm_from_config
from mcp_loader import load_mcp_tools_from_config

# 导入持久化模块 - 严格按照 LangGraph 官方标准
import aiosqlite
try:
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    SQLITE_AVAILABLE = True
    print("✅ AsyncSQLite checkpointer 可用")
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver
    SQLITE_AVAILABLE = False
    print("⚠️ AsyncSQLite checkpointer 不可用，将使用内存存储")




# 配置加载函数
def load_persistence_config(config_path: str = "persistence_config.json") -> Dict[str, Any]:
    """加载持久化配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 成功加载持久化配置: {config_path}")
        return config
    except FileNotFoundError:
        print(f"⚠️ 配置文件 {config_path} 不存在，使用默认配置")
        return {
            "persistence": {
                "enabled": True,
                "backend": "sqlite",
                "config": {
                    "sqlite": {
                        "database_path": "./data/agent_memory.db"
                    }
                }
            }
        }
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}，使用默认配置")
        return {
            "persistence": {
                "enabled": True,
                "backend": "sqlite",
                "config": {
                    "sqlite": {
                        "database_path": "./data/agent_memory.db"
                    }
                }
            }
        }


# 使用官方推荐的 MessagesState
class AgentState(MessagesState):
    """使用官方的 MessagesState，包含 messages 字段"""
    pass


async def create_checkpointer(config: Optional[Dict[str, Any]] = None):
    """创建检查点存储器 - 按照 LangGraph 官方标准实现"""
    if config is None:
        config = load_persistence_config()

    persistence_config = config.get("persistence", {})

    if not persistence_config.get("enabled", True):
        print("📝 持久化已禁用，使用内存存储器")
        return MemorySaver()

    backend = persistence_config.get("backend", "sqlite")
    backend_config = persistence_config.get("config", {})

    if backend == "sqlite" and SQLITE_AVAILABLE:
        # 从配置获取数据库路径
        db_path = backend_config.get("database_path", "./data/agent_memory.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        print(f"📝 使用 AsyncSQLite 检查点存储器: {db_path}")
        # 直接创建 AsyncSqliteSaver 实例
        conn = await aiosqlite.connect(db_path)
        checkpointer = AsyncSqliteSaver(conn)
        return checkpointer
    elif backend == "memory":
        print("📝 使用内存检查点存储器")
        return MemorySaver()
    else:
        print(f"⚠️ 不支持的后端 '{backend}' 或 SQLite 不可用，使用内存存储器")
        return MemorySaver()


class SimpleSessionManager:
    """简单的会话管理器 - 符合 LangGraph 官方标准"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        session_config = self.config.get("session_management", {})

        self.current_thread_id = None
        self.current_user_id = None
        self.default_user_id = session_config.get("default_user_prefix", "default_user")
        self.session_timeout_hours = session_config.get("session_timeout_hours", 24)
        self.max_sessions_per_user = session_config.get("max_sessions_per_user", 10)
        self.auto_cleanup_enabled = session_config.get("auto_cleanup_enabled", True)

    def create_session(self, user_id: Optional[str] = None):
        """创建新会话 - 支持 user_id 和 thread_id"""
        if user_id is None:
            user_id = self.default_user_id

        thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        self.current_thread_id = thread_id
        self.current_user_id = user_id

        print(f"🆕 创建新会话: {thread_id}")
        return thread_id

    def get_session_config(self, thread_id: str, user_id: Optional[str] = None):
        """获取 LangGraph 标准的会话配置 - 支持 user_id"""
        config = {"configurable": {"thread_id": thread_id}}

        # 如果提供了 user_id，添加到配置中（用于跨线程持久化）
        if user_id:
            config["configurable"]["user_id"] = user_id
        elif self.current_user_id:
            config["configurable"]["user_id"] = self.current_user_id

        return config

    def clear_current_session(self):
        """清除当前会话，创建新会话"""
        return self.create_session(self.current_user_id)

    def get_current_config(self):
        """获取当前会话的配置"""
        if self.current_thread_id:
            return self.get_session_config(self.current_thread_id, self.current_user_id)
        return None

    def resume_session(self, thread_id: str):
        """恢复到指定的会话"""
        self.current_thread_id = thread_id
        # 从 thread_id 中提取 user_id（如果遵循 user_id_xxxxxxxx 格式）
        if '_' in thread_id:
            self.current_user_id = thread_id.split('_')[0]
        print(f"🔄 恢复会话: {thread_id}")
        return thread_id


async def initialize_agent():
    """初始化Agent组件并构建工作流 - 简化版持久化功能"""
    print("--- 初始化Agent (带持久化功能) ---")

    # 加载持久化配置
    persistence_config = load_persistence_config("config/persistence_config.json")

    # 创建检查点存储器 - 参考 WoodenFish 项目
    checkpointer = await create_checkpointer(persistence_config)

    # 创建简单的会话管理器
    session_manager = SimpleSessionManager(persistence_config)

    # 自动使用配置文件中指定的默认提供商
    llm = load_llm_from_config("config/llm_config.json")
    _, tools = await load_mcp_tools_from_config("config/mcp_config.json")

    # 将工具绑定到LLM，这样LLM就知道可以使用哪些工具
    llm_with_tools = llm.bind_tools(tools)

    # 定义节点函数
    def call_model(state: AgentState):
        """调用模型节点 - 严格按照 LangGraph 官方标准"""
        messages = state["messages"]

        try:
            response = llm_with_tools.invoke(messages)

            # 确保响应不为空
            if not response.content and not (hasattr(response, 'tool_calls') and response.tool_calls):
                # 如果响应为空，创建一个默认响应
                from langchain_core.messages import AIMessage
                response = AIMessage(content="抱歉，我无法处理这个请求。请重新尝试。")

            return {"messages": [response]}
        except Exception as e:
            print(f"⚠️ 模型调用出错: {e}")
            from langchain_core.messages import AIMessage
            error_response = AIMessage(content=f"抱歉，处理请求时出现错误: {str(e)}")
            return {"messages": [error_response]}

    # 创建工具节点
    tool_node = ToolNode(tools)

    def should_continue(state: AgentState):
        """判断是否继续执行 - 严格按照 LangGraph 官方标准"""
        messages = state["messages"]
        last_message = messages[-1]

        # 严格检查 AIMessage 类型和 tool_calls
        from langchain_core.messages import AIMessage
        if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return END

    # --- 构建图 ---
    print("\n--- 构建LangGraph工作流 ---")
    workflow = StateGraph(AgentState)

    # 添加节点（标准的 LangGraph 模式）
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # 设置入口点
    workflow.set_entry_point("agent")

    # 添加条件边（官方标准做法）
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        ["tools", END]  # 官方推荐的简化写法
    )

    # 添加从工具节点返回到Agent节点的边
    workflow.add_edge("tools", "agent")

    # 关键修改：编译图时集成检查点 - 严格按照 LangGraph 官方标准（参考 WoodenFish）
    app = workflow.compile(checkpointer=checkpointer)
    print("--- 工作流构建完成 (已集成持久化) ---")
    
    # 显示持久化信息
    print(f"📝 检查点存储: {type(checkpointer).__name__}")

    return app, tools, session_manager


async def run_agent_with_persistence(app, query, session_manager, thread_id):
    """带持久化功能的Agent运行函数"""
    print(f"\n🚀 开始处理查询: '{query}' (会话: {thread_id})")
    inputs = {"messages": [HumanMessage(content=query)]}
    
    # 获取 LangGraph 标准的会话配置
    config = session_manager.get_session_config(thread_id)

    # 使用 stream 方法可以实时看到每一步的输出
    try:
        # 关键修改：传入 config 参数以启用持久化
        async for output in app.astream(inputs, config=config, stream_mode="values"):
            print(f"\n--- 状态更新 ---")
            messages = output["messages"]
            last_message = messages[-1]

            # 清楚显示消息类型和内容
            msg_type = type(last_message).__name__
            print(f"📨 新消息类型: {msg_type}")

            if isinstance(last_message, HumanMessage):
                print(f"👤 用户: {last_message.content}")
            elif isinstance(last_message, AIMessage):
                if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                    print(f"🤖 AI -> 调用工具: {[tc['name'] for tc in last_message.tool_calls]}")
                    for tc in last_message.tool_calls:
                        print(f"   工具: {tc['name']}, 参数: {tc['args']}")
                else:
                    print(f"🤖 AI -> 最终回复:\n{last_message.content}")
            elif isinstance(last_message, ToolMessage):
                print(f"🔧 工具 {last_message.name} -> 结果: {last_message.content[:100]}...")
        
    except Exception as e:
        print(f"\n💥 Agent执行出错: {e}")
        import traceback
        traceback.print_exc()


def show_welcome(tools=None):
    """显示欢迎信息"""
    print("\n🤖 LangGraph Agent 交互式助手 (持久化版本)")
    print("=" * 60)
    print("✅ 对话历史将自动保存")
    print("✅ 程序重启后可以继续之前的对话")
    
    if tools:
        print(f"🛠️  已加载 {len(tools)} 个工具")
    
    print("\n📋 可用命令:")
    print("  • 'new' - 开始新对话")
    print("  • 'resume <thread_id>' - 恢复到指定会话")
    print("  • 'history' - 查看对话历史")
    print("  • 'help' - 查看帮助")
    print("  • 'tools' - 查看可用工具")
    print("  • 'clear' - 清屏")
    print("  • 'quit' 或 'exit' - 退出程序")


def show_help(tools=None):
    """显示帮助信息"""
    print("\n📖 帮助信息:")
    print("这是一个基于 LangGraph 的智能助手，具有以下特性：")
    print("• 🧠 智能对话：支持复杂的多轮对话")
    print("• 🛠️ 工具调用：可以使用各种外部工具")
    print("• 💾 持久化：对话历史自动保存")
    print("• 🔄 会话管理：支持多个独立会话")
    
    if tools:
        print(f"\n🛠️ 当前可用工具 ({len(tools)} 个):")
        for tool in tools[:5]:  # 只显示前5个
            print(f"  • {tool.name}: {tool.description[:50]}...")
        if len(tools) > 5:
            print(f"  ... 还有 {len(tools) - 5} 个工具")


async def interactive_loop_with_persistence(app, tools, session_manager):
    """带持久化功能的交互式对话循环"""
    show_welcome(tools)
    
    # 创建新会话
    thread_id = session_manager.create_session()
    
    while True:
        try:
            print("\n" + "-" * 40)
            user_input = input("💬 请输入您的问题: ").strip()

            if not user_input:
                continue

            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！感谢使用 LangGraph Agent 助手！")
                break
            elif user_input.lower() == 'new':
                thread_id = session_manager.clear_current_session()
                print("✅ 已开始新对话")
                continue
            elif user_input.lower().startswith('resume '):
                # 恢复到指定会话：resume thread_id
                parts = user_input.split(' ', 1)
                if len(parts) == 2:
                    target_thread_id = parts[1].strip()
                    thread_id = session_manager.resume_session(target_thread_id)
                    print("✅ 已恢复到指定会话")
                else:
                    print("❌ 请提供会话ID，格式：resume <thread_id>")
                continue
            elif user_input.lower() == 'history':
                # 获取对话历史
                try:
                    config = session_manager.get_session_config(thread_id)
                    state = await app.aget_state(config)
                    if state.values and "messages" in state.values:
                        messages = state.values["messages"]
                        print(f"\n📚 当前会话历史 ({len(messages)} 条消息):")
                        for i, msg in enumerate(messages[-10:], 1):  # 只显示最近10条
                            msg_type = "👤" if isinstance(msg, HumanMessage) else "🤖" if isinstance(msg, AIMessage) else "🔧"
                            print(f"  {i}. {msg_type} {msg.content[:50]}...")
                    else:
                        print("📚 当前会话暂无历史记录")
                except Exception as e:
                    print(f"❌ 获取历史记录失败: {e}")
                continue
            elif user_input.lower() == 'help':
                show_help(tools)
                continue
            elif user_input.lower() == 'tools':
                print(f"\n🛠️ 可用工具 ({len(tools)} 个):")
                for tool in tools:
                    print(f"  • {tool.name}: {tool.description}")
                continue
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                show_welcome(tools)
                continue

            # 处理用户问题
            await run_agent_with_persistence(app, user_input, session_manager, thread_id)

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n💥 发生错误: {e}")
            print("请重试或输入 'quit' 退出")


async def main():
    """主函数"""
    try:
        # 初始化 Agent
        app, tools, session_manager = await initialize_agent()

        # 启动交互循环
        await interactive_loop_with_persistence(app, tools, session_manager)

    except Exception as e:
        print(f"\n💥 初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
