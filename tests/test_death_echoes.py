from __future__ import annotations

import unittest
from datetime import date

from vormir_sentinel.death_echoes import DeathEchoManager
from vormir_sentinel.state import ProgressState


class DeathEchoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = DeathEchoManager()
        self.state = ProgressState(cleared=True)

    def test_echoes_advance_once_per_day(self) -> None:
        first = self.manager.start_echo(self.state, today=date(2026, 10, 28))
        same_day = self.manager.start_echo(self.state, today=date(2026, 10, 28))
        next_day = self.manager.start_echo(self.state, today=date(2026, 10, 29))

        self.assertIn("DEATH ECHO 1", first)
        self.assertEqual(same_day, first)
        self.assertIn("DEATH ECHO 2", next_day)
        self.assertEqual(self.state.echo_count, 2)

    def test_reconstruct_does_not_increment_echo_count(self) -> None:
        self.manager.start_echo(self.state, today=date(2026, 10, 28))
        before = self.state.echo_count

        reconstruction = self.manager.reconstruct(self.state)

        self.assertIn("RETURN TO THE", reconstruction)
        self.assertEqual(self.state.echo_count, before)

    def test_uncleared_story_has_no_echo(self) -> None:
        state = ProgressState(cleared=False)

        self.assertEqual(self.manager.start_echo(state), "")


if __name__ == "__main__":
    unittest.main()
