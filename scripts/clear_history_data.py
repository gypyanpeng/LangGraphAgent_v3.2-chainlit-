#!/usr/bin/env python3
"""
历史数据清理脚本 - 安全清理所有历史记录
"""

import os
import sqlite3
import shutil
from datetime import datetime

def backup_databases():
    """备份数据库文件"""
    print("📦 创建数据库备份...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    backup_dir = os.path.join(data_dir, 'backups')
    
    # 创建备份目录
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    db_files = ['chainlit_history.db', 'agent_memory.db', 'agent_data.db']
    backup_files = []
    
    for db_file in db_files:
        src_path = os.path.join(data_dir, db_file)
        if os.path.exists(src_path):
            backup_name = f"{db_file}.backup_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)
            shutil.copy2(src_path, backup_path)
            backup_files.append(backup_path)
            print(f"   ✅ 备份: {db_file} -> {backup_name}")
    
    return backup_files

def clear_chainlit_history():
    """清理 Chainlit 历史数据"""
    print("\n🧹 清理 Chainlit 历史数据...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    db_path = os.path.join(data_dir, 'chainlit_history.db')
    
    if not os.path.exists(db_path):
        print("   ⚠️  chainlit_history.db 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取清理前的统计
        cursor.execute("SELECT COUNT(*) FROM threads")
        threads_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM steps")
        steps_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM elements")
        elements_before = cursor.fetchone()[0]
        
        print(f"   清理前: {threads_before} 个线程, {steps_before} 个步骤, {elements_before} 个元素")
        
        # 清理数据（保留表结构）
        cursor.execute("DELETE FROM elements")
        cursor.execute("DELETE FROM steps")
        cursor.execute("DELETE FROM threads")
        
        # 重置自增序列（如果存在）
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('threads', 'steps', 'elements')")
        except:
            pass  # 如果没有 sqlite_sequence 表就忽略
        
        conn.commit()
        
        # 获取清理后的统计
        cursor.execute("SELECT COUNT(*) FROM threads")
        threads_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM steps")
        steps_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM elements")
        elements_after = cursor.fetchone()[0]
        
        print(f"   清理后: {threads_after} 个线程, {steps_after} 个步骤, {elements_after} 个元素")
        print(f"   ✅ 成功清理 {threads_before} 个线程和 {steps_before} 个步骤")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 清理失败: {e}")

def clear_agent_memory():
    """清理 LangGraph Agent 内存数据"""
    print("\n🧹 清理 LangGraph Agent 内存数据...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    db_path = os.path.join(data_dir, 'agent_memory.db')
    
    if not os.path.exists(db_path):
        print("   ⚠️  agent_memory.db 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取清理前的统计
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        checkpoints_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM writes")
        writes_before = cursor.fetchone()[0]
        
        print(f"   清理前: {checkpoints_before} 个检查点, {writes_before} 个写入记录")
        
        # 清理数据（保留表结构）
        cursor.execute("DELETE FROM writes")
        cursor.execute("DELETE FROM checkpoints")
        
        conn.commit()
        
        # 获取清理后的统计
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        checkpoints_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM writes")
        writes_after = cursor.fetchone()[0]
        
        print(f"   清理后: {checkpoints_after} 个检查点, {writes_after} 个写入记录")
        print(f"   ✅ 成功清理 {checkpoints_before} 个检查点和 {writes_before} 个写入记录")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 清理失败: {e}")

def clear_agent_data():
    """清理 Agent 数据"""
    print("\n🧹 清理 Agent 数据...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    db_path = os.path.join(data_dir, 'agent_data.db')
    
    if not os.path.exists(db_path):
        print("   ⚠️  agent_data.db 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取清理前的统计
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversations_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        memories_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions_before = cursor.fetchone()[0]
        
        print(f"   清理前: {conversations_before} 个对话, {memories_before} 个记忆, {sessions_before} 个会话")
        
        # 清理数据（保留表结构）
        cursor.execute("DELETE FROM conversations")
        cursor.execute("DELETE FROM memories")
        cursor.execute("DELETE FROM sessions")
        
        # 重置自增序列
        try:
            cursor.execute("DELETE FROM sqlite_sequence")
        except:
            pass  # 如果没有 sqlite_sequence 表就忽略
        
        conn.commit()
        
        # 获取清理后的统计
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversations_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        memories_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions_after = cursor.fetchone()[0]
        
        print(f"   清理后: {conversations_after} 个对话, {memories_after} 个记忆, {sessions_after} 个会话")
        print(f"   ✅ 成功清理所有 Agent 数据")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 清理失败: {e}")

def vacuum_databases():
    """压缩数据库文件"""
    print("\n🗜️  压缩数据库文件...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    db_files = ['chainlit_history.db', 'agent_memory.db', 'agent_data.db']
    
    for db_file in db_files:
        db_path = os.path.join(data_dir, db_file)
        if os.path.exists(db_path):
            try:
                # 获取压缩前的大小
                size_before = os.path.getsize(db_path) / 1024 / 1024
                
                conn = sqlite3.connect(db_path)
                conn.execute("VACUUM")
                conn.close()
                
                # 获取压缩后的大小
                size_after = os.path.getsize(db_path) / 1024 / 1024
                
                print(f"   ✅ {db_file}: {size_before:.2f} MB -> {size_after:.2f} MB")
                
            except Exception as e:
                print(f"   ❌ {db_file} 压缩失败: {e}")

def main():
    print("🗑️  历史数据清理工具")
    print("=" * 60)
    print("⚠️  警告：此操作将清除所有历史对话和检查点数据！")
    print("📦 数据将先备份到 data/backups/ 目录")
    print("=" * 60)
    
    # 确认操作
    confirm = input("\n是否继续清理？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("❌ 操作已取消")
        return
    
    # 1. 备份数据库
    backup_files = backup_databases()
    
    # 2. 清理各个数据库
    clear_chainlit_history()
    clear_agent_memory()
    clear_agent_data()
    
    # 3. 压缩数据库
    vacuum_databases()
    
    print(f"\n🎉 清理完成！")
    print(f"📦 备份文件保存在: data/backups/")
    for backup_file in backup_files:
        print(f"   - {os.path.basename(backup_file)}")
    
    print(f"\n💡 提示:")
    print(f"   - 如需恢复数据，请使用备份文件")
    print(f"   - 重启应用后将从全新状态开始")
    print(f"   - 所有历史对话和检查点已清除")

if __name__ == "__main__":
    main()
