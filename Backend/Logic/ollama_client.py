"""Small local Ollama HTTP client; it never installs or downloads a model."""

import json
from urllib import error, request
from urllib.parse import urlparse

from Backend.Logic.ai_service import AIModelError


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 90):
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
            raise ValueError("Ollama base URL must use local HTTP")
        if not model.strip():
            raise ValueError("Ollama model name must not be empty")
        self.base_url = base_url.rstrip("/")
        self.model = model.strip()
        self.timeout_seconds = timeout_seconds
        self.opener = request.build_opener(request.ProxyHandler({}))

    def _json_request(self, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if data is not None else "GET",
        )
        try:
            with self.opener.open(req, timeout=self.timeout_seconds) as response:
                result = json.load(response)
        except (error.URLError, TimeoutError, OSError, ValueError) as exc:
            # Do not include request bodies, model output, or article text in errors.
            raise AIModelError("Ollama is unavailable or returned an invalid response") from exc
        if not isinstance(result, dict):
            raise AIModelError("Ollama returned an invalid response")
        return result

    def generate(self, system: str, prompt: str) -> str:
        models = self._json_request("/api/tags").get("models")
        installed = {
            item.get("name") for item in models if isinstance(item, dict)
        } if isinstance(models, list) else set()
        if self.model not in installed and f"{self.model}:latest" not in installed:
            raise AIModelError("Configured Ollama model is not installed")
        result = self._json_request(
            "/api/generate",
            {
                "model": self.model,
                "system": system,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0},
            },
        )
        text = result.get("response")
        if not isinstance(text, str):
            raise AIModelError("Ollama returned no generated text")
        return text
