import json
import unittest
from unittest.mock import Mock
from urllib.error import URLError

from Backend.Logic.ai_service import AIModelError
from Backend.Logic.ollama_client import OllamaClient


class Response:
    def __init__(self, payload: dict):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        from io import BytesIO

        self.stream = BytesIO(self.payload)
        return self.stream

    def __exit__(self, *_args):
        self.stream.close()


class OllamaClientTests(unittest.TestCase):
    def test_checks_installed_model_and_generates_without_streaming(self):
        client = OllamaClient("http://127.0.0.1:11434", "llama3.2")
        client.opener = Mock()
        client.opener.open.side_effect = [
            Response({"models": [{"name": "llama3.2:latest"}]}),
            Response({"response": '{"text":"Summary"}'}),
        ]
        self.assertEqual(client.generate("system", "prompt"), '{"text":"Summary"}')
        calls = client.opener.open.call_args_list
        self.assertTrue(calls[0].args[0].full_url.endswith("/api/tags"))
        body = json.loads(calls[1].args[0].data)
        self.assertEqual(body["model"], "llama3.2")
        self.assertFalse(body["stream"])
        self.assertEqual(body["format"], "json")

    def test_missing_model_never_generates_or_downloads(self):
        client = OllamaClient("http://localhost:11434", "llama3.2")
        client.opener = Mock()
        client.opener.open.return_value = Response({"models": [{"name": "other:latest"}]})
        with self.assertRaises(AIModelError):
            client.generate("system", "prompt")
        self.assertEqual(client.opener.open.call_count, 1)

    def test_connection_failure_is_a_model_error(self):
        client = OllamaClient("http://127.0.0.1:11434", "llama3.2")
        client.opener = Mock()
        client.opener.open.side_effect = URLError("offline")
        with self.assertRaises(AIModelError):
            client.generate("system", "prompt")

    def test_nonlocal_base_url_is_rejected(self):
        with self.assertRaises(ValueError):
            OllamaClient("https://models.example.org", "llama3.2")


if __name__ == "__main__":
    unittest.main()
