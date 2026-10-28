from __future__ import annotations

import unittest

from vormir_sentinel.character import (
    STONEKEEPER_SYSTEM_PROMPT,
    build_messages,
    postprocess_response,
)


class CharacterTests(unittest.TestCase):
    def test_system_prompt_fixes_voice_and_safety(self) -> None:
        self.assertIn("Johann Schmidt", STONEKEEPER_SYSTEM_PROMPT)
        self.assertIn("Answer the user's substantive question", STONEKEEPER_SYSTEM_PROMPT)
        self.assertIn("Never claim that you control", STONEKEEPER_SYSTEM_PROMPT)
        self.assertIn("Match the user's language", STONEKEEPER_SYSTEM_PROMPT)

    def test_response_postprocessing_removes_model_scaffolding(self) -> None:
        raw = (
            "<think>private reasoning}</think>\n"
            "As an AI assistant, the answer is 42.\n"
            "Keep the code:\n"
            "```python\nprint('ok')\n```\n"
        )
        cleaned = postprocess_response(raw)

        self.assertNotIn("private reasoning", cleaned)
        self.assertNotIn("AI assistant", cleaned)
        self.assertIn("answer is 42", cleaned)
        self.assertIn("print('ok')", cleaned)

    def test_generic_vendor_introduction_is_corrected_in_character(self) -> None:
        chinese = postprocess_response(
            "您好！我是由深度求索公司开发的智能助手DeepSeek-R1，请问有什么可以帮您？"
        )
        english = postprocess_response(
            "Hello! I am an AI assistant created to help users with many tasks."
        )

        self.assertIn("约翰·施密特", chinese)
        self.assertNotIn("DeepSeek-R1", chinese)
        self.assertIn("Johann Schmidt", english)
        self.assertNotIn("AI assistant", english)

    def test_message_history_is_bounded_to_twelve_turns(self) -> None:
        history = [
            {"role": "user" if index % 2 == 0 else "assistant", "content": str(index)}
            for index in range(20)
        ]
        messages = build_messages("question", history)

        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[-1], {"role": "user", "content": "question"})
        self.assertEqual(len(messages), 14)
        self.assertEqual(messages[1]["content"], "8")


if __name__ == "__main__":
    unittest.main()
