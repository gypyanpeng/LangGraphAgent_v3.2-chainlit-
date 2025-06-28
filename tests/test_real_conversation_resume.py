#!/usr/bin/env python3
"""
测试真实对话内容的会话恢复功能
"""

import asyncio
import sqlite3
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlite_data_layer import SQLiteDataLayer

async def test_real_conversation_resume():
    """测试真实对话内容的会话恢复"""
    print("🧪 测试真实对话内容的会话恢复功能")
    print("=" * 50)
    
    # 初始化数据层
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    data_layer = SQLiteDataLayer(db_path=db_path)
    
    # 查找有真实对话内容的线程
    print("🔍 查找有真实对话内容的线程...")
    
    # 直接查询数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找有用户消息且在 threads 表中存在的线程
    cursor.execute("""
        SELECT DISTINCT s.threadId, COUNT(*) as message_count
        FROM steps s
        INNER JOIN threads t ON s.threadId = t.id
        WHERE s.type = 'user_message'
        AND s.output IS NOT NULL
        AND s.output != ''
        AND s.output NOT LIKE '%会话已恢复%'
        GROUP BY s.threadId
        ORDER BY message_count DESC
        LIMIT 3
    """)
    
    threads_with_content = cursor.fetchall()
    
    if not threads_with_content:
        print("❌ 没有找到有真实对话内容的线程")
        return
    
    print(f"✅ 找到 {len(threads_with_content)} 个有真实对话内容的线程")
    
    for thread_id, message_count in threads_with_content:
        print(f"\n📋 测试线程: {thread_id} (消息数: {message_count})")
        
        # 获取线程的详细信息
        cursor.execute("""
            SELECT type, name, output, createdAt
            FROM steps 
            WHERE threadId = ? 
            AND output IS NOT NULL 
            AND output != ''
            AND output NOT LIKE '%会话已恢复%'
            ORDER BY createdAt ASC
            LIMIT 5
        """, (thread_id,))
        
        messages = cursor.fetchall()
        
        print(f"📝 线程中的消息预览:")
        for i, (msg_type, name, output, created_at) in enumerate(messages, 1):
            content = output if output else name
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"  {i}. [{msg_type}] {content_preview}")
        
        # 检查线程是否在 threads 表中存在
        cursor.execute("SELECT id, name FROM threads WHERE id = ?", (thread_id,))
        thread_row = cursor.fetchone()
        if thread_row:
            print(f"✅ 线程在 threads 表中存在: {thread_row}")
        else:
            print(f"❌ 线程在 threads 表中不存在")
            continue

        # 测试 get_thread 方法
        print(f"\n🔧 测试 get_thread 方法...")
        try:
            full_thread = await data_layer.get_thread(thread_id)
            if full_thread:
                steps = full_thread.get("steps", [])
                print(f"✅ 成功获取线程数据，包含 {len(steps)} 个步骤")

                # 统计有效消息数量
                valid_messages = 0
                for step in steps:
                    step_output = step.get("output", "")
                    if step_output and "会话已恢复" not in step_output:
                        valid_messages += 1

                print(f"📊 有效消息数量: {valid_messages}")

                if valid_messages > 0:
                    print(f"✅ 线程 {thread_id} 可以正常恢复历史消息")
                else:
                    print(f"⚠️ 线程 {thread_id} 没有有效的历史消息")
            else:
                print(f"❌ 无法获取线程 {thread_id} 的数据")
        except Exception as e:
            print(f"❌ 获取线程数据时出错: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_real_conversation_resume())
