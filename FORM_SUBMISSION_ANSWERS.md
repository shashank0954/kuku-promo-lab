# Placement form — copy-paste answers

Build checked: **c9b8e2104f0b** (the saved-output SHA-256 prefix, not a Git commit). Anonymous HTTP checks on 8 November 2026 returned 200 for the app, repository, PDF and raw-output folder. The PDF and saved JSON matched local checksums. HTTP availability alone does not verify the rendered app's current ranking; open it in incognito before submitting.

**Only if the reviewer sees a login/access screen — owner sharing fix:** Sign in at https://share.streamlit.io and locate this app, then:

1. Open the app's **⋮ → Settings**.
2. Click **Sharing**.
3. Under **Who can view this app**, select **This app is public and searchable**; save if prompted.

Reopen the live link in an incognito window. These are the owner's console actions; the automated check did not change sharing settings. [Official Streamlit sharing instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

## Exact placement-form values

Fill the three personal fields yourself; their values are not available in this project. Do not submit the bracketed placeholders.

**Full name**
```text
[Your full name]
```

**Roll number**
```text
[Your roll number]
```

**Branch**
```text
[Your branch]
```

**Problem Chosen**
```text
Problem 1: Find the Promos (Ads)
```

**Solution Doc Link (PDF, 2 pages)**
```text
https://raw.githubusercontent.com/shashank0954/kuku-promo-lab/main/SOLUTION_DOC.pdf
```
Local file for a Google Drive upload: `./SOLUTION_DOC.pdf`. Upload the PDF itself, not the HTML source; paste the resulting accessible Drive link if using Drive.

**Prototype Link**
```text
Live App: https://kuku-promo-lab-shashank.streamlit.app/
Runnable GitHub Repo: https://github.com/shashank0954/kuku-promo-lab
```
If the form accepts exactly one URL, use the live app after the incognito check. Use the repository if the app is inaccessible; place the second URL in Notes. The repository includes run instructions and a fresh synthetic demo.

**Raw Outputs Link**
```text
https://github.com/shashank0954/kuku-promo-lab/tree/main/raw_outputs
```
For Google Drive: upload `./raw_outputs/` as a folder and share its reviewer link, or upload `./READY_TO_SUBMIT.zip` as the complete handoff. Keep the generated files unchanged. The folder contains the full latest run; `history/` preserves earlier snapshots. Do not upload the original confidential screenplay folder, original input ZIP or API keys.

**Short Summary / Notes** — three sentences
```text
Kuku Promo Lab finds and ranks 20–60 second microdrama promos with exact source cuts, immediate hooks and unresolved endings. Deterministic code checks timestamps, duration, whole dialogue and overlap, while optional AI provides source-grounded critique and editors review timing and continuity. The full 50-episode run produced 64 shortlisted promos covering 38 episodes, with 282 of 282 structural checks passing; scores are editorial estimates, and footage approval and independent human quality evaluation remain separate.
```

**Walkthrough link** — optional, recommended
```text
[Paste your unlisted Loom, YouTube or reviewer-shared recording link after recording]
```
Leave this field empty if you do not record a video. No recording or form submission has been performed automatically.

## Word-for-word voiceover — approximately two minutes

The **On screen** lines are directions, not narration. Read only **Say** aloud in your own voice. The script is about 250 words; rehearse once and pause naturally so the recording follows the four timing windows. Keep API keys and the original source pack off screen. Start with saved results; if the live app cannot open, run the same app locally from the repository.

### 0:00–0:30

**On screen:** Open the app with the saved 50-episode results. Keep the provider panel collapsed. Show the episode count, structural checks and ranked playbook.

**Say:**
> Hi, this is Kuku Promo Lab, my submission for Problem One. It helps an editor find short drama promos with an immediate hook, an understandable conflict, and an unresolved ending. I ran it across all fifty episodes. The current shortlist contains sixty-four promos, representing thirty-eight episodes, with exact source cut points for each segment.

### 0:30–1:10

**On screen:** In **Ranked playbook**, show the first recommendation: **E3 00:08.80–00:40.40**. Under **Inspect a promo**, choose that same candidate. Point to its duration, opening evidence, cliffhanger and timeline.

**Say:**
> Here is the first recommendation: Episode Three, from eight point eight seconds to forty point four seconds, lasting thirty-one point six seconds. It opens with, “You stole my wedding,” so a new viewer immediately understands the betrayal. It ends with, “And what happens to me?” leaving the bride’s future unanswered. The timeline marks the opening and ending review windows. The explanation and posting priority make the choice inspectable, while the source timestamps tell an editor exactly where to cut.

### 1:10–1:40

**On screen:** Open **Where it fails**. In **Real failure example**, select **E9-40.8-87.4**. Point to its rejection explanation and human correction.

**Say:**
> This rejected example shows why keyword matching alone is not enough. A hearth chain was previously mistaken for restraint. The child is then cured, before the clip switches scenes and ends on, “What is it?” The tool now rejects that resolved arc and weak ending. It also filters ordinary burning lanterns and routine kneeling. Structural validity is checked in code; editorial judgment still needs review.

### 1:40–2:00

**On screen:** Select **Try a sample screenplay** and keep **Heuristic/Offline** selected. Click **Find promos** to show the progress stages and fresh results. Open **AI provider & API key** only to show the selector, keeping the key field empty.

**Say:**
> Finally, I can run a fresh sample, upload new scripts, or select an episode range. Offline mode needs no API key. An interviewer can choose a provider and supply their own key for optional critique. API costs and human quality claims are reported honestly.

## Final check before pressing Submit

- PDF opens and has exactly two pages; its footer shows `c9b8e2104f0b`.
- Saved results show **E3 00:08.80–00:40.40**, “You stole my wedding,” as posting priority one; episode coverage is **38/50**.
- Test every pasted link in incognito. GitHub directory pages are HTML; their underlying files, not the HTML page hashes, are compared with local files.
- Use `./deliverables/public_link_verification.json` for the final anonymous link and file-checksum evidence.
- Confirm the placement-cell deadline, fill your personal details, submit once, and save the confirmation.
