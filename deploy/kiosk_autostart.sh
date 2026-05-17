#!/usr/bin/env bash
set -euo pipefail

export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Disable screen blanking / power save for kiosk reliability.
xset s off || true
xset -dpms || true
xset s noblank || true

# Optional cursor hide support if unclutter is installed.
if command -v unclutter >/dev/null 2>&1; then
  unclutter -idle 0.1 -root &
fi
