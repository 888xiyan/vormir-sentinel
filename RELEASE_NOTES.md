# Vormir Sentinel 0.6.0 Release Notes

Vormir Sentinel is a local, fictional AI terminal experience where a ghost changes the perceived machine without compromising the real one.

## Phase Two

This release completes the second-stage startup and Agent experience:

- Read-only loopback Ollama discovery with installed-model metadata.
- Interactive GPU, CPU, custom-model, download-command, and offline selection.
- `--pick-model` and `--list-models` controls.
- RedSkoll installation progress, 99% metamorphosis, and Agent-page transition.
- RedSkoll Agent status page with conversation history.
- Fixed Slash commands for model management, status, story, context, relics, reconstruction, tribute, safety, and exit.
- POSIX virtual commands and safe exits remain compatible.
- Plain-text, offline, safe, non-TTY, and narrow-terminal fallback.

## Install

```bash
python -m pip install vormir_sentinel-0.6.0-py3-none-any.whl
ollama serve
ollama pull qwen2.5:7b-instruct-q4_K_M
vormir-sentinel --pick-model
```

## Safety

No background model download, arbitrary host command execution, real filesystem exploration, remote inference, credential collection, or conversation upload is implemented.

`/download` only prints a command for the user to run. Model names are validated strings sent only to loopback Ollama. `/clear` clears only Agent conversation history.

## Verification

- 90 automated tests passed at completion of Phase Two.
- Ruff, mypy, puzzle asset verification, and package build checks passed.
- README, CHANGELOG, release notes, and version metadata aligned to `0.6.0`.

## Known limitations

- Ollama is optional. Without a local loopback dialogue model, the program uses fixed offline character responses.
- Windows and macOS manual acceptance remain required before a v1.0 tag.
