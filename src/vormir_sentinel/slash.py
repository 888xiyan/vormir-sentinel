"""Fixed-script Slash command registry for the RedSkoll Agent page."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vormir_sentinel.startup import download_command, sanitize_model_name

SCRIPTS_ROOT = Path(__file__).resolve().parent / "scripts"


@dataclass(frozen=True)
class SlashCommand:
    name: str
    kind: str
    text: str
    description: str = ""
    state_updates: tuple[str, ...] = ()


@dataclass
class SlashContext:
    model: str
    mode: str
    context: str
    ollama_status: str
    story_act: str
    output_root: str
    installed_models: tuple[str, ...] = ()
    conversation_count: int = 0
    safe_mode: bool = False
    relic_text: str = "No relic has been generated yet."
    reconstruct_text: str = "No Death Echo fragments have been recorded yet."
    tribute_text: str = (
        "Symbolic tributes: time, fictional name, invented secret, release, virtual file."
    )


@dataclass(frozen=True)
class SlashOutcome:
    text: str = ""
    clear_conversation: bool = False
    exit_requested: bool = False
    offline_requested: bool = False
    safe_mode_requested: bool = False
    model_override: str | None = None
    status: str = "ok"


@dataclass
class SlashCommandRegistry:
    commands: dict[str, SlashCommand] = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path | None = None) -> SlashCommandRegistry:
        selected = root or SCRIPTS_ROOT
        path = selected / "slash_commands.json"
        if not path.exists():
            raise FileNotFoundError(f"Slash command script not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read slash command script: {exc}") from exc
        raw_commands = data.get("commands") if isinstance(data, dict) else None
        if not isinstance(raw_commands, dict):
            raise ValueError("Slash command script requires a commands object.")

        commands: dict[str, SlashCommand] = {}
        for name, raw in raw_commands.items():
            if not isinstance(name, str) or not isinstance(raw, dict):
                continue
            text = raw.get("text")
            kind = raw.get("kind", "fixed")
            description = raw.get("description", "")
            updates = raw.get("state_updates", [])
            if not isinstance(text, str) or not isinstance(kind, str):
                continue
            if not isinstance(description, str):
                description = ""
            if not isinstance(updates, list) or not all(isinstance(item, str) for item in updates):
                updates = []
            commands[name] = SlashCommand(
                name=name,
                kind=kind,
                text=text,
                description=description,
                state_updates=tuple(updates),
            )
        return cls(commands=commands)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self.commands))

    def complete(self, prefix: str) -> tuple[str, ...]:
        return tuple(name for name in self.names() if name.startswith(prefix))

    def render(self, raw: str, context: SlashContext) -> SlashOutcome:
        try:
            parts = shlex.split(raw, posix=True)
        except ValueError as exc:
            return SlashOutcome(text=f"Malformed slash command: {exc}", status="error")
        if not parts or not parts[0].startswith("/"):
            return SlashOutcome(text="Slash commands must start with /.", status="error")

        command = parts[0].lower()
        args = parts[1:]

        if command == "/model":
            return self._model(args, context)
        if command == "/download":
            return self._download(args)
        if command not in self.commands:
            return SlashOutcome(
                text=f"Unknown slash command: {command}\nType /help for the fixed command map.",
                status="error",
            )

        definition = self.commands[command]
        text = self._fill(definition.text, context)
        updates = set(definition.state_updates)
        return SlashOutcome(
            text=text,
            clear_conversation="clear_conversation" in updates,
            exit_requested="exit" in updates,
            offline_requested="offline" in updates,
            safe_mode_requested="safe" in updates,
        )

    @staticmethod
    def _fill(template: str, context: SlashContext) -> str:
        values: dict[str, str] = {
            "model": context.model,
            "mode": context.mode,
            "context": context.context,
            "ollama_status": context.ollama_status,
            "story_act": context.story_act,
            "output_root": context.output_root,
            "conversation_count": str(context.conversation_count),
            "relic_text": context.relic_text,
            "reconstruct_text": context.reconstruct_text,
            "tribute_text": context.tribute_text,
        }
        result = template
        for key, value in values.items():
            result = result.replace("{" + key + "}", value)
        return result

    @staticmethod
    def _model(args: list[str], context: SlashContext) -> SlashOutcome:
        if not args:
            return SlashOutcome(
                text=(
                    f"model: {context.model}\n"
                    f"mode: {context.mode}\n"
                    f"context: {context.context}\n"
                    f"ollama: {context.ollama_status}"
                )
            )
        if args == ["list"]:
            if not context.installed_models:
                return SlashOutcome(text="No local Ollama models are available.")
            return SlashOutcome(
                text="Installed models:\n"
                + "\n".join(f"- {name}" for name in context.installed_models)
            )
        if len(args) >= 2 and args[0] == "select":
            try:
                model = sanitize_model_name(" ".join(args[1:]))
            except ValueError as exc:
                return SlashOutcome(text=str(exc), status="error")
            if model not in context.installed_models:
                return SlashOutcome(
                    text=(
                        f"Model is not installed: {model}\nUse /model list to inspect local models."
                    ),
                    status="error",
                )
            return SlashOutcome(
                text=f"Selected installed model: {model}",
                model_override=model,
            )
        return SlashOutcome(
            text="Usage: /model, /model list, or /model select NAME",
            status="error",
        )

    @staticmethod
    def _download(args: list[str]) -> SlashOutcome:
        if len(args) != 1:
            return SlashOutcome(text="Usage: /download MODEL", status="error")
        try:
            command = download_command(args[0])
        except ValueError as exc:
            return SlashOutcome(text=str(exc), status="error")
        return SlashOutcome(
            text=(
                "Run this command yourself:\n\n"
                f"  {command}\n\n"
                "Vormir Sentinel did not download or execute anything."
            )
        )


def load_agent_script(root: Path | None = None) -> dict[str, Any]:
    selected = root or SCRIPTS_ROOT
    path = selected / "redskoll_agent.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("RedSkoll agent script must be an object.")
    return data
