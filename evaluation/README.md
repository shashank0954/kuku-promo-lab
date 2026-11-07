# Frozen editorial evaluation

`frozen_cases.json` contains 24 candidates frozen from the prior output before policy changes. Its source hash and deterministic selection method are recorded inside. Includes shortlisted, borderline and rejected windows. It is a small, deliberately stratified convenience sample; it is not a random show-wide estimate or an unseen benchmark. The existing eleven cases remain development regressions.

Have a real editor inspect all selected source tracks, opening timing, human conflict, endpoint and context. Copy `human_labels_blank.csv`; enter `yes`/`no` in `human_accept`, reviewer attribution and notes. In a copy of `pairwise_labels_blank.csv`, enter the preferred candidate ID or `tie`. Do not use AI labels as independent human judgments.

Run from the repository with the confidential input pack restored:

```sh
python scripts/evaluate_frozen.py
python scripts/evaluate_frozen.py --labels /path/human_labels.csv --pairs /path/pairs.csv --attest-human
```

Without labels, status is pending and metrics are null. Precision is human accepts divided by predicted accepts among labeled cases. Pairwise agreement uses labeled non-tied pairs only. Missing labels are excluded; denominators are exported. No recall is estimated because no exhaustive reference set exists. Human authenticity requires honest attribution; code cannot authenticate a reviewer. Keep completed labeling sheets private and separate from raw pipeline outputs.
