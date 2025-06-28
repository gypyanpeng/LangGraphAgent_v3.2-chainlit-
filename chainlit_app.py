#!/usr/bin/env python3
"""
Chainlit Web 前端集成 - 符合官方最佳实践，支持历史会话恢复
"""

import os
import asyncio
import logging
from typing import Optional

# 配置详细日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def generate_thread_name(message_content: str) -> str:
    """
    基于用户的第一条消息生成智能会话名称
    """
    # 清理消息内容
    content = message_content.strip()

    # 如果消息太短，使用默认格式
    if len(content) < 5:
        from datetime import datetime
        return f"对话 {datetime.now().strftime('%m-%d %H:%M')}"

    # 截取前30个字符作为标题，确保不会太长
    if len(content) > 30:
        title = content[:27] + "..."
    else:
        title = content

    # 移除换行符和多余空格
    title = " ".join(title.split())

    # 如果是问号结尾，保留问号
    if content.endswith('?') and not title.endswith('?'):
        title = title.rstrip('.') + '?'

    return title


async def update_thread_name_if_needed(session_id: str, message_content: str, current_user=None):
    """
    检查并更新线程名称（仅在第一条消息后）
    """
    try:
        # 获取数据层实例
        data_layer = cl.user_session.get("data_layer")
        if not data_layer:
            from sqlite_data_layer import SQLiteDataLayer
            data_layer = SQLiteDataLayer()
            cl.user_session.set("data_layer", data_layer)

        # 获取当前线程信息
        thread = await data_layer.get_thread(session_id)
        if not thread:
            logger.warning(f"⚠️ 未找到线程: {session_id}")
            return

        # 检查线程是否已有名称（不是 None 或空字符串）
        if thread.get("name"):
            logger.info(f"🏷️ 线程已有名称，跳过更新: {thread['name']}")
            return

        # 生成智能名称
        new_name = await generate_thread_name(message_content)

        # 更新线程名称
        await data_layer.update_thread(session_id, name=new_name)
        logger.info(f"✅ 线程名称已更新: {session_id} -> '{new_name}'")

    except Exception as e:
        logger.error(f"❌ 更新线程名称失败: {str(e)}")


logger = logging.getLogger(__name__)

# 禁用 LangSmith 追踪以避免错误
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""
os.environ["LANGSMITH_TRACING"] = "false"

import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage
from chainlit.types import ThreadDict

# 导入主程序的初始化函数
from main import initialize_agent

# 配置 Chainlit 数据层（用于历史会话显示）
from sqlite_data_layer import SQLiteDataLayer
import asyncio

# 数据库初始化现在由 SQLiteDataLayer 处理

@cl.data_layer
def get_data_layer():
    """配置 Chainlit 数据层以支持历史会话显示"""
    # 使用自定义的 SQLite 数据层，解决数组类型兼容性问题
    return SQLiteDataLayer(db_path="./data/chainlit_history.db")

# 配置简单的密码身份验证
@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    """简单的密码身份验证 - 带详细调试日志"""
    logger.info(f"🔐 AUTH_CALLBACK 被调用！用户名: {username}")

    # 简单的用户验证（生产环境请使用更安全的方式）
    if username == "admin" and password == "admin123":
        user = cl.User(
            identifier="admin",
            display_name="管理员"
        )
        logger.info(f"✅ 身份验证成功！用户: {user.identifier}, 显示名: {user.display_name}")
        return user
    elif username == "user" and password == "user123":
        user = cl.User(
            identifier="user",
            display_name="用户"
        )
        logger.info(f"✅ 身份验证成功！用户: {user.identifier}, 显示名: {user.display_name}")
        return user
    else:
        logger.warning(f"❌ 身份验证失败！用户名: {username}")
        return None


@cl.on_chat_start
async def on_chat_start():
    """
    Chainlit 会话开始时初始化 Agent
    """
    try:
        # 检查用户身份验证状态
        current_user = cl.user_session.get("user")
        session_id = cl.context.session.id
        logger.info(f"🚀 CHAT_START 被调用！会话ID: {session_id}")
        logger.info(f"👤 当前用户: {current_user.identifier if current_user else 'None'}")

        if not current_user:
            logger.warning(f"⚠️ 会话开始时未找到用户信息！会话ID: {session_id}")

        # 创建新的线程记录
        if current_user:
            from datetime import datetime, timezone
            from chainlit.types import ThreadDict
            thread_data: ThreadDict = {
                "id": session_id,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "name": None,  # 初始时没有名称，会在第一条消息后更新
                "userId": current_user.id,
                "userIdentifier": current_user.identifier,
                "tags": [],
                "metadata": {},
                "steps": [],  # 新线程开始时没有步骤
                "elements": []  # 新线程开始时没有元素
            }

            # 获取数据层实例并创建线程
            data_layer = cl.user_session.get("data_layer")
            if not data_layer:
                # 如果没有数据层实例，创建一个新的
                from sqlite_data_layer import SQLiteDataLayer
                data_layer = SQLiteDataLayer()
                cl.user_session.set("data_layer", data_layer)

            # 创建线程记录
            await data_layer.create_thread(thread_data)
            logger.info(f"✅ 新线程已创建: {session_id}")

        # 数据库初始化由 SQLiteDataLayer 自动处理

        # 初始化 Agent
        app, tools, session_manager = await initialize_agent()

        # 将 Agent 相关对象存储到用户会话中
        cl.user_session.set("app", app)
        cl.user_session.set("tools", tools)
        cl.user_session.set("session_manager", session_manager)

        # 发送欢迎消息
        await cl.Message(
            content="🤖 **LangGraph Agent 已启动！**\n\n我可以帮您处理各种任务，包括：\n- 🔍 网络搜索和信息检索\n- 🧠 复杂逻辑推理和分析\n- 📊 数据可视化和图表生成\n\n请告诉我您需要什么帮助？"
        ).send()

    except Exception as e:
        logger.error(f"❌ 初始化失败: {str(e)}")
        await cl.Message(
            content=f"❌ **初始化失败**: {str(e)}\n\n请检查配置文件并重试。"
        ).send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """
    恢复历史会话 - 重新显示历史消息
    """
    try:
        # 检查用户身份验证状态
        current_user = cl.user_session.get("user")
        session_id = cl.context.session.id
        thread_id = thread.get("id", "unknown")
        logger.info(f"🔄 CHAT_RESUME 被调用！会话ID: {session_id}, 线程ID: {thread_id}")
        logger.info(f"👤 当前用户: {current_user.identifier if current_user else 'None'}")

        if not current_user:
            logger.warning(f"⚠️ 恢复会话时未找到用户信息！会话ID: {session_id}")

        # 重新初始化 Agent
        app, tools, session_manager = await initialize_agent()

        # 将 Agent 相关对象存储到用户会话中
        cl.user_session.set("app", app)
        cl.user_session.set("tools", tools)
        cl.user_session.set("session_manager", session_manager)

        # 获取完整的线程信息（包含历史消息）
        data_layer = cl.user_session.get("data_layer")
        if not data_layer:
            # 如果没有数据层，创建一个新的
            from sqlite_data_layer import SQLiteDataLayer
            data_layer = SQLiteDataLayer()
            cl.user_session.set("data_layer", data_layer)

        # 获取完整的线程数据（包含步骤）
        full_thread = await data_layer.get_thread(thread_id)
        if not full_thread:
            logger.warning(f"⚠️ 无法获取线程数据: {thread_id}")
            await cl.Message(content="⚠️ 无法加载历史会话数据").send()
            return

        # 获取历史步骤
        steps = full_thread.get("steps", [])
        logger.info(f"📜 找到 {len(steps)} 条历史消息")

        # 重新显示历史消息
        displayed_count = 0
        for step in steps:
            step_type = step.get("type", "")
            step_output = step.get("output", "")
            step_name = step.get("name", "")

            # 跳过会话恢复消息，避免重复显示
            if "会话已恢复" in step_output or "已加载" in step_output:
                continue

            # 跳过系统消息和运行步骤
            if step_type in ["run", "system"]:
                continue

            # 使用 output 字段作为消息内容，如果为空则使用 name
            content = step_output if step_output else step_name
            if not content or content.strip() == "":
                continue

            # 根据 step_type 和 step_name 判断消息类型
            # 优先根据 name 字段判断，因为 type 字段可能不准确
            is_user_message = False
            is_assistant_message = False

            if step_name in ["用户", "admin"]:
                # 根据 name 字段判断是用户消息
                is_user_message = True
            elif step_name in ["助手", "LangGraph Agent"]:
                # 根据 name 字段判断是助手消息
                is_assistant_message = True
            elif step_type == "user_message":
                is_user_message = True
            elif step_type == "assistant_message":
                is_assistant_message = True

            # 显示消息
            if is_user_message:
                await cl.Message(
                    content=content,
                    author="用户"
                ).send()
                displayed_count += 1
                logger.info(f"📤 显示用户消息: {content[:50]}...")
            elif is_assistant_message:
                await cl.Message(
                    content=content,
                    author="助手"
                ).send()
                displayed_count += 1
                logger.info(f"📤 显示助手消息: {content[:50]}...")

        # 发送恢复会话的提示消息
        await cl.Message(
            content=f"🔄 **会话已恢复！**\n\n已加载 {displayed_count} 条历史消息。您可以继续之前的对话。"
        ).send()

    except Exception as e:
        logger.error(f"❌ 恢复会话失败: {str(e)}")
        await cl.Message(
            content=f"❌ **恢复会话失败**: {str(e)}\n\n将创建新的会话。"
        ).send()
        # 如果恢复失败，回退到新会话初始化
        await on_chat_start()


@cl.on_message
async def on_message(message: cl.Message):
    """
    处理用户消息 - 符合 Chainlit 官方最佳实践
    """
    # 检查用户身份验证状态
    current_user = cl.user_session.get("user")
    session_id = cl.context.session.id
    logger.info(f"💬 MESSAGE 被调用！会话ID: {session_id}, 消息: {message.content[:50]}...")
    logger.info(f"👤 当前用户: {current_user.identifier if current_user else 'None'}")

    if not current_user:
        logger.warning(f"⚠️ 处理消息时未找到用户信息！会话ID: {session_id}")
        await cl.Message(
            content="❌ **用户未认证**\n\n请重新登录。"
        ).send()
        return

    # 从用户会话中获取 Agent 相关对象
    app = cl.user_session.get("app")
    session_manager = cl.user_session.get("session_manager")

    if not app or not session_manager:
        logger.error(f"❌ Agent 未正确初始化！会话ID: {session_id}")
        await cl.Message(
            content="❌ **Agent 未正确初始化**\n\n请刷新页面重试。"
        ).send()
        return
    
    # 使用 Chainlit session id 作为 thread_id，确保多用户隔离
    thread_id = cl.context.session.id
    config = {"configurable": {"thread_id": thread_id}}
    
    # 创建 Chainlit 回调处理器
    cb = cl.LangchainCallbackHandler()
    
    # 创建消息对象用于流式输出
    final_answer = cl.Message(content="")
    
    try:
        # 使用 LangGraph 的流式输出 - 符合官方文档建议
        async for msg_obj, metadata in app.astream(
            {"messages": [HumanMessage(content=message.content)]},
            stream_mode="messages",
            config={**config, "callbacks": [cb]}
        ):
            # 过滤并输出最终回复 - 只显示 AI 的最终回答
            if (
                hasattr(msg_obj, "content")
                and msg_obj.content
                and not isinstance(msg_obj, HumanMessage)
                and metadata.get("langgraph_node") != "tools"  # 排除工具调用的中间输出
            ):
                await final_answer.stream_token(msg_obj.content)
        
        # 发送最终消息
        await final_answer.send()

        # 检查是否需要更新线程名称（仅在第一条消息后）
        await update_thread_name_if_needed(session_id, message.content, current_user)

    except Exception as e:
        await cl.Message(
            content=f"❌ **处理消息时出错**: {str(e)}\n\n请重试或联系管理员。"
        ).send()


if __name__ == "__main__":
    # 用于调试的入口点
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
