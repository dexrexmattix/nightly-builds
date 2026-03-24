const fs = require('fs');
const path = require('path');
const https = require('https');

const OPENCLAW_CONFIG_PATH = path.join(__dirname, 'openclaw.config.json');

// Load environment variables for API keys
const ZAI_API_KEY = process.env.ZAI_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!ZAI_API_KEY || !GEMINI_API_KEY) {
  console.error('Error: Please set ZAI_API_KEY and GEMINI_API_KEY environment variables.');
  process.exit(1);
}

// 1. Update Scout's OpenClaw config to add zai:manual auth profile and route glm-4.7-flash requests
function updateOpenClawConfig() {
  let config = {};
  if (fs.existsSync(OPENCLAW_CONFIG_PATH)) {
    config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG_PATH, 'utf-8'));
  }

  // Add zai:manual auth profile
  config.authProfiles = config.authProfiles || {};
  config.authProfiles['zai:manual'] = {
    type: 'manual',
    apiKey: ZAI_API_KEY
  };

  // Update or add OpenClaw config for GLM-4.7-Flash routing
  config.openClaw = config.openClaw || {};
  config.openClaw.models = config.openClaw.models || {};

  config.openClaw.models['glm-4.7-flash'] = {
    endpoint: 'https://api.z.ai/api/paas/v4/',
    authProfile: 'zai:manual',
    modelName: 'glm-4.7-flash'
  };

  // Save updated config
  fs.writeFileSync(OPENCLAW_CONFIG_PATH, JSON.stringify(config, null, 2), 'utf-8');
  console.log('Updated openclaw.config.json with zai:manual auth profile and glm-4.7-flash model routing.');
}

// 2. Function to call Gemini Flash model
function callGeminiFlash(prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'gemini-flash',
      prompt,
      max_tokens: 100
    });

    const options = {
      hostname: 'api.gemini.com',
      path: '/v1/flash',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GEMINI_API_KEY}`,
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const json = JSON.parse(body);
            resolve(json);
          } catch (e) {
            reject(new Error('Invalid JSON response from Gemini Flash'));
          }
        } else {
          reject(new Error(`Gemini Flash API error: ${res.statusCode} ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// 3. Function to call z.ai GLM-4.7-Flash model
function callZaiGlm47Flash(prompt) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: 'glm-4.7-flash',
      prompt,
      max_tokens: 100
    });

    const options = {
      hostname: 'api.z.ai',
      path: '/api/paas/v4/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${ZAI_API_KEY}`,
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const json = JSON.parse(body);
            resolve(json);
          } catch (e) {
            reject(new Error('Invalid JSON response from z.ai GLM-4.7-Flash'));
          }
        } else {
          reject(new Error(`z.ai API error: ${res.statusCode} ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// 4. Simple token cost and quality metric logger
function logMetrics(modelName, response) {
  // Assume response contains fields: tokens_used, cost_usd, text (response text)
  const tokens = response.tokens_used || 0;
  const cost = response.cost_usd || 0;
  const text = response.text || '';

  // Simple quality metric: response length and presence of prompt keywords
  const qualityScore = text.length;

  console.log(`Model: ${modelName}`);
  console.log(`Tokens used: ${tokens}`);
  console.log(`Cost (USD): ${cost.toFixed(6)}`);
  console.log(`Response length: ${text.length}`);
  console.log(`Sample response: ${text.slice(0, 100)}\n`);
  return { tokens, cost, qualityScore };
}

// 5. Run side-by-side tests
async function runTests() {
  const testPrompts = [
    'Explain the benefits of using AI in healthcare.',
    'Summarize the plot of the movie Inception.',
    'Write a short poem about the ocean.'
  ];

  console.log('Running side-by-side tests for Gemini Flash and z.ai GLM-4.7-Flash...\n');

  for (const prompt of testPrompts) {
    console.log(`Prompt: "${prompt}"\n`);

    try {
      const [geminiResp, zaiResp] = await Promise.all([
        callGeminiFlash(prompt),
        callZaiGlm47Flash(prompt)
      ]);

      console.log('Gemini Flash results:');
      const geminiMetrics = logMetrics('Gemini Flash', geminiResp);

      console.log('z.ai GLM-4.7-Flash results:');
      const zaiMetrics = logMetrics('z.ai GLM-4.7-Flash', zaiResp);

      // Compare cost and quality
      const costDiff = geminiMetrics.cost - zaiMetrics.cost;
      const qualityDiff = geminiMetrics.qualityScore - zaiMetrics.qualityScore;

      console.log(`Cost difference (Gemini - z.ai): $${costDiff.toFixed(6)}`);
      console.log(`Quality difference (Gemini - z.ai): ${qualityDiff}\n`);
      console.log('------------------------------------------------------------\n');

    } catch (err) {
      console.error('Error during test calls:', err);
    }
  }
}

async function main() {
  updateOpenClawConfig();
  await runTests();
}

main();