# Test Gemini through the app using Google's free tier

Official documentation checked: **7 November 2026**.

## Model and key

Google's [Gemini API pricing page](https://ai.google.dev/gemini-api/docs/pricing) lists **`gemini-3.8-flash`** with free-tier standard text input and output. This model is the app's default Gemini preset. Google also lists **`gemini-3.5-flash-lite`** with free-tier text input/output; it is available as a manually selected alternative. Free access is subject to project eligibility and quota; a model being listed does not prove your particular project has remaining quota.

The documentation uses placeholders such as `YOUR_API_KEY`, not a shared working API credential. Generate your own key in [Google AI Studio](https://aistudio.google.com/apikey). Google's [key setup guide](https://ai.google.dev/gemini-api/docs/api-key) explains project/key creation. Paste the key only into the app's password field, not into chat or GitHub.

Check that the project is shown as **Free Tier** in AI Studio. A key attached to a paid project can incur paid API charges. The app cannot infer your project's billing tier from the key. See [Google's billing guide](https://ai.google.dev/gemini-api/docs/billing) and [project-specific rate limits](https://ai.google.dev/gemini-api/docs/rate-limits); no universal quota is hardcoded into the app.

## Small live test

1. Refresh your deployed app and choose **Gemini** under **AI provider & API key**.
2. Choose **gemini-3.8-flash**, or manually select **gemini-3.5-flash-lite** if the former is unavailable.
3. Paste your personal AI Studio key into **API key (session only)**.
4. Click **Prepare small Gemini test**. This selects the original synthetic sample and an AI budget of **1**. It does not call Google.
5. Click **Test API connection**. This sends one short JSON request. Success confirms that the selected key/model can respond, not that the promo pipeline has already run.
6. Click **Find promos** in the sidebar. This parses and analyzes the sample and asks the selected model to judge at most one candidate.
7. Open **Scale & economics → Actual run telemetry**. Confirm `judged_candidates` is at least 1, `input_tokens`/`output_tokens` are nonzero and `errors` is empty. Each promo displays its own scoring source. An AI-rejected candidate may appear in rejected results rather than the shortlist.

You can then upload the full input pack or the interviewer's new scripts and increase the budget if your quota permits. Other candidates retain explicitly labeled heuristic scores.

## Interpret the result

| Result | Meaning |
|---|---|
| API connection succeeded | A live request returned the requested JSON status. |
| `judged_candidates > 0`, no errors | Real model judging completed for at least one candidate. This is separate from whether its editorial judgment is good. |
| HTTP 404 | Model is unavailable to this account/API; check its exact ID and AI Studio access. |
| HTTP 401/403 | Check key validity, API restrictions and project/model permissions. |
| HTTP 503 | The provider is temporarily unavailable. The app tries up to three times with exponential backoff. If it still fails, wait or manually test Flash-Lite; there is no guarantee another model is available. |
| HTTP 429 | Quota/rate limit reached or unavailable; inspect the selected project's limits before retrying. |
| Promos appear but `judged_candidates == 0` | The visible results are heuristic; their appearance is not proof of API success. |

No public/shared key is embedded in the app. A free-tier request still requires your account's valid key. Live account access must be checked with your own valid key.

Transient HTTP 500/502/503/504 responses use bounded retries with jitter. Long Retry-After instructions are respected by stopping rather than retrying early. Bad-key, unavailable-model and quota errors are not automatically retried. The app never silently changes models or billing tiers, and reports exhausted connection tests as failures. Provider retries are recorded as HTTP attempts separately from logical judging calls. [Google API error guidance](https://ai.google.dev/gemini-api/docs/api-errors).
