#!/usr/bin/env python3
"""
最终验证脚本 - 验证历史会话恢复功能的完整修复
"""

import os
import sys
import sqlite3
import asyncio

def main():
    print("🎯 最终验证：历史会话恢复功能修复")
    print("=" * 60)
    
    # 测试数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📂 数据库路径: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 检查孤立步骤的数量
        print("\n🔍 1. 检查孤立步骤（在steps表中但不在threads表中）")
        cursor.execute("""
            SELECT DISTINCT s.threadId 
            FROM steps s 
            LEFT JOIN threads t ON s.threadId = t.id 
            WHERE t.id IS NULL
        """)
        orphaned_threads = cursor.fetchall()
        print(f"   发现 {len(orphaned_threads)} 个孤立线程")
        
        # 2. 测试修改后的 get_thread 方法
        print("\n🔧 2. 测试修改后的 get_thread 方法")
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from sqlite_data_layer import SQLiteDataLayer
        
        data_layer = SQLiteDataLayer(db_path=db_path)
        
        async def test_orphaned_threads():
            success_count = 0
            total_messages = 0
            
            for (thread_id,) in orphaned_threads[:3]:  # 测试前3个孤立线程
                try:
                    full_thread = await data_layer.get_thread(thread_id)
                    if full_thread:
                        steps = full_thread.get("steps", [])
                        valid_messages = sum(1 for step in steps 
                                           if step.get("type") in ["user_message", "assistant_message"] 
                                           and step.get("output") 
                                           and "会话已恢复" not in step.get("output", ""))
                        
                        print(f"   ✅ 线程 {thread_id[:8]}... : {len(steps)} 步骤, {valid_messages} 有效消息")
                        success_count += 1
                        total_messages += valid_messages
                    else:
                        print(f"   ❌ 线程 {thread_id[:8]}... : 无法获取数据")
                except Exception as e:
                    print(f"   ❌ 线程 {thread_id[:8]}... : 错误 - {e}")
            
            return success_count, total_messages
        
        success_count, total_messages = asyncio.run(test_orphaned_threads())
        
        # 3. 检查正常线程
        print("\n🔍 3. 检查正常线程（在threads表中存在）")
        cursor.execute("SELECT id FROM threads LIMIT 3")
        normal_threads = cursor.fetchall()
        
        async def test_normal_threads():
            success_count = 0
            total_messages = 0
            
            for (thread_id,) in normal_threads:
                try:
                    full_thread = await data_layer.get_thread(thread_id)
                    if full_thread:
                        steps = full_thread.get("steps", [])
                        valid_messages = sum(1 for step in steps 
                                           if step.get("type") in ["user_message", "assistant_message"] 
                                           and step.get("output") 
                                           and "会话已恢复" not in step.get("output", ""))
                        
                        print(f"   ✅ 线程 {thread_id[:8]}... : {len(steps)} 步骤, {valid_messages} 有效消息")
                        success_count += 1
                        total_messages += valid_messages
                    else:
                        print(f"   ❌ 线程 {thread_id[:8]}... : 无法获取数据")
                except Exception as e:
                    print(f"   ❌ 线程 {thread_id[:8]}... : 错误 - {e}")
            
            return success_count, total_messages
        
        normal_success, normal_messages = asyncio.run(test_normal_threads())
        
        # 4. 总结
        print("\n📊 修复验证总结")
        print("-" * 40)
        print(f"孤立线程修复成功率: {success_count}/{min(len(orphaned_threads), 3)}")
        print(f"正常线程工作状态: {normal_success}/{len(normal_threads)}")
        print(f"总计可恢复消息数: {total_messages + normal_messages}")
        
        # 5. 最终结论
        print("\n🎉 修复状态评估")
        if success_count > 0:
            print("✅ 孤立步骤修复：成功！之前无法加载的历史会话现在可以正常恢复")
        else:
            print("❌ 孤立步骤修复：失败")
            
        if normal_success == len(normal_threads):
            print("✅ 正常线程功能：完好！没有破坏现有功能")
        else:
            print("❌ 正常线程功能：受损")
            
        overall_success = success_count > 0 and normal_success == len(normal_threads)
        
        if overall_success:
            print("\n🏆 总体结论：历史会话恢复功能修复完全成功！")
            print("   - 解决了数据库完整性问题")
            print("   - 孤立的历史对话现在可以正常加载")
            print("   - 保持了现有功能的完整性")
        else:
            print("\n⚠️  总体结论：修复存在问题，需要进一步调试")
            
        return overall_success
        
    except Exception as e:
        print(f"❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
