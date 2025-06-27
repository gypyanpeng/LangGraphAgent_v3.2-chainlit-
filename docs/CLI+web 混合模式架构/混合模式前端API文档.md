# 混合模式前端API开发文档

## 📋 概述

本文档基于混合模式架构，为前端开发者提供了与LangGraph智能体系统Web API交互的完整指南。该API与现有命令行版本共享相同的核心逻辑和数据库。

## 🎯 API特点

- **共享核心**：与命令行版本使用相同的智能体逻辑
- **实时通信**：支持WebSocket流式响应
- **会话隔离**：支持多用户多会话管理
- **配置驱动**：可通过配置启用/禁用功能
- **向后兼容**：不影响现有命令行功能

## 🔧 基础配置

### API基础信息
- **基础URL**: `http://localhost:8000`
- **WebSocket URL**: `ws://localhost:8000/ws`
- **认证方式**: 可选（通过配置控制）
- **数据格式**: JSON
- **响应格式**: 统一的成功/错误格式

### 启动Web API
```bash
# 仅启动Web API
uv run python web_main.py

# 或启动混合模式（CLI + Web API）
uv run python hybrid_main.py
```

### 配置Web API
编辑 `config/app_config.json`：
```json
{
  "interfaces": {
    "web": {
      "enabled": true,
      "host": "0.0.0.0",
      "port": 8000,
      "cors_origins": ["http://localhost:3000"],
      "auth_required": false
    }
  }
}
```

## 📡 API接口

### 1. 系统状态

#### 健康检查
```http
GET /health
```

**响应示例**：
```json
{
  "status": "healthy"
}
```

#### 系统信息
```http
GET /
```

**响应示例**：
```json
{
  "message": "LangGraph智能体API服务",
  "version": "2.0.0"
}
```

### 2. 会话管理

#### 创建会话
```http
POST /api/sessions
Content-Type: application/json

{
  "title": "新的对话",
  "mode": "single_agent",
  "user_id": "user123"
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "user123_a1b2c3d4",
      "title": "新的对话",
      "mode": "single_agent",
      "created_at": "2024-01-01T12:00:00Z",
      "status": "active"
    }
  }
}
```

#### 获取会话列表
```http
GET /api/sessions?user_id=user123
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "user123_a1b2c3d4",
        "title": "AI发展趋势讨论",
        "mode": "single_agent",
        "created_at": "2024-01-01T10:00:00Z",
        "last_activity": "2024-01-01T11:30:00Z",
        "status": "active"
      }
    ],
    "total": 1
  }
}
```

#### 获取会话详情
```http
GET /api/sessions/{session_id}
```

#### 删除会话
```http
DELETE /api/sessions/{session_id}
```

### 3. 消息处理

#### 获取会话历史
```http
GET /api/sessions/{session_id}/messages
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "role": "user",
        "content": "请帮我分析一下人工智能的发展趋势",
        "timestamp": "2024-01-01T10:00:00Z"
      },
      {
        "role": "assistant",
        "content": "我来为您分析人工智能的发展趋势...",
        "timestamp": "2024-01-01T10:01:00Z",
        "tool_calls": [
          {
            "name": "tavily_search",
            "args": {"query": "人工智能发展趋势 2024"}
          }
        ]
      }
    ],
    "session_id": "user123_a1b2c3d4"
  }
}
```

## 🔄 WebSocket实时通信

### 连接WebSocket
```javascript
const sessionId = 'user123_a1b2c3d4';
const ws = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}`);

ws.onopen = function(event) {
    console.log('WebSocket连接已建立');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    handleMessage(data);
};

ws.onerror = function(error) {
    console.error('WebSocket错误:', error);
};

ws.onclose = function(event) {
    console.log('WebSocket连接已关闭');
};
```

### 发送消息
```javascript
function sendMessage(content) {
    const message = {
        type: 'user_message',
        content: content
    };
    ws.send(JSON.stringify(message));
}

// 使用示例
sendMessage('请帮我分析一下人工智能的发展趋势');
```

### 处理响应
```javascript
function handleMessage(data) {
    switch (data.type) {
        case 'stream_chunk':
            // 处理流式消息块
            handleStreamChunk(data.data);
            break;
        case 'error':
            // 处理错误
            console.error('错误:', data.error);
            break;
    }
}

function handleStreamChunk(output) {
    const messages = output.messages;
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage.role === 'user') {
        console.log('用户:', lastMessage.content);
    } else if (lastMessage.role === 'assistant') {
        if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
            console.log('AI调用工具:', lastMessage.tool_calls.map(tc => tc.name));
        } else {
            console.log('AI回复:', lastMessage.content);
        }
    }
}
```

## 🎨 React集成示例

### 基础聊天组件
```jsx
import React, { useState, useEffect, useRef } from 'react';

function ChatInterface({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    // 建立WebSocket连接
    const ws = new WebSocket(`ws://localhost:8000/ws/sessions/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket连接已建立');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'stream_chunk') {
        handleStreamChunk(data.data);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket连接已关闭');
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const handleStreamChunk = (output) => {
    const newMessages = output.messages;
    setMessages(newMessages);
  };

  const sendMessage = () => {
    if (!inputValue.trim() || !isConnected) return;

    const message = {
      type: 'user_message',
      content: inputValue
    };

    wsRef.current.send(JSON.stringify(message));
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-interface">
      <div className="connection-status">
        状态: {isConnected ? '✅ 已连接' : '❌ 未连接'}
      </div>
      
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-role">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {message.content}
              {message.tool_calls && (
                <div className="tool-calls">
                  工具调用: {message.tool_calls.map(tc => tc.name).join(', ')}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题..."
          disabled={!isConnected}
        />
        <button 
          onClick={sendMessage}
          disabled={!inputValue.trim() || !isConnected}
        >
          发送
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
```

### 会话管理组件
```jsx
import React, { useState, useEffect } from 'react';

function SessionManager({ onSessionSelect }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const response = await fetch('/api/sessions?user_id=default_user');
      const data = await response.json();
      
      if (data.success) {
        setSessions(data.data.sessions);
      }
    } catch (error) {
      console.error('获取会话列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: '新的对话',
          mode: 'single_agent',
          user_id: 'default_user'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        await fetchSessions(); // 刷新会话列表
        onSessionSelect(data.data.session.id);
      }
    } catch (error) {
      console.error('创建会话失败:', error);
    }
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div className="session-manager">
      <div className="session-header">
        <h3>会话列表</h3>
        <button onClick={createSession}>新建会话</button>
      </div>
      
      <div className="session-list">
        {sessions.map(session => (
          <div 
            key={session.id} 
            className="session-item"
            onClick={() => onSessionSelect(session.id)}
          >
            <h4>{session.title}</h4>
            <p>创建时间: {new Date(session.created_at).toLocaleString()}</p>
            <p>状态: {session.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SessionManager;
```

## 🔧 开发工具

### cURL测试命令
```bash
# 健康检查
curl http://localhost:8000/health

# 创建会话
curl -X POST "http://localhost:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试会话",
    "mode": "single_agent",
    "user_id": "test_user"
  }'

# 获取会话列表
curl "http://localhost:8000/api/sessions?user_id=test_user"
```

### WebSocket测试
```javascript
// 在浏览器控制台中测试
const ws = new WebSocket('ws://localhost:8000/ws/sessions/test_session');
ws.onopen = () => console.log('连接成功');
ws.onmessage = (e) => console.log('收到消息:', JSON.parse(e.data));
ws.send(JSON.stringify({type: 'user_message', content: '你好'}));
```

## 📝 注意事项

1. **数据共享**：Web API与命令行版本共享相同的数据库
2. **会话格式**：会话ID格式为 `{user_id}_{8位随机字符}`
3. **实时性**：WebSocket提供实时的流式响应
4. **配置控制**：可通过配置文件启用/禁用Web API功能
5. **错误处理**：所有API都返回统一的错误格式

这个API文档基于实际的混合模式架构，确保了与现有系统的完全兼容性！
