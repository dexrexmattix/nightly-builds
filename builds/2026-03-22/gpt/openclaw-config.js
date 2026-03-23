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