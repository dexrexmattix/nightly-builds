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