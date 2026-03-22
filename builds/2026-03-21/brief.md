---
BUILD TARGET: Integrate z.ai GLM-4.7-Flash model as a drop-in cheaper routing option for Scout agent in OpenClaw and benchmark cost+quality against current Gemini Flash.

WHY: This can immediately reduce API costs for high-volume agents like Scout while maintaining quality, directly cutting recurring expenses with minimal risk.

WHAT TO BUILD: A simple config/auth update plus test script in OpenClaw to route Scout’s requests to `https://api.z.ai/api/paas/v4/` using a new `zai:manual` auth profile, and a lightweight comparison script that logs response quality and cost metrics vs current Gemini Flash.

STACK: node (OpenClaw config + test script)

ESTIMATED TIME: 1hr  
---
