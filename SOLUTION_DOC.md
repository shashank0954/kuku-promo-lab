# Kuku Promo Lab — Problem 1

Problem: help editors choose defensible 20–60s cold-viewer promos. Script timing is authoritative; dialogue stays whole; current mashups contain two segments. No footage or campaign performance is available.

## Architecture and editorial policy
Code parses 50 episodes / 3727 beats and validates exact cuts, duration, dialogue and overlap. These are structural checks, not proof of editorial quality. AI optionally critiques opening, conflict, unresolved ending, answers already supplied, missing context and continuity with validated selected beat IDs. Unsupported references reject the batch; AI never changes cuts. The budget includes deterministic top and borderline candidates.

Heuristic scores only determine ordering: recommended script candidates before review-required, then heuristic composite. AI assessments can veto or require review; AI scores remain separate, uncalibrated diagnostics.

Uncertainty is categorical: supported by script timing; uncertain within a long source beat; requires continuity review; insufficient evidence. Review needs accompany recommendations. Editors compare candidates, record separate script/footage decisions and export an independent selected shortlist. Script review never grants footage approval.

## Actual output and posting order
64 shortlisted; 282/282 structurally valid emitted candidates. First cuts: E3 00:08.80–00:40.40; E46 01:16.80–01:40.40; E3 01:24.00–01:52.50. Prioritize timing-supported, understandable conflict before review-required bridges. No measured ad lift.

## Quality evidence and failure
11/11 curated development regressions pass; these are not independent quality labels. A frozen 24-case diverse sample includes rejected and borderline windows. Human labeling is pending human labels; acceptance precision and pairwise agreement remain unreported until genuine labels exist. No recall claim. E9 00:40.80–01:27.40 cures the child before a new-scene greeting and is rejected. Filler questions, benign chains/heat and routine kneeling no longer qualify as dramatic signals. Coverage is 38/50, with a three-single-per-episode cap. AI-assisted development once misread hang inside cliffhanger; source review and word boundaries corrected that rule.

## Scale and economics
Offline measured API usage: zero calls, zero tokens, $0. Local elapsed 1.083s. Eight finalists with 14,400 input / 1,280 output tokens at historical $0.30/$2.50 per million estimate $0.00752/show; live structured critiques can use more output. Editable assumptions, not measured live prices or bills. Independent show workers scale under quotas; footage review remains manual. No successful live inference verified. Codex assisted implementation, tests and documentation; provider tests use mocks.
