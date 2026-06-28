"""Tools de execução de comandos."""

import subprocess
import os
from typing import Dict

from .base import Tool, ToolResult


class RunCommandTool(Tool):
    name = "executar_comando"
    description = "Executa um comando de terminal (cmd/PowerShell)"
    dangerous = True
    requires_confirmation = True

    # Whitelist de comandos permitidos
    SAFE_COMMANDS = {
        "python", "pip", "git", "dir", "ls", "echo", "type", "cat",
        "ipconfig", "ping", "tracert", "nslookup", "systeminfo",
        "tasklist", "taskkill", "where", "find", "findstr", "grep",
        "node", "npm", "yarn", "dotnet", "cargo", "rustc",
        "mkdir", "rmdir", "cd", "pwd", "whoami", "hostname",
        "ver", "date", "time", "cls", "clear",
    }

    BLOCKED_TOKENS = {"format", "del /f", "rm -rf", "rd /s", "shutdown",
                      "reg delete", "diskpart", "bcdedit", "cipher /w"}

    def execute(self, params: Dict) -> ToolResult:
        cmd = params.get("cmd", "").strip()
        if not cmd:
            return ToolResult(False, error="Comando vazio")

        cmd_lower = cmd.lower()
        for blocked in self.BLOCKED_TOKENS:
            if blocked in cmd_lower:
                return ToolResult(False, error=f"Comando bloqueado: {blocked}")

        first_token = cmd.split()[0].lower()
        if first_token not in self.SAFE_COMMANDS:
            return ToolResult(False, error=f"Comando não permitido: {first_token}")

        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=30,
                cwd=params.get("cwd", os.getcwd())
            )
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            return ToolResult(
                success=(result.returncode == 0),
                data={
                    "stdout": stdout,
                    "stderr": stderr,
                    "returncode": result.returncode,
                    "cmd": cmd,
                },
                display=f"$ {cmd}\n{stdout}{stderr}".strip()[:1000]
            )
        except subprocess.TimeoutExpired:
            return ToolResult(False, error="Timeout (>30s)")
        except Exception as e:
            return ToolResult(False, error=str(e))


class InstallPipTool(Tool):
    name = "instalar_pip"
    description = "Instala um pacote Python via pip"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        package = params.get("pacote", "")
        if not package:
            return ToolResult(False, error="Pacote vazio")

        try:
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True, text=True, timeout=120
            )
            return ToolResult(
                success=(result.returncode == 0),
                data={"output": result.stdout, "package": package},
                display=f"📦 pip install {package}\n{(result.stdout or '')[:300]}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))
