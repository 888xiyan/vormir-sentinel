"""Generate harmless, auditable story artifacts inside an approved output directory."""

from __future__ import annotations

import html
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from vormir_sentinel.state import ProgressState

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_BASE = PROJECT_ROOT if (PROJECT_ROOT / "pyproject.toml").exists() else Path.cwd()
CONTENT_ROOT = PROJECT_ROOT / "content"
TEMPLATE_ROOT = PROJECT_ROOT / "templates"
GITHUB_URL = "https://github.com/888xiyan/vormir-sentinel"
RELIC_NAMES = (
    "A_DEED_OF_SACRIFICE.txt",
    "polyglot_relic.txt",
    "polyglot_relic.bf",
    "whitespace_relic.ws",
    "resurrection.html",
)


class RelicError(RuntimeError):
    """Raised when harmless artifacts cannot be generated safely."""


@dataclass(frozen=True)
class GeneratedRelic:
    path: Path
    kind: str


def resolve_output_root(workspace: str | Path = "vormir-output") -> Path:
    """Resolve only a relative project output path; absolute paths are rejected."""
    candidate = Path(workspace).expanduser()
    if candidate.is_absolute() or ".." in candidate.parts or candidate == Path("."):
        raise RelicError("Output workspace must be a relative path inside the project directory.")
    root = OUTPUT_BASE.resolve()
    resolved = (root / candidate).resolve()
    if not resolved.is_relative_to(root):
        raise RelicError("Output workspace escapes the project directory.")
    return resolved


class RelicGenerator:
    def __init__(self, output_root: str | Path = "vormir-output") -> None:
        self.output_root = resolve_output_root(output_root)

    def generate(self, state: ProgressState) -> tuple[GeneratedRelic, ...]:
        self.output_root.mkdir(parents=True, exist_ok=True)
        generated: list[GeneratedRelic] = []

        for name in ("polyglot_relic.txt", "polyglot_relic.bf", "whitespace_relic.ws"):
            source = CONTENT_ROOT / name
            if not source.exists():
                continue
            generated.append(self._copy(source, name, "puzzle"))

        deed = self.output_root / "A_DEED_OF_SACRIFICE.txt"
        if not deed.exists():
            deed.write_text(
                "A DEED OF SACRIFICE — fictional story artifact\n"
                "===============================================\n\n"
                "This file records symbolic story state only.\n"
                "No host file, account, credential, or secret was sacrificed.\n\n"
                f"Tributes recorded: {state.tribute_count}\n"
                "All effects remain reversible and auditable.\n",
                encoding="utf-8",
            )
        generated.append(GeneratedRelic(deed, "deed"))

        resurrection = self._generate_resurrection()
        if resurrection is not None:
            generated.append(resurrection)
        state.relic_generated = True
        state.resurrection_generated = any(item.kind == "resurrection" for item in generated)
        return tuple(generated)

    def clean(self) -> bool:
        """Delete only known generated filenames; never recurse into arbitrary paths."""
        removed = False
        if not self.output_root.exists():
            return False
        for name in RELIC_NAMES:
            candidate = self.output_root / name
            if candidate.is_file():
                candidate.unlink()
                removed = True
        if self.output_root.is_dir() and not any(self.output_root.iterdir()):
            self.output_root.rmdir()
        return removed

    def _copy(self, source: Path, name: str, kind: str) -> GeneratedRelic:
        destination = self.output_root / name
        if not destination.exists():
            shutil.copyfile(source, destination)
        return GeneratedRelic(destination, kind)

    def _generate_resurrection(self) -> GeneratedRelic | None:
        template = TEMPLATE_ROOT / "resurrection.template.html"
        incantations = CONTENT_ROOT / "resurrection_incantations.json"
        if not template.exists() or not incantations.exists():
            return None
        try:
            data = json.loads(incantations.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RelicError(f"Cannot read resurrection incantations: {exc}") from exc
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise RelicError("Resurrection incantations require an items array.")

        marquee = "\n".join(
            '<div class="marquee"><div class="track">'
            + " // ".join(html.escape(str(item.get("text", ""))) for item in items)
            + "</div></div>"
            for _ in range(3)
        )
        rows = "\n".join(
            "<li><span>"
            + html.escape(str(item.get("id", "")))
            + " // "
            + html.escape(str(item.get("language", "")))
            + "</span>"
            + html.escape(str(item.get("text", "")))
            + "</li>"
            for item in items
        )
        rendered = (
            template.read_text(encoding="utf-8")
            .replace("{{MARQUEE_ROWS}}", marquee)
            .replace("{{INCANTATION_ROWS}}", rows)
            .replace("https://github.com/888xiyan/vormir-sentinel", GITHUB_URL)
        )
        destination = self.output_root / "resurrection.html"
        if not destination.exists():
            destination.write_text(rendered, encoding="utf-8")
        return GeneratedRelic(destination, "resurrection")
