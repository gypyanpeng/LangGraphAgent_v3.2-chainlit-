#!/usr/bin/env python3
"""
监控数据库变化
"""

import sqlite3
import os
import time
import json

def monitor_database_changes():
    """监控数据库变化"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"👀 开始监控数据库变化: {db_path}")
    print("请在Web界面发送一条测试消息...")
    print("=" * 60)
    
    # 记录初始状态
    initial_counts = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM threads")
        initial_counts['threads'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM steps")
        initial_counts['steps'] = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📊 初始状态:")
        print(f"  线程数: {initial_counts['threads']}")
        print(f"  步骤数: {initial_counts['steps']}")
        print()
        
    except Exception as e:
        print(f"❌ 获取初始状态失败: {e}")
        return
    
    # 监控变化
    last_step_count = initial_counts['steps']
    last_thread_count = initial_counts['threads']
    
    print("🔍 监控中... (按Ctrl+C停止)")
    
    try:
        while True:
            time.sleep(2)  # 每2秒检查一次
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查线程变化
            cursor.execute("SELECT COUNT(*) FROM threads")
            current_thread_count = cursor.fetchone()[0]
            
            # 检查步骤变化
            cursor.execute("SELECT COUNT(*) FROM steps")
            current_step_count = cursor.fetchone()[0]
            
            if current_thread_count != last_thread_count:
                print(f"🆕 新线程创建! 总数: {last_thread_count} -> {current_thread_count}")
                
                # 显示新线程信息
                cursor.execute("""
                    SELECT id, name, createdAt, userIdentifier 
                    FROM threads 
                    ORDER BY createdAt DESC 
                    LIMIT 1
                """)
                new_thread = cursor.fetchone()
                if new_thread:
                    print(f"   ID: {new_thread[0]}")
                    print(f"   名称: {new_thread[1] or '未命名'}")
                    print(f"   用户: {new_thread[3]}")
                    print(f"   时间: {new_thread[2]}")
                
                last_thread_count = current_thread_count
            
            if current_step_count != last_step_count:
                print(f"📝 新步骤创建! 总数: {last_step_count} -> {current_step_count}")
                
                # 显示新步骤信息
                cursor.execute("""
                    SELECT id, name, type, output, threadId, createdAt 
                    FROM steps 
                    ORDER BY createdAt DESC 
                    LIMIT 5
                """)
                new_steps = cursor.fetchall()
                
                for step in new_steps:
                    print(f"   步骤ID: {step[0][:8]}...")
                    print(f"   名称: {step[1]}")
                    print(f"   类型: {step[2]}")
                    print(f"   输出: {step[3][:100] if step[3] else 'None'}...")
                    print(f"   线程: {step[4][:8]}...")
                    print(f"   时间: {step[5]}")
                    print("   ---")
                
                last_step_count = current_step_count
            
            conn.close()
            
    except KeyboardInterrupt:
        print("\n⏹️ 监控已停止")
    except Exception as e:
        print(f"❌ 监控过程中出错: {e}")

def check_latest_thread_steps():
    """检查最新线程的步骤"""
    db_path = "data/chainlit_history.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    print(f"\n🔍 检查最新线程的步骤")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最新线程
        cursor.execute("""
            SELECT id, name, createdAt 
            FROM threads 
            ORDER BY createdAt DESC 
            LIMIT 1
        """)
        latest_thread = cursor.fetchone()
        
        if not latest_thread:
            print("❌ 没有找到线程")
            return
        
        thread_id, thread_name, created_at = latest_thread
        print(f"📋 最新线程:")
        print(f"  ID: {thread_id}")
        print(f"  名称: {thread_name or '未命名'}")
        print(f"  创建时间: {created_at}")
        
        # 获取该线程的所有步骤
        cursor.execute("""
            SELECT id, name, type, output, input, createdAt 
            FROM steps 
            WHERE threadId = ? 
            ORDER BY createdAt
        """, (thread_id,))
        steps = cursor.fetchall()
        
        print(f"\n👣 步骤总数: {len(steps)}")
        
        for i, step in enumerate(steps):
            step_id, name, step_type, output, input_data, step_created_at = step
            print(f"\n步骤 {i+1}:")
            print(f"  ID: {step_id[:8]}...")
            print(f"  名称: {name}")
            print(f"  类型: {step_type}")
            print(f"  输入: {input_data[:100] if input_data else 'None'}...")
            print(f"  输出: {output[:100] if output else 'None'}...")
            print(f"  时间: {step_created_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查时出错: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_latest_thread_steps()
    else:
        monitor_database_changes()
