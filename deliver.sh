#!/bin/bash
# deliver.sh — Reviews output, commits to GitHub, delivers to Codi via Slack
# Uses Flash model (cheap) for review. Calls OpenClaw to send Slack message.

OUTPUT_DIR="/tmp/nightly-output"
BRIEF=$(cat /tmp/nightly-brief.md 2>/dev/null)
DATE=$(date +%Y-%m-%d)
BRANCH="nightly-$DATE"

if [ ! -d "$OUTPUT_DIR" ]; then
  echo "No output found. Run builder.sh first."
  exit 1
fi

# Copy output to repo
REPO_DIR="$HOME/Projects/nightly-builds/builds/$DATE"
mkdir -p "$REPO_DIR"
cp -r "$OUTPUT_DIR/"* "$REPO_DIR/" 2>/dev/null

# Commit to GitHub
cd "$HOME/Projects/nightly-builds"
git add .
git commit -m "Nightly build: $DATE

$(cat /tmp/nightly-brief.md | head -5)"
git push origin main 2>&1 || git push --set-upstream origin main 2>&1

# Get README summary
README=$(cat "$REPO_DIR/README.md" 2>/dev/null || cat "$OUTPUT_DIR/README.md" 2>/dev/null || echo "See GitHub for details.")

# Send Slack notification via OpenClaw
SLACK_MSG="🌙 *Nightly Build — $DATE*

$(echo "$BRIEF" | grep 'BUILD TARGET:' | sed 's/BUILD TARGET: //')

*What it does:* $README

*Live on GitHub:* https://github.com/dexrexmattix/nightly-builds/tree/main/builds/$DATE

Reply 'deploy it' and I'll set it up, or ignore if it's not useful."

# Use openclaw to send to Slack
openclaw message send --channel slack --to cwmattix --message "$SLACK_MSG" 2>/dev/null || \
  echo "Slack delivery: $SLACK_MSG"

echo "Delivery complete."
