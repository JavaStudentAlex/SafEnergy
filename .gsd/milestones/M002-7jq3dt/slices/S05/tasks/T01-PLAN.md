---
estimated_steps: 1
estimated_files: 3
skills_used: []
---

# T01: Design orchestration phase model

Define typed phase inputs and outputs for provider retrieval, feature construction, forecast serving, baseline comparison, signal generation, explanation, storage, and response assembly. Keep orchestration separate from route handlers.

## Inputs

- `src/safenergy/signals/pipeline.py`
- `src/safenergy/forecast/models.py`
- `src/safenergy/storage/client.py`

## Expected Output

- `src/safenergy/pipeline.py`
- `tests/test_pipeline.py`

## Verification

uv run pytest tests/test_pipeline.py -q

## Observability Impact

Adds phase names, status enum, artifact references, and diagnostic payload shape.
