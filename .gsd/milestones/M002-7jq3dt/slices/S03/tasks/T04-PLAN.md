---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T04: Verify timezone and CRS contracts

Add focused tests for UTC normalization, issue-time versus valid-time distinction, CRS serialization, and footprint round trips across provenance, storage, and API schemas.

## Inputs

- `src/safenergy/core/provenance.py`

## Expected Output

- `tests/core/test_provenance.py`

## Verification

uv run pytest tests/core/test_provenance.py tests/test_storage.py tests/test_api.py -q

## Observability Impact

Prevents silent provenance corruption that would undermine live-data claims.
