from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from vormir_sentinel.slash import SCRIPTS_ROOT, SlashCommandRegistry, SlashContext


def context(**overrides: object) -> SlashContext:
    values: dict[str, object] = {
        "model": "qwen2.5:7b-instruct-q4_K_M",
        "mode": "GPU",
        "context": "8k",
        "ollama_status": "OLLAMA_READY_GPU",
        "story_act": "AGENT_PAGE",
        "output_root": "/tmp/vormir-output",
        "installed_models": (
            "qwen2.5:7b-instruct-q4_K_M",
            "qwen2.5:3b-instruct-q4_K_M",
        ),
        "conversation_count": 3,
    }
    values.update(overrides)
    return SlashContext(**values)  # type: ignore[arg-type]


class SlashCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = SlashCommandRegistry.load()

    def test_registry_loads_fixed_commands(self) -> None:
        names = self.registry.names()

        for expected in (
            "/help",
            "/model",
            "/download",
            "/offline",
            "/status",
            "/clear",
            "/reconstruct",
            "/safe",
            "/exit",
        ):
            self.assertIn(expected, names)

    def test_status_uses_whitelisted_placeholders(self) -> None:
        outcome = self.registry.render("/status", context())

        self.assertIn("model: qwen2.5:7b-instruct-q4_K_M", outcome.text)
        self.assertIn("story: AGENT_PAGE", outcome.text)
        self.assertNotIn("{model}", outcome.text)

    def test_model_list_and_select(self) -> None:
        listing = self.registry.render("/model list", context())
        selected = self.registry.render(
            "/model select qwen2.5:3b-instruct-q4_K_M",
            context(),
        )
        missing = self.registry.render("/model select absent:latest", context())

        self.assertIn("qwen2.5:3b-instruct-q4_K_M", listing.text)
        self.assertEqual(selected.model_override, "qwen2.5:3b-instruct-q4_K_M")
        self.assertEqual(missing.status, "error")

    def test_download_prints_command_without_execution(self) -> None:
        with patch.object(subprocess, "run") as run:
            outcome = self.registry.render("/download qwen2.5:7b-instruct-q4_K_M", context())

        self.assertIn("ollama pull qwen2.5:7b-instruct-q4_K_M", outcome.text)
        self.assertIn("did not download or execute", outcome.text)
        run.assert_not_called()

    def test_clear_and_exit_state_updates(self) -> None:
        cleared = self.registry.render("/clear", context())
        exited = self.registry.render("/exit", context())

        self.assertTrue(cleared.clear_conversation)
        self.assertFalse(cleared.exit_requested)
        self.assertTrue(exited.exit_requested)

    def test_unknown_slash_command_is_rejected(self) -> None:
        outcome = self.registry.render("/rm -rf /", context())

        self.assertEqual(outcome.status, "error")
        self.assertIn("Unknown slash command", outcome.text)

    def test_fixed_scripts_contain_no_executable_code(self) -> None:
        for path in Path(SCRIPTS_ROOT).glob("*.json"):
            raw = path.read_text(encoding="utf-8").lower()
            self.assertNotIn("subprocess", raw)
            self.assertNotIn("os.system", raw)
            self.assertNotIn("shell=true", raw)
            json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
