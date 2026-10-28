from __future__ import annotations

import unittest

from vormir_sentinel.commands import CommandRouter, SessionState
from vormir_sentinel.config import Config


class CommandRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = CommandRouter(Config())
        self.state = SessionState()

    def test_core_posix_commands(self) -> None:
        self.assertEqual(
            self.router.route("whoami", self.state).text,
            "a sacrifice yet to be claimed",
        )
        self.assertIn("vormir-soulkeeper", self.router.route("uname -a", self.state).text)
        self.assertEqual(self.router.route("pwd", self.state).text, "/")
        self.assertIn("soulkeepers", self.router.route("id", self.state).text)
        self.assertIn("Vormir epoch", self.router.route("date", self.state).text)
        self.assertIn("soul-storage", self.router.route("df -h", self.state).text)
        listing = self.router.route("ls", self.state).text
        self.assertIn("vormir/", listing)
        self.assertIn("tesseract.core", listing)

    def test_navigation_and_cat_are_virtual(self) -> None:
        self.assertEqual(self.router.route("cd /vormir", self.state).text, "")
        self.assertEqual(self.state.cwd, "/vormir")

        outcome = self.router.route("cat tesseract.core", self.state)
        self.assertIn("merely weighed", outcome.text)

    def test_host_sensitive_file_is_not_available(self) -> None:
        outcome = self.router.route("cat /etc/passwd", self.state)
        self.assertEqual(outcome.status, "error")
        self.assertIn("No such fictional path", outcome.text)

    def test_windows_commands_are_intercepted(self) -> None:
        outcome = self.router.route("dir", self.state)
        self.assertIn("we speak POSIX", outcome.text)

        powershell = self.router.route("powershell Get-ChildItem", self.state)
        self.assertIn("nothing was executed", powershell.text)

    def test_unknown_command_never_requests_host_execution(self) -> None:
        outcome = self.router.route("sudo rm -rf /", self.state)
        self.assertEqual(outcome.status, "unknown")
        self.assertIn("Nothing was sent to the host", outcome.text)
        self.assertFalse(outcome.exit_requested)

    def test_force_exit_only_recognizes_now_flag(self) -> None:
        self.assertTrue(self.router.route("exit --now", self.state).exit_requested)
        self.assertFalse(self.router.route("exit --force", self.state).exit_requested)

    def test_fictional_secret_does_not_request_real_credentials(self) -> None:
        outcome = self.router.route("secret --fictional", self.state)
        self.assertIn("invented shadows", outcome.text)

    def test_help_states_the_safety_boundary(self) -> None:
        outcome = self.router.route("help", self.state)
        self.assertIn("no host shell", outcome.text)
        self.assertIn("exit --now", outcome.text)


if __name__ == "__main__":
    unittest.main()
