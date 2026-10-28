from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vormir_sentinel.state import ProgressState, StateStore


class StateStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.path = Path(self._tempdir.name) / "state.json"
        self.store = StateStore(self.path)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def test_save_and_load_round_trip(self) -> None:
        state = ProgressState(act="vormir_shell", tribute_count=2, tribute_kinds=["time", "name"])
        self.store.save(state)

        loaded = self.store.load()

        self.assertEqual(loaded.act, "vormir_shell")
        self.assertEqual(loaded.tribute_kinds, ["time", "name"])
        self.assertEqual(list(self.path.parent.glob(".*.tmp")), [])

    def test_corrupt_state_recovers_to_clean_default(self) -> None:
        self.path.write_text("{not-json", encoding="utf-8")

        loaded = self.store.load()

        self.assertFalse(loaded.cleared)
        self.assertEqual(loaded.act, "boot")

    def test_forget_removes_only_state_and_temp_files(self) -> None:
        self.store.save(ProgressState())
        temp = self.path.parent / f".{self.path.name}.abc.tmp"
        temp.write_text("temporary", encoding="utf-8")

        self.assertTrue(self.store.forget())

        self.assertFalse(self.path.exists())
        self.assertFalse(temp.exists())


if __name__ == "__main__":
    unittest.main()
