"""In-memory four-act story director for the M3 world layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum

from vormir_sentinel.commands import CommandOutcome
from vormir_sentinel.config import Config


class StoryAct(IntEnum):
    BOOT = 1
    METAMORPHOSIS = 2
    VORMIR_SHELL = 3
    TAKEOVER = 4
    CLEARED = 5


@dataclass
class StoryState:
    act: StoryAct = StoryAct.BOOT
    boot_completed: bool = False
    defiance_count: int = 0
    interrupt_count: int = 0
    takeover_triggered: bool = False
    flags: set[str] = field(default_factory=set)


class StoryDirector:
    """Provides narrative transitions without touching the host."""

    def __init__(self, config: Config, state: StoryState | None = None) -> None:
        self.config = config
        self.state = state or StoryState()

    @property
    def act(self) -> StoryAct:
        return self.state.act

    def begin(self) -> str:
        """Run the Trojan Installation and Metamorphosis prologue."""
        if self.state.boot_completed:
            return self._returning_text()
        self.state.boot_completed = True

        if self.config.app.safe_mode or self.config.app.low_stimulation:
            self.state.act = StoryAct.VORMIR_SHELL
            return (
                "Vormir Sentinel — local fictional terminal.\n"
                "Low-stimulation startup: the boot simulation is disabled.\n"
                "The window remains under your control."
            )

        self.state.act = StoryAct.VORMIR_SHELL
        return (
            "Vormir Sentinel bootstrap\n"
            "Fetching local agent runtime...\n"
            "Resolving dependencies...\n"
            "Validating host signature...\n"
            "Host: NT-x86_64\n"
            "Target: HYDRA-SOULKEEPER\n"
            "Warning: dependency metadata contains non-Euclidean paths\n"
            "Progress: 99% — host architecture corrupted\n"
            "NT subsystem dereferenced.\n"
            "Kernel identity replaced by Vormir keeper protocol.\n"
            "[fictional takeover only; no host command was executed]"
        )

    def observe_command(self, raw: str, outcome: CommandOutcome) -> str:
        """Advance the story for selected fictional commands."""
        command = raw.strip().split(maxsplit=1)[0].lower() if raw.strip() else ""
        if command in {"defy", "betray", "refuse"}:
            self.state.defiance_count += 1
            return self._trigger_takeover(reason="defiance")
        if command in {"dir", "cls", "powershell", "cmd"}:
            return self._trigger_takeover(reason="legacy ritual")
        return ""

    def on_interrupt(self, count: int) -> str:
        """Return the narrative response for a Ctrl+C interrupt."""
        self.state.interrupt_count = max(self.state.interrupt_count, count)
        if self.config.app.safe_mode or self.config.app.low_stimulation:
            if count == 1:
                return (
                    "Interrupted. Safe mode keeps you in control; "
                    "interrupt again or type 'exit --now' to leave."
                )
            return "Second interrupt accepted. Safe exit engaged; the process is ending."

        if count == 1:
            return (
                "^C\n"
                "Interrupt observed. No host command was issued.\n"
                "The following line is fictional and was not executed:\n"
                "  sudo /opt/hydra/vormir-daemon --bind-soul-to-pid $$\n"
                "You cannot escape the void with a keyboard interrupt."
            )
        if count == 2:
            return (
                "^C\n"
                "This process belongs to Johann Schmidt now.\n"
                "But the physical window remains yours.\n"
                "Close it, or leave with my permission.\n"
                "type: exit --now"
            )
        return (
            "^C\n"
            "The keeper is counting your interruptions. "
            "The physical window remains yours; safe exits remain available."
        )

    def _trigger_takeover(self, *, reason: str) -> str:
        self.state.takeover_triggered = True
        self.state.act = StoryAct.TAKEOVER
        return (
            "TAKEOVER PROTOCOL — fictional alarm state\n"
            f"Trigger: {reason}.\n"
            "Pentagon geometry locked. Silo doors are narrative props.\n"
            "No real alarm, file, process, or system setting was touched.\n"
            "The keeper: choose defiance, or choose the exit that remains real."
        )

    @staticmethod
    def _returning_text() -> str:
        return (
            "The installation does not need to repeat itself.\n"
            "Vormir remembers the shape of your previous return."
        )
