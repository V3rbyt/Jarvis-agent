"""Registro central de tools."""

from typing import Dict, List
from .base import Tool
from .file_tools import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool, CreateDirTool, DeleteTool, MoveTool
from .shell_tools import RunCommandTool, InstallPipTool
from .search_tools import SearchFilesTool, GrepTool
from .code_tools import AnalyzePythonTool, ValidateSyntaxTool


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_defaults()

    def _register_defaults(self):
        for tool in [
            ReadFileTool(), WriteFileTool(), EditFileTool(),
            ListDirTool(), CreateDirTool(), DeleteTool(), MoveTool(),
            RunCommandTool(), InstallPipTool(),
            SearchFilesTool(), GrepTool(),
            AnalyzePythonTool(), ValidateSyntaxTool(),
        ]:
            self.register(tool)

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self.tools.get(name)

    def list_names(self) -> List[str]:
        return list(self.tools.keys())

    def get_schemas(self) -> List[Dict]:
        return [t.get_schema() for t in self.tools.values()]
