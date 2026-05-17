#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash deploy/install.sh"
  exit 1
fi

APP_USER="${SUDO_USER:-pi}"
APP_ROOT="/opt/hydrohalo"
SERVICE_SRC="${APP_ROOT}/deploy/hydrohalo.service"
SERVICE_DST="/etc/systemd/system/hydrohalo.service"
LOG_DIR="/var/log/hydrohalo"

apt-get update
apt-get install -y python3 python3-pip python3-tk xserver-xorg xinit x11-xserver-utils

mkdir -p "${LOG_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${LOG_DIR}"

cd "${APP_ROOT}"
pip3 install -r requirements.txt

cp "${SERVICE_SRC}" "${SERVICE_DST}"
sed -i "s/^User=.*/User=${APP_USER}/" "${SERVICE_DST}"

install -m 755 deploy/kiosk_autostart.sh /usr/local/bin/hydrohalo-kiosk-autostart

# Verify touchscreen env basics.
if [[ ! -e /dev/input/touchscreen && ! -d /dev/input ]]; then
  echo "Warning: touchscreen input device not detected under /dev/input"
fi

systemctl daemon-reload
systemctl enable hydrohalo.service
systemctl restart hydrohalo.service
systemctl status hydrohalo.service --no-pager || true

echo "HydroHalo kiosk install complete"
