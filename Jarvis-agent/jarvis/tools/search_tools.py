"""Tools de busca."""

import glob
import os
from pathlib import Path
from typing import Dict

from .base import Tool, ToolResult


class SearchFilesTool(Tool):
    name = "buscar_arquivos"
    description = "Busca arquivos por padrão (ex: *.py)"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        padrao = params.get("padrao", "*")
        raiz = params.get("raiz", ".")
        try:
            results = []
            for match in glob.glob(os.path.join(raiz, "**", padrao), recursive=True):
                if os.path.isfile(match):
                    results.append(match)
                if len(results) >= 100:
                    break
            return ToolResult(True, data={"results": results, "count": len(results)},
                              display=f"🔍 {padrao}: {len(results)} resultados")
        except Exception as e:
            return ToolResult(False, error=str(e))


class GrepTool(Tool):
    name = "buscar_conteudo"
    description = "Busca texto em arquivos (grep)"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        texto = params.get("texto", "")
        raiz = Path(params.get("raiz", ".")).resolve()
        try:
            results = []
            for f in raiz.rglob("*"):
                if not f.is_file():
                    continue
                try:
                    with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                        for i, line in enumerate(fp, 1):
                            if texto in line:
                                results.append({"file": str(f), "line": i, "content": line.rstrip()})
                                if len(results) >= 50:
                                    break
                except Exception:
                    continue
                if len(results) >= 50:
                    break
            return ToolResult(True, data={"results": results, "count": len(results)},
                              display=f"🔍 '{texto}': {len(results)} matches")
        except Exception as e:
            return ToolResult(False, error=str(e))
