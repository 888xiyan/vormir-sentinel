"""Safe interactive loop for the fictional terminal."""

from __future__ import annotations

import contextlib
import shlex
from collections.abc import Callable
from typing import TextIO

from vormir_sentinel.commands import WHITELIST, CommandOutcome, CommandRouter, SessionState
from vormir_sentinel.console import Display
from vormir_sentinel.death_echoes import DeathEchoManager
from vormir_sentinel.dialogue import DialogueEngine
from vormir_sentinel.relics import GeneratedRelic, RelicError, RelicGenerator
from vormir_sentinel.state import ProgressState, StateStore
from vormir_sentinel.story import StoryAct, StoryDirector
from vormir_sentinel.tributes import TributeManager

InputFunction = Callable[[str], str]
_READLINE_COMMANDS = tuple(sorted(WHITELIST))


def _command_completer(text: str, state: int) -> str | None:
    """Complete only Vormir whitelist words, never host paths or executables."""
    matches = [command for command in _READLINE_COMMANDS if command.startswith(text.lower())]
    if state < len(matches):
        return matches[state]
    return None


class Repl:
    def __init__(
        self,
        display: Display,
        router: CommandRouter,
        *,
        input_function: InputFunction | None = None,
        stdin: TextIO | None = None,
        safe_mode: bool = False,
        dialogue: DialogueEngine | None = None,
        director: StoryDirector | None = None,
        progress: ProgressState | None = None,
        state_store: StateStore | None = None,
        tributes: TributeManager | None = None,
        echoes: DeathEchoManager | None = None,
        relics: RelicGenerator | None = None,
    ) -> None:
        self.display = display
        self.router = router
        self.input_function = input_function
        self.stdin = stdin
        self.safe_mode = safe_mode
        self.dialogue = dialogue
        self.director = director
        self.progress = progress
        self.state_store = state_store
        self.tributes = tributes
        self.echoes = echoes
        self.relics = relics
        self.state = SessionState()

    def run(self) -> int:
        self._begin_progress()
        if self.director is not None and not (self.progress and self.progress.cleared):
            prologue = self.director.begin()
            if prologue:
                self.display.print(prologue)
                self.display.print()
        self._print_banner()
        if self.input_function is None and self._can_use_readline():
            self._configure_readline()

        while True:
            prompt = self.router.prompt(self.state.cwd)
            self.display.prompt(prompt)
            try:
                line = self._read_line()
            except KeyboardInterrupt:
                if self._handle_interrupt():
                    break
                continue
            except EOFError:
                self.display.print("\nInput channel closed. Exiting safely.")
                break

            if line is None:
                self.display.print("\nInput channel closed. Exiting safely.")
                break

            stripped = line.strip()
            if not stripped:
                continue

            self.state.history.append(stripped)
            try:
                outcome = self._route_with_progress(stripped)
                if outcome.status == "unknown" and self.dialogue is not None:
                    self._stream_dialogue(stripped)
                else:
                    self._render(outcome)
                    if stripped.lower() == "settings" and self.dialogue is not None:
                        self.display.print(self.dialogue.status_line)
                if self.director is not None:
                    story_text = self.director.observe_command(stripped, outcome)
                    if story_text:
                        self.display.print(story_text, style="yellow")
            except KeyboardInterrupt:
                if self._handle_interrupt():
                    break
                continue
            if outcome.exit_requested:
                break

        self.display.print("The terminal returns to your control.")
        return 0

    def _read_line(self) -> str | None:
        if self.input_function is not None:
            return self.input_function("")
        if self.stdin is not None:
            return self.stdin.readline().removesuffix("\n") if not self.stdin.closed else None
        return input()

    def _begin_progress(self) -> None:
        if self.progress is None:
            return
        if self.progress.cleared:
            self.progress.act = "cleared"
            if self.director is not None:
                self.director.state.boot_completed = True
                self.director.state.act = StoryAct.CLEARED
        elif self.progress.act in {"", "boot"}:
            self.progress.act = "vormir_shell"
        elif self.director is not None:
            self.director.state.boot_completed = True
            if self.progress.act == "vormir_shell":
                self.director.state.act = StoryAct.VORMIR_SHELL
        if self.state_store is not None:
            self.state_store.save(self.progress)
        if self.echoes is not None and self.progress.cleared:
            echo_text = self.echoes.start_echo(self.progress)
            if echo_text:
                self.display.print(echo_text, style="magenta")
                self.display.print()
            if self.state_store is not None:
                self.state_store.save(self.progress)

    def _route_with_progress(self, stripped: str) -> CommandOutcome:
        if self.progress is not None and self.tributes is not None:
            try:
                parts = shlex.split(stripped, posix=True)
            except ValueError:
                return self.router.route(stripped, self.state)
            is_tribute = bool(parts) and parts[0].lower() == "tribute"
            is_secret = parts[:2] == ["secret", "--fictional"]
            if is_tribute or is_secret:
                tribute_args = parts[1:] if is_tribute else parts
                result = self.tributes.record(tribute_args, self.progress)
                self.display.print(result.text, style="yellow" if result.kind else None)
                if result.completed:
                    self._complete_story()
                elif self.state_store is not None:
                    self.state_store.save(self.progress)
                return CommandOutcome()

        if self.progress is not None and self.echoes is not None:
            try:
                parts = shlex.split(stripped, posix=True)
            except ValueError:
                parts = []
            if parts[:2] == ["show", "fragments"]:
                self.display.print(self.echoes.reconstruct(self.progress), style="magenta")
                return CommandOutcome()
            if parts[:2] == ["show", "relic"]:
                if self.progress.relic_generated:
                    self.display.print("The relics are waiting in the approved output directory.")
                else:
                    self.display.print("No relic has been generated yet.")
                return CommandOutcome()

        return self.router.route(stripped, self.state)

    def _complete_story(self) -> None:
        if self.progress is None:
            return
        self.progress.act = "cleared"
        if self.director is not None:
            self.director.state.act = StoryAct.CLEARED
        if self.relics is not None:
            try:
                generated: tuple[GeneratedRelic, ...] = self.relics.generate(self.progress)
                names = "\n".join(f"- {item.path}" for item in generated)
                self.display.print(
                    "The main story is cleared. Harmless relics were generated:\n" + names,
                    style="green",
                )
            except RelicError as exc:
                self.display.print(f"Relic generation failed safely: {exc}", style="red")
        if self.state_store is not None:
            self.state_store.save(self.progress)

    def _stream_dialogue(self, question: str) -> None:
        assert self.dialogue is not None
        for fragment in self.dialogue.stream(question):
            self.display.write_fragment(fragment)
        self.display.print()

    def _render(self, outcome: CommandOutcome) -> None:
        if outcome.clear_screen:
            self.display.clear()
        if outcome.text:
            style = "red" if outcome.status == "error" else None
            self.display.print(outcome.text, style=style)

    def _handle_interrupt(self) -> bool:
        self.state.interrupt_count += 1
        if self.director is not None:
            narrative = self.director.on_interrupt(self.state.interrupt_count)
            self.display.print(narrative, style="yellow")
        elif self.state.interrupt_count == 1:
            self.display.print(
                "\nInterrupt observed. No host command was issued.\n"
                "Type 'exit --now' or interrupt again to force a safe exit.",
                style="yellow",
            )
        else:
            self.display.print(
                "\nSecond interrupt accepted. Safe exit engaged; the process is ending.",
                style="yellow",
            )
        return self.state.interrupt_count >= 2

    def _print_banner(self) -> None:
        mode = (
            "SAFE MODE — no animation, network, or host commands."
            if self.safe_mode
            else ("FICTIONAL INTERFACE — the real host is not being controlled.")
        )
        self.display.print("Vormir Sentinel / local character core", style="bold red")
        self.display.print(mode, style="cyan")
        if self.dialogue is not None:
            self.display.print(self.dialogue.status_line, style="cyan")
        self.display.print(
            "Type help for the virtual command map. Safe exits: "
            "exit --now, Ctrl+C twice, or close this window."
        )
        self.display.print()

    def _can_use_readline(self) -> bool:
        if self.stdin is None:
            return True
        return not self.stdin.closed and self.stdin.isatty()

    @staticmethod
    def _configure_readline() -> None:
        try:
            import readline
        except ImportError:
            try:
                import pyreadline3.rlmain as readline  # type: ignore[import-not-found,no-redef]
            except ImportError:
                return

        readline.set_completer(_command_completer)
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")
        with contextlib.suppress(AttributeError, OSError):
            readline.set_history_length(1000)
