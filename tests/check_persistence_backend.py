#!/usr/bin/env python3
"""
检查数据持久化后端状态
"""

import sqlite3
import os
import json
from datetime import datetime

def check_chainlit_database():
    """检查Chainlit数据库中的历史数据"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"📊 检查Chainlit数据库: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 数据库表: {[table[0] for table in tables]}")
        
        # 检查线程数据
        if ('threads',) in tables:
            cursor.execute("SELECT COUNT(*) FROM threads;")
            thread_count = cursor.fetchone()[0]
            print(f"🧵 线程总数: {thread_count}")
            
            if thread_count > 0:
                # 显示最近的线程
                cursor.execute("""
                    SELECT id, createdAt, name, userId, userIdentifier 
                    FROM threads 
                    ORDER BY createdAt DESC 
                    LIMIT 5
                """)
                recent_threads = cursor.fetchall()
                print("\n📝 最近的线程:")
                for thread in recent_threads:
                    print(f"  ID: {thread[0][:8]}...")
                    print(f"  创建时间: {thread[1]}")
                    print(f"  名称: {thread[2] or '未命名'}")
                    print(f"  用户: {thread[4]}")
                    print("  ---")
        
        # 检查步骤数据
        if ('steps',) in tables:
            cursor.execute("SELECT COUNT(*) FROM steps;")
            step_count = cursor.fetchone()[0]
            print(f"👣 步骤总数: {step_count}")
            
            if step_count > 0:
                # 显示最近的步骤
                cursor.execute("""
                    SELECT threadId, type, name, output, createdAt 
                    FROM steps 
                    ORDER BY createdAt DESC 
                    LIMIT 10
                """)
                recent_steps = cursor.fetchall()
                print("\n📋 最近的步骤:")
                for step in recent_steps:
                    print(f"  线程: {step[0][:8]}...")
                    print(f"  类型: {step[1]}")
                    print(f"  名称: {step[2]}")
                    print(f"  输出: {step[3][:100] if step[3] else 'None'}...")
                    print(f"  时间: {step[4]}")
                    print("  ---")
        
        # 检查用户数据
        if ('users',) in tables:
            cursor.execute("SELECT COUNT(*) FROM users;")
            user_count = cursor.fetchone()[0]
            print(f"👤 用户总数: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, identifier, createdAt FROM users;")
                users = cursor.fetchall()
                print("\n👥 用户列表:")
                for user in users:
                    print(f"  ID: {user[0]}")
                    print(f"  标识符: {user[1]}")
                    print(f"  创建时间: {user[2]}")
                    print("  ---")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")

def check_langgraph_database():
    """检查LangGraph持久化数据库"""
    db_path = "data/agent_memory.db"
    
    if not os.path.exists(db_path):
        print(f"❌ LangGraph数据库文件不存在: {db_path}")
        return
    
    print(f"\n🧠 检查LangGraph数据库: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 数据库表: {[table[0] for table in tables]}")
        
        # 检查checkpoints表
        if ('checkpoints',) in tables:
            cursor.execute("SELECT COUNT(*) FROM checkpoints;")
            checkpoint_count = cursor.fetchone()[0]
            print(f"💾 检查点总数: {checkpoint_count}")
            
            if checkpoint_count > 0:
                # 显示最近的检查点
                cursor.execute("""
                    SELECT thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id 
                    FROM checkpoints 
                    ORDER BY checkpoint_id DESC 
                    LIMIT 5
                """)
                recent_checkpoints = cursor.fetchall()
                print("\n📊 最近的检查点:")
                for cp in recent_checkpoints:
                    print(f"  线程ID: {cp[0]}")
                    print(f"  命名空间: {cp[1]}")
                    print(f"  检查点ID: {cp[2]}")
                    print(f"  父检查点: {cp[3] or 'None'}")
                    print("  ---")
        
        # 检查writes表
        if ('writes',) in tables:
            cursor.execute("SELECT COUNT(*) FROM writes;")
            write_count = cursor.fetchone()[0]
            print(f"✍️ 写入记录总数: {write_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查LangGraph数据库时出错: {e}")

def check_specific_thread_data(thread_id=None):
    """检查特定线程的详细数据"""
    if not thread_id:
        # 获取最新的线程ID
        db_path = "data/chainlit_history.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM threads ORDER BY createdAt DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                thread_id = result[0]
            conn.close()
    
    if not thread_id:
        print("❌ 没有找到线程ID")
        return
    
    print(f"\n🔍 检查线程详细数据: {thread_id}")
    print("=" * 60)
    
    # 检查Chainlit数据
    db_path = "data/chainlit_history.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取线程信息
        cursor.execute("SELECT * FROM threads WHERE id = ?", (thread_id,))
        thread = cursor.fetchone()
        if thread:
            print("📋 线程信息:")
            print(f"  ID: {thread[0]}")
            print(f"  创建时间: {thread[1]}")
            print(f"  名称: {thread[2] or '未命名'}")
            print(f"  用户ID: {thread[3]}")
            print(f"  用户标识符: {thread[4]}")
        
        # 获取步骤信息
        cursor.execute("SELECT * FROM steps WHERE threadId = ? ORDER BY createdAt", (thread_id,))
        steps = cursor.fetchall()
        print(f"\n👣 步骤数量: {len(steps)}")
        for i, step in enumerate(steps):
            print(f"  步骤 {i+1}:")
            print(f"    ID: {step[0]}")
            print(f"    类型: {step[2]}")
            print(f"    名称: {step[3]}")
            print(f"    输出: {step[4][:200] if step[4] else 'None'}...")
            print(f"    创建时间: {step[5]}")
        
        conn.close()

if __name__ == "__main__":
    print("🔍 开始检查数据持久化后端状态...")
    print()
    
    check_chainlit_database()
    check_langgraph_database()
    check_specific_thread_data()
    
    print("\n✅ 检查完成！")
