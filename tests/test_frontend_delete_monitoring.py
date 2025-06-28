#!/usr/bin/env python3
"""
前端删除功能监控测试 - 监控 Chainlit 前端删除操作是否调用后端方法
"""

import asyncio
import sqlite3
import time
import sys
import os

# 添加父目录到路径以导入 sqlite_data_layer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlite_data_layer import SQLiteDataLayer

async def monitor_delete_operations():
    """监控删除操作 - 检查数据库变化"""
    print("🔍 开始监控前端删除操作...")
    print("📋 请在浏览器中尝试删除历史会话，我将监控数据库变化")
    print("=" * 60)
    
    # 初始化数据层
    data_layer = SQLiteDataLayer(db_path="./data/chainlit_history.db")
    
    # 获取初始线程列表
    initial_threads = await data_layer.list_threads(None, None)
    print(f"📊 当前数据库中的线程数量: {len(initial_threads)}")
    
    for thread in initial_threads:
        print(f"  - 线程ID: {thread['id'][:8]}... | 名称: {thread.get('name', '未命名')}")
    
    print("\n⏳ 监控中... (按 Ctrl+C 停止)")
    
    try:
        while True:
            await asyncio.sleep(2)  # 每2秒检查一次
            
            # 获取当前线程列表
            current_threads = await data_layer.list_threads(None, None)
            
            # 检查是否有线程被删除
            if len(current_threads) != len(initial_threads):
                print(f"\n🎯 检测到变化！")
                print(f"   之前线程数: {len(initial_threads)}")
                print(f"   当前线程数: {len(current_threads)}")
                
                # 找出被删除的线程
                initial_ids = {t['id'] for t in initial_threads}
                current_ids = {t['id'] for t in current_threads}
                deleted_ids = initial_ids - current_ids
                
                if deleted_ids:
                    print(f"✅ 删除成功！被删除的线程ID: {list(deleted_ids)}")
                else:
                    print(f"➕ 新增线程！")
                
                # 更新初始状态
                initial_threads = current_threads
                print("\n📊 更新后的线程列表:")
                for thread in current_threads:
                    print(f"  - 线程ID: {thread['id'][:8]}... | 名称: {thread.get('name', '未命名')}")
                print("\n⏳ 继续监控...")
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")

async def test_direct_delete():
    """直接测试删除功能"""
    print("\n🧪 直接测试删除功能...")
    
    data_layer = SQLiteDataLayer(db_path="./data/chainlit_history.db")
    
    # 获取所有线程
    threads = await data_layer.list_threads(None, None)
    
    if not threads:
        print("❌ 没有找到可删除的线程")
        return
    
    # 选择第一个线程进行删除测试
    test_thread = threads[0]
    thread_id = test_thread['id']
    
    print(f"🎯 测试删除线程: {thread_id[:8]}...")
    
    try:
        # 执行删除
        await data_layer.delete_thread(thread_id)
        print("✅ 后端删除方法执行成功！")
        
        # 验证删除结果
        remaining_threads = await data_layer.list_threads(None, None)
        if len(remaining_threads) == len(threads) - 1:
            print("✅ 删除验证成功！线程已从数据库中移除")
        else:
            print("❌ 删除验证失败！线程仍在数据库中")
            
    except Exception as e:
        print(f"❌ 删除测试失败: {e}")

if __name__ == "__main__":
    print("🔧 前端删除功能监控测试")
    print("=" * 60)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 监控模式 - 监控前端删除操作")
    print("2. 直接测试 - 直接测试后端删除方法")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        asyncio.run(monitor_delete_operations())
    elif choice == "2":
        asyncio.run(test_direct_delete())
    else:
        print("❌ 无效选择")
