#!/usr/bin/env python3
"""
测试 Chainlit 修复效果
验证数据库表结构和中文编码问题是否已解决
"""

import sqlite3
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_structure():
    """测试数据库表结构是否正确"""
    print("🔍 测试数据库表结构...")
    
    try:
        # 连接数据库
        conn = sqlite3.connect("./data/chainlit_history.db")
        cursor = conn.cursor()
        
        # 检查 steps 表结构
        cursor.execute("PRAGMA table_info(steps)")
        columns = cursor.fetchall()
        
        # 检查是否包含 defaultOpen 列
        column_names = [col[1] for col in columns]
        
        print(f"📋 Steps 表包含的列: {column_names}")
        
        if "defaultOpen" in column_names:
            print("✅ defaultOpen 列存在 - 数据库结构修复成功")
        else:
            print("❌ defaultOpen 列不存在 - 数据库结构需要修复")
            return False
            
        # 检查其他必要的列
        required_columns = [
            "id", "name", "type", "threadId", "parentId", 
            "streaming", "metadata", "tags", "input", "output", 
            "createdAt", "start", "end", "generation", "showInput", 
            "language", "defaultOpen"
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        if missing_columns:
            print(f"⚠️ 缺少列: {missing_columns}")
        else:
            print("✅ 所有必要的列都存在")
        
        conn.close()
        return len(missing_columns) == 0
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_config_file():
    """测试配置文件是否正确"""
    print("\n🔍 测试 Chainlit 配置文件...")
    
    try:
        # 检查配置文件是否存在
        config_path = ".chainlit/config.toml"
        if not os.path.exists(config_path):
            print("❌ 配置文件不存在")
            return False
            
        # 读取配置文件内容
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查关键配置
        checks = [
            ('name = "LangGraph Agent"', "应用名称使用英文"),
            ('[UI.avatar]', "头像配置存在"),
            ('author = "👤"', "用户头像使用emoji"),
            ('assistant = "🤖"', "助手头像使用emoji")
        ]
        
        all_passed = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - 未找到: {check}")
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def test_chainlit_app_structure():
    """测试 chainlit_app.py 结构"""
    print("\n🔍 测试 Chainlit 应用结构...")
    
    try:
        # 检查关键函数是否存在
        with open("chainlit_app.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('@cl.on_chat_start', "会话开始处理器"),
            ('@cl.on_chat_resume', "会话恢复处理器"),
            ('@cl.on_message', "消息处理器"),
            ('@cl.data_layer', "数据层配置"),
            ('defaultOpen INTEGER DEFAULT 0', "数据库表结构包含 defaultOpen 列")
        ]
        
        all_passed = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - 未找到: {check}")
                all_passed = False
                
        return all_passed
        
    except Exception as e:
        print(f"❌ 应用结构测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试 Chainlit 修复效果\n")
    
    tests = [
        ("数据库表结构", test_database_structure),
        ("配置文件", test_config_file),
        ("应用结构", test_chainlit_app_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {test_name}")
        print('='*50)
        
        result = test_func()
        results.append((test_name, result))
        
        if result:
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    # 总结
    print(f"\n{'='*50}")
    print("测试总结")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Chainlit 修复成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
