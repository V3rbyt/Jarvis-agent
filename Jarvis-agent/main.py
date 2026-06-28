"""JARVIS Agent — entry point."""

import sys
import tkinter as tk
from tkinter import messagebox

from jarvis import config
from jarvis.ui import JarvisApp


def main():
    # Valida configurações
    try:
        config.validate()
    except ValueError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Configuração inválida", str(e))
        sys.exit(1)

    # Cria app
    root = tk.Tk()
    app = JarvisApp(root)

    # Cleanup ao fechar
    root.protocol("WM_DELETE_WINDOW", lambda: cleanup(app))

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


def cleanup(app):
    """Limpa recursos ao fechar."""
    try:
        app.voice.stop()
        app.stt.stop()
    except Exception:
        pass
    app.root.destroy()


if __name__ == "__main__":
    main()
