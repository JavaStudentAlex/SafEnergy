---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T04: Document dashboard backend run modes

Update demo documentation with commands for running FastAPI and Streamlit, how dashboard backend mode is selected, and what live, cached, fixture, and unavailable labels mean.

## Inputs

- `docs/demo.md`
- `docs/CONFIGURATION.md`
- `src/safenergy/api/dashboard.py`

## Expected Output

- `docs/demo.md`
- `docs/CONFIGURATION.md`

## Verification

uv run pytest tests/test_dashboard.py -q && uv run ruff check src/safenergy/api/dashboard.py tests/test_dashboard.py

## Observability Impact

Reduces ambiguity for future demos and handoffs.
