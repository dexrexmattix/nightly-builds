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