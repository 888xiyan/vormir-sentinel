from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vormir_sentinel.config import (
    Config,
    ConfigError,
    apply_cli_overrides,
    load_config,
)


class ConfigTests(unittest.TestCase):
    def test_repository_configuration_loads_safely(self) -> None:
        config = load_config()

        self.assertEqual(config.llm.model, "qwen2.5:7b-instruct-q4_K_M")
        self.assertFalse(config.safety.allow_network)
        self.assertFalse(config.safety.allow_real_command_execution)
        self.assertTrue(config.safety.allow_local_inference)

    def test_cli_overrides_enforce_safe_network_policy(self) -> None:
        config = Config()
        config = apply_cli_overrides(config, safe_mode=True, offline=True)

        self.assertTrue(config.app.safe_mode)
        self.assertTrue(config.app.low_stimulation)
        self.assertFalse(config.safety.allow_network)
        self.assertFalse(config.safety.allow_local_inference)

    def test_real_command_execution_is_rejected(self) -> None:
        content = """
[safety]
allow_real_command_execution = true
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.toml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_remote_networking_is_rejected(self) -> None:
        content = """
[safety]
allow_network = true
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe-network.toml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_real_filesystem_exploration_is_rejected(self) -> None:
        content = """
[safety]
allow_filesystem_exploration = true
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.toml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_missing_explicit_config_is_an_error(self) -> None:
        with self.assertRaises(ConfigError):
            load_config("/definitely/not/a/vormir-config.toml")


if __name__ == "__main__":
    unittest.main()
