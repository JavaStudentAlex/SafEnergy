---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T02: Display provenance and data mode clearly

Update dashboard panels to show whether a result used live, cached, fixture, or unavailable provider data, plus provenance summaries, uncertainty, and model or baseline mode.

## Inputs

- `src/safenergy/api/dashboard.py`

## Expected Output

- `src/safenergy/api/dashboard.py`
- `tests/test_dashboard.py`

## Verification

uv run pytest tests/test_dashboard.py -q

## Observability Impact

Makes user-facing data lineage and provider availability explicit.
