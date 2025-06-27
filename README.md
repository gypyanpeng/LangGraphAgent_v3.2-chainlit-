# LangGraph Agent 项目

这是一个基于 LangGraph 的智能代理项目，**严格按照 LangGraph 官方标准实现**，集成了多种 MCP (Model Context Protocol) 工具，支持完整的对话历史持久化功能。

> **🔧 最新更新**：项目已完全重构，修复了所有持久化问题，现在完全符合 LangGraph 官方标准！

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
- 💾 **持久化存储**：SQLite 数据库，对话历史永不丢失
- 🛠️ **丰富工具集成**：30+ MCP 工具，包括搜索、图表、推理等
- 🔧 **多模型支持**：支持阿里云、ModelScope、OpenAI 等多种 LLM
- 🔄 **会话管理**：支持多会话隔离，可以清除上下文记忆
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

#### Web 界面模式 (推荐)
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
- **用户身份验证**：使用密码登录（默认密码：`admin`）
- **历史会话查看**：在左侧面板查看所有历史对话
- **一键切换会话**：点击历史会话即可恢复对话上下文
- **多用户支持**：每个用户的会话完全隔离

## 🔧 最新修复详情

### 1. TracerException 错误处理
- **现象**: `Error in callback coroutine: TracerException('No indexed run ID xxx')`
- **原因**: LangSmith 追踪系统内部错误
- **解决**: 完全禁用 LangSmith 追踪，不影响核心功能
- **状态**: ✅ 已修复，服务正常运行

### 2. 数据库表结构修复 (2025-06-27)
- **现象**: `table steps has no column named defaultOpen` 错误
- **原因**: Chainlit 2.5.5 期望的数据库表结构与实际表结构不匹配
- **解决**: 添加缺失的 `defaultOpen` 列到 steps 表
- **状态**: ✅ 已修复，会话持久化正常工作

### 3. 中文编码问题修复 (2025-06-27)
- **现象**: `GET /avatars/LangGraph%E6%99%BA%E8%83%BD%E4%BD%93%E7%B3%BB%E7%BB%9F HTTP/1.1" 400 Bad Request`
- **原因**: 配置文件中的中文应用名称被用作头像路径，导致URL编码问题
- **解决**:
  - 将应用名称改为英文 `"LangGraph Agent"`
  - 配置emoji头像避免路径问题
- **状态**: ✅ 已修复，界面加载正常

### 4. 代码优化
- 清理 main.py 中冗余的 Chainlit 相关代码
- 分离 CLI 和 Web 功能到独立文件
- 优化环境变量设置

### 5. Chainlit 高级功能集成
- **身份验证系统**: 基于密码的用户身份验证
- **前端历史会话**: Web 界面中的历史对话查看和切换
- **中文本地化**: 完整的配置文件和界面中文翻译
- **自动数据库初始化**: 应用启动时自动创建必要的数据库表
- **会话恢复**: 使用 `@cl.on_chat_resume` 装饰器自动恢复对话上下文
- **数据持久化**: 基于 LangGraph AsyncSqliteSaver 和 Chainlit SQLAlchemy 数据层

### 测试验证
```bash
# 测试修复效果
uv run python tests/test_chainlit_fixes.py

# 测试历史会话恢复功能
uv run python tests/test_session_resume.py
```

## 📝 使用说明

### 1. 启动 Web 界面
```bash
# 启动 Chainlit Web 界面
uv run chainlit run chainlit_app.py -w --port 8000

# 或者使用 Python 直接运行
uv run python chainlit_app.py
```

### 2. 启动 CLI 界面
```bash
# 启动命令行界面
uv run python main.py
```

### 3. 访问 Web 界面
- 打开浏览器访问: http://localhost:8000
- 使用密码登录: `admin123`
- 开始与 LangGraph Agent 对话

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 数据库表结构错误
**错误信息**: `table steps has no column named defaultOpen`

**解决方案**:
```bash
# 运行修复脚本
uv run python tests/test_chainlit_fixes.py

# 或手动修复数据库
sqlite3 ./data/chainlit_history.db "ALTER TABLE steps ADD COLUMN defaultOpen INTEGER DEFAULT 0;"
```

#### 2. 中文编码问题
**错误信息**: `GET /avatars/...%E6%99%BA... HTTP/1.1" 400 Bad Request`

**解决方案**: 检查 `.chainlit/config.toml` 文件，确保应用名称使用英文：
```toml
[UI]
name = "LangGraph Agent"  # 使用英文名称

[UI.avatar]
author = "👤"
assistant = "🤖"
```

#### 3. 端口占用问题
**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 结束进程
kill -9 <PID>

# 或使用不同端口
uv run chainlit run chainlit_app.py -w --port 8001
```

#### 4. 依赖安装问题
**解决方案**:
```bash
# 重新安装依赖
uv sync --all-extras

# 或清理缓存后重新安装
uv cache clean
uv sync --all-extras
```

## 🏗️ 技术架构

### LangGraph 官方标准实现

本项目严格按照 LangGraph 官方标准实现，包括：

- **检查点机制**：使用官方的 `AsyncSqliteSaver` 实现对话历史持久化
- **会话管理**：标准的 `{"configurable": {"thread_id": "xxx"}}` 配置格式
- **状态管理**：使用官方的 `MessagesState` 作为状态模式
- **工具集成**：标准的 `ToolNode` 和条件边实现

### 项目结构

```
LangGraphAgentv3.2/
├── main.py                    # CLI 主程序入口
├── chainlit_app.py            # Chainlit Web 界面入口
├── llm_loader.py              # LLM 加载器
├── mcp_loader.py              # MCP 工具加载器
├── chainlit.md                # Chainlit 集成说明
├── README.md                  # 项目说明文档
├── pyproject.toml             # 依赖管理
├── .env                       # 环境变量配置（身份验证密钥）
├── tests/                     # 测试文件夹
│   └── test_system_integration.py
├── docs/                      # 文档目录
├── data/                      # 数据存储目录
│   ├── agent_memory.db        # LangGraph SQLite 数据库
│   └── chainlit_history.db    # Chainlit 历史数据库
├── .chainlit/                 # Chainlit 配置目录
│   ├── config.toml            # Chainlit 配置文件（完整中文翻译）
│   └── translations/          # 界面翻译文件
│       └── zh-CN.json         # 中文界面翻译
└── config/                    # 配置文件目录
    ├── llm_config.json        # LLM 提供商配置
    ├── mcp_config.json        # MCP 工具配置
    └── persistence_config.json# 持久化配置
```

### 配置文件说明

- `config/llm_config.json`：LLM 提供商配置
- `config/mcp_config.json`：MCP 工具配置
- `config/persistence_config.json`：持久化配置
- `.chainlit/config.toml`：Chainlit 配置文件（完整中文翻译）
- `.env`：环境变量配置（包含身份验证密钥）

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
```

测试覆盖：
- ✅ 配置加载测试
- ✅ 检查点存储器测试
- ✅ 基本功能测试
- ✅ 持久化功能测试
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

## 📚 文档

### 🎯 多智能体系统文档
- [**多智能体系统详细调用报告和实施计划**](docs/多智能体系统详细调用报告和实施计划.md) - 完整的多智能体实施方案
- [**多智能体系统实施指南**](docs/多智能体系统实施指南.md) - 项目小白快速上手指南
- [**项目实施时间表和里程碑**](docs/项目实施时间表和里程碑.md) - 详细的8周实施计划
- [LangGraph 多智能体协作集成计划](docs/LangGraph_MultiAgent_Collaboration_Integration_Plan.md) - 技术深度分析

### 📖 技术文档
- [实施路线图](docs/Implementation_Roadmap.md) - 详细的功能实施计划
- [LangGraph 研究报告](docs/LangGraph_Research_Report.md) - 深度技术分析
- [模型提供商分析](docs/Model_Provider_Analysis.md) - 多模型支持方案
- [会话管理指南](docs/SESSION_MANAGEMENT_GUIDE.md) - 会话和记忆管理
- [WoodenFish 分析报告](docs/WoodenFish_Analysis_Report.md) - 最佳实践借鉴

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

## �� 许可证

MIT License
