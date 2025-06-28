#!/usr/bin/env python3
"""
调试会话恢复问题 - 检查为什么历史消息没有在前端显示
"""

import os
import sys
import sqlite3
import asyncio
import json

def main():
    print("🔍 调试会话恢复问题")
    print("=" * 50)
    
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    
    # 测试线程ID - 使用一个我们知道有数据的线程
    test_thread_id = "e0ee9273-16b9-49ed-8738-b03b4f058ff2"
    
    print(f"📂 数据库路径: {db_path}")
    print(f"🎯 测试线程ID: {test_thread_id}")
    
    # 1. 直接查询数据库
    print("\n1️⃣ 直接查询数据库中的步骤")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT type, name, output, createdAt 
        FROM steps 
        WHERE threadId = ? 
        ORDER BY createdAt
    """, (test_thread_id,))
    
    raw_steps = cursor.fetchall()
    print(f"   数据库中找到 {len(raw_steps)} 个步骤")
    
    for i, (step_type, name, output, created_at) in enumerate(raw_steps, 1):
        print(f"   {i}. [{step_type}] name='{name}' output='{output[:50]}...' ")
    
    conn.close()
    
    # 2. 测试 get_thread 方法
    print("\n2️⃣ 测试 get_thread 方法")
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sqlite_data_layer import SQLiteDataLayer
    
    data_layer = SQLiteDataLayer(db_path=db_path)
    
    async def test_get_thread():
        try:
            full_thread = await data_layer.get_thread(test_thread_id)
            if not full_thread:
                print("   ❌ get_thread 返回 None")
                return
            
            steps = full_thread.get("steps", [])
            print(f"   ✅ get_thread 返回 {len(steps)} 个步骤")
            
            # 3. 模拟 on_chat_resume 的逻辑
            print("\n3️⃣ 模拟 on_chat_resume 的消息过滤逻辑")
            displayed_count = 0
            
            for i, step in enumerate(steps, 1):
                step_type = step.get("type", "")
                step_output = step.get("output", "")
                step_name = step.get("name", "")
                
                print(f"   步骤 {i}: type='{step_type}', output='{step_output[:50]}...', name='{step_name}'")
                
                # 跳过会话恢复消息，避免重复显示
                if "会话已恢复" in step_output:
                    print(f"      ⏭️  跳过会话恢复消息")
                    continue
                
                # 使用 output 字段作为消息内容，如果为空则使用 name
                content = step_output if step_output else step_name
                if not content:
                    print(f"      ⏭️  跳过空内容")
                    continue
                
                # 只显示用户消息和助手回复
                if step_type == "user_message":
                    print(f"      ✅ 用户消息: {content[:50]}...")
                    displayed_count += 1
                elif step_type == "assistant_message":
                    print(f"      ✅ 助手消息: {content[:50]}...")
                    displayed_count += 1
                else:
                    print(f"      ⏭️  跳过类型 '{step_type}'")
            
            print(f"\n   📊 最终统计: 应该显示 {displayed_count} 条消息")
            
            if displayed_count == 0:
                print("\n❌ 问题发现：没有消息被识别为可显示！")
                print("   可能的原因：")
                print("   1. 所有消息都被过滤掉了")
                print("   2. step_type 不是 'user_message' 或 'assistant_message'")
                print("   3. 所有消息的 output 和 name 都为空")
                print("   4. 所有消息都包含 '会话已恢复' 文本")
            else:
                print(f"\n✅ 应该显示 {displayed_count} 条历史消息")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_get_thread())

if __name__ == "__main__":
    main()
