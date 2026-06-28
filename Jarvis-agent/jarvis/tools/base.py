"""Classe base para tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str = ""
    display: str = ""

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "display": self.display,
        }


class Tool(ABC):
    name: str = ""
    description: str = ""
    requires_confirmation: bool = False
    dangerous: bool = False

    @abstractmethod
    def execute(self, params: Dict) -> ToolResult:
        pass

    def get_schema(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "dangerous": self.dangerous,
            "requires_confirmation": self.requires_confirmation,
        }
