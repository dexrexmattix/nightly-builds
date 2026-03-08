#!/bin/bash

# Script to install and start the Tailscale add-on on Home Assistant at 192.168.7.4:8123
# Usage: ./install_tailscale_addon.sh

HA_HOST="192.168.7.4"
HA_PORT="8123"
HA_URL="http://${HA_HOST}:${HA_PORT}"
ADDON_SLUG="core_tailscale"
API_TOKEN_FILE="./ha_long_lived_token.txt"

# Check if token file exists
if [ ! -f "$API_TOKEN_FILE" ]; then
  echo "Error: Long-lived Home Assistant API token file '$API_TOKEN_FILE' not found."
  echo "Please create a long-lived access token in Home Assistant and save it in this file."
  exit 1
fi

API_TOKEN=$(cat "$API_TOKEN_FILE")

# Function to check if Home Assistant is reachable
function check_ha() {
  curl -sf "${HA_URL}/api/" > /dev/null
  return $?
}

echo "Checking Home Assistant availability at ${HA_URL}..."
if ! check_ha; then
  echo "Error: Home Assistant is not reachable at ${HA_URL}."
  exit 1
fi

# Check if the addon is already installed
echo "Checking if Tailscale add-on is already installed..."
ADDON_INSTALLED=$(curl -s -H "Authorization: Bearer ${API_TOKEN}" \
  "${HA_URL}/api/hassio/addons/${ADDON_SLUG}" | jq -r '.slug // empty')

if [ "$ADDON_INSTALLED" == "$ADDON_SLUG" ]; then
  echo "Tailscale add-on is already installed."
else
  echo "Installing Tailscale add-on..."
  INSTALL_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${API_TOKEN}" \
    -H "Content-Type: application/json" \
    "${HA_URL}/api/hassio/addons/${ADDON_SLUG}/install")

  if echo "$INSTALL_RESPONSE" | grep -q '"result":"ok"'; then
    echo "Tailscale add-on installed successfully."
  else
    echo "Failed to install Tailscale add-on:"
    echo "$INSTALL_RESPONSE"
    exit 1
  fi
fi

# Start the addon
echo "Starting Tailscale add-on..."
START_RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${API_TOKEN}" \
  "${HA_URL}/api/hassio/addons/${ADDON_SLUG}/start")

if echo "$START_RESPONSE" | grep -q '"result":"ok"'; then
  echo "Tailscale add-on started successfully."
else
  echo "Failed to start Tailscale add-on:"
  echo "$START_RESPONSE"
  exit 1
fi

echo "Tailscale add-on is installed and running on Home Assistant at ${HA_URL}."