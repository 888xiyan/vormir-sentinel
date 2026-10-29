from __future__ import annotations

import unittest
from io import StringIO

from vormir_sentinel.agent import AgentPage
from vormir_sentinel.console import Display


class TTYStringIO(StringIO):
    def isatty(self) -> bool:
        return True


class AgentPageTests(unittest.TestCase):
    def test_full_page_contains_status_ascii_and_safety_boundary(self) -> None:
        display = Display(TTYStringIO(), color=True)
        page = AgentPage(
            display=display,
            model="qwen2.5:7b",
            mode="GPU",
            context="8k",
            ollama_status="OLLAMA_READY_GPU",
            story_act="AGENT_PAGE",
        )

        self.assertTrue(page.full_page)
        page.enter()
        output = display.stream.getvalue()

        self.assertIn("RedSkoll Agent Terminal", output)
        self.assertIn("model: qwen2.5:7b", output)
        self.assertIn("REDSKOLL AGENT", output)
        self.assertIn("fictional takeover only", output)

    def test_plain_mode_does_not_render_full_page(self) -> None:
        display = Display(StringIO(), color=False)
        page = AgentPage(
            display=display,
            model="none",
            mode="OFFLINE",
            context="4k",
            ollama_status="OFFLINE",
            story_act="OFFLINE_AGENT_PAGE",
            safe_mode=True,
        )

        self.assertFalse(page.full_page)
        page.enter()

        self.assertEqual(display.stream.getvalue(), "")

    def test_conversation_is_bounded_to_twelve_turns(self) -> None:
        display = Display(StringIO(), color=False)
        page = AgentPage(
            display=display,
            model="none",
            mode="OFFLINE",
            context="4k",
            ollama_status="OFFLINE",
            story_act="OFFLINE_AGENT_PAGE",
        )
        for index in range(15):
            page.finish_turn(f"q{index}", f"a{index}")

        self.assertEqual(len(page.conversation), 12)
        self.assertEqual(page.conversation[0][0], "q3")


if __name__ == "__main__":
    unittest.main()
