"""Tools de manipulação de arquivos."""

import os
import shutil
from pathlib import Path
from typing import Dict

from .base import Tool, ToolResult


def _resolve(path: str) -> str:
    if not path:
        return ""
    if os.path.isabs(path):
        return os.path.normpath(path)
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    candidate = os.path.join(desktop, path)
    if os.path.exists(candidate):
        return os.path.normpath(candidate)
    return os.path.normpath(os.path.join(os.getcwd(), path))


class ReadFileTool(Tool):
    name = "ler_arquivo"
    description = "Lê o conteúdo de um arquivo"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        try:
            if not os.path.isfile(path):
                return ToolResult(False, error=f"Arquivo não encontrado: {path}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return ToolResult(
                True,
                data={"path": path, "content": content, "lines": content.count("\n") + 1},
                display=f"📄 {path} ({len(content)} chars)"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class WriteFileTool(Tool):
    name = "escrever_arquivo"
    description = "Cria ou sobrescreve arquivo com conteúdo novo"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        conteudo = params.get("conteudo", "")
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return ToolResult(True, data={"path": path, "size": len(conteudo)},
                              display=f"✏️ Criado: {path} ({len(conteudo)} chars)")
        except Exception as e:
            return ToolResult(False, error=str(e))


class EditFileTool(Tool):
    name = "editar_arquivo"
    description = "Edita arquivo substituindo trecho"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        antigo = params.get("antigo", "")
        novo = params.get("novo", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if antigo not in content:
                return ToolResult(False, error="Trecho não encontrado")
            new = content.replace(antigo, novo, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            return ToolResult(True, data={"path": path},
                              display=f"🔧 Editado: {path}")
        except Exception as e:
            return ToolResult(False, error=str(e))


class ListDirTool(Tool):
    name = "listar_pasta"
    description = "Lista arquivos em diretório"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        try:
            if not os.path.isdir(path):
                return ToolResult(False, error="Não é diretório")
            items = sorted(os.listdir(path))
            return ToolResult(True, data={"path": path, "items": items, "count": len(items)},
                              display=f"📁 {path}: {len(items)} itens")
        except Exception as e:
            return ToolResult(False, error=str(e))


class CreateDirTool(Tool):
    name = "criar_pasta"
    description = "Cria diretório"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        try:
            os.makedirs(path, exist_ok=True)
            return ToolResult(True, data={"path": path}, display=f"📁 Criada: {path}")
        except Exception as e:
            return ToolResult(False, error=str(e))


class DeleteTool(Tool):
    name = "deletar"
    description = "Deleta arquivo ou pasta"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = _resolve(params.get("path", ""))
        try:
            if not os.path.exists(path):
                return ToolResult(False, error="Não existe")
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return ToolResult(True, data={"path": path}, display=f"🗑️ Deletado: {path}")
        except Exception as e:
            return ToolResult(False, error=str(e))


class MoveTool(Tool):
    name = "mover"
    description = "Move arquivo/pasta"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        src = _resolve(params.get("src", ""))
        dst = _resolve(params.get("dst", ""))
        try:
            shutil.move(src, dst)
            return ToolResult(True, data={"src": src, "dst": dst},
                              display=f"➡️ {src} → {dst}")
        except Exception as e:
            return ToolResult(False, error=str(e))
