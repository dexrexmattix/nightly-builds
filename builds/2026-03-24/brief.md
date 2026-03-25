---
BUILD TARGET: Integrate and test GLM-4.7-Flash model in Scout agent as a drop-in alternative to Gemini Flash for cost and quality comparison.  
WHY: This will potentially reduce model API costs on high-volume agents by leveraging a cheaper OpenAI-compatible model without disrupting existing workflows.  
WHAT TO BUILD: A short script or config update that adds a `zai:manual` auth profile with the GLM-4.7-Flash API key, points Scout at `glm-4.7-flash` endpoint, runs a batch of typical prompts, and logs quality and cost metrics versus Gemini Flash baseline.  
STACK: Node.js or Python script (whichever Scout currently uses for config and testing)  
ESTIMATED TIME: 1hr  
---
