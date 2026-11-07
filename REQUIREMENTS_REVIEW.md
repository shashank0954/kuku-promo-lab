# Assignment recheck — Problem 1

This review follows the actual six-page Kuku brief. It separates mandatory submission requirements from extra implementation features. It does not claim that valid timestamps prove great advertising.

## Required work and evidence

| Actual requirement | Result | Evidence / practical limit |
|---|---|---|
| Choose one problem and explain why | Complete | Problem 1 only. Solution PDF explains the editor's shortlisting problem and the scope. |
| Read the full supplied input pack | Complete | 50 episodes / 3,727 original source beats parsed. Every episode appears in coverage, including those with no surviving cut. |
| Find 20–60-second promos | Structurally verified; editorial review remains | Latest run: 64 shortlisted promos, 231 retained rejections. All 295 emitted candidates pass duration/source-boundary checks. Surviving cuts are recommendations, not certified ad winners. |
| Episode and every segment's start/end in playback order | Complete | JSON, full CSV, Markdown report and UI expose exact verbatim source timestamps; mashups preserve their listed order. |
| First-three-second hook | Implemented, with uncertainty disclosed | Signals are restricted to opening onsets. Full dialogue is preserved. Long visual/spoken beats are flagged because scripts do not provide word/action-level timing. Source footage is needed for final approval. |
| Unresolved ending | Implemented, with semantic limits disclosed | Final spoken line is used instead of an earlier question already answered. Music-only endings, detected de-escalation and a cured-child-to-Duchess pivot are rejected. Rhetorical questions can still fool heuristics. |
| Cold-viewer standalone clarity | Implemented; not a formal guarantee | Relationship/role clues and lore penalties; ambiguous threat-object and victim-changing mashup checks. Book visuals are considered alongside dialogue. Human review still matters. |
| Hook, cliffhanger, one line explaining why it works | Complete | Each cut carries specific opening/ending evidence and a candidate-specific explanation. The prior repeated generic explanation was replaced. |
| Rank promos and explain which to post first | Complete | Composite `rank` plus explicit `posting_priority` and `posting_reason`. Dashboard defaults to posting order; full CSV/report preserve both. Clear singles precede uncertain openings and trailer bridges. |
| Show where the tool picks badly | Complete | Generated failure audit plus 11 deliberately selected script regressions. Examples include watch chains, burning ambition, slow openings and a resolved illness pivot. This is not an independent accuracy benchmark. |
| Rerun on a new input | Verified | TXT/ZIP loading and a fresh original synthetic Episode 101. AppTest proves the saved 50-episode result is replaced with a newly computed one-episode result. |
| Make models easy to swap | Implemented; paid live run unverified | Gemini / OpenAI / Anthropic, editable model ID and session key, API connection test, actual provider endpoint/body display, labeled fallback. No valid replacement key was supplied for paid live testing. |
| Explain code vs AI and scale/cost | Complete | Solution PDF and calculator expose filtering, bounded AI budget, measured offline time, usage counters and editable rate/latency scenarios. Historical rate assumptions are not current-model quotes. |
| Explain assumptions, AI tools and an actual AI mistake | Complete | Solution PDF covers timestamp authority, script-only limitations, Codex assistance, and the `hang` / `cliffhanger` false match. |
| Solution document: PDF, up to two pages | Complete | `SOLUTION_DOC.pdf` is generated and checked as exactly two pages, with complete ending text on both pages. Markdown/HTML sources accompany it. |
| Openable prototype link | Repository available; hosted URL needs separate check | Public GitHub repository with run steps is an explicitly permitted prototype format. Deployed Streamlit URL was not supplied for live-site inspection. Local clean-install HTTP startup is checked separately. |
| Unedited raw outputs on full input pack | Complete | `raw_outputs/` contains the actual full-pack JSON, complete CSV, report and failure audit; hashes verify the files. They are not manually rewritten examples. |
| Walkthrough in your own voice, up to three minutes | Optional; not recorded | `INTERVIEW_GUIDE.md` gives a demonstration sequence. A video is recommended by Kuku, not mandatory. |

## Fixes made during this recheck

- Decorative watch chains, wounded pride, burning ambition and a hot forehead no longer receive automatic physical-attack hook scores.
- The true opening beat is quoted; a pre-cut overlapping description cannot stand in for it.
- An earlier question is not scored as the final cliffhanger after a later spoken answer.
- Explicit same-speaker ellipsis continuations are joined so an edit cannot split their boundary/gap.
- A cured-child clip pivoting to another victim's illness is rejected rather than called an unresolved rescue.
- Trailer near-duplicates sharing the same two start points are reduced.
- Explanations and posting reasons are specific to the selected source evidence; posting tiers are recomputed after AI scores change.
- Weights are normalized in run metadata as well as scoring.
- Scoring source is visible per promo; partial AI judging is not presented as full-show AI evaluation.
- API connection tests and placeholder-key request contracts are accessible before uploading scripts. Invalid JSON still retains reported token usage for honest accounting.
- Multiple ZIP uploads share a combined expanded-size/file-count limit, and changing upload bytes marks results stale until rerun.
- An original public sample allows interview reruns without bundling confidential source scripts.
- Runtime dependencies are pinned after testing a clean install, rather than relying on the machine's older global packages.
- A real submission PDF replaces the earlier print-only HTML/Markdown deliverable.

## Verification performed

- Full-pack offline run: **50 episodes; 64 shortlisted / 231 rejected; 295/295 hard checks passed**.
- **56 automated tests passed** in a clean Python 3.11 environment using Streamlit 1.67.0, pandas 2.3.3 and pytest 9.2.0.
- Source beat coverage, overlap preservation, whole-dialogue boundaries, ellipsis joins, tampered timestamps/durations and reproducible offline promo outputs are tested.
- Eleven selected script-review regressions match expected shortlist/reject decisions. The cases were used during development, so 11/11 is not a general quality claim.
- Provider request/response contracts, invalid judge output, token accounting and the API connection-test UI are mocked; no paid API success is invented.
- All four tabs, model/key controls, a fresh sample run and cloud startup without the original screenplay folder are exercised.
- Primary output row counts, timestamp references, file checksums and PDF page count are checked.
- Deployment package is tested after extraction without confidential input files; source integration tests skip explicitly there.

## Submission boundaries and remaining actions

1. **Live API:** Use a valid replacement key in Test API connection, then analyze a sample with AI budget one. Verify `judged_candidates > 0`, nonzero reported usage and no errors. Exposed chat keys are not used by the agent.
2. **Live site:** Check the actual Streamlit URL in incognito. The repository itself satisfies the brief's alternate prototype format, but an unprovided hosted URL cannot be certified.
3. **Editorial approval:** Verify the first three seconds, unresolved cut and mashup causality against source footage before posting. No real campaign metrics were available.
4. **Access and confidentiality:** Original screenplays, original input archives, assignment PDF and credentials are excluded from tracked deployment files. The public repository was made public at the user's explicit request. Generated outputs and solution examples contain selected show quotations; share them within the intended reviewer audience. No visibility change or Git history rewrite was made during this audit.
5. **Personal submission:** Submit the form with your own name/roll/branch, Problem 1, PDF link, prototype link and raw-output folder link. Learn the explanation in the interview guide. The optional own-voice video remains your task.

Not required by this assignment: a separate REST endpoint for the whole pipeline, video rendering, music or text overlays, paid inference, or a specific model. The extra dashboard/calculator features are useful only insofar as they support the required editorial result.

## Manual episode scope

The app now lets users upload the full pack once and select a subset by numbers/ranges or a picker. Selection is enforced before candidate retrieval and AI judging, not just in the leaderboard. Run metadata records loaded count and selected episode numbers. Invalid selections never trigger a pipeline run. Explicitly chosen distant episodes may form compatible two-part mashups; the default full-show search retains the original nearby-episode limit. Tests cover valid/invalid ranges, source isolation, distant-episode matching, switching subsets without reuploading and the episode picker.

## Visual submission review

The submission PDF has been redesigned as two visual A4 pages with actual posting cards, a code/AI/editor architecture diagram, rubric weights, exact source timeline and concrete failure examples. Both pages fit above their footers and are verified as exactly two PDF pages. SVG assets and a self-contained searchable playbook derive from the saved JSON; `deliverables/visual_source.json` identifies that snapshot. Presentation files have their own checksum manifest and do not modify the raw outputs. The repository now opens with required-deliverable links, page previews and a real offline app capture. No fictional video frames or campaign results are presented. The current app also shows the source hook/cliffhanger timeline. All 56 tests pass after those UI changes. Public-clone run instructions launch the saved-results app without requiring the excluded original pack.

## Editorial policy revision (current implementation)

- Structural constraints remain deterministic and independent from editorial recommendation. `src/editorial_policy.py` is shared by pipeline, evaluator and development review.
- Six AI assessments require source beat IDs; unsupported references discard the batch. Opening/ending evidence must overlap their proper windows. Semantic truth of a valid reference still needs an editor.
- Ranking preserves heuristic scores. AI diagnostics are displayed separately; supported AI concerns may veto. Long-beat onset, missing evidence and mashup continuity create categorical review needs, never invented confidence percentages.
- UI leads with three cuts, offers two-candidate comparison and scoped decisions, separates script from footage approval, and exports editor selections independently.
- Frozen sample: 24 cases, including borderline/rejected; genuine human labels pending. Acceptance precision and pairwise agreement are undefined until labels arrive. No recall claim. Eleven cases remain development regressions.
- History is preserved before regeneration. No live inference or campaign outcomes are asserted. Structured AI critiques can exceed the old 160-output-token scenario; the calculator is an estimate, not measured cost.
