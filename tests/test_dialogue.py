from __future__ import annotations

import unittest

from vormir_sentinel.dialogue import (
    OfflineDialogueEngine,
    StreamingDialogueEngine,
)
from vormir_sentinel.model_policy import ModelProfile
from vormir_sentinel.ollama import OllamaConnectionError


def _profile(name: str, model: str, *, offline: bool = False) -> ModelProfile:
    return ModelProfile(
        name=name,
        provider="offline" if offline else "ollama",
        model=model,
        display_name=name,
    )


class FakeGenericClient:
    def chat_stream(self, _model: str, _messages: object, _options: object):
        yield "我是深度求索（DeepSeek）公司开发的智能助手，"
        yield "很高兴为您服务。"


class FakeFailingThenWorkingClient:
    def __init__(self, partial_failure: bool = False) -> None:
        self.partial_failure = partial_failure
        self.calls: list[str] = []

    def chat_stream(self, model: str, _messages: object, _options: object):
        self.calls.append(model)
        if model == "gpu-model":
            if self.partial_failure:
                yield "partial"
            raise OllamaConnectionError("GPU unavailable")
        yield "A useful "
        yield "answer."


class DialogueEngineTests(unittest.TestCase):
    def test_offline_engine_uses_fixed_safe_text(self) -> None:
        engine = OfflineDialogueEngine(reason="test")
        answer = "".join(engine.stream("Who are you?"))

        self.assertIn("Stonekeeper", answer)
        self.assertIn("fictional", answer)
        self.assertIn("OFFLINE STORY", engine.status_line)

    def test_streaming_engine_falls_back_from_gpu_to_cpu(self) -> None:
        client = FakeFailingThenWorkingClient()
        engine = StreamingDialogueEngine(
            client,
            (
                _profile("gpu", "gpu-model"),
                _profile("cpu", "cpu-model"),
                _profile("offline", "none", offline=True),
            ),
        )

        answer = "".join(engine.stream("question"))

        self.assertEqual(client.calls, ["gpu-model", "cpu-model"])
        self.assertEqual(answer, "A useful answer.")
        self.assertIn("CPU", engine.status_line)
        self.assertIn("fell back", engine.status_line)

    def test_generic_self_introduction_is_replaced_before_release(self) -> None:
        engine = StreamingDialogueEngine(
            FakeGenericClient(),
            (_profile("gpu", "gpu-model"),),
        )

        answer = "".join(engine.stream("你是谁？"))

        self.assertNotIn("深度求索", answer)
        self.assertIn("约翰·施密特", answer)

    def test_partial_stream_is_not_replayed(self) -> None:
        client = FakeFailingThenWorkingClient(partial_failure=True)
        engine = StreamingDialogueEngine(
            client,
            (
                _profile("gpu", "gpu-model"),
                _profile("cpu", "cpu-model"),
            ),
        )

        answer = "".join(engine.stream("question"))

        self.assertEqual(client.calls, ["gpu-model"])
        self.assertIn("partial", answer)
        self.assertIn("vessel faltered", answer)


if __name__ == "__main__":
    unittest.main()
