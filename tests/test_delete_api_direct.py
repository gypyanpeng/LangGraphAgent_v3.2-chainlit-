#!/usr/bin/env python3
"""
直接测试 Chainlit DELETE API 端点
模拟前端发送的 DELETE 请求到 /project/thread
"""

import asyncio
import aiohttp
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_delete_api():
    """测试 DELETE /project/thread API 端点"""
    
    base_url = "http://localhost:8000"
    
    # 首先登录获取认证
    async with aiohttp.ClientSession() as session:
        
        # 1. 登录获取认证 cookie
        logger.info("🔐 步骤1: 登录获取认证")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }

        access_token = None
        async with session.post(f"{base_url}/login", data=login_data) as response:
            logger.info(f"登录响应状态: {response.status}")
            if response.status == 200:
                logger.info("✅ 登录成功")
                # 打印 cookies 并提取 access_token
                for cookie in session.cookie_jar:
                    logger.info(f"Cookie: {cookie.key}={cookie.value}")
                    if cookie.key == "access_token":
                        access_token = cookie.value
                        logger.info(f"🎯 提取到 access_token: {access_token[:50]}...")
            else:
                logger.error(f"❌ 登录失败: {await response.text()}")
                return
        
        # 2. 获取用户信息验证认证状态
        logger.info("👤 步骤2: 验证用户认证状态")
        async with session.get(f"{base_url}/user") as response:
            logger.info(f"用户信息响应状态: {response.status}")
            if response.status == 200:
                user_data = await response.json()
                logger.info(f"✅ 当前用户: {user_data}")
            else:
                logger.error(f"❌ 获取用户信息失败: {await response.text()}")
                return
        
        # 3. 获取线程列表
        logger.info("📋 步骤3: 获取线程列表")
        threads_payload = {
            "pagination": {"first": 10, "cursor": None},
            "filter": {}
        }
        
        async with session.post(f"{base_url}/project/threads", json=threads_payload) as response:
            logger.info(f"线程列表响应状态: {response.status}")
            if response.status == 200:
                threads_data = await response.json()
                logger.info(f"✅ 获取到 {len(threads_data.get('data', []))} 个线程")
                
                # 选择第一个线程进行删除测试
                if threads_data.get('data'):
                    thread_to_delete = threads_data['data'][0]
                    thread_id = thread_to_delete['id']
                    logger.info(f"🎯 选择删除线程: {thread_id} - {thread_to_delete.get('name', 'Unnamed')}")
                    
                    # 4. 尝试删除线程
                    logger.info("🗑️ 步骤4: 尝试删除线程")
                    delete_payload = {
                        "threadId": thread_id
                    }
                    
                    # 添加必要的请求头，包括 Authorization
                    headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }

                    # 如果有 access_token，添加到 Authorization header
                    if access_token:
                        headers["Authorization"] = f"Bearer {access_token}"
                        logger.info(f"✅ 添加 Authorization header: Bearer {access_token[:50]}...")

                    # 打印当前的 cookies 以便调试
                    logger.info("当前会话 cookies:")
                    for cookie in session.cookie_jar:
                        logger.info(f"  {cookie.key}={cookie.value}")

                    logger.info(f"DELETE 请求头: {headers}")
                    logger.info(f"DELETE 请求体: {delete_payload}")

                    async with session.delete(f"{base_url}/project/thread",
                                            json=delete_payload,
                                            headers=headers) as response:
                        logger.info(f"删除响应状态: {response.status}")
                        response_text = await response.text()
                        logger.info(f"删除响应内容: {response_text}")
                        
                        if response.status == 200:
                            logger.info("✅ 删除成功！")
                        else:
                            logger.error(f"❌ 删除失败: {response.status} - {response_text}")
                            
                            # 打印响应头以便调试
                            logger.info("响应头:")
                            for name, value in response.headers.items():
                                logger.info(f"  {name}: {value}")
                else:
                    logger.warning("⚠️ 没有找到可删除的线程")
            else:
                logger.error(f"❌ 获取线程列表失败: {await response.text()}")

if __name__ == "__main__":
    asyncio.run(test_delete_api())
