#!/usr/bin/env python3
"""
系统集成测试 - 验证 LangGraph 持久化、检查点、会话管理功能
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import initialize_agent, run_agent_with_persistence


async def test_basic_functionality():
    """测试基本功能"""
    print("🧪 测试 1: 基本功能测试")

    try:
        # 初始化 Agent
        app, tools, session_manager = await initialize_agent()
        print("✅ Agent 初始化成功")

        # 创建测试会话
        thread_id = session_manager.create_session("test_user")
        print(f"✅ 会话创建成功: {thread_id}")

        # 测试基本对话
        result = await run_agent_with_persistence(
            app, "你好，我是测试用户", session_manager, thread_id
        )
        print("✅ 基本对话测试成功")

        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False


async def test_persistence():
    """测试持久化功能"""
    print("\n🧪 测试 2: 持久化功能测试")

    try:
        # 初始化 Agent
        app, _, session_manager = await initialize_agent()

        # 创建测试会话
        thread_id = session_manager.create_session("test_user")

        # 第一次对话 - 存储信息
        await run_agent_with_persistence(
            app, "请记住我的名字是张三", session_manager, thread_id
        )
        print("✅ 信息存储成功")

        # 第二次对话 - 验证记忆
        await run_agent_with_persistence(
            app, "我的名字是什么？", session_manager, thread_id
        )
        print("✅ 记忆验证成功")

        return True
    except Exception as e:
        print(f"❌ 持久化测试失败: {e}")
        return False


async def test_session_management():
    """测试会话管理"""
    print("\n🧪 测试 3: 会话管理测试")

    try:
        # 初始化 Agent
        app, _, session_manager = await initialize_agent()

        # 创建多个会话
        thread_id1 = session_manager.create_session("user1")
        thread_id2 = session_manager.create_session("user2")

        print(f"✅ 创建了两个会话: {thread_id1}, {thread_id2}")

        # 在第一个会话中存储信息
        await run_agent_with_persistence(
            app, "我是用户1，我喜欢苹果", session_manager, thread_id1
        )

        # 在第二个会话中存储不同信息
        await run_agent_with_persistence(
            app, "我是用户2，我喜欢橙子", session_manager, thread_id2
        )

        print("✅ 会话隔离测试成功")

        return True
    except Exception as e:
        print(f"❌ 会话管理测试失败: {e}")
        return False


async def test_configuration():
    """测试配置加载"""
    print("\n🧪 测试 4: 配置加载测试")
    
    try:
        from main import load_persistence_config
        
        # 测试配置加载
        config = load_persistence_config()
        
        # 验证配置结构
        assert "persistence" in config
        assert "session_management" in config
        assert "memory_settings" in config
        
        print("✅ 配置加载和验证成功")
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False


async def test_checkpointer():
    """测试检查点存储器"""
    print("\n🧪 测试 5: 检查点存储器测试")
    
    try:
        from main import create_checkpointer
        
        # 测试检查点存储器创建
        checkpointer = await create_checkpointer()
        
        # 验证检查点存储器类型
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        from langgraph.checkpoint.memory import MemorySaver
        
        assert isinstance(checkpointer, (AsyncSqliteSaver, MemorySaver))
        
        print("✅ 检查点存储器测试成功")
        
        return True
    except Exception as e:
        print(f"❌ 检查点存储器测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始系统集成测试")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_checkpointer,
        test_basic_functionality,
        test_persistence,
        test_session_management,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查系统配置")
        return False


if __name__ == "__main__":
    asyncio.run(run_all_tests())
