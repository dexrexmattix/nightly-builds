This project integrates the z.ai GLM-4.7-Flash model into Scout as a drop-in cheaper alternative to Gemini Flash. It updates Scout's OpenClaw configuration to add a `zai:manual` auth profile with your z.ai API key and routes requests to the GLM-4.7-Flash model endpoint. The included script runs side-by-side test calls to both Gemini Flash and z.ai GLM-4.7-Flash models, logging token costs and response quality metrics for comparison. To run, set your API keys in environment variables and execute the test script via Node.js.

Usage:
1. Set environment variables:
   - ZAI_API_KEY (your z.ai API key)
   - GEMINI_API_KEY (your Gemini Flash API key)
2. Run `node integrate_and_test.js`

This will update the config file `openclaw.config.json` and perform test calls, outputting cost and quality logs.