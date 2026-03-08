#!/bin/bash
# builder-phi.sh — Builds using Phi-4 on Mac mini (localhost:11434)
# Input: /tmp/nightly-brief.md
# Output: /tmp/nightly-output-phi/

OLLAMA_URL="http://localhost:11434"
BRIEF_FILE="/tmp/nightly-brief.md"
OUTPUT_DIR="/tmp/nightly-output-phi"
RAW_FILE="/tmp/nightly-raw-phi.txt"

if [ ! -f "$BRIEF_FILE" ] || [ ! -s "$BRIEF_FILE" ]; then
  echo "[Phi-4] No brief found. Run scout.sh first."
  exit 1
fi

# Check Phi-4 is available
if ! curl -s --max-time 5 "$OLLAMA_URL/api/tags" | grep -q "phi4"; then
  echo "[Phi-4] phi4 model not available at $OLLAMA_URL — skipping"
  exit 0
fi

rm -rf "$OUTPUT_DIR" && mkdir -p "$OUTPUT_DIR"
echo "[Phi-4] Building with phi4 (this takes ~5-8 min)..."

python3 << PYEOF
import urllib.request, json, sys

brief = open("$BRIEF_FILE").read()

prompt = f"""You are a builder agent. Write clean, complete, working code.

Rules:
- Output ONLY the deliverable files. No explanations before or after.
- For each file use this EXACT format:
=== FILENAME: filename.ext ===
[complete file contents]
=== END ===
- Always include a README.md (one paragraph: what it does and how to run it).
- Write complete runnable code. No placeholders. No TODOs.
- Keep it simple — one or two files max.
- Target: a non-coder who runs things via terminal or browser.

Build exactly what this brief describes:

{brief}

Output the files now."""

data = json.dumps({
    "model": "phi4",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": 3000,
        "temperature": 0.3,
        "num_ctx": 8192
    }
}).encode()

req = urllib.request.Request(
    "$OLLAMA_URL/api/generate",
    data=data,
    headers={"Content-Type": "application/json"}
)
try:
    res = urllib.request.urlopen(req, timeout=600)
    body = json.loads(res.read())
    content = body.get("response", "")
    speed = body.get("eval_count", 0) / max(body.get("eval_duration", 1) / 1e9, 1)
    with open("$RAW_FILE", "w") as f:
        f.write(content)
    print(f"[Phi-4] Got {len(content)} chars at {speed:.1f} tok/s")
except Exception as e:
    print(f"[Phi-4] Error: {e}")
    sys.exit(1)
PYEOF

# Parse files (same logic as GPT builder)
python3 << PYEOF2
import re, os

with open("$RAW_FILE") as f:
    content = f.read()

os.makedirs("$OUTPUT_DIR", exist_ok=True)

with open("$OUTPUT_DIR/raw_response.md", "w") as f:
    f.write(content)

pattern = r'=== FILENAME: (.+?) ===\n(.*?)=== END ==='
matches = re.findall(pattern, content, re.DOTALL)

if not matches:
    blocks = re.findall(r'` ` `(?:\w+)?\n(.*?)` ` `'.replace(' ', ''), content, re.DOTALL)
    if blocks:
        matches = [(f"output_{i}.sh" if i == 0 else f"file_{i}.txt", b) for i, b in enumerate(blocks)]

for filename, file_content in matches:
    filename = filename.strip()
    if not filename or len(filename) > 200 or '\n' in filename:
        continue
    filepath = os.path.join("$OUTPUT_DIR", filename)
    if '/' in filename:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(file_content.strip())
    print(f"[Phi-4] Created: {filename} ({len(file_content)} chars)")
PYEOF2

echo "[Phi-4] Build complete."
ls "$OUTPUT_DIR"
