"""Plugin de ferramentas Web (HTTP, scraping, download)."""

import requests
import urllib.parse
from pathlib import Path
from typing import Dict

from ...tools.base import Tool, ToolResult

__plugin_name__ = "Web Tools"
__plugin_version__ = "1.0.0"
__plugin_author__ = "JARVIS"
__plugin_description__ = "Requisições HTTP, download de arquivos, info de URLs"


class HttpGetTool(Tool):
    name = "http_get"
    description = "Faz GET request e retorna conteúdo"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        url = params.get("url", "")
        if not url:
            return ToolResult(False, error="URL vazia")

        try:
            resp = requests.get(url, timeout=15)
            return ToolResult(
                success=(resp.status_code == 200),
                data={
                    "status": resp.status_code,
                    "headers": dict(resp.headers),
                    "content": resp.text[:5000],
                    "length": len(resp.text),
                },
                display=f"🌐 GET {url}\nStatus: {resp.status_code}\nTamanho: {len(resp.text)} chars"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class DownloadFileTool(Tool):
    name = "download_file"
    description = "Baixa arquivo da web"
    dangerous = True
    requires_confirmation = True

    def execute(self, params: Dict) -> ToolResult:
        url = params.get("url", "")
        dest = params.get("dest", "")

        if not url:
            return ToolResult(False, error="URL vazia")

        # Se não tem destino, usa Desktop
        if not dest:
            dest = str(Path.home() / "Desktop" / Path(url).name)
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            resp = requests.get(url, stream=True, timeout=60)
            resp.raise_for_status()

            total = int(resp.headers.get("content-length", 0))
            written = 0

            with open(dest, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        written += len(chunk)

            return ToolResult(
                True,
                data={"path": str(dest), "size": written},
                display=f"⬇️ Baixado: {dest} ({written:,} bytes)"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class CheckUrlTool(Tool):
    name = "check_url"
    description = "Verifica se URL está acessível"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        url = params.get("url", "")
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            return ToolResult(
                True,
                data={"status": resp.status_code, "url": resp.url},
                display=f"✓ {url} → {resp.status_code}"
            )
        except Exception as e:
            return ToolResult(False, error=str(e))


class ShortenUrlTool(Tool):
    name = "shorten_url"
    description = "Encurta URL (via tinyurl)"
    dangerous = False

    def execute(self, params: Dict) -> ToolResult:
        url = params.get("url", "")
        try:
            resp = requests.get(f"http://tinyurl.com/api-create.php?url={urllib.parse.quote(url)}",
                              timeout=10)
            if resp.status_code == 200:
                return ToolResult(True, data={"short": resp.text},
                                  display=f"🔗 {url} → {resp.text}")
            return ToolResult(False, error="Falha ao encurtar")
        except Exception as e:
            return ToolResult(False, error=str(e))
