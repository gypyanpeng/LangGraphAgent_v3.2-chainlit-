"""
Ollama 自定义适配器
解决 Ollama OpenAI 兼容接口的 502 错误问题
"""

import json
import requests
from typing import List, Dict, Any, Optional, AsyncIterator
from langchain_core.language_models.llms import LLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
import asyncio
import aiohttp

class OllamaLLM(LLM):
    """Ollama LLM 适配器 - 使用原生 API"""
    
    base_url: str = "http://localhost:11434"
    model: str = "qwen3:1.7b"
    temperature: float = 0.7
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用 Ollama 模型"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            raise Exception(f"Ollama API 调用失败: {e}")

class OllamaChatModel(BaseChatModel):
    """Ollama 聊天模型适配器 - 使用原生 API"""

    base_url: str = "http://localhost:11434"

    @property
    def api_url(self) -> str:
        """获取正确的 API URL"""
        # 移除 /v1 后缀，因为我们使用原生 API
        base = self.base_url.rstrip('/v1').rstrip('/')
        return base
    model: str = "qwen3:1.7b"
    temperature: float = 0.7
    streaming: bool = True

    @property
    def model_name(self) -> str:
        """返回模型名称"""
        return self.model

    @property
    def openai_api_key(self) -> str:
        """返回 API 密钥（兼容性）"""
        return "ollama"

    @property
    def openai_api_base(self) -> str:
        """返回 API 基础URL（兼容性）"""
        return self.base_url

    def bind_tools(self, tools, **kwargs):
        """绑定工具到模型"""
        # 创建一个新的实例，保存工具信息
        new_instance = self.__class__(
            base_url=self.base_url,
            model=self.model,
            temperature=self.temperature,
            streaming=self.streaming
        )
        new_instance._bound_tools = tools
        return new_instance

    @property
    def bound_tools(self):
        """获取绑定的工具"""
        return getattr(self, '_bound_tools', [])
    
    @property
    def _llm_type(self) -> str:
        return "ollama-chat"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天回复 - 使用异步方法的同步包装"""
        # 使用异步方法的同步包装
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._agenerate(messages, stop, run_manager, **kwargs))
            return result
        finally:
            loop.close()
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """异步生成聊天回复"""
        prompt = self._messages_to_prompt(messages)

        # 如果有绑定的工具，添加工具信息到提示中
        if self.bound_tools:
            tools_info = self._format_tools_for_prompt(self.bound_tools)
            prompt = f"{tools_info}\n\n{prompt}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": self.temperature
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    content = result.get("response", "")

                    # 创建 AI 消息，暂时不处理工具调用
                    message = AIMessage(content=content)
                    generation = ChatGeneration(message=message)
                    return ChatResult(generations=[generation])

        except Exception as e:
            raise Exception(f"Ollama API 异步调用失败: {e}")
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGeneration]:
        """异步流式生成"""
        prompt = self._messages_to_prompt(messages)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": self.temperature
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if 'response' in data:
                                    content = data['response']
                                    if content:
                                        message = AIMessage(content=content)
                                        yield ChatGeneration(message=message)
                                        
                                        if run_manager:
                                            await run_manager.on_llm_new_token(content)
                                            
                                if data.get('done', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            raise Exception(f"Ollama API 流式调用失败: {e}")
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """将消息列表转换为提示字符串"""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                prompt_parts.append(f"{message.type}: {message.content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)

    def _format_tools_for_prompt(self, tools) -> str:
        """将工具信息格式化为提示文本"""
        if not tools:
            return ""

        tools_text = "你可以使用以下工具来帮助回答问题：\n\n"
        for tool in tools:
            tools_text += f"工具名称: {tool.name}\n"
            tools_text += f"描述: {tool.description}\n"
            if hasattr(tool, 'args_schema') and tool.args_schema:
                tools_text += f"参数: {tool.args_schema}\n"
            tools_text += "\n"

        tools_text += "如果需要使用工具，请在回复中明确说明要使用哪个工具以及相应的参数。"
        return tools_text

def create_ollama_chat_model(
    model: str = "qwen3:1.7b",
    base_url: str = "http://localhost:11434",
    temperature: float = 0.7,
    streaming: bool = True
) -> OllamaChatModel:
    """创建 Ollama 聊天模型实例"""
    return OllamaChatModel(
        model=model,
        base_url=base_url,
        temperature=temperature,
        streaming=streaming
    )

def test_ollama_adapter():
    """测试 Ollama 适配器"""
    print("🧪 测试 Ollama 适配器...")
    
    # 创建模型实例
    llm = create_ollama_chat_model()
    
    # 测试消息
    messages = [HumanMessage(content="你好，请简单介绍一下自己")]
    
    try:
        # 同步调用
        result = llm._generate(messages)
        print(f"✅ 同步调用成功: {result.generations[0].message.content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 同步调用失败: {e}")
        return False

async def test_ollama_adapter_async():
    """异步测试 Ollama 适配器"""
    print("🧪 异步测试 Ollama 适配器...")
    
    # 创建模型实例
    llm = create_ollama_chat_model()
    
    # 测试消息
    messages = [HumanMessage(content="你好，请简单介绍一下自己")]
    
    try:
        # 异步调用
        result = await llm._agenerate(messages)
        print(f"✅ 异步调用成功: {result.generations[0].message.content[:100]}...")
        
        # 流式调用
        print("🔄 测试流式调用...")
        stream_content = ""
        async for chunk in llm._astream(messages):
            stream_content += chunk.message.content
            if len(stream_content) > 50:
                break
        print(f"✅ 流式调用成功: {stream_content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ 异步调用失败: {e}")
        return False

if __name__ == "__main__":
    # 同步测试
    test_ollama_adapter()
    
    # 异步测试
    asyncio.run(test_ollama_adapter_async())
