"""Long-term memory."""
import sqlite3, json, time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from .. import config


@dataclass
class MemoryEntry:
    id: int
    timestamp: datetime
    type: str
    content: str
    metadata: Dict
    importance: int


class LongTermMemory:
    def __init__(self, db_path=None):
        self.db_path = db_path or (config.DATA_DIR / "memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL NOT NULL,
                type TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT,
                importance INTEGER DEFAULT 5);
                CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL, updated_at REAL NOT NULL);""")

    def remember(self, type_, content, metadata=None, importance=5):
        with sqlite3.connect(self.db_path) as c:
            cur = c.execute("INSERT INTO memories (timestamp,type,content,metadata,importance) VALUES (?,?,?,?,?)",
                (time.time(), type_, content, json.dumps(metadata or {}), importance))
            return cur.lastrowid

    def set_fact(self, key, value):
        with sqlite3.connect(self.db_path) as c:
            c.execute("INSERT OR REPLACE INTO facts (key,value,updated_at) VALUES (?,?,?)",
                (key, value, time.time()))

    def get_fact(self, key):
        with sqlite3.connect(self.db_path) as c:
            r = c.execute("SELECT value FROM facts WHERE key=?", (key,)).fetchone()
            return r[0] if r else None

    def search(self, query, limit=20):
        with sqlite3.connect(self.db_path) as c:
            rows = c.execute("SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
                (f"%{query}%", limit)).fetchall()
        return [MemoryEntry(id=r[0], timestamp=datetime.fromtimestamp(r[1]),
            type=r[2], content=r[3], metadata=json.loads(r[4] or "{}"), importance=r[5]) for r in rows]
