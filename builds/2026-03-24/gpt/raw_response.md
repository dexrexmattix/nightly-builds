=== FILENAME: README.md ===
This script integrates the GLM-4.7-Flash model as a drop-in alternative to Gemini Flash in the Scout agent for cost and quality comparison. It sets up a `zai:manual` auth profile with the GLM API key, runs a batch of typical prompts against both GLM-4.7-Flash and Gemini Flash endpoints, and logs the quality (response length and simple similarity) and estimated cost metrics for each. To run, set your API keys in environment variables `GLM_API_KEY` and `GEMINI_API_KEY`, then execute `node scout-glm-vs-gemini.js` in a terminal with Node.js installed.

=== END ===

=== FILENAME: scout-glm-vs-gemini.js ===
```js
/**
 * Scout agent GLM-4.7-Flash vs Gemini Flash comparison script
 *
 * Usage:
 *   Set environment variables GLM_API_KEY and GEMINI_API_KEY with your API keys.
 *   Run: node scout-glm-vs-gemini.js
 *
 * This script:
 * - Defines a zai:manual auth profile for GLM-4.7-Flash
 * - Sends a batch of prompts to GLM-4.7-Flash and Gemini Flash endpoints
 * - Logs responses, estimated costs, and a simple quality metric (response length and token overlap)
 */

import fetch from "node-fetch";

const GLM_API_KEY = process.env.GLM_API_KEY;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!GLM_API_KEY || !GEMINI_API_KEY) {
  console.error("ERROR: Please set GLM_API_KEY and GEMINI_API_KEY environment variables.");
  process.exit(1);
}

// Config for GLM-4.7-Flash
const GLM_AUTH_PROFILE = {
  name: "zai:manual",
  apiKey: GLM_API_KEY,
  endpoint: "https://api.openai.com/v1/engines/glm-4.7-flash/completions",
  modelName: "glm-4.7-flash",
  costPer1KTokens: 0.002, // hypothetical cost per 1k tokens for GLM-4.7-Flash
};

// Config for Gemini Flash baseline
const GEMINI_AUTH_PROFILE = {
  name: "gemini:flash",
  apiKey: GEMINI_API_KEY,
  endpoint: "https://api.openai.com/v1/engines/gemini-flash/completions",
  modelName: "gemini-flash",
  costPer1KTokens: 0.006, // hypothetical cost per 1k tokens for Gemini Flash
};

// Typical prompts batch for testing
const PROMPTS = [
  "Explain the theory of relativity in simple terms.",
  "Write a short poem about the ocean.",
  "What are the health benefits of green tea?",
  "Summarize the plot of 'Pride and Prejudice'.",
  "How do you make a chocolate cake?",
];

// Helper: call OpenAI-compatible completion endpoint
async function callCompletion({endpoint, apiKey, prompt}) {
  const body = {
    prompt,
    max_tokens: 100,
    temperature: 0.7,
    n: 1,
    stop: null,
  };

  const res = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API error: ${res.status} ${res.statusText} - ${errText}`);
  }

  const data = await res.json();
  // OpenAI completion response shape: {choices: [{text: "..."}]}
  return data.choices[0].text.trim();
}

// Simple quality metric: token overlap ratio between prompt and response tokens
function tokenOverlapRatio(prompt, response) {
  const promptTokens = new Set(prompt.toLowerCase().split(/\W+/).filter(Boolean));
  const responseTokens = new Set(response.toLowerCase().split(/\W+/).filter(Boolean));
  if (promptTokens.size === 0) return 0;
  let overlapCount = 0;
  for (const t of promptTokens) {
    if (responseTokens.has(t)) overlapCount++;
  }
  return overlapCount / promptTokens.size;
}

// Estimate tokens count (rough): words count * 1.3 (approx)
function estimateTokens(text) {
  const words = text.trim().split(/\s+/).length;
  return Math.ceil(words * 1.3);
}

async function runComparison() {
  console.log("Running GLM-4.7-Flash vs Gemini Flash comparison...\n");

  for (const prompt of PROMPTS) {
    console.log(`Prompt: "${prompt}"`);

    // Call GLM-4.7-Flash
    let glmResponse;
    try {
      glmResponse = await callCompletion({
        endpoint: GLM_AUTH_PROFILE.endpoint,
        apiKey: GLM_AUTH_PROFILE.apiKey,
        prompt,
      });
    } catch (e) {
      console.error("GLM call failed:", e.message);
      continue;
    }

    // Call Gemini Flash
    let geminiResponse;
    try {
      geminiResponse = await callCompletion({
        endpoint: GEMINI_AUTH_PROFILE.endpoint,
        apiKey: GEMINI_AUTH_PROFILE.apiKey,
        prompt,
      });
    } catch (e) {
      console.error("Gemini call failed:", e.message);
      continue;
    }

    // Estimate tokens and costs
    const glmPromptTokens = estimateTokens(prompt);
    const glmResponseTokens = estimateTokens(glmResponse);
    const glmTotalTokens = glmPromptTokens + glmResponseTokens;
    const glmCost = (glmTotalTokens / 1000) * GLM_AUTH_PROFILE.costPer1KTokens;

    const geminiPromptTokens = estimateTokens(prompt);
    const geminiResponseTokens = estimateTokens(geminiResponse);
    const geminiTotalTokens = geminiPromptTokens + geminiResponseTokens;
    const geminiCost = (geminiTotalTokens / 1000) * GEMINI_AUTH_PROFILE.costPer1KTokens;

    // Quality metrics (token overlap ratio)
    const glmQuality = tokenOverlapRatio(prompt, glmResponse);
    const geminiQuality = tokenOverlapRatio(prompt, geminiResponse);

    console.log(`GLM-4.7-Flash response: "${glmResponse}"`);
    console.log(`  Tokens: prompt=${glmPromptTokens}, response=${glmResponseTokens}, total=${glmTotalTokens}`);
    console.log(`  Estimated cost: $${glmCost.toFixed(5)}`);
    console.log(`  Quality (token overlap): ${(glmQuality * 100).toFixed(1)}%`);

    console.log(`Gemini Flash response: "${geminiResponse}"`);
    console.log(`  Tokens: prompt=${geminiPromptTokens}, response=${geminiResponseTokens}, total=${geminiTotalTokens}`);
    console.log(`  Estimated cost: $${geminiCost.toFixed(5)}`);
    console.log(`  Quality (token overlap): ${(geminiQuality * 100).toFixed(1)}%`);

    console.log("------------------------------------------------------------\n");
  }

  console.log("Comparison complete.");
}

runComparison().catch((e) => {
  console.error("Fatal error:", e);
  process.exit(1);
});
=== END ===