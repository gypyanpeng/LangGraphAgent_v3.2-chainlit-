#!/usr/bin/env python3
"""
检查特定线程的详细信息
"""

import sqlite3
import os
import json

def check_thread_details(thread_id):
    """检查特定线程的详细信息"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"🔍 检查线程: {thread_id}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取线程信息
        cursor.execute("""
            SELECT id, name, createdAt, userIdentifier 
            FROM threads 
            WHERE id = ?
        """, (thread_id,))
        thread = cursor.fetchone()
        
        if not thread:
            print(f"❌ 线程不存在: {thread_id}")
            return
        
        print(f"📋 线程信息:")
        print(f"  ID: {thread[0]}")
        print(f"  名称: {thread[1] or '未命名'}")
        print(f"  用户: {thread[3]}")
        print(f"  创建时间: {thread[2]}")
        
        # 获取该线程的所有步骤
        cursor.execute("""
            SELECT id, name, type, output, input, createdAt 
            FROM steps 
            WHERE threadId = ? 
            ORDER BY createdAt
        """, (thread_id,))
        steps = cursor.fetchall()
        
        print(f"\n👣 步骤总数: {len(steps)}")
        
        # 统计重复内容
        content_counts = {}
        
        for i, step in enumerate(steps):
            step_id, name, step_type, output, input_data, step_created_at = step
            print(f"\n步骤 {i+1}:")
            print(f"  ID: {step_id[:8]}...")
            print(f"  名称: {name}")
            print(f"  类型: {step_type}")
            print(f"  输出: {output[:100] if output else 'None'}...")
            print(f"  时间: {step_created_at}")
            
            # 统计重复内容
            content_key = f"{step_type}:{output[:50] if output else 'None'}"
            content_counts[content_key] = content_counts.get(content_key, 0) + 1
        
        print(f"\n📊 内容重复统计:")
        for content, count in content_counts.items():
            if count > 1:
                print(f"  🔄 重复 {count} 次: {content}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查时出错: {e}")

if __name__ == "__main__":
    # 检查用户当前访问的线程
    thread_id = "02cf7633-da50-4d31-ba5a-1924ebadf762"
    check_thread_details(thread_id)
