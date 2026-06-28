"""Planejador."""
import json, re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .. import config
from ..brain import Brain


@dataclass
class Plan:
    description: str
    steps: List[str]
    tool: Optional[str] = None
    params: Dict = field(default_factory=dict)
    fala: str = ""


class Planner:
    def __init__(self, brain):
        self.brain = brain

    def plan(self, user_text, history):
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        messages.extend(history[-config.MAX_HISTORY:])
        messages.append({"role": "user", "content": user_text})
        try:
            resp = self.brain._raw_call(messages)
            return self._parse(resp)
        except Exception as e:
            return Plan(description=f"Erro: {e}", steps=[], fala="Erro aqui.")

    @staticmethod
    def _parse(raw):
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                d = json.loads(m.group())
                return Plan(description=d.get("plano",""), steps=d.get("passos",[]),
                           tool=d.get("tool","nenhuma"), params=d.get("params",{}),
                           fala=d.get("fala", raw))
            except: pass
        return Plan(description="", steps=[], tool="nenhuma", params={}, fala=raw)
