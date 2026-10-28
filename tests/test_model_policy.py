from __future__ import annotations

import unittest
from unittest.mock import patch

from vormir_sentinel.model_policy import (
    ModelCatalog,
    available_memory_gib,
)


class ModelPolicyTests(unittest.TestCase):
    def test_repository_catalog_loads_gpu_cpu_and_offline_profiles(self) -> None:
        catalog = ModelCatalog.load()

        self.assertEqual(catalog.gpu_profile.model, "qwen2.5:7b-instruct-q4_K_M")
        self.assertEqual(catalog.cpu_profile.model, "qwen2.5:3b-instruct-q4_K_M")
        self.assertTrue(catalog.offline_profile.is_offline)
        self.assertEqual(catalog.gpu_profile.request_options()["num_gpu"], 999)
        self.assertEqual(catalog.cpu_profile.request_options()["threads"], 12)

    @patch("vormir_sentinel.model_policy.available_memory_gib", return_value=8.0)
    def test_auto_prefers_gpu_above_threshold(self, _memory: object) -> None:
        candidates = ModelCatalog.load().candidates("auto")

        self.assertEqual(candidates[0].name, "gpu_primary")
        self.assertIn("gpu_emergency", [profile.name for profile in candidates])
        self.assertIn("cpu_fallback", [profile.name for profile in candidates])
        self.assertTrue(candidates[-1].is_offline)

    @patch("vormir_sentinel.model_policy.available_memory_gib", return_value=3.0)
    def test_auto_uses_cpu_between_thresholds(self, _memory: object) -> None:
        candidates = ModelCatalog.load().candidates("auto")

        self.assertEqual(candidates[0].name, "cpu_fallback")
        self.assertTrue(all(profile.name != "gpu_primary" for profile in candidates))

    @patch("vormir_sentinel.model_policy.available_memory_gib", return_value=1.0)
    def test_auto_uses_offline_below_minimum(self, _memory: object) -> None:
        candidates = ModelCatalog.load().candidates("auto")

        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0].is_offline)

    def test_explicit_modes_are_deterministic(self) -> None:
        catalog = ModelCatalog.load()

        self.assertEqual(catalog.candidates("gpu")[0].name, "gpu_primary")
        self.assertEqual(catalog.candidates("gpu")[1].name, "gpu_emergency")
        self.assertEqual(catalog.candidates("cpu")[0].name, "cpu_fallback")
        self.assertTrue(catalog.candidates("offline")[0].is_offline)

    def test_memory_detection_returns_non_negative_value(self) -> None:
        value = available_memory_gib()

        if value is not None:
            self.assertGreaterEqual(value, 0.0)


if __name__ == "__main__":
    unittest.main()
