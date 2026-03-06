#!/bin/bash
# builder.sh — Takes the brief from scout, builds the actual thing
# Runs on local Ollama coder model (free). Output: files in /tmp/nightly-output/

OLLAMA_URL="http://192.168.1.79:11434"
MODEL="qwen2.5-coder:7b"
BRIEF=$(cat /tmp/nightly-brief.md 2>/dev/null)
OUTPUT_DIR="/tmp/nightly-output"

if [ -z "$BRIEF" ]; then
  echo "No brief found. Run scout.sh first."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

PROMPT="You are a builder agent. You write clean, working code and scripts.

Here is your build brief:
$BRIEF

Your job: build exactly what's described. Output ONLY the deliverable files.

For each file, use this format:
=== FILENAME: path/filename.ext ===
[file contents]
=== END ===

Rules:
- Write complete, runnable code. No placeholders.
- Include a README.md explaining what it does and how to use it (one paragraph, plain English, no jargon).
- If it's a script, make it executable (add shebang).
- Keep it simple. One file if possible.
- Test cases or example usage if relevant."

RESPONSE=$(curl -s --max-time 120 -X POST "$OLLAMA_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\": \"$MODEL\", \"prompt\": $(echo "$PROMPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))'), \"stream\": false}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['response'])")

# Parse and save files
echo "$RESPONSE" | python3 - <<'PYEOF'
import sys, os, re

content = sys.stdin.read()
output_dir = "/tmp/nightly-output"
os.makedirs(output_dir, exist_ok=True)

# Save raw response
with open(f"{output_dir}/raw_response.md", "w") as f:
    f.write(content)

# Parse file blocks
pattern = r'=== FILENAME: (.+?) ===\n(.*?)=== END ==='
matches = re.findall(pattern, content, re.DOTALL)

if matches:
    for filename, file_content in matches:
        filepath = os.path.join(output_dir, filename.strip())
        os.makedirs(os.path.dirname(filepath), exist_ok=True) if '/' in filename else None
        with open(filepath, 'w') as f:
            f.write(file_content.strip())
        print(f"Created: {filepath}")
else:
    print("No structured files found — raw response saved")
PYEOF

echo "Builder complete. Output in $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
