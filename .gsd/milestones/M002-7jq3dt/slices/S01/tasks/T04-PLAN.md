---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T04: Document satellite availability modes

Document live, cached, fixture, and unavailable satellite modes, including which environment variables enable live discovery and what deterministic tests prove without credentials.

## Inputs

- `src/safenergy/core/config.py`
- `src/safenergy/ingest/satellite.py`

## Expected Output

- `docs/CONFIGURATION.md`
- `docs/forecast_contract.md`

## Verification

uv run ruff check src/safenergy/ingest/satellite.py src/safenergy/features/satellite.py tests/ingest/test_satellite.py tests/features/test_satellite_features.py && uv run pytest tests/ingest/test_satellite.py tests/features/test_satellite_features.py -q

## Observability Impact

Makes provider availability and fallback behavior visible to future operators and agents.
