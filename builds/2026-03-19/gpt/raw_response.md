=== FILENAME: README.md ===
This project provides a Node.js script to benchmark the z.ai GLM-4.7-Flash model against the current Gemini Flash model used by the Scout agent. It configures a new `zai:manual` auth profile and redirects API calls to the z.ai endpoint for GLM-4.7-Flash, then runs side-by-side prompt tests comparing response quality and token costs. To run, install dependencies with `npm install` and execute `node benchmark.js`. The script outputs prompt responses, token usage, and cost estimates for both models to help evaluate cost savings and quality retention.

=== END ===
=== FILENAME: package.json ===
{
  "name": "scout-agent-zai-benchmark",
  "version": "1.0.0",
  "description": "Benchmark z.ai GLM-4.7-Flash vs Gemini Flash for Scout agent",
  "main": "benchmark.js",
  "scripts": {
    "start": "node benchmark.js"
  },
  "dependencies": {
    "axios": "^1.4.0"
  }
}
=== END ===
=== FILENAME: benchmark.js ===
const axios = require("axios");

// Configuration for Gemini Flash (current)
const GEMINI_API_BASE = "https://api.scout.gemini.com/v1/flash";
const GEMINI_AUTH = {
  type: "apiKey",
  key: process.env.GEMINI_API_KEY || "your_gemini_api_key_here"
};
const GEMINI_MODEL = "gemini-flash";

// Configuration for z.ai GLM-4.7-Flash (alternative)
const ZAI_API_BASE = "https://api.z.ai/api/paas/v4/";
const ZAI_AUTH = {
  type: "manual",
  apiKey: process.env.ZAI_API_KEY || "your_zai_api_key_here"
};
const ZAI_MODEL = "GLM-4.7-Flash";

// Cost per 1000 tokens (example values, adjust as needed)
const COST_PER_1000_GEMINI = 0.03; // $0.03 per 1000 tokens
const COST_PER_1000_ZAI = 0.015;   // $0.015 per 1000 tokens (cheaper alternative)

// Prompts to test
const TEST_PROMPTS = [
  "Explain the theory of relativity in simple terms.",
  "Write a short poem about the ocean.",
  "Summarize the latest news about climate change.",
  "Generate a creative startup idea in the education sector.",
  "Translate 'Hello, how are you?' into French."
];

// Helper: call Gemini Flash API
async function callGemini(prompt) {
  try {
    const response = await axios.post(
      `${GEMINI_API_BASE}/generate`,
      {
        model: GEMINI_MODEL,
        prompt: prompt,
        max_tokens: 150
      },
      {
        headers: {
          "Authorization": `Bearer ${GEMINI_AUTH.key}`,
          "Content-Type": "application/json"
        }
      }
    );
    // Assuming response includes usage info
    return {
      text: response.data.choices?.[0]?.text || "",
      tokens: response.data.usage?.total_tokens || 0
    };
  } catch (error) {
    console.error("Gemini API error:", error.response?.data || error.message);
    return { text: "", tokens: 0 };
  }
}

// Helper: call z.ai GLM-4.7-Flash API
async function callZai(prompt) {
  try {
    const response = await axios.post(
      `${ZAI_API_BASE}completion`,
      {
        model: ZAI_MODEL,
        prompt: prompt,
        max_tokens: 150
      },
      {
        headers: {
          "Authorization": `Bearer ${ZAI_AUTH.apiKey}`,
          "Content-Type": "application/json"
        }
      }
    );
    // Assuming response format similar to OpenAI style
    return {
      text: response.data.choices?.[0]?.text || "",
      tokens: response.data.usage?.total_tokens || 0
    };
  } catch (error) {
    console.error("z.ai API error:", error.response?.data || error.message);
    return { text: "", tokens: 0 };
  }
}

// Calculate cost given tokens and cost per 1000 tokens
function calculateCost(tokens, costPerThousand) {
  return (tokens / 1000) * costPerThousand;
}

async function runBenchmark() {
  console.log("Starting side-by-side benchmark of Gemini Flash vs z.ai GLM-4.7-Flash\n");

  for (const prompt of TEST_PROMPTS) {
    console.log("Prompt:");
    console.log(prompt);
    console.log();

    const [geminiResult, zaiResult] = await Promise.all([
      callGemini(prompt),
      callZai(prompt)
    ]);

    const geminiCost = calculateCost(geminiResult.tokens, COST_PER_1000_GEMINI);
    const zaiCost = calculateCost(zaiResult.tokens, COST_PER_1000_ZAI);

    console.log("Gemini Flash Response:");
    console.log(geminiResult.text.trim());
    console.log(`Tokens used: ${geminiResult.tokens}, Estimated cost: $${geminiCost.toFixed(5)}`);
    console.log();

    console.log("z.ai GLM-4.7-Flash Response:");
    console.log(zaiResult.text.trim());
    console.log(`Tokens used: ${zaiResult.tokens}, Estimated cost: $${zaiCost.toFixed(5)}`);
    console.log();

    console.log("------------------------------------------------------------\n");
  }

  console.log("Benchmark complete.");
}

runBenchmark();

=== END ===