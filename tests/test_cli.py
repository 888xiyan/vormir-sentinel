from __future__ import annotations

import os
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from vormir_sentinel.cli import main
from vormir_sentinel.ollama import InstalledModel
from vormir_sentinel.repl import Repl
from vormir_sentinel.startup import StartupDiscovery
from vormir_sentinel.state import StateStore


class TTYStringIO(StringIO):
    def isatty(self) -> bool:
        return True


class ScriptedInput:
    def __init__(self, lines: list[str]) -> None:
        self._lines = iter(lines)
        self.prompts: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self._lines)


class InterruptingInput:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, _prompt: str) -> str:
        self.calls += 1
        if self.calls <= 2:
            raise KeyboardInterrupt
        return "exit --now"


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.state_store = StateStore(Path(self._tempdir.name) / "state.json")

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_repl_starts_routes_and_force_exits(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["whoami", "exit --now"])

        result = main(
            ["--offline", "--no-color"],
            stdout=output,
            input_function=scripted,
            state_store=self.state_store,
        )

        self.assertEqual(result, 0)
        self.assertIn("FICTIONAL INTERFACE", output.getvalue())
        self.assertIn("a sacrifice yet to be claimed", output.getvalue())
        self.assertIn("Safe exit engaged", output.getvalue())

    def test_returning_run_skips_installation_bait(self) -> None:
        first_output = StringIO()
        first = ScriptedInput(["exit --now"])
        main(
            ["--offline", "--no-color"],
            stdout=first_output,
            input_function=first,
            state_store=self.state_store,
        )
        second_output = StringIO()
        second = ScriptedInput(["exit --now"])

        main(
            ["--offline", "--no-color"],
            stdout=second_output,
            input_function=second,
            state_store=self.state_store,
        )

        self.assertIn("Vormir Sentinel bootstrap", first_output.getvalue())
        self.assertNotIn("Vormir Sentinel bootstrap", second_output.getvalue())
        self.assertIn("does not need to repeat", second_output.getvalue())

    def test_piped_output_has_no_ansi_escape_sequences(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["help", "exit"])

        main(
            ["--offline", "--no-color"],
            stdout=output,
            input_function=scripted,
            state_store=self.state_store,
        )

        self.assertNotIn("\x1b[", output.getvalue())

    def test_export_state_prints_versioned_json(self) -> None:
        output = StringIO()

        result = main(
            ["--export-state", "--plain"],
            stdout=output,
            state_store=self.state_store,
        )

        self.assertEqual(result, 0)
        self.assertIn('"schema_version": 1', output.getvalue())
        self.assertIn('"cleared": false', output.getvalue())

    def test_plain_alias_disables_ansi(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["help", "exit"])

        main(
            ["--offline", "--plain"],
            stdout=output,
            input_function=scripted,
            state_store=self.state_store,
        )

        self.assertNotIn("\x1b[", output.getvalue())
        self.assertIn("Vormir Sentinel", output.getvalue())

    def test_second_interrupt_always_exits(self) -> None:
        output = StringIO()
        interrupting = InterruptingInput()

        result = main(
            ["--offline", "--no-color"],
            stdout=output,
            input_function=interrupting,
            state_store=self.state_store,
        )

        self.assertEqual(result, 0)
        self.assertIn("Johann Schmidt", output.getvalue())
        self.assertIn("type: exit --now", output.getvalue())
        self.assertIn("returns to your control", output.getvalue())

    def test_safe_mode_still_exits_on_second_interrupt(self) -> None:
        output = StringIO()
        interrupting = InterruptingInput()

        result = main(
            ["--safe", "--offline", "--no-color"],
            stdout=output,
            input_function=interrupting,
            state_store=self.state_store,
        )

        self.assertEqual(result, 0)
        self.assertIn("SAFE MODE", output.getvalue())
        self.assertIn("Second interrupt accepted", output.getvalue())

    def test_list_models_reads_only_local_metadata(self) -> None:
        output = StringIO()
        discovery = StartupDiscovery(
            status="OLLAMA_READY_CUSTOM",
            models=(
                InstalledModel(name="local-chat:latest"),
                InstalledModel(name="embedding:latest", family="embedding"),
            ),
        )

        with patch("vormir_sentinel.cli.discover_startup", return_value=discovery):
            result = main(
                ["--list-models", "--plain"],
                stdout=output,
                state_store=self.state_store,
            )

        self.assertEqual(result, 0)
        self.assertIn("local-chat:latest", output.getvalue())
        self.assertIn("[not selectable: embedding]", output.getvalue())

    def test_pick_model_uses_interactive_selector(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["4", "exit --now"])
        discovery = StartupDiscovery(
            status="OLLAMA_READY_GPU",
            models=(InstalledModel(name="qwen2.5:7b-instruct-q4_K_M"),),
        )

        with patch("vormir_sentinel.cli.discover_startup", return_value=discovery):
            result = main(
                ["--pick-model", "--plain"],
                stdout=output,
                input_function=scripted,
                state_store=self.state_store,
            )

        self.assertEqual(result, 0)
        self.assertIn("Startup selection", output.getvalue())
        self.assertIn("Offline mode selected", output.getvalue())

    def test_offline_slash_commands_render_fixed_newlines(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["/help", "/download qwen2.5:7b-instruct-q4_K_M", "/exit"])

        result = main(
            ["--offline", "--plain"],
            stdout=output,
            input_function=scripted,
            state_store=self.state_store,
        )

        self.assertEqual(result, 0)
        self.assertIn("RedSkoll Agent commands:\n", output.getvalue())
        self.assertNotIn("RedSkoll Agent commands:\\n", output.getvalue())
        self.assertIn("ollama pull qwen2.5:7b-instruct-q4_K_M", output.getvalue())
        self.assertIn("Safe exit engaged", output.getvalue())

    def test_full_agent_page_supports_slash_and_posix_commands(self) -> None:
        output = TTYStringIO()
        scripted = ScriptedInput(["/help", "whoami", "exit --now"])
        discovery = StartupDiscovery(
            status="OLLAMA_READY_GPU",
            models=(InstalledModel(name="qwen2.5:7b-instruct-q4_K_M"),),
        )

        old_no_color = os.environ.pop("NO_COLOR", None)
        old_term = os.environ.get("TERM")
        os.environ["TERM"] = "xterm-256color"
        try:
            with (
                patch("vormir_sentinel.cli.discover_startup", return_value=discovery),
                patch.object(Repl, "_can_animate_install", return_value=False),
            ):
                result = main(
                    ["--mode", "gpu"],
                    stdout=output,
                    input_function=scripted,
                    state_store=self.state_store,
                )
        finally:
            if old_no_color is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = old_no_color
            if old_term is None:
                os.environ.pop("TERM", None)
            else:
                os.environ["TERM"] = old_term

        rendered = output.getvalue()
        self.assertEqual(result, 0)
        self.assertIn("RedSkoll Agent Terminal", rendered)
        self.assertIn("RedSkoll Agent commands:\n", rendered)
        self.assertIn("a sacrifice yet to be claimed", rendered)
        self.assertIn("SAFE EXIT: exit --now", rendered)

    def test_unknown_input_is_not_executed(self) -> None:
        output = StringIO()
        scripted = ScriptedInput(["touch /tmp/not-real", "exit --now"])

        main(
            ["--offline", "--no-color"],
            stdout=output,
            input_function=scripted,
            state_store=self.state_store,
        )

        self.assertIn("No request left this machine", output.getvalue())


if __name__ == "__main__":
    unittest.main()
