# Vormir Sentinel

**A local fictional AI terminal where a ghost changes the machine without compromising it.**

Vormir Sentinel pairs an open-weight local model with a four-act story, a safe virtual terminal, and the RedSkoll Agent page. It never executes host commands, downloads models in the background, or uploads conversations.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) for local model dialogue
- A supported GPU/CPU model, or use offline mode

Vormir Sentinel contacts only loopback Ollama (`127.0.0.1`, `localhost`, or `::1`). Remote inference and external networking are rejected.

## Install Ollama

Install Ollama using its official instructions, then start the local service yourself:

```bash
ollama serve
```

Vormir Sentinel only prints this command when needed. It never starts Ollama automatically.

## Download a model

Choose the profile that matches your machine:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull qwen2.5:3b-instruct-q4_K_M
```

The first command is recommended for capable GPUs. The second is the safer CPU fallback. Vormir Sentinel never runs `ollama pull` for you.

## Install Vormir Sentinel

From a checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -e .
```

## Start the terminal

Automatic discovery and selection:

```bash
vormir-sentinel
```

Choose a model interactively:

```bash
vormir-sentinel --pick-model
```

Inspect installed local models without starting the story:

```bash
vormir-sentinel --list-models
```

Force a mode:

```bash
vormir-sentinel --mode gpu
vormir-sentinel --mode cpu
vormir-sentinel --offline
```

Safe and plain-text variants:

```bash
vormir-sentinel --safe
vormir-sentinel --plain
```

The equivalent module entry point is:

```bash
python -m vormir_sentinel
```

## Model modes

| Mode | Behavior |
|---|---|
| `auto` | Discover loopback Ollama and select an installed recommended model |
| `gpu` | Prefer the configured GPU model; fall back safely if unavailable |
| `cpu` | Prefer the configured CPU model; fall back safely if unavailable |
| `offline` | Use fixed story responses and make no Ollama request |
| `custom` | Select another installed dialogue model from `--pick-model` or `/model select` |

Embedding models are listed for inspection but are not selectable for dialogue.

## Slash commands

The RedSkoll Agent page routes `/` commands through fixed JSON scripts:

```text
/help
/model
/model list
/model select NAME
/download MODEL
/offline
/status
/story
/context
/clear
/relic
/reconstruct
/tribute
/safe
/exit
```

Examples:

```text
/model list
/download qwen2.5:7b-instruct-q4_K_M
/model select deepseek-r1:7b
```

`/download` only prints `ollama pull <model>`. It does not download or execute anything.

Existing virtual POSIX commands such as `ls`, `cat`, `whoami`, `uname`, and `pwd` remain available.

## Safety

- No arbitrary host shell execution.
- No real filesystem exploration.
- No background model downloads.
- No remote inference or conversation upload.
- No modification of shell profiles, registry, startup items, or system files.
- Symbolic sacrifices never request real credentials or delete real files.
- Generated artifacts stay in a relative approved output directory.

Always-available exits:

```text
/exit
exit --now
Ctrl+C twice
close the terminal window
```

The RedSkoll transition always includes:

```text
[fictional takeover only; no host command was executed]
```

## Troubleshooting

**`Ollama is not running`**

Start it yourself:

```bash
ollama serve
```

**`No local dialogue model was found`**

Download a recommended model:

```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama pull qwen2.5:3b-instruct-q4_K_M
```

**Model is too large or the machine is under memory pressure**

Use the CPU profile or offline mode:

```bash
vormir-sentinel --mode cpu
vormir-sentinel --offline
```

**Need a directly controlled, low-stimulation session**

```bash
vormir-sentinel --safe
```

**Need to inspect or clean local state**

```bash
vormir-sentinel --status
vormir-sentinel --export-state
vormir-sentinel --forget
vormir-sentinel --clean
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
mypy src/vormir_sentinel
pytest -q
python tools/verify_relics.py
python -m build
```

The test suite covers startup discovery, model selection, Agent-page fallback, fixed slash commands, safety boundaries, story transitions, state, puzzles, and streaming.

## Documentation

- [完整方案（中文）](./Vormir_Sentinel_完整方案.md)
- [第二阶段计划](./docs/phase2-plan.md)
- [项目管理文档](./PROJECT_MANAGEMENT.md)
- [模型选型](./docs/model-selection.md)
- [发布检查清单](./docs/release-checklist.md)
- [Windows 人工验收工单](./docs/windows-manual-acceptance.md)
- [变更记录](./CHANGELOG.md)

## License

MIT. See [LICENSE](./LICENSE).

This is an original, unofficial fictional homage. It does not use official film assets, logos, music, or copied extended dialogue.
