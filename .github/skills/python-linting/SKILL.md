---
name: python-linting
description: Run Python linting checks for SafEnergy using uv and Ruff. Use when editing package modules, scripts, tests, or repository Python tooling.
---

# Python Linting Skill

## Scope

- Package modules under `src/`, when present
- Scripts under `scripts/`, when present
- Application modules under `app/`, when present
- Tests under `tests/`, when present
- Configuration source of truth: `pyproject.toml` and
  `.github/workflows/ci-lint.yml`

All commands should go through `uv`.

## Quality Gates

```bash
uv run ruff check .
```

After dependency changes:

```bash
uv lock --check
```

## Current Formatting Policy

The current repository is a scaffold with Ruff linting configured. Do not add a
new formatter or linter unless the project configuration and CI are updated
together.

## Guardrails

- Do not change runtime behavior solely to satisfy linting unless the lint issue
  exposes a real bug.
- Re-run the relevant check after fixes.
- Pair linting with targeted pytest or a deterministic smoke check when the
  change affects behavior.
