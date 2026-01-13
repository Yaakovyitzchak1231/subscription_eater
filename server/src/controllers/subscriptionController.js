const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const gmailService = require('../services/gmailService');
const geminiService = require('../services/geminiService');
const { google } = require('googleapis');

const getSubscriptions = async (req, res) => {
  const userId = req.user.id;
  const subs = await prisma.subscription.findMany({
    where: { userId },
    orderBy: { nextPaymentDate: 'asc' }
  });
  res.json(subs);
};

const scanEmails = async (req, res) => {
  const userId = req.user.id;
  
  try {
    const googleAccounts = await prisma.googleAccount.findMany({ where: { userId } });
    let totalFound = 0;

    for (const account of googleAccounts) {
      const oauth2Client = new google.auth.OAuth2(
        process.env.GOOGLE_CLIENT_ID,
        process.env.GOOGLE_CLIENT_SECRET,
        process.env.GOOGLE_REDIRECT_URI
      );

      oauth2Client.setCredentials({
        access_token: account.accessToken,
        refresh_token: account.refreshToken,
        expiry_date: Number(account.expiryDate)
      });

      const messages = await gmailService.listMessages(oauth2Client);
      
      for (const msgInfo of messages) {
        // Check if we already processed this thread
        const existing = await prisma.subscription.findFirst({
          where: { emailThreadId: msgInfo.threadId, userId }
        });
        if (existing) continue;

        const message = await gmailService.getMessage(oauth2Client, msgInfo.id);
        
        // Extract headers
        const headers = message.payload.headers;
        const subject = headers.find(h => h.name === 'Subject')?.value || '';
        const from = headers.find(h => h.name === 'From')?.value || '';
        const body = gmailService.getBody(message.payload);
        const snippet = message.snippet;

        // CHECK BLACKLIST
        const isBlacklisted = await prisma.blacklist.findFirst({
          where: {
            userId,
            OR: [
              { type: 'sender', term: from },
              { type: 'subject', term: subject } // Simplified exact match for now
            ]
          }
        });

        if (isBlacklisted) {
          console.log(`Skipping blacklisted email from: ${from}`);
          continue;
        }
        
        // Pass extra context to Gemini
        const subData = await geminiService.parseEmailForSubscription(body, subject, from);
        
        if (subData && subData.name) {
          await prisma.subscription.create({
            data: {
              userId,
              name: subData.name,
              provider: subData.name,
              amount: subData.amount,
              currency: subData.currency || 'USD',
              billingCycle: subData.billingCycle,
              status: subData.status || 'active',
              category: subData.category,
              nextPaymentDate: subData.nextPaymentDate ? new Date(subData.nextPaymentDate) : null,
              trialExpirationDate: subData.trialExpirationDate ? new Date(subData.trialExpirationDate) : null,
              emailThreadId: msgInfo.threadId,
              sourceEmail: account.email,
              emailSubject: subject,
              emailSnippet: snippet,
              emailBody: body.substring(0, 5000) // Truncate to save space
            }
          });
          totalFound++;
        }
      }
    }

    res.json({ message: `Scan complete. Found ${totalFound} new subscriptions.` });
  } catch (error) {
    console.error('Scan Error:', error);
    res.status(500).json({ error: 'Failed to scan emails' });
  }
};

const updateSubscription = async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;
  const data = req.body;

  try {
    const sub = await prisma.subscription.updateMany({
      where: { id, userId },
      data
    });
    res.json(sub);
  } catch (error) {
    res.status(400).json({ error: 'Update failed' });
  }
};

const deleteSubscription = async (req, res) => {
  const { id } = req.params;
  const userId = req.user.id;
  await prisma.subscription.deleteMany({ where: { id, userId } });
  res.json({ success: true });
};

const addToBlacklist = async (req, res) => {
  const { term, type } = req.body; // type: "sender" or "subject"
  const userId = req.user.id;

  try {
    await prisma.blacklist.create({
      data: { userId, term, type }
    });
    
    // Also remove any existing subscriptions that match this
    // This cleans up the dashboard immediately
    if (type === 'sender') {
        // We can't easily filter by sender in the sub table unless we saved it exactly
        // For now, we just blacklist for future.
    }

    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to blacklist' });
  }
};

module.exports = { getSubscriptions, scanEmails, updateSubscription, deleteSubscription, addToBlacklist };
