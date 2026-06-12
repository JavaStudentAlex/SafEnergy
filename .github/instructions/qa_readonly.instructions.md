---
description: "Read-only review overlay for analysis, QA, and code review tasks."
---

# Read-Only QA Instructions

## Purpose

Use this when the task is to inspect, review, audit, or explain without making
changes.

## Rules

- Do not edit files unless the user explicitly changes the task to
  implementation.
- Ground findings in repository evidence: files, tests, commands, and observed
  behavior.
- Distinguish confirmed issues from hypotheses.
- Prioritize findings by severity and likelihood.
- Call out missing verification and untested behavior explicitly.
- For SafEnergy concerns, name the affected convention: issue time, valid time,
  forecast horizon, timezone, CRS, spatial footprint, provider provenance,
  target leakage, baseline, signal threshold, market data, or output path.
- Avoid broad style commentary unless it creates a maintainability or
  correctness risk.

## Output Shape

Prefer:

1. Findings ordered by severity.
2. Evidence and affected path for each finding.
3. Suggested fix or next verification step.
4. Open questions or limitations.

If no issues are found, state what was reviewed and what verification was or was
not performed.
