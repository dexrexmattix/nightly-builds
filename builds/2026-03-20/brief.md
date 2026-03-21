---
BUILD TARGET: Integrate z.ai GLM-4.7-Flash model as a drop-in alternative routing option for Scout to benchmark cost and quality against Gemini Flash.  
WHY: This will provide immediate cost savings potential on high-volume agent calls by switching to a cheaper, OpenAI-compatible model without changing code structure, enabling Codi to reduce API spend while maintaining quality.  
WHAT TO BUILD: Add a new `zai:manual` auth profile with z.ai API key and update Scout agent’s config to route requests to `https://api.z.ai/api/paas/v4/` using GLM-4.7-Flash model; then run comparative test queries and log cost + output quality.  
STACK: node / TypeScript (existing OpenClaw agent config and test harness)  
ESTIMATED TIME: 1hr  
---
