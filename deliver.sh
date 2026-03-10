#!/bin/bash
# deliver.sh — Commits GPT build output, delivers to Codi via Slack

DATE=$(date +%Y-%m-%d)
BRIEF=$(cat /tmp/nightly-brief.md 2>/dev/null)
BUILD_TARGET=$(echo "$BRIEF" | grep 'BUILD TARGET:' | sed 's/BUILD TARGET: //' | head -1)

GPT_DIR="/tmp/nightly-output-gpt"
REPO_DIR="$HOME/Projects/nightly-builds/builds/$DATE"

if [ ! -d "$GPT_DIR" ]; then
  echo "No build output found."
  exit 1
fi

# Copy output to repo
mkdir -p "$REPO_DIR/gpt"
cp -r "$GPT_DIR/"* "$REPO_DIR/gpt/" 2>/dev/null

# Save brief too
cp /tmp/nightly-brief.md "$REPO_DIR/brief.md" 2>/dev/null

# Commit to GitHub
cd "$HOME/Projects/nightly-builds"
git add .
git commit -m "Nightly build: $DATE — $BUILD_TARGET"
git push origin main 2>&1 || echo "Push failed — continuing"

# Build Slack message
GPT_README=$(cat "$REPO_DIR/gpt/README.md" 2>/dev/null | head -4 || echo "(no README)")
GPT_FILES=$(ls "$REPO_DIR/gpt/" 2>/dev/null | grep -v raw_response | grep -v README | tr '\n' ', ' | sed 's/,$//')

SLACK_MSG="🌙 *Nightly Build — $DATE*
*Tonight's target:* $BUILD_TARGET

$GPT_README
Files: $GPT_FILES

GitHub: https://github.com/dexrexmattix/nightly-builds/tree/main/builds/$DATE/gpt

Reply 'deploy it' and I'll set it up."

openclaw message send --channel slack --to cwmattix --message "$SLACK_MSG" 2>/dev/null || \
  echo "Slack: $SLACK_MSG"

echo "Delivery complete."
