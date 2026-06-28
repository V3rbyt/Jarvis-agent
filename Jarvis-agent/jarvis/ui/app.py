"""Interface principal estilo Claude Code."""

import threading
import time
import tkinter as tk
from pathlib import Path
from queue import Queue
from tkinter import filedialog, messagebox, scrolledtext

from .. import config
from ..agent import Executor, Memory, Planner
from ..analytics import AnalyticsTracker
from ..brain import Brain
from ..memory import LongTermMemory
from ..plugins import PluginManager
from ..safety import sanitize_speech
from ..tools import ToolRegistry
from ..voice import STTEngine, VoiceEngine
from .file_tree import FileTree
from .plan_panel import PlanPanel


class JarvisApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("JARVIS — AI Agent")
        self.root.configure(bg=config.BG_DARK)
        self.root.geometry("1100x780")

        # ============ CÉREBRO ============
        self.brain = Brain()
        self.memory = Memory()
        self.voice = VoiceEngine()
        self.stt = STTEngine()

        # ============ SISTEMAS ============
        self.plugins = PluginManager()
        self.long_memory = LongTermMemory()
        self.analytics = AnalyticsTracker()

        # ============ TOOLS + EXECUTOR ============
        self.registry = ToolRegistry()
        self.executor = Executor(
            registry=self.registry,
            plugins=self.plugins,
            on_step_start=self._on_step_start,
            on_step_done=self._on_step_done,
            on_confirm=self._confirm_action,
            analytics=self.analytics,
        )
        self.planner = Planner(self.brain)
        self.analytics.track("app_start", "jarvis")

        # ============ UI STATE ============
        self.ui_queue: Queue = Queue()
        self.cwd = str(Path.home())

        # ============ MONTA INTERFACE ============
        self._build_ui()
        self._poll_queue()

        # Atalhos
        self.root.bind("<Control-Return>", lambda e: self._on_send())
        self.root.bind("<Control-m>", lambda e: self._toggle_mic())
        self.root.bind("<Escape>", lambda e: self._voice_stop())

    # ============================================================
    # BUILD UI
    # ============================================================
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=config.BG_PANEL, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="⚡ JARVIS", font=("Segoe UI", 14, "bold"),
                 fg=config.ACCENT_BLUE, bg=config.BG_PANEL).pack(side="left", padx=15)
        tk.Label(header, text="AI Agent", font=("Segoe UI", 10),
                 fg=config.TEXT_DIM, bg=config.BG_PANEL).pack(side="left")

        self.status_lbl = tk.Label(header, text="● Online",
                                   font=("Consolas", 9), fg=config.ACCENT_GREEN,
                                   bg=config.BG_PANEL)
        self.status_lbl.pack(side="right", padx=15)

        # Layout 3 colunas
        main = tk.Frame(self.root, bg=config.BG_DARK)
        main.pack(fill="both", expand=True, padx=2, pady=2)

        # ---- Esquerda: árvore de arquivos ----
        left = tk.Frame(main, bg=config.BG_PANEL, width=220)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="📁 ARQUIVOS", font=("Consolas", 9, "bold"),
                 fg=config.TEXT_DIM, bg=config.BG_PANEL).pack(anchor="w", padx=10, pady=(10, 5))

        path_frame = tk.Frame(left, bg=config.BG_PANEL)
        path_frame.pack(fill="x", padx=5)
        self.cwd_var = tk.StringVar(value=self.cwd)
        tk.Entry(path_frame, textvariable=self.cwd_var, font=("Consolas", 9),
                 bg=config.BG_INPUT, fg=config.TEXT_MAIN,
                 insertbackground=config.TEXT_MAIN,
                 relief="flat").pack(side="left", fill="x", expand=True)
        tk.Button(path_frame, text="↻", font=("Consolas", 9),
                  bg=config.BG_INPUT, fg=config.TEXT_MAIN,
                  relief="flat", command=self._refresh_tree).pack(side="left")

        self.tree = FileTree(left, self.cwd, on_select=self._on_file_select)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

        # ---- Centro: chat + plano ----
        center = tk.Frame(main, bg=config.BG_DARK)
        center.pack(side="left", fill="both", expand=True)

        # Plano
        self.plan_panel = PlanPanel(center)
        self.plan_panel.pack(fill="x", padx=5, pady=5)

        # Chat
        chat_frame = tk.Frame(center, bg=config.BG_PANEL)
        chat_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.chat_box = scrolledtext.ScrolledText(
            chat_frame, font=("Consolas", 11),
            bg=config.BG_PANEL, fg=config.TEXT_MAIN,
            insertbackground=config.ACCENT_BLUE,
            relief="flat", wrap="word", state="disabled",
            padx=15, pady=10
        )
        self.chat_box.pack(fill="both", expand=True)

        for tag, color in [
            ("you", config.ACCENT_BLUE),
            ("jarvis", config.ACCENT_GREEN),
            ("system", config.TEXT_DIM),
            ("error", config.ACCENT_RED),
            ("tool", config.ACCENT_PURP),
            ("tool_out", config.TEXT_MAIN),
            ("plan", config.ACCENT_YEL),
        ]:
            self.chat_box.tag_configure(tag, foreground=color)

        # Input
        input_frame = tk.Frame(center, bg=config.BG_DARK)
        input_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.input_box = tk.Text(input_frame, height=3, font=("Consolas", 11),
                                 bg=config.BG_INPUT, fg=config.TEXT_MAIN,
                                 insertbackground=config.ACCENT_BLUE,
                                 relief="flat", wrap="word",
                                 padx=10, pady=8)
        self.input_box.pack(side="left", fill="x", expand=True)
        self.input_box.bind("<Control-Return>", lambda e: self._on_send())

        btns = tk.Frame(input_frame, bg=config.BG_DARK)
        btns.pack(side="left", fill="y", padx=(5, 0))

        tk.Button(btns, text="🎙", font=("Segoe UI", 12),
                  bg=config.BG_INPUT, fg=config.ACCENT_BLUE,
                  relief="flat", command=self._toggle_mic).pack(fill="x", pady=1)
        tk.Button(btns, text="▶", font=("Segoe UI", 12, "bold"),
                  bg=config.ACCENT_BLUE, fg="white",
                  relief="flat", command=self._on_send).pack(fill="x", pady=1)

        # ---- Direita: terminal output ----
        right = tk.Frame(main, bg=config.BG_PANEL, width=300)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="💻 OUTPUT", font=("Consolas", 9, "bold"),
                 fg=config.TEXT_DIM, bg=config.BG_PANEL).pack(anchor="w", padx=10, pady=(10, 5))

        self.output_box = scrolledtext.ScrolledText(
            right, font=("Consolas", 9),
            bg="#1e1e1e", fg=config.TEXT_MAIN,
            relief="flat", wrap="word", state="disabled",
            padx=10, pady=10
        )
        self.output_box.pack(fill="both", expand=True, padx=5, pady=5)

        self._append_chat("JARVIS", "Sistema pronto. Me diga o que fazer.\n\n", "jarvis")

    # ============================================================
    # FILE TREE HANDLERS
    # ============================================================
    def _on_file_select(self, path: str):
        self.cwd_var.set(str(Path(path).parent))
        self._append_chat("Sistema", f"📂 {path}\n", "system")

    def _refresh_tree(self):
        try:
            new_cwd = self.cwd_var.get()
            if Path(new_cwd).is_dir():
                self.cwd = new_cwd
                self.tree.load(self.cwd)
        except Exception as e:
            self._append_chat("Erro", str(e), "error")

    # ============================================================
    # MICROFONE
    # ============================================================
    def _toggle_mic(self):
        if self.stt.listening:
            self.stt.stop()
            self._append_chat("Sistema", "Microfone desativado.\n", "system")
        else:
            def on_text(text):
                self.ui_queue.put(("user_msg", text))
                self.input_box.delete("1.0", "end")
                self.input_box.insert("1.0", text)
                self._on_send()

            try:
                self.stt.start(on_text)
                self._append_chat("Sistema", "Microfone ativo.\n", "system")
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _voice_stop(self):
        if self.voice.speaking:
            self.voice.stop()
            self._append_chat("Sistema", "[fala interrompida]\n", "system")

    # ============================================================
    # ENVIO DE MENSAGEM
    # ============================================================
    def _on_send(self):
        text = self.input_box.get("1.0", "end").strip()
        if not text:
            return
        self.input_box.delete("1.0", "end")
        self._append_chat("Você", f"{text}\n", "you")
        self.memory.add("user", text)
        threading.Thread(target=self._think_and_execute,
                         args=(text,), daemon=True).start()

    def _think_and_execute(self, user_text: str):
        try:
            self.ui_queue.put(("status", "Pensando...", config.ACCENT_PURP))
            plan = self.planner.plan(user_text, self.memory.get())

            self.ui_queue.put(("plan", plan))

            result = self.executor.execute(plan)

            self.memory.add("assistant", plan.fala)

            self.ui_queue.put(("tool_result", result, plan.fala))
        except Exception as e:
            self.ui_queue.put(("error_msg", str(e)))

    # ============================================================
    # EXECUTOR CALLBACKS
    # ============================================================
    def _on_step_start(self, plan):
        self.ui_queue.put(("tool_start", plan.tool, plan.params))

    def _on_step_done(self, plan, result):
        self.ui_queue.put(("tool_done", result))

    def _confirm_action(self, plan) -> bool:
        """Mostra confirmação na UI."""
        result_holder = [None]

        def ask():
            msg = (f"⚠ Confirma executar?\n\n"
                   f"Tool: {plan.tool}\n"
                   f"Params: {plan.params}")
            result_holder[0] = messagebox.askyesno("Confirmação necessária", msg)

        self.root.after(0, ask)

        # Espera resultado na main thread
        timeout = 30
        start = time.time()
        while result_holder[0] is None and (time.time() - start) < timeout:
            time.sleep(0.05)
            try:
                self.root.update()
            except Exception:
                break

        return result_holder[0] if result_holder[0] is not None else False

    # ============================================================
    # UI HELPERS
    # ============================================================
    def _append_chat(self, sender: str, text: str, tag: str):
        self.chat_box.config(state="normal")
        if sender and sender not in ("Sistema", "Erro", "JARVIS"):
            self.chat_box.insert("end", f"{sender}: ", "system")
        self.chat_box.insert("end", text + "\n", tag)
        self.chat_box.see("end")
        self.chat_box.config(state="disabled")

    def _append_output(self, text: str):
        self.output_box.config(state="normal")
        self.output_box.insert("end", text + "\n")
        self.output_box.see("end")
        self.output_box.config(state="disabled")

    def _set_status(self, text: str, color: str = None):
        self.status_lbl.config(text=text, fg=color or config.ACCENT_GREEN)

    # ============================================================
    # POLL QUEUE (thread-safe UI updates)
    # ============================================================
    def _poll_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                kind = item[0]

                if kind == "user_msg":
                    text = item[1]
                    self._append_chat("Você", text, "you")

                elif kind == "plan":
                    plan = item[1]
                    self.plan_panel.show_plan(plan.description, plan.steps, 0)
                    self._append_chat("JARVIS", f"📋 Plano: {plan.description}\n", "plan")
                    if plan.steps:
                        for i, step in enumerate(plan.steps, 1):
                            self._append_chat("", f"  {i}. {step}\n", "system")

                elif kind == "tool_start":
                    tool_name = item[1]
                    params = item[2]
                    self._set_status(f"⚙ {tool_name}", config.ACCENT_PURP)
                    params_str = str(params)[:80]
                    self._append_chat("", f"⚙ {tool_name}({params_str})\n", "tool")

                elif kind == "tool_done":
                    result = item[1]
                    if result.success:
                        self._append_output(result.display)
                        self._append_chat("", f"✓ {result.display}\n", "tool_out")
                    else:
                        self._append_chat("Erro", f"✗ {result.error}\n", "error")

                elif kind == "tool_result":
                    result = item[1]
                    fala = item[2]
                    if fala:
                        self._append_chat("JARVIS", f"{fala}\n\n", "jarvis")
                        self.voice.speak(sanitize_speech(fala))
                    self._set_status("● Online", config.ACCENT_GREEN)

                elif kind == "error_msg":
                    self._append_chat("Erro", item[1] + "\n", "error")
                    self._set_status("● Erro", config.ACCENT_RED)

                elif kind == "status":
                    self._set_status(item[1], item[2] if len(item) > 2 else None)

        except Exception:
            pass
        self.root.after(80, self._poll_queue)
