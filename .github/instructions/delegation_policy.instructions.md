---
description: "Policy for delegating work to specialized agents while preserving repository contracts."
---

# Delegation Policy

## Purpose

Use this when splitting work across specialized LLM agents or reviewing work
produced by another agent.

## Rules

- Every delegated agent must treat `AGENTS.md` as the base repository contract.
- Delegate self-contained work with clear inputs, expected outputs, and
  verification requirements.
- Do not ask one agent to make assumptions that another agent must later guess.
- Keep domain-heavy satellite, weather, forecasting, trading-signal, and
  backtest work with SafEnergy-aware agents and review-heavy work with
  read-only reviewers.
- Parallelize independent exploration, review, and test-design tasks when the
  harness supports it.
- Synthesize delegated results before editing; do not blindly apply patches.
- Verify merged or adopted work in the current session before claiming it works.

## Good Delegation Targets

- Mapping an unfamiliar data provider, feature contract, model target, or
  backtest method.
- Reviewing a risky diff for timestamp, leakage, CRS, baseline, numerical,
  market-signal, or test regressions.
- Designing deterministic tests for a known forecasting or backtest behavior.
- Checking docs against actual commands and project layout.

## Poor Delegation Targets

- Tasks that require hidden user intent.
- Broad refactors without a narrow contract.
- External service actions, paid data pulls, live trading, or publishing steps.
- Anything that would make an agent invent provider credentials, market data, or
  satellite access it does not have.
