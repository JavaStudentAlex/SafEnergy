# S07: Trading Backtest and Explanation Hardening

**Goal:** Make decision-support claims safer and more explainable without implying production trading performance.
**Demo:** Backtest and explanation outputs document transaction-cost assumptions, leakage controls, issue-time constraints, and attribution limits tied to real forecast features.

## Must-Haves

- Backtest inputs enforce forecast issue-time constraints.
- Outputs include assumptions for costs, slippage, delivery intervals, and market holidays even if defaulted.
- Explanation output can reference real feature provenance and clearly label heuristic attribution.
- Tests cover leakage guardrails and explanation metadata.

## Proof Level

- This slice proves: Unit tests and deterministic backtest fixture tests.

## Integration Closure

Signals, API, dashboard, and docs use honest backtest and explanation metadata.

## Verification

- Adds assumption metadata, leakage-check results, and attribution-source labels.

## Tasks

- [ ] **T01: Add backtest assumption model** `est:0.75d`
  Extend backtest inputs and outputs with transaction cost, fee, slippage, liquidity, position sizing, delivery interval, market holiday, and no-live-trading assumption fields. Defaults must be explicit, not hidden.
  - Files: `src/safenergy/signals/backtest.py`, `src/safenergy/signals/objects.py`, `tests/test_backtest.py`
  - Verify: uv run pytest tests/test_backtest.py tests/test_signals.py -q

- [ ] **T02: Enforce issue time leakage guards** `est:0.75d`
  Add validation that backtest records and feature rows do not use inputs with valid times unavailable at the forecast issue time. Fail with clear diagnostics when leakage is detected.
  - Files: `src/safenergy/signals/backtest.py`, `src/safenergy/features/alignment.py`, `tests/test_backtest.py`, `tests/test_features.py`
  - Verify: uv run pytest tests/test_backtest.py tests/test_features.py -q

- [ ] **T03: Add explanation attribution metadata** `est:0.5d`
  Extend explanations with attribution source labels such as heuristic, model feature importance, satellite feature provenance, or unavailable. Clearly state when SHAP or counterfactual attribution is not implemented.
  - Files: `src/safenergy/signals/explanation.py`, `tests/test_explanation.py`
  - Verify: uv run pytest tests/test_explanation.py -q

- [ ] **T04: Propagate honest trading metadata to API and dashboard** `est:0.5d`
  Expose backtest assumptions, leakage-check status, and explanation attribution labels in API and dashboard outputs so users understand the decision-support boundary.
  - Files: `src/safenergy/api/schemas.py`, `src/safenergy/api/routes.py`, `src/safenergy/api/dashboard.py`, `tests/test_api.py`, `tests/test_dashboard.py`
  - Verify: uv run pytest tests/test_api.py tests/test_dashboard.py tests/test_backtest.py tests/test_explanation.py -q

## Files Likely Touched

- src/safenergy/signals/backtest.py
- src/safenergy/signals/objects.py
- tests/test_backtest.py
- src/safenergy/features/alignment.py
- tests/test_features.py
- src/safenergy/signals/explanation.py
- tests/test_explanation.py
- src/safenergy/api/schemas.py
- src/safenergy/api/routes.py
- src/safenergy/api/dashboard.py
- tests/test_api.py
- tests/test_dashboard.py
