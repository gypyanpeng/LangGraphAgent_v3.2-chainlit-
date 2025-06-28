#!/usr/bin/env python3
"""
测试 Agent 初始化过程
"""

import asyncio
import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_agent_initialization():
    """测试 Agent 初始化的每个步骤"""
    print("🧪 开始测试 Agent 初始化过程...")
    
    try:
        # 1. 测试配置加载
        print("\n1️⃣ 测试配置加载...")
        
        from main import load_persistence_config
        persistence_config = load_persistence_config("config/persistence_config.json")
        print(f"✅ 持久化配置加载成功")
        
        # 2. 测试检查点存储器创建
        print("\n2️⃣ 测试检查点存储器创建...")
        
        from main import create_checkpointer
        checkpointer = await create_checkpointer(persistence_config)
        print(f"✅ 检查点存储器创建成功: {type(checkpointer).__name__}")
        
        # 3. 测试会话管理器创建
        print("\n3️⃣ 测试会话管理器创建...")
        
        from main import SimpleSessionManager
        session_manager = SimpleSessionManager(persistence_config)
        print(f"✅ 会话管理器创建成功")
        
        # 4. 测试 LLM 加载
        print("\n4️⃣ 测试 LLM 加载...")
        
        from llm_loader import load_llm_from_config
        llm = load_llm_from_config("config/llm_config.json")
        print(f"✅ LLM 加载成功: {llm.model_name}")
        
        # 5. 测试 MCP 工具加载
        print("\n5️⃣ 测试 MCP 工具加载...")
        
        from mcp_loader import load_mcp_tools_from_config
        try:
            _, tools = await load_mcp_tools_from_config("config/mcp_config.json")
            print(f"✅ MCP 工具加载成功: {len(tools)} 个工具")
        except Exception as e:
            print(f"⚠️ MCP 工具加载失败: {e}")
            print("   使用空工具列表继续测试...")
            tools = []
        
        # 6. 测试工具绑定
        print("\n6️⃣ 测试工具绑定...")
        
        llm_with_tools = llm.bind_tools(tools)
        print(f"✅ 工具绑定成功")
        
        # 7. 测试工作流构建
        print("\n7️⃣ 测试工作流构建...")
        
        from langgraph.graph import StateGraph, END
        from langgraph.prebuilt import ToolNode
        from main import AgentState
        
        # 定义节点函数
        def call_model(state):
            """调用模型节点"""
            messages = state["messages"]
            try:
                response = llm_with_tools.invoke(messages)
                return {"messages": [response]}
            except Exception as e:
                print(f"⚠️ 模型调用出错: {e}")
                from langchain_core.messages import AIMessage
                error_response = AIMessage(content=f"抱歉，处理请求时出现错误: {str(e)}")
                return {"messages": [error_response]}
        
        # 创建工具节点
        tool_node = ToolNode(tools) if tools else None
        
        def should_continue(state):
            """判断是否继续执行"""
            messages = state["messages"]
            last_message = messages[-1]
            
            from langchain_core.messages import AIMessage
            if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return END
        
        # 构建工作流
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_model)
        
        if tool_node:
            workflow.add_node("tools", tool_node)
            workflow.set_entry_point("agent")
            workflow.add_conditional_edges("agent", should_continue, ["tools", END])
            workflow.add_edge("tools", "agent")
        else:
            workflow.set_entry_point("agent")
            workflow.add_edge("agent", END)
        
        print(f"✅ 工作流构建成功")
        
        # 8. 测试工作流编译
        print("\n8️⃣ 测试工作流编译...")
        
        app = workflow.compile(checkpointer=checkpointer)
        print(f"✅ 工作流编译成功")
        
        # 9. 测试简单调用
        print("\n9️⃣ 测试简单调用...")
        
        from langchain_core.messages import HumanMessage
        inputs = {"messages": [HumanMessage(content="你好")]}
        config = {"configurable": {"thread_id": "test_thread"}}
        
        result = await app.ainvoke(inputs, config=config)
        print(f"✅ 简单调用成功")
        print(f"   回复: {result['messages'][-1].content[:50]}...")
        
        print("\n🎉 所有初始化步骤都成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        print("\n📋 详细错误信息:")
        traceback.print_exc()
        return False

async def test_initialize_agent_function():
    """直接测试 initialize_agent 函数"""
    print("\n🔧 直接测试 initialize_agent 函数...")
    
    try:
        from main import initialize_agent
        app, tools, session_manager = await initialize_agent()
        
        print(f"✅ initialize_agent 函数成功")
        print(f"   App: {type(app).__name__}")
        print(f"   Tools: {len(tools)} 个")
        print(f"   Session Manager: {type(session_manager).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ initialize_agent 函数失败: {e}")
        print("\n📋 详细错误信息:")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 Agent 初始化诊断工具")
    print("=" * 50)
    
    # 分步测试
    success1 = await test_agent_initialization()
    
    # 直接函数测试
    success2 = await test_initialize_agent_function()
    
    print("\n" + "=" * 50)
    print("🎯 诊断结果:")
    print(f"   分步初始化: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   函数调用: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 Agent 初始化正常！")
    else:
        print("\n⚠️ Agent 初始化存在问题，请查看上述错误信息")

if __name__ == "__main__":
    asyncio.run(main())
