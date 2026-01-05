# Gmail API Setup Guide

Follow these steps to enable real Gmail integration in Subscription Eater.

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click **NEW PROJECT**
4. Name it "Subscription Eater" and click **CREATE**
5. Wait for the project to initialize

## Step 2: Enable Gmail API

1. In the Cloud Console, go to **APIs & Services** > **Library**
2. Search for **Gmail API**
3. Click on it and press **ENABLE**
4. Wait for it to enable

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. If prompted, click **CREATE OAUTH CONSENT SCREEN** first:
   - Select **External** user type
   - Fill in app name: "Subscription Eater"
   - Add your email as test user
   - Save and continue
4. Back in Credentials, click **+ CREATE CREDENTIALS** > **OAuth client ID**
5. Choose **Web application**
6. Under **Authorized JavaScript origins**, add:
   - `http://localhost:3000`
   - `http://localhost:8000`
   - Your actual domain (if hosting online)
7. Under **Authorized redirect URIs**, add:
   - `http://localhost:3000`
   - `http://localhost:8000`
8. Click **CREATE**
9. Copy the **Client ID** (looks like: `xxxxx.apps.googleusercontent.com`)

## Step 4: Add Client ID to Subscription Eater

1. Open `index.html`
2. Find this line (around line 230):
   ```javascript
   const CLIENT_ID = 'YOUR_CLIENT_ID.apps.googleusercontent.com';
   ```
3. Replace `YOUR_CLIENT_ID` with your actual Client ID from Step 3
4. Save the file

## Step 5: Run Locally (or Deploy)

### Option A: Local Testing
```bash
# Use Python's built-in server
python -m http.server 3000

# Or Node.js
npx http-server -p 3000
```

Then open: `http://localhost:3000`

### Option B: Deploy Online
- Upload `index.html` to GitHub Pages, Vercel, Netlify, or any static host
- Add your domain to Google Cloud OAuth redirect URIs
- Update `Client ID` if needed

## Step 6: Grant Permission

1. Open the app in your browser
2. Click the **Gmail Sign In** button
3. Select your Google account
4. Review permissions and click **Allow**
5. You're connected!

## Features After Setup

✅ **Sync Inbox** - Scans your last 20 subscription-related emails  
✅ **Auto-Detection** - AI identifies billing, renewal, membership emails  
✅ **Extract Unsubscribe** - Pulls unsubscribe links from email headers  
✅ **Track Spending** - Shows total monthly cost  
✅ **Manual Review** - Flag uncertain emails for approval  

## Troubleshooting

**"Client ID not configured"**
- Check that you added your Client ID correctly (no extra spaces)

**"Failed to fetch emails"**
- Check browser console for error details
- Make sure Gmail API is enabled in Cloud Console
- Verify your OAuth consent screen is set up

**"401 Unauthorized"**
- Your token expired. Click Logout and sign in again

**"CORS Error"**
- Make sure you're running on `localhost:3000` or a whitelisted domain
- Add your domain to OAuth redirect URIs in Cloud Console

## Security Notes

⚠️ This app requests **read-only** access (`gmail.readonly`)  
⚠️ Tokens are stored in browser `localStorage` only  
⚠️ No server backend = no data leaves your device  
⚠️ For production, consider adding a backend to rotate tokens safely

## Limitations

- Scans up to 20 emails per sync (can be increased in code)
- Uses heuristic detection (not ML, for privacy)
- No automatic unsubscribe (you click links manually)
- Needs re-authentication if token expires

Enjoy tracking your subscriptions!
