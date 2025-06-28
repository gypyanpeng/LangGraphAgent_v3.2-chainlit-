#!/usr/bin/env python3
"""
清理数据库中的重复消息
"""

import sqlite3
import os
from datetime import datetime

def clean_duplicate_messages():
    """清理数据库中的重复消息"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"🧹 开始清理重复消息: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有线程
        cursor.execute("SELECT id, name FROM threads ORDER BY createdAt")
        threads = cursor.fetchall()
        
        total_deleted = 0
        
        for thread_id, thread_name in threads:
            print(f"\n🔍 处理线程: {thread_name or '未命名'} ({thread_id[:8]}...)")
            
            # 获取该线程的所有步骤，按时间排序
            cursor.execute("""
                SELECT id, name, type, output, createdAt 
                FROM steps 
                WHERE threadId = ? 
                ORDER BY createdAt
            """, (thread_id,))
            steps = cursor.fetchall()
            
            print(f"   📝 原始步骤数: {len(steps)}")
            
            # 找出重复的步骤
            seen_messages = set()
            steps_to_keep = []
            steps_to_delete = []
            
            for step in steps:
                step_id, name, step_type, output, created_at = step
                
                # 跳过会话恢复消息
                if "会话已恢复" in (output or ""):
                    steps_to_delete.append(step_id)
                    continue
                
                # 创建消息的唯一标识
                message_key = f"{step_type}:{name}:{output}"
                
                if message_key in seen_messages:
                    # 重复消息，标记删除
                    steps_to_delete.append(step_id)
                else:
                    # 第一次出现，保留
                    seen_messages.add(message_key)
                    steps_to_keep.append(step_id)
            
            # 删除重复的步骤
            if steps_to_delete:
                print(f"   🗑️ 删除重复步骤: {len(steps_to_delete)} 条")
                for step_id in steps_to_delete:
                    cursor.execute("DELETE FROM steps WHERE id = ?", (step_id,))
                total_deleted += len(steps_to_delete)
            
            print(f"   ✅ 保留步骤数: {len(steps_to_keep)}")
        
        # 提交更改
        conn.commit()
        conn.close()
        
        print(f"\n🎉 清理完成！")
        print(f"   总共删除: {total_deleted} 条重复步骤")
        
    except Exception as e:
        print(f"❌ 清理时出错: {e}")

def verify_cleanup():
    """验证清理结果"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"\n🔍 验证清理结果")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有线程及其步骤数
        cursor.execute("""
            SELECT t.id, t.name, COUNT(s.id) as step_count
            FROM threads t
            LEFT JOIN steps s ON t.id = s.threadId
            GROUP BY t.id, t.name
            ORDER BY t.createdAt DESC
        """)
        threads = cursor.fetchall()
        
        for thread_id, thread_name, step_count in threads:
            print(f"📋 {thread_name or '未命名'}: {step_count} 条步骤")
            
            # 检查是否还有重复
            cursor.execute("""
                SELECT type, name, output, COUNT(*) as count
                FROM steps 
                WHERE threadId = ?
                GROUP BY type, name, output
                HAVING COUNT(*) > 1
            """, (thread_id,))
            duplicates = cursor.fetchall()
            
            if duplicates:
                print(f"   ⚠️ 仍有重复:")
                for dup in duplicates:
                    print(f"      - {dup[0]}:{dup[1]} (重复{dup[3]}次)")
            else:
                print(f"   ✅ 无重复消息")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证时出错: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_cleanup()
    else:
        clean_duplicate_messages()
        verify_cleanup()
