# Changelog

All notable changes to Vormir Sentinel are documented here.

## [0.5.0] - 2026-10-28

### Added

- Executable `vormir-sentinel` CLI and `python -m vormir_sentinel` entry point.
- Safe TOML runtime configuration with loopback-only Ollama inference.
- Rich presentation, plain-text mode, Readline completion, and virtual filesystem commands.
- GPU/CPU/offline model selection with automatic degradation.
- Inspectable Stonekeeper System Prompt and role-drift post-processing.
- Four-act story director, boot metamorphosis, fictional takeover, and Ctrl+C responses.
- Atomic local story state, symbolic tributes, Death Echoes, and fragment reconstruction.
- Harmless Polyglot, Brainfuck, Whitespace, deed, and resurrection artifacts.
- `--status`, `--reconstruct`, `--clean`, `--forget`, `--safe`, and `--offline` controls.
- Cross-platform CI matrix for Linux, Windows, and macOS.

### Safety

- No arbitrary host command execution, real filesystem exploration, or remote networking.
- Generated artifacts are limited to an approved relative output directory.
- Remote Ollama endpoints, proxies, and redirects are rejected.
