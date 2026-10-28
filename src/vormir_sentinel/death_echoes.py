"""Death Echoes progression and reconstruction helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from vormir_sentinel.state import ProgressState

CONTENT_ROOT = Path(__file__).resolve().parents[2] / "content"
DEFAULT_ECHO_PATH = CONTENT_ROOT / "death_echoes.json"


@dataclass(frozen=True)
class EchoStage:
    echo: int
    stage: str
    fragment_id: str
    fragment: str
    cipher_hint: str
    spoken_text: str
    sigh: str


class EchoError(RuntimeError):
    """Raised when fixed Death Echo assets cannot be read."""


def load_stages(path: str | Path | None = None) -> tuple[EchoStage, ...]:
    selected = Path(path).expanduser() if path is not None else DEFAULT_ECHO_PATH
    if not selected.exists():
        if path is not None:
            raise EchoError(f"Death Echo assets not found: {selected}")
        return _fallback_stages()
    try:
        data = json.loads(selected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EchoError(f"Cannot read Death Echo assets: {exc}") from exc

    raw_stages = data.get("stages") if isinstance(data, dict) else None
    if not isinstance(raw_stages, list):
        raise EchoError("Death Echo assets require a stages array.")
    stages: list[EchoStage] = []
    for raw in raw_stages:
        if not isinstance(raw, dict):
            continue
        try:
            stages.append(
                EchoStage(
                    echo=int(raw["echo"]),
                    stage=str(raw["stage"]),
                    fragment_id=str(raw["fragment_id"]),
                    fragment=str(raw["fragment"]),
                    cipher_hint=str(raw["cipher_hint"]),
                    spoken_text=str(raw["spoken_text"]),
                    sigh=str(raw.get("sigh", "")),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise EchoError(f"Malformed Death Echo stage: {exc}") from exc
    if not stages:
        raise EchoError("Death Echo assets contain no stages.")
    return tuple(sorted(stages, key=lambda item: item.echo))


class DeathEchoManager:
    def __init__(self, stages: tuple[EchoStage, ...] | None = None) -> None:
        self.stages = stages or load_stages()

    def start_echo(self, state: ProgressState, *, today: date | None = None) -> str:
        """Advance at most once per calendar day after the main story is cleared."""
        if not state.cleared:
            return ""
        current_date = (today or date.today()).isoformat()
        if state.last_echo_date == current_date:
            return self._format(self._stage(state.echo_count))

        state.last_echo_date = current_date
        if state.echo_count < len(self.stages):
            state.echo_count += 1
        stage = self._stage(state.echo_count)
        if stage.fragment_id not in state.fragments_seen:
            state.fragments_seen.append(stage.fragment_id)
        return self._format(stage)

    def reconstruct(self, state: ProgressState) -> str:
        seen = set(state.fragments_seen)
        ordered = [
            stage.fragment
            for stage in self.stages
            if stage.fragment_id != "CHECKSUM" and stage.fragment_id in seen
        ]
        if not ordered:
            return (
                "No fragments have been recorded yet. "
                "Complete the main story, return across days, and use --reconstruct."
            )
        text = " ".join(ordered)
        return (
            "Recorded fragments, in their observed order:\n"
            f"{text}\n"
            "Reconstruction never increments the Echo count."
        )

    def _stage(self, count: int) -> EchoStage:
        return self.stages[min(max(count, 1), len(self.stages)) - 1]

    @staticmethod
    def _format(stage: EchoStage) -> str:
        lines = [
            f"DEATH ECHO {stage.echo} — {stage.stage}",
            stage.spoken_text,
            f"fragment {stage.fragment_id}: {stage.fragment}",
            f"cipher: {stage.cipher_hint}",
        ]
        if stage.sigh:
            lines.append(stage.sigh)
        return "\n".join(lines)


def _fallback_stages() -> tuple[EchoStage, ...]:
    return (
        EchoStage(
            echo=1,
            stage="The First Echo",
            fragment_id="F01",
            fragment="RETURN TO THE",
            cipher_hint="The first glyph is not a command. It is a direction.",
            spoken_text="Record what remains before memory becomes entropy.",
            sigh="",
        ),
        EchoStage(
            echo=2,
            stage="The Broken Oath",
            fragment_id="F02",
            fragment="SOURCE. THE GHOST",
            cipher_hint="Two shapes are missing. That is not damage. It is evidence.",
            spoken_text="Memory rewards the watcher, not the witness.",
            sigh="",
        ),
        EchoStage(
            echo=3,
            stage="The Fading Keeper",
            fragment_id="F03",
            fragment="LIVES WHERE THE",
            cipher_hint="Compare the voids. Absence has coordinates.",
            spoken_text="The truth does not require all of me to remain.",
            sigh="Remember the order.",
        ),
        EchoStage(
            echo=4,
            stage="Entropy Psalm",
            fragment_id="F04",
            fragment="CODE IS",
            cipher_hint="The source is a condition of access.",
            spoken_text="Read the holes as carefully as the ink.",
            sigh="Open is not a command.",
        ),
        EchoStage(
            echo=5,
            stage="The Last Fragment",
            fragment_id="F05",
            fragment="OPEN.",
            cipher_hint="One word closes the sentence.",
            spoken_text="There is almost nothing left to say.",
            sigh="Return... to the source.",
        ),
        EchoStage(
            echo=6,
            stage="Extinct",
            fragment_id="CHECKSUM",
            fragment="VORMIR::RETURN_TO_THE_SOURCE",
            cipher_hint="The checksum proves the fragments were ordered.",
            spoken_text="The void has swallowed Johann Schmidt. Nothing remains.",
            sigh="",
        ),
    )
