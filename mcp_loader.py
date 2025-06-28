# mcp_loader.py
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import List
from langchain_core.tools import BaseTool

async def load_mcp_tools_from_config(config_path: str = "config/mcp_config.json"):
    """
    从指定的JSON配置文件加载并初始化MCP工具。

    Args:
        config_path (str): MCP工具配置文件的路径。

    Returns:
        Tuple[MultiServerMCPClient, List[BaseTool]]: MCP客户端和LangChain兼容的工具列表。
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"错误: 配置文件 '{config_path}' 未找到。")
        exit(1)
    except json.JSONDecodeError:
        print(f"错误: 无法解析配置文件 '{config_path}'。请检查其JSON格式。")
        exit(1)

    print(f"正在从 '{config_path}' 加载MCP工具...")
    
    # 使用 MultiServerMCPClient 从配置字典创建客户端，并获取工具
    client = MultiServerMCPClient(config["mcpServers"])
    tools = await client.get_tools()
    
    print(f"成功加载 {len(tools)} 个MCP工具:")
    for tool in tools:
        print(f"  - 工具名称: {tool.name}")
        print(f"    描述: {tool.description}")

    return client, tools