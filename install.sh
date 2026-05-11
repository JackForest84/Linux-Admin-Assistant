#!/bin/bash
set -e

REPO="https://github.com/JackForest84/Linux-Admin-Assistant.git"
INSTALL_DIR="/opt/linuxcmd"
SERVICE="linuxcmd"
PORT=80

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; exit 1; }

echo ""
echo "  linuxcmd installer"
echo "  =================="
echo ""

# Root check
[ "$EUID" -ne 0 ] && err "Spusť jako root: sudo bash install.sh"

# Závislosti
echo "→ Instaluji závislosti..."
apt-get update -qq
apt-get install -y -qq git python3-venv nginx curl 2>/dev/null
ok "Závislosti OK"

# Klon nebo update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "→ Aktualizuji existující instalaci..."
    git -C "$INSTALL_DIR" pull --quiet
    ok "Aktualizováno"
else
    echo "→ Stahuji projekt..."
    git clone --quiet "$REPO" "$INSTALL_DIR"
    ok "Staženo do $INSTALL_DIR"
fi

# Venv + závislosti
echo "→ Instaluji Python závislosti..."
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/app/requirements.txt"
ok "Python prostředí OK"

# Systemd service
echo "→ Nastavuji systemd službu..."
cp "$INSTALL_DIR/deploy/linuxcmd.service" /etc/systemd/system/linuxcmd.service
systemctl daemon-reload
systemctl enable --now linuxcmd
sleep 2
systemctl is-active --quiet linuxcmd && ok "Služba běží" || err "Služba nastartovala chybou — zkontroluj: journalctl -u linuxcmd -n 20"

# Nginx
echo "→ Nastavuji nginx..."
cp "$INSTALL_DIR/deploy/nginx.conf" /etc/nginx/sites-available/linuxcmd
ln -sf /etc/nginx/sites-available/linuxcmd /etc/nginx/sites-enabled/linuxcmd
rm -f /etc/nginx/sites-enabled/default
nginx -t -q 2>/dev/null && ok "Nginx konfigurace OK" || err "Chyba v nginx konfiguraci"
systemctl reload nginx

# Firewall (UFW pokud je k dispozici)
if command -v ufw &>/dev/null; then
    ufw allow 80/tcp &>/dev/null || true
    ok "UFW: port 80 povolen"
fi

# Hotovo
IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "  ${GREEN}Instalace dokončena!${NC}"
echo ""
echo "  Otevři v prohlížeči: http://$IP"
echo ""
