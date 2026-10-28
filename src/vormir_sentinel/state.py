"""Versioned, atomic local story state with conservative cleanup."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_SCHEMA_VERSION = 1


class StateError(RuntimeError):
    """Raised when state persistence cannot be completed safely."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def default_state_path() -> Path:
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if root:
            return Path(root) / "VormirSentinel" / "state.json"
    if os.uname().sysname == "Darwin":
        return Path.home() / "Library" / "Application Support" / "VormirSentinel" / "state.json"
    root = os.environ.get("XDG_DATA_HOME")
    if root:
        return Path(root) / "vormir-sentinel" / "state.json"
    return Path.home() / ".local" / "share" / "vormir-sentinel" / "state.json"


@dataclass
class ProgressState:
    schema_version: int = STATE_SCHEMA_VERSION
    started_at: str = field(default_factory=utc_now)
    last_run_at: str = field(default_factory=utc_now)
    act: str = "boot"
    cleared: bool = False
    tribute_count: int = 0
    tribute_kinds: list[str] = field(default_factory=list)
    echo_count: int = 0
    last_echo_date: str = ""
    fragments_seen: list[str] = field(default_factory=list)
    relic_generated: bool = False
    resurrection_generated: bool = False
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgressState:
        if data.get("schema_version") != STATE_SCHEMA_VERSION:
            raise StateError(f"Unsupported state schema: {data.get('schema_version')!r}")
        state = cls()
        for key in (
            "started_at",
            "last_run_at",
            "act",
            "last_echo_date",
        ):
            value = data.get(key, getattr(state, key))
            if not isinstance(value, str):
                raise StateError(f"State field {key!r} must be a string.")
            setattr(state, key, value)
        for key in ("cleared",):
            value = data.get(key, getattr(state, key))
            if not isinstance(value, bool):
                raise StateError(f"State field {key!r} must be boolean.")
            setattr(state, key, value)
        for key in ("tribute_count", "echo_count"):
            value = data.get(key, getattr(state, key))
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise StateError(f"State field {key!r} must be a non-negative integer.")
            setattr(state, key, value)
        for key in ("tribute_kinds", "fragments_seen", "flags"):
            value = data.get(key, getattr(state, key))
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise StateError(f"State field {key!r} must be a string list.")
            setattr(state, key, list(value))
        return state


class StateStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path is not None else default_state_path()

    def load(self) -> ProgressState:
        if not self.path.exists():
            return ProgressState()
        try:
            raw = self.path.read_text(encoding="utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise StateError("State root must be a JSON object.")
            return ProgressState.from_dict(data)
        except (OSError, json.JSONDecodeError, StateError):
            return ProgressState()

    def save(self, state: ProgressState) -> None:
        state.last_run_at = utc_now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2) + "\n"
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.path)
        except OSError as exc:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
            raise StateError(f"Cannot save story state: {exc}") from exc

    def forget(self) -> bool:
        """Delete only this application's state file and temp artifacts."""
        removed = False
        for candidate in (self.path,):
            if candidate.exists():
                candidate.unlink()
                removed = True
        temp_pattern = f".{self.path.name}.*.tmp"
        for candidate in self.path.parent.glob(temp_pattern):
            if candidate.is_file():
                candidate.unlink()
                removed = True
        return removed

    def clean(self) -> bool:
        return self.forget()
