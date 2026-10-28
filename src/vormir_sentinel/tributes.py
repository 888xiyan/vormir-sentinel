"""Symbolic, reversible tribute mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass

from vormir_sentinel.state import ProgressState

TRIBUTE_KINDS = ("time", "name", "secret", "release", "file")
_SAFE_NAME = re.compile(r"^[\w \-\u3400-\u9fff]{1,80}$", re.UNICODE)


@dataclass(frozen=True)
class TributeResult:
    text: str
    completed: bool = False
    kind: str = ""


class TributeManager:
    """Records only fictional acts; it never asks for or deletes real data."""

    def record(self, args: list[str], state: ProgressState) -> TributeResult:
        if not args:
            return TributeResult(
                "The altar accepts five symbolic acts:\n"
                "  tribute time\n"
                "  tribute name <fictional-name>\n"
                "  tribute secret --fictional\n"
                "  tribute release\n"
                "  tribute file\n"
                "No password, token, private message, or real file is requested."
            )

        kind = args[0].lower()
        if kind == "secret":
            if args[1:] not in ([], ["--fictional"]):
                return TributeResult("Only 'tribute secret --fictional' is accepted.", kind=kind)
            kind = "secret"
        elif kind == "name":
            if len(args) < 2 or not _SAFE_NAME.fullmatch(" ".join(args[1:])):
                return TributeResult(
                    "Name a fictional identity of at most 80 ordinary characters.",
                    kind=kind,
                )
        elif kind not in {"time", "release", "file"}:
            return TributeResult(
                f"Unknown symbolic tribute: {kind}. Type 'tribute' for the altar map.",
                kind=kind,
            )
        elif len(args) > 1:
            return TributeResult(f"'tribute {kind}' takes no additional values.", kind=kind)

        if kind in state.tribute_kinds:
            return TributeResult(
                f"The altar already remembers your {kind} tribute. Nothing is counted twice.",
                kind=kind,
            )

        state.tribute_kinds.append(kind)
        state.tribute_count = len(state.tribute_kinds)
        descriptions = {
            "time": "A few seconds of attention; time returned to you immediately.",
            "name": "A fictional name; no identity or credential was requested.",
            "secret": "An invented shadow; no real secret was requested.",
            "release": "A wish released; no possession or account was surrendered.",
            "file": "The virtual /tmp/regret.tmp vanished; no host file was touched.",
        }
        completed = len(state.tribute_kinds) >= len(TRIBUTE_KINDS)
        if completed:
            state.cleared = True
            state.flags.append("cleared")
            return TributeResult(
                descriptions[kind]
                + "\nAll five symbolic tributes are recorded. The main story is cleared.",
                completed=True,
                kind=kind,
            )
        remaining = len(TRIBUTE_KINDS) - len(state.tribute_kinds)
        return TributeResult(
            descriptions[kind] + f"\nThe altar waits for {remaining} more symbolic act(s).",
            kind=kind,
        )
