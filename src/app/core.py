# src/app/core.py

from .init import queue_mod
from .init import time_mod
from .init import threading_mod
from .gui import Gui
from .memory import Memory
from .mistral import Mistral
from .init import os_mod

class Engine:
    def __init__(self):
        self.reply_buffer = ""
        self.queue = queue_mod.Queue()
        self.work_path = os_mod.environ.get("WORK_PATH", "")
        self.ui = Gui(self.queue)
        self.memory = Memory(self.work_path)
        self.mistral = Mistral(self.queue)
        self.running = False
        self.thread = None
        self.pending = False

    def start(self):
        self.running = True
        self._start_timer()
        self.ui.show_ui()

    def _send(self, src, data):
        self.memory._debug(f"src={src}, data={data}")
        self.queue.put((src, data))

    def _start_timer(self):
        from .init import qt_core_mod
        self.timer = qt_core_mod.QTimer()
        self.timer.timeout.connect(self._poll)
        self.timer.start(10)

    def _poll(self):
        if not self.running:
            return
        if self.queue.empty():
            return
        msg = self.queue.get()
        src, data = msg
        self._dispatch(src, data)

    def _dispatch(self, src, data):
        if src.startswith("ui_"):
            self._ui_event(src, data)
            return
        if src == "mistral":
            self._mistral_event(data)
            return

    def _ui_event(self, src, data):
        if src == "ui_logger":
            self.ui.logger_set(data)
            return
        if src == "ui_button_submit":
            self._submit()
            return
        if src == "ui_button_clear":
            self._clear()
            return
        if src == "ui_button_zoom":
            self.ui.zoom_ui()
            return
        if src == "ui_button_append":
            self._append(data)
            return
        if src == "ui_button_exit":
            self.running = False
            return

    def _submit(self):
        self.reply_buffer = ""

        ctx = self.ui.context_get()
        pr = self.ui.prompt_get()

        if ctx.strip() != "" and not ctx.endswith("\n"):
            self.ui.append_ui("\n")

        if ctx.strip() == "":
            self.ui.append_ui("# prompt\n")
        else:
            self.ui.append_ui("\n# prompt\n")

        self.ui.append_ui(pr + "\n")

        new_ctx = self.ui.context_get()
        self.memory.context_set(new_ctx)

        self.memory.prompt_set(pr)
        self.memory.session_event("prompt", pr)

        self.pending = True

        self.mistral.request(new_ctx)
        self._send("ui_logger", "Submit Prompt.")


    def _clear(self):
        self.memory.context_set("")
        self.memory.prompt_set("")
        self.memory.session_event("log", "clear")
        self.ui.clear_ui()
        self._send("ui_logger", "Cleared.")

    def _append(self, data):
        txt = self.memory.load_text()
        if not txt:
            return
        self.ui.append_ui(txt)
        ctx = self.memory.context_get()
        buf = ctx + txt
        self.memory.context_set(buf)
        self._send("ui_logger", "Appending text.")

    def _mistral_event(self, data):
        if data in ("timeout", "end", "stop"):
            ctx = self.memory.context_get()
            new_ctx = ctx + "\n# assistant\n"\
                + self.reply_buffer + "\n"
            self.memory.context_set(new_ctx)

            self.ui.context_set(new_ctx)

            self.memory.session_event("assistant",
                self.reply_buffer)

            self.memory.session_event("assistant",
                "assistant: finished")

            self.reply_buffer = ""
            self.pending = False

            self._send("ui_logger", "Model replied.")

            return

        if self.reply_buffer == "":
            self.ui.append_ui("\n# assistant\n")
            self.memory.session_event("log",
                "assistant: started")

        self.reply_buffer += data
        self.ui.append_ui(data)

engine = Engine()
