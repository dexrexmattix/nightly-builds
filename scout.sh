#!/bin/bash
# scout.sh — Reads Codi's workspace context, picks tonight's build target
# Uses GPT-4.1-mini (resilient — no Ollama dependency)

WORKSPACE="/Users/codimattix/.openclaw/workspace"
OPENAI_KEY="${OPENAI_API_KEY}"

# Gather context — themes only, no raw personal/work content
SPARK=$(cat "$WORKSPACE/SPARK.md" 2>/dev/null | grep -E "^\*\*|^-" | head -20)
FLOAT=$(cat "$WORKSPACE/FLOAT.md" 2>/dev/null | grep -E "^###|^-" | head -20)
COMMIT=$(cat "$WORKSPACE/COMMIT.md" 2>/dev/null | grep -E "^##|^-" | head -20)
MEMORY=$(cat "$WORKSPACE/MEMORY.md" 2>/dev/null | grep -E "^##|^- \[" | head -20)

PROMPT="You are a scout agent for Dex, an AI assistant helping Codi Mattix — a non-coder who uses AI to build tools for his life.

Your job: pick ONE concrete thing to build tonight that would make his life meaningfully easier.

CODI'S IDEAS (SPARK.md):
$SPARK

DEX'S FLOAT IDEAS (FLOAT.md):
$FLOAT

OPEN COMMITMENTS (COMMIT.md):
$COMMIT

RECENT MEMORY / CAPABILITIES:
$MEMORY

OUTPUT FORMAT (strict, nothing else):
---
BUILD TARGET: [one sentence]
WHY: [one sentence — what problem does this solve?]
WHAT TO BUILD: [specific deliverable — script, web tool, automation]
STACK: [bash / python / node / html — keep it simple]
ESTIMATED TIME: [15min / 30min / 1hr]
---

Rules: pick something buildable in one session, high-impact, low-complexity. Be specific. Prefer tools Codi can actually use tomorrow morning."

RESPONSE=$(python3 -c "
import urllib.request, json, os, sys

key = '$OPENAI_KEY'
prompt = '''$PROMPT'''

data = json.dumps({
  'model': 'gpt-4.1-mini',
  'messages': [{'role': 'user', 'content': prompt}],
  'max_tokens': 400,
  'temperature': 0.7
}).encode()

req = urllib.request.Request(
  'https://api.openai.com/v1/chat/completions',
  data=data,
  headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req, timeout=30)
body = json.loads(res.read())
print(body['choices'][0]['message']['content'])
" 2>&1)

echo "$RESPONSE" > /tmp/nightly-brief.md
echo "Scout complete. Brief saved to /tmp/nightly-brief.md"
echo "---"
cat /tmp/nightly-brief.md
