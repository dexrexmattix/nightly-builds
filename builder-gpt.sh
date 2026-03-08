#!/bin/bash
# builder-gpt.sh — Builds using GPT-4.1-mini
# Input: /tmp/nightly-brief.md
# Output: /tmp/nightly-output-gpt/

OPENAI_KEY="${OPENAI_API_KEY}"
BRIEF_FILE="/tmp/nightly-brief.md"
OUTPUT_DIR="/tmp/nightly-output-gpt"
RAW_FILE="/tmp/nightly-raw-gpt.txt"

if [ ! -f "$BRIEF_FILE" ] || [ ! -s "$BRIEF_FILE" ]; then
  echo "[GPT] No brief found. Run scout.sh first."
  exit 1
fi

rm -rf "$OUTPUT_DIR" && mkdir -p "$OUTPUT_DIR"
echo "[GPT] Building with gpt-4.1-mini..."

python3 << PYEOF
import urllib.request, json, sys

key = "$OPENAI_KEY"
brief = open("$BRIEF_FILE").read()

system = """You are a builder agent. Write clean, complete, working code.

Rules:
- Output ONLY the deliverable files. No explanations before or after.
- For each file use this EXACT format:
=== FILENAME: filename.ext ===
[complete file contents]
=== END ===
- Always include a README.md (one paragraph: what it does and how to run it).
- Write complete runnable code. No placeholders. No TODOs.
- Keep it simple — one or two files max.
- Target: a non-coder who runs things via terminal or browser."""

data = json.dumps({
    "model": "gpt-4.1-mini",
    "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Build exactly what this brief describes:\n\n{brief}\n\nOutput the files now."}
    ],
    "max_tokens": 3000,
    "temperature": 0.3
}).encode()

req = urllib.request.Request(
    "https://api.openai.com/v1/chat/completions",
    data=data,
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
)
try:
    res = urllib.request.urlopen(req, timeout=60)
    body = json.loads(res.read())
    content = body["choices"][0]["message"]["content"]
    with open("$RAW_FILE", "w") as f:
        f.write(content)
    print(f"[GPT] Got {len(content)} chars")
except Exception as e:
    print(f"[GPT] API error: {e}")
    sys.exit(1)
PYEOF

# Parse files
python3 << PYEOF2
import re, os

with open("$RAW_FILE") as f:
    content = f.read()

os.makedirs("$OUTPUT_DIR", exist_ok=True)

# Save raw
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
    print(f"[GPT] Created: {filename} ({len(file_content)} chars)")
PYEOF2

echo "[GPT] Build complete."
ls "$OUTPUT_DIR"
