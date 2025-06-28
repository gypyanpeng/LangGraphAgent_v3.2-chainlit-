#!/usr/bin/env python3
"""
测试新会话保存功能
验证新创建的会话是否能正确保存到数据库
"""

import asyncio
import sqlite3
import requests
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
DB_PATH = "./data/chainlit_history.db"

def check_database_before():
    """检查测试前的数据库状态"""
    logger.info("🔍 检查测试前的数据库状态")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM threads")
        thread_count = cursor.fetchone()[0]
        logger.info(f"📊 测试前线程数量: {thread_count}")
        
        cursor.execute("SELECT id, name, createdAt FROM threads ORDER BY createdAt DESC LIMIT 5")
        recent_threads = cursor.fetchall()
        logger.info(f"📋 最近的线程:")
        for thread_id, name, created_at in recent_threads:
            logger.info(f"  - {thread_id}: {name} (创建时间: {created_at})")
            
        return thread_count
    finally:
        conn.close()

def check_database_after():
    """检查测试后的数据库状态"""
    logger.info("🔍 检查测试后的数据库状态")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM threads")
        thread_count = cursor.fetchone()[0]
        logger.info(f"📊 测试后线程数量: {thread_count}")
        
        cursor.execute("SELECT id, name, createdAt FROM threads ORDER BY createdAt DESC LIMIT 5")
        recent_threads = cursor.fetchall()
        logger.info(f"📋 最近的线程:")
        for thread_id, name, created_at in recent_threads:
            logger.info(f"  - {thread_id}: {name} (创建时间: {created_at})")
            
        return thread_count
    finally:
        conn.close()

def login_and_get_token():
    """登录并获取认证令牌"""
    logger.info("🔐 步骤1: 登录获取认证")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    logger.info(f"登录响应状态: {response.status_code}")
    
    if response.status_code == 200:
        logger.info("✅ 登录成功")
        
        # 从 Set-Cookie 头中提取 access_token
        cookies = response.headers.get('Set-Cookie', '')
        logger.info(f"Cookie: {cookies}")
        
        # 提取 access_token
        if 'access_token=' in cookies:
            token_start = cookies.find('access_token=') + len('access_token=')
            token_end = cookies.find(';', token_start)
            if token_end == -1:
                token_end = len(cookies)
            access_token = cookies[token_start:token_end]
            logger.info(f"🎯 提取到 access_token: {access_token[:50]}...")
            return access_token
        else:
            logger.error("❌ 未找到 access_token")
            return None
    else:
        logger.error(f"❌ 登录失败: {response.status_code}")
        logger.error(f"响应内容: {response.text}")
        return None

def test_new_session_creation():
    """测试新会话创建和保存"""
    logger.info("\n🧪 测试新会话创建和保存")
    logger.info("=" * 50)
    
    # 获取认证令牌
    access_token = login_and_get_token()
    if not access_token:
        logger.error("❌ 无法获取认证令牌，测试终止")
        return False
    
    # 检查测试前的数据库状态
    thread_count_before = check_database_before()
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 模拟创建新会话的过程
    logger.info("📝 步骤2: 模拟创建新会话")
    
    # 1. 首先获取用户信息
    user_response = requests.get(f"{BASE_URL}/user", headers=headers)
    logger.info(f"获取用户信息状态: {user_response.status_code}")
    
    if user_response.status_code != 200:
        logger.error(f"❌ 获取用户信息失败: {user_response.text}")
        return False
    
    user_info = user_response.json()
    logger.info(f"✅ 用户信息: {user_info}")
    
    # 2. 创建新线程（模拟前端行为）
    thread_data = {
        "name": f"测试会话 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "userId": user_info["id"],
        "userIdentifier": user_info["identifier"],
        "tags": [],
        "metadata": {}
    }
    
    logger.info(f"📤 创建线程数据: {thread_data}")
    
    # 使用 POST /project/threads 创建新线程
    create_response = requests.post(
        f"{BASE_URL}/project/threads", 
        headers=headers,
        json=thread_data
    )
    
    logger.info(f"创建线程响应状态: {create_response.status_code}")
    logger.info(f"创建线程响应内容: {create_response.text}")
    
    if create_response.status_code == 200:
        logger.info("✅ 线程创建请求成功")
        
        # 等待一下让数据库操作完成
        import time
        time.sleep(2)
        
        # 检查测试后的数据库状态
        thread_count_after = check_database_after()
        
        if thread_count_after > thread_count_before:
            logger.info(f"✅ 新会话保存成功！线程数量从 {thread_count_before} 增加到 {thread_count_after}")
            return True
        else:
            logger.error(f"❌ 新会话未保存到数据库！线程数量仍为 {thread_count_after}")
            return False
    else:
        logger.error(f"❌ 线程创建失败: {create_response.text}")
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试新会话保存功能")
    logger.info("=" * 60)
    
    try:
        success = test_new_session_creation()
        
        if success:
            logger.info("\n🎉 测试通过：新会话保存功能正常工作！")
        else:
            logger.error("\n❌ 测试失败：新会话保存功能存在问题！")
            
    except Exception as e:
        logger.error(f"\n💥 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
