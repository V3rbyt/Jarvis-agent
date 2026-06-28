"""Analytics."""
import time, json, sqlite3
from collections import defaultdict
from datetime import datetime
from typing import Dict
from .. import config


class AnalyticsTracker:
    def __init__(self):
        self.db_path = config.DATA_DIR / "analytics.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL, type TEXT NOT NULL, name TEXT NOT NULL,
                duration_ms INTEGER DEFAULT 0, metadata TEXT)""")

    def track(self, type_, name, duration_ms=0, **metadata):
        try:
            with sqlite3.connect(self.db_path) as c:
                c.execute("INSERT INTO events (timestamp, type, name, duration_ms, metadata) VALUES (?,?,?,?,?)",
                    (time.time(), type_, name, duration_ms, json.dumps(metadata) if metadata else None))
        except: pass

    def get_stats(self, days=7):
        cutoff = time.time() - (days * 86400)
        try:
            with sqlite3.connect(self.db_path) as c:
                ev = c.execute("SELECT type, name FROM events WHERE timestamp >= ?", (cutoff,)).fetchall()
        except: return {"total": 0}
        if not ev: return {"total": 0}
        by_type = defaultdict(int)
        by_name = defaultdict(int)
        for t, n in ev:
            by_type[t] += 1
            by_name[n] += 1
        return {"total": len(ev), "by_type": dict(by_type),
                "top_commands": sorted(by_name.items(), key=lambda x: x[1], reverse=True)[:10]}
