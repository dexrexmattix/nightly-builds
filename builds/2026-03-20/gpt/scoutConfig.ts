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