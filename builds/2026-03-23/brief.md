---
BUILD TARGET: Integrate z.ai GLM-4.7-Flash model into Scout as a drop-in cheaper alternative to Gemini Flash for cost savings and quality comparison.  
WHY: This will reduce token costs for Scout’s high-volume usage immediately and provide data on quality tradeoffs to decide if it can replace the current expensive Flash model.  
WHAT TO BUILD: Add a zai:manual auth profile with z.ai API key, update Scout’s OpenClaw config to route requests to `glm-4.7-flash` via `https://api.z.ai/api/paas/v4/`, then run side-by-side tests logging cost and response quality metrics.  
STACK: Node.js or Python scripting to modify config + test calls; minimal integration code update.  
ESTIMATED TIME: 1hr  
---
