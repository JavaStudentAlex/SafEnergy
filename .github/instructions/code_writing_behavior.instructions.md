---
description: "Behavioral overlay for code writing, review, and refactor tasks."
---

# Code Writing Behavior

## Purpose

This file defines the expected engineering behavior for day-to-day work in this
repository.

Use it when a task involves:

- writing or editing code
- reviewing code
- refactoring or cleanup work
- changing data contracts, forecasting logic, trading signals, APIs, or CI

## Core Behavior

- Make assumptions explicit when project behavior, provider data shape,
  timestamp handling, geospatial footprint, forecast horizon, baseline, trading
  signal, output path, or public API behavior affects the result.
- Prefer the smallest correct change. Do not add speculative abstractions.
- Keep edits surgical and grounded in the current scaffold or existing package
  layout.
- Match local style and existing patterns unless a scoped instruction says
  otherwise.
- If you notice unrelated issues, call them out separately instead of widening
  the change set.
- Preserve public entry points and data contracts unless a task explicitly
  requires a breaking change.
- Keep deterministic transformations separate from network calls, file I/O,
  model training, plotting, API routes, and scheduling concerns.

## Execution Pattern

Before implementing:

- state working assumptions when they materially affect the solution
- identify the simplest viable approach
- define what will verify success

During implementation:

- touch only the files and code paths needed for the task
- remove imports or helpers made unused by your own changes
- preserve any existing test seams and deterministic fixtures
- keep ad hoc debugging separate from reusable logic whenever possible
- avoid hardcoded local paths, credentials, site IDs, market names, dataset
  locations, or machine-specific settings

Before completion:

- verify the claimed outcome with the lightest sufficient evidence
- report open questions, external-data constraints, forecast assumptions,
  leakage risks, market-data caveats, or blocked gates explicitly

## Stack-Specific Work

- For renewable forecasting, satellite/weather data, geospatial processing,
  generation models, trading signals, or backtests, load
  `.github/instructions/python_renewable_forecasting.instructions.md`.
- For tests or verification work, load `.github/instructions/tests.instructions.md`
  and `.github/instructions/python_quality_gates.instructions.md`.
