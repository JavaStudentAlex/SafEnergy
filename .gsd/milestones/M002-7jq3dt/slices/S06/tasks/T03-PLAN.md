---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T03: Add unavailable state UI path

Add dashboard behavior for missing credentials, provider outage, missing model artifact, and stale data so the UI explains the issue instead of implying live results are available.

## Inputs

- `src/safenergy/api/dashboard.py`

## Expected Output

- `src/safenergy/api/dashboard.py`
- `tests/test_dashboard.py`

## Verification

uv run pytest tests/test_dashboard.py -q

## Observability Impact

Creates visible failure-mode copy and diagnostic status for demo operators.
