# Release Checklist

## Automated gates

- [ ] `ruff check .`
- [ ] `ruff format --check .`
- [ ] `mypy src/vormir_sentinel`
- [ ] `pytest -q`
- [ ] `python tools/verify_relics.py`
- [ ] `python -m build`
- [ ] Wheel contains `vormir_sentinel/assets/` and `assets/templates/`.

## Manual acceptance

- [ ] Linux first launch, second launch, `--safe`, and `--offline`.
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
