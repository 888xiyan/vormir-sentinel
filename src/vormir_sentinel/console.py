"""Terminal presentation with graceful Rich and ANSI fallbacks."""

from __future__ import annotations

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

    def clear(self) -> None:
        """Clear only this display. No host terminal command is executed."""
        if not self.color_enabled or self.low_stimulation:
            return
        self.stream.write("\x1b[2J\x1b[H")
        self.stream.flush()
