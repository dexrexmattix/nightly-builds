module.exports = {
  agents: {
    scout: {
      // Existing config for Scout agent
      modelRouting: {
        default: 'gemini:flash',
        cheaperOption: 'zai:manual'
      },
      endpoints: {
        'gemini:flash': {
          url: 'https://api.gemini.com/flash',
          authProfile: 'gemini:flash'
        },
        'zai:manual': {
          url: 'https://api.z.ai/api/paas/v4/',
          authProfile: 'zai:manual'
        }
      }
    }
  },
  authProfiles: {
    'gemini:flash': {
      apiKey: process.env.GEMINI_API_KEY || 'your-gemini-api-key'
    },
    'zai:manual': {
      apiKey: process.env.ZAI_API_KEY || 'your-zai-api-key'
    }
  }
};