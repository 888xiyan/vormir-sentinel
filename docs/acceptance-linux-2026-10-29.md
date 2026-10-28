# Linux Release Acceptance — 2026-10-29

Environment:

- Python 3.12.13
- Linux host
- `vormir-sentinel 0.5.0` installed from the built wheel
- Isolated `XDG_DATA_HOME` and temporary output directory
- Offline mode, `--plain`, no Ollama connection

## Checks

| Check | Result |
|---|---|
| First launch bootstrap and `99%` metamorphosis | Pass |
| Second launch skips installation bait | Pass |
| `id`, `uname -a`, and Windows `dir` interception | Pass |
| Five symbolic tributes complete the story | Pass |
| Polyglot, Brainfuck, Whitespace, deed, and resurrection artifacts generated | Pass |
| `--status` reports cleared state and counts | Pass |
| `--clean` removes only state and generated artifacts | Pass |
| `exit --now` returns control | Pass |
| No ANSI escape output with `--plain` | Pass |
| Packaged assets readable outside the source checkout | Pass |

## Build hashes

```text
af83aaf0cb2cc03b5c58364bff0ea9e669b7e046633a06099d1010dd77aef6e7  vormir_sentinel-0.5.0-py3-none-any.whl
8cfa47a51ae08e80aab99797f366a8186f80186fa783597769b49afbef099166  vormir_sentinel-0.5.0.tar.gz
```

Windows and macOS manual acceptance remain required before the `v1.0` tag.
