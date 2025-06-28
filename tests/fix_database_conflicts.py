#!/usr/bin/env python3
"""
修复数据库约束冲突问题
"""

import sqlite3
import os
import uuid
import logging
from datetime import datetime, timezone

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_database_conflicts():
    """修复数据库中的约束冲突问题"""
    
    # 检查并修复 chainlit_history.db
    chainlit_db_path = "data/chainlit_history.db"
    if os.path.exists(chainlit_db_path):
        logger.info(f"修复 {chainlit_db_path}...")
        try:
            conn = sqlite3.connect(chainlit_db_path)
            cursor = conn.cursor()
            
            # 检查是否有重复的线程ID
            cursor.execute("SELECT id, COUNT(*) as count FROM threads GROUP BY id HAVING count > 1;")
            duplicates = cursor.fetchall()
            
            if duplicates:
                logger.warning(f"发现重复的线程ID: {duplicates}")
                
                # 对于每个重复的ID，保留最早的记录，删除其他记录
                for thread_id, count in duplicates:
                    logger.info(f"处理重复线程ID: {thread_id} (共{count}条记录)")
                    
                    # 获取所有重复记录，按创建时间排序
                    cursor.execute("""
                        SELECT id, createdAt, name, userId, userIdentifier 
                        FROM threads 
                        WHERE id = ? 
                        ORDER BY createdAt ASC
                    """, (thread_id,))
                    records = cursor.fetchall()
                    
                    # 保留第一条记录，删除其他记录
                    if len(records) > 1:
                        logger.info(f"保留最早的记录: {records[0]}")
                        
                        # 删除重复记录（除了第一条）
                        for i in range(1, len(records)):
                            # 先删除相关的steps和elements
                            cursor.execute("DELETE FROM steps WHERE threadId = ?", (thread_id,))
                            cursor.execute("DELETE FROM elements WHERE threadId = ?", (thread_id,))
                            logger.info(f"删除重复记录: {records[i]}")
                        
                        # 删除重复的threads记录（保留一条）
                        cursor.execute("""
                            DELETE FROM threads 
                            WHERE id = ? AND rowid NOT IN (
                                SELECT MIN(rowid) FROM threads WHERE id = ?
                            )
                        """, (thread_id, thread_id))
                
                conn.commit()
                logger.info("重复记录清理完成")
            else:
                logger.info("未发现重复的线程ID")
            
            # 验证修复结果
            cursor.execute("SELECT id, COUNT(*) as count FROM threads GROUP BY id HAVING count > 1;")
            remaining_duplicates = cursor.fetchall()
            if remaining_duplicates:
                logger.error(f"仍有重复记录: {remaining_duplicates}")
            else:
                logger.info("✅ 数据库约束冲突已修复")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"修复 {chainlit_db_path} 时出错: {e}")
    else:
        logger.info(f"{chainlit_db_path} 不存在，跳过修复")

def add_unique_constraint_handling():
    """为线程创建添加唯一约束处理"""
    logger.info("添加唯一约束处理逻辑...")
    
    # 这个函数将在sqlite_data_layer.py中实现
    # 这里只是记录需要做的修改
    modifications = [
        "1. 在create_thread方法中添加重试逻辑",
        "2. 当遇到UNIQUE constraint failed时，生成新的线程ID",
        "3. 添加最大重试次数限制",
        "4. 记录详细的错误日志"
    ]
    
    for mod in modifications:
        logger.info(f"  - {mod}")

if __name__ == "__main__":
    logger.info("开始修复数据库约束冲突问题...")
    fix_database_conflicts()
    add_unique_constraint_handling()
    logger.info("修复完成！")
