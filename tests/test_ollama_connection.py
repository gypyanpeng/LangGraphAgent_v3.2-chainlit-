#!/usr/bin/env python3
"""
测试 Ollama 连接和模型调用
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_loader import load_llm_from_config
from langchain_core.messages import HumanMessage

async def test_ollama_connection():
    """测试 Ollama 连接"""
    print("🧪 开始测试 Ollama 连接...")
    
    try:
        # 1. 测试配置加载
        print("\n1️⃣ 测试配置加载...")
        llm = load_llm_from_config(provider="ollama")
        print(f"✅ LLM 配置加载成功")
        print(f"   模型: {llm.model_name}")
        print(f"   API Key: {llm.openai_api_key}")
        print(f"   Base URL: {llm.openai_api_base}")
        
        # 2. 测试简单调用
        print("\n2️⃣ 测试简单模型调用...")
        message = HumanMessage(content="你好，请简单回复一下")
        
        try:
            response = await llm.ainvoke([message])
            print(f"✅ 模型调用成功")
            print(f"   回复: {response.content[:100]}...")
        except Exception as e:
            print(f"❌ 模型调用失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            
            # 详细错误信息
            if hasattr(e, 'response'):
                print(f"   HTTP状态码: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
                print(f"   响应内容: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")
        
        # 3. 测试流式调用
        print("\n3️⃣ 测试流式调用...")
        try:
            stream_response = ""
            async for chunk in llm.astream([message]):
                stream_response += chunk.content
                if len(stream_response) > 50:  # 限制输出长度
                    break
            print(f"✅ 流式调用成功")
            print(f"   流式回复: {stream_response[:100]}...")
        except Exception as e:
            print(f"❌ 流式调用失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False
    
    return True

def test_ollama_api_direct():
    """直接测试 Ollama API"""
    print("\n🔧 直接测试 Ollama API...")
    
    import requests
    
    try:
        # 测试健康检查
        health_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if health_response.status_code == 200:
            print("✅ Ollama 服务运行正常")
            models = health_response.json().get("models", [])
            print(f"   可用模型数量: {len(models)}")
            for model in models:
                if "qwen3:1.7b" in model.get("name", ""):
                    print(f"   ✅ 找到目标模型: {model['name']}")
        else:
            print(f"❌ Ollama 服务异常: {health_response.status_code}")
            
        # 测试 OpenAI 兼容接口
        api_response = requests.post(
            "http://localhost:11434/v1/chat/completions",
            json={
                "model": "qwen3:1.7b",
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if api_response.status_code == 200:
            print("✅ OpenAI 兼容接口正常")
            result = api_response.json()
            print(f"   响应: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')[:50]}...")
        else:
            print(f"❌ OpenAI 兼容接口异常: {api_response.status_code}")
            print(f"   错误内容: {api_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Ollama 服务")
        print("   请确保 Ollama 正在运行: ollama serve")
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
        print("   Ollama 服务可能响应缓慢")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查配置文件
    config_path = "config/llm_config.json"
    if os.path.exists(config_path):
        print("✅ 配置文件存在")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            default_provider = config.get("default_provider")
            print(f"   默认提供商: {default_provider}")
            
            if "ollama" in config.get("models", {}):
                ollama_config = config["models"]["ollama"]
                print(f"   Ollama 配置:")
                print(f"     模型: {ollama_config.get('model_name')}")
                print(f"     URL: {ollama_config.get('base_url')}")
            else:
                print("❌ 未找到 Ollama 配置")
    else:
        print("❌ 配置文件不存在")
    
    # 检查依赖
    try:
        import langchain_openai
        print("✅ langchain_openai 已安装")
    except ImportError:
        print("❌ langchain_openai 未安装")

async def main():
    """主测试函数"""
    print("🚀 Ollama 连接诊断工具")
    print("=" * 50)
    
    # 环境检查
    check_environment()
    
    # 直接 API 测试
    test_ollama_api_direct()
    
    # LangChain 集成测试
    await test_ollama_connection()
    
    print("\n" + "=" * 50)
    print("🎯 诊断完成")

if __name__ == "__main__":
    asyncio.run(main())
