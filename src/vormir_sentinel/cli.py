"""Command-line entry point for Vormir Sentinel."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO, cast

from vormir_sentinel import __version__
from vormir_sentinel.commands import CommandRouter
from vormir_sentinel.config import Config, ConfigError, apply_cli_overrides, load_config
from vormir_sentinel.console import Display
from vormir_sentinel.death_echoes import DeathEchoManager, EchoError
from vormir_sentinel.dialogue import DialogueEngine, OfflineDialogueEngine, StreamingDialogueEngine
from vormir_sentinel.model_policy import (
    ModelCatalog,
    ModelPolicyError,
    ModelProfile,
    RunMode,
)
from vormir_sentinel.ollama import OllamaClient, OllamaError
from vormir_sentinel.relics import RelicError, RelicGenerator
from vormir_sentinel.repl import InputFunction, Repl
from vormir_sentinel.state import StateStore
from vormir_sentinel.story import StoryDirector
from vormir_sentinel.tributes import TributeManager

SAFETY_EPILOG = """
safety:
  Virtual commands are interpreted by a fixed whitelist and never execute a host shell.
  Model dialogue is limited to loopback Ollama; remote networking, real filesystem
  exploration, and conversation upload are forbidden.
  Always available exits: 'exit --now', Ctrl+C twice, or closing the terminal window.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vormir-sentinel",
        description="Enter a local fictional terminal haunted by the Stonekeeper.",
        epilog=SAFETY_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "gpu", "cpu", "offline"),
        help="select automatic, GPU, CPU, or fixed offline character dialogue",
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="enable directly controlled offline, low-stimulation mode",
    )
    parser.add_argument(
        "--offline",
        "--story-only",
        dest="offline",
        action="store_true",
        help="forbid loopback inference and use fixed story behavior",
    )
    parser.add_argument(
        "--low-stimulation",
        action="store_true",
        help="disable clear-screen effects and other high-intensity presentation",
    )
    parser.add_argument(
        "--no-color",
        "--plain",
        dest="no_color",
        action="store_true",
        help="disable ANSI color and use plain-text presentation",
    )
    parser.add_argument(
        "--config",
        type=Path,
        metavar="PATH",
        help="load an alternate TOML configuration file",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="show local story progress and exit",
    )
    parser.add_argument(
        "--reconstruct",
        action="store_true",
        help="inspect recorded Death Echo fragments without incrementing them",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove only generated artifacts and local state",
    )
    parser.add_argument(
        "--forget",
        action="store_true",
        help="remove local story state while leaving artifacts untouched",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _requested_mode(args: argparse.Namespace, parser: argparse.ArgumentParser) -> RunMode:
    if args.offline and args.mode not in {None, "offline"}:
        parser.error("--offline cannot be combined with a model mode")
    if args.safe or args.offline or args.mode == "offline":
        return "offline"
    if args.mode in {"auto", "gpu", "cpu"}:
        return cast(RunMode, args.mode)
    return "auto"


def create_dialogue_engine(
    config: Config,
    mode: RunMode,
) -> DialogueEngine:
    """Create a safe local character engine, degrading to offline behavior."""
    if mode == "offline":
        return OfflineDialogueEngine(reason="offline mode requested")
    if not config.safety.allow_local_inference:
        return OfflineDialogueEngine(reason="local inference disabled by configuration")

    try:
        catalog = ModelCatalog.load()
    except ModelPolicyError as exc:
        return OfflineDialogueEngine(reason=f"invalid model catalog: {exc}")

    try:
        client = OllamaClient(config.llm.base_url)
        installed = client.list_models()
    except (OllamaError, OSError):
        return OfflineDialogueEngine(reason="loopback Ollama service unavailable")

    candidates = catalog.candidates(mode)
    installed_profiles = tuple(
        profile for profile in candidates if not profile.is_offline and profile.model in installed
    )
    if not installed_profiles:
        return OfflineDialogueEngine(reason="selected dialogue model is not installed")

    ordered: list[ModelProfile] = [*installed_profiles, catalog.offline_profile]
    return StreamingDialogueEngine(client, tuple(dict.fromkeys(ordered)))


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    input_function: InputFunction | None = None,
    state_store: StateStore | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    output = stdout or sys.stdout
    error = stderr or sys.stderr
    input_stream = stdin or sys.stdin

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        error.write(f"vormir-sentinel: {exc}\n")
        return 2

    mode = _requested_mode(args, parser)
    config = apply_cli_overrides(
        config,
        safe_mode=args.safe,
        low_stimulation=args.low_stimulation,
        offline=mode == "offline",
    )

    display = Display(
        output,
        color=False if args.no_color else None,
        low_stimulation=config.app.low_stimulation,
    )
    store = state_store or StateStore()
    progress = store.load()
    try:
        relics = RelicGenerator(config.output.workspace)
    except RelicError as exc:
        error.write(f"vormir-sentinel: {exc}\n")
        return 2

    if args.clean:
        state_removed = store.clean()
        artifact_removed = relics.clean()
        removed = []
        if state_removed:
            removed.append("state")
        if artifact_removed:
            removed.append("generated artifacts")
        display.print("Clean complete. Removed: " + (", ".join(removed) if removed else "nothing"))
        return 0
    if args.forget:
        forgotten = "local story state" if store.forget() else "nothing"
        display.print(f"Forget complete. Removed: {forgotten}")
        return 0
    if args.reconstruct:
        try:
            display.print(DeathEchoManager().reconstruct(progress))
        except EchoError as exc:
            error.write(f"vormir-sentinel: {exc}\n")
            return 2
        return 0
    if args.status:
        display.print(
            f"Act: {progress.act}\n"
            f"Cleared: {str(progress.cleared).lower()}\n"
            f"Tributes: {progress.tribute_count}/5\n"
            f"Death Echoes: {progress.echo_count}/6\n"
            f"Fragments: {', '.join(progress.fragments_seen) or 'none'}\n"
            f"State file: {store.path}\n"
            f"Output directory: {relics.output_root}"
        )
        return 0

    dialogue = create_dialogue_engine(config, mode)
    router = CommandRouter(config)
    director = StoryDirector(config)
    repl = Repl(
        display,
        router,
        input_function=input_function,
        stdin=input_stream,
        safe_mode=config.app.safe_mode,
        dialogue=dialogue,
        director=director,
        progress=progress,
        state_store=store,
        tributes=TributeManager(),
        echoes=DeathEchoManager(),
        relics=relics,
    )
    return repl.run()


def entrypoint() -> None:
    raise SystemExit(main())
