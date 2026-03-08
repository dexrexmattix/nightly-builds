This script installs and starts the Tailscale add-on on your Home Assistant instance running at 192.168.7.4:8123. It uses the Home Assistant REST API to automate the add-on installation and startup, enabling smart home syncing through Tailscale.

To use this script:
1. Create a long-lived access token in your Home Assistant user profile.
2. Save the token as plain text in a file named `ha_long_lived_token.txt` in the same directory as the script.
3. Run the script from a terminal with `./install_tailscale_addon.sh`.

Make sure you have `curl` and `jq` installed on your system. The script will check connectivity, install the Tailscale add-on if not present, and start it automatically.

This removes blockers preventing smart device integration in Home Assistant, enabling smoother home automation setup.