#!/usr/bin/env python3
"""
深度调试 Chainlit 认证问题
测试不同的认证方式
"""

import asyncio
import aiohttp
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_auth_methods():
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # 1. 登录获取认证 token
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

        if not access_token:
            logger.error("❌ 未能获取 access_token")
            return

        # 2. 测试不同的认证方式
        test_cases = [
            {
                "name": "仅使用 Cookie",
                "headers": {"Content-Type": "application/json"},
                "use_session": True
            },
            {
                "name": "仅使用 Authorization Header",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                "use_session": False
            },
            {
                "name": "同时使用 Cookie 和 Authorization Header",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                "use_session": True
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n🧪 测试 {i}: {test_case['name']}")
            logger.info("=" * 50)
            
            # 选择使用哪个 session
            if test_case['use_session']:
                test_session = session  # 带 cookie 的 session
            else:
                test_session = aiohttp.ClientSession()  # 新的 session，没有 cookie
            
            try:
                # 测试 GET /user
                logger.info("📋 测试 GET /user")
                async with test_session.get(f"{base_url}/user", headers=test_case['headers']) as response:
                    logger.info(f"GET /user 状态: {response.status}")
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"✅ 用户信息: {user_data}")
                    else:
                        logger.error(f"❌ GET /user 失败: {await response.text()}")

                # 测试 DELETE /project/thread
                logger.info("🗑️ 测试 DELETE /project/thread")
                delete_payload = {"threadId": "3a25e5d3-f5b4-4240-83cc-66d497eaab6c"}
                
                async with test_session.delete(
                    f"{base_url}/project/thread",
                    headers=test_case['headers'],
                    json=delete_payload
                ) as response:
                    logger.info(f"DELETE /project/thread 状态: {response.status}")
                    response_text = await response.text()
                    if response.status == 200:
                        logger.info(f"✅ 删除成功: {response_text}")
                    else:
                        logger.error(f"❌ 删除失败: {response_text}")
                        
                        # 打印响应头以获取更多信息
                        logger.info("响应头:")
                        for key, value in response.headers.items():
                            logger.info(f"  {key}: {value}")

            finally:
                # 如果创建了新的 session，需要关闭它
                if not test_case['use_session']:
                    await test_session.close()

if __name__ == "__main__":
    asyncio.run(test_auth_methods())
