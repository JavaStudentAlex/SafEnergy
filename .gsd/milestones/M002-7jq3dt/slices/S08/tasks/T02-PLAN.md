---
estimated_steps: 1
estimated_files: 5
skills_used: []
---

# T02: Make CORS and request validation explicit

Move CORS settings and geospatial request validation into explicit configuration and tests. Default local demo behavior can remain permissive only if documented as local-only.

## Inputs

- `src/safenergy/core/config.py`
- `src/safenergy/api/main.py`
- `src/safenergy/api/schemas.py`

## Expected Output

- `src/safenergy/core/config.py`
- `src/safenergy/api/main.py`
- `tests/core/test_config.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/core/test_config.py tests/test_api.py -q

## Observability Impact

Adds explicit environment-driven API safety settings and validation failures.
