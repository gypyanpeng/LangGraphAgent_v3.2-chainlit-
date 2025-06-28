#!/usr/bin/env python3
"""
分析线程中所有步骤的类型
"""

import sqlite3
import sys
import os

def analyze_step_types():
    """分析步骤类型"""
    print("🧪 分析线程中的步骤类型")
    print("=" * 50)
    
    # 测试线程ID - 使用一个有真实对话的线程
    test_thread_id = "e0ee9273-16b9-49ed-8738-b03b4f058ff2"

    # 测试 get_thread 方法
    print(f"\n🔧 测试修改后的 get_thread 方法...")
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sqlite_data_layer import SQLiteDataLayer

    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    data_layer = SQLiteDataLayer(db_path=db_path)

    import asyncio
    async def test_get_thread():
        try:
            full_thread = await data_layer.get_thread(test_thread_id)
            if full_thread:
                steps = full_thread.get("steps", [])
                print(f"✅ 成功获取线程数据，包含 {len(steps)} 个步骤")

                # 统计有效消息数量
                valid_messages = 0
                for step in steps:
                    step_output = step.get("output", "")
                    step_type = step.get("type", "")
                    if step_output and "会话已恢复" not in step_output:
                        if step_type in ["user_message", "assistant_message"]:
                            valid_messages += 1

                print(f"📊 有效消息数量: {valid_messages}")
                return True
            else:
                print(f"❌ 无法获取线程 {test_thread_id} 的数据")
                return False
        except Exception as e:
            print(f"❌ 获取线程数据时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    success = asyncio.run(test_get_thread())

    if success:
        print(f"\n🎯 测试完成！修改后的 get_thread 方法成功处理了孤立的步骤数据")
        print(f"✅ 线程 {test_thread_id} 现在可以正常加载历史消息了")
    else:
        print(f"\n❌ 测试失败，需要进一步调试")
    
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"🔍 分析线程: {test_thread_id}")
    
    # 查询所有步骤
    cursor.execute("""
        SELECT type, name, output, createdAt
        FROM steps 
        WHERE threadId = ? 
        ORDER BY createdAt ASC
    """, (test_thread_id,))
    
    steps = cursor.fetchall()
    print(f"📝 总步骤数: {len(steps)}")
    
    # 统计步骤类型
    type_counts = {}
    valid_messages = 0
    
    for i, (step_type, name, output, created_at) in enumerate(steps, 1):
        # 统计类型
        type_counts[step_type] = type_counts.get(step_type, 0) + 1
        
        # 检查是否是有效消息
        content = output if output else name
        if content and "会话已恢复" not in content:
            if step_type in ["user_message", "assistant_message"]:
                valid_messages += 1
        
        # 显示前10个步骤的详细信息
        if i <= 10:
            content = output if output else name
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"  {i}. [{step_type}] {content_preview}")
    
    print(f"\n📊 步骤类型统计:")
    for step_type, count in sorted(type_counts.items()):
        print(f"  - {step_type}: {count} 个")
    
    print(f"\n✅ 有效消息数量 (user_message + assistant_message): {valid_messages}")
    
    # 查看非标准类型的步骤
    print(f"\n🔍 查看非标准类型的步骤内容:")
    cursor.execute("""
        SELECT type, name, output
        FROM steps 
        WHERE threadId = ? 
        AND type NOT IN ('user_message', 'assistant_message')
        AND (output IS NOT NULL AND output != '' AND output NOT LIKE '%会话已恢复%')
        ORDER BY createdAt ASC
        LIMIT 5
    """, (test_thread_id,))
    
    non_standard_steps = cursor.fetchall()
    for i, (step_type, name, output) in enumerate(non_standard_steps, 1):
        content = output if output else name
        content_preview = content[:100] + "..." if len(content) > 100 else content
        print(f"  {i}. [{step_type}] {content_preview}")
    
    conn.close()
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    analyze_step_types()
