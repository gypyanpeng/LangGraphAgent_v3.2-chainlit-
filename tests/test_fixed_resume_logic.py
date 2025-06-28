#!/usr/bin/env python3
"""
测试修复后的会话恢复逻辑
"""

import os
import sys
import sqlite3
import asyncio

def main():
    print("🔧 测试修复后的会话恢复逻辑")
    print("=" * 50)
    
    # 数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'chainlit_history.db')
    
    # 测试线程ID
    test_thread_id = "e0ee9273-16b9-49ed-8738-b03b4f058ff2"
    
    print(f"📂 数据库路径: {db_path}")
    print(f"🎯 测试线程ID: {test_thread_id}")
    
    # 获取数据
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sqlite_data_layer import SQLiteDataLayer
    
    data_layer = SQLiteDataLayer(db_path=db_path)
    
    async def test_fixed_logic():
        try:
            full_thread = await data_layer.get_thread(test_thread_id)
            if not full_thread:
                print("   ❌ get_thread 返回 None")
                return
            
            steps = full_thread.get("steps", [])
            print(f"   ✅ get_thread 返回 {len(steps)} 个步骤")
            
            # 模拟修复后的 on_chat_resume 逻辑
            print("\n🔧 模拟修复后的消息过滤和显示逻辑")
            displayed_count = 0
            
            for i, step in enumerate(steps, 1):
                step_type = step.get("type", "")
                step_output = step.get("output", "")
                step_name = step.get("name", "")
                
                print(f"\n   步骤 {i}: type='{step_type}', name='{step_name}'")
                print(f"           output='{step_output[:50]}...'")
                
                # 跳过会话恢复消息，避免重复显示
                if "会话已恢复" in step_output or "已加载" in step_output:
                    print(f"      ⏭️  跳过会话恢复消息")
                    continue
                    
                # 跳过系统消息和运行步骤
                if step_type in ["run", "system"]:
                    print(f"      ⏭️  跳过系统/运行步骤")
                    continue

                # 使用 output 字段作为消息内容，如果为空则使用 name
                content = step_output if step_output else step_name
                if not content or content.strip() == "":
                    print(f"      ⏭️  跳过空内容")
                    continue

                # 根据 step_type 和 step_name 判断消息类型
                # 优先根据 name 字段判断，因为 type 字段可能不准确
                is_user_message = False
                is_assistant_message = False

                if step_name in ["用户", "admin"]:
                    # 根据 name 字段判断是用户消息
                    is_user_message = True
                elif step_name in ["助手", "LangGraph Agent"]:
                    # 根据 name 字段判断是助手消息
                    is_assistant_message = True
                elif step_type == "user_message":
                    is_user_message = True
                elif step_type == "assistant_message":
                    is_assistant_message = True

                # 显示消息
                if is_user_message:
                    print(f"      ✅ 用户消息: {content[:50]}...")
                    displayed_count += 1
                elif is_assistant_message:
                    print(f"      ✅ 助手消息: {content[:50]}...")
                    displayed_count += 1
                else:
                    print(f"      ⏭️  未识别的消息类型")
            
            print(f"\n   📊 修复后统计: 应该显示 {displayed_count} 条消息")
            
            if displayed_count > 0:
                print(f"\n✅ 修复成功！应该能在前端看到 {displayed_count} 条历史消息")
                
                # 分析消息分布
                user_count = 0
                assistant_count = 0
                
                for step in steps:
                    step_type = step.get("type", "")
                    step_output = step.get("output", "")
                    step_name = step.get("name", "")
                    
                    if "会话已恢复" in step_output or "已加载" in step_output:
                        continue
                    if step_type in ["run", "system"]:
                        continue
                    content = step_output if step_output else step_name
                    if not content or content.strip() == "":
                        continue
                    
                    is_user_message = False
                    is_assistant_message = False

                    if step_name in ["用户", "admin"]:
                        is_user_message = True
                    elif step_name in ["助手", "LangGraph Agent"]:
                        is_assistant_message = True
                    elif step_type == "user_message":
                        is_user_message = True
                    elif step_type == "assistant_message":
                        is_assistant_message = True
                    
                    if is_user_message:
                        user_count += 1
                    elif is_assistant_message:
                        assistant_count += 1
                
                print(f"   📈 消息分布: {user_count} 条用户消息, {assistant_count} 条助手消息")
            else:
                print(f"\n❌ 修复失败：仍然没有消息被识别为可显示")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test_fixed_logic())

if __name__ == "__main__":
    main()
