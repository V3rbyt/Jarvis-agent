"""Tools de manipulação de arquivos."""

import os
import shutil
from pathlib import Path
from typing import Dict

from .base import Tool, ToolResult


class ReadFileTool(Tool):
    name = "ler_arquivo"
    description = "Lê o conteúdo de um arquivo"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            path = self._resolve(path)
            if not os.path.isfile(path):
                return ToolResult(False, error=f"Arquivo não encontrado: {path}")

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return ToolResult(
                success=True,
                data={"path": path, "content": content, "lines": content.count("\n") + 1},
                display=f"📄 {path} ({len(content)} chars, {content.count(chr(10))+1} linhas)"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))

    @staticmethod
    def _resolve(path: str) -> str:
        if os.path.isabs(path):
            return os.path.normpath(path)
        # Tenta Desktop, depois CWD
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        candidate = os.path.join(desktop, path)
        if os.path.exists(candidate):
            return os.path.normpath(candidate)
        return os.path.normpath(os.path.join(os.getcwd(), path))


class WriteFileTool(Tool):
    name = "escrever_arquivo"
    description = "Cria ou sobrescreve um arquivo com conteúdo novo"
    dangerous = True  # Sobrescreve!
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        conteudo = params.get("conteudo", "")
        try:
            path = ReadFileTool._resolve(path)
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(conteudo)
            return ToolResult(
                success=True,
                data={"path": path, "size": len(conteudo)},
                display=f"✏️ Arquivo criado: {path} ({len(conteudo)} chars)"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class EditFileTool(Tool):
    name = "editar_arquivo"
    description = "Edita arquivo substituindo um trecho específico"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        antigo = params.get("antigo", "")
        novo = params.get("novo", "")
        try:
            path = ReadFileTool._resolve(path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if antigo not in content:
                return ToolResult(False, error="Trecho antigo não encontrado no arquivo")

            new_content = content.replace(antigo, novo, 1)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            return ToolResult(
                success=True,
                data={"path": path},
                display=f"🔧 Editado: {path}\n  - {len(antigo)} chars removidos\n  + {len(novo)} chars adicionados"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class ListDirTool(Tool):
    name = "listar_pasta"
    description = "Lista arquivos e pastas em um diretório"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            path = ReadFileTool._resolve(path)
            if not os.path.isdir(path):
                return ToolResult(False, error="Não é um diretório")

            items = []
            for entry in sorted(os.listdir(path)):
                full = os.path.join(path, entry)
                is_dir = os.path.isdir(full)
                size = "" if is_dir else f"{os.path.getsize(full):,}B"
                items.append({
                    "name": entry,
                    "is_dir": is_dir,
                    "size": size,
                    "path": full,
                })

            return ToolResult(
                success=True,
                data={"path": path, "items": items, "count": len(items)},
                display=f"📁 {path}\n  {len(items)} itens"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class CreateDirTool(Tool):
    name = "criar_pasta"
    description = "Cria diretório"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            path = ReadFileTool._resolve(path)
            os.makedirs(path, exist_ok=True)
            return ToolResult(
                success=True,
                data={"path": path},
                display=f"📁 Pasta criada: {path}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class DeleteTool(Tool):
    name = "deletar"
    description = "Deleta arquivo ou pasta"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        path = params.get("path", "")
        try:
            path = ReadFileTool._resolve(path)
            safe, msg = self._is_safe(path)
            if not safe:
                return ToolResult(False, error=f"Bloqueado: {msg}")

            if not os.path.exists(path):
                return ToolResult(False, error="Não existe")

            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

            return ToolResult(True, data={"path": path}, display=f"🗑️ Deletado: {path}")
        except Exception as e:
            return ToolResult(False, error=str(e))

    @staticmethod
    def _is_safe(path: str) -> tuple:
        protected = [
            os.environ.get("SYSTEMROOT", r"C:\Windows"),
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]
        abs_path = os.path.abspath(path).lower()
        for p in protected:
            if abs_path.startswith(p.lower()):
                return False, p
        if abs_path in ("c:\\", "c:/", "/"):
            return False, "raiz do disco"
        return True, ""


class MoveTool(Tool):
    name = "mover"
    description = "Move arquivo ou pasta"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        src = ReadFileTool._resolve(params.get("src", ""))
        dst = ReadFileTool._resolve(params.get("dst", ""))
        try:
            shutil.move(src, dst)
            return ToolResult(True, data={"src": src, "dst": dst},
                              display=f"➡️ {src} → {dst}")
        except Exception as e:
            return ToolResult(False, error=str(e))
