#!/usr/bin/env python3
"""Verify the harmless Vormir puzzle assets."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
EXPECTED = "RETURN TO THE SOURCE. THE GHOST LIVES WHERE THE CODE IS OPEN."


def run_bf(source: str) -> str:
    tape = [0] * 30000
    ptr = 0
    pc = 0
    stack: list[int] = []
    jumps: dict[int, int] = {}
    for i, token in enumerate(source):
        if token == "[":
            stack.append(i)
        elif token == "]":
            if not stack:
                raise ValueError("unbalanced Brainfuck")
            start = stack.pop()
            jumps[start] = i
            jumps[i] = start
    if stack:
        raise ValueError("unbalanced Brainfuck")
    output: list[str] = []
    while pc < len(source):
        token = source[pc]
        if token == ">":
            ptr += 1
        elif token == "<":
            ptr -= 1
        elif token == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif token == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif token == ".":
            output.append(chr(tape[ptr]))
        elif (token == "[" and tape[ptr] == 0) or (token == "]" and tape[ptr] != 0):
            pc = jumps[pc]
        pc += 1
    return "".join(output)


def run_whitespace(source: str) -> str:
    tokens = [c for c in source if c in " \t\n"]
    i = 0
    output: list[str] = []

    def take() -> str:
        nonlocal i
        if i >= len(tokens):
            raise ValueError("unexpected Whitespace EOF")
        token = tokens[i]
        i += 1
        return token

    while i < len(tokens):
        imp = take()
        if imp == " ":  # stack manipulation
            command = take()
            if command != " ":
                raise ValueError("unsupported stack command")
            sign = take()
            bits = ""
            while True:
                token = take()
                if token == "\n":
                    break
                bits += "0" if token == " " else "1"
            value = int(bits or "0", 2)
            if sign == "\t":
                value = -value
            tape = globals().setdefault("_ws_stack", [])
            tape.append(value)
        elif imp == "\t":  # I/O
            first, second = take(), take()
            if (first, second) != ("\n", " "):
                raise ValueError("unsupported I/O command")
            third = take()
            if third != " ":
                raise ValueError("unsupported I/O command")
            output.append(chr(globals()["_ws_stack"].pop()))
        elif imp == "\n":  # flow
            first, second = take(), take()
            if (first, second) != ("\n", "\n"):
                raise ValueError("unsupported flow command")
            break
    return "".join(output)


def main() -> None:
    death = json.loads((CONTENT / "death_echoes.json").read_text(encoding="utf-8"))
    assert death["concatenated_fragments"] == EXPECTED

    bf = (CONTENT / "polyglot_relic.bf").read_text(encoding="ascii")
    assert run_bf(bf) == EXPECTED

    ws = (CONTENT / "whitespace_relic.ws").read_text(encoding="ascii")
    assert run_whitespace(ws) == EXPECTED

    python_run = subprocess.run(
        [sys.executable, str(CONTENT / "polyglot_relic.txt")],
        check=True,
        capture_output=True,
        text=True,
    )
    assert python_run.stdout.strip() == "RETURN TO THE SOURCE."

    polyglot = (CONTENT / "polyglot_relic.txt").read_text(encoding="utf-8")
    if os.name == "nt":
        # Git Bash is not guaranteed on Windows CI; the source is still audited.
        assert "THE GHOST LIVES WHERE THE CODE IS OPEN." in polyglot
    else:
        shell_run = subprocess.run(
            ["bash", str(CONTENT / "polyglot_relic.txt")],
            check=True,
            capture_output=True,
            text=True,
        )
        assert shell_run.stdout.strip() == "THE GHOST LIVES WHERE THE CODE IS OPEN."

    incantations = json.loads(
        (CONTENT / "resurrection_incantations.json").read_text(encoding="utf-8")
    )
    assert incantations["count"] == len(incantations["items"]) == 72

    for name in ("polyglot_relic.bf", "whitespace_relic.ws"):
        digest = hashlib.sha256((CONTENT / name).read_bytes()).hexdigest()
        assert digest in (CONTENT / "polyglot_relic.txt").read_text(encoding="utf-8")

    print("Death Echoes: OK")
    print("Brainfuck:    OK")
    print("Whitespace:   OK")
    print("Polyglot:     OK")
    print("Incantations: OK (72)")


if __name__ == "__main__":
    main()
