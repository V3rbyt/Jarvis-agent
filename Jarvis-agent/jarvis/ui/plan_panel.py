"""Painel de plano de execução."""

import tkinter as tk
from .. import config


class PlanPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=config.BG_PANEL, height=80)
        self.pack_propagate(False)

        self.title_lbl = tk.Label(self, text="", font=("Consolas", 10, "bold"),
                                  fg=config.ACCENT_YEL, bg=config.BG_PANEL,
                                  anchor="w")
        self.title_lbl.pack(fill="x", padx=10, pady=(8, 2))

        self.steps_lbl = tk.Label(self, text="", font=("Consolas", 9),
                                  fg=config.TEXT_DIM, bg=config.BG_PANEL,
                                  anchor="w", justify="left", wraplength=900)
        self.steps_lbl.pack(fill="x", padx=10)

    def show_plan(self, description: str, steps: list, current: int):
        self.title_lbl.config(text=f"📋 {description}")
        text = "  →  ".join([f"[{i+1}] {s}" for i, s in enumerate(steps)])
        self.steps_lbl.config(text=text if text else "Sem passos definidos")

    def clear(self):
        self.title_lbl.config(text="")
        self.steps_lbl.config(text="")
