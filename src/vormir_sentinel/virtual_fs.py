"""A fixed virtual filesystem that never touches host paths."""

from __future__ import annotations

import posixpath
from dataclasses import dataclass
from pathlib import PurePosixPath


class VirtualPathError(ValueError):
    """Raised for invalid or unavailable virtual paths."""


@dataclass(frozen=True)
class VirtualFile:
    content: str
    description: str = ""


DEFAULT_DIRECTORIES = frozenset(
    {
        "/",
        "/etc",
        "/opt",
        "/opt/hydra",
        "/root",
        "/tmp",
        "/var",
        "/var/log",
        "/vormir",
    }
)

DEFAULT_FILES: dict[str, VirtualFile] = {
    "/etc/vormir-release": VirtualFile(
        "Vormir keeper protocol 6.6.6-hydra\n",
        "fictional release metadata",
    ),
    "/opt/hydra/protocol.conf": VirtualFile(
        "keeper.bind = false\nsoul.capture = fictional\nhost_access = forbidden\n",
        "safe fictional daemon configuration",
    ),
    "/opt/hydra/vormir-daemon": VirtualFile(
        "A program-shaped absence. It has never been executed on this host.\n",
        "inert narrative artifact",
    ),
    "/root/last_words.txt": VirtualFile(
        "The window is still yours.\n",
        "a reminder from the keeper",
    ),
    "/tmp/regret.tmp": VirtualFile(
        "It exists only here. Removing it would alter no host file.\n",
        "future symbolic sacrifice target",
    ),
    "/var/log/vormir.log": VirtualFile(
        "[boot] A visitor opened a door that was never installed.\n"
        "[watch] The keeper is listening, but only to this window.\n",
        "fictional log",
    ),
    "/vormir/entropy.sha": VirtualFile(
        "6c3f2b6c6f73656b65657065722d6e657665722d74656c6c732d7468652d7472757468\n",
        "immutable fictional checksum",
    ),
    "/vormir/johann_echo.mem": VirtualFile(
        "A shape waits where memory refuses to end.\n",
        "fragmented keeper echo",
    ),
    "/vormir/sacrifice.log": VirtualFile(
        "No tribute has been recorded.\n",
        "symbolic tribute ledger",
    ),
    "/vormir/tesseract.core": VirtualFile(
        "Knowledge is not denied here. It is merely weighed.\n",
        "sealed narrative core",
    ),
}

# Keep the primary story artifacts visible from the opening `/` prompt, as shown
# in the product walkthrough. They remain fixed content, not host files.
for _name in ("entropy.sha", "johann_echo.mem", "sacrifice.log", "tesseract.core"):
    DEFAULT_FILES[f"/{_name}"] = DEFAULT_FILES[f"/vormir/{_name}"]


class VirtualFileSystem:
    """Purely in-memory path mapping and fixed content lookup."""

    def __init__(
        self,
        directories: frozenset[str] = DEFAULT_DIRECTORIES,
        files: dict[str, VirtualFile] | None = None,
    ) -> None:
        self.directories = frozenset(directories)
        self.files = dict(DEFAULT_FILES if files is None else files)

    @staticmethod
    def normalize(cwd: str, target: str) -> str:
        if "\x00" in target:
            raise VirtualPathError("NUL bytes do not exist in Vormir.")
        expanded = "/root" if target == "~" else target
        base = "" if expanded.startswith("/") else cwd
        joined = posixpath.join(base or "/", expanded)
        normalized = posixpath.normpath(joined)
        if not normalized.startswith("/"):
            normalized = f"/{normalized}"
        if PurePosixPath(normalized).is_absolute() is False:
            raise VirtualPathError("That path escapes the fictional root.")
        return normalized

    def resolve(self, cwd: str, target: str) -> str:
        normalized = self.normalize(cwd, target)
        if normalized in self.directories or normalized in self.files:
            return normalized
        raise VirtualPathError(f"No such fictional path: {target}")

    def is_directory(self, path: str) -> bool:
        return path in self.directories

    def is_file(self, path: str) -> bool:
        return path in self.files

    def read_file(self, cwd: str, target: str) -> VirtualFile:
        path = self.resolve(cwd, target)
        if path not in self.files:
            raise VirtualPathError(f"Not a fictional file: {target}")
        return self.files[path]

    def list_directory(self, cwd: str, target: str = ".") -> list[tuple[str, bool]]:
        path = self.resolve(cwd, target)
        if not self.is_directory(path):
            raise VirtualPathError(f"Not a fictional directory: {target}")

        prefix = "" if path == "/" else path
        entries: set[tuple[str, bool]] = set()
        for directory in self.directories:
            if directory == path or directory == "/":
                continue
            if directory.startswith(f"{prefix}/"):
                child = directory.removeprefix(prefix).strip("/")
                if "/" not in child:
                    entries.add((child, True))
        for file_path in self.files:
            if file_path.startswith(f"{prefix}/"):
                child = file_path.removeprefix(prefix).strip("/")
                if "/" not in child:
                    entries.add((child, False))

        return sorted(entries, key=lambda item: (item[0].lower(), not item[1]))
