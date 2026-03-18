=== FILENAME: README.md ===
This project integrates the z.ai GLM-4.7-Flash API into OpenClaw as a new `zai:manual` auth profile and creates a test routing agent to benchmark cost and quality against the existing Gemini Flash model. It runs side-by-side prompt tests, comparing responses and token usage, and outputs a simple cost and quality comparison report. To run, set your API keys in the `.env` file, then execute `node test.js` in the terminal.

=== END ===
=== FILENAME: .env ===
ZAI_API_KEY=your_zai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
=== END ===
=== FILENAME: openclaw.config.js ===
require('dotenv').config();

module.exports = {
  authProfiles: {
    'zai:manual': {
      apiKey: process.env.ZAI_API_KEY,
      baseUrl: 'https://api.z.ai/api/paas/v4/',
      model: 'glm-4.7-flash',
      headers: {
        'Authorization': `Bearer ${process.env.ZAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    },
    'gemini:flash': {
      apiKey: process.env.GEMINI_API_KEY,
      baseUrl: 'https://api.gemini.com/v1/flash/', // Placeholder Gemini Flash URL
      model: 'gemini-flash',
      headers: {
        'Authorization': `Bearer ${process.env.GEMINI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    },
  },

  routingAgents: {
    zaiTestAgent: {
      authProfile: 'zai:manual',
      endpoint: 'chat/completions',
      model: 'glm-4.7-flash',
    },
    geminiTestAgent: {
      authProfile: 'gemini:flash',
      endpoint: 'chat/completions',
      model: 'gemini-flash',
    },
  },

  costPerToken: {
    'glm-4.7-flash': 0.0001, // example cost per token in USD
    'gemini-flash': 0.00015, // example cost per token in USD
  },
};
=== END ===
=== FILENAME: test.js ===
require('dotenv').config();
const fetch = require('node-fetch');
const config = require('./openclaw.config.js');

const prompts = [
  "Explain the theory of relativity in simple terms.",
  "Write a short poem about the ocean.",
  "What are the health benefits of green tea?",
];

async function callModel(authProfile, routingAgent, prompt) {
  const profile = config.authProfiles[authProfile];
  const agent = config.routingAgents[routingAgent];

  const url = profile.baseUrl + agent.endpoint;

  const body = {
    model: agent.model,
    messages: [{ role: "user", content: prompt }],
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: profile.headers,
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error: ${response.status} ${response.statusText} - ${text}`);
  }

  const data = await response.json();

  // Assuming response format:
  // {
  //   choices: [{ message: { content: "response text" } }],
  //   usage: { prompt_tokens: X, completion_tokens: Y, total_tokens: Z }
  // }

  const message = data.choices?.[0]?.message?.content || "";
  const usage = data.usage || { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };

  return { message, usage };
}

function simpleSimilarity(a, b) {
  // Basic similarity: ratio of common words to average word count
  const aWords = a.toLowerCase().split(/\W+/).filter(Boolean);
  const bWords = b.toLowerCase().split(/\W+/).filter(Boolean);
  const setA = new Set(aWords);
  const setB = new Set(bWords);
  const common = [...setA].filter(x => setB.has(x));
  const avgLen = (aWords.length + bWords.length) / 2 || 1;
  return common.length / avgLen;
}

async function runTests() {
  console.log("Running side-by-side tests for prompts...\n");

  const results = [];

  for (const prompt of prompts) {
    console.log(`Prompt: "${prompt}"\n`);

    let zaiResult, geminiResult;
    try {
      zaiResult = await callModel('zai:manual', 'zaiTestAgent', prompt);
    } catch (e) {
      console.error("Error calling z.ai GLM-4.7-Flash:", e.message);
      zaiResult = { message: "", usage: { total_tokens: 0 } };
    }

    try {
      geminiResult = await callModel('gemini:flash', 'geminiTestAgent', prompt);
    } catch (e) {
      console.error("Error calling Gemini Flash:", e.message);
      geminiResult = { message: "", usage: { total_tokens: 0 } };
    }

    const similarity = simpleSimilarity(zaiResult.message, geminiResult.message);

    const zaiCost = (zaiResult.usage.total_tokens || 0) * (config.costPerToken['glm-4.7-flash'] || 0);
    const geminiCost = (geminiResult.usage.total_tokens || 0) * (config.costPerToken['gemini-flash'] || 0);

    results.push({
      prompt,
      zai: {
        response: zaiResult.message,
        tokens: zaiResult.usage.total_tokens,
        cost: zaiCost,
      },
      gemini: {
        response: geminiResult.message,
        tokens: geminiResult.usage.total_tokens,
        cost: geminiCost,
      },
      similarity,
    });

    console.log(`z.ai GLM-4.7-Flash response tokens: ${zaiResult.usage.total_tokens}, cost: $${zaiCost.toFixed(5)}`);
    console.log(`Gemini Flash response tokens: ${geminiResult.usage.total_tokens}, cost: $${geminiCost.toFixed(5)}`);
    console.log(`Response similarity (0-1): ${similarity.toFixed(2)}\n`);
  }

  // Summary report
  console.log("\n=== Summary Report ===\n");
  results.forEach(({ prompt, zai, gemini, similarity }, i) => {
    console.log(`Test ${i + 1}: "${prompt}"`);
    console.log(`  z.ai tokens: ${zai.tokens}, cost: $${zai.cost.toFixed(5)}`);
    console.log(`  Gemini tokens: ${gemini.tokens}, cost: $${gemini.cost.toFixed(5)}`);
    console.log(`  Similarity score: ${similarity.toFixed(2)}`);
    console.log('');
  });

  // Aggregate cost and similarity
  const totalZaiCost = results.reduce((a, r) => a + r.zai.cost, 0);
  const totalGeminiCost = results.reduce((a, r) => a + r.gemini.cost, 0);
  const avgSimilarity = results.reduce((a, r) => a + r.similarity, 0) / results.length;

  console.log(`Total z.ai cost: $${totalZaiCost.toFixed(5)}`);
  console.log(`Total Gemini cost: $${totalGeminiCost.toFixed(5)}`);
  console.log(`Average similarity: ${avgSimilarity.toFixed(2)}`);

  if (totalZaiCost < totalGeminiCost) {
    console.log("\nCost Optimization: z.ai GLM-4.7-Flash is cheaper.");
  } else {
    console.log("\nCost Optimization: Gemini Flash is cheaper.");
  }

  if (avgSimilarity > 0.7) {
    console.log("Quality: Responses are similar enough to consider z.ai a viable alternative.");
  } else {
    console.log("Quality: Responses differ significantly; further evaluation needed.");
  }
}

runTests().catch(e => {
  console.error("Fatal error:", e);
  process.exit(1);
});
=== END ===