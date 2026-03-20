---
BUILD TARGET: Integrate and test z.ai GLM-4.7-Flash as a cheaper model endpoint for Scout with cost and quality comparison.  
WHY: This could reduce API costs significantly by switching to a cheaper, OpenAI-compatible model without losing quality, directly impacting monthly expenses.  
WHAT TO BUILD: Add a `zai:manual` auth profile for GLM-4.7-Flash, configure Scout or a dedicated test agent to route requests to `https://api.z.ai/api/paas/v4/` with the new key, then run a batch of typical prompts to compare output quality and token costs versus current Gemini Flash. Produce a simple cost/quality summary report.  
STACK: node (OpenClaw config + test script)  
ESTIMATED TIME: 1hr  
---
