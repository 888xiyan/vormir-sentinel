# Changelog

All notable changes to Vormir Sentinel are documented here.

## [0.6.0] - 2026-10-29

### Added

- Read-only loopback Ollama discovery with model names, sizes, and update times.
- GPU, CPU, custom, download-command, and offline startup selection.
- `--pick-model` and `--list-models` startup controls.
- RedSkoll installation progress, 99% metamorphosis, and Agent-page transition.
- RedSkoll Agent status page with conversation history and safe plain-text fallback.
- Fixed-script Slash commands for model, download, status, story, context, clear, relic, reconstruction, tribute, safety, and exit.
- In-session switching between installed dialogue models.
- Startup, model metadata, Agent-page, and Slash-command test coverage.

### Changed

- README rewritten as a user-facing Ollama installation and startup guide.
- Story state now recognizes model selection, installation, metamorphosis, Agent page, and offline Agent page stages.
- Embedding models remain visible for inspection but cannot be selected for dialogue.

### Safety

- `/download` only prints `ollama pull <model>` and never executes it.
- Model names are validated before being printed or sent to loopback Ollama.
- `/clear` clears only the Agent conversation.
- No background downloads, remote inference, host command execution, or privacy upload was added.

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
- `--status`, `--export-state`, `--reconstruct`, `--clean`, `--forget`, `--safe`, and `--offline` controls.
- Cross-platform CI matrix for Linux, Windows, and macOS.

### Safety

- No arbitrary host command execution, real filesystem exploration, or remote networking.
- Generated artifacts are limited to an approved relative output directory.
- Remote Ollama endpoints, proxies, and redirects are rejected.
