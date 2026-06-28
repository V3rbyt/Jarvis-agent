"""Memória de curto prazo."""
import json
from typing import List, Dict
from .. import config


class Memory:
    def __init__(self):
        self.history = []
        self.load()

    def add(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > config.MAX_HISTORY:
            self.history = self.history[-config.MAX_HISTORY:]
        self.save()

    def get(self):
        return self.history.copy()

    def clear(self):
        self.history = []
        self.save()

    def save(self):
        try:
            config.HISTORY_FILE.write_text(
                json.dumps(self.history, indent=2, ensure_ascii=False), encoding="utf-8")
        except: pass

    def load(self):
        try:
            if config.HISTORY_FILE.exists():
                self.history = json.loads(config.HISTORY_FILE.read_text(encoding="utf-8"))
        except:
            self.history = []
