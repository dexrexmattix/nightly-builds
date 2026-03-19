---
BUILD TARGET: Integrate z.ai GLM-4.7-Flash model as a drop-in cheaper alternative in Scout agent and benchmark cost and quality against current Gemini Flash.

WHY: This reduces token costs on high-volume agents without risking quality loss, directly cutting operational expenses.

WHAT TO BUILD: A test script or config patch to add `zai:manual` auth profile, redirect Scout’s API base URL to `https://api.z.ai/api/paas/v4/` with GLM-4.7-Flash model, then run side-by-side prompt quality and cost comparison with current Gemini Flash setup.

STACK: bash + simple Node.js or Python test script for API calls

ESTIMATED TIME: 1hr  
---
