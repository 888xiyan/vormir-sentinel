from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from vormir_sentinel.config import Config
from vormir_sentinel.model_policy import ModelCatalog
from vormir_sentinel.ollama import InstalledModel, OllamaConnectionError
from vormir_sentinel.startup import (
    default_selection,
    discover_startup,
    download_command,
    format_model_list,
    interactive_selection,
    selection_from_model,
)


class FakeClient:
    def __init__(self, models: tuple[InstalledModel, ...] | None = None, error: bool = False):
        self.models = models or ()
        self.error = error

    def list_model_metadata(self) -> tuple[InstalledModel, ...]:
        if self.error:
            raise OllamaConnectionError("not running")
        return self.models


GPU = InstalledModel(name="qwen2.5:7b-instruct-q4_K_M", size_bytes=5_000_000_000)
CPU = InstalledModel(name="qwen2.5:3b-instruct-q4_K_M", size_bytes=2_000_000_000)
CUSTOM = InstalledModel(name="local-chat:latest", family="qwen2")
EMBEDDING = InstalledModel(name="qwen3-embedding:4b", family="embedding")


class StartupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config()
        self.catalog = ModelCatalog.load()

    def test_gpu_model_discovery(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient((GPU, CPU)),  # type: ignore[arg-type]
        )

        self.assertEqual(discovery.status, "OLLAMA_READY_GPU")
        self.assertEqual(discovery.dialogue_model_names, (GPU.name, CPU.name))

    def test_only_embedding_models_reports_no_dialogue_model(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient((EMBEDDING,)),  # type: ignore[arg-type]
        )

        self.assertEqual(discovery.status, "OLLAMA_NO_MODEL")
        self.assertEqual(discovery.dialogue_model_names, ())
        self.assertIn("ollama pull", discovery.message)

    def test_service_failure_reports_not_running(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient(error=True),  # type: ignore[arg-type]
        )

        self.assertEqual(discovery.status, "OLLAMA_NOT_RUNNING")
        self.assertIn("ollama serve", discovery.message)

    def test_custom_models_are_selectable_but_embeddings_are_not(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient((EMBEDDING, CUSTOM)),  # type: ignore[arg-type]
        )
        selection = default_selection(self.config, self.catalog, discovery)

        self.assertEqual(discovery.status, "OLLAMA_READY_CUSTOM")
        self.assertEqual(selection.model_name, CUSTOM.name)
        with self.assertRaises(ValueError):
            selection_from_model(self.config, self.catalog, discovery, EMBEDDING.name)

    def test_download_command_is_printed_not_executed(self) -> None:
        with patch.object(subprocess, "run") as run:
            command = download_command("qwen2.5:7b-instruct-q4_K_M")

        self.assertEqual(command, "ollama pull qwen2.5:7b-instruct-q4_K_M")
        run.assert_not_called()

    def test_interactive_offline_choice(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient((GPU,)),  # type: ignore[arg-type]
        )
        outputs: list[str] = []

        selection = interactive_selection(
            self.config,
            self.catalog,
            discovery,
            read=lambda _prompt: "4",
            write=outputs.append,
        )

        self.assertEqual(selection.mode, "offline")
        self.assertTrue(any("Startup selection" in line for line in outputs))

    def test_interactive_download_choice_does_not_start_download(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient(error=True),  # type: ignore[arg-type]
        )
        outputs: list[str] = []
        answers = iter(["5"])

        def read(_prompt: str) -> str:
            try:
                return next(answers)
            except StopIteration:
                raise EOFError from None

        with patch.object(subprocess, "run") as run:
            selection = interactive_selection(
                self.config,
                self.catalog,
                discovery,
                read=read,
                write=outputs.append,
            )

        self.assertEqual(selection.mode, "offline")
        self.assertTrue(any("ollama serve" in line or "ollama pull" in line for line in outputs))
        run.assert_not_called()

    def test_model_list_marks_embedding_models(self) -> None:
        discovery = discover_startup(
            self.config,
            self.catalog,
            FakeClient((EMBEDDING, CUSTOM)),  # type: ignore[arg-type]
        )

        listing = format_model_list(discovery)

        self.assertIn(CUSTOM.name, listing)
        self.assertIn("[not selectable: embedding]", listing)


if __name__ == "__main__":
    unittest.main()
