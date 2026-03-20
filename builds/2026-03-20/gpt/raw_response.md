=== FILENAME: README.md ===
This project integrates the z.ai GLM-4.7-Flash model as a cheaper alternative endpoint for Scout, configured under a new `zai:manual` auth profile. It includes a Node.js test script that sends a batch of typical prompts to both GLM-4.7-Flash and the existing Gemini Flash model endpoints, compares their output quality (via simple text similarity) and token usage, and produces a cost/quality summary report. To run, set your API keys in `.env`, then run `npm install` and `node test.js` from the terminal.

=== END ===
=== FILENAME: .env ===
ZAI_API_KEY=your_zai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

=== END ===
=== FILENAME: openclaw.config.js ===
/**
 * OpenClaw configuration with two auth profiles:
 * - zai:manual for z.ai GLM-4.7-Flash
 * - gemini:flash for current Gemini Flash model
 */
module.exports = {
  authProfiles: {
    'zai:manual': {
      apiKey: process.env.ZAI_API_KEY,
      baseUrl: 'https://api.z.ai/api/paas/v4/',
      model: 'GLM-4.7-Flash',
      // OpenAI-compatible endpoint assumed
    },
    'gemini:flash': {
      apiKey: process.env.GEMINI_API_KEY,
      baseUrl: 'https://api.gemini.com/api/flash/', // example Gemini Flash endpoint
      model: 'Gemini-Flash',
    },
  },
};

=== END ===
=== FILENAME: package.json ===
{
  "name": "zai-glm47-flash-integration",
  "version": "1.0.0",
  "description": "Test integration of z.ai GLM-4.7-Flash vs Gemini Flash with cost and quality comparison",
  "main": "test.js",
  "scripts": {
    "test": "node test.js"
  },
  "dependencies": {
    "axios": "^1.4.0",
    "dotenv": "^16.0.3",
    "string-similarity": "^4.0.4"
  }
}

=== END ===
=== FILENAME: test.js ===
require('dotenv').config();
const axios = require('axios');
const stringSimilarity = require('string-similarity');
const config = require('./openclaw.config.js');

const prompts = [
  "Explain the theory of relativity in simple terms.",
  "Write a short poem about the ocean.",
  "What are the health benefits of green tea?",
  "Summarize the plot of 'To Kill a Mockingbird'.",
  "How do you make a chocolate cake?",
  "Translate 'Good morning' to French.",
  "What is the capital of Australia?",
  "Describe the process of photosynthesis.",
  "List three famous painters from the Renaissance.",
  "What is the meaning of life?"
];

// Cost assumptions (example, adjust as needed)
const COST_PER_1K_TOKENS_ZAI = 0.002; // hypothetical cheaper cost
const COST_PER_1K_TOKENS_GEMINI = 0.01; // example Gemini cost

async function callModel(authProfile, prompt) {
  const { apiKey, baseUrl, model } = authProfile;
  try {
    const response = await axios.post(
      baseUrl + 'chat/completions',
      {
        model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 256,
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 15000,
      }
    );
    // Assume response format includes usage and choices similar to OpenAI
    const data = response.data;
    const text = data.choices?.[0]?.message?.content || '';
    const promptTokens = data.usage?.prompt_tokens || 0;
    const completionTokens = data.usage?.completion_tokens || 0;
    const totalTokens = data.usage?.total_tokens || (promptTokens + completionTokens);
    return { text, promptTokens, completionTokens, totalTokens };
  } catch (error) {
    console.error(`Error calling model ${model}:`, error.response?.data || error.message);
    return { text: '', promptTokens: 0, completionTokens: 0, totalTokens: 0 };
  }
}

function calculateCost(tokens, costPer1k) {
  return (tokens / 1000) * costPer1k;
}

function similarityScore(text1, text2) {
  return stringSimilarity.compareTwoStrings(text1, text2);
}

async function runComparison() {
  console.log('Starting batch test for z.ai GLM-4.7-Flash vs Gemini Flash...\n');

  const zaiProfile = config.authProfiles['zai:manual'];
  const geminiProfile = config.authProfiles['gemini:flash'];

  if (!zaiProfile.apiKey || !geminiProfile.apiKey) {
    console.error('Please set both ZAI_API_KEY and GEMINI_API_KEY in .env file.');
    process.exit(1);
  }

  let totalZaiTokens = 0;
  let totalGeminiTokens = 0;
  let totalSimilarity = 0;
  let count = 0;

  for (const prompt of prompts) {
    console.log(`Prompt #${count + 1}: ${prompt}`);

    const [zaiResult, geminiResult] = await Promise.all([
      callModel(zaiProfile, prompt),
      callModel(geminiProfile, prompt),
    ]);

    if (!zaiResult.text || !geminiResult.text) {
      console.log('Skipping this prompt due to error in API call.\n');
      continue;
    }

    const sim = similarityScore(zaiResult.text, geminiResult.text);
    totalSimilarity += sim;
    totalZaiTokens += zaiResult.totalTokens;
    totalGeminiTokens += geminiResult.totalTokens;
    count++;

    console.log(`- z.ai output: ${zaiResult.text.substring(0, 100)}${zaiResult.text.length > 100 ? '...' : ''}`);
    console.log(`- Gemini output: ${geminiResult.text.substring(0, 100)}${geminiResult.text.length > 100 ? '...' : ''}`);
    console.log(`- Similarity score: ${(sim * 100).toFixed(2)}%`);
    console.log(`- z.ai tokens: ${zaiResult.totalTokens}, Gemini tokens: ${geminiResult.totalTokens}\n`);
  }

  if (count === 0) {
    console.log('No successful prompt comparisons to report.');
    return;
  }

  const avgSimilarity = totalSimilarity / count;
  const zaiCost = calculateCost(totalZaiTokens, COST_PER_1K_TOKENS_ZAI);
  const geminiCost = calculateCost(totalGeminiTokens, COST_PER_1K_TOKENS_GEMINI);

  console.log('=== Summary Report ===');
  console.log(`Prompts tested: ${count}`);
  console.log(`Average similarity score: ${(avgSimilarity * 100).toFixed(2)}%`);
  console.log(`Total tokens used by z.ai GLM-4.7-Flash: ${totalZaiTokens}`);
  console.log(`Total tokens used by Gemini Flash: ${totalGeminiTokens}`);
  console.log(`Estimated cost for z.ai GLM-4.7-Flash: $${zaiCost.toFixed(4)}`);
  console.log(`Estimated cost for Gemini Flash: $${geminiCost.toFixed(4)}`);
  console.log(`Cost savings: $${(geminiCost - zaiCost).toFixed(4)} (${(((geminiCost - zaiCost) / geminiCost) * 100).toFixed(2)}%)`);
}

runComparison();

=== END ===