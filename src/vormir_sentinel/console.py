"""Terminal presentation with graceful Rich and ANSI fallbacks."""

from __future__ import annotations

import time
from os import environ
from typing import Any, TextIO


def _stream_is_tty(stream: TextIO) -> bool:
    isatty = getattr(stream, "isatty", None)
    return bool(isatty and isatty())


class Display:
    """Small output abstraction that never invokes a shell."""

    def __init__(
        self,
        stream: TextIO,
        *,
        color: bool | None = None,
        low_stimulation: bool = False,
    ) -> None:
        self.stream = stream
        self.is_tty = _stream_is_tty(stream)
        self.color_enabled = (
            self.is_tty and environ.get("NO_COLOR") is None and environ.get("TERM", "") != "dumb"
            if color is None
            else color
        )
        self.low_stimulation = low_stimulation
        self._console: Any = self._make_rich_console()

    @property
    def width(self) -> int:
        if self._console is not None:
            try:
                return int(self._console.width)
            except (AttributeError, TypeError, ValueError):
                pass
        return 80

    def _make_rich_console(self) -> Any:
        try:
            from rich.console import Console
        except ImportError:
            return None

        return Console(
            file=self.stream,
            force_terminal=self.color_enabled or None,
            no_color=not self.color_enabled,
            highlight=False,
            markup=False,
            soft_wrap=True,
        )

    def print(self, text: str = "", *, style: str | None = None) -> None:
        if self._console is not None:
            self._console.print(text, style=style, markup=False, highlight=False, soft_wrap=True)
            return
        if text:
            self.stream.write(f"{text}\n")
        else:
            self.stream.write("\n")
        self.stream.flush()

    def write_fragment(self, text: str) -> None:
        """Write a streamed fragment without adding a newline or host ANSI."""
        if not text:
            return
        if self._console is not None:
            self._console.print(
                text,
                end="",
                markup=False,
                highlight=False,
                soft_wrap=True,
            )
            return
        self.stream.write(text)
        self.stream.flush()

    def prompt(self, text: str) -> None:
        """Print an input prompt without adding an extra newline."""
        if self._console is not None:
            self._console.print(text, end="", markup=False, highlight=False, soft_wrap=True)
            self.stream.flush()
            return
        self.stream.write(text)
        self.stream.flush()

    def panel(self, title: str, text: str, *, style: str | None = None) -> None:
        """Render a Rich panel when possible, otherwise an ASCII bordered block."""
        if self._console is not None and self.color_enabled:
            try:
                from rich.panel import Panel

                self._console.print(
                    Panel(text, title=title, style=style or "none", padding=(0, 1)),
                    highlight=False,
                    markup=False,
                )
                return
            except (ImportError, TypeError, ValueError):
                pass
        lines = text.splitlines() or [""]
        width = max(len(title) + 4, max(len(line) for line in lines) + 2, 20)
        self.print(f"+-{title}-{'-' * max(0, width - len(title) - 4)}+")
        for line in lines:
            self.print(f"| {line.ljust(width - 2)} |")
        self.print(f"+{'-' * width}+")

    def run_progress(self, stages: list[tuple[int, str]]) -> None:
        """Animate fixed fictional installation stages on capable terminals."""
        if not stages:
            return
        if not (self.is_tty and self.color_enabled and not self.low_stimulation and self._console):
            for percent, label in stages:
                self.print(f"{percent:>3}%  {label}")
            return

        try:
            from rich.progress import BarColumn, Progress, TextColumn
        except ImportError:
            for percent, label in stages:
                self.print(f"{percent:>3}%  {label}")
            return

        progress = Progress(
            TextColumn("[bold red]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3}%"),
            console=self._console,
            transient=False,
        )
        with progress:
            task = progress.add_task(stages[0][1], total=100)
            for percent, label in stages:
                progress.update(task, completed=percent, description=label)
                time.sleep(0.12)
            time.sleep(0.8)

    def clear(self) -> None:
        """Clear only this display. No host terminal command is executed."""
        if not self.color_enabled or self.low_stimulation:
            return
        self.stream.write("\x1b[2J\x1b[H")
        self.stream.flush()
