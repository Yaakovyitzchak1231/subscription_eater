# Subscription Eater (Stitch Brand)

AI-powered email subscription tracker that monitors Gmail, detects subscriptions using Gemini AI, and helps you manage them.

## Features
- **Gmail Integration:** Connect multiple Google accounts with OAuth 2.0.
- **AI-Powered Scanning:** Automatically identifies subscription receipts and trial notifications using Gemini 2.0 Flash.
- **Modern Dashboard:** "Stitch" branded UI with dark mode, spend analytics, and upcoming renewal alerts.
- **Management:** Track active subscriptions and free trials effortlessly.

## Project Structure
- `/client`: React (Vite) + Tailwind CSS frontend.
- `/server`: Node.js (Express) + Prisma (SQLite) + Gemini AI backend.

## Setup Instructions

### 1. Prerequisites
- Node.js installed.
- Google Cloud Project with Gmail API enabled.
- Gemini API Key (from [Google AI Studio](https://aistudio.google.com/)).

### 2. Backend Setup
1. Navigate to the `server/` directory.
2. Create a `.env` file with the following:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI=http://localhost:3001/api/auth/google/callback`
   - `GEMINI_API_KEY`
   - `JWT_SECRET` (any secure string)
   - `DATABASE_URL="file:./dev.db"`
3. Install dependencies: `npm install`
4. Run migrations: `npx prisma migrate dev`
5. Start the server: `npm run dev`

### 3. Frontend Setup
1. Navigate to the `client/` directory.
2. Install dependencies: `npm install`
3. Start the app: `npm run dev`

### 4. Google OAuth Configuration
- Add `http://localhost:3001/api/auth/google/callback` to your **Authorized Redirect URIs** in the Google Cloud Console.

## License
MIT