"""LLM client."""
import requests
from typing import List, Dict
from .. import config


class Brain:
    def __init__(self):
        self.provider = "gemini" if config.GEMINI_API_KEY else "groq"
        self.session = requests.Session()
        if self.provider == "gemini":
            self.session.headers.update({"Content-Type": "application/json",
                "x-goog-api-key": config.GEMINI_API_KEY})
            self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent"
        else:
            self.session.headers.update({"Content-Type": "application/json",
                "Authorization": f"Bearer {config.GROQ_API_KEY}"})
            self.base_url = config.GROQ_URL

    def _call_gemini(self, messages):
        sys = ""
        contents = []
        for m in messages:
            if m["role"] == "system":
                sys = m["content"]
            elif m["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": m["content"]}]})
            elif m["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": m["content"]}]})
        payload = {"systemInstruction": {"parts": [{"text": sys}]},
                   "contents": contents,
                   "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}}
        r = self.session.post(self.base_url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_groq(self, messages):
        payload = {"model": config.GROQ_MODEL, "max_tokens": 2000,
                   "temperature": 0.7, "messages": messages}
        r = self.session.post(self.base_url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()

    def _raw_call(self, messages):
        return self._call_gemini(messages) if self.provider == "gemini" else self._call_groq(messages)

    def chat(self, messages):
        try: return self._raw_call(messages)
        except Exception as e: return f"Erro: {e}"
