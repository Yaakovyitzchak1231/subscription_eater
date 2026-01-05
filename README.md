# subscription_eater
AI-powered email subscription tracker that monitors Gmail, detects subscriptions, and helps you cancel them.

## Backend service
This repository now includes a FastAPI backend that handles OAuth 2.0 authorization for Gmail (offline access), stores tokens per account, schedules periodic syncs, and exposes APIs for the frontend.

### Environment variables
Create a `.env` file (or export variables) with the following values:

- `GOOGLE_CLIENT_ID` – OAuth client ID from Google Cloud
- `GOOGLE_CLIENT_SECRET` – OAuth client secret from Google Cloud
- `OAUTH_REDIRECT_URI` – Redirect URI configured in your Google OAuth client (default: `http://localhost:8000/auth/google/callback`)
- `DATABASE_URL` – SQLAlchemy connection string (default: `sqlite:///./subscription_eater.db`)
- `SUBSCRIPTION_QUERY` – Gmail search query for subscription-like messages (default targets unsubscribe/billing keywords)
- `SYNC_INTERVAL_MINUTES` – How often (in minutes) the background job syncs Gmail for all stored accounts (default: 15)

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Running the API
```bash
uvicorn backend.app:app --reload --port 8000
```

### Key endpoints
- `GET /auth/google/start` – Returns an authorization URL and state for OAuth 2.0 authorization_code flow (offline access + refresh tokens).
- `GET /auth/google/callback` – Handles Google’s redirect, exchanges the code for tokens, and stores/updates the account.
- `GET /accounts` – Lists all connected accounts with their last sync time and aggregated subscription entries grouped by sender.
- `POST /sync` – Manually trigger a sync for all accounts (the scheduler also runs automatically based on `SYNC_INTERVAL_MINUTES`).

### Data stored
- Accounts: email, tokens (including refresh token), token expiry, timestamps, and last sync time.
- Email metadata: normalized Gmail message details (sender, subject, snippet, internal date, subscription keyword guess) keyed per account.
