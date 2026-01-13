const axios = require('axios');

class GeminiService {
  constructor() {
    this.apiKey = process.env.GEMINI_API_KEY;
    // Using the newer, faster Gemini 2.0 Flash model
    this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
  }

  async parseEmailForSubscription(emailContent, subject, sender) {
    if (!this.apiKey || this.apiKey === 'your_gemini_api_key') {
      console.warn('Gemini API key not configured. Skipping LLM parsing.');
      return null;
    }

    const prompt = `
      You are an expert at analyzing emails to identify RECURRING subscriptions and free trials.
      
      Task: Analyze this email to determine if it is a RECEIPT for a recurring subscription or a TRIAL confirmation.
      
      STRICT RULES:
      1. IGNORE one-time purchases (e.g., Amazon product orders, food delivery, flight tickets).
      2. IGNORE general newsletters or marketing spam that are not receipts.
      3. LOOK FOR keywords like "renew", "recurring", "monthly", "yearly", "subscription", "membership", "trial ending".
      4. IF AMBIGUOUS, lean towards ignoring it. Only extract if you are 80% sure it's a subscription service.

      Email Context:
      - Subject: ${subject}
      - Sender: ${sender}
      - Body Preview: ${emailContent.substring(0, 3000)}

      If it IS a subscription, return a JSON object with:
      - name: Service Name (e.g., "Netflix", "Spotify")
      - amount: Numeric value (e.g., 9.99)
      - currency: 3-letter code (default USD)
      - billingCycle: "monthly", "yearly", "weekly" (infer from context)
      - status: "active" (paid) or "trial"
      - nextPaymentDate: ISO date string (YYYY-MM-DD) estimate based on current date.
      - trialExpirationDate: ISO date string if it's a trial.
      - category: "Entertainment", "Utility", "Productivity", "Health", or "Other".
      - confidence: number between 0 and 1.

      If NOT a subscription, return null.
    `;

    try {
      const response = await axios.post(`${this.apiUrl}?key=${this.apiKey}`, {
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { responseMimeType: "application/json" }
      });

      const resultText = response.data.candidates[0].content.parts[0].text;
      const result = JSON.parse(resultText);
      
      // Filter low confidence
      if (result && result.confidence < 0.7) return null;
      
      return result;
    } catch (error) {
      console.error('Gemini API Error:', error.response?.data || error.message);
      return null;
    }
  }
}

module.exports = new GeminiService();
