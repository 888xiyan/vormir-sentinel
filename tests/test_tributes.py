from __future__ import annotations

import unittest

from vormir_sentinel.state import ProgressState
from vormir_sentinel.tributes import TributeManager


class TributeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = TributeManager()
        self.state = ProgressState()

    def test_five_symbolic_tributes_clear_story(self) -> None:
        results = [
            self.manager.record(["time"], self.state),
            self.manager.record(["name", "Jonas-Schmidt"], self.state),
            self.manager.record(["secret", "--fictional"], self.state),
            self.manager.record(["release"], self.state),
            self.manager.record(["file"], self.state),
        ]

        self.assertTrue(results[-1].completed)
        self.assertTrue(self.state.cleared)
        self.assertEqual(self.state.tribute_count, 5)

    def test_duplicate_tribute_is_not_counted_twice(self) -> None:
        self.manager.record(["time"], self.state)
        duplicate = self.manager.record(["time"], self.state)

        self.assertIn("already remembers", duplicate.text)
        self.assertEqual(self.state.tribute_count, 1)

    def test_secret_tribute_never_requests_real_credentials(self) -> None:
        result = self.manager.record(["secret", "--fictional"], self.state)

        self.assertIn("invented shadow", result.text)
        self.assertNotIn("password", result.text.lower())

    def test_name_values_are_limited_to_fictional_identifiers(self) -> None:
        result = self.manager.record(["name", "../../etc/passwd"], self.state)

        self.assertIn("fictional identity", result.text)
        self.assertEqual(self.state.tribute_count, 0)


if __name__ == "__main__":
    unittest.main()
