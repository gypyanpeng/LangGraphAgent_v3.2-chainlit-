#!/usr/bin/env python3
"""
检查特定线程是否存在
"""

import sqlite3
import os

def check_specific_thread(thread_id_prefix):
    """检查特定线程是否存在"""
    db_path = "./data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查找包含特定前缀的线程
        cursor.execute("SELECT id, name, createdAt FROM threads WHERE id LIKE ?", (f"{thread_id_prefix}%",))
        matching_threads = cursor.fetchall()
        
        print(f"🔍 查找线程ID前缀: {thread_id_prefix}")
        
        if matching_threads:
            print(f"✅ 找到 {len(matching_threads)} 个匹配的线程:")
            for thread in matching_threads:
                thread_id, name, created_at = thread
                print(f"   - ID: {thread_id}")
                print(f"     名称: {name or '未命名'}")
                print(f"     创建时间: {created_at}")
        else:
            print("❌ 没有找到匹配的线程")
        
        # 获取最新的几个线程
        print(f"\n📋 最新的5个线程:")
        cursor.execute("SELECT id, name, createdAt FROM threads ORDER BY createdAt DESC LIMIT 5")
        recent_threads = cursor.fetchall()
        
        for i, thread in enumerate(recent_threads, 1):
            thread_id, name, created_at = thread
            print(f"   {i}. ID: {thread_id[:8]}... | 名称: {name or '未命名'} | 创建时间: {created_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查询数据库失败: {e}")

if __name__ == "__main__":
    # 检查新创建的线程
    check_specific_thread("26178fcd")
