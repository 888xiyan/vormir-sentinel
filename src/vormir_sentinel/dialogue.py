"""Offline and streaming character dialogue engines."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Protocol

from vormir_sentinel.character import build_messages, postprocess_response
from vormir_sentinel.model_policy import ModelProfile
from vormir_sentinel.ollama import OllamaClient, OllamaError


class DialogueEngine(Protocol):
    @property
    def status_line(self) -> str: ...

    def stream(self, question: str) -> Iterator[str]: ...


class _StreamingCleaner:
    """Removes model scaffolding while preserving streaming whitespace."""

    def __init__(self) -> None:
        self._raw_parts: list[str] = []
        self._released = 0

    def feed(self, fragment: str) -> str:
        self._raw_parts.append(fragment)
        raw = "".join(self._raw_parts)
        stripped = raw.strip()
        if "\n" not in stripped and len(stripped) < 512:
            return ""
        cleaned = postprocess_response(raw)
        delta = cleaned[self._released :]
        self._released = len(cleaned)
        return delta

    def flush(self) -> str:
        raw = "".join(self._raw_parts)
        cleaned = postprocess_response(raw)
        delta = cleaned[self._released :]
        self._released = len(cleaned)
        return delta


@dataclass(frozen=True)
class _OfflineReply:
    markers: tuple[str, ...]
    text: str


_OFFLINE_REPLIES = (
    _OfflineReply(
        ("code", "python", "javascript", "函数", "代码"),
        "The local model vessel is absent, so I will not invent code I cannot verify.\n"
        "Start Ollama and use GPU or CPU mode for useful answers. Here, I remain a keeper, "
        "not a compiler.",
    ),
    _OfflineReply(
        ("who", "johann", "stonekeeper", "red skull", "红骷髅", "你是谁"),
        "I am the Stonekeeper of this fictional Vormir terminal. "
        "I hold knowledge; you brought the willingness to pay for it.",
    ),
    _OfflineReply(
        ("exit", "quit", "leave", "退出", "离开"),
        "Type 'exit --now'. Close the window if the words are already too heavy. "
        "Both paths are real.",
    ),
)

_OFFLINE_DEFAULT = (
    "Ollama is absent, and the offline story has no voice beyond fixed fragments.\n"
    "No request left this machine. Enable a local GPU/CPU model when you want an answer "
    "instead of a legend."
)


class OfflineDialogueEngine:
    """Fixed, deterministic character behavior with no network access."""

    def __init__(self, *, reason: str = "offline mode requested") -> None:
        self.reason = reason
        self._history: list[dict[str, str]] = []

    @property
    def status_line(self) -> str:
        return f"Dialogue source: OFFLINE STORY ({self.reason})"

    def stream(self, question: str) -> Iterator[str]:
        lowered = question.lower()
        text = next(
            (
                reply.text
                for reply in _OFFLINE_REPLIES
                if any(marker in lowered for marker in reply.markers)
            ),
            _OFFLINE_DEFAULT,
        )
        self._remember(question, text)
        yield text

    def _remember(self, question: str, answer: str) -> None:
        self._history.extend(
            (
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            )
        )
        del self._history[:-24]


class StreamingDialogueEngine:
    """Streams a local Ollama answer and degrades GPU -> CPU -> offline."""

    def __init__(
        self,
        client: OllamaClient,
        profiles: Sequence[ModelProfile],
        *,
        fallback_reason: str | None = None,
    ) -> None:
        if not profiles:
            raise ValueError("At least one model profile is required.")
        self.client = client
        self.profiles = tuple(profiles)
        self.active_index = 0
        self.fallback_reason = fallback_reason
        self._history: list[dict[str, str]] = []

    @property
    def active_profile(self) -> ModelProfile:
        return self.profiles[self.active_index]

    def select_model(self, model: str) -> bool:
        """Switch in memory to another profile already supplied for this session."""
        for index, profile in enumerate(self.profiles):
            if profile.model == model:
                self.active_index = index
                self.fallback_reason = None
                return True
        return False

    @property
    def status_line(self) -> str:
        profile = self.active_profile
        source = f"{profile.display_name} via {profile.provider.upper()} [{profile.name.upper()}]"
        if self.fallback_reason:
            return f"Dialogue source: {source} ({self.fallback_reason})"
        return f"Dialogue source: {source}"

    def stream(self, question: str) -> Iterator[str]:
        while self.active_index < len(self.profiles):
            profile = self.active_profile
            if profile.is_offline:
                offline = OfflineDialogueEngine(reason="local model unavailable")
                yield from offline.stream(question)
                return

            messages = build_messages(question, self._history)
            emitted: list[str] = []
            cleaner = _StreamingCleaner()
            try:
                for fragment in self.client.chat_stream(
                    profile.model,
                    messages,
                    profile.request_options(),
                ):
                    emitted.append(fragment)
                    cleaned = cleaner.feed(fragment)
                    if cleaned:
                        yield cleaned
                remainder = cleaner.flush()
                if remainder:
                    yield remainder
            except OllamaError as exc:
                if emitted:
                    self._remember(question, "".join(emitted))
                    self.fallback_reason = "connection interrupted"
                    buffered = cleaner.flush()
                    if buffered:
                        yield buffered
                    yield (
                        "\n\nThe local vessel faltered. "
                        "Your real terminal remains untouched; interrupt again if you "
                        "wish to leave."
                    )
                    return
                if self.active_index + 1 >= len(self.profiles):
                    self.fallback_reason = "local model unavailable"
                    offline = OfflineDialogueEngine(reason=str(exc))
                    yield from offline.stream(question)
                    return
                self.active_index += 1
                self.fallback_reason = f"fell back after: {exc}"
                continue
            else:
                answer = postprocess_response("".join(emitted))
                if not answer:
                    answer = "The vessel returned silence. Even silence is an answer at Vormir."
                self._remember(question, answer)
                return

        offline = OfflineDialogueEngine(reason="all model profiles exhausted")
        yield from offline.stream(question)

    def _remember(self, question: str, answer: str) -> None:
        self._history.extend(
            (
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            )
        )
        del self._history[:-24]
