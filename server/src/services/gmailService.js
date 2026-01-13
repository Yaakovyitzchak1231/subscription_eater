const { google } = require('googleapis');

class GmailService {
  constructor() {
    if (!process.env.GOOGLE_CLIENT_ID || !process.env.GOOGLE_CLIENT_SECRET) {
      console.error('CRITICAL: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET is missing in .env!');
    } else {
      console.log('GmailService: Credentials loaded successfully.');
    }

    this.oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      process.env.GOOGLE_REDIRECT_URI
    );
  }

  getAuthUrl(userId) {
    const scopes = [
      'https://www.googleapis.com/auth/gmail.readonly',
      'https://www.googleapis.com/auth/userinfo.email'
    ];

    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      prompt: 'consent',
      state: userId
    });
  }

  async getTokens(code) {
    const { tokens } = await this.oauth2Client.getToken(code);
    return tokens;
  }

  async listMessages(auth, query = 'subject:(receipt OR invoice OR subscription OR "free trial" OR "renewed")') {
    const gmail = google.gmail({ version: 'v1', auth });
    const res = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: 20
    });
    return res.data.messages || [];
  }

  async getMessage(auth, messageId) {
    const gmail = google.gmail({ version: 'v1', auth });
    const res = await gmail.users.messages.get({
      userId: 'me',
      id: messageId,
      format: 'full'
    });
    return res.data;
  }

  // Extract body from message parts
  getBody(payload) {
    let body = "";
    if (payload.parts) {
      payload.parts.forEach(part => {
        if (part.mimeType === "text/plain") {
          body += Buffer.from(part.body.data, 'base64').toString();
        } else if (part.mimeType === "text/html") {
          // You could parse HTML here, but plain text is easier for LLM
          body += Buffer.from(part.body.data, 'base64').toString();
        } else if (part.parts) {
          body += this.getBody(part);
        }
      });
    } else {
      body = Buffer.from(payload.body.data, 'base64').toString();
    }
    return body;
  }
}

module.exports = new GmailService();
