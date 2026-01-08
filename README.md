# Subscription Eater

AI-powered email subscription tracker that monitors Gmail, detects subscriptions, and helps you track them.

## Architecture
This application uses a **FastAPI backend** (Python) to handle OAuth and data processing, and a static **HTML frontend** served by the backend.

- **Backend:** `backend/app.py` (FastAPI)
- **Frontend:** `index.html` (served at `/`)
- **Database:** SQLite (local file)
- **API Prefix:** All API endpoints are prefixed with `/api`

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
   - **Authorized Redirect URIs:** `http://localhost:8000/api/auth/google/callback`
     - *Note: Ensure this matches exactly. The backend listens on this path.*
   - Copy the **Client ID** and **Client Secret**.

### 3. Installation

1. Clone the repo.

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On macOS/Linux:
   source .venv/bin/activate
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Configuration:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and paste your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
   - Ensure `OAUTH_REDIRECT_URI` is set to `http://localhost:8000/api/auth/google/callback`.

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
3. The app will sync your emails in the background (looking for subscription-related emails such as those containing "unsubscribe", "subscription", "receipt", or "billing") and populate the dashboard with live data.
