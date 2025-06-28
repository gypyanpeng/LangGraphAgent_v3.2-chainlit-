# llm_loader.py
import json
import os
from typing import Optional
from langchain_openai import ChatOpenAI

# 导入自定义 Ollama 适配器
try:
    from ollama_adapter import create_ollama_chat_model
    OLLAMA_ADAPTER_AVAILABLE = True
except ImportError:
    OLLAMA_ADAPTER_AVAILABLE = False

def load_llm_from_config(config_path: str = "config/llm_config.json", provider: Optional[str] = None):
    """
    加载 LLM 模型，支持多种提供商包括 Ollama 自定义适配器。
    支持多模型配置，provider 可选，默认加载 default_provider。
    默认配置文件路径为 config/llm_config.json。
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    # 兼容单模型和多模型配置
    if "models" in config:
        models = config["models"]
        default_provider = config.get("default_provider")
        provider = provider or default_provider
        if provider not in models:
            raise ValueError(f"未找到 provider: {provider} 的模型配置")
        llm_conf = models[provider]
        model = llm_conf.get("model_name")
        api_key = llm_conf.get("api_key")
        api_base = llm_conf.get("base_url")
        temperature = llm_conf.get("temperature", 0.7)
        streaming = llm_conf.get("streaming", True)
        provider_type = llm_conf.get("provider", provider)
    else:
        llm_conf = config["llm"]
        model = llm_conf.get("model")
        api_key = llm_conf.get("api_key")
        api_base = llm_conf.get("api_base")
        temperature = llm_conf.get("temperature", 0.7)
        streaming = llm_conf.get("streaming", True)
        provider_type = llm_conf.get("provider", "openai")

    # 如果是 Ollama 提供商且自定义适配器可用，使用自定义适配器
    if provider_type == "ollama" and OLLAMA_ADAPTER_AVAILABLE:
        print(f"🔧 使用 Ollama 自定义适配器: {model}")
        return create_ollama_chat_model(
            model=model,
            base_url=api_base,
            temperature=temperature,
            streaming=streaming
        )
    else:
        # 使用标准 OpenAI 兼容接口
        if provider_type == "ollama" and not OLLAMA_ADAPTER_AVAILABLE:
            print("⚠️ Ollama 适配器不可用，尝试使用 OpenAI 兼容接口")

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=api_base,
            temperature=temperature,
            streaming=streaming
        )

def list_available_models(config_path: str = "llm_config.json"):
    """
    列出配置文件中所有可用的模型。

    Args:
        config_path (str): LLM配置文件的路径。

    Returns:
        dict: 包含所有模型配置的字典。
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"错误: 配置文件 '{config_path}' 未找到。")
        return {}
    except json.JSONDecodeError:
        print(f"错误: 无法解析配置文件 '{config_path}'。")
        return {}

    if "models" not in config:
        print("⚠️ 配置文件使用旧格式，不支持多模型列表")
        return {}

    models = config.get("models", {})
    default_provider = config.get("default_provider")

    print("📋 可用模型列表:")
    for provider, model_config in models.items():
        default_mark = " (默认)" if provider == default_provider else ""
        description = model_config.get("description", "")

        print(f"  - {provider}{default_mark}")
        print(f"    模型: {model_config.get('model_name', 'N/A')}")
        print(f"    描述: {description}")
        print(f"    URL: {model_config.get('base_url', 'N/A')}")
        print()

    return models