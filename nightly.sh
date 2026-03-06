#!/bin/bash
# nightly.sh — Master orchestrator. Runs the full pipeline.
# Called by cron at 11PM nightly.

set -e
LOGFILE="/tmp/nightly-build-$(date +%Y-%m-%d).log"

echo "=== Nightly Build Starting $(date) ===" | tee -a "$LOGFILE"

# Step 1: Scout (local Ollama — free)
echo "Running scout..." | tee -a "$LOGFILE"
bash "$(dirname "$0")/scout.sh" 2>&1 | tee -a "$LOGFILE"

# Step 2: Build (local Ollama coder — free)
echo "Running builder..." | tee -a "$LOGFILE"
bash "$(dirname "$0")/builder.sh" 2>&1 | tee -a "$LOGFILE"

# Step 3: Deliver (commit + Slack)
echo "Delivering..." | tee -a "$LOGFILE"
bash "$(dirname "$0")/deliver.sh" 2>&1 | tee -a "$LOGFILE"

echo "=== Nightly Build Complete $(date) ===" | tee -a "$LOGFILE"
