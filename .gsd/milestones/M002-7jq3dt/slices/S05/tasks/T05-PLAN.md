---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T05: Add end to end smoke check

Extend or add a deterministic smoke check that runs the orchestrator end to end using fixtures and confirms forecast, signal, explanation, storage artifact, and diagnostic fields are present.

## Inputs

- `scripts/smoke_check.py`
- `src/safenergy/pipeline.py`

## Expected Output

- `scripts/smoke_check.py`
- `tests/test_pipeline.py`

## Verification

uv run python scripts/smoke_check.py && uv run pytest tests/test_pipeline.py -q

## Observability Impact

Provides a single command that proves operational wiring and emits useful failure context.
