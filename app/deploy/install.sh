#!/bin/bash
set -e

echo "=== HydroHalo One-Time Pi Setup ==="

# System deps
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-tk git

# Clone repo if not already there
if [ ! -d "/home/pi/hydrohalo" ]; then
  git clone https://github.com/Lunic25/hydrohalo.git /home/pi/hydrohalo
fi

# Python deps
cd /home/pi/hydrohalo
pip3 install -r requirements.txt --break-system-packages

# Allow systemctl without password (for the Actions runner)
echo "pi ALL=(ALL) NOPASSWD: /bin/systemctl restart hydrohalo" | sudo tee /etc/sudoers.d/hydrohalo

# Install & enable systemd service
sudo cp deploy/hydrohalo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hydrohalo
sudo systemctl start hydrohalo

# Install GitHub Actions self-hosted runner
# (follow GitHub's runner setup here — repo Settings → Actions → Runners → New)
echo ""
echo "=== Done. Now add this Pi as a GitHub Actions self-hosted runner. ==="
echo "Go to: https://github.com/Lunic25/hydrohalo/settings/actions/runners"
