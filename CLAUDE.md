# CLAUDE.md

@AGENTS.md

The file above is the repository-local contract for this project. Load it first.

For code-writing, review, or refactor tasks, also load:

- `.github/instructions/code_writing_behavior.instructions.md`

For renewable generation forecasting, satellite/weather features, geospatial
data, solar/wind nowcasts, forecast deltas, trading signals, or backtests, also
load:

- `.github/instructions/python_renewable_forecasting.instructions.md`

For test changes or verification work, also load:

- `.github/instructions/tests.instructions.md`
- `.github/instructions/python_quality_gates.instructions.md`

For read-only analysis or review tasks, also load:

- `.github/instructions/qa_readonly.instructions.md`

## Tooling Rules

- Use `rtk` for shell commands, per `AGENTS.md`.
- Use `uv run ...` for Python execution and dependency-managed commands.
- Use `uv sync --group dev` to install the runtime and development toolchain.
- Use Ruff through `uv run ruff ...`; do not introduce alternate formatters or
  linters unless the project changes.
- Prefer targeted checks for the touched package, script, or subsystem before
  running broader gates.

## Completion Rule

Before finishing, re-check that:

- the reported verification actually ran in the current session
- any remaining external API, credentials, data availability, temporal split,
  leakage, geospatial, or market-data caveats are named explicitly
- docs and agent files stay aligned with SafEnergy's satellite-enhanced
  renewable forecasting and forecast-to-trade stack
