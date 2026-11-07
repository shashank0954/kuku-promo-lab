<style>
@page { size: A4; margin: 14mm; }
body { font: 10pt/1.28 Arial, sans-serif; color: #172235; }
h1 { font-size: 19pt; margin: 0 0 7pt; } h2 { font-size: 11.5pt; margin: 10pt 0 4pt; }
p { margin: 5pt 0; } table { border-collapse: collapse; width: 100%; font-size: 9pt; }
td, th { text-align: left; vertical-align: top; padding: 5pt; border-bottom: 1px solid #ddd; }
.page-break { break-before: page; page-break-before: always; }
a { color: #264b7b; } code { font-size: 9pt; }
</style>

# Kuku · Find the Promos / Ads
**Problem 1 — Source-grounded cuts, with an honest editorial review loop**

## 1. Problem choice & assumptions
Editors need a small, useful shortlist rather than another full-script summary. I chose Problem 1 because code can enforce real edit boundaries while AI can critique emotional stakes and standalone comprehension.

I treat the supplied timestamps as authoritative. Cuts last 20–60 seconds, inclusively; mashups use two segments. Spoken utterances remain whole even when other tracks overlap. These are script-based recommendations: no footage or ad-performance data was supplied. Some episodes have no suitable window. I do not force one promo per episode or claim exhaustive recall.

**Full run:** 50 episodes, 3,727 source beats, **64 shortlisted promos**, 231 retained rejections, **295/295 hard checks passed**. Runtime is approximately one second locally; exact telemetry is saved. Results are unedited pipeline exports, not hand-selected success examples.

## 2. What code does, what AI does, what an editor does
**Code:** parse scenes and original beats; merge concurrent camera, action, sound and dialogue into timeline slices; retrieve high-hook / high-tension windows; remove near-duplicates; propose short trailer bridges; validate exact source boundaries and whole dialogue. Gates reject weak openings, weak endings, low clarity, music-only tension and detected resolution-to-subplot pivots.

**AI:** Gemini, OpenAI or Anthropic critiques a bounded shortlist using hook 30%, cliffhanger 30%, clarity 20%, arousal 10% and pacing 10%. Model IDs are editable; keys can be supplied live. Eight finalists are judged by default, in batches of four. Remaining scores stay labeled heuristic. Invalid responses, inaccessible models and quota errors fall back visibly. AI cannot edit source timestamps.

**Editor:** confirm the action/words occur in the opening three seconds, test whether a stranger understands the conflict, check that the ending remains unresolved, and approve mashup continuity. A high score does not replace footage review. Posting priority favors clearer continuous cuts before uncertain hooks and trailers; composite rank remains separately visible.

## 3. Scale, latency & cost
The measured offline run costs **$0 in API fees**. Parallelize independent shows, cache by input/model version, bound the AI shortlist, and rate-limit provider calls. Current candidate construction enumerates boundary pairs and rescans candidate beats; a 60-second sliding index is the next optimization.

Planning example: 8 × 1,800 input + 8 × 160 output tokens at reference rates $0.30/$2.50 per million = **$0.00752/show**, or ~$1.50 for 200 shows/week. This is an editable historical-rate scenario, **not a current Gemini 3.8 price quote**. Usage is collected from API responses; unknown model rates remain unpriced.

A premium naive scenario with 200k input tokens × three passes and 10k output tokens at $2.50/$10 costs $1.60. This sample is only ~67.8k estimated tokens, so the equivalent scenario is ~$0.61. Two AI batches at an assumed eight seconds each add ~16 seconds; paid live latency is unmeasured. Hosting, retries and editor time are separate.

<div class="page-break"></div>

# Posting playbook & evidence

## 4. What I would post first, and why
The generated playbook gives every cut an explicit posting priority, episode, ordered segment timestamps, duration, hook, cliffhanger and specific one-line explanation. I would test these clear continuous conflicts first, subject to footage review:

| Order | Exact source cut | Duration | Conflict and withheld payoff |
|---|---|---:|---|
| 1 | E1 00:39.10–01:14.30 | 35.2s | “Because he is marrying me” opens a stolen-wedding confrontation; cut on “How long?” before the answer. |
| 2 | E3 01:24.00–01:52.50 | 28.5s | A stranger drops a guard, defends an abused woman, then she asks “Why are you doing this?” |
| 3 | E3 00:08.80–00:40.40 | 31.6s | “You stole my wedding” makes the betrayal explicit; cut on “And what happens to me?” |
| Challenger | E25 00:13.20–00:33.80 | 20.6s | Painful shoulder grab, bloody wound reveal, repeated “Who?” before the attacker is named. |

Use equal initial spend and compare three-second hold, click-through and downstream viewing starts. Tier 2 is for warmer conflict audiences; Tier 3 is a trailer pool requiring continuity approval. No conversion or retention improvement has been measured.

## 5. Quality checking & where the tool picks badly
**Hard checks** cover every emitted shortlisted/rejected candidate: correct episode/file, verbatim start/end boundary strings, 20–60s total, duration arithmetic, no overlapping reused footage and no cut through simultaneous dialogue. Tests check that all 3,727 source beats survive timeline partitioning. Eleven deliberately chosen script cases provide regression evidence, not an unbiased accuracy benchmark.

**Real weak picks and corrections:** E30 00:03.00–00:43.50 originally scored a pocket-watch “chain” as physical conflict. E49 01:24.00–01:52.80 matched eyes “burning” with ambition. Both now fail the hook gate. E21 00:47.30–01:39.20 shows the child recovering before pivoting to the Duchess; the original human conflict is resolved, so it is rejected. E24 00:00.00–00:20.50 wastes its opening on a door handle and depends on medicine context. These failures remain documented rather than hidden.

**Input anomaly:** E22's sound effect at 00:41.50–00:42.80 extends 0.3s beyond its declared scene end. Preserve the actual beat timestamp and report a warning. Never invent a “corrected” boundary.

Limits remain: rhetorical questions can look unresolved; a long beat does not establish exact word/action onset; shared roles do not prove mashup causality. Full visual descriptions matter: E32's “Burn it” has a book shown onscreen, which dialogue-only review would miss.

## 6. AI tools used & interview readiness
Codex assisted implementation, rubric design, testing and documentation. One AI-authored rule matched “hang” inside “cliffhanger,” falsely promoting a calm cello ending in E16 00:59.00–01:23.19. Word boundaries, music-only caps and de-escalation checks fixed it. Additional tests cover metaphorical injuries and decorative chains.

The saved run is **offline**, not paid AI inference. Provider contracts and the connection-test UI are tested with mocks. Reviewers can run the original synthetic sample immediately, upload new TXT/ZIP scripts, change models/keys, test the API, rerun and download fresh results. The app exposes the provider endpoint/body; a separate REST service is not required. A live paid request and video-based editorial approval remain unverified.

References: [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing); [Gemini models](https://ai.google.dev/gemini-api/docs/models). Code, raw outputs and reproduction steps accompany this PDF.
