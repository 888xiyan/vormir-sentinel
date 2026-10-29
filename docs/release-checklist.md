# Release Checklist

## Automated gates

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy src/vormir_sentinel`
- [ ] `pytest -q`
- [ ] `python tools/verify_relics.py`
- [ ] `python -m build`
- [ ] `python tools/release_check.py --wheel dist/vormir_sentinel-<version>-py3-none-any.whl`
- [ ] Wheel contains `vormir_sentinel/assets/` and `assets/templates/`.

## Phase Two acceptance

- [x] README shows Ollama prerequisite, model download commands, startup modes, and safe exits.
- [x] `--list-models` reads only loopback Ollama metadata.
- [x] `--pick-model` supports GPU, CPU, custom, download-command, and offline choices.
- [x] Installation progress reaches 99% and shows the fixed fictional metamorphosis text.
- [x] Full Agent page renders on capable TTY/color terminals.
- [x] Plain, safe, offline, non-TTY, and narrow-terminal modes use fallback presentation.
- [x] `/download` prints without executing or downloading.
- [x] POSIX virtual commands and all safe exits remain available.

## Manual acceptance

- [x] Linux first launch, second launch, `--safe`, and `--offline` — 2026-10-29.
- [ ] macOS first launch, second launch, `--safe`, and `--offline`.
- [ ] Windows first launch, second launch, `--safe`, and `--offline`.
- [ ] GPU model when available; CPU model when available; offline fallback otherwise.
- [ ] `Ctrl+C` twice always exits.
- [ ] `exit --now` and closing the window always exit.
- [ ] Five symbolic tributes clear the story without touching real files or credentials.
- [ ] Death Echoes advance at most once per day.
- [ ] `--reconstruct` does not increment Echo count.
- [ ] `--clean` removes only generated artifacts and local state.
- [ ] `--forget` removes state but preserves generated artifacts.
- [ ] Low-stimulation and plain-text modes contain no flashing or ANSI escape output.

## Release materials

- [ ] `CHANGELOG.md` matches the tagged version.
- [ ] README includes install, run, safety, cleanup, and offline instructions.
- [ ] Build hashes recorded.
- [ ] GitHub Release notes include known issues and third-party licenses.
