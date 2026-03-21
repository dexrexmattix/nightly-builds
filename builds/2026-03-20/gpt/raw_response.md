=== FILENAME: README.md ===
This project adds a new `zai:manual` authentication profile for the z.ai GLM-4.7-Flash model and updates the Scout agent configuration to route requests to z.ai's API endpoint. It includes a test script that sends comparative queries to both the z.ai GLM-4.7-Flash model and the existing Gemini Flash model, logging the cost and output quality for benchmarking purposes. To run, install dependencies with `npm install` and execute `npm run test` to see the comparative results in the console.

=== END ===
=== FILENAME: package.json ===
{
  "name": "scout-zai-integration",
  "version": "1.0.0",
  "description": "Scout agent integration with z.ai GLM-4.7-Flash model for benchmarking",
  "main": "test.ts",
  "scripts": {
    "test": "ts-node test.ts"
  },
  "dependencies": {
    "axios": "^1.4.0",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "@types/node": "^20.3.1",
    "ts-node": "^10.9.1",
    "typescript": "^5.1.3"
  }
}
=== END ===
=== FILENAME: .env ===
# Put your API keys here
ZAI_API_KEY=your_zai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
=== END ===
=== FILENAME: scoutConfig.ts ===
import dotenv from 'dotenv';
dotenv.config();

export interface AuthProfile {
  type: string;
  apiKey: string;
  baseUrl: string;
  model: string;
}

export interface ScoutConfig {
  authProfiles: Record<string, AuthProfile>;
  defaultProfile: string;
}

export const scoutConfig: ScoutConfig = {
  authProfiles: {
    // Existing Gemini Flash profile
    'gemini:flash': {
      type: 'openai-compatible',
      apiKey: process.env.GEMINI_API_KEY || '',
      baseUrl: 'https://api.gemini.com/v1/',
      model: 'gemini-flash',
    },

    // New z.ai GLM-4.7-Flash profile
    'zai:manual': {
      type: 'openai-compatible',
      apiKey: process.env.ZAI_API_KEY || '',
      baseUrl: 'https://api.z.ai/api/paas/v4/',
      model: 'GLM-4.7-Flash',
    },
  },
  defaultProfile: 'gemini:flash',
};
=== END ===
=== FILENAME: scoutAgent.ts ===
import axios from 'axios';
import { AuthProfile } from './scoutConfig';

export interface AgentResponse {
  output: string;
  cost: number; // in USD
  rawResponse: any;
}

export class ScoutAgent {
  private profile: AuthProfile;

  constructor(profile: AuthProfile) {
    if (!profile.apiKey) {
      throw new Error(`API key missing for profile: ${profile.type}`);
    }
    this.profile = profile;
  }

  /**
   * Sends a prompt to the configured model endpoint and returns the output and cost.
   * Assumes OpenAI-compatible API.
   */
  async query(prompt: string): Promise<AgentResponse> {
    const url = this.profile.baseUrl + 'chat/completions';

    // Construct request payload
    const data = {
      model: this.profile.model,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,
      max_tokens: 256,
    };

    try {
      const response = await axios.post(url, data, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.profile.apiKey}`,
        },
        timeout: 15000,
      });

      // Extract output text
      const output = response.data.choices?.[0]?.message?.content || '';

      // Extract usage tokens for cost calculation
      const usage = response.data.usage || {};
      const promptTokens = usage.prompt_tokens || 0;
      const completionTokens = usage.completion_tokens || 0;
      const totalTokens = usage.total_tokens || promptTokens + completionTokens;

      // Cost calculation per token (example rates, adjust as needed)
      // Gemini Flash assumed $0.0004 per 1k tokens
      // z.ai GLM-4.7-Flash assumed $0.0002 per 1k tokens (cheaper)
      let costPerThousandTokens = 0.0004;
      if (this.profile.type === 'openai-compatible' && this.profile.model === 'GLM-4.7-Flash') {
        costPerThousandTokens = 0.0002;
      }

      const cost = (totalTokens / 1000) * costPerThousandTokens;

      return {
        output,
        cost,
        rawResponse: response.data,
      };
    } catch (error: any) {
      throw new Error(`Agent query failed: ${error.message || error}`);
    }
  }
}
=== END ===
=== FILENAME: test.ts ===
import { scoutConfig } from './scoutConfig';
import { ScoutAgent } from './scoutAgent';

async function runComparativeTest() {
  const testPrompt = `Explain the benefits of using a cheaper OpenAI-compatible model for high-volume agent calls.`;

  console.log('Starting comparative test between Gemini Flash and z.ai GLM-4.7-Flash...\n');

  // Gemini Flash agent
  const geminiProfile = scoutConfig.authProfiles['gemini:flash'];
  const geminiAgent = new ScoutAgent(geminiProfile);

  // z.ai GLM-4.7-Flash agent
  const zaiProfile = scoutConfig.authProfiles['zai:manual'];
  const zaiAgent = new ScoutAgent(zaiProfile);

  try {
    console.log('Querying Gemini Flash model...');
    const geminiResult = await geminiAgent.query(testPrompt);
    console.log('Gemini Flash output:\n', geminiResult.output);
    console.log(`Gemini Flash cost: $${geminiResult.cost.toFixed(6)}\n`);

    console.log('Querying z.ai GLM-4.7-Flash model...');
    const zaiResult = await zaiAgent.query(testPrompt);
    console.log('z.ai GLM-4.7-Flash output:\n', zaiResult.output);
    console.log(`z.ai GLM-4.7-Flash cost: $${zaiResult.cost.toFixed(6)}\n`);

    // Basic output quality comparison (length and similarity)
    const geminiLength = geminiResult.output.length;
    const zaiLength = zaiResult.output.length;

    console.log('Output length comparison:');
    console.log(`Gemini Flash output length: ${geminiLength}`);
    console.log(`z.ai GLM-4.7-Flash output length: ${zaiLength}`);

    // Simple similarity check: number of common words
    const geminiWords = new Set(geminiResult.output.toLowerCase().split(/\W+/));
    const zaiWords = new Set(zaiResult.output.toLowerCase().split(/\W+/));
    const commonWords = [...geminiWords].filter(w => zaiWords.has(w) && w.length > 3);

    console.log(`Common words (length > 3): ${commonWords.length}`);
    console.log('Sample common words:', commonWords.slice(0, 10).join(', '));

    console.log('\nComparative test completed.');
  } catch (err) {
    console.error('Error during comparative test:', err);
  }
}

runComparativeTest();
=== END ===
=== FILENAME: tsconfig.json ===
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist"
  },
  "include": ["*.ts"]
}
=== END ===