"""Whitelisted fictional command routing.

No module in this file imports subprocess, os.system, or any other host-execution
API. Unknown commands remain inside the fictional interface.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field

from vormir_sentinel.config import Config
from vormir_sentinel.virtual_fs import VirtualFileSystem, VirtualPathError

WINDOWS_COMMANDS = frozenset(
    {
        "cmd",
        "cmd.exe",
        "copy",
        "del",
        "dir",
        "erase",
        "ipconfig",
        "move",
        "netstat",
        "powershell",
        "powershell.exe",
        "rd",
        "reg",
        "reg.exe",
        "rmdir",
        "schtasks",
        "systeminfo",
        "taskkill",
        "tasklist",
        "type",
        "xcopy",
    }
)

WHITELIST = frozenset(
    {
        "cat",
        "cd",
        "clear",
        "date",
        "defy",
        "df",
        "exit",
        "help",
        "history",
        "id",
        "ls",
        "pwd",
        "quit",
        "secret",
        "settings",
        "show",
        "tribute",
        "uname",
        "whoami",
    }
)

VIRTUAL_PROMPT_USER = "root"
VIRTUAL_PROMPT_HOST = "vormir"


@dataclass
class SessionState:
    cwd: str = "/"
    history: list[str] = field(default_factory=list)
    interrupt_count: int = 0


@dataclass(frozen=True)
class CommandOutcome:
    text: str = ""
    exit_requested: bool = False
    clear_screen: bool = False
    status: str = "ok"


class CommandRouter:
    def __init__(self, config: Config, filesystem: VirtualFileSystem | None = None) -> None:
        self.config = config
        self.filesystem = filesystem or VirtualFileSystem()

    @staticmethod
    def prompt(cwd: str) -> str:
        return f"{VIRTUAL_PROMPT_USER}@{VIRTUAL_PROMPT_HOST}:{cwd}# "

    def route(self, raw: str, state: SessionState) -> CommandOutcome:
        try:
            parts = shlex.split(raw, posix=True)
        except ValueError as exc:
            return CommandOutcome(
                text=f"The void rejects that broken quotation: {exc}",
                status="error",
            )

        if not parts:
            return CommandOutcome()

        command = parts[0]
        args = parts[1:]
        lowered = command.lower()

        if lowered in WINDOWS_COMMANDS:
            return self._windows_rejection(lowered)
        if lowered == "exit":
            return self._exit(args)
        if lowered == "quit":
            return CommandOutcome(
                text="The window closes. The keeper does not.", exit_requested=True
            )
        if lowered == "help":
            return self._help(args)
        if lowered == "whoami":
            return CommandOutcome("a sacrifice yet to be claimed")
        if lowered == "uname":
            return self._uname(args)
        if lowered == "pwd":
            return CommandOutcome(state.cwd)
        if lowered == "id":
            return CommandOutcome("uid=0(root) gid=0(soulkeepers) groups=hydra,vormir")
        if lowered == "date":
            return CommandOutcome("Vormir epoch 6.6.6-hydra // cycle 0000")
        if lowered == "df":
            return self._df(args)
        if lowered == "ls":
            return self._ls(args, state)
        if lowered == "cat":
            return self._cat(args, state)
        if lowered == "cd":
            return self._cd(args, state)
        if lowered == "history":
            return self._history(state)
        if lowered == "settings":
            return self._settings()
        if lowered == "clear":
            if args:
                return CommandOutcome("clear takes no arguments.", status="error")
            return CommandOutcome(clear_screen=True)
        if lowered == "show":
            return self._show(args)
        if lowered == "defy":
            return CommandOutcome(
                "Defiance is recognized. It has not granted you control of the host; "
                "only of this fiction."
            )
        if lowered == "tribute":
            return CommandOutcome(
                "The tribute altar accepts symbolic acts only; no real data is requested."
            )
        if lowered == "secret":
            return self._fictional_secret(args)

        return CommandOutcome(
            text=(
                f"'{command}' is not in the Vormir whitelist.\n"
                "Nothing was sent to the host. Type help to inspect the permitted words."
            ),
            status="unknown",
        )

    @staticmethod
    def _exit(args: list[str]) -> CommandOutcome:
        if args == ["--now"]:
            return CommandOutcome("Safe exit engaged. The process is ending.", exit_requested=True)
        if args:
            return CommandOutcome(
                "Only 'exit --now' is recognized as the force-exit form.",
                status="error",
            )
        return CommandOutcome("The keeper releases the terminal.", exit_requested=True)

    @staticmethod
    def _help(args: list[str]) -> CommandOutcome:
        if args:
            return CommandOutcome(
                "Help is a single command here. Type 'help' without arguments.",
                status="error",
            )
        return CommandOutcome(
            "Vormir Sentinel — fictional command surface\n"
            "\n"
            "Navigation:  pwd, ls [path], cd path, cat FILE\n"
            "Identity:    whoami, id, date, df -h, uname [-a], settings, history\n"
            "Story:       show relic, show fragments, tribute,\n"
            "             secret --fictional, defy\n"
            "Control:     clear, help, exit, exit --now\n"
            "\n"
            "This router has no host shell. Natural-language questions may reach the\n"
            "local character engine, but no input is ever executed on the host.\n"
            "Safe exits: type 'exit --now', press Ctrl+C twice, or close the window."
        )

    @staticmethod
    def _df(args: list[str]) -> CommandOutcome:
        if args and args != ["-h"]:
            return CommandOutcome("df recognizes only -h here.", status="error")
        return CommandOutcome(
            "Filesystem      Size  Used Avail Use% Mounted on\n"
            "soul-storage    6.6G  6.6G     0 100% /vormir"
        )

    @staticmethod
    def _uname(args: list[str]) -> CommandOutcome:
        if not args or args == ["-a"]:
            return CommandOutcome(
                "Linux vormir-soulkeeper 6.6.6-hydra-amd64 #1 SMP PREEMPT_DYNAMIC"
            )
        if args == ["-s"]:
            return CommandOutcome("Linux")
        if args == ["-n"]:
            return CommandOutcome("vormir-soulkeeper")
        if args == ["-r"]:
            return CommandOutcome("6.6.6-hydra-amd64")
        if args == ["-m"]:
            return CommandOutcome("x86_64")
        return CommandOutcome(
            "This fictional kernel recognizes -a, -s, -n, -r, and -m.", status="error"
        )

    def _ls(self, args: list[str], state: SessionState) -> CommandOutcome:
        flags = "".join(arg[1:] for arg in args if arg.startswith("-") and arg != "-")
        targets = [arg for arg in args if not arg.startswith("-")]
        if len(targets) > 1:
            return CommandOutcome("One fictional directory per invocation.", status="error")
        target = targets[0] if targets else "."
        try:
            entries = self.filesystem.list_directory(state.cwd, target)
        except VirtualPathError as exc:
            return CommandOutcome(str(exc), status="error")

        if not entries:
            return CommandOutcome("")
        if "l" in flags:
            rows = []
            for name, is_directory in entries:
                kind = "drwxr-xr-x" if is_directory else "-rw-r--r--"
                rows.append(f"{kind}  keeper  void  {name}")
            return CommandOutcome("\n".join(rows))
        names = [f"{name}/" if is_directory else name for name, is_directory in entries]
        return CommandOutcome("  ".join(names))

    def _cat(self, args: list[str], state: SessionState) -> CommandOutcome:
        if not args:
            return CommandOutcome("cat: missing fictional file", status="error")
        sections: list[str] = []
        for target in args:
            try:
                sections.append(self.filesystem.read_file(state.cwd, target).content.rstrip("\n"))
            except VirtualPathError as exc:
                return CommandOutcome(str(exc), status="error")
        return CommandOutcome("\n".join(sections))

    def _cd(self, args: list[str], state: SessionState) -> CommandOutcome:
        if len(args) > 1:
            return CommandOutcome("cd: one fictional path at a time", status="error")
        target = args[0] if args else "/"
        try:
            path = self.filesystem.resolve(state.cwd, target)
        except VirtualPathError as exc:
            return CommandOutcome(str(exc), status="error")
        if not self.filesystem.is_directory(path):
            return CommandOutcome(f"cd: not a fictional directory: {target}", status="error")
        state.cwd = path
        return CommandOutcome()

    @staticmethod
    def _history(state: SessionState) -> CommandOutcome:
        if not state.history:
            return CommandOutcome("No words have been offered to the keeper yet.")
        width = len(str(len(state.history)))
        rows = [f"{index:>{width}}  {line}" for index, line in enumerate(state.history, start=1)]
        return CommandOutcome("\n".join(rows))

    def _settings(self) -> CommandOutcome:
        mode = "SAFE" if self.config.app.safe_mode else "NARRATIVE"
        local_inference = "enabled" if self.config.safety.allow_local_inference else "disabled"
        return CommandOutcome(
            f"Interface mode: {mode}\n"
            f"Low stimulation: {str(self.config.app.low_stimulation).lower()}\n"
            f"Local loopback inference: {local_inference}\n"
            f"Remote networking: forbidden\n"
            f"Real command execution: forbidden\n"
            f"Real filesystem exploration: forbidden\n"
            f"Configured primary model: {self.config.llm.model}"
        )

    @staticmethod
    def _show(args: list[str]) -> CommandOutcome:
        if args == ["relic"]:
            return CommandOutcome(
                "The relic sleeps beneath the story. Its release belongs to a later threshold."
            )
        if args == ["fragments"]:
            return CommandOutcome(
                "No Death Echo has been recorded. Later launches will make fragments necessary."
            )
        return CommandOutcome("show accepts: relic, fragments", status="error")

    @staticmethod
    def _fictional_secret(args: list[str]) -> CommandOutcome:
        if args != ["--fictional"]:
            return CommandOutcome(
                "Use 'secret --fictional'. No password, token, or real private data is requested.",
                status="error",
            )
        return CommandOutcome(
            "Noted. The keeper accepts invented shadows only; no real secret has been requested."
        )

    @staticmethod
    def _windows_rejection(command: str) -> CommandOutcome:
        if command == "dir":
            return CommandOutcome(
                "Do not bring your fragile DOS legacy here.\nIn Vormir, we speak POSIX."
            )
        return CommandOutcome(
            f"Windows ritual '{command}' is recognized only as fiction.\n"
            "The host was not contacted, and nothing was executed."
        )
