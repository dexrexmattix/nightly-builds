#!/bin/bash
# scout.sh — Reads Codi's workspace context, picks tonight's build target
# Runs on local Ollama (free). Output: a build brief saved to /tmp/nightly-brief.md

WORKSPACE="/Users/codimattix/.openclaw/workspace"
OLLAMA_URL="http://192.168.1.79:11434"
MODEL="qwen2.5:7b"

# Gather context — SECURITY: extract themes only, never send raw personal/work content externally
SPARK=$(cat "$WORKSPACE/SPARK.md" 2>/dev/null)

# Safe summary: extract section headers and bullet topics only (no sensitive details)
WORKSTATE_THEMES=$(cat "$WORKSPACE/WORKSTATE.md" 2>/dev/null | grep -E "^#|^- \*\*|^\*\*" | head -20)
PERSONAL_THEMES=$(cat "$WORKSPACE/PERSONALSTATE.md" 2>/dev/null | grep -E "^#|^- \*\*|^\*\*" | head -15)
MEMORY_THEMES=$(cat "$WORKSPACE/MEMORY.md" 2>/dev/null | grep -E "^#|^##|^- \*\*" | head -20)

PROMPT="You are a scout agent for Dex, an AI assistant helping Codi Mattix.
Your job: pick ONE concrete thing to build tonight that would make his life meaningfully easier through tech or automation.

CONTEXT THEMES (sanitized — no personal details):
## Work Focus Areas
$WORKSTATE_THEMES

## Personal Focus Areas
$PERSONAL_THEMES

## Spark Ideas (verbatim — user-generated)
$SPARK

## Infrastructure/Capabilities
$MEMORY_THEMES

OUTPUT FORMAT (strict):
---
BUILD TARGET: [one sentence description]
WHY: [one sentence — what problem does this solve for Codi?]
WHAT TO BUILD: [specific deliverable — script, doc, automation, tool]
STACK: [what tech/tools to use — bash, python, API, etc.]
---

Pick something buildable in one session. Prioritize high-impact, low-complexity. Be specific."

# Call local Ollama
RESPONSE=$(curl -s -X POST "$OLLAMA_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"$MODEL\", \"prompt\": $(echo "$PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"stream\": false}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])")

echo "$RESPONSE" > /tmp/nightly-brief.md
echo "Scout complete. Brief saved to /tmp/nightly-brief.md"
cat /tmp/nightly-brief.md
