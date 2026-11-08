# Final requirements review — Problem 1

The six-page original brief is the authority for submission requirements. This review distinguishes implementation checks from editorial quality and from actions the applicant must complete. Latest verification: `deliverables/final_verification.json`.

| Requirement | Evidence and status |
|---|---|
| Choose one problem and explain framing/assumptions | Problem 1; solution PDF describes the editor's shortlist, source timing assumptions and limits. |
| Process all 50 episodes | Fresh offline run: 50 episodes, 3,727 beats; matches saved shortlisted cuts, scores and decisions. |
| 20–60s promos with exact source segments | All 282 emitted candidates pass structural validation; 64 shortlisted. Every endpoint matches source, duration arithmetic is checked, dialogue stays whole and footage is not reused in overlapping mashup segments. |
| Hook in first 3s, unresolved ending, standalone conflict | Deterministic retrieval plus optional structured AI critique. Timing/continuity uncertainties affect recommendations; an editor must judge actual footage. These semantic conditions are not proven by timestamp tests. |
| Continuous and joined moments | Singles and two-segment intra/cross-episode mashups implemented; automatic three-segment search is not implemented or required by the original “few moments” wording. |
| Ranked outputs with hook, cliffhanger, one-line why and posting rationale | Full JSON, CSV and report include these fields. Heuristic ordering is preserved; AI findings and diagnostic scores stay separate and uncalibrated. |
| Explain where the tool picks badly | Audit includes real failures; eleven curated development regressions pass. E21 rescue resolution before a Duchess subplot is a concrete rejected arc. |
| Rerun on fresh input, easy model swapping | TXT/ZIP uploads, synthetic demo, manual episode ranges and picker; three provider REST adapters and editable model IDs/key fields. Contracts are mocked; provider availability and successful live inference are not asserted. |
| Code, AI and editor responsibilities | Shared editorial policy separates hard errors, heuristic concerns, AI findings and categorical uncertainty. AI requires valid source beat references and never changes cuts. |
| Practical editor workflow | Three leading recommendations, source timeline, two-candidate comparison, session-persistent scoped decisions with import/export, independent editor shortlist; script and footage approvals remain distinct. |
| Scale and cost | Bounded top-plus-borderline AI sample, usage telemetry and editable economics. Saved offline API usage is zero; live token scenarios and latency are estimates, not invoices or campaign measurements. |
| AI tool and specific error disclosed | Codex assistance and the erroneous “hang” substring match in “cliffhanger” are disclosed. |
| Solution document | Two readable PDF pages generated from source script; final browser rendering verifies no footer overlap. |
| Openable prototype | Deployed Streamlit URL supplied by applicant; local UI tested; see final report for live check result. Runnable GitHub repository is a brief-approved fallback. |
| Unedited full-pack outputs | Four primary files plus manifests and development review; historical snapshots preserved. Current raw hashes verified. |
| Human evaluation | Frozen 24-case sample includes shortlisted/borderline/rejected cuts. Genuine human labels pending; no fabricated precision, pairwise agreement, recall or campaign lift. Not a mandatory blocker in the brief. |
| Confidentiality | Original input folder/ZIP excluded from bundle and Git. Public repository and derived outputs contain selected screenplay quotations; sharing review remains necessary. Do not claim the public results are fully sanitized. |
| Personal form submission | Applicant must enter name/roll/branch, confirm deadline, verify link permissions and submit through the placement-cell form. |
| Optional walkthrough | Up to 3 minutes, applicant's own voice; guide provided, recording not created. |

## Readiness judgment

The core prototype and required artifacts are sufficient for a defensible submission. This is not a claim of exhaustive retrieval, perfect editorial choices, secure infrastructure certification or successful live provider inference. Complete the link/access and confidentiality checks in `FINAL_SUBMISSION_GUIDE.md`, then submit. A model API success is optional; the brief explicitly permits a free smaller implementation and a rerunnable repository.

## Six-point editorial audit follow-up

121 tests passed. Coverage is 38/50 episodes, including 58 singles and 6 mashups; final singles are capped at three per episode. New regressions cover benign/violent chain and heat contexts, routine/forced kneeling, filler/substantive endings, scene-pivot rejection, speaker-label themes and model presets. E25/E32 development labels were revised because their old endpoints are now explicitly prohibited; no independent human labels were manufactured.
