---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T03: Expose provenance summaries in API schemas

Add compact API schema fields for provenance, quality flags, source mode, and diagnostics. Keep detailed raw provider payloads out of public responses.

## Inputs

- `src/safenergy/core/provenance.py`
- `src/safenergy/api/schemas.py`

## Expected Output

- `src/safenergy/api/schemas.py`
- `tests/test_api.py`

## Verification

uv run pytest tests/test_api.py tests/core/test_provenance.py -q

## Observability Impact

Makes response-level data lineage visible while avoiding raw provider payload leakage.
