#!/bin/bash
# Starts a minimal X session with only the HydroHalo app — no desktop

# Disable screen blanking
xset s off
xset -dpms  
xset s noblank

# Hide cursor after 0.1s idle
unclutter -idle 0.1 -root &

# Launch the app — if it crashes, X exits and systemd restarts everything
cd /home/lunic21/hydrohalo
python3 -m app.main