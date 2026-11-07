# Deploy to Streamlit Community Cloud

The app is ready for Community Cloud. Deployment still requires your GitHub and Streamlit accounts.

## 1. Create a GitHub repository

Recommended name: `kuku-promo-lab`. Use a **private** repository for the assignment results, which include show quotations. The confidential screenplay folder and original ZIP are not part of the deployment package. Do not upload the whole workspace indiscriminately.

Extract `streamlit_deploy.zip` locally, then upload the **contents** of its folder into the repository. `app.py` and `requirements.txt` must be at the repository root, alongside `src/`, `raw_outputs/` and `.streamlit/`. GitHub's upload page does not unpack ZIP files: do not upload just the ZIP itself. Include the hidden `.streamlit` directory if using a desktop file picker (Cmd+Shift+. on macOS reveals hidden files).

## 2. Deploy

1. Sign into https://share.streamlit.io with GitHub.
2. Choose **Create app**, then **Yup, I have an app** (the labels can change).
3. Select the repository you just created.
4. Branch: `main`.
5. Main file path: `app.py`.
6. Under **Advanced settings**, select **Python 3.11**.
7. No secrets are required for offline mode. Click **Deploy**.

For a private repository, authorize Streamlit's access to that repository when prompted. A private repository does not automatically mean a freely accessible app: configure app sharing deliberately. Check your final reviewer link in an incognito window.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## 3. What reviewers see

The saved 50-episode playbook loads even though the original source folder is absent. Rankings, hooks, cuts, the episode explorer, failure audit, calculator and downloads work immediately. Full source timelines and fresh pipeline runs require uploading the TXT files or ZIP in the sidebar and clicking **Find promos**. Uploaded files are parsed in memory rather than extracted onto the server.

This is deliberate: original confidential scripts are not published as part of the deployment. The saved result JSON contains selected quotations, so keep assignment content within the intended reviewer audience.

## 4. Optional AI keys

A reviewer can enter a personal key in the expanded **AI provider & API key** section at the top of the page, then use **Test API connection** before running the full pipeline. **Show API endpoint and example request body** exposes a placeholder-key request contract. If you want to provide a server-side key instead, add it in Streamlit's app secrets settings:

```toml
GEMINI_API_KEY = "your-key"
# Or OPENAI_API_KEY / ANTHROPIC_API_KEY
```

Root-level Streamlit secrets are available as environment variables. Never commit `.streamlit/secrets.toml` or keys to GitHub. A server-side key can incur usage whenever someone runs the selected provider; offline mode needs none.

## 5. Smoke test after deployment

- Saved playbook shows 50 episodes and 64 shortlisted cuts.
- Select **Try a sample screenplay**, click **Find promos**, and verify the result changes to one episode (Episode 101).
- All four tabs open; Episode 25 is selectable.
- Upload the original ZIP, choose offline mode, and click **Find promos**.
- Under **Choose episodes**, enter `2, 5, 8-10`, rerun, and verify the result lists only those episode numbers. Change the selection without uploading again.
- Verbatim timeline opens after the uploaded source run.
- Download JSON / CSV.
- Check the reviewer link without your owner session.

If the app cannot import `src`, confirm that the full `src/` directory sits beside `app.py`. If no saved playbook appears, confirm `raw_outputs/all_episodes_promos_ranked.json` is present. Cloud logs appear in the app's management panel.
