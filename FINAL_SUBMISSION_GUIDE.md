# Final submission guide — Kuku, Problem 1

Verified on 8 November 2026. The required prototype, two-page solution and full-pack outputs are prepared. This is a working script-based editorial shortlist, not proof of ad performance or automatic footage approval. See `deliverables/final_verification.json` for the latest measured checks.

The live app URL was supplied by you. External automated verification encountered an HTTP redirect loop and a browser timeout; this does not prove the app is broken. Complete the incognito check below. The GitHub PDF and raw-output links returned HTTP 200.

Final checks: 121 tests passed with the pack. See final_verification.json for the extracted source-free package check. The full run has 64 shortlisted promos and 282/282 structural checks; the PDF is two pages.

## 1. Read the final document

Open `SOLUTION_DOC.pdf`. It is the solution document to submit. `SOLUTION_DOC.html` and `SOLUTION_DOC.md` are editable sources; do not submit either instead of the PDF.

Confirm you can explain: why Problem 1; exact source cuts versus uncertain editorial judgment; code/AI/editor responsibilities; model swapping; failure cases; measured offline usage versus estimated live cost. Human acceptance precision and pairwise agreement are pending real labels. Do not describe development tests as independent accuracy results.

## 2. Prepare the three required links

| Form field | What to supply |
|---|---|
| Solution document | Upload `SOLUTION_DOC.pdf` to your submission folder and copy its view/download link. Maximum two pages. |
| Prototype | https://kuku-promo-lab-shashank.streamlit.app/ ; fallback runnable repository: https://github.com/shashank0954/kuku-promo-lab |
| Raw outputs | Upload the contents of `raw_outputs/` to your assignment submission folder and copy the folder link. The latest full run is in the four main files below; `history/` preserves earlier runs. |

Main unedited outputs:

- `all_episodes_promos_ranked.json`: complete structured results, cuts, scores, decisions and run metadata.
- `top_promos_ranked.csv`: spreadsheet handoff to editors.
- `top_promos_report.md`: ranked playbook and posting rationale.
- `quality_and_failure_audit.md`: actual weak picks, rejections and correction needs.

Keep `manifest.json` and `editorial_regression_review.json` alongside these outputs. The 24-case frozen evaluation is in `evaluation/`; human labeling sheets remain blank. `deliverables/visual_playbook.html` is an optional local visual companion, not a replacement for raw results. `SUBMISSION_BUNDLE.zip` is a backup containing the code, docs and generated artifacts, not the original input pack; it is not an extra mandatory form field.

## 3. Check confidentiality and link access

The brief forbids publishing the input pack. Do not upload the original screenplay folder, input ZIP, assignment PDF or API keys to a public repository or walkthrough. Generated results and the solution PDF also contain selected screenplay quotations: share those through the assignment's reviewer link, not as general publicity. The existing public repository includes these derived quotations; do not call it fully sanitized or claim confidentiality is fully resolved. Review its exposure before submission. Changing repository visibility can affect app access; deleting a current file does not remove earlier Git history.

Use the intended placement-cell/reviewer sharing method. If the form requires “anyone with the link,” enable that only on the specific submission artifacts, without publishing the original scripts. Verify each submitted link in an incognito window. Keep the source pack local for the interview.

## 4. Run the short smoke test

1. Open the deployed app in an incognito window; confirm it opens without your owner account.
2. Choose **Try a sample screenplay**, select **Heuristic/Offline**, then **Find promos**. Expect Episode 101, two shortlisted promos, and successful structural checks.
3. Privately upload the original pack. Under **Choose episodes**, enter `5-8`, then **Find promos**. Expect exactly episodes 5, 6, 7 and 8 analyzed; the verified offline defaults yield 3 shortlisted promos and 10/10 structural checks across shortlisted/rejected candidates. Different duration or scoring settings can change these counts.
4. In Tab 1, inspect the exact segment cuts, total seconds, hook, unresolved ending, ranking reason and review needs. Each segment must belong to your selected episodes. A mashup need not include every selected episode.
5. Compare two candidates, record a note and separate script/footage decisions. Download the editor-selected shortlist separately from the original ranked JSON. Script approval does not grant footage approval.
6. Optional: enter a fresh restricted provider key, test the connection, set AI budget to one and run the sample. A successful connection probe alone does not prove candidate judging worked: confirm `judged_candidates > 0`, usage and any warnings. Clear API keys afterward. No live inference is claimed by the verification report.

If the hosted app is unavailable, the brief explicitly accepts the repository with clear run instructions. The repository supports a synthetic demo without the confidential pack:

```sh
pip install -r requirements.txt
streamlit run app.py
# Fresh CLI sample:
python run_pipeline.py --input examples --provider Heuristic/Offline --output /tmp/kuku-demo
```

## 5. Optional recommended walkthrough — maximum three minutes

Record in your own voice. Show the synthetic sample or only the selected output evidence; keep keys and original source pack off screen.

- 0:00–0:25: editor's problem and why you chose Problem 1.
- 0:25–1:10: run sample input; show loading stages and first recommendations.
- 1:10–1:50: inspect cuts, total duration, hook and unresolved ending; explain why one posts first.
- 1:50–2:25: show a real rejected case and the editor's correction.
- 2:25–3:00: show swappable provider controls without a visible key; explain code versus AI, uncertainty and estimated cost.

Upload the video as an unlisted/reviewer-shared recording and check its access. A recording has not been created on your behalf.

## 6. Complete the placement-cell form

Enter your name, roll number, branch and **Problem 1 — Find the Promos (Ads)**. Paste the three required links and the optional walkthrough link. The exact placement-cell form URL and your personal details are not part of this workspace. Verify the actual deadline: the brief says within 48 hours of receiving it; its receipt time is unknown here.

Suggested short description:

> Kuku Promo Lab finds 20–60s script-grounded promo cuts across all 50 episodes. Deterministic code validates timestamps, whole dialogue, duration and overlap; optional AI critiques selected evidence without changing cuts. Editors review timing and continuity, compare candidates and export a separate approved shortlist. The submission includes full offline outputs, concrete failures and a rerunnable Streamlit prototype. Scores are editorial estimates; live ad performance and independent human-label metrics are not claimed.

Open each final link again, submit once, and save the form confirmation. Neither the form nor a video is submitted automatically by this project.
