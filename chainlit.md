# LangGraph Agent 项目

这是一个基于 LangGraph 的智能代理项目，**严格按照 LangGraph 官方标准实现**，集成了多种 MCP (Model Context Protocol) 工具，支持完整的对话历史持久化功能。

## 🎉 核心特性

- 🤖 **智能对话系统**：基于 LangGraph 的状态机工作流
- 💾 **持久化存储**：SQLite 数据库，对话历史永不丢失
- 🛠️ **丰富工具集成**：30+ MCP 工具，包括搜索、图表、推理等
- 🔧 **多模型支持**：支持阿里云、ModelScope、OpenAI 等多种 LLM
- 🔄 **会话管理**：支持多会话隔离，可以清除上下文记忆
- 📊 **实时交互**：流式输出，实时查看 AI 思考过程

## 🏗️ 技术架构

### LangGraph 官方标准实现

本项目严格按照 LangGraph 官方标准实现，包括：

- **检查点机制**：使用官方的 `AsyncSqliteSaver` 实现对话历史持久化
- **会话管理**：标准的 `{"configurable": {"thread_id": "xxx"}}` 配置格式
- **状态管理**：使用官方的 `MessagesState` 作为状态模式
- **工具集成**：标准的 `ToolNode` 和条件边实现

### 项目结构

```
my_project/
├── main.py                    # 主程序入口
├── llm_loader.py             # LLM 加载器
├── mcp_loader.py             # MCP 工具加载器
├── llm_config.json           # LLM 配置文件
├── mcp_config.json           # MCP 工具配置文件
├── persistence_config.json   # 持久化配置文件
├── tests/                    # 测试文件
│   └── test_system_integration.py
├── docs/                     # 文档目录
└── data/                     # 数据存储目录
    └── agent_memory.db       # SQLite 数据库
```

### 配置文件说明

- `llm_config.json`：LLM 提供商配置
- `mcp_config.json`：MCP 工具配置
- `persistence_config.json`：持久化和会话管理配置

## 💾 持久化功能

### 自动保存对话历史
- ✅ 所有对话自动保存到 SQLite 数据库
- ✅ 程序重启后可以继续之前的对话
- ✅ 支持多个独立会话

### 清除上下文记忆的方法

#### 方法1：开始新对话（推荐）
```
💬 请输入您的问题: new
🆕 创建新会话: default_user_40e11643
✅ 已开始新对话
```

#### 方法2：重启程序
- 程序重启后会自动创建新会话
- 之前的对话历史仍然保存在数据库中

#### 方法3：完全重置（删除所有历史）
```bash
rm data/agent_memory.db
```

### 可用命令
| 命令 | 功能 | 示例 |
|------|------|------|
| `history` | 查看当前会话的对话历史 | `history` |
| `new` | 开始新对话 | `new` |
| `resume <thread_id>` | 恢复到指定会话 | `resume default_user_504840f1` |
| `help` | 查看帮助信息 | `help` |
| `tools` | 查看可用工具列表 | `tools` |
| `clear` | 清屏 | `clear` |
| `quit` 或 `exit` | 退出程序 | `quit` |

## 🛠️ 集成工具

### 搜索和内容工具
- **Tavily Search**: 强大的网络搜索引擎
- **Tavily Extract**: 网页内容提取
- **Tavily Crawl**: 网站结构化爬取
- **Tavily Map**: 网站地图生成

### 图表生成工具
- **面积图、柱状图、箱线图**：数据可视化
- **饼图、雷达图、散点图**：多维数据展示
- **思维导图、流程图**：结构化信息展示
- **地图工具**：地理数据可视化

### 推理工具
- **Sequential Thinking**: 动态思维链推理
- 支持多步骤问题分解和解决


## 🔧 技术架构

### 持久化实现
- **严格按照 LangGraph 官方标准**
- **参考 WoodenFish 项目的最佳实践**
- **使用官方 SqliteSaver checkpointer**

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# 创建检查点存储器
checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{db_path}")

# 编译工作流时集成检查点
app = workflow.compile(checkpointer=checkpointer)

# 运行时传入会话配置
config = {"configurable": {"thread_id": thread_id}}
async for output in app.astream(inputs, config=config):
    # 处理输出
```

### 会话管理
```python
class SimpleSessionManager:
    def create_session(self, user_id=None):
        thread_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        return thread_id
    
    def get_session_config(self, thread_id):
        return {"configurable": {"thread_id": thread_id}}
```

## 📊 使用示例

### 智能对话
```
💬 请输入您的问题: 帮我分析一下人工智能的发展趋势

🚀 开始处理查询: '帮我分析一下人工智能的发展趋势' (会话: default_user_80b405d6)

--- 状态更新 ---
📨 新消息类型: AIMessage
🤖 AI -> 调用工具: ['tavily-search']
   工具: tavily-search, 参数: {'query': '人工智能发展趋势 2024 2025'}

--- 状态更新 ---
📨 新消息类型: ToolMessage
🔧 工具 tavily-search -> 结果: 根据最新的搜索结果，人工智能在2024-2025年的发展趋势...

--- 状态更新 ---
📨 新消息类型: AIMessage
🤖 AI -> 最终回复:
基于最新的信息，我为您分析人工智能的发展趋势...
```

### 查看对话历史
```
💬 请输入您的问题: history

📚 当前会话历史 (4 条消息):
  1. 👤 帮我分析一下人工智能的发展趋势...
  2. 🤖 我来为您搜索最新的人工智能发展趋势信息...
  3. 🔧 根据最新的搜索结果，人工智能在2024-2025年...
  4. 🤖 基于最新的信息，我为您分析人工智能的发展趋势...
```

## 🛠️ 开发指南

### 添加新的 MCP 工具

1. 在 `mcp_config.json` 中添加工具配置
2. 重启程序即可使用新工具

### 自定义 LLM 提供商

1. 修改 `llm_config.json` 中的配置
2. 支持任何 OpenAI 兼容的 API

### 配置持久化选项

1. 修改 `persistence_config.json` 中的配置
2. 支持 SQLite、内存等多种存储后端

## 🎯 开发说明

- **Python 3.11+**
- **uv 包管理器**
- **严格遵循 LangGraph 官方标准**
- **支持异步操作和流式输出**
- **完整的错误处理和日志记录**

## 📈 项目优势

1. **生产级可靠性**：参考成熟项目 WoodenFish 的最佳实践
2. **官方标准兼容**：严格按照 LangGraph 官方规范实现
3. **多智能体协作**：专门化智能体提升处理效率和质量
4. **真正的持久化**：SQLite 数据库存储，数据永不丢失
5. **灵活的会话管理**：支持多会话，可以随时清除上下文
6. **可扩展架构**：模块化设计，易于添加新的智能体和功能

## 🚀 下一步计划

项目正在进行多智能体系统升级，预计8周内完成：

- **Week 1-2**：基础架构搭建
- **Week 3-4**：核心专家智能体实现
- **Week 5-6**：系统集成和优化
- **Week 7-8**：测试和部署

详细计划请参考 [项目实施时间表和里程碑](docs/项目实施时间表和里程碑.md)
