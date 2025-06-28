#!/usr/bin/env python3
"""
测试历史会话恢复功能修复
验证历史消息是否能正确显示
"""

import asyncio
import sqlite3
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlite_data_layer import SQLiteDataLayer

async def test_get_thread_with_steps():
    """测试获取包含步骤的线程数据"""
    print("🔍 测试历史会话恢复功能修复")
    print("=" * 50)
    
    # 创建数据层实例
    data_layer = SQLiteDataLayer()
    
    # 获取数据库中的所有线程
    print("\n📋 获取所有线程...")
    try:
        # 直接查询数据库获取线程列表
        conn = sqlite3.connect("data/chainlit_history.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, createdAt FROM threads ORDER BY createdAt DESC LIMIT 5")
        threads = cursor.fetchall()
        
        if not threads:
            print("❌ 没有找到任何历史线程")
            return
        
        print(f"✅ 找到 {len(threads)} 个历史线程:")
        for i, (thread_id, name, created_at) in enumerate(threads):
            print(f"  {i+1}. {thread_id[:8]}... - {name or '未命名'} ({created_at})")
        
        # 查找既存在于 threads 表又有历史消息的线程
        cursor.execute("""
            SELECT t.id, COUNT(s.id) as step_count
            FROM threads t
            LEFT JOIN steps s ON t.id = s.threadId
            GROUP BY t.id
            HAVING step_count > 0
            ORDER BY step_count DESC
            LIMIT 1
        """)
        thread_with_steps = cursor.fetchone()

        if thread_with_steps:
            test_thread_id = thread_with_steps[0]
            print(f"\n🎯 测试线程 (有 {thread_with_steps[1]} 个步骤): {test_thread_id}")
        else:
            # 选择第一个线程进行测试
            test_thread_id = threads[0][0]
            print(f"\n🎯 测试线程: {test_thread_id}")
        
        # 检查该线程的步骤数量
        cursor.execute("SELECT COUNT(*) FROM steps WHERE threadId = ?", (test_thread_id,))
        step_count = cursor.fetchone()[0]
        print(f"📊 该线程包含 {step_count} 个步骤")
        
        if step_count == 0:
            print("⚠️ 该线程没有历史消息，创建一些测试数据...")
            # 创建测试步骤
            test_steps = [
                {
                    "id": f"step_user_{datetime.now().timestamp()}",
                    "name": "你好，我想了解一下这个项目的功能",
                    "type": "user_message",
                    "threadId": test_thread_id,
                    "parentId": None,
                    "disableFeedback": 0,
                    "streaming": 0,
                    "waitForAnswer": 0,
                    "isError": 0,
                    "metadata": "{}",
                    "tags": "[]",
                    "input": "",
                    "output": "",
                    "createdAt": datetime.now().isoformat(),
                    "start": None,
                    "end": None,
                    "generation": None,
                    "showInput": None,
                    "language": None,
                    "indent": 0,
                    "defaultOpen": 0,
                    "command": None
                },
                {
                    "id": f"step_assistant_{datetime.now().timestamp()}",
                    "name": "你好！这是一个基于 LangGraph 的智能对话系统，具有持久化功能和多种工具集成。",
                    "type": "assistant_message",
                    "threadId": test_thread_id,
                    "parentId": None,
                    "disableFeedback": 0,
                    "streaming": 0,
                    "waitForAnswer": 0,
                    "isError": 0,
                    "metadata": "{}",
                    "tags": "[]",
                    "input": "",
                    "output": "",
                    "createdAt": datetime.now().isoformat(),
                    "start": None,
                    "end": None,
                    "generation": None,
                    "showInput": None,
                    "language": None,
                    "indent": 0,
                    "defaultOpen": 0,
                    "command": None
                }
            ]
            
            for step in test_steps:
                cursor.execute("""
                    INSERT INTO steps (
                        id, name, type, threadId, parentId, disableFeedback, streaming,
                        waitForAnswer, isError, metadata, tags, input, output, createdAt,
                        start, end, generation, showInput, language, indent, defaultOpen, command
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step["id"], step["name"], step["type"], step["threadId"], step["parentId"],
                    step["disableFeedback"], step["streaming"], step["waitForAnswer"], step["isError"],
                    step["metadata"], step["tags"], step["input"], step["output"], step["createdAt"],
                    step["start"], step["end"], step["generation"], step["showInput"], step["language"],
                    step["indent"], step["defaultOpen"], step["command"]
                ))
            
            conn.commit()
            print("✅ 测试数据创建完成")
        
        conn.close()
        
        # 测试 get_thread 方法
        print(f"\n🔄 测试 get_thread 方法...")
        thread_data = await data_layer.get_thread(test_thread_id)
        
        if thread_data:
            print("✅ 成功获取线程数据:")
            print(f"  - 线程ID: {thread_data['id']}")
            print(f"  - 线程名称: {thread_data.get('name', '未命名')}")
            print(f"  - 用户标识: {thread_data.get('userIdentifier', 'N/A')}")
            print(f"  - 步骤数量: {len(thread_data.get('steps', []))}")
            print(f"  - 元素数量: {len(thread_data.get('elements', []))}")
            
            # 显示步骤详情
            steps = thread_data.get('steps', [])
            if steps:
                print("\n📜 历史消息:")
                for i, step in enumerate(steps):
                    step_type = step.get('type', 'unknown')
                    step_name = step.get('name', 'N/A')
                    print(f"  {i+1}. [{step_type}] {step_name[:50]}...")
            else:
                print("⚠️ 没有找到历史消息")
        else:
            print("❌ 无法获取线程数据")
        
        print("\n" + "=" * 50)
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_get_thread_with_steps())
