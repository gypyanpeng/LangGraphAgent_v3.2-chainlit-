#!/usr/bin/env python3
"""
测试交互式 LangGraph Agent 的功能
"""

import asyncio
import sys
import os
import pytest

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import initialize_agent, run_agent_with_persistence, SimpleSessionManager


@pytest.mark.asyncio
async def test_agent_initialization():
    """测试 Agent 初始化"""
    print("🧪 测试 Agent 初始化...")
    try:
        app, tools, session_manager = await initialize_agent()
        print("✅ Agent 初始化成功")
        print(f"✅ 成功加载 {len(tools)} 个工具")
        assert app is not None
        assert tools is not None
        assert session_manager is not None
    except Exception as e:
        print(f"❌ Agent 初始化失败: {e}")
        assert False


@pytest.mark.asyncio
async def test_simple_query():
    """测试简单查询"""
    print("\n🧪 测试简单数学问题...")
    query = "2 + 2 等于多少？"
    app, tools, session_manager = await initialize_agent()
    thread_id = session_manager.create_session(user_id="test_user")
    try:
        await run_agent_with_persistence(app, query, session_manager, thread_id)
        print("✅ 简单查询测试通过")
    except Exception as e:
        print(f"❌ 简单查询测试失败: {e}")
        assert False


@pytest.mark.asyncio
async def test_complex_query():
    """测试复杂查询（需要工具）"""
    print("\n🧪 测试复杂逻辑问题...")
    query = "请使用思考工具分析：如果一个数字加上它的一半等于15，这个数字是多少？"
    app, tools, session_manager = await initialize_agent()
    thread_id = session_manager.create_session(user_id="test_user")
    try:
        await run_agent_with_persistence(app, query, session_manager, thread_id)
        print("✅ 复杂查询测试通过")
    except Exception as e:
        print(f"❌ 复杂查询测试失败: {e}")
        assert False


@pytest.mark.asyncio
async def test_search_query():
    """测试搜索查询"""
    print("\n🧪 测试搜索功能...")
    query = "请搜索关于Python 3.12的新特性"
    app, tools, session_manager = await initialize_agent()
    thread_id = session_manager.create_session(user_id="test_user")
    try:
        await run_agent_with_persistence(app, query, session_manager, thread_id)
        print("✅ 搜索查询测试通过")
    except Exception as e:
        print(f"❌ 搜索查询测试失败: {e}")
        assert False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 LangGraph Agent 功能测试")
    print("=" * 60)

    # 初始化测试
    await test_agent_initialization()

    # 运行各种测试
    await test_simple_query()
    await test_complex_query()
    await test_search_query()

    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)
    print("\n💡 提示：运行 'python main.py' 开始交互式对话")


if __name__ == "__main__":
    asyncio.run(main())
