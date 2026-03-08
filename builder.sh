#!/bin/bash
# builder.sh — Takes the brief from scout, builds the actual thing
# Uses GPT-4.1-mini (resilient — no Ollama dependency)

OPENAI_KEY="${OPENAI_API_KEY}"
BRIEF_FILE="/tmp/nightly-brief.md"
OUTPUT_DIR="/tmp/nightly-output"
RAW_FILE="/tmp/nightly-raw-response.txt"

if [ ! -f "$BRIEF_FILE" ] || [ ! -s "$BRIEF_FILE" ]; then
  echo "No brief found. Run scout.sh first."
  exit 1
fi

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "Calling GPT-4.1-mini to build..."

python3 << PYEOF
import urllib.request, json, sys

key = "$OPENAI_KEY"
brief = open("$BRIEF_FILE").read()

system = """You are a builder agent. Write clean, complete, working code.

Rules:
- Output ONLY the deliverable files. No explanations before or after.
- For each file use this EXACT format (no variations):
=== FILENAME: filename.ext ===
[complete file contents]
=== END ===
- Always include a README.md (one paragraph, plain English, what it does and how to run it).
- Write complete runnable code. No placeholders. No TODOs.
- Keep it simple — one or two files max.
- Target: a non-coder who runs things via terminal or browser."""

data = json.dumps({
    "model": "gpt-4.1-mini",
    "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Build exactly what this brief describes:\n\n{brief}\n\nOutput the files now using the exact === FILENAME === format."}
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
    print(f"Builder: got {len(content)} chars from API")
except Exception as e:
    print(f"Builder API error: {e}")
    sys.exit(1)
PYEOF

if [ ! -f "$RAW_FILE" ] || [ ! -s "$RAW_FILE" ]; then
  echo "ERROR: No response from builder API."
  exit 1
fi

# Copy raw to output dir
cp "$RAW_FILE" "$OUTPUT_DIR/raw_response.md"

# Parse files from raw response
python3 << PYEOF2
import re, os

with open("$RAW_FILE") as f:
    content = f.read()

output_dir = "$OUTPUT_DIR"

pattern = r'=== FILENAME: (.+?) ===\n(.*?)=== END ==='
matches = re.findall(pattern, content, re.DOTALL)

# Fallback: markdown code blocks
if not matches:
    pattern_md = r'```(?:\w+)?\n(.*?)```'
    blocks = re.findall(pattern_md, content, re.DOTALL)
    if blocks:
        matches = [(f"output_{i}.sh" if i == 0 else f"file_{i}.txt", b) for i, b in enumerate(blocks)]
        print("Used fallback code block parser")

if matches:
    for filename, file_content in matches:
        filename = filename.strip()
        if not filename or len(filename) > 200 or '\n' in filename:
            continue
        filepath = os.path.join(output_dir, filename)
        if '/' in filename:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(file_content.strip())
        print(f"Created: {filename} ({len(file_content)} chars)")
else:
    print("Warning: no structured files found — raw_response.md is the artifact")
PYEOF2

echo "Builder complete."
ls -la "$OUTPUT_DIR"
