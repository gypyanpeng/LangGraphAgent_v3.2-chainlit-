#!/usr/bin/env python3
"""
测试线程删除功能
"""
import asyncio
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlite_data_layer import SQLiteDataLayer

async def test_delete_thread():
    """测试删除线程功能"""
    data_layer = SQLiteDataLayer(db_path="../data/chainlit_history.db")
    
    # 首先查看现有的线程
    print("=== 删除前的线程列表 ===")
    conn = sqlite3.connect("../data/chainlit_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, createdAt FROM threads")
    threads = cursor.fetchall()
    for thread in threads:
        print(f"线程ID: {thread[0]}, 名称: {thread[1]}, 创建时间: {thread[2]}")
    conn.close()
    
    if not threads:
        print("没有找到任何线程")
        return
    
    # 选择第一个线程进行删除测试
    thread_to_delete = threads[0][0]
    print(f"\n=== 尝试删除线程: {thread_to_delete} ===")
    
    try:
        # 调用删除方法
        await data_layer.delete_thread(thread_to_delete)
        print("删除方法调用成功")
        
        # 验证删除结果
        print("\n=== 删除后的线程列表 ===")
        conn = sqlite3.connect("../data/chainlit_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, createdAt FROM threads")
        remaining_threads = cursor.fetchall()
        for thread in remaining_threads:
            print(f"线程ID: {thread[0]}, 名称: {thread[1]}, 创建时间: {thread[2]}")
        conn.close()
        
        if len(remaining_threads) < len(threads):
            print("✅ 线程删除成功！")
        else:
            print("❌ 线程删除失败，数量没有变化")
            
    except Exception as e:
        print(f"❌ 删除过程中出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(test_delete_thread())
