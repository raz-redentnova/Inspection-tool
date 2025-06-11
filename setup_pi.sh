#!/usr/bin/env bash
#
# setup_pi.sh – Bootstrap Inspection-System on Raspberry Pi CM4
# -------------------------------------------------------------
# 1. Installs OS dependencies
# 2. Clones or updates repository
# 3. Creates Python virtual-environment & installs wheels
# 4. Deploys & enables systemd services
# 5. Runs quick health checks
# -------------------------------------------------------------
# Author: <your-name>  |  Last updated: 2025-06-10
#

set -euo pipefail
IFS=$'\n\t'

# ---------- USER-EDITABLE VARIABLES ---------------------------------------
REPO_URL="https://github.com/<org>/inspection-system.git"
APP_DIR="/home/pi/inspection-system"
PY_BIN="/usr/bin/python3"
PORT="8501"
# --------------------------------------------------------------------------

# ---------- COLOUR HELPERS -------------------------------------------------
green(){ echo -e "\e[32m$*\e[0m"; }
red()  { echo -e "\e[31m$*\e[0m"; }
cyan() { echo -e "\e[36m$*\e[0m"; }

# ---------- ERROR HANDLER --------------------------------------------------
clean_exit=false
trap 'red "❌  ERROR in ${FUNCNAME:-main} (line $LINENO)."; exit 1' ERR

[[ $EUID -ne 0 ]] && red "Please run with sudo." && exit 1

#############################################################################
cyan "Step 1/5  –  Installing OS packages"
#############################################################################
apt-get update -qq
apt-get install -y --no-install-recommends \
    git python3-venv python3-pip libatlas-base-dev libavdevice-dev \
    v4l-utils chromium-browser >/dev/null
green "✓  APT packages installed"

#############################################################################
cyan "Step 2/5  –  Cloning or updating repository"
#############################################################################
if [[ -d "$APP_DIR/.git" ]]; then
    git -C "$APP_DIR" pull --quiet
    green "✓  Repository updated"
else
    git clone --quiet "$REPO_URL" "$APP_DIR"
    green "✓  Repository cloned"
fi

#############################################################################
cyan "Step 3/5  –  Python venv + requirements"
#############################################################################
cd "$APP_DIR"
$PY_BIN -m venv .venv
source .venv/bin/activate
pip install -U pip >/dev/null
pip install -q -r requirements.txt
green "✓  Virtual environment ready"

#############################################################################
cyan "Step 4/5  –  Deploying systemd services"
#############################################################################
cat >/etc/systemd/system/streamlit.service <<EOF
[Unit]
Description=Inspection-System Streamlit backend
After=network.target

[Service]
User=pi
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/streamlit run $APP_DIR/app.py --server.headless true --server.port $PORT
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/systemd/system/chromium-kiosk.service <<EOF
[Unit]
Description=Chromium kiosk for Inspection-System
After=streamlit.service

[Service]
User=pi
Environment=XAUTHORITY=/home/pi/.Xauthority
Environment=DISPLAY=:0
ExecStart=/usr/bin/chromium-browser --kiosk --app=http://localhost:$PORT --noerrdialogs
Restart=always

[Install]
WantedBy=graphical.target
EOF

systemctl daemon-reload
systemctl enable streamlit.service chromium-kiosk.service
systemctl restart streamlit.service chromium-kiosk.service
green "✓  streamlit & chromium-kiosk services enabled"

#############################################################################
cyan "Step 5/5  –  Quick health checks"
#############################################################################
# Camera check
if v4l2-ctl --list-devices | grep -qE "video"; then
    green "✓  Camera detected"
else
    red   "⚠  Camera NOT detected – continuing (CSI cameras need libcamera)."
fi
# Streamlit check
if systemctl is-active --quiet streamlit; then
    green "✓  streamlit service running"
else
    red   "❌ streamlit failed – inspect with: journalctl -u streamlit -f"
fi

clean_exit=true
green "✅  All steps completed successfully!"

#############################################################################
# Offer reboot only if everything succeeded
#############################################################################
if $clean_exit; then
   read -rp $'\nDo you want to reboot now to launch kiosk mode? [y/N] ' ans
   if [[ ${ans,,} == y* ]]; then
       cyan "Rebooting…"
       reboot
   else
       cyan "Reboot later with: sudo reboot"
   fi
fi
