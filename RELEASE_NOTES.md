# Vormir Sentinel 0.5.0 Release Notes

Vormir Sentinel is a local, fictional AI terminal experience inspired by a ghost that changes the machine without compromising it.

## Included

- Safe Python CLI with `vormir-sentinel` and `python -m vormir_sentinel` entry points.
- Rich and plain-text terminal presentation with Readline completion.
- Fixed virtual filesystem and whitelisted POSIX/Windows command interception.
- Loopback-only Ollama streaming with GPU, CPU, emergency, and offline profiles.
- Inspectable Stonekeeper System Prompt and role-drift post-processing.
- Four-act story director, boot metamorphosis, Ctrl+C responses, and fictional takeover alarms.
- Atomic JSON story state, five symbolic tribute types, Death Echoes, and fragment reconstruction.
- Harmless Polyglot, Brainfuck, Whitespace, deed, and resurrection artifacts.
- `--status`, `--export-state`, `--reconstruct`, `--clean`, `--forget`, `--safe`, and `--offline` controls.

## Install

```bash
python -m pip install vormir_sentinel-0.5.0-py3-none-any.whl
vormir-sentinel --safe
```

## Safety

No arbitrary host command execution, real filesystem exploration, remote networking, credential collection, or conversation upload is implemented. Generated files stay in a relative approved output directory and can be removed with `--clean`.

## Known limitations

- Ollama is optional. Without a local loopback model, the program uses fixed offline character responses.
- The current development machine may not have the Qwen GPU/CPU profiles installed; `gpu_emergency` is available when DeepSeek is installed.
- Three-platform manual acceptance is still required before a v1.0 tag.
