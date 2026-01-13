const fs = require('fs');
const path = require('path');
const readline = require('readline');

const envPath = path.join(__dirname, 'server', '.env');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const questions = [
  { key: 'GOOGLE_CLIENT_ID', question: 'Enter your Google Client ID: ' },
  { key: 'GOOGLE_CLIENT_SECRET', question: 'Enter your Google Client Secret: ' },
  { key: 'GEMINI_API_KEY', question: 'Enter your Gemini API Key: ' }
];

const updateEnv = (key, value) => {
  let content = '';
  if (fs.existsSync(envPath)) {
    content = fs.readFileSync(envPath, 'utf8');
  }

  const regex = new RegExp(`^${key}=.*`, 'm');
  if (regex.test(content)) {
    content = content.replace(regex, `${key}="${value}"`);
  } else {
    content += `\n${key}="${value}"`;
  }

  fs.writeFileSync(envPath, content);
  console.log(`Updated ${key}`);
};

const askQuestion = (index) => {
  if (index >= questions.length) {
    console.log('\nEnvironment variables updated successfully!');
    rl.close();
    return;
  }

  const { key, question } = questions[index];
  rl.question(question, (answer) => {
    if (answer.trim()) {
      updateEnv(key, answer.trim());
    }
    askQuestion(index + 1);
  });
};

console.log('--- Subscription Tracker Setup ---');
console.log('Please provide the following credentials.\n');
askQuestion(0);
