# LangGraph 会话管理完整指南

## 📋 概述

本项目基于 LangGraph 官方标准实现了完整的会话管理和持久化功能，支持多会话隔离、历史记录查看和会话恢复等功能。

## 🔄 如何回到历史会话中继续提问

### 方法一：自动恢复（推荐）

**程序重启后会自动恢复到最近的会话**

```bash
# 启动程序
uv run python main.py

# 程序会显示：
🆕 创建新会话: default_user_xxxxxxxx
# 或者恢复到之前的会话
```

由于使用了 LangGraph 官方的 `AsyncSqliteSaver`，所有对话历史都会自动保存到 SQLite 数据库中，程序重启后可以直接继续之前的对话。

### 方法二：使用 `history` 命令查看历史

在程序中输入 `history` 命令可以查看当前会话的完整对话历史：

```
💬 请输入您的问题: history

📚 当前会话历史 (6 条消息):
  1. 👤 你好...
  2. 🤖 你好！有什么我可以帮你的吗？...
  3. 👤 绘制中美 gdp 增速对比柱状图...
  4. 🤖 ...
  5. 🔧 https://mdn.alipayobjects.com/one_clip/afts/img/69...
  6. 🤖 以下是中美两国2013-2022年GDP增速对比柱状图：...
```

### 方法三：手动恢复到指定会话

使用 `resume <thread_id>` 命令可以恢复到任何历史会话：

```
💬 请输入您的问题: resume default_user_504840f1
🔄 恢复会话: default_user_504840f1
✅ 已恢复到指定会话
```

**如何获取会话ID？**
- 程序启动时会显示当前会话ID
- 使用 `history` 命令时会显示会话信息
- 会话ID格式：`{user_id}_{8位随机字符}`

### 方法四：创建新会话

如果想开始全新的对话，使用 `new` 命令：

```
💬 请输入您的问题: new
✅ 已开始新对话
🆕 创建新会话: default_user_xxxxxxxx
```

## 🛠️ 可用命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `history` | 查看当前会话的对话历史 | `history` |
| `new` | 开始新对话 | `new` |
| `resume <thread_id>` | 恢复到指定会话 | `resume default_user_504840f1` |
| `help` | 查看帮助信息 | `help` |
| `tools` | 查看可用工具列表 | `tools` |
| `clear` | 清屏 | `clear` |
| `quit` 或 `exit` | 退出程序 | `quit` |

## 🏗️ 技术实现

### LangGraph 官方标准

项目严格按照 LangGraph 官方标准实现：

1. **检查点机制**：使用 `AsyncSqliteSaver` 实现对话历史持久化
2. **会话配置**：标准的 `{"configurable": {"thread_id": "xxx"}}` 格式
3. **状态管理**：使用官方的 `MessagesState` 作为状态模式

### 会话管理器

<augment_code_snippet path="main.py" mode="EXCERPT">
````python
class SimpleSessionManager:
    """简单的会话管理器 - 符合 LangGraph 官方标准"""
    
    def get_session_config(self, thread_id: str, user_id: Optional[str] = None):
        """获取 LangGraph 标准的会话配置 - 支持 user_id"""
        config = {"configurable": {"thread_id": thread_id}}
        
        if user_id:
            config["configurable"]["user_id"] = user_id
            
        return config
    
    def resume_session(self, thread_id: str):
        """恢复到指定的会话"""
        self.current_thread_id = thread_id
        if '_' in thread_id:
            self.current_user_id = thread_id.split('_')[0]
        print(f"🔄 恢复会话: {thread_id}")
        return thread_id
````
</augment_code_snippet>

### 数据存储

- **数据库文件**：`./data/agent_memory.db`（SQLite）
- **存储内容**：完整的消息历史、会话状态、检查点数据
- **数据格式**：LangGraph 官方的消息格式（HumanMessage、AIMessage、ToolMessage）

## 📊 实际使用示例

### 示例 1：基本会话恢复

```bash
# 第一次使用
$ uv run python main.py
🆕 创建新会话: default_user_abc12345

💬 请输入您的问题: 你好，我是张三
🤖 AI -> 你好张三！很高兴认识你...

💬 请输入您的问题: quit
👋 再见！

# 重启程序后
$ uv run python main.py
🆕 创建新会话: default_user_def67890

💬 请输入您的问题: resume default_user_abc12345
🔄 恢复会话: default_user_abc12345
✅ 已恢复到指定会话

💬 请输入您的问题: 我的名字是什么？
🤖 AI -> 你的名字是张三...
```

### 示例 2：多会话管理

```bash
# 会话 1：工作相关
💬 请输入您的问题: 帮我分析一下销售数据
🤖 AI -> 好的，我来帮你分析销售数据...

💬 请输入您的问题: new
✅ 已开始新对话

# 会话 2：学习相关  
💬 请输入您的问题: 解释一下机器学习的基本概念
🤖 AI -> 机器学习是人工智能的一个分支...

# 回到会话 1
💬 请输入您的问题: resume default_user_abc12345
🔄 恢复会话: default_user_abc12345

💬 请输入您的问题: 继续分析销售数据的趋势
🤖 AI -> 基于之前的分析，我们可以看到...
```

## 🔍 故障排除

### 问题 1：无法找到历史会话

**原因**：数据库文件可能被删除或损坏

**解决方案**：
```bash
# 检查数据库文件是否存在
ls -la data/agent_memory.db

# 如果文件不存在，程序会自动创建新的数据库
```

### 问题 2：会话ID格式错误

**原因**：输入的会话ID格式不正确

**解决方案**：
- 确保会话ID格式为：`{user_id}_{8位字符}`
- 使用 `history` 命令查看正确的会话ID

### 问题 3：恢复会话后历史记录为空

**原因**：可能是数据库权限问题或数据损坏

**解决方案**：
```bash
# 检查数据库文件权限
ls -la data/agent_memory.db

# 确保程序有读写权限
chmod 644 data/agent_memory.db
```

## 📝 最佳实践

1. **定期备份**：定期备份 `data/agent_memory.db` 文件
2. **会话命名**：为重要会话记录会话ID，便于后续恢复
3. **清理策略**：定期使用 `new` 命令开始新会话，避免单个会话过长
4. **多用户支持**：不同用户可以使用不同的 `user_id` 前缀

## 🎯 总结

通过 LangGraph 官方标准的持久化机制，本项目实现了：

- ✅ **真正的对话历史保存**：重启程序后对话不丢失
- ✅ **多会话隔离管理**：支持同时管理多个独立会话
- ✅ **灵活的会话恢复**：可以恢复到任何历史会话
- ✅ **标准化实现**：完全符合 LangGraph 官方规范

这使得用户可以像使用专业的聊天应用一样，随时中断和恢复对话，极大提升了使用体验！🚀
