#!/usr/bin/env python3
"""
检查数据库当前状态
"""

import sqlite3
import os

def check_database_status():
    """检查数据库当前状态"""
    db_path = "./data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取线程数量
        cursor.execute("SELECT COUNT(*) FROM threads")
        thread_count = cursor.fetchone()[0]
        
        print(f"📊 当前数据库状态:")
        print(f"   线程总数: {thread_count}")
        
        # 获取所有线程详情
        cursor.execute("SELECT id, userId, userIdentifier, name, createdAt FROM threads ORDER BY createdAt DESC")
        threads = cursor.fetchall()

        print(f"\n📋 线程列表:")
        for i, thread in enumerate(threads, 1):
            thread_id, user_id, user_identifier, name, created_at = thread
            print(f"   {i}. ID: {thread_id[:8]}... | 用户: {user_identifier} | 名称: {name or '未命名'} | 创建时间: {created_at}")

        # 查询最近的线程（最近1小时内）
        cursor.execute("""
            SELECT id, userId, userIdentifier, name, createdAt
            FROM threads
            WHERE datetime(createdAt) > datetime('now', '-1 hour')
            ORDER BY createdAt DESC
        """)
        recent_threads = cursor.fetchall()

        if recent_threads:
            print(f"\n🕐 最近1小时内的线程 ({len(recent_threads)}个):")
            for i, thread in enumerate(recent_threads, 1):
                thread_id, user_id, user_identifier, name, created_at = thread
                print(f"   {i}. ID: {thread_id} | 用户: {user_identifier} | 名称: {name or '未命名'} | 创建时间: {created_at}")
        else:
            print(f"\n🕐 最近1小时内没有新线程")
        
        # 获取步骤数量
        cursor.execute("SELECT COUNT(*) FROM steps")
        step_count = cursor.fetchone()[0]
        print(f"\n📝 步骤总数: {step_count}")
        
        # 获取用户数量
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 用户总数: {user_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 查询数据库失败: {e}")

if __name__ == "__main__":
    check_database_status()
