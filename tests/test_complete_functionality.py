#!/usr/bin/env python3
"""
完整功能测试脚本
测试新会话创建、删除功能、数据持久化等核心功能
"""

import asyncio
import sqlite3
import uuid
import sys
import os
from datetime import datetime, timezone

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlite_data_layer import SQLiteDataLayer
from chainlit.types import ThreadDict

async def test_complete_functionality():
    """测试完整的数据层功能"""
    print("🧪 开始完整功能测试...")
    
    # 初始化数据层
    data_layer = SQLiteDataLayer()
    
    # 测试用户信息
    test_user_id = str(uuid.uuid4())
    test_user_identifier = "test_complete_user"
    
    print(f"\n📊 测试前数据库状态:")
    await show_database_status()
    
    # 1. 测试创建新线程
    print(f"\n1️⃣ 测试创建新线程...")
    thread_id = str(uuid.uuid4())
    thread_data: ThreadDict = {
        "id": thread_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "name": "完整功能测试线程",
        "userId": test_user_id,
        "userIdentifier": test_user_identifier,
        "tags": ["test", "complete"],
        "metadata": {"test": "complete_functionality"},
        "steps": [],
        "elements": []
    }
    
    created_thread = await data_layer.create_thread(thread_data)
    print(f"✅ 线程创建成功: {created_thread['id']}")
    
    # 2. 测试获取线程
    print(f"\n2️⃣ 测试获取线程...")
    retrieved_thread = await data_layer.get_thread(thread_id)
    if retrieved_thread:
        print(f"✅ 线程获取成功: {retrieved_thread['name']}")
    else:
        print("❌ 线程获取失败")
        return
    
    # 3. 测试更新线程
    print(f"\n3️⃣ 测试更新线程...")
    new_name = "更新后的测试线程"
    new_metadata = {"updated": True, "test": "complete_functionality"}

    updated_thread = await data_layer.update_thread(thread_id, name=new_name, metadata=new_metadata)
    if updated_thread:
        print(f"✅ 线程更新成功: {updated_thread['name']}")
    else:
        print("❌ 线程更新失败")
    
    # 4. 测试列出线程
    print(f"\n4️⃣ 测试列出线程...")
    from chainlit.types import Pagination
    pagination = Pagination(first=10, cursor=None)
    thread_list = await data_layer.list_threads(pagination, None)
    print(f"✅ 找到 {len(thread_list.data)} 个线程")
    
    # 5. 测试获取线程作者
    print(f"\n5️⃣ 测试获取线程作者...")
    author = await data_layer.get_thread_author(thread_id)
    print(f"✅ 线程作者: {author}")
    
    # 6. 测试删除线程
    print(f"\n6️⃣ 测试删除线程...")
    await data_layer.delete_thread(thread_id)
    print(f"✅ 线程删除成功")
    
    # 7. 验证删除
    print(f"\n7️⃣ 验证线程已删除...")
    deleted_thread = await data_layer.get_thread(thread_id)
    if deleted_thread is None:
        print("✅ 线程确认已删除")
    else:
        print("❌ 线程删除失败")
    
    print(f"\n📊 测试后数据库状态:")
    await show_database_status()
    
    print(f"\n🎉 完整功能测试完成！")

async def show_database_status():
    """显示数据库状态"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 统计线程数量
    cursor.execute("SELECT COUNT(*) FROM threads")
    thread_count = cursor.fetchone()[0]
    
    # 获取最近的线程
    cursor.execute("""
        SELECT id, userIdentifier, name, createdAt 
        FROM threads 
        ORDER BY createdAt DESC 
        LIMIT 5
    """)
    recent_threads = cursor.fetchall()
    
    print(f"   线程总数: {thread_count}")
    if recent_threads:
        print(f"   最近的线程:")
        for thread in recent_threads:
            thread_id, user, name, created = thread
            short_id = thread_id[:8] + "..."
            display_name = name if name else "未命名"
            print(f"     - {short_id} | {user} | {display_name} | {created}")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(test_complete_functionality())
