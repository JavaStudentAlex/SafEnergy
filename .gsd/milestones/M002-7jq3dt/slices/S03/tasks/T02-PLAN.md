---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T02: Persist provenance in storage layer

Extend DuckDB or storage serialization so forecast inputs, outputs, and signals can store and reload provenance metadata without losing UTC timestamp or CRS information.

## Inputs

- `src/safenergy/core/provenance.py`
- `src/safenergy/storage/client.py`

## Expected Output

- `src/safenergy/storage/client.py`
- `tests/test_storage.py`

## Verification

uv run pytest tests/test_storage.py tests/core/test_provenance.py -q

## Observability Impact

Adds artifact-level provenance summaries for later debugging and API responses.
