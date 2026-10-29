"""Safe interactive loop for the fictional terminal and RedSkoll Agent page."""

from __future__ import annotations

import contextlib
import shlex
from collections.abc import Callable
from dataclasses import replace
from typing import TextIO

from vormir_sentinel.agent import AgentPage
from vormir_sentinel.commands import WHITELIST, CommandOutcome, CommandRouter, SessionState
from vormir_sentinel.console import Display
from vormir_sentinel.death_echoes import DeathEchoManager
from vormir_sentinel.dialogue import DialogueEngine, OfflineDialogueEngine
from vormir_sentinel.relics import GeneratedRelic, RelicError, RelicGenerator
from vormir_sentinel.slash import SlashCommandRegistry, SlashContext, SlashOutcome
from vormir_sentinel.startup import StartupDiscovery, StartupSelection
from vormir_sentinel.state import ProgressState, StateStore
from vormir_sentinel.story import StoryDirector
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
        startup: StartupDiscovery | None = None,
        selection: StartupSelection | None = None,
        slash_registry: SlashCommandRegistry | None = None,
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
        self.startup = startup
        self.selection = selection
        self.slash_registry = slash_registry or SlashCommandRegistry.load()
        self.state = SessionState()
        self.agent_page = self._make_agent_page()

    def _make_agent_page(self) -> AgentPage | None:
        if self.selection is None:
            return None
        return AgentPage(
            display=self.display,
            model=self.selection.model_name,
            mode=self.selection.mode_label,
            context=self.selection.context_label,
            ollama_status=self.selection.status,
            story_act=self.director.act.name if self.director else "BOOT",
            safe_mode=self.safe_mode,
        )

    def run(self) -> int:
        self._begin_progress()
        if self.director is not None and not (self.progress and self.progress.cleared):
            callback = self.display.run_progress if self._can_animate_install() else None
            prologue = self.director.begin(callback)
            if prologue:
                self.display.print(prologue)
                self.display.print()
            if self.progress is not None:
                self.progress.act = self.director.act.name.lower()
                if self.state_store is not None:
                    self.state_store.save(self.progress)
            if self.agent_page is not None:
                self.agent_page.story_act = self.director.act.name
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
            if stripped.startswith("/"):
                slash_outcome = self._route_slash(stripped)
                if slash_outcome.exit_requested:
                    break
                continue

            try:
                outcome = self._route_with_progress(stripped)
                if outcome.status == "unknown" and self.dialogue is not None:
                    if self.agent_page is not None:
                        self.agent_page.begin_turn(stripped)
                    answer = self._stream_dialogue(stripped)
                    if self.agent_page is not None:
                        self.agent_page.finish_turn(stripped, answer)
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
            if self.stdin.closed:
                return None
            line = self.stdin.readline()
            if line == "":
                return None
            return line.removesuffix("\n")
        return input()

    def _begin_progress(self) -> None:
        if self.progress is None:
            return
        if self.progress.cleared:
            self.progress.act = "cleared"
            if self.director is not None:
                self.director.state.boot_completed = True
                from vormir_sentinel.story import StoryAct

                self.director.state.act = StoryAct.CLEARED
        elif self.progress.act in {"", "boot"}:
            self.progress.act = "model_selection"
        elif self.director is not None:
            self.director.state.boot_completed = True
            if self.progress.act in {"vormir_shell", "agent_page"}:
                from vormir_sentinel.story import StoryAct

                self.director.state.act = StoryAct.AGENT_PAGE
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

    def _route_slash(self, stripped: str) -> SlashOutcome:
        context = self._slash_context()
        outcome = self.slash_registry.render(stripped, context)
        if outcome.text:
            self.display.print(outcome.text, style="yellow" if outcome.status == "error" else None)

        if outcome.clear_conversation and self.agent_page is not None:
            self.agent_page.clear_conversation()
        if outcome.offline_requested:
            self._switch_to_offline()
        if outcome.safe_mode_requested:
            self._enable_safe_mode()
        if outcome.model_override is not None:
            self._switch_model(outcome.model_override)
        return outcome

    def _slash_context(self) -> SlashContext:
        selection = self.selection
        model = selection.model_name if selection else "offline"
        mode = selection.mode_label if selection else "OFFLINE"
        context = selection.context_label if selection else "0k"
        status = selection.status if selection else "OFFLINE"
        story_act = (
            self.director.act.name
            if self.director
            else (self.progress.act.upper() if self.progress else "BOOT")
        )
        output_root = str(self.relics.output_root) if self.relics else "not configured"
        installed: tuple[str, ...] = ()
        if self.startup is not None:
            installed = self.startup.dialogue_model_names
        elif selection is not None:
            installed = tuple(
                profile.model for profile in selection.profiles if not profile.is_offline
            )

        relic_text = (
            "Relics are available in the approved output directory."
            if self.progress and self.progress.relic_generated
            else "No relic has been generated yet."
        )
        reconstruct_text = (
            self.echoes.reconstruct(self.progress)
            if self.echoes is not None and self.progress is not None
            else "No Death Echo fragments have been recorded yet."
        )
        return SlashContext(
            model=model,
            mode=mode,
            context=context,
            ollama_status=status,
            story_act=story_act,
            output_root=output_root,
            installed_models=installed,
            conversation_count=len(self.agent_page.conversation) if self.agent_page else 0,
            safe_mode=self.safe_mode,
            relic_text=relic_text,
            reconstruct_text=reconstruct_text,
        )

    def _switch_to_offline(self) -> None:
        self.dialogue = OfflineDialogueEngine(reason="slash /offline")
        if self.selection is not None:
            offline_profile = next(
                (profile for profile in self.selection.profiles if profile.is_offline),
                self.selection.active_profile,
            )
            self.selection = replace(
                self.selection,
                mode="offline",
                active_profile=offline_profile,
                source="slash-offline",
                message="Offline mode selected from Agent page.",
            )
        if self.agent_page is not None and self.selection is not None:
            self.agent_page.update_model(
                self.selection.model_name,
                self.selection.mode_label,
                self.selection.context_label,
            )
            self.agent_page.ollama_status = "OFFLINE"
            self.agent_page.mode = "OFFLINE"

    def _enable_safe_mode(self) -> None:
        self.safe_mode = True
        self.display.low_stimulation = True
        if self.agent_page is not None:
            self.agent_page.safe_mode = True

    def _switch_model(self, model: str) -> None:
        if self.selection is None:
            return
        for profile in self.selection.profiles:
            if profile.model == model:
                self.selection = replace(
                    self.selection,
                    active_profile=profile,
                    source="slash-select",
                    message=f"Selected installed model: {model}",
                )
                if self.dialogue is not None:
                    switch = getattr(self.dialogue, "select_model", None)
                    if callable(switch):
                        switch(model)
                if self.agent_page is not None:
                    self.agent_page.update_model(
                        self.selection.model_name,
                        self.selection.mode_label,
                        self.selection.context_label,
                    )
                return

    def _complete_story(self) -> None:
        if self.progress is None:
            return
        self.progress.act = "cleared"
        if self.director is not None:
            from vormir_sentinel.story import StoryAct

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

    def _stream_dialogue(self, question: str) -> str:
        assert self.dialogue is not None
        answer_parts: list[str] = []
        for fragment in self.dialogue.stream(question):
            answer_parts.append(fragment)
            self.display.write_fragment(fragment)
        self.display.print()
        return "".join(answer_parts)

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
        if self.agent_page is not None and self.agent_page.full_page:
            self.agent_page.enter()
            return

        mode = (
            "SAFE MODE — no animation, network, or host commands."
            if self.safe_mode
            else ("FICTIONAL INTERFACE — the real host is not being controlled.")
        )
        self.display.print("RedSkoll Agent Terminal / Vormir Sentinel", style="bold red")
        self.display.print(mode, style="cyan")
        if self.selection is not None:
            self.display.print(
                f"model: {self.selection.model_name}   mode: {self.selection.mode_label}   "
                f"context: {self.selection.context_label}",
                style="cyan",
            )
        elif self.dialogue is not None:
            self.display.print(self.dialogue.status_line, style="cyan")
        self.display.print(
            "Type /help for Agent commands or help for the virtual command map. "
            "Safe exits: /exit, exit --now, Ctrl+C twice, or close this window."
        )
        self.display.print("[fictional takeover only; no host command was executed]")
        self.display.print()

    def _can_animate_install(self) -> bool:
        return bool(
            self.display.is_tty
            and self.display.color_enabled
            and not self.display.low_stimulation
            and not self.safe_mode
        )

    def _can_use_readline(self) -> bool:
        if self.stdin is None:
            return True
        return not self.stdin.closed and self.stdin.isatty()

    def _configure_readline(self) -> None:
        try:
            import readline
        except ImportError:
            try:
                import pyreadline3.rlmain as readline  # type: ignore[import-not-found,no-redef]
            except ImportError:
                return

        commands = tuple(sorted(set(_READLINE_COMMANDS).union(self.slash_registry.names())))

        def completer(text: str, state: int) -> str | None:
            matches = [command for command in commands if command.startswith(text.lower())]
            return matches[state] if state < len(matches) else None

        readline.set_completer(completer)
        readline.set_completer_delims(" \t\n")
        readline.parse_and_bind("tab: complete")
        with contextlib.suppress(AttributeError, OSError):
            readline.set_history_length(1000)
