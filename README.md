# Kuku · Find the Promos / Ads

A complete Problem 1 submission: deterministic screenplay parsing and safe edit points, signal-based candidate retrieval, a swappable AI critique layer, a Streamlit editorial workbench, and real outputs from all 50 episodes.

## Run

Python 3.11+ required (3.11 tested). From this directory:

```bash
pip install -r requirements.txt
python run_pipeline.py
streamlit run app.py
```

Open http://localhost:8501. The dashboard loads the saved playbook immediately; choose **Try a sample screenplay** for a fresh public demo input; **Find promos** reruns with the selected input and settings. Offline mode needs no account, API key, or network. Outputs are overwritten only by the CLI, never by dashboard runs.

For isolated installation, optionally run `python -m venv .venv` and activate it first. One-command end-to-end launch after Python setup:

```bash
pip install -r requirements.txt && python run_pipeline.py && streamlit run app.py
```

## Submission map

| File | Purpose |
|---|---|
| `SOLUTION_DOC.pdf` | Required submission PDF, verified at two pages; Markdown and HTML sources included |
| `src/parser.py` | Episode / scene / source beat objects; simultaneous audiovisual slices |
| `src/candidate_generator.py` | Hook and endpoint retrieval; diverse continuous cuts and two-part mashups |
| `src/llm_evaluator.py` | Five-score rubric; REST adapters for Gemini, OpenAI, Anthropic; explicit offline fallback |
| `src/quality_auditor.py` | Exact source-boundary and dialogue validation; actual weak-pick examples |
| `src/economics.py` | Editable token-cost arithmetic |
| `run_pipeline.py` | Reproducible orchestration and exports |
| `app.py` | Four-tab interview prototype; TXT / ZIP uploads, model swaps, timeline, audit, economics |
| `raw_outputs/` | Unedited generated JSON, CSV, report, failure audit, SHA-256 manifest |
| `tests/` | Source-losslessness, safety, regressions, deterministic runs, provider contracts, UI smoke test |

The sample source directory is `I Married a Broken Soldier. He was a Duke/`. It is deliberately excluded from Git along with ZIPs and PDFs. To run elsewhere, restore that directory or pass `--input /path/to/scripts`; upload your own scripts in the app. Generated outputs contain selected script quotations, not sanitized synthetic examples.

## Choose an AI judge

CLI automatically selects the first configured environment key in Gemini → OpenAI → Anthropic order. Dashboard defaults explicitly to offline. Keys entered in its password field stay in the current session and are never serialized to results.

```bash
export GEMINI_API_KEY='your-key'
python run_pipeline.py --provider Gemini --model gemini-3.8-flash --judge-budget 8
# Or configure OPENAI_API_KEY / ANTHROPIC_API_KEY and select that provider.
python run_pipeline.py --provider Heuristic/Offline
python run_pipeline.py --input /path/to/new/scripts --output /tmp/promo-run --min-duration 25 --max-duration 45
```

The judge receives exact shortlisted excerpts, not all 50 full scripts. Defaults: at most 8 candidates, in batches of 4; all other candidates retain labeled heuristic scores. Malformed JSON, wrong IDs, invalid scores, authentication failures, timeouts, and retired models produce a visible warning and keep the offline evaluation. No silent claims of successful AI judgment. Provider responses cannot change edit timestamps. Temperature zero reduces variation but does not guarantee deterministic live AI output.

Gemini defaults to `gemini-3.8-flash`; legacy presets `gemini-2.5-flash` and `gemini-2.5-pro` remain selectable for accounts that still have access. Use the editable model ID if your account exposes different models. OpenAI: `gpt-4o-mini`, `gpt-4o`. Anthropic has editable current-generation presets and exact legacy Claude 3.5 IDs; the latter may be retired and error on the live API. Model availability depends on the account; use the editable model field. APIs were tested with mocked contracts, not paid live requests.

References: [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [OpenAI Chat Completions](https://developers.openai.com/api/reference/chat-completions/overview), [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create), [Claude lifecycle](https://platform.claude.com/docs/en/about-claude/model-deprecations).

## Reading the results

`all_episodes_promos_ranked.json` includes run telemetry, all 50 episode coverage entries, accepted `promos`, complete `rejected_candidates`, the audit, and economics assumptions. Each promo has immutable source cuts, total duration, hook / cliff evidence, scores, a composite rank, posting tier, rationale, and review flags. The CSV and Markdown report contain every shortlisted promo, not just the first ten. The manifest fingerprints the four generated deliverables.

Scoring weights: hook 30%, unresolved cut 30%, standalone clarity 20%, arousal 10%, pacing 10%. UI weights normalize automatically. Editorial gates require hook ≥55, cliff ≥55, clarity ≥55, and no detected de-escalation or music-only ending. A scene may have no qualifying promo; the explorer still lists it. Mashups contain two segments (within the allowed 2–3), total 20–60s, ordered chronologically, with shared role signals and no reused overlapping footage. They still need human continuity checks.

Hard guarantees: timestamp strings exist verbatim on the correct episode, segment duration arithmetic matches, and no edit cuts through any overlapping spoken utterance. Visual / sound tracks may legitimately span an edit; the viewer shows their complete original descriptions and clips the unified time slices to the selected interval. Hook onset within a long visual beat is uncertain and flagged. Narrative comprehension and “maximum tension” cannot be proven from lexicons alone; shortlist scores are editorial estimates, not predicted CTR.

Offline rankings and script-derived outputs are deterministic. Wall-clock telemetry naturally differs per run. Costs are estimates unless API token usage is present; a billed-cost estimate still depends on editable reference rates. The default $0.00752 hybrid scenario uses 8 × 1,800 input and 160 output tokens; $1.60 naive comparison assumes 200k script tokens, three passes, and premium rates. The actual sample contains ~67.8k estimated text tokens, so a same-model naive run costs less than that illustrative premium scenario. Hosting, retry usage, human review, and taxes are separate.

## Verify / interview demo

```bash
python -m pytest -q
python run_pipeline.py
python -m streamlit run app.py --server.headless true --server.port 8501
```

Demo sequence: inspect the top playbook → Episode 25 wound reveal → compare Episode 24's rejected slow opening in **Where it fails** → upload a TXT / ZIP → adjust duration and weights → optionally select a keyed provider → change token assumptions in the calculator. Never paste keys into screenplay files or check them into Git.

**Validation performed:** all 50 episodes parsed (3,727 beats); complete exports generated; every emitted accepted/rejected candidate checked against source; deterministic runs and mocked provider adapters tested; four dashboard tabs rendered and the run button executed through Streamlit AppTest. No footage or ad campaign was available, so visual timing and performance remain editor-review tasks.

## Streamlit Community Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for exact account/deployment steps. Use `app.py` on branch `main`, with Python 3.11. `streamlit_deploy.zip` contains the deployable files without the confidential original screenplays or input ZIP. Extract it before uploading its contents to GitHub.

When the original folder is absent, the app loads the saved 50-episode playbook and uses saved episode metadata. To rerun or open full source timelines, upload the TXT/ZIP input and click **Find promos**. No API key is required for offline mode.

## Assignment recheck

See [REQUIREMENTS_REVIEW.md](REQUIREMENTS_REVIEW.md) for the item-by-item evidence and remaining verification limits. The latest complete input-pack run contains **64 shortlisted promos, 231 retained rejections and 295/295 passing source checks**. The stricter count replaces the earlier 83; false hook matches and a resolved-illness pivot were removed.

Each promo now includes a specific one-line explanation, `posting_priority`, `posting_reason` and `evaluation_source`. The dashboard defaults to posting order and also offers composite score order. Eleven deliberately selected development cases are exported by `python scripts/review_editorial_cases.py`; they are regression examples, not a measured real-world accuracy rate.

For an interview: select **Try a sample screenplay** → **Find promos** to demonstrate a fresh run without publishing the input pack. Then upload the interviewer’s TXT/ZIP files. Choose a supported provider and model, enter the key, and click **Test API connection**. The checkbox below exposes the actual provider endpoint and a placeholder-key request body. API tests send a tiny live request; selecting a provider alone does not call it. Pipeline runs show actual judged-candidate counts and per-candidate score sources.

Build a distribution with `python scripts/package_deploy.py`. It contains the original synthetic demo and the two-page solution PDF, with the confidential original pack excluded. See [INTERVIEW_GUIDE.md](INTERVIEW_GUIDE.md) for a short presentation and explanations you should understand.

Runtime versions are pinned to the clean installation used for the final audit: Streamlit 1.67.0, pandas 2.3.3 and pytest 9.2.0. All 31 tests pass there. Source-dependent tests skip deliberately when the confidential pack is absent; fresh sample and dashboard tests still run.
