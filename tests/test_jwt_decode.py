#!/usr/bin/env python3
"""
测试 JWT token 解码
验证我们获取的 JWT token 是否有效
"""

import jwt
import json
from datetime import datetime

# 从测试脚本输出中获取的 JWT token
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGlmaWVyIjoiYWRtaW4iLCJkaXNwbGF5X25hbWUiOiJcdTdiYTFcdTc0MDZcdTU0NTgiLCJtZXRhZGF0YSI6e30sImV4cCI6MTc1MjM3MzIzNiwiaWF0IjoxNzUxMDc3MjM2fQ.mvmrjX5cCK4KMFUF1Ld-P6Jg8BQd6el0LkHW6OXsFd8"

print("🔍 JWT Token 分析")
print("=" * 50)

# 解码 JWT header 和 payload（不验证签名）
try:
    # 解码 header
    header = jwt.get_unverified_header(jwt_token)
    print(f"📋 JWT Header: {json.dumps(header, indent=2)}")
    
    # 解码 payload
    payload = jwt.decode(jwt_token, options={"verify_signature": False})
    print(f"📋 JWT Payload: {json.dumps(payload, indent=2)}")
    
    # 检查过期时间
    exp_timestamp = payload.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        current_datetime = datetime.now()
        print(f"⏰ Token 过期时间: {exp_datetime}")
        print(f"⏰ 当前时间: {current_datetime}")
        
        if current_datetime < exp_datetime:
            print("✅ Token 尚未过期")
        else:
            print("❌ Token 已过期")
    
    # 检查必要字段
    required_fields = ['identifier', 'exp', 'iat']
    for field in required_fields:
        if field in payload:
            print(f"✅ 包含必要字段: {field} = {payload[field]}")
        else:
            print(f"❌ 缺少必要字段: {field}")
            
except Exception as e:
    print(f"❌ JWT 解码失败: {e}")

print("\n🔍 尝试使用可能的密钥验证签名")
print("=" * 50)

# 尝试一些可能的密钥
possible_secrets = [
    "kyk^d^l^HjqGxrhX6^4jh>*u1gTPLKB0Z>lJletDUpQ6b3fI>$UHK9DVlxJS7Zvm",  # 从 .env 文件中的实际密钥
    "chainlit-secret",
    "secret",
    "your-secret",
    "CHAINLIT_AUTH_SECRET",
    "",
    "admin"
]

for secret in possible_secrets:
    try:
        decoded = jwt.decode(jwt_token, secret, algorithms=["HS256"])
        print(f"✅ 使用密钥 '{secret}' 验证成功!")
        print(f"   解码结果: {json.dumps(decoded, indent=2)}")
        break
    except jwt.InvalidSignatureError:
        print(f"❌ 密钥 '{secret}' 验证失败")
    except Exception as e:
        print(f"❌ 密钥 '{secret}' 验证出错: {e}")
