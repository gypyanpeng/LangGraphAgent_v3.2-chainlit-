# LangGraph Agent 项目

这是一个基于 LangGraph 的智能代理项目，**严格按照 LangGraph 官方标准实现**，集成了多种 MCP (Model Context Protocol) 工具，支持完整的对话历史持久化功能。

> **🎉 最新更新 (2025-06-28)**：**所有核心功能完全修复并新增智能特性！**
> - ✅ **新会话创建功能**：新对话现在可以正确保存到数据库
> - ✅ **历史会话删除功能**：用户可以从前端界面删除历史会话
> - ✅ **智能会话命名**：基于首条消息自动生成有意义的会话标题
> - ✅ **完整数据持久化**：所有会话操作（创建、读取、更新、删除）全部正常工作
> - ✅ **多用户会话隔离**：支持多用户独立会话管理
> - ✅ **数据库优化**：清理无用文件，优化存储结构
> - ✅ **完整测试验证**：通过了全面的功能测试，确保系统稳定性

## 📚 项目参考
- [LangGraph 官方文档](https://langgraph.readthedocs.io/en/latest/)
- [WoodenFish](https://github.com/WoodenFish/WoodenFish)
- [Chainlit 官方文档](https://docs.chainlit.cn/)
- [chainlit 官方langgraph集成文档](https://docs.chainlit.cn/integrations/langchain)

##  声明
本项目严格遵循 LangGraph 官方标准，并使用 LangChain 进行开发。
本项目完全符合 Chainlit 官方最佳实践。

## 🎉 核心特性

- 🤖 **智能对话系统**：基于 LangGraph 的状态机工作流
- 💾 **完整持久化存储**：
  - ✅ SQLite 数据库，对话历史永不丢失
  - ✅ 自定义 SQLiteDataLayer，完全兼容 Chainlit 2.5.5
  - ✅ 支持用户认证和多用户会话隔离
  - ✅ 前端可点击访问历史会话
  - ✅ GraphQL 风格分页支持
- 🛠️ **丰富工具集成**：30+ MCP 工具，包括搜索、图表、推理等
- 🔧 **多模型支持**：支持智谱AI、ModelScope、Ollama（自定义适配器）、OpenAI 等多种 LLM
- 🔄 **会话管理**：支持多会话隔离，可以清除上下文记忆
- 🏷️ **智能命名**：基于首条消息自动生成有意义的会话标题
- 🗑️ **会话删除**：支持从前端界面删除不需要的历史会话
- 📊 **实时交互**：流式输出，实时查看 AI 思考过程

## 🚀 快速开始

### 0. 准备工作

```bash
uv venv  # 创建虚拟环境
source .venv/bin/activate  # 激活环境（Linux/macOS）
```
### 1. 安装依赖

```bash
uv sync
```

### 2. 运行程序

#### CLI 模式
```bash
uv run python main.py
```

#### chainlit Web 界面模式 (推荐)
```bash
uv run chainlit run chainlit_app.py
```

访问 http://localhost:8000 使用 Web 界面

> **✅ 最新功能**: 新版本已完全集成 Chainlit 高级功能，包括：
> - 🔐 **身份验证系统**：支持用户登录和会话隔离
> - 📚 **前端历史会话**：在 Web 界面中查看和切换历史对话
> - 🌏 **完整中文界面**：所有配置和界面完全中文化
> - 💾 **自动数据库初始化**：项目迁移无需手动配置
> - 🔄 **会话恢复功能**：自动恢复历史对话上下文
> - ✅ **官方标准合规**：完全符合 Chainlit 官方最佳实践

### 🔐 身份验证和历史会话功能

Web 界面现在支持：
- **管理员身份验证**：使用admin账号登录（用户名：`admin`，密码：`admin123`）
- **历史会话查看**：在左侧面板查看所有历史对话
- **智能会话命名**：基于首条消息自动生成有意义的标题，告别"未命名对话"
- **一键切换会话**：点击历史会话即可恢复对话上下文
- **会话删除功能**：支持删除不需要的历史会话，保持界面整洁
- **安全访问控制**：只允许管理员账号访问系统


## 📁 项目结构

```
LangGraphAgentv3.2/
├── 📄 核心文件
│   ├── main.py                    # CLI 主程序入口
│   ├── chainlit_app.py            # Chainlit Web 界面入口（含智能命名功能）
│   ├── llm_loader.py              # LLM 加载器
│   ├── mcp_loader.py              # MCP 工具加载器
│   ├── sqlite_data_layer.py       # 自定义 SQLite 数据层实现
│   ├── chainlit.md                # Chainlit 集成说明
│   ├── README.md                  # 项目说明文档
│   ├── pyproject.toml             # 依赖管理
│   └── .env                       # 环境变量配置（身份验证密钥）
│
├── 🗂️ 配置目录
│   ├── config/                    # 应用配置文件
│   │   ├── llm_config.json        # LLM 提供商配置
│   │   ├── mcp_config.json        # MCP 工具配置
│   │   └── persistence_config.json# 持久化配置
│   └── .chainlit/                 # Chainlit 配置目录
│       ├── config.toml            # Chainlit 配置文件（完整中文翻译）
│       └── translations/          # 界面翻译文件
│           └── zh-CN.json         # 中文界面翻译
│
├── 💾 数据目录
│   └── data/                      # 数据存储目录
│       ├── agent_memory.db        # LangGraph 检查点数据库（5.5MB）
│       ├── chainlit_history.db    # Chainlit 会话历史数据库（1.6MB）
│       └── agent_data.db          # 业务数据存储（44KB）
│
├── 📚 文档目录
│   └── docs/                      # 项目文档
│       ├── 问题解决复盘报告.md      # 问题解决过程详细记录
│       └── 数据库文件分析报告.md    # 数据库架构分析文档
│
├── 🧪 测试目录
│   └── tests/                     # 测试文件集合
│       ├── test_thread_naming.py  # 智能命名功能测试
│       ├── test_system_integration.py # 系统集成测试
│       ├── test_complete_functionality.py # 完整功能测试
│       └── ...                    # 其他测试文件
│
├── 🛠️ 脚本目录
│   └── scripts/                   # 实用工具脚本
│       ├── cleanup_databases.py   # 数据库清理和分析脚本
│       └── verify_project_structure.py # 项目结构验证脚本
│
└── 📁 运行时目录
    ├── .files/                    # Chainlit 文件存储（运行时生成）
    └── __pycache__/               # Python 缓存文件（运行时生成）
```

## 📋 配置文件说明

### 🔧 应用配置
- **`config/llm_config.json`**：LLM 提供商配置（ModelScope、OpenAI等）
- **`config/mcp_config.json`**：MCP 工具配置（Sequential Thinking、Tavily等30个工具）
- **`config/persistence_config.json`**：持久化配置（数据库路径、检查点设置）

### 🎨 界面配置
- **`.chainlit/config.toml`**：Chainlit 配置文件（完整中文翻译、UI设置）
- **`.chainlit/translations/zh-CN.json`**：中文界面翻译文件

### 🔐 环境配置
- **`.env`**：环境变量配置（API密钥、身份验证密码等）

### 💾 数据库文件
- **`data/agent_memory.db`**：LangGraph 检查点存储（短期记忆、状态管理）
- **`data/chainlit_history.db`**：Chainlit 会话历史（界面显示、用户交互）
- **`data/agent_data.db`**：业务数据存储（长期记忆、跨会话数据）

## 🔍 项目结构验证

使用内置的验证脚本检查项目结构完整性：

```bash
python3 scripts/verify_project_structure.py
```

该脚本会检查：
- ✅ 所有核心文件是否存在
- ✅ 配置目录和文件的完整性
- ✅ 数据库文件状态和大小
- ✅ 文档和测试文件
- ✅ 清理状态（确保测试临时文件已删除）

### 🌏 中文本地化功能

项目现在完全支持中文界面：

- **配置文件中文化**：`.chainlit/config.toml` 中所有注释和说明都已翻译为中文
- **界面中文化**：Web 界面完全中文显示，包括按钮、菜单、提示信息等
- **错误信息中文化**：所有系统提示和错误信息都使用中文显示

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
rm data/agent_memory.db data/chainlit_history.db
```

### 🔄 自动数据库初始化

项目现在支持自动数据库初始化：

- **无需手动配置**：首次运行时自动创建所有必要的数据库表
- **项目迁移友好**：迁移到新环境时无需手动初始化数据库
- **智能检测**：自动检测数据库状态，只在需要时创建表
- **错误处理**：完善的错误处理和日志记录

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

### 🤖 多智能体系统架构（待实现）

本项目正在升级为多智能体协作系统，采用 LangGraph 官方推荐的监督者模式：

#### 核心组件
- **监督者智能体**：任务分析和协调
- **搜索专家**：信息检索和网络搜索
- **分析专家**：逻辑推理和复杂思考
- **图表专家**：数据可视化和图表生成
- **代码专家**：代码编写和技术实现
- **浏览器专家**：网页自动化操作
- **文档专家**：文档生成和知识管理

#### 工作流程
1. 用户输入问题
2. 监督者分析任务类型
3. 智能路由到合适的专家
4. 专家执行具体任务
5. 监督者整合结果
6. 返回最终答案

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

## 🧪 测试

项目包含完整的系统集成测试，验证所有核心功能：

```bash
# 运行系统集成测试
uv run python tests/test_system_integration.py

# 运行完整持久化功能测试
uv run python tests/test_persistence_complete.py
```

测试覆盖：
- ✅ 配置加载测试
- ✅ 检查点存储器测试
- ✅ 基本功能测试
- ✅ **完整持久化功能测试**（新增）
  - 用户创建和认证
  - 线程创建和管理
  - 步骤跟踪和存储
  - GraphQL 风格分页
  - 数据序列化/反序列化
  - 数据库结构验证
- ✅ 会话管理测试

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

项目核心功能已完全稳定，接下来可以专注于功能扩展：

- **多智能体系统升级**：基于稳定的持久化基础实现专业化智能体
- **性能优化**：数据库查询优化和缓存机制
- **用户体验提升**：更丰富的前端交互功能
- **监控和分析**：添加使用统计和性能监控

详细计划请参考 [项目实施时间表和里程碑](docs/项目实施时间表和里程碑.md)

## �� 许可证

MIT License
