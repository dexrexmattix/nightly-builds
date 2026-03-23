---
BUILD TARGET: Integrate and test GLM-4.7-Flash model in OpenClaw as a drop-in cheaper alternative for Scout agent routing.  
WHY: This will reduce Dex’s API costs for high-volume agents by switching to a lower-cost, OpenAI-compatible model without disrupting current workflows.  
WHAT TO BUILD: Add `zai:manual` auth profile with API key from z.ai, configure Scout to route requests to GLM-4.7-Flash via base URL swap, run side-by-side quality and cost comparison with existing Gemini Flash model.  
STACK: Node.js (OpenClaw config + test script)  
ESTIMATED TIME: 1hr  
---
