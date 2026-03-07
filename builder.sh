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

# Always save raw response first — no matter what
with open(f"{output_dir}/raw_response.md", "w") as f:
    f.write(content)

if not content.strip():
    print("ERROR: Builder got an empty response from Ollama. Check if Ollama is reachable and the model is loaded.")
    sys.exit(1)

print(f"Raw response saved ({len(content)} chars)")

# Try strict format first: === FILENAME: ... === END ===
pattern = r'=== FILENAME: (.+?) ===\n(.*?)=== END ==='
matches = re.findall(pattern, content, re.DOTALL)

# Fallback: try markdown code blocks with filenames (```filename\n...\n```)
if not matches:
    pattern_md = r'```(?:\w+)?\s*\n#\s*(\S+)\n(.*?)```'
    matches_md = re.findall(pattern_md, content, re.DOTALL)
    if matches_md:
        matches = matches_md
        print("Used fallback markdown code block parser")

if matches:
    for filename, file_content in matches:
        filename = filename.strip()
        # Skip obviously bad filenames
        if len(filename) > 200 or '\n' in filename:
            continue
        filepath = os.path.join(output_dir, filename)
        if '/' in filename:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(file_content.strip())
        print(f"Created: {filepath}")
else:
    # No structured files — save raw as the build artifact so it's not lost
    print("No structured files parsed — raw_response.md IS the build artifact")
PYEOF

echo "Builder complete. Output in $OUTPUT_DIR"
ls -la "$OUTPUT_DIR"
