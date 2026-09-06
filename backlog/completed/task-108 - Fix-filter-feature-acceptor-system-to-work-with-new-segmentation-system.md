---
id: TASK-108
title: Fix "filter" "feature acceptor" system to work with new segmentation system
status: Done
assignee: []
created_date: '2026-09-03 13:38'
updated_date: '2026-09-03 15:03'
labels: []
dependencies:
  - TASK-106
ordinal: 113000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`[PrefixClass=a_stem][Pro=3sg.A][H_DROP]that`
We have prefix class that can't occur before consonant root but it is there.

Ideas:
1. Create acceptor FSTs that layer in and use potentially long range dependencies...
2. order elements so that restricting morphemes are segmentally _next to_ whatever they restrict
3. Create a complex input domain cascade that unions and intersects all the constraints.

Other idea, become less general
Prefix class restricts root start --> we union over [PrefixClass]MatchingStart
Aspect class selects root end --> we union over MatchingEnd[AspectClass]

We concat these two.

If possible we can create local acceptors that say "this prefix class must occur next to (or seperated by a Pro) from one of these phones"
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This issue is directly resolved by TASK-106 (compile_prefix_stem_shape_acceptor anchored at [PrefixClass=c]<Pro><H_ALT>?<PhoneConstraint>), which prunes combinations like [PrefixClass=a_stem]...that.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved by TASK-106 and TASK-107
<!-- SECTION:FINAL_SUMMARY:END -->
