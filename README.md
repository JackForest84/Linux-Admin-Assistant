# linuxcmd

**Česko-anglický cheatsheet linuxových příkazů** — zadáš co hledáš, dostaneš příkazy, jedním klikem zkopíruješ.

🌐 **[jakub.forejt.it](https://jakub.forejt.it)**

---

## Co to dělá

- Hledáš česky nebo anglicky — najde příkazy
- Funguje bez internetu (vše lokálně, SQLite FTS5)
- Přepínač CS / EN
- Klik na ikonku = příkaz ve schránce
- **778 příkazů ve 36 kategoriích**

## Kategorie

| Kategorie | Příklady |
|---|---|
| Disk | df, du, lsblk, mount, LVM, swap |
| Procesy | ps, top, kill, htop |
| Síť | ip, ss, ufw, iptables, nmap, curl |
| Systemd | start/stop/restart, journalctl, timery |
| Balíčky | apt, dpkg |
| Soubory | find, grep, chmod, rsync, tar, zip |
| SSH | connect, klíče, tunel, scp |
| Git | commit, branch, remote, log, stash |
| Docker | ps, run, logs, compose, cleanup |
| Kubernetes | pods, deployments, context |
| Text | sed, awk, sort, cut, diff, wc |
| Bash | history, pipes, aliasy, smyčky |
| Vim / Nano | základy, navigace, úpravy |
| Tmux | sessions, zkratky, screen |
| Databáze | postgres, mysql, redis, sqlite |
| Zálohy | rsync, tar, restic, dd |
| Bezpečnost | fail2ban, openssl, certbot, gpg |
| Monitoring | iotop, iftop, tcpdump, benchmark |
| Proxmox | pct, qm, cluster, vzdump |
| Hardware | lshw, SMART, teploty |
| + 16 dalších | ... |

## Stack

- **Backend**: FastAPI + SQLite FTS5 (fulltext se diakritikou)
- **Frontend**: Vanilla JS, bez frameworků
- **Deploy**: systemd + nginx
- **Data**: YAML soubory → snadno rozšiřitelné

## Vlastní deploy (Debian / Ubuntu)

Jeden příkaz — nainstaluje vše automaticky (git clone, Python venv, systemd, nginx):

```bash
curl -fsSL https://raw.githubusercontent.com/JackForest84/Linux-Admin-Assistant/main/install.sh | sudo bash
```

Po dokončení otevři `http://<IP-serveru>` v prohlížeči.

### Ruční instalace

```bash
# Závislosti
sudo apt install git python3-venv nginx

# Projekt
git clone https://github.com/JackForest84/Linux-Admin-Assistant.git /opt/linuxcmd
cd /opt/linuxcmd
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt

# Systemd service
sudo cp deploy/linuxcmd.service /etc/systemd/system/
sudo systemctl enable --now linuxcmd

# Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/linuxcmd
sudo ln -s /etc/nginx/sites-available/linuxcmd /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Přidat příkazy

Uprav nebo přidej YAML soubor v `data/`:

```yaml
- id: muj-prikaz
  title_cs: "Název česky"
  title_en: "Title in English"
  tags_cs: [tag1, tag2]
  tags_en: [tag1, tag2]
  commands:
    - cmd: "prikaz --flag"
      desc_cs: "Popis česky"
      desc_en: "Description in English"
```

Restart:
```bash
sudo systemctl restart linuxcmd
```

---

Made by [Jakub Forejt](https://jakub.forejt.it)
