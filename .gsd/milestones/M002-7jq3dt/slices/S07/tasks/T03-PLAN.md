---
estimated_steps: 1
estimated_files: 2
skills_used: []
---

# T03: Add explanation attribution metadata

Extend explanations with attribution source labels such as heuristic, model feature importance, satellite feature provenance, or unavailable. Clearly state when SHAP or counterfactual attribution is not implemented.

## Inputs

- `src/safenergy/signals/explanation.py`

## Expected Output

- `src/safenergy/signals/explanation.py`
- `tests/test_explanation.py`

## Verification

uv run pytest tests/test_explanation.py -q

## Observability Impact

Makes explanation confidence and attribution limitations visible.
