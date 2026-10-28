from __future__ import annotations

import unittest

from vormir_sentinel.repl import _command_completer


class ReadlineCompleterTests(unittest.TestCase):
    def test_completion_is_limited_to_whitelist_words(self) -> None:
        self.assertEqual(_command_completer("un", 0), "uname")
        self.assertEqual(_command_completer("un", 1), None)

    def test_completion_is_case_insensitive(self) -> None:
        self.assertEqual(_command_completer("WHO", 0), "whoami")

    def test_completion_never_returns_host_commands(self) -> None:
        self.assertEqual(_command_completer("sudo", 0), None)
        self.assertEqual(_command_completer("/usr", 0), None)


if __name__ == "__main__":
    unittest.main()
