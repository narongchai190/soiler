# Deploying S.O.I.L.E.R. to Streamlit Cloud

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Repository pushed to GitHub

## Quick Start (No API Keys Required)

S.O.I.L.E.R. works **out of the box** without any API keys:

1. **Maps**: Uses OpenStreetMap via Folium (free, no key required)
2. **Analysis**: Uses deterministic skill-based agents (no LLM API needed)
3. **Database**: SQLite created automatically on first run

### Deploy Steps

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repo
4. Set main file path: `streamlit_app.py`
5. Click "Deploy"

That's it! The app will work immediately.

## Optional: Adding API Keys

If you want to enable additional features (future LLM integration), you can add secrets:

### Adding Secrets in Streamlit Cloud

1. Go to your app's dashboard on Streamlit Cloud
2. Click the "..." menu > "Settings"
3. Select "Secrets" tab
4. Add secrets in TOML format:

```toml
# Example secrets.toml format
# Add only the keys you have

# Optional: Google Maps API (not required - app uses OpenStreetMap by default)
# GOOGLE_MAPS_API_KEY = "AIzaSy..."

# Optional: OpenAI API (for future LLM features)
# OPENAI_API_KEY = "sk-..."
```

5. Click "Save"
6. Reboot the app

### Local Development

For local development, create `.streamlit/secrets.toml`:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit with your keys (optional)
```

Note: `.streamlit/secrets.toml` is gitignored and will never be committed.

## Environment Variables

The app checks for secrets in this order:
1. `st.secrets` (Streamlit Cloud or local secrets.toml)
2. Environment variables
3. Falls back to built-in defaults (OpenStreetMap, deterministic agents)

## Troubleshooting

### App won't start

1. Check Streamlit Cloud logs for errors
2. Ensure `requirements.txt` is in the repo root
3. Verify Python version compatibility (3.10+)

### Database issues

The app creates `data/soiler_v1.db` on first run. On Streamlit Cloud, this is ephemeral (resets on reboot). For persistent storage, consider external database options.

### Map not loading

The app uses OpenStreetMap which should work everywhere. If maps fail:
- Check if `folium` and `streamlit-folium` are in requirements.txt
- Verify no network/firewall blocks to OpenStreetMap

## File Structure

```
soiler/
├── streamlit_app.py      # Main app entry point
├── requirements.txt      # Python dependencies
├── .streamlit/
│   ├── config.toml       # Theme configuration
│   └── secrets.toml      # (gitignored) Your local secrets
└── data/
    └── seed/             # Seed data for fresh installs
```

## Security Notes

- Never commit secrets to git
- API keys should only be in Streamlit Cloud secrets or `.env` files
- Run `python scripts/scan_secrets.py` before commits to verify no leaked secrets
