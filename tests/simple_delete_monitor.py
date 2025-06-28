#!/usr/bin/env python3
"""
简化的删除监控脚本 - 直接查询数据库
"""

import sqlite3
import time
import os

def get_thread_count():
    """获取当前线程数量"""
    db_path = "./data/chainlit_history.db"
    if not os.path.exists(db_path):
        return 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM threads")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"❌ 查询数据库失败: {e}")
        return 0

def get_thread_list():
    """获取线程列表"""
    db_path = "./data/chainlit_history.db"
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, createdAt FROM threads ORDER BY createdAt DESC")
        threads = cursor.fetchall()
        conn.close()
        return threads
    except Exception as e:
        print(f"❌ 查询线程列表失败: {e}")
        return []

def monitor_delete_operations():
    """监控删除操作"""
    print("🔍 开始监控前端删除操作...")
    print("📋 请在浏览器中尝试删除历史会话，我将监控数据库变化")
    print("=" * 60)
    
    # 获取初始状态
    initial_count = get_thread_count()
    initial_threads = get_thread_list()
    
    print(f"📊 当前数据库中的线程数量: {initial_count}")
    
    for thread in initial_threads:
        thread_id, name, created_at = thread
        print(f"  - 线程ID: {thread_id[:8]}... | 名称: {name or '未命名'} | 创建时间: {created_at}")
    
    print("\n⏳ 监控中... (按 Ctrl+C 停止)")
    
    try:
        while True:
            time.sleep(2)  # 每2秒检查一次
            
            current_count = get_thread_count()
            
            if current_count != initial_count:
                print(f"\n🎯 检测到变化！")
                print(f"   之前线程数: {initial_count}")
                print(f"   当前线程数: {current_count}")
                
                current_threads = get_thread_list()
                
                if current_count < initial_count:
                    print("✅ 检测到删除操作！")
                    
                    # 找出被删除的线程
                    initial_ids = {t[0] for t in initial_threads}
                    current_ids = {t[0] for t in current_threads}
                    deleted_ids = initial_ids - current_ids
                    
                    if deleted_ids:
                        print(f"🗑️  被删除的线程ID: {list(deleted_ids)}")
                        print("✅ 前端删除功能正常工作！")
                    
                elif current_count > initial_count:
                    print("➕ 检测到新增线程！")
                
                # 更新状态
                initial_count = current_count
                initial_threads = current_threads
                
                print("\n📊 更新后的线程列表:")
                for thread in current_threads:
                    thread_id, name, created_at = thread
                    print(f"  - 线程ID: {thread_id[:8]}... | 名称: {name or '未命名'} | 创建时间: {created_at}")
                print("\n⏳ 继续监控...")
            
    except KeyboardInterrupt:
        print("\n\n🛑 监控已停止")

def test_direct_delete():
    """直接测试删除功能"""
    print("🧪 直接测试删除功能...")
    
    threads = get_thread_list()
    
    if not threads:
        print("❌ 没有找到可删除的线程")
        return
    
    # 选择第一个线程进行删除测试
    test_thread = threads[0]
    thread_id = test_thread[0]
    
    print(f"🎯 测试删除线程: {thread_id[:8]}...")
    
    try:
        # 直接执行 SQL 删除
        db_path = "./data/chainlit_history.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        conn.commit()
        conn.close()
        
        print("✅ 直接 SQL 删除执行成功！")
        
        # 验证删除结果
        remaining_count = get_thread_count()
        if remaining_count == len(threads) - 1:
            print("✅ 删除验证成功！线程已从数据库中移除")
        else:
            print("❌ 删除验证失败！线程仍在数据库中")
            
    except Exception as e:
        print(f"❌ 删除测试失败: {e}")

if __name__ == "__main__":
    print("🔧 简化删除功能监控测试")
    print("=" * 60)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 监控模式 - 监控前端删除操作")
    print("2. 直接测试 - 直接测试 SQL 删除")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        monitor_delete_operations()
    elif choice == "2":
        test_direct_delete()
    else:
        print("❌ 无效选择")
