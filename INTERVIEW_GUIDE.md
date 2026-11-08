# Interview walkthrough

Use this as an explanation guide, not a script for claiming work you did not do. The assignment permits AI assistance; explain that Codex assisted implementation and testing, and understand the design decisions yourself.

## A three-minute demonstration

1. **0:00–0:35 — Solve the actual problem.** Open the posting playbook. Show the first recommended wedding-betrayal cut, its exact episode/start/end and the question left unanswered. Explain why an editor can act on it.
2. **0:35–1:10 — Prove source grounding.** Upload the source pack and run offline, then open a verbatim timeline. Green marks the opening three seconds; red marks the last four. Camera tracks may overlap edits; dialogue cannot be cut mid-utterance.
3. **1:10–1:40 — Show honest failures.** Open Where it fails. Explain the decorative-watch-chain false hook or cured-child subplot pivot. Show the actual cut, not just a list of possible failures.
4. **1:40–2:15 — Prove rerunnability.** Select Try a sample screenplay and click Find promos. Metrics should change from 50 episodes to one, Episode 101. Upload any new script in the documented format to show it is not a hardcoded show lookup.
5. **2:15–2:45 — Swap AI.** Select the interviewer's provider/model, enter their key and test the connection. Show the endpoint/body checkbox if requested. Then analyze an input with AI budget one; show `judged_candidates` > 0 and per-candidate score source. Never claim an API run succeeded based only on heuristic results appearing.
6. **2:45–3:00 — Explain scale and limits.** Code filters candidate windows; AI judges a small budget. Cost rates and latency assumptions are editable; no video or campaign performance has been measured.

## Questions you should be able to answer

**Why not send all scripts directly to an LLM?** Code can enumerate safe source boundaries consistently. Keeping cuts in code reduces timestamp hallucination, token volume and the amount of confidential text sent to providers. AI then critiques the difficult editorial questions.

**Does every ranked promo use AI?** No. The saved run is offline. A live run judges at most the configured finalist budget, eight by default; the rest keep labeled heuristic scores. Ranking keeps the heuristic score; AI scores remain separate and uncalibrated. AI critique can veto or require review. Independent human-label evaluation remains pending.

**How do you know a cliffhanger is unresolved?** The code looks for questions, threats and reveals and penalizes known resolutions. It is not a proof of story meaning. AI and an editor can notice answers already supplied or misleading changes of victim.

**Why are some episodes empty?** The task is to find useful promos across all episodes, not force a bad 20-second cut from every episode. Every episode is parsed and included in coverage, even if no candidate survives.

**Why do posting order and composite rank differ?** Posting order considers format and review risk. A strong continuous cold-audience cut gets priority over an uncertain long opening or an unverified trailer bridge even if their numeric composites are similar.

**What was an actual AI mistake?** The first generated scoring rule matched `hang` inside `cliffhanger`. A calm music ending became an execution threat. Source inspection led to word boundaries, music-only caps and a regression test. Later audit found a decorative chain and burning ambition false positives.

**Can the interviewer call a REST endpoint for this tool?** There is no deployed REST service. The required prototype is a Streamlit UI or runnable repository. Its AI endpoint/body are visible in the app, but those call the model, not the complete pipeline. The CLI also reruns the full tool.

**What remains unverified?** Paid live inference with a valid replacement key, the precise visual onset in footage, real ad results, and the live hosted URL unless it is separately checked. Eleven selected development regressions are not a statistical accuracy benchmark.

## Before submitting

- Submit `SOLUTION_DOC.pdf` (two pages), the prototype/repository link, and a reviewer-accessible folder of unedited `raw_outputs/`.
- A screen recording up to three minutes in your own voice is optional but recommended.
- Test links in incognito. Keep the original screenplay pack and credentials out of public Git history. Generated outputs include selected quotations; choose the intended reviewer audience for them.
- Do not paste API keys into chat or source code. Replace any key already shared publicly.
