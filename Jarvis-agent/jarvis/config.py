"""Configuracoes centralizadas."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
LOG_FILE = DATA_DIR / "jarvis.log"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

TTS_VOICE = os.getenv("TTS_VOICE", "pt-BR-FranciscaNeural")
STT_LANGUAGE = os.getenv("STT_LANGUAGE", "pt-BR")

MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))
REQUIRE_CONFIRMATION = os.getenv("REQUIRE_CONFIRMATION", "true").lower() == "true"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

BG_DARK     = "#1a1a1a"
BG_PANEL    = "#252525"
BG_INPUT    = "#2d2d2d"
BORDER      = "#3a3a3a"
TEXT_MAIN   = "#e6e6e6"
TEXT_DIM    = "#8b8b8b"
ACCENT_BLUE = "#3b82f6"
ACCENT_GREEN= "#10b981"
ACCENT_RED  = "#ef4444"
ACCENT_YEL  = "#f59e0b"
ACCENT_PURP = "#a855f7"

SYSTEM_PROMPT = """Voce e JARVIS, um assistente de IA estilo Claude Code.

Responda em JSON para acoes:
{"plano": "...", "passos": [...], "tool": "nome", "params": {...}, "fala": "..."}

Para conversa normal use tool="nenhuma".

Tools: ler_arquivo, escrever_arquivo, editar_arquivo, listar_pasta,
buscar_arquivos, buscar_conteudo, executar_comando, criar_pasta,
deletar, mover, instalar_pip, abrir_app, abrir_site, screenshot,
sistema_info, lembrar_fato, buscar_memoria.

Respostas curtas em portugues brasileiro."""


def validate():
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        raise ValueError(
            "Nenhuma API key configurada. Adicione GEMINI_API_KEY ou GROQ_API_KEY no .env"
        )
