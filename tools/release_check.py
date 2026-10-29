#!/usr/bin/env python3
"""Check release metadata and optional wheel contents before tagging."""

from __future__ import annotations

import argparse
import tomllib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check_metadata() -> str:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    version = project["version"]

    package_init = (ROOT / "src" / "vormir_sentinel" / "__init__.py").read_text(encoding="utf-8")
    assert f'__version__ = "{version}"' in package_init
    assert f"## [{version}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert (ROOT / ".github" / "workflows" / "ci.yml").exists()
    assert (ROOT / "docs" / "release-checklist.md").exists()
    return version


def check_wheel(path: Path, version: str) -> None:
    if not path.exists():
        raise AssertionError(f"Wheel not found: {path}")
    with zipfile.ZipFile(path) as wheel:
        names = set(wheel.namelist())
    expected = {
        "vormir_sentinel/__init__.py",
        "vormir_sentinel/assets/death_echoes.json",
        "vormir_sentinel/assets/polyglot_relic.txt",
        "vormir_sentinel/assets/polyglot_relic.bf",
        "vormir_sentinel/assets/whitespace_relic.ws",
        "vormir_sentinel/assets/templates/resurrection.template.html",
        "vormir_sentinel/scripts/slash_commands.json",
        "vormir_sentinel/scripts/redskoll_agent.json",
        "vormir_sentinel/scripts/startup.json",
        "vormir_sentinel/scripts/takeover.json",
    }
    missing = expected - names
    if missing:
        raise AssertionError(f"Wheel is missing assets: {sorted(missing)}")
    assert f"{version}" in path.name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()

    version = check_metadata()
    if args.wheel is not None:
        check_wheel(args.wheel, version)
    print(f"Release metadata: OK ({version})")
    if args.wheel is not None:
        print(f"Wheel assets: OK ({args.wheel.name})")


if __name__ == "__main__":
    main()
