---
id: TASK-141
title: Create AGENTS.md guidance document for future coding agents
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-08 13:00'
updated_date: '2026-09-08 13:03'
labels: []
dependencies: []
priority: high
type: docs
ordinal: 151000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Analyze repository manifests, configs, architecture, and constraints to generate a concise, high-signal AGENTS.md under 250 lines.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Inspect manifests, configs, and directory structure
- [x] #2 Document exact verification commands for build, test, lint, and format
- [x] #3 Document architectural guardrails, data flow, and directory boundaries
- [x] #4 Document anti-patterns, negative rules, and internal-only/no backwards-compatibility policy
- [x] #5 Include truncated source tree and update instructions
- [x] #6 Verify AGENTS.md is strictly under 250 lines without generic platitudes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect repository manifests, config files, build/test scripts, and directory structures.
2. Identify architecture, data flow, layering invariants, anti-patterns, and internal-only policies.
3. Draft concise, high-signal AGENTS.md strictly under 250 lines with source tree and commands.
4. Write AGENTS.md and verify all commands and constraints.
5. Complete acceptance criteria and definition of done in backlog.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Analyzed repository structure, conda environment, parC framework bindings, and module boundaries. Authored concise, high-signal AGENTS.md (145 lines, strictly under 250 line limit) containing exact verification/execution commands, architectural guardrails, anti-patterns, internal-only no-backward-compatibility policy, and a truncated 2-level directory tree with update instructions. All commands tested and verified against active parC environment.
<!-- SECTION:FINAL_SUMMARY:END -->
