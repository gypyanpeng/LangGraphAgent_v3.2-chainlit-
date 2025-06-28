#!/usr/bin/env python3
"""
项目结构验证脚本
验证项目目录结构的完整性和一致性
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (缺失)")
        return False

def check_directory_exists(dir_path: str, description: str) -> bool:
    """检查目录是否存在"""
    if os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} (缺失)")
        return False

def get_file_size(file_path: str) -> str:
    """获取文件大小"""
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        if size > 1024 * 1024:
            return f"{size / (1024 * 1024):.1f}MB"
        elif size > 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size}B"
    return "N/A"

def main():
    """主验证函数"""
    print("🔍 LangGraph Agent 项目结构验证")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    all_checks_passed = True
    
    print("\n📄 核心文件检查:")
    core_files = [
        ("main.py", "CLI 主程序入口"),
        ("chainlit_app.py", "Chainlit Web 界面入口"),
        ("llm_loader.py", "LLM 加载器"),
        ("mcp_loader.py", "MCP 工具加载器"),
        ("sqlite_data_layer.py", "SQLite 数据层实现"),
        ("chainlit.md", "Chainlit 集成说明"),
        ("README.md", "项目说明文档"),
        ("pyproject.toml", "依赖管理"),
        (".env", "环境变量配置")
    ]
    
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    print("\n🗂️ 配置目录检查:")
    config_items = [
        ("config/", "应用配置目录"),
        ("config/llm_config.json", "LLM 提供商配置"),
        ("config/mcp_config.json", "MCP 工具配置"),
        ("config/persistence_config.json", "持久化配置"),
        (".chainlit/", "Chainlit 配置目录"),
        (".chainlit/config.toml", "Chainlit 配置文件"),
        (".chainlit/translations/", "界面翻译目录"),
        (".chainlit/translations/zh-CN.json", "中文界面翻译")
    ]
    
    for item_path, description in config_items:
        if item_path.endswith('/'):
            if not check_directory_exists(item_path, description):
                all_checks_passed = False
        else:
            if not check_file_exists(item_path, description):
                all_checks_passed = False
    
    print("\n💾 数据目录检查:")
    data_items = [
        ("data/", "数据存储目录"),
        ("data/agent_memory.db", "LangGraph 检查点数据库"),
        ("data/chainlit_history.db", "Chainlit 会话历史数据库"),
        ("data/agent_data.db", "业务数据存储")
    ]
    
    for item_path, description in data_items:
        if item_path.endswith('/'):
            if not check_directory_exists(item_path, description):
                all_checks_passed = False
        else:
            exists = check_file_exists(item_path, description)
            if exists:
                size = get_file_size(item_path)
                print(f"   📊 文件大小: {size}")
            if not exists:
                all_checks_passed = False
    
    print("\n📚 文档目录检查:")
    docs_items = [
        ("docs/", "项目文档目录"),
        ("docs/问题解决复盘报告.md", "问题解决过程记录"),
        ("docs/数据库文件分析报告.md", "数据库架构分析")
    ]
    
    for item_path, description in docs_items:
        if item_path.endswith('/'):
            if not check_directory_exists(item_path, description):
                all_checks_passed = False
        else:
            if not check_file_exists(item_path, description):
                all_checks_passed = False
    
    print("\n🧪 测试目录检查:")
    test_items = [
        ("tests/", "测试文件目录"),
        ("tests/test_thread_naming.py", "智能命名功能测试"),
        ("tests/test_system_integration.py", "系统集成测试"),
        ("tests/test_complete_functionality.py", "完整功能测试")
    ]
    
    for item_path, description in test_items:
        if item_path.endswith('/'):
            if not check_directory_exists(item_path, description):
                all_checks_passed = False
        else:
            if not check_file_exists(item_path, description):
                all_checks_passed = False
    
    print("\n🛠️ 脚本目录检查:")
    script_items = [
        ("scripts/", "实用工具脚本目录"),
        ("scripts/cleanup_databases.py", "数据库清理脚本"),
        ("scripts/verify_project_structure.py", "项目结构验证脚本")
    ]
    
    for item_path, description in script_items:
        if item_path.endswith('/'):
            if not check_directory_exists(item_path, description):
                all_checks_passed = False
        else:
            if not check_file_exists(item_path, description):
                all_checks_passed = False
    
    print("\n🚫 清理验证:")
    # 检查不应该存在的文件
    unwanted_items = [
        ("tests/.chainlit", "测试目录下的 Chainlit 配置（应已删除）"),
        ("tests/.files", "测试目录下的文件存储（应已删除）")
    ]
    
    for item_path, description in unwanted_items:
        if os.path.exists(item_path):
            print(f"⚠️  {description}: {item_path} (应该删除)")
            all_checks_passed = False
        else:
            print(f"✅ {description}: 已正确清理")
    
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 项目结构验证通过！所有必要文件和目录都存在。")
        return 0
    else:
        print("❌ 项目结构验证失败！请检查缺失的文件和目录。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
