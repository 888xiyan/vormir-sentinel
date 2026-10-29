"""Minimal, local-only Ollama HTTP client with streaming chat support."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


@dataclass(frozen=True)
class InstalledModel:
    """Read-only metadata returned by the local Ollama service."""

    name: str
    size_bytes: int | None = None
    modified_at: str | None = None
    family: str | None = None
    quantization: str | None = None


class OllamaError(RuntimeError):
    """Base class for safe Ollama communication failures."""


class UnsafeEndpointError(OllamaError):
    """Raised when a configured Ollama endpoint is not loopback-only."""


class OllamaConnectionError(OllamaError):
    """Raised when the local Ollama service cannot be reached."""


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


class OllamaProtocolError(OllamaError):
    """Raised when Ollama returns malformed or unsuccessful data."""


def validate_endpoint(base_url: str) -> str:
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeEndpointError("Ollama endpoint must be an explicit HTTP(S) URL.")
    if parsed.hostname not in LOOPBACK_HOSTS:
        raise UnsafeEndpointError(
            "Remote inference is forbidden. Use a loopback Ollama endpoint such as "
            "http://127.0.0.1:11434."
        )
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise UnsafeEndpointError(
            "Ollama endpoint must not contain a URL path, query, or fragment."
        )
    return base_url.rstrip("/")


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 120.0,
        health_timeout: float = 1.5,
    ) -> None:
        self.base_url = validate_endpoint(base_url)
        self.timeout = timeout
        self.health_timeout = health_timeout
        # Disable proxies and redirects so loopback traffic cannot be rerouted off-host.
        self._opener = build_opener(ProxyHandler({}), _RejectRedirects())

    def is_available(self) -> bool:
        try:
            self._request("GET", "/api/tags", timeout=self.health_timeout)
        except OllamaError:
            return False
        return True

    def list_model_metadata(self) -> tuple[InstalledModel, ...]:
        """Fetch installed model metadata without starting or downloading anything."""
        payload = self._request("GET", "/api/tags", timeout=self.health_timeout)
        models = payload.get("models")
        if not isinstance(models, list):
            raise OllamaProtocolError("Ollama /api/tags did not return a model list.")

        installed: list[InstalledModel] = []
        seen: set[str] = set()
        for item in models:
            if not isinstance(item, dict):
                continue
            name = item.get("model") or item.get("name")
            if not isinstance(name, str) or not name or name in seen:
                continue
            seen.add(name)
            size = item.get("size")
            details = item.get("details")
            details_dict = details if isinstance(details, dict) else {}
            family = details_dict.get("family")
            quantization = details_dict.get("quantization_level")
            modified_at = item.get("modified_at")
            installed.append(
                InstalledModel(
                    name=name,
                    size_bytes=(
                        size if isinstance(size, int) and not isinstance(size, bool) else None
                    ),
                    modified_at=modified_at if isinstance(modified_at, str) else None,
                    family=family if isinstance(family, str) else None,
                    quantization=quantization if isinstance(quantization, str) else None,
                )
            )
        return tuple(sorted(installed, key=lambda model: model.name))

    def list_models(self) -> set[str]:
        return {model.name for model in self.list_model_metadata()}

    def chat_stream(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        options: Mapping[str, int | float],
    ) -> Iterator[str]:
        payload = {
            "model": model,
            "messages": [dict(message) for message in messages],
            "stream": True,
            "options": dict(options),
        }
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            response = self._opener.open(request, timeout=self.timeout)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            raise OllamaConnectionError(f"Ollama request failed: {exc}") from exc

        with response:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise OllamaProtocolError(
                        f"Ollama returned malformed stream data: {exc}"
                    ) from exc
                if not isinstance(event, dict):
                    raise OllamaProtocolError("Ollama stream event was not an object.")

                error = event.get("error")
                if error:
                    raise OllamaProtocolError(str(error))

                message = event.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    if isinstance(content, str) and content:
                        yield content
                if event.get("done") is True:
                    break

    def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, Any] | None = None,
        timeout: float,
    ) -> dict[str, Any]:
        data = json.dumps(dict(payload)).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with self._opener.open(request, timeout=timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OllamaProtocolError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise OllamaConnectionError(f"Ollama request failed: {exc}") from exc

        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaProtocolError(f"Ollama returned invalid JSON: {exc}") from exc
        if not isinstance(result, dict):
            raise OllamaProtocolError("Ollama response was not a JSON object.")
        return result
