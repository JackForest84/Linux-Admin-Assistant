#!/bin/bash
set -euo pipefail

# linuxcmd installer.
#
# This script installs system packages, clones the repo into /opt/linuxcmd,
# creates a dedicated unprivileged service account, and sets up systemd + nginx.
# It will DISABLE the default nginx site (moved to default.disabled, not deleted).
#
# Running it via `curl ... | sudo bash` means executing remote code as root.
# Prefer downloading and reading it first:
#   curl -fsSLO https://raw.githubusercontent.com/JackForest84/Linux-Admin-Assistant/main/install.sh
#   less install.sh && sudo bash install.sh

REPO="https://github.com/JackForest84/Linux-Admin-Assistant.git"
INSTALL_DIR="/opt/linuxcmd"
SERVICE="linuxcmd"
SVC_USER="linuxcmd"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; exit 1; }

echo ""
echo "  linuxcmd installer"
echo "  =================="
echo ""

# Root check
[ "${EUID:-$(id -u)}" -ne 0 ] && err "Run as root: sudo bash install.sh"

# Dependencies
echo "→ Installing dependencies..."
apt-get update -qq
apt-get install -y -qq git python3-venv nginx curl
ok "Dependencies OK"

# Dedicated service account (no home, no shell)
if ! id "$SVC_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SVC_USER"
    ok "Created system user '$SVC_USER'"
else
    ok "System user '$SVC_USER' already exists"
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "→ Updating existing installation..."
    git -C "$INSTALL_DIR" pull --quiet
    ok "Updated"
else
    echo "→ Downloading project..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
    ok "Cloned into $INSTALL_DIR"
fi

# Code stays owned by root and world-readable: the service user can read and
# execute it but cannot modify its own code (pairs with ProtectSystem=strict).
chmod -R a+rX "$INSTALL_DIR"

# Venv + dependencies
echo "→ Installing Python dependencies..."
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/app/requirements.txt"
chmod -R a+rX "$INSTALL_DIR/.venv"
ok "Python environment OK"

# Systemd service
echo "→ Configuring systemd service..."
cp "$INSTALL_DIR/deploy/linuxcmd.service" /etc/systemd/system/linuxcmd.service
systemctl daemon-reload
systemctl enable --now "$SERVICE"
sleep 2
if systemctl is-active --quiet "$SERVICE"; then
    ok "Service running"
else
    err "Service failed to start — check: journalctl -u $SERVICE -n 20"
fi

# Nginx
echo "→ Configuring nginx..."
cp "$INSTALL_DIR/deploy/nginx.conf" /etc/nginx/sites-available/linuxcmd
ln -sf /etc/nginx/sites-available/linuxcmd /etc/nginx/sites-enabled/linuxcmd
# Disable (don't delete) the default site so it can be restored later.
if [ -e /etc/nginx/sites-enabled/default ]; then
    mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.disabled
    warn "Disabled default nginx site (kept as default.disabled)"
fi
if nginx -t -q; then
    ok "Nginx configuration OK"
else
    err "Nginx configuration error"
fi
systemctl reload nginx

# Firewall (UFW if present)
if command -v ufw &>/dev/null; then
    ufw allow 80/tcp &>/dev/null || true
    ok "UFW: port 80 allowed"
fi

# Done
IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "  ${GREEN}Installation complete!${NC}"
echo ""
echo "  Open in your browser: http://$IP"
echo "  For public use, put it behind TLS (see deploy/nginx.conf)."
echo ""
