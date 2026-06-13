---
estimated_steps: 1
estimated_files: 4
skills_used: []
---

# T03: Create root README

Add a repository-root README that explains SafEnergy scope, architecture, live versus fixture modes, setup with uv, tests, API and dashboard run commands, optional credentials, known limitations, and no-live-trading boundary.

## Inputs

- `SafEnergy_Implementation_Verdict.md`
- `docs/demo.md`
- `docs/CONFIGURATION.md`

## Expected Output

- `README.md`

## Verification

test -f README.md && uv run ruff check .

## Observability Impact

Gives judges, teammates, and agents an accurate entry point and operational runbook.
