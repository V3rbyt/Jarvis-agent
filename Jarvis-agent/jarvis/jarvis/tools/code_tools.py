"""Tools de análise de código."""

import ast
import os
from pathlib import Path
from typing import Dict

from .base import Tool, ToolResult


class AnalyzePythonTool(Tool):
    name = "analisar_python"
    description = "Analisa estrutura de um arquivo Python (classes, funções)"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            path = os.path.abspath(path)
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [m.name for m in node.body
                                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)
                               if hasattr(p, 'body') and node in getattr(p, 'body', [])):
                        functions.append({"name": node.name, "line": node.lineno})
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))

            summary = f"🐍 {path}\n"
            summary += f"  Classes: {len(classes)}, Funções: {len(functions)}\n"
            summary += f"  Imports: {len(imports)}\n"

            return ToolResult(
                success=True,
                data={"classes": classes, "functions": functions, "imports": imports},
                display=summary
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class ValidateSyntaxTool(Tool):
    name = "validar_sintaxe"
    description = "Verifica erros de sintaxe em arquivo Python"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                source = f.read()
            ast.parse(source)
            return ToolResult(True, display=f"✅ Sintaxe OK: {path}")
        except SyntaxError as e:
            return ToolResult(
                False, error=f"Linha {e.lineno}: {e.msg}",
                display=f"❌ Erro de sintaxe em {path}\n  Linha {e.lineno}: {e.msg}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))
