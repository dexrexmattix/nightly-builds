#!/bin/bash
# distill.sh — Weekly memory distillation pass
# Reads last 7 days of daily notes, extracts only high-signal insights,
# appends compressed learnings to MEMORY.md
# Runs Sunday nights via cron, after the nightly build

set -e

ENV_FILE="$(dirname "$0")/.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

WORKSPACE="$HOME/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
TODAY=$(date +%Y-%m-%d)
LOGFILE="/tmp/distill-$TODAY.log"

echo "=== Memory Distillation — $TODAY ===" | tee -a "$LOGFILE"

# Gather last 7 days of daily notes
NOTES=""
for i in {0..6}; do
  DAY=$(date -v-${i}d +%Y-%m-%d 2>/dev/null || date -d "$i days ago" +%Y-%m-%d 2>/dev/null)
  NOTE_FILE="$WORKSPACE/memory/$DAY.md"
  if [ -f "$NOTE_FILE" ]; then
    NOTES="$NOTES\n\n--- $DAY ---\n$(cat "$NOTE_FILE")"
  fi
done

if [ -z "$NOTES" ]; then
  echo "No daily notes found for the last 7 days. Skipping." | tee -a "$LOGFILE"
  exit 0
fi

# Current MEMORY.md tail (last 100 lines) to avoid duplicates
MEMORY_TAIL=$(tail -100 "$MEMORY_FILE" 2>/dev/null || echo "")

PROMPT="You are a memory distillation assistant for an AI agent named Dex.

Your job: read the last 7 days of Dex's daily notes and extract ONLY what is worth keeping in long-term memory.

**Rules — only include something if it is:**
- A decision that was made (tech, personal, process, config)
- A new durable fact (new tool live, new person added, preference confirmed, config changed)
- A lesson learned or mistake to avoid repeating
- A meaningful shift in direction or priority
- Something explicitly flagged as important

**Do NOT include:**
- Routine heartbeat logs
- Things already in MEMORY.md (check the tail provided)
- Transient status updates
- Anything that will be stale/irrelevant in 30 days

**Output format:**
If there are insights worth keeping, output them as a short markdown block starting with:
## Distilled — $TODAY
Then bullet points, each max 2 sentences. Aim for 3-8 bullets. Quality > quantity.

If nothing passes the bar, output exactly: NOTHING_NEW

--- CURRENT MEMORY.MD TAIL (last 100 lines) ---
$MEMORY_TAIL

--- DAILY NOTES (last 7 days) ---
$NOTES"

echo "Running distillation via GPT-4.1-mini..." | tee -a "$LOGFILE"

RESULT=$(curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json, sys
prompt = sys.stdin.read()
payload = {
  'model': 'gpt-4.1-mini',
  'messages': [{'role': 'user', 'content': prompt}],
  'max_tokens': 600,
  'temperature': 0.3
}
print(json.dumps(payload))
" <<< "$PROMPT")" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])")

echo "Distillation result:" | tee -a "$LOGFILE"
echo "$RESULT" | tee -a "$LOGFILE"

if [ "$RESULT" = "NOTHING_NEW" ]; then
  echo "Nothing new worth keeping. MEMORY.md unchanged." | tee -a "$LOGFILE"
  MSG="🧠 Weekly distillation ran — nothing new worth adding to long-term memory this week."
else
  # Append to MEMORY.md
  echo "" >> "$MEMORY_FILE"
  echo "$RESULT" >> "$MEMORY_FILE"
  echo "Appended to MEMORY.md ✅" | tee -a "$LOGFILE"
  PREVIEW=$(echo "$RESULT" | head -6)
  MSG="🧠 *Weekly Memory Distillation — $TODAY*

Compressed last 7 days → MEMORY.md updated:
\`\`\`
$PREVIEW
\`\`\`"
fi

# Deliver to Slack
openclaw message send --channel slack --to cwmattix --message "$MSG" 2>/dev/null || \
  echo "Slack delivery: $MSG"

echo "=== Distillation Complete ===" | tee -a "$LOGFILE"
