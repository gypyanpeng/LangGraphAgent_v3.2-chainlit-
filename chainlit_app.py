#!/usr/bin/env python3
"""
Chainlit Web 前端集成 - 符合官方最佳实践，支持历史会话恢复
"""

import os
import asyncio
from typing import Optional

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
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncio

def init_database_sync():
    """同步方式初始化数据库表（在模块导入时调用）"""
    try:
        # 确保数据目录存在
        os.makedirs("./data", exist_ok=True)

        # 使用同步SQLite连接进行初始化
        import sqlite3

        db_path = "./data/chainlit_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查 users 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("🔧 正在初始化 Chainlit 数据库表...")

            # 创建表的 SQL
            create_tables_sql = [
                """CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL UNIQUE,
                    metadata TEXT NOT NULL,
                    createdAt TEXT
                )""",
                """CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    createdAt TEXT,
                    name TEXT,
                    userId TEXT,
                    userIdentifier TEXT,
                    tags TEXT,
                    metadata TEXT,
                    FOREIGN KEY (userId) REFERENCES users(id)
                )""",
                """CREATE TABLE IF NOT EXISTS steps (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    threadId TEXT NOT NULL,
                    parentId TEXT,
                    disableFeedback INTEGER DEFAULT 0,
                    streaming INTEGER DEFAULT 0,
                    waitForAnswer INTEGER DEFAULT 0,
                    isError INTEGER DEFAULT 0,
                    metadata TEXT,
                    tags TEXT,
                    input TEXT,
                    output TEXT,
                    createdAt TEXT NOT NULL,
                    command TEXT,
                    start TEXT,
                    end TEXT,
                    generation TEXT,
                    showInput TEXT,
                    language TEXT,
                    indent INTEGER DEFAULT 0,
                    defaultOpen INTEGER DEFAULT 0,
                    FOREIGN KEY (threadId) REFERENCES threads(id)
                )""",
                """CREATE TABLE IF NOT EXISTS elements (
                    id TEXT PRIMARY KEY,
                    threadId TEXT,
                    stepId TEXT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    url TEXT,
                    objectKey TEXT,
                    size TEXT,
                    page INTEGER,
                    language TEXT,
                    forId TEXT,
                    mime TEXT,
                    chainlitKey TEXT,
                    display TEXT,
                    props TEXT,
                    FOREIGN KEY (threadId) REFERENCES threads(id),
                    FOREIGN KEY (stepId) REFERENCES steps(id)
                )""",
                """CREATE TABLE IF NOT EXISTS feedbacks (
                    id TEXT PRIMARY KEY,
                    forId TEXT NOT NULL,
                    threadId TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    comment TEXT,
                    FOREIGN KEY (threadId) REFERENCES threads(id)
                )"""
            ]

            # 执行创建表的 SQL
            for sql in create_tables_sql:
                cursor.execute(sql)

            conn.commit()
            print("✅ Chainlit 数据库表初始化完成")
        else:
            print("✅ Chainlit 数据库表已存在")

        conn.close()

    except Exception as e:
        print(f"⚠️ 数据库初始化警告: {e}")

# 在模块导入时初始化数据库
init_database_sync()

async def init_database_if_needed():
    """数据库已在模块导入时初始化，此函数保留用于兼容性"""
    pass

@cl.data_layer
def get_data_layer():
    """配置 Chainlit 数据层以支持历史会话显示"""
    # 注意：不使用 storage_provider 意味着元素（如图片、文件）不会被持久化
    # 但基本的聊天历史功能仍然可以工作
    return SQLAlchemyDataLayer(
        conninfo="sqlite+aiosqlite:///./data/chainlit_history.db",
        storage_provider=None  # 本地开发暂不使用存储提供商
    )

# 配置简单的密码身份验证
@cl.password_auth_callback
async def auth_callback(username: str, password: str):
    """简单的密码身份验证"""
    # 简单的用户验证（生产环境请使用更安全的方式）
    if username == "admin" and password == "admin123":
        return cl.User(
            identifier="admin",
            display_name="管理员"
        )
    elif username == "user" and password == "user123":
        return cl.User(
            identifier="user",
            display_name="用户"
        )
    return None


@cl.on_chat_start
async def on_chat_start():
    """
    Chainlit 会话开始时初始化 Agent
    """
    try:
        # 确保数据库已初始化
        await init_database_if_needed()

        # 初始化 Agent
        app, tools, session_manager = await initialize_agent()

        # 将 Agent 相关对象存储到用户会话中
        cl.user_session.set("app", app)
        cl.user_session.set("tools", tools)
        cl.user_session.set("session_manager", session_manager)

        # 发送欢迎消息
        await cl.Message(
            content="🤖 **LangGraph Agent 已启动！**\n\n我可以帮您处理各种任务，包括：\n- 🔍 网络搜索和信息检索\n- 🧠 复杂逻辑推理和分析\n- 📊 数据可视化和图表生成\n- 💻 代码编写和技术支持\n- 🌐 网页自动化操作\n\n请告诉我您需要什么帮助？"
        ).send()

    except Exception as e:
        await cl.Message(
            content=f"❌ **初始化失败**: {str(e)}\n\n请检查配置文件并重试。"
        ).send()


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """
    恢复历史会话 - 按照 Chainlit 官方文档实现
    """
    try:
        # 重新初始化 Agent
        app, tools, session_manager = await initialize_agent()

        # 将 Agent 相关对象存储到用户会话中
        cl.user_session.set("app", app)
        cl.user_session.set("tools", tools)
        cl.user_session.set("session_manager", session_manager)

        # 获取历史消息数量
        message_count = len(thread.get("steps", []))

        # 发送恢复会话的提示消息
        await cl.Message(
            content=f"🔄 **会话已恢复！**\n\n已加载 {message_count} 条历史消息。您可以继续之前的对话。"
        ).send()

    except Exception as e:
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
    # 从用户会话中获取 Agent 相关对象
    app = cl.user_session.get("app")
    session_manager = cl.user_session.get("session_manager")
    
    if not app or not session_manager:
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
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **处理消息时出错**: {str(e)}\n\n请重试或联系管理员。"
        ).send()


if __name__ == "__main__":
    # 用于调试的入口点
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
