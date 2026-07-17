---
id: TASK-53
title: Implement insertion macro system to replace hand-coded insertion rules
status: Done
assignee:
  - '@agent'
created_date: '2026-07-17 15:47'
updated_date: '2026-07-17 15:55'
labels: []
dependencies: []
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace hand-coded Phonology/Rules/wi.yaml and Phonology/Rules/di.yaml in min-min-config with a new insertion macro system. Instead of hand-writing rule YAML files, users write insert_*.csv files (with metadata + columns tag,rule_name,l_context,r_context,content) and a new generator (generate_insertion_rules.py) produces the Rules/*.yaml automatically. This avoids the epsilon-insertion + cyclic FST problem by keeping tags in the open-root template and using only tag-substitution rules (never epsilon insertion). The new system is demonstrated in a new min-min-insertion-config/ directory with corresponding min-min-insertion-generated/ output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create min-min-insertion-config/ as a copy of min-min-config with old Phonology/Rules/wi.yaml and di.yaml removed
- [x] #2 Integrate generate_insertion_rules.py call into generate_markers.py pipeline (called before Rules files are needed)
- [x] #3 Tests pass for both min-min-generated and min-min-insertion-generated
- [x] #4 Create insert_wi.csv with metadata (# kind: insertion, # rule: insert_WI) and columns tag,rule_name,l_context,r_context,content
- [x] #5 Create insert_di.csv with metadata (# kind: insertion, # rule: insert_DIST) and columns tag,rule_name,l_context,r_context,content
- [x] #6 Generated YAML has: named sub-rules using rule_name column, string_map: [[tag, content]], optional l_context/r_context (omitted if blank), and a top-level rule_sequence named after the # rule: metadata value
- [x] #7 Create parc_macros/generate_insertion_rules.py that reads insert_*.csv files and generates Rules/insert_*.yaml in the generated dir
- [x] #8 Extend tests/test_prefix_template.py to also test min-min-insertion-generated/ with same surface/tag assertions (watata->[WI], tatata->[DIST], witata->[WI][DIST])
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented insertion macro system. Created min-min-insertion-config/ as a copy of min-min-config/ with wi.yaml and di.yaml removed from Phonology/Rules/. Added insertions/ subfolder containing insert_wi.csv and insert_di.csv with metadata headers (# kind: insertion, # rule: ...) and columns tag,rule_name,l_context,r_context,content. Created parc_macros/generate_insertion_rules.py which reads insert_*.csv files and generates Phonology/Rules/insert_*.yaml in the output directory; each CSV row becomes a named sub-rule (string_map + optional l/r_context), with a top-level rule_sequence appended using the # rule: metadata. Hooked generate_insertion_rules() into generate_markers.py main() immediately after the Phonology copy step. Added tests/test_insertion_template.py with the same watata/tatata/witata surface assertions against min-min-insertion-generated/. Both test_prefix_template.py and test_insertion_template.py pass.
<!-- SECTION:FINAL_SUMMARY:END -->
