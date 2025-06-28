#!/usr/bin/env python3
"""
检查数据库状态 - 清理前的状态检查
"""

import os
import sqlite3
from datetime import datetime

def check_database_status():
    print("🔍 数据库状态检查")
    print("=" * 60)
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # 检查数据目录
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        return
    
    print(f"📂 数据目录: {data_dir}")
    
    # 列出所有数据库文件
    db_files = []
    for file in os.listdir(data_dir):
        if file.endswith('.db'):
            db_files.append(file)
    
    print(f"\n📋 发现的数据库文件:")
    for db_file in db_files:
        file_path = os.path.join(data_dir, db_file)
        file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
        print(f"   - {db_file} ({file_size:.2f} MB)")
    
    # 检查每个数据库的详细信息
    for db_file in db_files:
        db_path = os.path.join(data_dir, db_file)
        print(f"\n🔍 检查数据库: {db_file}")
        print("-" * 40)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"   表数量: {len(tables)}")
            
            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table_name}: {count} 条记录")
                except Exception as e:
                    print(f"   - {table_name}: 无法查询 ({e})")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ 无法连接数据库: {e}")
    
    print(f"\n📊 总结:")
    print(f"   - 发现 {len(db_files)} 个数据库文件")
    total_size = sum(os.path.getsize(os.path.join(data_dir, f)) for f in db_files) / 1024 / 1024
    print(f"   - 总大小: {total_size:.2f} MB")

if __name__ == "__main__":
    check_database_status()
