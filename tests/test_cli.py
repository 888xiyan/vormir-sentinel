from __future__ import annotations

import tempfile
import unittest
from io import StringIO
from pathlib import Path

from vormir_sentinel.cli import main
from vormir_sentinel.state import StateStore


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
