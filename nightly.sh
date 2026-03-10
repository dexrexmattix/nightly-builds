#!/bin/bash
# nightly.sh — Master orchestrator. GPT-only build pipeline.
# Called by cron at 11PM nightly.

set -e
LOGFILE="/tmp/nightly-build-$(date +%Y-%m-%d).log"

# Load API keys from local env file (not committed to git)
ENV_FILE="$(dirname "$0")/.env"
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

echo "=== Nightly Build Starting $(date) ===" | tee -a "$LOGFILE"

# Step 1: Scout — picks tonight's build target
echo "--- Step 1: Scout ---" | tee -a "$LOGFILE"
bash "$(dirname "$0")/scout.sh" 2>&1 | tee -a "$LOGFILE"

# Step 2: Build with GPT-4.1-mini
echo "--- Step 2: Builder (GPT-4.1-mini) ---" | tee -a "$LOGFILE"
bash "$(dirname "$0")/builder-gpt.sh" 2>&1 | tee -a "$LOGFILE"

# Step 3: Deliver — commit + send to Slack
echo "--- Step 3: Deliver ---" | tee -a "$LOGFILE"
bash "$(dirname "$0")/deliver.sh" 2>&1 | tee -a "$LOGFILE"

echo "=== Nightly Build Complete $(date) ===" | tee -a "$LOGFILE"
