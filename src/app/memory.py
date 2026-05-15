# src/app/memory.py

from .init import os_mod
from .init import json_mod
from .init import inspect_mod
from .init import qt_widgets_mod

class Memory:
    def __init__(self, work_path):
        self.work_path = work_path
        self.context = ""
        self.prompt = ""
        self.file = self._ensure_file()

    def _debug(self, message: str) -> None:
        frame = inspect_mod.currentframe().f_back
        full_path = frame.f_code.co_filename

        parent, filename = os_mod.path.split(full_path)
        parent = os_mod.path.basename(parent)

        short_path = f"{parent}/{filename}"

        line_number = frame.f_lineno
        print(f"[{short_path}:{line_number}] {message}")

    def _ensure_file(self):
        base = self.work_path
        if not base:
            base = os_mod.getcwd()
        if not os_mod.path.exists(base):
            os_mod.makedirs(base)
        path = os_mod.path.join(base, "session.md")
        exists = os_mod.path.exists(path)
        if not exists:
            f = open(path, "w", encoding="utf-8")
            f.close()
        return path

    def context_set(self, text):
        self.context = text

    def context_get(self):
        return self.context

    def prompt_set(self, text):
        self.prompt = text

    def prompt_get(self):
        return self.prompt

    def _write(self, block):
        f = open(self.file, "a", encoding="utf-8")
        f.write(block)
        f.write("\n")
        f.close()

    def session_event(self, type_str, message):
        block = f"# {type_str}\n```\n{message}\n```\n\n"
        self._write(block)

    def load_text(self):
        dlg = qt_widgets_mod.QFileDialog
        path, _ = dlg.getOpenFileName(
            None,
            "open",
            "",
            "Text (*.txt *.md *.log);;All (*)",
        )
        if not path:
            return ""
        f = open(path, "r", encoding="utf-8")
        data = f.read()
        f.close()
        return data


memory = Memory
