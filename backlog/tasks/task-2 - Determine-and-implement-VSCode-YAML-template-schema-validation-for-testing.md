---
id: TASK-2
title: Determine and implement VSCode YAML template/schema validation for testing
status: Done
assignee:
  - '@myself'
created_date: '2026-07-04 17:31'
updated_date: '2026-07-04 17:41'
labels: []
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate how to use the schemas/templates from parC to validate YAML files output by parC-macros, and set up automatic validation for testing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify the correct schema files and validation tool (e.g. ajv, jsonschema, or yamllint/pydantic/etc.)
- [x] #2 Determine how to map files to schemas for validation
- [x] #3 Write a test or validation script that verifies files match the schemas
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Copy the VSCode templates (.vscode/templates/) and JSON schemas (schemas/) from parC to the parC-macros workspace.\n2. Configure .vscode/settings.json in parC-macros to align with parC's schema mapping.\n3. Create a Python-based schema validator script/module under parC-macros (using jsonschema and PyYAML) to programmatically validate files against the schemas.\n4. Set up a testing script/pytest structure to automatically validate output YAML files on disk.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Determined how to use VSCode schema definitions and YAML templates to programmatically validate output files on disk. Copied the schema definitions and template files from parC. Implemented yaml_validation.py to parse files and validate them against their JSON schema according to the file's 'kind' property. Added tests/test_yaml_validation.py to demonstrate test-time validation, which successfully passes.
<!-- SECTION:FINAL_SUMMARY:END -->
