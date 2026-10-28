from __future__ import annotations

import unittest

from vormir_sentinel.commands import CommandOutcome
from vormir_sentinel.config import AppConfig, Config
from vormir_sentinel.story import StoryAct, StoryDirector


class StoryDirectorTests(unittest.TestCase):
    def test_boot_sequence_reaches_vormir_shell(self) -> None:
        director = StoryDirector(Config())

        prologue = director.begin()

        self.assertIn("Progress: 99%", prologue)
        self.assertIn("fictional takeover only", prologue)
        self.assertEqual(director.act, StoryAct.VORMIR_SHELL)

    def test_safe_mode_skips_high_intensity_boot(self) -> None:
        config = Config(app=AppConfig(safe_mode=True, low_stimulation=True))
        director = StoryDirector(config)

        prologue = director.begin()

        self.assertIn("Low-stimulation startup", prologue)
        self.assertNotIn("Progress: 99%", prologue)

    def test_returning_run_skips_installation_bait(self) -> None:
        director = StoryDirector(Config())
        director.begin()

        returning = director.begin()

        self.assertIn("does not need to repeat", returning)

    def test_defy_advances_to_takeover_act(self) -> None:
        director = StoryDirector(Config())
        director.begin()

        result = director.observe_command("defy", CommandOutcome(status="unknown"))

        self.assertEqual(director.act, StoryAct.TAKEOVER)
        self.assertIn("TAKEOVER PROTOCOL", result)
        self.assertIn("No real alarm", result)

    def test_interrupts_are_always_labeled_fictional(self) -> None:
        director = StoryDirector(Config())

        first = director.on_interrupt(1)
        second = director.on_interrupt(2)

        self.assertIn("fictional and was not executed", first)
        self.assertIn("sudo /opt/hydra", first)
        self.assertIn("physical window remains yours", second)
        self.assertIn("exit --now", second)


if __name__ == "__main__":
    unittest.main()
