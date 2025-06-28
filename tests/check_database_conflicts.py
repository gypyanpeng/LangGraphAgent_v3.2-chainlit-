#!/usr/bin/env python3
"""
检查数据库中的约束冲突问题
"""

import sqlite3
import os

def check_database_conflicts():
    """检查数据库中的重复数据和约束冲突"""
    
    # 检查 chainlit_history.db
    chainlit_db_path = "data/chainlit_history.db"
    if os.path.exists(chainlit_db_path):
        print(f"检查 {chainlit_db_path}...")
        try:
            conn = sqlite3.connect(chainlit_db_path)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"数据库表: {[table[0] for table in tables]}")
            
            # 检查threads表是否存在
            if ('threads',) in tables:
                # 检查重复的thread ID
                cursor.execute("SELECT id, COUNT(*) as count FROM threads GROUP BY id HAVING count > 1;")
                duplicates = cursor.fetchall()
                if duplicates:
                    print(f"发现重复的线程ID: {duplicates}")
                    
                    # 显示所有threads记录
                    cursor.execute("SELECT id, createdAt, name, userId FROM threads ORDER BY createdAt;")
                    all_threads = cursor.fetchall()
                    print("所有线程记录:")
                    for thread in all_threads:
                        print(f"  ID: {thread[0]}, 创建时间: {thread[1]}, 名称: {thread[2]}, 用户ID: {thread[3]}")
                else:
                    print("未发现重复的线程ID")
                    
                # 检查总记录数
                cursor.execute("SELECT COUNT(*) FROM threads;")
                count = cursor.fetchone()[0]
                print(f"线程总数: {count}")
            
            conn.close()
            
        except Exception as e:
            print(f"检查 {chainlit_db_path} 时出错: {e}")
    else:
        print(f"{chainlit_db_path} 不存在")
    
    # 检查其他数据库文件
    for db_file in ["data/agent_data.db", "data/agent_memory.db"]:
        if os.path.exists(db_file):
            print(f"\n检查 {db_file}...")
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"数据库表: {[table[0] for table in tables]}")
                
                conn.close()
            except Exception as e:
                print(f"检查 {db_file} 时出错: {e}")

if __name__ == "__main__":
    check_database_conflicts()
