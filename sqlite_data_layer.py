"""
SQLite 兼容的 Chainlit 数据层实现
解决 SQLite 不支持数组类型的问题
"""

import json
import sqlite3
import asyncio
from typing import Dict, List, Optional, Any, TypedDict
from datetime import datetime
import uuid
import logging

import chainlit as cl

# 配置详细的日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from chainlit.data import BaseDataLayer
from chainlit.types import (
    ThreadDict,
    ThreadFilter,
    FeedbackDict,
    PaginatedResponse,
    Pagination
)

# Chainlit 类型定义
class PersistedUserDict(dict):
    """模拟 Chainlit 的 PersistedUser 类型，继承自字典但具有属性访问"""
    def __init__(self, id: str, identifier: str, metadata: Dict[str, Any], createdAt: str, display_name: Optional[str] = None):
        super().__init__({
            "id": id,
            "identifier": identifier,
            "metadata": metadata,
            "createdAt": createdAt
        })
        self.display_name = display_name or identifier
        self.identifier = identifier  # 添加 identifier 属性
        self.id = id  # 添加 id 属性

# 定义 Step 类型（因为 Chainlit 可能没有导出 StepDict）
class StepDict(TypedDict):
    id: str
    name: str
    type: str
    threadId: str
    parentId: Optional[str]
    streaming: bool
    waitForAnswer: Optional[bool]
    isError: Optional[bool]
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    input: Optional[str]
    output: Optional[str]
    createdAt: Optional[str]
    command: Optional[str]
    start: Optional[str]
    end: Optional[str]
    generation: Optional[Dict[str, Any]]
    showInput: Optional[str]
    language: Optional[str]
    indent: Optional[int]
    defaultOpen: Optional[bool]
    disableFeedback: Optional[bool]

# 定义 Element 类型
class ElementDict(TypedDict):
    id: str
    threadId: Optional[str]
    type: Optional[str]
    url: Optional[str]
    chainlitKey: Optional[str]
    name: str
    display: Optional[str]
    objectKey: Optional[str]
    size: Optional[str]
    page: Optional[int]
    language: Optional[str]
    forId: Optional[str]
    mime: Optional[str]
    props: Optional[Dict[str, Any]]

# 定义 User 类型
class UserDict(TypedDict):
    id: str
    identifier: str
    metadata: Dict[str, Any]
    createdAt: Optional[str]


class SQLiteDataLayer(BaseDataLayer):
    """SQLite 兼容的数据层实现"""
    
    def __init__(self, db_path: str = "./data/chainlit_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                identifier TEXT NOT NULL UNIQUE,
                metadata TEXT NOT NULL,
                createdAt TEXT
            )
        """)
        
        # 创建线程表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id TEXT PRIMARY KEY,
                createdAt TEXT,
                name TEXT,
                userId TEXT,
                userIdentifier TEXT,
                tags TEXT,
                metadata TEXT,
                FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # 创建步骤表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                threadId TEXT NOT NULL,
                parentId TEXT,
                streaming INTEGER NOT NULL,
                waitForAnswer INTEGER,
                isError INTEGER,
                metadata TEXT,
                tags TEXT,
                input TEXT,
                output TEXT,
                createdAt TEXT,
                command TEXT,
                start TEXT,
                end TEXT,
                generation TEXT,
                showInput TEXT,
                language TEXT,
                indent INTEGER,
                defaultOpen INTEGER DEFAULT 0,
                disableFeedback INTEGER DEFAULT 0,
                FOREIGN KEY (threadId) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
        
        # 创建元素表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS elements (
                id TEXT PRIMARY KEY,
                threadId TEXT,
                type TEXT,
                url TEXT,
                chainlitKey TEXT,
                name TEXT NOT NULL,
                display TEXT,
                objectKey TEXT,
                size TEXT,
                page INTEGER,
                language TEXT,
                forId TEXT,
                mime TEXT,
                props TEXT,
                FOREIGN KEY (threadId) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
        
        # 创建反馈表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id TEXT PRIMARY KEY,
                forId TEXT NOT NULL,
                threadId TEXT NOT NULL,
                value INTEGER NOT NULL,
                comment TEXT,
                FOREIGN KEY (threadId) REFERENCES threads(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _serialize_data(self, data: Any) -> str:
        """序列化复杂数据为 JSON 字符串"""
        if data is None:
            return None
        if isinstance(data, (list, dict)):
            return json.dumps(data, ensure_ascii=False)
        return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """反序列化 JSON 字符串为 Python 对象"""
        if data is None:
            return None
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data
    
    async def create_user(self, user) -> Optional[PersistedUserDict]:
        """创建用户"""
        def _create_user():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # 处理输入参数（可能是字典或对象）
                if isinstance(user, dict):
                    user_id = user.get("id", str(uuid.uuid4()))
                    identifier = user.get("identifier")
                    metadata = user.get("metadata", {})
                    created_at = user.get("createdAt", datetime.now().isoformat())
                    display_name = user.get("display_name")
                else:
                    # 生成用户ID和创建时间
                    user_id = str(uuid.uuid4())
                    created_at = datetime.now().isoformat()
                    identifier = user.identifier
                    metadata = user.metadata.copy() if user.metadata else {}
                    display_name = user.display_name
                    if display_name:
                        metadata["display_name"] = display_name

                cursor.execute("""
                    INSERT INTO users (id, identifier, metadata, createdAt)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_id,
                    identifier,
                    self._serialize_data(metadata),
                    created_at
                ))
                conn.commit()

                # 返回 PersistedUserDict 对象
                return PersistedUserDict(
                    id=user_id,
                    identifier=identifier,
                    metadata=metadata,
                    createdAt=created_at,
                    display_name=display_name or identifier
                )
            except sqlite3.IntegrityError:
                return None
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _create_user)
    
    async def get_user(self, identifier: str) -> Optional[PersistedUserDict]:
        """获取用户"""
        def _get_user():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM users WHERE identifier = ?", (identifier,))
                row = cursor.fetchone()
                if row:
                    metadata = self._deserialize_data(row[2])
                    # 返回 PersistedUser 对象
                    display_name = identifier
                    if isinstance(metadata, dict) and "display_name" in metadata:
                        display_name = metadata["display_name"]

                    return PersistedUserDict(
                        id=row[0],
                        identifier=row[1],
                        metadata=metadata if isinstance(metadata, dict) else {},
                        createdAt=row[3],
                        display_name=display_name
                    )
                return None
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _get_user)
    
    async def create_thread(self, thread: ThreadDict) -> ThreadDict:
        """创建线程 - 带重试逻辑处理UNIQUE约束冲突"""
        import uuid

        logger.info(f"🔥 CREATE_THREAD 被调用！线程ID: {thread.get('id')}")
        logger.info(f"🔥 CREATE_THREAD 参数: {thread}")

        def _create_thread_with_retry():
            max_retries = 3
            current_thread = thread.copy()

            for attempt in range(max_retries):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                try:
                    logger.info(f"🔥 正在插入线程到数据库: {current_thread['id']} (尝试 {attempt + 1}/{max_retries})")
                    cursor.execute("""
                        INSERT INTO threads (id, createdAt, name, userId, userIdentifier, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        current_thread["id"],
                        current_thread.get("createdAt"),
                        current_thread.get("name"),
                        current_thread.get("userId"),
                        current_thread.get("userIdentifier"),
                        self._serialize_data(current_thread.get("tags", [])),
                        self._serialize_data(current_thread.get("metadata", {}))
                    ))
                    conn.commit()
                    logger.info(f"✅ 线程创建成功: {current_thread['id']}")
                    return current_thread
                except sqlite3.IntegrityError as e:
                    if "UNIQUE constraint failed" in str(e) and attempt < max_retries - 1:
                        # 生成新的线程ID并重试
                        old_id = current_thread["id"]
                        new_id = f"{old_id}_{uuid.uuid4().hex[:4]}"
                        current_thread["id"] = new_id
                        logger.warning(f"⚠️ 线程ID冲突，重试使用新ID: {old_id} -> {new_id}")
                        conn.close()
                        continue
                    else:
                        logger.error(f"❌ 创建线程失败 (UNIQUE约束): {e}")
                        raise
                except Exception as e:
                    logger.error(f"❌ 创建线程失败: {e}")
                    raise
                finally:
                    conn.close()

            # 如果所有重试都失败了
            raise Exception(f"创建线程失败：经过{max_retries}次重试仍然存在ID冲突")

        return await asyncio.get_event_loop().run_in_executor(None, _create_thread_with_retry)
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        """获取线程（包含完整的步骤和元素）"""
        def _get_thread():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # 获取线程基本信息
                cursor.execute("SELECT * FROM threads WHERE id = ?", (thread_id,))
                row = cursor.fetchone()

                # 如果线程不在 threads 表中，检查是否有步骤数据
                if not row:
                    cursor.execute("SELECT COUNT(*) FROM steps WHERE threadId = ?", (thread_id,))
                    step_count = cursor.fetchone()[0]

                    if step_count == 0:
                        return None

                    # 如果有步骤数据但没有线程记录，创建一个默认的线程信息
                    row = (thread_id, None, "历史对话", None, "admin", "[]", "{}")

                # 获取线程的所有步骤（按正确的列顺序）
                cursor.execute("""
                    SELECT id, name, type, threadId, parentId, disableFeedback, streaming,
                           waitForAnswer, isError, metadata, tags, input, output, createdAt,
                           start, end, generation, showInput, language, indent, defaultOpen, command
                    FROM steps WHERE threadId = ? ORDER BY createdAt ASC
                """, (thread_id,))
                step_rows = cursor.fetchall()

                steps = []
                for step_row in step_rows:
                    step = {
                        "id": step_row[0],
                        "name": step_row[1],
                        "type": step_row[2],
                        "threadId": step_row[3],
                        "parentId": step_row[4],
                        "disableFeedback": bool(step_row[5]),
                        "streaming": bool(step_row[6]),
                        "waitForAnswer": bool(step_row[7]),
                        "isError": bool(step_row[8]),
                        "metadata": self._deserialize_data(step_row[9]),
                        "tags": self._deserialize_data(step_row[10]),
                        "input": step_row[11],
                        "output": step_row[12],
                        "createdAt": step_row[13],
                        "start": step_row[14],
                        "end": step_row[15],
                        "generation": self._deserialize_data(step_row[16]),
                        "showInput": step_row[17],
                        "language": step_row[18],
                        "indent": step_row[19] or 0,
                        "defaultOpen": bool(step_row[20]),
                        "command": step_row[21]
                    }
                    steps.append(step)

                # 获取线程的所有元素（按正确的列顺序）
                cursor.execute("""
                    SELECT id, threadId, stepId, name, type, url, objectKey, size,
                           page, language, forId, mime, chainlitKey, display, props
                    FROM elements WHERE threadId = ?
                """, (thread_id,))
                element_rows = cursor.fetchall()

                elements = []
                for element_row in element_rows:
                    element = {
                        "id": element_row[0],
                        "threadId": element_row[1],
                        "stepId": element_row[2],
                        "name": element_row[3],
                        "type": element_row[4],
                        "url": element_row[5],
                        "objectKey": element_row[6],
                        "size": element_row[7],
                        "page": element_row[8],
                        "language": element_row[9],
                        "forId": element_row[10],
                        "mime": element_row[11],
                        "chainlitKey": element_row[12],
                        "display": element_row[13],
                        "props": self._deserialize_data(element_row[14])
                    }
                    elements.append(element)

                return {
                    "id": row[0],
                    "createdAt": row[1],
                    "name": row[2],
                    "userId": row[3],
                    "userIdentifier": row[4],
                    "tags": self._deserialize_data(row[5]) or [],
                    "metadata": self._deserialize_data(row[6]) or {},
                    "steps": steps,
                    "elements": elements
                }
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _get_thread)
    
    async def update_thread(self, thread_id: str, name: Optional[str] = None, 
                          user_id: Optional[str] = None, tags: Optional[List[str]] = None, 
                          metadata: Optional[Dict] = None) -> Optional[ThreadDict]:
        """更新线程"""
        def _update_thread():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(name)
                if user_id is not None:
                    updates.append("userId = ?")
                    params.append(user_id)
                if tags is not None:
                    updates.append("tags = ?")
                    params.append(self._serialize_data(tags))
                if metadata is not None:
                    updates.append("metadata = ?")
                    params.append(self._serialize_data(metadata))
                
                if updates:
                    params.append(thread_id)
                    cursor.execute(f"""
                        UPDATE threads SET {', '.join(updates)} WHERE id = ?
                    """, params)
                    conn.commit()
                
                return self._get_thread_sync(cursor, thread_id)
            finally:
                conn.close()
        
        return await asyncio.get_event_loop().run_in_executor(None, _update_thread)
    
    def _get_thread_sync(self, cursor, thread_id: str) -> Optional[ThreadDict]:
        """同步获取线程（内部使用）"""
        cursor.execute("SELECT * FROM threads WHERE id = ?", (thread_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "createdAt": row[1],
                "name": row[2],
                "userId": row[3],
                "userIdentifier": row[4],
                "tags": self._deserialize_data(row[5]) or [],
                "metadata": self._deserialize_data(row[6]) or {}
            }
        return None

    async def list_threads(self, pagination: Pagination, thread_filter: Optional[ThreadFilter] = None) -> PaginatedResponse[ThreadDict]:
        """列出线程"""
        def _list_threads():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # 构建查询
                where_clause = ""
                params = []
                if thread_filter and thread_filter.userId:
                    where_clause = "WHERE userId = ?"
                    params.append(thread_filter.userId)

                # 获取总数
                cursor.execute(f"SELECT COUNT(*) FROM threads {where_clause}", params)
                total = cursor.fetchone()[0]

                # 计算偏移量（基于cursor）
                offset = 0
                if pagination.cursor:
                    try:
                        offset = int(pagination.cursor)
                    except (ValueError, TypeError):
                        offset = 0

                # 获取分页数据
                params.extend([pagination.first, offset])
                cursor.execute(f"""
                    SELECT * FROM threads {where_clause}
                    ORDER BY createdAt DESC
                    LIMIT ? OFFSET ?
                """, params)

                threads = []
                for row in cursor.fetchall():
                    threads.append({
                        "id": row[0],
                        "createdAt": row[1],
                        "name": row[2],
                        "userId": row[3],
                        "userIdentifier": row[4],
                        "tags": self._deserialize_data(row[5]) or [],
                        "metadata": self._deserialize_data(row[6]) or {}
                    })

                return PaginatedResponse(
                    data=threads,
                    pageInfo={
                        "hasNextPage": offset + pagination.first < total,
                        "hasPreviousPage": offset > 0,
                        "startCursor": str(offset),
                        "endCursor": str(offset + len(threads))
                    }
                )
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _list_threads)

    async def delete_thread(self, thread_id: str):
        """删除线程 - Chainlit已在API层面处理认证和授权"""
        logger.info(f"🗑️ DELETE_THREAD 被调用！线程ID: {thread_id}")

        def _delete_thread():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # 首先检查线程是否存在
                cursor.execute("SELECT id, userId, name FROM threads WHERE id = ?", (thread_id,))
                thread = cursor.fetchone()

                if not thread:
                    logger.error(f"❌ 线程不存在: {thread_id}")
                    raise ValueError(f"线程不存在: {thread_id}")

                thread_id_db, user_id, thread_name = thread
                logger.info(f"📋 找到线程: ID={thread_id_db}, 用户ID={user_id}, 名称={thread_name}")

                # 删除相关的步骤
                cursor.execute("DELETE FROM steps WHERE threadId = ?", (thread_id,))
                deleted_steps = cursor.rowcount
                logger.info(f"🗑️ 删除了 {deleted_steps} 个步骤")

                # 删除相关的元素
                cursor.execute("DELETE FROM elements WHERE threadId = ?", (thread_id,))
                deleted_elements = cursor.rowcount
                logger.info(f"🗑️ 删除了 {deleted_elements} 个元素")

                # 删除相关的反馈
                cursor.execute("DELETE FROM feedbacks WHERE threadId = ?", (thread_id,))
                deleted_feedbacks = cursor.rowcount
                logger.info(f"🗑️ 删除了 {deleted_feedbacks} 个反馈")

                # 最后删除线程本身
                cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
                deleted_threads = cursor.rowcount
                logger.info(f"🗑️ 删除了 {deleted_threads} 个线程")

                conn.commit()
                logger.info(f"✅ 线程删除成功: {thread_id}")

            except Exception as e:
                logger.error(f"❌ 删除线程失败: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _delete_thread)

    async def create_step(self, step_dict: StepDict) -> StepDict:
        """创建步骤"""
        def _create_step():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO steps (
                        id, name, type, threadId, parentId, streaming, waitForAnswer,
                        isError, metadata, tags, input, output, createdAt, command,
                        start, end, generation, showInput, language, indent, defaultOpen, disableFeedback
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    step_dict["id"],
                    step_dict["name"],
                    step_dict["type"],
                    step_dict["threadId"],
                    step_dict.get("parentId"),
                    int(step_dict.get("streaming", False)),
                    int(step_dict.get("waitForAnswer", False)),
                    int(step_dict.get("isError", False)),
                    self._serialize_data(step_dict.get("metadata", {})),
                    self._serialize_data(step_dict.get("tags", [])),
                    step_dict.get("input"),
                    step_dict.get("output"),
                    step_dict.get("createdAt"),
                    step_dict.get("command"),
                    step_dict.get("start"),
                    step_dict.get("end"),
                    self._serialize_data(step_dict.get("generation")),
                    step_dict.get("showInput"),
                    step_dict.get("language"),
                    step_dict.get("indent", 0),
                    int(step_dict.get("defaultOpen", False)),
                    int(step_dict.get("disableFeedback", False))
                ))
                conn.commit()
                return step_dict
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _create_step)

    async def get_steps(self, thread_id: str) -> List[StepDict]:
        """获取线程的所有步骤"""
        def _get_steps():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT * FROM steps WHERE threadId = ? ORDER BY createdAt ASC
                """, (thread_id,))

                steps = []
                for row in cursor.fetchall():
                    steps.append({
                        "id": row[0],
                        "name": row[1],
                        "type": row[2],
                        "threadId": row[3],
                        "parentId": row[4],
                        "streaming": bool(row[5]),
                        "waitForAnswer": bool(row[6]),
                        "isError": bool(row[7]),
                        "metadata": self._deserialize_data(row[8]) or {},
                        "tags": self._deserialize_data(row[9]) or [],
                        "input": row[10],
                        "output": row[11],
                        "createdAt": row[12],
                        "command": row[13],
                        "start": row[14],
                        "end": row[15],
                        "generation": self._deserialize_data(row[16]),
                        "showInput": row[17],
                        "language": row[18],
                        "indent": row[19],
                        "defaultOpen": bool(row[20]),
                        "disableFeedback": bool(row[21])
                    })
                return steps
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _get_steps)

    async def delete_step(self, step_id: str):
        """删除步骤"""
        def _delete_step():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM steps WHERE id = ?", (step_id,))
                conn.commit()
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _delete_step)

    # 简化实现，其他方法返回空或默认值
    async def create_element(self, element: ElementDict) -> ElementDict:
        return element

    async def get_element(self, element_id: str, thread_id: Optional[str] = None) -> Optional[ElementDict]:
        return None

    async def delete_element(self, element_id: str, thread_id: Optional[str] = None):
        pass

    async def upsert_feedback(self, feedback: FeedbackDict) -> str:
        return feedback.get("id", str(uuid.uuid4()))

    async def delete_feedback(self, feedback_id: str) -> bool:
        return True

    # 实现缺失的抽象方法
    async def build_debug_url(self) -> str:
        """构建调试 URL"""
        return ""

    async def get_thread_author(self, thread_id: str) -> str:
        """获取线程作者 - 返回用户标识符（用户名）而不是用户ID"""
        logger.info(f"🔍 GET_THREAD_AUTHOR 被调用！线程ID: {thread_id}")

        def _get_thread_author():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                # 查询线程的 userIdentifier（用户名）而不是 userId（UUID）
                cursor.execute("SELECT id, userId, userIdentifier, name FROM threads WHERE id = ?", (thread_id,))
                row = cursor.fetchone()

                if row:
                    thread_id_db, user_id, user_identifier, thread_name = row
                    logger.info(f"✅ 找到线程: ID={thread_id_db}, 用户ID={user_id}, 用户标识符={user_identifier}, 名称={thread_name}")
                    # 返回用户标识符（用户名）而不是用户ID
                    return user_identifier or ""
                else:
                    logger.error(f"❌ 线程不存在: {thread_id}")
                    # 列出所有线程以便调试
                    cursor.execute("SELECT id, userId, userIdentifier, name FROM threads LIMIT 10")
                    all_threads = cursor.fetchall()
                    logger.info(f"📋 数据库中的线程列表: {all_threads}")
                    return ""

            except Exception as e:
                logger.error(f"❌ 获取线程作者失败: {e}")
                return ""
            finally:
                conn.close()

        result = await asyncio.get_event_loop().run_in_executor(None, _get_thread_author)
        logger.info(f"🎯 GET_THREAD_AUTHOR 返回结果: '{result}'")
        return result

    async def update_step(self, step_dict: StepDict):
        """更新步骤"""
        def _update_step():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE steps SET
                        name = ?, type = ?, threadId = ?, parentId = ?, streaming = ?,
                        waitForAnswer = ?, isError = ?, metadata = ?, tags = ?,
                        input = ?, output = ?, createdAt = ?, command = ?,
                        start = ?, end = ?, generation = ?, showInput = ?,
                        language = ?, indent = ?, defaultOpen = ?, disableFeedback = ?
                    WHERE id = ?
                """, (
                    step_dict.get("name"),
                    step_dict.get("type"),
                    step_dict.get("threadId"),
                    step_dict.get("parentId"),
                    int(step_dict.get("streaming", False)),
                    int(step_dict.get("waitForAnswer", False)),
                    int(step_dict.get("isError", False)),
                    self._serialize_data(step_dict.get("metadata")),
                    self._serialize_data(step_dict.get("tags")),
                    step_dict.get("input"),
                    step_dict.get("output"),
                    step_dict.get("createdAt"),
                    step_dict.get("command"),
                    step_dict.get("start"),
                    step_dict.get("end"),
                    self._serialize_data(step_dict.get("generation")),
                    step_dict.get("showInput"),
                    step_dict.get("language"),
                    step_dict.get("indent"),
                    int(step_dict.get("defaultOpen", False)),
                    int(step_dict.get("disableFeedback", False)),
                    step_dict["id"]
                ))
                conn.commit()
            except Exception as e:
                print(f"更新步骤失败: {e}")
                raise
            finally:
                conn.close()

        return await asyncio.get_event_loop().run_in_executor(None, _update_step)
