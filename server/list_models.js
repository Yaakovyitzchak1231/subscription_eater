const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.join(__dirname, '.env') });

const apiKey = process.env.GEMINI_API_KEY;
const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

async function listModels() {
  try {
    console.log('Fetching available Gemini models...');
    const response = await axios.get(url);
    const models = response.data.models;
    
    console.log('\n--- Available Models ---');
    models.forEach(model => {
      if (model.supportedGenerationMethods.includes('generateContent')) {
        console.log(`- ${model.name} (v: ${model.version})`);
      }
    });
    console.log('------------------------\n');
  } catch (error) {
    console.error('Error fetching models:', error.response?.data || error.message);
  }
}

listModels();
