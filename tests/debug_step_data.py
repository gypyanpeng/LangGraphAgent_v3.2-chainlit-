#!/usr/bin/env python3
"""
调试步骤数据保存问题
"""

import sqlite3
import os
import json

def debug_step_data():
    """调试步骤数据"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"🔍 调试步骤数据: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最新的线程
        cursor.execute("SELECT id, name FROM threads ORDER BY createdAt DESC LIMIT 1")
        thread = cursor.fetchone()
        if not thread:
            print("❌ 没有找到线程")
            return
        
        thread_id, thread_name = thread
        print(f"📋 最新线程: {thread_id}")
        print(f"📝 线程名称: {thread_name}")
        
        # 获取该线程的所有步骤
        cursor.execute("""
            SELECT id, name, type, output, input, createdAt, metadata, tags
            FROM steps 
            WHERE threadId = ? 
            ORDER BY createdAt
        """, (thread_id,))
        steps = cursor.fetchall()
        
        print(f"\n👣 步骤总数: {len(steps)}")
        
        for i, step in enumerate(steps):
            step_id, name, step_type, output, input_data, created_at, metadata, tags = step
            print(f"\n步骤 {i+1}:")
            print(f"  ID: {step_id}")
            print(f"  名称: {name}")
            print(f"  类型: {step_type}")
            print(f"  输入: {input_data[:100] if input_data else 'None'}...")
            print(f"  输出: {output[:100] if output else 'None'}...")
            print(f"  创建时间: {created_at}")
            print(f"  元数据: {metadata[:100] if metadata else 'None'}...")
            print(f"  标签: {tags}")
        
        # 检查是否有用户消息和助手消息
        cursor.execute("""
            SELECT type, COUNT(*) 
            FROM steps 
            WHERE threadId = ? 
            GROUP BY type
        """, (thread_id,))
        type_counts = cursor.fetchall()
        
        print(f"\n📊 步骤类型统计:")
        for step_type, count in type_counts:
            print(f"  {step_type}: {count}")
        
        # 检查是否有非空的输出
        cursor.execute("""
            SELECT COUNT(*) 
            FROM steps 
            WHERE threadId = ? AND output IS NOT NULL AND output != ''
        """, (thread_id,))
        non_empty_output_count = cursor.fetchone()[0]
        print(f"\n📝 有内容的输出: {non_empty_output_count}")
        
        # 检查是否有非空的输入
        cursor.execute("""
            SELECT COUNT(*) 
            FROM steps 
            WHERE threadId = ? AND input IS NOT NULL AND input != ''
        """, (thread_id,))
        non_empty_input_count = cursor.fetchone()[0]
        print(f"📝 有内容的输入: {non_empty_input_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 调试时出错: {e}")

def check_chainlit_step_creation():
    """检查Chainlit步骤创建机制"""
    print(f"\n🔍 检查Chainlit步骤创建机制")
    print("=" * 60)
    
    # 检查是否有Chainlit的回调函数正确设置
    try:
        import chainlit as cl
        from sqlite_data_layer import SQLiteDataLayer
        
        print("✅ Chainlit和SQLiteDataLayer导入成功")
        
        # 检查数据层配置
        data_layer = SQLiteDataLayer()
        print("✅ SQLiteDataLayer实例化成功")
        
        # 检查数据库表结构
        db_path = "data/chainlit_history.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取steps表的结构
            cursor.execute("PRAGMA table_info(steps)")
            columns = cursor.fetchall()
            print(f"\n📋 steps表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
            
            conn.close()
        
    except Exception as e:
        print(f"❌ 检查Chainlit机制时出错: {e}")

if __name__ == "__main__":
    debug_step_data()
    check_chainlit_step_creation()
