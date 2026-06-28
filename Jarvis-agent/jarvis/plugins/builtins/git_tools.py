"""Plugin de ferramentas Git."""

import subprocess
from pathlib import Path
from typing import Dict

from ...tools.base import Tool, ToolResult
from ..loader import plugin

__plugin_name__ = "Git Tools"
__plugin_version__ = "1.0.0"
__plugin_author__ = "JARVIS"
__plugin_description__ = "Operações Git (status, commit, push, log, diff)"


def _run_git(args: list, cwd: str = None) -> ToolResult:
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30,
            cwd=cwd or str(Path.cwd())
        )
        return ToolResult(
            success=(result.returncode == 0),
            data={"stdout": result.stdout, "stderr": result.stderr},
            display=result.stdout or result.stderr
        )
    except FileNotFoundError:
        return ToolResult(False, error="Git não instalado")
    except Exception as e:
        return ToolResult(False, error=str(e))


class GitStatusTool(Tool):
    name = "git_status"
    description = "Mostra status do repositório Git"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        return _run_git(["status"])


class GitLogTool(Tool):
    name = "git_log"
    description = "Mostra histórico de commits"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        limit = params.get("limit", 10)
        return _run_git(["log", f"--oneline", f"-{limit}"])


class GitDiffTool(Tool):
    name = "git_diff"
    description = "Mostra diff de mudanças não commitadas"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        return _run_git(["diff"])


class GitCommitTool(Tool):
    name = "git_commit"
    description = "Faz commit das mudanças staged"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        message = params.get("message", "")
        if not message:
            return ToolResult(False, error="Mensagem de commit vazia")
        return _run_git(["commit", "-m", message])


class GitAddTool(Tool):
    name = "git_add"
    description = "Adiciona arquivos ao staging"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        files = params.get("files", ".")
        if isinstance(files, list):
            return _run_git(["add"] + files)
        return _run_git(["add", files])


class GitPushTool(Tool):
    name = "git_push"
    description = "Faz push das mudanças pro remote"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        remote = params.get("remote", "origin")
        branch = params.get("branch", "")
        args = ["push", remote]
        if branch:
            args.append(branch)
        return _run_git(args)


class GitPullTool(Tool):
    name = "git_pull"
    description = "Faz pull das mudanças do remote"
    dangerous = True

    def execute(self, params: Dict) -> ToolResult:
        return _run_git(["pull"])


class GitCloneTool(Tool):
    name = "git_clone"
    description = "Clona um repositório"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        url = params.get("url", "")
        target = params.get("target", "")
        if not url:
            return ToolResult(False, error="URL vazia")
        args = ["clone", url]
        if target:
            args.append(target)
        return _run_git(args)
