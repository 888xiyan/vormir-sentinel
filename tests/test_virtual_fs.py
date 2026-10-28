from __future__ import annotations

import unittest

from vormir_sentinel.virtual_fs import VirtualFileSystem, VirtualPathError


class VirtualFileSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = VirtualFileSystem()

    def test_absolute_and_relative_paths_stay_in_the_fiction(self) -> None:
        self.assertEqual(self.fs.resolve("/", "vormir/tesseract.core"), "/vormir/tesseract.core")
        self.assertEqual(self.fs.resolve("/vormir", "tesseract.core"), "/vormir/tesseract.core")
        self.assertEqual(self.fs.resolve("/vormir", ".."), "/")
        self.assertEqual(self.fs.resolve("/", "~"), "/root")

    def test_host_paths_are_not_discoverable(self) -> None:
        with self.assertRaises(VirtualPathError):
            self.fs.resolve("/", "/etc/passwd")
        with self.assertRaises(VirtualPathError):
            self.fs.resolve("/", str(PathHome()))

    def test_listing_contains_only_fixed_entries(self) -> None:
        entries = self.fs.list_directory("/", "vormir")
        names = [name for name, _is_directory in entries]

        self.assertEqual(
            names,
            ["entropy.sha", "johann_echo.mem", "sacrifice.log", "tesseract.core"],
        )

    def test_file_content_is_fixed(self) -> None:
        content = self.fs.read_file("/", "/vormir/tesseract.core").content
        self.assertIn("Knowledge is not denied here", content)


class PathHome:
    """Small sentinel value used to ensure no host path lookup occurs."""

    def __str__(self) -> str:
        return "/home/yhy/.ssh/id_test"


if __name__ == "__main__":
    unittest.main()
