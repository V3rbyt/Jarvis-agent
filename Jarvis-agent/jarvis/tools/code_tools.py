"""Tools de análise de código Python."""

import ast
import os
from typing import Dict

from .base import Tool, ToolResult


class AnalyzePythonTool(Tool):
    name = "analisar_python"
    description = "Analisa estrutura de arquivo Python"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n.name for n in ast.walk(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            return ToolResult(True, display=f"🐍 {path}: {len(classes)} classes, {len(functions)} funções")
        except Exception as e:
            return ToolResult(False, error=str(e))


class ValidateSyntaxTool(Tool):
    name = "validar_sintaxe"
    description = "Verifica sintaxe Python"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            return ToolResult(True, display=f"✅ Sintaxe OK: {path}")
        except SyntaxError as e:
            return ToolResult(False, error=f"Linha {e.lineno}: {e.msg}",
                              display=f"❌ Erro em {path}")
        except Exception as e:
            return ToolResult(False, error=str(e))
