const gmailService = require('../services/gmailService');
const { PrismaClient } = require('@prisma/client');
const { google } = require('googleapis');
const prisma = new PrismaClient();

const getGoogleAuthUrl = (req, res) => {
  console.log('Requesting Google Auth URL for user:', req.user.id);
  try {
    const userId = req.user.id;
    const url = gmailService.getAuthUrl(userId);
    console.log('Generated Auth URL:', url);
    res.json({ url });
  } catch (error) {
    console.error('Error generating Google Auth URL:', error);
    res.status(500).json({ error: 'Failed to generate auth URL' });
  }
};

const googleCallback = async (req, res) => {
  const { code, state } = req.query;
  const userId = state; // userId is passed back in the state parameter

  if (!userId) {
    return res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:5173'}/dashboard?status=error&message=NoUserIdentified`);
  }

  try {
    const tokens = await gmailService.getTokens(code);
    
    // Get user info from Google
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials(tokens);
    const oauth2 = google.oauth2({ version: 'v2', auth: oauth2Client });
    const userInfo = await oauth2.userinfo.get();
    
    const googleEmail = userInfo.data.email;

    // Save or update GoogleAccount
    await prisma.googleAccount.upsert({
      where: { userId_email: { userId, email: googleEmail } },
      update: {
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        expiryDate: tokens.expiry_date
      },
      create: {
        userId,
        email: googleEmail,
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
        expiryDate: tokens.expiry_date
      }
    });

    res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:5173'}/dashboard?status=success`);
  } catch (error) {
    console.error('OAuth Error:', error);
    res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:5173'}/dashboard?status=error`);
  }
};

module.exports = { getGoogleAuthUrl, googleCallback };
