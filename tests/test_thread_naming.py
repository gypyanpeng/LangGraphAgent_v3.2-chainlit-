#!/usr/bin/env python3
"""
测试智能会话命名功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chainlit_app import generate_thread_name

async def test_thread_naming():
    """测试智能会话命名功能"""
    print("🧪 测试智能会话命名功能...")
    
    test_cases = [
        # 测试用例: (输入消息, 期望的命名模式)
        ("你好，我想了解一下人工智能的发展历史", "你好，我想了解一下人工智能的发展历史"),
        ("什么是机器学习？", "什么是机器学习？"),
        ("帮我写一个Python程序", "帮我写一个Python程序"),
        ("今天天气怎么样", "今天天气怎么样"),
        ("这是一个非常长的消息，超过了30个字符的限制，应该会被截断", "这是一个非常长的消息，超过了30个字符的限制，应该会被截断"[:27] + "..."),
        ("hi", None),  # 太短的消息应该使用默认格式
        ("", None),    # 空消息应该使用默认格式
        ("   ", None), # 只有空格的消息应该使用默认格式
        ("如何学习\n\n深度学习？", "如何学习 深度学习？"),  # 测试换行符处理
        ("你能帮我分析一下这个问题吗？", "你能帮我分析一下这个问题吗？"),  # 测试问号保留
    ]
    
    print(f"\n📋 测试 {len(test_cases)} 个用例:")
    
    for i, (input_msg, expected_pattern) in enumerate(test_cases, 1):
        try:
            result = await generate_thread_name(input_msg)
            
            print(f"\n{i}. 输入: '{input_msg}'")
            print(f"   输出: '{result}'")
            
            # 验证结果
            if expected_pattern is None:
                # 对于太短的消息，应该使用默认格式
                if "对话" in result and len(result) > 10:
                    print(f"   ✅ 正确使用默认格式")
                else:
                    print(f"   ❌ 默认格式不正确")
            else:
                if expected_pattern in result or result == expected_pattern:
                    print(f"   ✅ 命名正确")
                else:
                    print(f"   ❌ 命名不符合预期")
                    print(f"   期望: '{expected_pattern}'")
            
            # 验证长度限制
            if len(result) <= 35:  # 允许一些额外字符
                print(f"   ✅ 长度合适 ({len(result)} 字符)")
            else:
                print(f"   ❌ 长度过长 ({len(result)} 字符)")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
    
    print(f"\n🎉 智能命名功能测试完成！")

if __name__ == "__main__":
    asyncio.run(test_thread_naming())
