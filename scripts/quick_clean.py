#!/usr/bin/env python3
"""
快速清理脚本 - 一键清理历史数据
"""

import os
import sqlite3
import shutil
from datetime import datetime

def quick_clean():
    """快速清理所有历史数据"""
    print("🚀 快速清理历史数据")
    print("=" * 40)
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # 统计清理前的数据
    total_cleaned = 0
    
    # 清理 Chainlit 历史
    chainlit_db = os.path.join(data_dir, 'chainlit_history.db')
    if os.path.exists(chainlit_db):
        try:
            conn = sqlite3.connect(chainlit_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM threads")
            threads = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM steps")
            steps = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM elements")
            cursor.execute("DELETE FROM steps")
            cursor.execute("DELETE FROM threads")
            
            conn.commit()
            conn.close()
            
            total_cleaned += threads + steps
            print(f"✅ Chainlit: 清理 {threads} 线程, {steps} 步骤")
            
        except Exception as e:
            print(f"❌ Chainlit 清理失败: {e}")
    
    # 清理 Agent 内存
    memory_db = os.path.join(data_dir, 'agent_memory.db')
    if os.path.exists(memory_db):
        try:
            conn = sqlite3.connect(memory_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM checkpoints")
            checkpoints = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM writes")
            writes = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM writes")
            cursor.execute("DELETE FROM checkpoints")
            
            conn.commit()
            conn.close()
            
            total_cleaned += checkpoints + writes
            print(f"✅ Agent 内存: 清理 {checkpoints} 检查点, {writes} 写入")
            
        except Exception as e:
            print(f"❌ Agent 内存清理失败: {e}")
    
    # 清理 Agent 数据
    agent_db = os.path.join(data_dir, 'agent_data.db')
    if os.path.exists(agent_db):
        try:
            conn = sqlite3.connect(agent_db)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM memories")
            cursor.execute("DELETE FROM sessions")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Agent 数据: 已清理")
            
        except Exception as e:
            print(f"❌ Agent 数据清理失败: {e}")
    
    print(f"\n🎉 清理完成！总计清理 {total_cleaned} 条记录")
    print(f"💡 重启应用后将从全新状态开始")

if __name__ == "__main__":
    quick_clean()
