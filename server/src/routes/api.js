const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const oauthController = require('../controllers/oauthController');
const subController = require('../controllers/subscriptionController');
const authMiddleware = require('../middleware/authMiddleware');

// Auth
router.post('/auth/register', authController.register);
router.post('/auth/login', authController.login);

// Google OAuth
router.get('/auth/google', authMiddleware, oauthController.getGoogleAuthUrl);
router.get('/auth/google/callback', oauthController.googleCallback);

// Subscriptions
router.get('/subscriptions', authMiddleware, subController.getSubscriptions);
router.post('/subscriptions/scan', authMiddleware, subController.scanEmails);
router.put('/subscriptions/:id', authMiddleware, subController.updateSubscription);
router.delete('/subscriptions/:id', authMiddleware, subController.deleteSubscription);
router.post('/blacklist', authMiddleware, subController.addToBlacklist);

module.exports = router;
