#!/usr/bin/env python3
"""
数据库清理脚本
安全删除不需要的数据库文件
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_database_usage(db_path):
    """检查数据库是否被使用（是否有数据）"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            conn.close()
            return False, "数据库为空（无表）"
        
        # 检查每个表是否有数据
        total_rows = 0
        table_info = []
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            total_rows += count
            table_info.append(f"{table_name}: {count} 行")
        
        conn.close()
        
        if total_rows == 0:
            return False, f"数据库为空（{len(tables)} 个表，0 行数据）"
        else:
            return True, f"数据库有数据（{len(tables)} 个表，{total_rows} 行数据）\n  " + "\n  ".join(table_info)
            
    except Exception as e:
        return None, f"检查失败: {str(e)}"

def analyze_databases():
    """分析所有数据库文件"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        print("❌ data 目录不存在")
        return
    
    print("🔍 分析数据库文件...")
    print("=" * 60)
    
    db_files = list(data_dir.glob("*.db"))
    
    if not db_files:
        print("📁 data 目录中没有找到数据库文件")
        return
    
    analysis_results = {}
    
    for db_file in sorted(db_files):
        print(f"\n📊 分析: {db_file.name}")
        print("-" * 40)
        
        file_size = db_file.stat().st_size
        print(f"文件大小: {file_size:,} 字节 ({file_size/1024:.1f} KB)")
        
        has_data, info = check_database_usage(str(db_file))
        
        if has_data is None:
            print(f"⚠️  {info}")
            analysis_results[db_file.name] = "error"
        elif has_data:
            print(f"✅ {info}")
            analysis_results[db_file.name] = "used"
        else:
            print(f"🗑️  {info}")
            analysis_results[db_file.name] = "empty"
    
    return analysis_results

def cleanup_empty_databases(analysis_results, dry_run=True):
    """清理空数据库文件"""
    data_dir = Path("data")
    
    empty_files = [name for name, status in analysis_results.items() if status == "empty"]
    
    if not empty_files:
        print("\n✅ 没有发现需要清理的空数据库文件")
        return
    
    print(f"\n🗑️  发现 {len(empty_files)} 个空数据库文件:")
    for file_name in empty_files:
        print(f"  - {file_name}")
    
    if dry_run:
        print("\n🔍 这是预览模式，不会实际删除文件")
        print("如要实际删除，请运行: python scripts/cleanup_databases.py --execute")
        return
    
    # 实际删除
    print(f"\n⚠️  准备删除 {len(empty_files)} 个文件...")
    
    for file_name in empty_files:
        file_path = data_dir / file_name
        try:
            # 创建备份
            backup_path = data_dir / f"{file_name}.backup"
            file_path.rename(backup_path)
            print(f"✅ 已备份并删除: {file_name} -> {file_name}.backup")
        except Exception as e:
            print(f"❌ 删除失败 {file_name}: {str(e)}")

def show_recommendations():
    """显示优化建议"""
    print("\n" + "=" * 60)
    print("📋 数据库优化建议")
    print("=" * 60)
    
    recommendations = [
        "🔄 定期备份重要数据库文件:",
        "  - agent_memory.db (LangGraph 状态数据)",
        "  - chainlit_history.db (用户界面数据)",
        "  - agent_data.db (业务数据)",
        "",
        "🗑️  可以安全删除的文件:",
        "  - chainlit.db (如果为空)",
        "  - *.db-journal (临时文件)",
        "",
        "⚡ 性能优化文件（保留）:",
        "  - *.db-shm (共享内存文件)",
        "  - *.db-wal (预写日志文件)",
        "",
        "📊 监控建议:",
        "  - 定期检查数据库大小",
        "  - 监控查询性能",
        "  - 设置自动备份计划"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    """主函数"""
    print("🧹 LangGraph Agent 数据库清理工具")
    print("=" * 60)
    
    # 检查是否在正确的目录
    if not Path("chainlit_app.py").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 分析数据库
    analysis_results = analyze_databases()
    
    if not analysis_results:
        return
    
    # 检查命令行参数
    execute_cleanup = "--execute" in sys.argv
    
    # 清理空数据库
    cleanup_empty_databases(analysis_results, dry_run=not execute_cleanup)
    
    # 显示建议
    show_recommendations()
    
    print(f"\n🎉 分析完成！")

if __name__ == "__main__":
    main()
