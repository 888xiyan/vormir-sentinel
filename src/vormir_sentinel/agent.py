"""Rich RedSkoll Agent page with safe plain-terminal degradation."""

from __future__ import annotations

from dataclasses import dataclass, field

from vormir_sentinel.console import Display

DEFAULT_ASCII = (
    "      .-^^^^-.\n"
    "    .`  ____  `.\n"
    "   /   / ## \\   \\\n"
    "  |   | #### |   |\n"
    "   \\   \\____/   /\n"
    "    `.  ____  .`\n"
    "      `-______-`"
)


@dataclass
class AgentPage:
    display: Display
    model: str
    mode: str
    context: str
    ollama_status: str
    story_act: str
    safe_mode: bool = False
    conversation: list[tuple[str, str]] = field(default_factory=list)
    ascii_art: str = DEFAULT_ASCII

    @property
    def full_page(self) -> bool:
        return bool(
            self.display.is_tty
            and self.display.color_enabled
            and not self.display.low_stimulation
            and not self.safe_mode
            and self.display.width >= 60
        )

    @property
    def service_label(self) -> str:
        if self.mode == "OFFLINE" or self.ollama_status in {
            "OLLAMA_NOT_RUNNING",
            "OLLAMA_NO_MODEL",
            "OFFLINE",
        }:
            return "[OFFLINE STORY]"
        return "[LOCAL OLLAMA]"

    def update_model(self, model: str, mode: str, context: str) -> None:
        self.model = model
        self.mode = mode
        self.context = context

    def enter(self) -> None:
        if not self.full_page:
            return
        self.display.clear()
        status = (
            f"REDSKOLL AGENT   model: {self.model}   mode: {self.mode}   "
            f"context: {self.context}\n"
            f"{self.service_label}   [SAFE EXIT: exit --now]   [/ for commands]\n\n"
            f"{self.ascii_art}\n\n"
            "RedSkoll\n"
            "The host is ready. Ask, and pay in attention.\n\n"
            "[fictional takeover only; no host command was executed]"
        )
        self.display.panel("RedSkoll Agent Terminal", status, style="bold red")

    def begin_turn(self, question: str) -> None:
        if self.full_page:
            self.display.print(f"\n> {question}", style="bold red")
        else:
            self.display.print(f"\n> {question}")

    def finish_turn(self, question: str, answer: str) -> None:
        self.conversation.append((question, answer))
        if len(self.conversation) > 12:
            del self.conversation[:-12]

    def clear_conversation(self) -> None:
        self.conversation.clear()
        if self.full_page:
            self.display.clear()
            self.enter()

    def render_history(self) -> None:
        if not self.full_page or not self.conversation:
            return
        for question, answer in self.conversation[-3:]:
            self.display.print(f"\n> {question}", style="bold red")
            self.display.print(answer)
