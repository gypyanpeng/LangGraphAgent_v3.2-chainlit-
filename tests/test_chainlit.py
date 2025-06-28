#!/usr/bin/env python3
"""
测试 Chainlit 集成的脚本
"""

import os
import asyncio
import subprocess
import sys

def test_cli_mode():
    """测试 CLI 模式"""
    print("🧪 测试 CLI 模式...")
    try:
        # 运行一个简单的测试
        result = subprocess.run([
            sys.executable, "-c", 
            """
import asyncio
from main import initialize_agent

async def test():
    try:
        app, tools, session_manager = await initialize_agent()
        print(f"✅ CLI 模式测试成功 - 加载了 {len(tools)} 个工具")
        return True
    except Exception as e:
        print(f"❌ CLI 模式测试失败: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test())
    exit(0 if result else 1)
            """
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI 模式测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ CLI 模式测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ CLI 模式测试异常: {e}")
        return False

def test_chainlit_import():
    """测试 Chainlit 导入"""
    print("🧪 测试 Chainlit 导入...")
    try:
        import chainlit as cl
        print("✅ Chainlit 导入成功")
        return True
    except ImportError as e:
        print(f"❌ Chainlit 导入失败: {e}")
        return False

def test_chainlit_app():
    """测试 Chainlit 应用"""
    print("🧪 测试 Chainlit 应用...")
    try:
        # 检查 chainlit_app.py 是否可以导入
        result = subprocess.run([
            sys.executable, "-c", 
            """
try:
    import chainlit_app
    print("✅ chainlit_app.py 导入成功")
except Exception as e:
    print(f"❌ chainlit_app.py 导入失败: {e}")
    raise
            """
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Chainlit 应用测试通过")
            print(result.stdout)
            return True
        else:
            print("❌ Chainlit 应用测试失败")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Chainlit 应用测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🚀 LangGraph + Chainlit 集成测试")
    print("=" * 60)
    
    tests = [
        ("Chainlit 导入", test_chainlit_import),
        ("CLI 模式", test_cli_mode),
        ("Chainlit 应用", test_chainlit_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n💡 使用说明:")
        print("  CLI 模式: python main.py")
        print("  Web 模式: chainlit run chainlit_app.py")
    else:
        print("❌ 部分测试失败，请检查配置")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
