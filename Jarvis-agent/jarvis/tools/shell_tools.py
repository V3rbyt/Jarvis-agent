"""Tools de execução de comandos."""

import subprocess
import os
from typing import Dict

from .base import Tool, ToolResult


class RunCommandTool(Tool):
    name = "executar_comando"
    description = "Executa comando de terminal"
    dangerous = True
    requires_confirmation = True

    SAFE_COMMANDS = {
        "python", "pip", "git", "dir", "ls", "echo",
        "ipconfig", "ping", "nslookup", "systeminfo",
        "tasklist", "whoami", "hostname", "where", "find", "findstr",
        "node", "npm", "cd", "pwd", "ver", "date", "cls",
    }
    BLOCKED = {"format", "del /f", "rd /s /q", "shutdown", "reg delete"}

    def execute(self, params: Dict) -> ToolResult:
        cmd = params.get("cmd", "").strip()
        if not cmd:
            return ToolResult(False, error="Comando vazio")
        if any(b in cmd.lower() for b in self.BLOCKED):
            return ToolResult(False, error="Comando bloqueado")
        first = cmd.split()[0].lower()
        if first not in self.SAFE_COMMANDS:
            return ToolResult(False, error=f"Não permitido: {first}")
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True, timeout=30)
            return ToolResult(
                r.returncode == 0,
                data={"stdout": r.stdout, "stderr": r.stderr},
                display=f"$ {cmd}\n{(r.stdout or r.stderr)[:500]}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class InstallPipTool(Tool):
    name = "instalar_pip"
    description = "Instala pacote Python"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        pkg = params.get("pacote", "")
        if not pkg:
            return ToolResult(False, error="Pacote vazio")
        try:
            r = subprocess.run(["pip", "install", pkg], capture_output=True,
                               text=True, timeout=120)
            return ToolResult(
                r.returncode == 0,
                display=f"📦 pip install {pkg}\n{(r.stdout or '')[:300]}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))
