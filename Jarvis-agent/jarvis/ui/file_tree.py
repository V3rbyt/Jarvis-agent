"""Árvore de arquivos (versao robusta)."""

import os
from pathlib import Path
from typing import Callable, Optional

import tkinter as tk
from tkinter import ttk

from .. import config

IGNORED = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".idea", ".vscode", ".next",
    "AppData", "$Recycle.Bin", "System Volume Information",
    "$WinREAgent", "Config.Msi", "PerfLogs", "Recovery",
    "Program Files", "Program Files (x86)", "ProgramData",
}

MAX_DEPTH = 3
MAX_ITEMS = 500


class FileTree(tk.Frame):
    def __init__(self, parent, path, on_select=None):
        super().__init__(parent, bg=config.BG_PANEL)
        self.path = path
        self.on_select = on_select
        self.item_count = 0

        self.tree = ttk.Treeview(self, show="tree", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)

        style = ttk.Style()
        try:
            style.configure("Treeview", background=config.BG_PANEL,
                fieldbackground=config.BG_PANEL, foreground=config.TEXT_MAIN, rowheight=22)
            style.map("Treeview", background=[("selected", config.ACCENT_BLUE)])
        except Exception: pass

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.load(path)

    def load(self, path):
        self.path = path
        self.item_count = 0
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
        except Exception: pass
        try:
            self._populate("", path, 0)
        except Exception as e:
            print(f"[FileTree] Erro: {e}")

    def _populate(self, parent_node, path, depth):
        if depth > MAX_DEPTH: return
        if self.item_count > MAX_ITEMS: return
        if not path or not os.path.exists(path): return

        try:
            path_obj = Path(path)
            basename = str(path_obj.name or path)[:50]

            node = self.tree.insert(parent_node, "end",
                text=f"\U0001f4c1 {basename}", values=(path,))
            self.item_count += 1

            try:
                entries = list(os.scandir(path))
            except (PermissionError, OSError, FileNotFoundError):
                return

            entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

            for entry in entries:
                if self.item_count > MAX_ITEMS: break

                try:
                    if entry.name in IGNORED: continue
                    if entry.name.startswith(".") and entry.name not in (".env", ".gitignore"):
                        continue

                    full = entry.path

                    if entry.is_dir():
                        try:
                            self._populate(node, full, depth + 1)
                        except (PermissionError, OSError): continue
                    elif entry.is_file():
                        icon = self._icon_for(entry.name)
                        self.tree.insert(node, "end",
                            text=f"{icon} {entry.name}", values=(full,))
                        self.item_count += 1
                except (PermissionError, OSError, FileNotFoundError): continue
                except Exception: continue

        except (PermissionError, OSError): pass
        except Exception as e:
            print(f"[FileTree] Erro em {path}: {e}")

    @staticmethod
    def _icon_for(name):
        try:
            ext = os.path.splitext(str(name))[1].lower()
        except Exception:
            return "\U0001f4c4"

        return {
            ".py": "\U0001f40d", ".js": "\U0001f4dc", ".ts": "\U0001f4dc",
            ".html": "\U0001f310", ".css": "\U0001f3a8", ".json": "\U0001f4cb",
            ".md": "\U0001f4dd", ".txt": "\U0001f4c4", ".log": "\U0001f4dc",
            ".png": "\U0001f5bc", ".jpg": "\U0001f5bc", ".jpeg": "\U0001f5bc",
            ".gif": "\U0001f5bc", ".svg": "\U0001f5bc",
            ".mp3": "\U0001f3b5", ".mp4": "\U0001f3ac", ".wav": "\U0001f3b5",
            ".pdf": "\U0001f4d5", ".doc": "\U0001f4d8", ".docx": "\U0001f4d8",
            ".xls": "\U0001f4d7", ".xlsx": "\U0001f4d7",
            ".zip": "\U0001f4e6", ".rar": "\U0001f4e6", ".7z": "\U0001f4e6",
            ".exe": "\u2699", ".msi": "\u2699", ".bat": "\u2699",
            ".env": "\U0001f512", ".gitignore": "\U0001f512",
            ".yml": "\u2699", ".yaml": "\u2699", ".sql": "\U0001f5c4",
            ".db": "\U0001f5c4", ".java": "\u2615", ".cpp": "\u2699",
            ".c": "\u2699", ".go": "\U0001f439", ".rs": "\U0001f980",
        }.get(ext, "\U0001f4c4")

    def _on_select(self, event):
        sel = self.tree.selection()
        if sel and self.on_select:
            try:
                values = self.tree.item(sel[0])["values"]
                if values:
                    self.on_select(values[0])
            except Exception: pass
