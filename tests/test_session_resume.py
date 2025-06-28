#!/usr/bin/env python3
"""
测试 Chainlit 历史会话恢复功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import initialize_agent
from langchain_core.messages import HumanMessage


async def test_session_persistence():
    """测试会话持久化功能"""
    print("🧪 测试会话持久化功能...")
    
    try:
        # 初始化 Agent
        app, tools, session_manager = await initialize_agent()
        
        # 测试会话 ID
        test_thread_id = "test_session_123"
        config = {"configurable": {"thread_id": test_thread_id}}
        
        print(f"📝 使用测试会话 ID: {test_thread_id}")
        
        # 第一轮对话
        print("\n--- 第一轮对话 ---")
        test_message_1 = "你好，我是测试用户"
        
        response_1 = ""
        async for msg_obj, metadata in app.astream(
            {"messages": [HumanMessage(content=test_message_1)]},
            stream_mode="messages",
            config=config
        ):
            if (
                hasattr(msg_obj, "content")
                and msg_obj.content
                and not isinstance(msg_obj, HumanMessage)
                and metadata.get("langgraph_node") != "tools"
            ):
                response_1 += msg_obj.content
        
        print(f"用户: {test_message_1}")
        print(f"助手: {response_1[:100]}...")
        
        # 第二轮对话（测试历史记忆）
        print("\n--- 第二轮对话（测试历史记忆）---")
        test_message_2 = "你还记得我刚才说了什么吗？"
        
        response_2 = ""
        async for msg_obj, metadata in app.astream(
            {"messages": [HumanMessage(content=test_message_2)]},
            stream_mode="messages",
            config=config
        ):
            if (
                hasattr(msg_obj, "content")
                and msg_obj.content
                and not isinstance(msg_obj, HumanMessage)
                and metadata.get("langgraph_node") != "tools"
            ):
                response_2 += msg_obj.content
        
        print(f"用户: {test_message_2}")
        print(f"助手: {response_2[:100]}...")
        
        # 检查是否记住了历史
        if "测试用户" in response_2 or "你好" in response_2:
            print("✅ 会话持久化测试成功 - Agent 记住了历史对话")
        else:
            print("⚠️ 会话持久化可能有问题 - Agent 似乎没有记住历史对话")
        
        # 测试新会话（不同 thread_id）
        print("\n--- 测试新会话 ---")
        new_thread_id = "test_session_456"
        new_config = {"configurable": {"thread_id": new_thread_id}}
        
        test_message_3 = "你还记得我之前说了什么吗？"
        
        response_3 = ""
        async for msg_obj, metadata in app.astream(
            {"messages": [HumanMessage(content=test_message_3)]},
            stream_mode="messages",
            config=new_config
        ):
            if (
                hasattr(msg_obj, "content")
                and msg_obj.content
                and not isinstance(msg_obj, HumanMessage)
                and metadata.get("langgraph_node") != "tools"
            ):
                response_3 += msg_obj.content
        
        print(f"用户: {test_message_3}")
        print(f"助手: {response_3[:100]}...")
        
        # 新会话应该不记得之前的对话
        if "测试用户" not in response_3:
            print("✅ 会话隔离测试成功 - 新会话不记得其他会话的内容")
        else:
            print("⚠️ 会话隔离可能有问题 - 新会话记住了其他会话的内容")
        
        print("\n🎉 会话持久化测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("🚀 开始测试 Chainlit 历史会话恢复功能")
    await test_session_persistence()


if __name__ == "__main__":
    asyncio.run(main())
