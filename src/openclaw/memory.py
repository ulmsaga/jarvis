"""세션 · 대화 히스토리 저장 (SQLite)"""
import json
import time
import aiosqlite

DB_PATH = "jarvis_memory.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                channel_id TEXT,
                user_id    TEXT,
                history    TEXT DEFAULT '[]',
                updated_at REAL
            )
        """)
        await db.commit()


async def get_history(session_id: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT history FROM sessions WHERE session_id = ?", (session_id,)
        ) as cur:
            row = await cur.fetchone()
            return json.loads(row[0]) if row else []


async def append_history(session_id: str, channel_id: str, user_id: str, role: str, content: str) -> None:
    history = await get_history(session_id)
    history.append({"role": role, "content": content})
    # 최근 20턴만 유지
    history = history[-40:]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO sessions (session_id, channel_id, user_id, history, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                history = excluded.history,
                updated_at = excluded.updated_at
        """, (session_id, channel_id, user_id, json.dumps(history, ensure_ascii=False), time.time()))
        await db.commit()


async def clear_history(session_id: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        await db.commit()
