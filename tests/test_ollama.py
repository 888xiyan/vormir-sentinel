from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from vormir_sentinel.ollama import (
    OllamaClient,
    OllamaProtocolError,
    UnsafeEndpointError,
    validate_endpoint,
)


class _FakeOllamaHandler(BaseHTTPRequestHandler):
    received: dict[str, object] = {}

    def do_GET(self) -> None:  # noqa: N802 - HTTP handler API
        if self.path == "/api/redirect":
            self.send_response(302)
            self.send_header("Location", "http://example.invalid/api/tags")
            self.end_headers()
            return
        if self.path != "/api/tags":
            self.send_error(404)
            return
        body = json.dumps(
            {
                "models": [
                    {
                        "name": "qwen2.5:7b-instruct-q4_K_M",
                        "model": "qwen2.5:7b-instruct-q4_K_M",
                        "size": 5_000_000_000,
                        "modified_at": "2026-10-29T00:00:00Z",
                        "details": {"family": "qwen2", "quantization_level": "Q4_K_M"},
                    },
                    {"name": "qwen2.5:3b-instruct-q4_K_M"},
                ]
            }
        ).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - HTTP handler API
        length = int(self.headers.get("Content-Length", "0"))
        _FakeOllamaHandler.received = json.loads(self.rfile.read(length))
        events = [
            {"message": {"role": "assistant", "content": "Knowledge "}, "done": False},
            {"message": {"role": "assistant", "content": "is weighed."}, "done": True},
        ]
        body = "".join(f"{json.dumps(event)}\n" for event in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *args: object) -> None:
        return


class OllamaClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _FakeOllamaHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.client = OllamaClient(f"http://{host}:{port}", health_timeout=1.0)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_remote_endpoints_are_rejected(self) -> None:
        with self.assertRaises(UnsafeEndpointError):
            validate_endpoint("https://example.com:11434")
        with self.assertRaises(UnsafeEndpointError):
            validate_endpoint("http://192.168.1.10:11434")

    def test_redirects_cannot_reroute_loopback_requests_off_host(self) -> None:
        host, port = self.server.server_address
        client = OllamaClient(f"http://{host}:{port}", health_timeout=1.0)

        with self.assertRaises(OllamaProtocolError):
            client._request("GET", "/api/redirect", timeout=1.0)

    def test_list_models_reads_loopback_tags(self) -> None:
        self.assertTrue(self.client.is_available())
        models = self.client.list_models()

        self.assertIn("qwen2.5:7b-instruct-q4_K_M", models)
        self.assertIn("qwen2.5:3b-instruct-q4_K_M", models)

    def test_model_metadata_includes_read_only_details(self) -> None:
        models = self.client.list_model_metadata()
        gpu = next(model for model in models if model.name == "qwen2.5:7b-instruct-q4_K_M")

        self.assertEqual(gpu.size_bytes, 5_000_000_000)
        self.assertEqual(gpu.family, "qwen2")
        self.assertEqual(gpu.quantization, "Q4_K_M")
        self.assertEqual(gpu.modified_at, "2026-10-29T00:00:00Z")

    def test_chat_stream_yields_ndjson_fragments(self) -> None:
        messages = [{"role": "user", "content": "Who are you?"}]
        chunks = list(
            self.client.chat_stream(
                "qwen2.5:7b-instruct-q4_K_M",
                messages,
                {"temperature": 0.85, "num_ctx": 8192},
            )
        )

        self.assertEqual("".join(chunks), "Knowledge is weighed.")
        self.assertTrue(_FakeOllamaHandler.received["stream"])
        options = _FakeOllamaHandler.received["options"]
        self.assertEqual(options, {"temperature": 0.85, "num_ctx": 8192})


if __name__ == "__main__":
    unittest.main()
