#!/usr/bin/env python3
"""
测试当前活跃线程的会话恢复功能
"""

import asyncio
import sqlite3
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlite_data_layer import SQLiteDataLayer

async def test_current_thread():
    """测试当前活跃线程"""
    print("🧪 测试当前活跃线程的会话恢复功能")
    print("=" * 50)
    
    # 从浏览器中看到的线程ID
    test_thread_id = "86e6dff9-054c-4064-9460-6bc5fdc2f164"
    
    # 初始化数据层
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    data_layer = SQLiteDataLayer(db_path=db_path)
    
    # 直接查询数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 检查线程: {test_thread_id}")
    
    # 检查线程是否在 threads 表中存在
    cursor.execute("SELECT id, name, createdAt FROM threads WHERE id = ?", (test_thread_id,))
    thread_row = cursor.fetchone()
    if thread_row:
        print(f"✅ 线程在 threads 表中存在: {thread_row}")
    else:
        print(f"❌ 线程在 threads 表中不存在")
    
    # 检查线程的步骤
    cursor.execute("""
        SELECT type, name, output, createdAt
        FROM steps 
        WHERE threadId = ? 
        ORDER BY createdAt ASC
        LIMIT 10
    """, (test_thread_id,))
    
    steps = cursor.fetchall()
    print(f"📝 线程中的步骤数量: {len(steps)}")
    
    for i, (step_type, name, output, created_at) in enumerate(steps, 1):
        content = output if output else name
        content_preview = content[:50] + "..." if len(content) > 50 else content
        print(f"  {i}. [{step_type}] {content_preview}")
    
    # 测试 get_thread 方法
    print(f"\n🔧 测试 get_thread 方法...")
    try:
        full_thread = await data_layer.get_thread(test_thread_id)
        if full_thread:
            steps = full_thread.get("steps", [])
            print(f"✅ 成功获取线程数据，包含 {len(steps)} 个步骤")
            
            # 统计有效消息数量
            valid_messages = 0
            for step in steps:
                step_output = step.get("output", "")
                step_type = step.get("type", "")
                if step_output and "会话已恢复" not in step_output:
                    if step_type in ["user_message", "assistant_message"]:
                        valid_messages += 1
            
            print(f"📊 有效消息数量: {valid_messages}")
            
            if valid_messages > 0:
                print(f"✅ 线程 {test_thread_id} 可以正常恢复历史消息")
            else:
                print(f"⚠️ 线程 {test_thread_id} 没有有效的历史消息")
        else:
            print(f"❌ 无法获取线程 {test_thread_id} 的数据")
    except Exception as e:
        print(f"❌ 获取线程数据时出错: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_current_thread())
