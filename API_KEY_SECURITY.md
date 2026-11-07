# API key handling

Keys entered in the password widget are held in that user's Streamlit session. The app does not intentionally write them to disk, cache them, include them in prompts, export them, or print them to logs. Clear API keys removes the app's stored widget values for all providers in the current session; it cannot erase provider logs or guarantee immediate memory erasure.

Requests travel through the hosting server to fixed official HTTPS provider endpoints, with keys in authentication headers. Provider redirects are blocked. Model IDs cannot inject URL paths or query parameters. Parsed provider responses have exact copies of the active key redacted before they can enter results. Errors show sanitized status messages; detailed Streamlit UI exceptions are disabled. API request examples always use a placeholder key.

These protections do not guarantee 100% security. The hosting operator and provider remain trust boundaries; browser extensions, compromised devices and infrastructure are outside this app's control. Password masking is display protection, not end-to-end encryption. Never paste keys into screenplay content, editor notes or model-name fields. Use your own restricted, low-quota test key, revoke any key shared in chat, and clear the session when finished.

Server-side environment/Streamlit secrets keys are optional and must never be committed. A publicly accessible app using an owner-funded server key can incur costs, so reviewer-entered keys are preferred. Offline mode requires none.

Security checks use fake keys and mocks: redirect blocking, model-ID validation, response redaction, sanitized errors, session isolation and key clearing. No live provider call or independent penetration test is claimed.
