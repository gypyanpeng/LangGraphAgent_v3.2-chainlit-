#!/usr/bin/env python3
"""
测试 Ollama 适配器在 LangGraph 中的工作情况
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_loader import load_llm_from_config
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

async def test_simple_ollama_langgraph():
    """测试简单的 Ollama + LangGraph 集成"""
    print("🧪 测试 Ollama + LangGraph 集成...")
    
    try:
        # 1. 加载 Ollama 模型
        print("\n1️⃣ 加载 Ollama 模型...")
        llm = load_llm_from_config(provider="ollama")
        print(f"✅ 模型加载成功: {llm.model_name}")
        
        # 2. 创建简单的 LangGraph 工作流
        print("\n2️⃣ 创建 LangGraph 工作流...")
        
        async def call_model(state: MessagesState):
            """调用模型"""
            messages = state["messages"]
            response = await llm.ainvoke(messages)
            return {"messages": [response]}
        
        # 创建工作流
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        
        # 编译工作流
        app = workflow.compile()
        print("✅ LangGraph 工作流创建成功")
        
        # 3. 测试工作流
        print("\n3️⃣ 测试工作流...")
        
        # 准备输入
        inputs = {
            "messages": [HumanMessage(content="你好，请简单介绍一下自己")]
        }
        
        # 运行工作流
        result = await app.ainvoke(inputs)
        
        if result and "messages" in result:
            last_message = result["messages"][-1]
            print(f"✅ 工作流运行成功")
            print(f"   AI回复: {last_message.content[:100]}...")
            return True
        else:
            print("❌ 工作流返回结果异常")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_streaming_ollama_langgraph():
    """测试流式 Ollama + LangGraph"""
    print("\n🔄 测试流式 Ollama + LangGraph...")
    
    try:
        # 加载模型
        llm = load_llm_from_config(provider="ollama")
        
        # 创建流式工作流
        async def call_model_stream(state: MessagesState):
            """流式调用模型"""
            messages = state["messages"]
            response = await llm.ainvoke(messages)  # 先用非流式测试
            return {"messages": [response]}
        
        # 创建工作流
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model_stream)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        
        # 编译工作流
        app = workflow.compile()
        
        # 准备输入
        inputs = {
            "messages": [HumanMessage(content="请用一句话介绍人工智能")]
        }
        
        # 流式运行
        print("🔄 开始流式处理...")
        async for output in app.astream(inputs):
            for key, value in output.items():
                if "messages" in value:
                    last_message = value["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        print(f"   流式输出: {last_message.content[:50]}...")
                        break
        
        print("✅ 流式处理成功")
        return True
        
    except Exception as e:
        print(f"❌ 流式测试失败: {e}")
        return False

async def test_with_persistence():
    """测试带持久化的 Ollama + LangGraph"""
    print("\n💾 测试带持久化的 Ollama + LangGraph...")
    
    try:
        # 导入持久化相关模块
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        
        # 加载模型
        llm = load_llm_from_config(provider="ollama")
        
        # 创建检查点存储器
        checkpointer = AsyncSqliteSaver.from_conn_string("sqlite:///./data/test_ollama_memory.db")
        
        # 创建工作流
        async def call_model(state: MessagesState):
            messages = state["messages"]
            response = await llm.ainvoke(messages)
            return {"messages": [response]}
        
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", call_model)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        
        # 编译带持久化的工作流
        app = workflow.compile(checkpointer=checkpointer)
        print("✅ 带持久化的工作流创建成功")
        
        # 测试会话
        thread_id = "test_ollama_thread"
        config = {"configurable": {"thread_id": thread_id}}
        
        # 第一轮对话
        inputs1 = {
            "messages": [HumanMessage(content="我叫张三")]
        }
        
        result1 = await app.ainvoke(inputs1, config=config)
        print(f"✅ 第一轮对话成功")
        
        # 第二轮对话（测试记忆）
        inputs2 = {
            "messages": [HumanMessage(content="我叫什么名字？")]
        }
        
        result2 = await app.ainvoke(inputs2, config=config)
        print(f"✅ 第二轮对话成功")
        print(f"   AI回复: {result2['messages'][-1].content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 持久化测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 Ollama + LangGraph 集成测试")
    print("=" * 50)
    
    # 基础测试
    success1 = await test_simple_ollama_langgraph()
    
    # 流式测试
    success2 = await test_streaming_ollama_langgraph()
    
    # 持久化测试
    success3 = await test_with_persistence()
    
    print("\n" + "=" * 50)
    print("🎯 测试结果总结:")
    print(f"   基础集成: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"   流式处理: {'✅ 成功' if success2 else '❌ 失败'}")
    print(f"   持久化功能: {'✅ 成功' if success3 else '❌ 失败'}")
    
    if success1 and success2 and success3:
        print("\n🎉 所有测试通过！Ollama 适配器可以正常工作")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
