# subscription_eater
AI-powered email subscription tracker that monitors Gmail, detects subscriptions, and helps you cancel them.

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your Google OAuth credentials:**
   - Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Web application)
   - Add `http://localhost:8000/auth/google/callback` as an authorized redirect URI
   - Copy Client ID and Client Secret to `.env`

3. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

4. **Run the backend:**
   ```bash
   uvicorn backend.app:app --reload --port 8000
   ```

5. **Open the frontend:**
   - Open `index.html` in your browser
   - Click "Sign in with Google"
   - Authorize the app
   - Your subscriptions will sync automatically every 15 minutes

## Backend service
This repository now includes a FastAPI backend that handles OAuth 2.0 authorization for Gmail (offline access), stores tokens per account, schedules periodic syncs, and exposes APIs for the frontend.

### Environment variables
The `.env.example` file has been created for you. Copy it to `.env` and configure the following:

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

## Troubleshooting

### Application won't start
- **Missing `.env` file**: Make sure you copied `.env.example` to `.env`
- **Invalid credentials**: Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set correctly in `.env`
- **Port already in use**: Change the port with `uvicorn backend.app:app --reload --port 8001`

### Background sync not working
- **Check logs**: The application now has comprehensive logging. Look for error messages in the console output
- **Authentication errors (401)**: Your OAuth token may have expired or been revoked. Re-authenticate by signing in again
- **Permission errors (403)**: Make sure the Gmail API is enabled in your Google Cloud project
- **Rate limiting (429)**: Google is rate limiting your requests. The app will retry on the next sync cycle

### No subscriptions showing up
- **Wait for first sync**: After signing in, wait up to 15 minutes for the first automatic sync, or trigger manually with `POST /sync`
- **Check the query**: The `SUBSCRIPTION_QUERY` in `.env` determines which emails are detected. Default: `subject:unsubscribe OR "subscription" OR "receipt" OR "billing"`
- **View logs**: Logs will show how many messages were found and processed

### Database issues
- **Reset database**: Delete `subscription_eater.db` and restart the app to create a fresh database
- **Corruption**: If you see SQLAlchemy errors, try deleting the database file

### Common error messages and solutions

| Error | Solution |
|-------|----------|
| `Failed to parse token JSON` | Database corruption. Delete `subscription_eater.db` and re-authenticate |
| `Authentication failed. Token may be expired` | Sign in again through the web interface |
| `Permission denied. Check Gmail API scopes` | Verify Gmail API is enabled in Google Cloud Console |
| `Rate limit exceeded` | Normal during high usage. App will retry automatically |
| `Unable to resolve account email` | OAuth flow failed. Check redirect URI in Google Cloud Console |

### Checking logs
The application now includes detailed logging. When running the backend, you'll see:
- Sync start/completion for each account
- Number of messages processed
- Any errors or warnings
- Background scheduler status

Example log output:
```
2026-01-05 10:00:00 - backend.gmail_sync - INFO - Starting sync for account user@example.com (ID: 1)
2026-01-05 10:00:02 - backend.gmail_sync - INFO - Found 50 messages to process for user@example.com
2026-01-05 10:00:10 - backend.gmail_sync - INFO - Sync completed for user@example.com: 50 messages processed, 0 errors
```
