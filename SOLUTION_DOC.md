<style>
@page { size: A4; margin: 15mm; }
body { font: 10pt/1.3 Arial, sans-serif; color: #172235; }
h1 { font-size: 20pt; margin: 0 0 8pt; } h2 { font-size: 12pt; margin: 10pt 0 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; } td, th { text-align: left; padding: 5pt; border-bottom: 1px solid #ddd; }
p { margin: 5pt 0; } .page-break { break-before: page; page-break-before: always; }
</style>

# Kuku · Find the Promos / Ads
**Problem 1 · A hybrid editorial system, not a full-script LLM wrapper**

## 1. Choice & explicit assumptions
Find 20–60s vertical-ad cuts that stop a stranger in three seconds and end before the emotional payoff. I chose this problem because safe edit boundaries are computational, while understanding betrayal and unresolved tension is editorial: each deserves a different tool.

The 50 supplied screenplays are the timing authority; there is no video, audio or campaign performance data. Timestamps are episode-local. Duration limits are inclusive. Entire spoken utterances must survive edits; visual tracks may overlap a cut. Two segments satisfy the allowed 2–3-part mashup format. A scene can produce no qualifying promo rather than forcing an unsuitable one. Script-based scores are hypotheses, not observed ad lift.

**Completed run:** 50 episodes; 3,727 original beats; 83 shortlisted promos; 229 retained rejected candidates; **312/312 source-validity checks passed**. Offline execution takes about one second on this machine; exact telemetry is in the generated JSON. Every episode remains browsable, including episodes without shortlisted cuts.

## 2. Hybrid architecture & human review
**Code:** parse Episode → Scene → Beat; preserve source strings and full dialogue; partition overlapping tracks at every event boundary into unified half-open audiovisual slices. Generate high-signal windows, remove overlapping alternatives, and assemble chronologically ordered role-linked mashups. Every cut must use a real source start/end and cross no spoken line. Validate duration and arithmetic independently after judging.

**AI:** Gemini, OpenAI and Anthropic share one JSON rubric. Only a bounded shortlist reaches the provider; AI critiques cold-viewer clarity, emotional intensity, continuity and the exact endpoint. It cannot invent or move timestamps. Scores: hook **30%**, cliffhanger **30%**, clarity **20%**, arousal **10%**, pacing **10%**. Eight finalists maximum by default, four per request; remaining scores stay explicitly heuristic. Keys auto-enable the CLI judge; the UI offers an explicit provider selector. Invalid responses fall back visibly to offline scoring. Legacy Claude 3.5 IDs remain configurable but can be retired.

**Editor:** compare verbatim evidence with footage, confirm the action actually happens in the first three seconds, check that the question remains unanswered, and reject misleading mashup bridges. Automated gates exclude weak hooks, weak cuts, low clarity, music-only endings and detected de-escalation. Surviving cuts still carry review flags where appropriate.

## 3. Scale, latency & unit economics
Default planning scenario: 8 × 1,800 input tokens + 8 × 160 output tokens. At Gemini 2.5 Flash reference rates of **$0.30 input / $2.50 output per million**, that is **$0.00752/show**, below $0.03. Offline costs $0. These are estimates, not a paid-run claim; live usage fields are recorded and costed separately.

A premium naive scenario of 200k script tokens × three passes, plus 10k output tokens, at $2.50/$10 costs **$1.60/show**. The actual supplied text is approximately 67.8k tokens by characters/4: the same naive premium assumptions produce about **$0.61**, not $1.60. The calculator exposes both scenarios and editable rates; a same-model comparison is also shown.

At 200 weekly shows, the default AI estimate is **$1.50/week**, excluding retries, hosting and editors. Two sequential AI batches at an assumed eight seconds each add ~16s/show; live latency is unmeasured. Scale through a show-level worker queue, content-hash caching, bounded shortlist budgets and rate-limited provider pools. Exhaustive window construction is quadratic in beat count per episode; production can use a sliding 60s boundary index.

<div class="page-break"></div>

# Editorial playbook & quality evidence

## 4. Top picks & actual posting order
The full CSV/report preserve composite ranking. Posting order also considers review risk: start with clear single-scene conflict, then test protective rage, then use reviewed mashups. Do not interpret a high score as permission to publish an ambiguous cut.

| Use | Exact source cuts | Duration | Why / unresolved cut |
|---|---|---:|---|
| First test · ranked #1 · 84.7 | E21 00:11.20–00:35.80 | 24.6s | A child cannot breathe; desperate plea ends “he will die.” No cure is shown. |
| Rescue challenger · #6 · 80.6 | E3 01:24.00–01:52.50 | 28.5s | Stranger strikes a guard; ends “Why are you doing this?” before his answer. |
| Protective-rage challenger · #24 · 78.0 | E25 00:13.20–00:33.80 | 20.6s | Painful shoulder grab → bloody welt → repeated “Who?” Cut before naming her attacker. |
| Trailer · #3 · 81.6 | E28 01:10.50–01:21.90 + E31 01:48.80–02:02.00 | 24.6s | Necklace coercion → defiant “make me kneel?” Requires continuity approval. |

Rank #2, E37 01:32.00–01:59.80 (84.7), opens on a chained hand and ends with an execution question; the long opening visual needs footage verification. Keep it behind a verified opening despite its high composite. Allocate equal test spend to the first three reviewed singles; compare three-second hold, click-through and downstream starts. Tier 2 serves warmer conflict audiences; Tier 3 is the trailer pool. No performance result is claimed.

## 5. Quality checks & honest weak picks
**Hard evidence:** source boundary existence, exact timestamp strings, correct episode/file pairing, 20–60s total, 1–3 segments, correct duration sums, no reused overlapping footage and no cut through any simultaneous dialogue. Every emitted accepted/rejected candidate is checked. Tests verify all 3,727 beats survive timeline partitioning without loss.

**Actual failures retained in JSON and audit:** E24 **00:00.00–00:20.50** begins with a slow door handle and needs medicine lore; an ominous sound is not a first-three-second hook. Reject or start on the later physical confrontation. E16 **00:19.20–01:15.80** reaches softening empathy near the endpoint; end before the comfort beat, then recheck duration. E21 **00:11.20–00:18.20 + 01:19.80–01:39.20** jumps from a sick child to the Dowager Duchess: shared “illness” semantics falsely suggest one victim. The explicit victim-change penalty rejects that mashup; an editor must preserve a single causal story.

**Source anomaly:** E22 beat 22:23 ends at **00:42.80**, while its scene is declared to end at **00:42.50**. Preserve the sound effect, record the warning, and use actual beat boundaries. Normalizing it silently would invent a timestamp.

Remaining limitations: lexicons can mistake metaphor for injury; a question may be rhetorical or answered earlier; role overlap does not prove mashup causality; long visual descriptions do not establish exact action onset. The audit presents weaker and stronger evidence side by side so an editor can correct these cases. No claim of perfect semantic recall or video verification.

## 6. AI tools used & one mistake during development
Codex assisted Python/UI implementation, rubric design and verification. An initial AI-authored lexical rule matched **“hang” inside “cliffhanger”**, promoting an emotional cello ending in E16 **00:59.00–01:23.19** as an execution threat. Reading the actual source revealed a calm, intimate resolution. Word boundaries, a music-only score cap and de-escalation checks fixed it; a regression test now protects this case. “Tear-streaked” was another false physical-conflict match and is also covered.

The saved run uses **heuristic/offline evaluation only**. Provider request/response contracts are tested with mocks; no paid inference or invented LLM judgments are reported. The app's four tabs and rerun action were exercised through Streamlit AppTest. See README for reproduction and the unedited raw outputs for every candidate and reason.

Pricing reference: [Google Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). Model lifecycle: [Anthropic deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations). Reference rates remain editable and are not invoice guarantees.
