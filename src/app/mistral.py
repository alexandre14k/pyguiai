# src/app/mistral.py

from .init import os_mod
from .init import json_mod
from .init import time_mod
from .init import threading_mod
from .init import requests_mod

class Mistral:
    def __init__(self, queue_ref):
        self.queue = queue_ref
        self.api_key = self._load_key()
        self.url = self._build_url()
        self.model = "mistral-large-latest"
        self.timeout = 5
        self.lock = threading_mod.Lock()
        self.worker = None
        self.cancel_flag = False
        self.in_code_block = False
        self.phrase_buffer = ""

    def _load_key(self):
        env = os_mod.environ
        key = env.get("MISTRAL_APIKEY", "")
        return key

    def _build_url(self):
        base = "https://api.mistral.ai"
        path = "/v1/chat/completions"
        url = base + path
        return url

    def _headers(self):
        token = f"Bearer {self.api_key}"
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
        }
        return headers

    def _payload(self, text):
        system_rules = (
            "write measured calm phrases to shorten replies"
            "reply in precise french-belgian manner"
        )

        messages = [
            {"role": "system", "content": system_rules},
            {"role": "user", "content": text},
        ]

        return {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

    def _put_token(self, token):
        if "```" in token:
            self.in_code_block = not self.in_code_block
            self.queue.put(("mistral", token))
            return

        if self.in_code_block:
            self.queue.put(("mistral", token))
            return

        self.phrase_buffer += token

        boundaries = (" ", ".", "!", "?", ",", ";", ":", "\n")

        if token in boundaries:
            phrase = self.phrase_buffer
            self.phrase_buffer = ""
            self.queue.put(("mistral", phrase))

    def _put_timeout(self):
        src = "mistral"
        data = "timeout"
        message = (src, data)
        self.queue.put(message)

    def _parse_line(self, line):
        text = line.decode("utf-8")
        stripped = text.strip()
        if not stripped:
            return ""
        if stripped.startswith("data:"):
            stripped = stripped[5:].strip()
        if stripped == "[DONE]":
            return ""
        try:
            obj = json_mod.loads(stripped)
        except Exception:
            return ""
        choice_list = obj.get("choices", [])
        if not choice_list:
            return ""
        choice = choice_list[0]
        delta = choice.get("delta") or choice.get("message") or {}
        content = delta.get("content", "")
        if content is None:
            content = ""
        return content

    def _stream_response(self, text):
        headers = self._headers()
        payload = self._payload(text)
        try:
            resp = requests_mod.post(
                self.url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=self.timeout,
            )
        except requests_mod.Timeout:
            self._put_timeout()
            return
        except Exception:
            self._put_timeout()
            return

        for line in resp.iter_lines():
            with self.lock:
                flag = self.cancel_flag
            if flag:
                break
            if not line:
                continue
            token = self._parse_line(line)
            if not token:
                continue
            self._put_token(token)

        if self.phrase_buffer:
            self.queue.put(("mistral", self.phrase_buffer))
            self.phrase_buffer = ""

        self.queue.put(("mistral", "end"))

    def _run_worker(self, text):
        self._stream_response(text)
        with self.lock:
            self.worker = None
            self.cancel_flag = False

    def request(self, text):
        with self.lock:
            if self.worker is not None:
                self.cancel_flag = True
        if self.worker is not None:
            while True:
                with self.lock:
                    active = self.worker is not None
                if not active:
                    break
                time_mod.sleep(0.01)
        with self.lock:
            self.cancel_flag = False
            thread_args = (text,)
            worker = threading_mod.Thread(
                target=self._run_worker,
                args=thread_args,
                daemon=True,
            )
            self.worker = worker
        worker.start()


mistral = Mistral
