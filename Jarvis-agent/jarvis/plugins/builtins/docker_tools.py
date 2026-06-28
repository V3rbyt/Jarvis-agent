"""Plugin Docker."""

import subprocess
from typing import Dict

from ...tools.base import Tool, ToolResult

__plugin_name__ = "Docker Tools"
__plugin_version__ = "1.0.0"
__plugin_author__ = "JARVIS"
__plugin_description__ = "Gerenciamento de containers Docker"


def _docker(args: list) -> ToolResult:
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True, text=True, timeout=60
        )
        return ToolResult(
            success=(result.returncode == 0),
            data={"stdout": result.stdout, "stderr": result.stderr},
            display=result.stdout or result.stderr
        )
    except FileNotFoundError:
        return ToolResult(False, error="Docker não instalado")
    except Exception as e:
        return ToolResult(False, error=str(e))


class DockerPsTool(Tool):
    name = "docker_ps"
    description = "Lista containers em execução"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        return _docker(["ps"])


class DockerImagesTool(Tool):
    name = "docker_images"
    description = "Lista imagens Docker"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        return _docker(["images"])


class DockerLogsTool(Tool):
    name = "docker_logs"
    description = "Mostra logs de um container"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        container = params.get("container", "")
        if not container:
            return ToolResult(False, error="Nome do container vazio")
        return _docker(["logs", "--tail", "50", container])


class DockerStopTool(Tool):
    name = "docker_stop"
    description = "Para um container"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        container = params.get("container", "")
        return _docker(["stop", container])


class DockerStartTool(Tool):
    name = "docker_start"
    description = "Inicia um container"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        container = params.get("container", "")
        return _docker(["start", container])
