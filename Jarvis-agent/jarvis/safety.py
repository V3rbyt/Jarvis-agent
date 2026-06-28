"""Camada de seguranca."""

import os
import re
from typing import Tuple

PROTECTED_PATHS = [
    os.environ.get("SYSTEMROOT", r"C:\Windows"),
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\Boot",
]


def is_path_safe(path: str) -> Tuple[bool, str]:
    try:
        abs_path = os.path.abspath(path).lower()
    except Exception:
        return False, "Caminho invalido"
    for protected in PROTECTED_PATHS:
        if abs_path.startswith(protected.lower()):
            return False, protected
    if abs_path in ("c:\\", "c:/", "/"):
        return False, "raiz do disco"
    return True, ""


def sanitize_speech(text: str) -> str:
    user_home = os.path.expanduser("~")
    text = re.sub(
        rf"{re.escape(user_home)}\\([^\\]+)\\",
        r"na pasta \1: ", text, flags=re.IGNORECASE
    )
    text = re.sub(r"[A-Z]:\\Users\\[^\\]+\\", "na sua pasta: ", text)
    text = re.sub(r"[A-Z]:\\Program Files[^\\]*\\", "na pasta de programas: ", text)
    return text


def format_path_for_speech(path: str) -> str:
    user_home = os.path.expanduser("~")
    path_norm = path.replace("\\", "/")
    if path_norm.lower().startswith(user_home.lower().replace("\\", "/")):
        rel = path_norm[len(user_home):].strip("/")
        parts = rel.split("/", 1)
        if len(parts) > 1:
            folder = parts[0].lower()
            mapping = {
                "desktop": "na area de trabalho",
                "documents": "em Documentos",
                "downloads": "em Downloads",
            }
            if folder in mapping:
                return mapping[folder]
        return f"em {rel}"
    return path
