# media-extract-skill

Project facts for coding agents and contributors.

Agent skill for media metadata, captions, local transcription, and still frames. `SKILL.md` is the skill entry point.

## Layout

- `SKILL.md`: skill definition. `references/`: material the skill loads on demand.
- `scripts/`: helpers plus `documentation.py` docs checker. `tests/`: pytest suites.

## Verify

Matches CI (`.github/workflows/`):

- `pip install pytest`
- `python -m compileall scripts tests`
- `python scripts/documentation.py --check`
- `python -m pytest tests/ -q`

## Docs

- Facts and known gaps: [`docs/KB.md`](docs/KB.md). Update it in the same change when a documented fact changes.

## Issues and PRs

Issue forms in `.github/ISSUE_TEMPLATE/` apply the `bug`, `feature`, and `chore` labels.
