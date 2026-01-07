# subscription_eater

AI-powered email subscription tracker that monitors Gmail, detects subscriptions, and helps you cancel them.

## Overview

This repository includes a **FastAPI backend** that handles OAuth 2.0 authorization for Gmail (offline access), stores tokens per account, schedules periodic syncs, and exposes APIs for the frontend. The frontend is a static HTML/JS app served by the backend.

## Setup & Running Locally

### 1. Prerequisites
- Python 3.9+ installed
- A Google Cloud Project with Gmail API enabled
- OAuth credentials (Client ID and Client Secret)

### 2. Google Cloud Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "Subscription Eater").
3. Enable the **Gmail API** in "APIs & Services" > "Library".
4. Configure the **OAuth Consent Screen**:
   - User Type: External (or Internal if you have a Workspace).
   - Add your email as a Test User.
   - Scopes: Add `https://www.googleapis.com/auth/gmail.readonly`.
5. Create Credentials:
   - Go to "Credentials" > "Create Credentials" > "OAuth Client ID".
   - Application Type: **Web application**.
   - Authorized Redirect URIs: `http://localhost:8000/auth/google/callback`
   - Copy the **Client ID** and **Client Secret**.

### 3. Installation

1. Clone the repo and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. Configuration:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and paste your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

### 4. Run the App

Start the backend server:
```bash
uvicorn backend.app:app --reload --port 8000
```

Open your browser to:
[http://localhost:8000](http://localhost:8000)

### 5. Usage
1. Click **Sign in with Google** on the dashboard.
2. Grant the requested permissions.
3. The app will sync your emails in the background (looking for receipts/invoices) and populate the dashboard with live data.

## Environment Variables

Create a `.env` file (or export variables) with the following values:

- `GOOGLE_CLIENT_ID` – OAuth client ID from Google Cloud
- `GOOGLE_CLIENT_SECRET` – OAuth client secret from Google Cloud
- `OAUTH_REDIRECT_URI` – Redirect URI configured in your Google OAuth client (default: `http://localhost:8000/auth/google/callback`)
- `DATABASE_URL` – SQLAlchemy connection string (default: `sqlite:///./subscription_eater.db`)
- `SUBSCRIPTION_QUERY` – Gmail search query for subscription-like messages (default targets unsubscribe/billing keywords)
- `SYNC_INTERVAL_MINUTES` – How often (in minutes) the background job syncs Gmail for all stored accounts (default: 15)

## API Endpoints

- `GET /auth/google/start` – Returns an authorization URL and state for OAuth 2.0 authorization_code flow (offline access + refresh tokens).
- `GET /auth/google/callback` – Handles Google's redirect, exchanges the code for tokens, and stores/updates the account.
- `GET /accounts` – Lists all connected accounts with their last sync time and aggregated subscription entries grouped by sender.
- `POST /sync` – Manually trigger a sync for all accounts (the scheduler also runs automatically based on `SYNC_INTERVAL_MINUTES`).
