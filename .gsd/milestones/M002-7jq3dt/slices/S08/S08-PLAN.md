# S08: API Hardening and Root Documentation

**Goal:** Close judge and maintainer readiness gaps: harden API error surfaces, make CORS and request validation explicit, and add a root README that matches actual behavior.
**Demo:** A fresh user can read the root README, configure optional providers, run tests, start API and dashboard demos, and see safe API errors without raw exception leakage.

## Must-Haves

- Broad raw exception responses are replaced or wrapped with safe structured errors.
- CORS and environment-driven API settings are documented and tested.
- Root README explains current scope, live versus fixture data, setup, tests, demo commands, and no-live-trading boundary.
- Documentation matches verified commands.

## Proof Level

- This slice proves: API tests, ruff, pytest, and documentation path checks.

## Integration Closure

Milestone outputs are discoverable by judges, teammates, and future agents from the repository root.

## Verification

- Adds safe error codes, request IDs or diagnostic IDs where practical, and documented runbook cues.

## Tasks

- [ ] **T01: Replace raw API exception leakage** `est:0.75d`
  Audit FastAPI route error handling and replace raw exception-string responses with safe structured errors that include error code, phase or endpoint, diagnostic ID where practical, and user-safe message.
  - Files: `src/safenergy/api/main.py`, `src/safenergy/api/routes.py`, `src/safenergy/api/schemas.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/test_api.py -q

- [ ] **T02: Make CORS and request validation explicit** `est:0.5d`
  Move CORS settings and geospatial request validation into explicit configuration and tests. Default local demo behavior can remain permissive only if documented as local-only.
  - Files: `src/safenergy/core/config.py`, `src/safenergy/api/main.py`, `src/safenergy/api/schemas.py`, `tests/core/test_config.py`, `tests/test_api.py`
  - Verify: uv run pytest tests/core/test_config.py tests/test_api.py -q

- [ ] **T03: Create root README** `est:0.5d`
  Add a repository-root README that explains SafEnergy scope, architecture, live versus fixture modes, setup with uv, tests, API and dashboard run commands, optional credentials, known limitations, and no-live-trading boundary.
  - Files: `README.md`, `docs/demo.md`, `docs/CONFIGURATION.md`, `SafEnergy_Implementation_Verdict.md`
  - Verify: test -f README.md && uv run ruff check .

- [ ] **T04: Final documentation and quality gate pass** `est:0.5d`
  Align README, demo docs, configuration docs, and forecast contract with actual commands and implemented live or fixture modes. Run full lint and test gates before closing the milestone.
  - Files: `README.md`, `docs/demo.md`, `docs/CONFIGURATION.md`, `docs/forecast_contract.md`
  - Verify: uv run ruff check . && uv run pytest tests -q

## Files Likely Touched

- src/safenergy/api/main.py
- src/safenergy/api/routes.py
- src/safenergy/api/schemas.py
- tests/test_api.py
- src/safenergy/core/config.py
- tests/core/test_config.py
- README.md
- docs/demo.md
- docs/CONFIGURATION.md
- SafEnergy_Implementation_Verdict.md
- docs/forecast_contract.md
