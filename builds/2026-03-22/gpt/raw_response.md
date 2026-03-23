=== FILENAME: README.md ===
This project integrates the GLM-4.7-Flash model from z.ai as a drop-in alternative to the Gemini Flash model in the OpenClaw Scout agent routing system. It adds a new `zai:manual` authentication profile with an API key, configures Scout to route requests to GLM-4.7-Flash by swapping the base URL, and includes a test script to run side-by-side quality and cost comparisons between the existing Gemini Flash model and the new GLM-4.7-Flash model. To run, set your z.ai API key in the environment variable `ZAI_API_KEY`, then run `node test.js` in the terminal.

=== END ===

=== FILENAME: openclaw-config.js ===
module.exports = {
  authProfiles: {
    // Existing Gemini Flash auth profile (example)
    gemini: {
      apiKey: process.env.GEMINI_API_KEY || 'your-gemini-api-key',
      baseUrl: 'https://api.gemini.openai.com/v1/chat/completions',
    },
    // New zai:manual auth profile for GLM-4.7-Flash
    'zai:manual': {
      apiKey: process.env.ZAI_API_KEY || 'your-zai-api-key',
      baseUrl: 'https://api.z.ai/v1/chat/completions',
    },
  },

  // Scout routing config
  scoutRouting: {
    // Default route uses Gemini Flash
    defaultModel: 'gemini',
    // Model configs
    models: {
      gemini: {
        authProfile: 'gemini',
        modelName: 'gemini-flash',
      },
      glmFlash: {
        authProfile: 'zai:manual',
        modelName: 'glm-4.7-flash',
      },
    },
  },
};
=== END ===

=== FILENAME: test.js ===
const https = require('https');
const openclawConfig = require('./openclaw-config');

const GEMINI_MODEL = openclawConfig.scoutRouting.models.gemini;
const GLM_MODEL = openclawConfig.scoutRouting.models.glmFlash;

const GEMINI_AUTH = openclawConfig.authProfiles[GEMINI_MODEL.authProfile];
const GLM_AUTH = openclawConfig.authProfiles[GLM_MODEL.authProfile];

// Sample prompt for testing
const PROMPT = [
  { role: 'system', content: 'You are a helpful assistant.' },
  { role: 'user', content: 'Explain the benefits of using GLM-4.7-Flash over Gemini Flash.' },
];

// Helper to make POST request to chat completions endpoint
function callModel({ baseUrl, apiKey, modelName, messages }) {
  return new Promise((resolve, reject) => {
    const url = new URL(baseUrl);
    const data = JSON.stringify({
      model: modelName,
      messages,
    });

    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
        'Authorization': `Bearer ${apiKey}`,
      },
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            const json = JSON.parse(body);
            resolve(json);
          } catch (e) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body}`));
        }
      });
    });

    req.on('error', (e) => reject(e));
    req.write(data);
    req.end();
  });
}

async function runComparison() {
  console.log('Starting side-by-side comparison of Gemini Flash and GLM-4.7-Flash models...\n');

  try {
    console.log('Calling Gemini Flash model...');
    const geminiStart = Date.now();
    const geminiResponse = await callModel({
      baseUrl: GEMINI_AUTH.baseUrl,
      apiKey: GEMINI_AUTH.apiKey,
      modelName: GEMINI_MODEL.modelName,
      messages: PROMPT,
    });
    const geminiDuration = Date.now() - geminiStart;

    console.log('Gemini Flash response received.');
    const geminiText = geminiResponse.choices?.[0]?.message?.content || '[No content]';

    console.log('\nCalling GLM-4.7-Flash model...');
    const glmStart = Date.now();
    const glmResponse = await callModel({
      baseUrl: GLM_AUTH.baseUrl,
      apiKey: GLM_AUTH.apiKey,
      modelName: GLM_MODEL.modelName,
      messages: PROMPT,
    });
    const glmDuration = Date.now() - glmStart;

    console.log('GLM-4.7-Flash response received.');
    const glmText = glmResponse.choices?.[0]?.message?.content || '[No content]';

    console.log('\n--- Results ---');
    console.log(`Gemini Flash (model: ${GEMINI_MODEL.modelName}) response time: ${geminiDuration} ms`);
    console.log(`Response:\n${geminiText}\n`);

    console.log(`GLM-4.7-Flash (model: ${GLM_MODEL.modelName}) response time: ${glmDuration} ms`);
    console.log(`Response:\n${glmText}\n`);

    console.log('Note: Compare the quality and cost of these responses to decide on switching.');
  } catch (err) {
    console.error('Error during comparison:', err.message);
  }
}

runComparison();

=== END ===