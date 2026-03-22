const https = require('https');
const crypto = require('crypto');
const config = require('./openclaw.config.js');

const prompts = [
  "Explain the benefits of renewable energy.",
  "Write a short poem about the sea.",
  "Summarize the plot of 'Romeo and Juliet'."
];

// Helper: simple similarity metric (Jaccard similarity on words)
function similarity(text1, text2) {
  const set1 = new Set(text1.toLowerCase().split(/\W+/));
  const set2 = new Set(text2.toLowerCase().split(/\W+/));
  const intersection = new Set([...set1].filter(x => set2.has(x)));
  const union = new Set([...set1, ...set2]);
  return (intersection.size / union.size) || 0;
}

// Helper: make POST request with JSON body and auth header
function postRequest(url, apiKey, prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ prompt });
    const urlObj = new URL(url);

    const options = {
      hostname: urlObj.hostname,
      path: urlObj.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
        'Authorization': `Bearer ${apiKey}`
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          resolve(json);
        } catch (e) {
          reject(new Error('Invalid JSON response'));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Estimate cost based on token count and model pricing (dummy values)
function estimateCost(model, text) {
  // Rough token estimate: 1 token ~ 4 chars
  const tokens = Math.ceil(text.length / 4);
  // Pricing per 1k tokens (example)
  const pricing = {
    'gemini:flash': 0.020, // $0.020 per 1k tokens
    'zai:manual': 0.010   // $0.010 per 1k tokens (cheaper)
  };
  const costPer1k = pricing[model] || 0.02;
  return (tokens / 1000) * costPer1k;
}

async function testRouting() {
  const scoutConfig = config.agents.scout;
  const geminiProfile = config.authProfiles['gemini:flash'];
  const zaiProfile = config.authProfiles['zai:manual'];

  console.log('Testing Scout agent routing: Gemini Flash vs z.ai GLM-4.7-Flash\n');

  for (const prompt of prompts) {
    console.log(`Prompt: "${prompt}"`);

    // Gemini Flash request
    let geminiResp, zaiResp;
    try {
      geminiResp = await postRequest(
        scoutConfig.endpoints['gemini:flash'].url,
        geminiProfile.apiKey,
        prompt
      );
    } catch (e) {
      console.error('Gemini Flash request failed:', e.message);
      geminiResp = { text: '' };
    }

    // z.ai GLM-4.7-Flash request
    try {
      zaiResp = await postRequest(
        scoutConfig.endpoints['zai:manual'].url,
        zaiProfile.apiKey,
        prompt
      );
    } catch (e) {
      console.error('z.ai GLM-4.7-Flash request failed:', e.message);
      zaiResp = { text: '' };
    }

    const geminiText = geminiResp.text || '';
    const zaiText = zaiResp.text || '';

    // Quality metrics
    const lengthGemini = geminiText.length;
    const lengthZai = zaiText.length;
    const sim = similarity(geminiText, zaiText);

    // Cost estimates
    const costGemini = estimateCost('gemini:flash', geminiText);
    const costZai = estimateCost('zai:manual', zaiText);

    console.log(`  Gemini Flash response length: ${lengthGemini} chars`);
    console.log(`  z.ai GLM-4.7-Flash response length: ${lengthZai} chars`);
    console.log(`  Similarity between responses: ${(sim * 100).toFixed(2)}%`);
    console.log(`  Estimated cost Gemini Flash: $${costGemini.toFixed(5)}`);
    console.log(`  Estimated cost z.ai GLM-4.7-Flash: $${costZai.toFixed(5)}`);
    console.log('---\n');
  }
}

testRouting().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});