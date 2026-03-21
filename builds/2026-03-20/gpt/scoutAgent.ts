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