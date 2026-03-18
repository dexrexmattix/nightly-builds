---
BUILD TARGET: Integrate z.ai GLM-4.7-Flash API key and create a test proxy in OpenClaw to benchmark cost and quality against Gemini Flash.  
WHY: This will enable Codi to immediately evaluate a cheaper model alternative, potentially reducing API costs while maintaining quality, addressing a high-value cost optimization with minimal setup friction.  
WHAT TO BUILD: Add a new `zai:manual` auth profile in OpenClaw config, create a test routing agent targeting `glm-4.7-flash` via `https://api.z.ai/api/paas/v4/`, and run side-by-side prompt tests comparing responses and token usage to current Gemini Flash. Output a simple cost + quality comparison report.  
STACK: Node.js (OpenClaw config + test script)  
ESTIMATED TIME: 1hr  
---
