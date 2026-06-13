# Codebase Map

Generated: 2026-06-13T21:50:51Z | Files: 114 | Described: 0/114
<!-- gsd:codebase-meta {"generatedAt":"2026-06-13T21:50:51Z","fingerprint":"cf938de0aca52e35d00ce19856242438882ebe51","fileCount":114,"truncated":false} -->

### (root)/
- `.env.example`
- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `GEMINI.md`
- `plan.md`
- `pyproject.toml`
- `README.md`
- `run_dashboard.py`
- `skills-lock.json`

### .github/
- `.github/PULL_REQUEST_TEMPLATE.md`

### .github/agents/
- `.github/agents/code-reviewer.agent.md`
- `.github/agents/docs-maintainer.agent.md`
- `.github/agents/renewable-forecasting-engineer.agent.md`
- `.github/agents/satellite-weather-data-engineer.agent.md`
- `.github/agents/test-engineer.agent.md`
- `.github/agents/trading-backtest-engineer.agent.md`

### .github/instructions/
- `.github/instructions/agent_maintenance_workflow.instructions.md`
- `.github/instructions/code_writing_behavior.instructions.md`
- `.github/instructions/delegation_policy.instructions.md`
- `.github/instructions/python_quality_gates.instructions.md`
- `.github/instructions/python_renewable_forecasting.instructions.md`
- `.github/instructions/qa_readonly.instructions.md`
- `.github/instructions/tests.instructions.md`

### .github/skills/forecast-contract-check/
- `.github/skills/forecast-contract-check/SKILL.md`

### .github/skills/python-linting/
- `.github/skills/python-linting/SKILL.md`

### .github/skills/python-testing/
- `.github/skills/python-testing/SKILL.md`

### .github/workflows/
- `.github/workflows/ci-lint.yml`
- `.github/workflows/ci-tests.yml`
- `.github/workflows/jules_automerge.yml`
- `.github/workflows/jules_next_task.yml`

### docs/
- `docs/CONFIGURATION.md`
- `docs/demo.md`
- `docs/forecast_contract.md`
- `docs/no_training_forecast.md`

### scripts/
- `scripts/market_forecast_smoke.py`
- `scripts/smoke_check.py`

### src/safenergy/
- `src/safenergy/__init__.py`

### src/safenergy/api/
- `src/safenergy/api/__init__.py`
- `src/safenergy/api/dashboard.py`
- `src/safenergy/api/main.py`
- `src/safenergy/api/routes.py`
- `src/safenergy/api/schemas.py`

### src/safenergy/commitment/
- `src/safenergy/commitment/__init__.py`
- `src/safenergy/commitment/engine.py`
- `src/safenergy/commitment/ledger.py`

### src/safenergy/core/
- `src/safenergy/core/__init__.py`
- `src/safenergy/core/config.py`
- `src/safenergy/core/paths.py`

### src/safenergy/features/
- `src/safenergy/features/__init__.py`
- `src/safenergy/features/alignment.py`
- `src/safenergy/features/engineering.py`
- `src/safenergy/features/satellite.py`

### src/safenergy/forecast/
- `src/safenergy/forecast/__init__.py`
- `src/safenergy/forecast/baselines.py`
- `src/safenergy/forecast/evaluate.py`
- `src/safenergy/forecast/models.py`
- `src/safenergy/forecast/selector.py`
- `src/safenergy/forecast/service.py`

### src/safenergy/health/
- `src/safenergy/health/__init__.py`
- `src/safenergy/health/diagnostics.py`

### src/safenergy/ingest/
- `src/safenergy/ingest/__init__.py`
- `src/safenergy/ingest/market.py`
- `src/safenergy/ingest/plants.py`
- `src/safenergy/ingest/satellite.py`
- `src/safenergy/ingest/weather.py`

### src/safenergy/orchestrator/
- `src/safenergy/orchestrator/__init__.py`
- `src/safenergy/orchestrator/pipeline.py`

### src/safenergy/signals/
- `src/safenergy/signals/__init__.py`
- `src/safenergy/signals/backtest.py`
- `src/safenergy/signals/explanation.py`
- `src/safenergy/signals/market.py`
- `src/safenergy/signals/objects.py`
- `src/safenergy/signals/pipeline.py`
- `src/safenergy/signals/thresholds.py`

### src/safenergy/storage/
- `src/safenergy/storage/__init__.py`
- `src/safenergy/storage/client.py`

### tests/
- *(26 files: 26 .py)*

### tests/api/
- `tests/api/test_ledger.py`

### tests/core/
- `tests/core/test_config.py`

### tests/features/
- `tests/features/test_satellite_features.py`

### tests/fixtures/market/
- `tests/fixtures/market/delu_prices.csv`
- `tests/fixtures/market/generation.csv`
- `tests/fixtures/market/prices.csv`

### tests/fixtures/satellite/
- `tests/fixtures/satellite/sample_discovery.json`

### tests/ingest/
- `tests/ingest/test_market.py`
- `tests/ingest/test_plants.py`
- `tests/ingest/test_satellite.py`
- `tests/ingest/test_weather.py`
