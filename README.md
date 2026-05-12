# linuxcmd

**Multilingual Linux command cheatsheet** — type what you need, get the commands, click to copy.

🌐 [jakub.forejt.it](https://jakub.forejt.it)

---

## What it does

- Search in plain language, find the right command — across **12 languages**
- Works offline (everything is local, SQLite FTS5)
- One click → command in your clipboard
- 800+ commands across 36 categories
- No AI, no cloud, no telemetry

## Languages

🇬🇧 English · 🇨🇿 Čeština · 🇸🇰 Slovenčina · 🇩🇪 Deutsch · 🇪🇸 Español · 🇫🇷 Français · 🇮🇹 Italiano · 🇵🇱 Polski · 🇹🇷 Türkçe · 🇵🇹 Português · 🇳🇱 Nederlands · 🇭🇺 Magyar

> English and Czech are fully translated. Other languages fall back to English where translations are missing — contributions welcome (see below).

## Categories

| Category | Examples |
|---|---|
| Disk | df, du, lsblk, mount, LVM, swap |
| Processes | ps, top, kill, htop |
| Network | ip, ss, ufw, iptables, nmap, curl |
| Systemd | start/stop/restart, journalctl, timers |
| Packages | apt, dpkg |
| Files | find, grep, chmod, rsync, tar, zip |
| SSH | connect, keys, tunnel, scp |
| Git | commit, branch, remote, log, stash |
| Docker | ps, run, logs, compose, cleanup |
| Kubernetes | pods, deployments, context |
| Text | sed, awk, sort, cut, diff, wc |
| Bash | history, pipes, aliases, loops |
| Vim / Nano | basics, navigation, editing |
| Tmux | sessions, shortcuts, screen |
| Databases | postgres, mysql, redis, sqlite |
| Backup | rsync, tar, restic, dd |
| Security | fail2ban, openssl, certbot, gpg |
| Monitoring | iotop, iftop, tcpdump, benchmark |
| Proxmox | pct, qm, cluster, vzdump |
| Hardware | lshw, SMART, temperatures |
| + 16 more | ... |

## Tech stack

- **Backend**: FastAPI + SQLite FTS5 (full-text search with diacritics handling per language)
- **Frontend**: Vanilla JS, no frameworks
- **Deploy**: systemd + nginx
- **Data**: YAML files → easy to extend, easy to translate

## One-command install (Debian / Ubuntu)

Installs everything automatically (git clone, Python venv, systemd, nginx):

```bash
curl -fsSL https://raw.githubusercontent.com/JackForest84/Linux-Admin-Assistant/main/install.sh | sudo bash
```

Then open `http://<your-server-ip>` in your browser.

### Manual install

```bash
sudo apt install git python3-venv nginx
git clone https://github.com/JackForest84/Linux-Admin-Assistant.git /opt/linuxcmd
cd /opt/linuxcmd
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt
sudo cp deploy/linuxcmd.service /etc/systemd/system/
sudo systemctl enable --now linuxcmd
sudo cp deploy/nginx.conf /etc/nginx/sites-available/linuxcmd
sudo ln -s /etc/nginx/sites-available/linuxcmd /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## Adding commands

Edit or create a YAML file in `data/`:

```yaml
- id: my-command
  title:
    en: "Title in English"
    cs: "Název česky"
    de: "Titel auf Deutsch"
    # ... other languages
  tags:
    en: [tag1, tag2]
    cs: [tag1, tag2]
    # ... other languages
  commands:
    - cmd: "your --command --here"
      desc:
        en: "Description in English"
        cs: "Popis česky"
        # ... other languages
```

Missing translations fall back to English. Restart the service:

```bash
sudo systemctl restart linuxcmd
```

## Contributing translations

Want to help translate to your language? Pick a YAML file in `data/`, add your language to `title`, `tags`, and `desc` fields, and open a pull request. Even a single file or category helps.

Supported language codes: `en`, `cs`, `sk`, `de`, `es`, `fr`, `it`, `pl`, `tr`, `pt`, `nl`, `hu`.

## License

Open source. Use it however you like.

---

Made by [Jakub Forejt](https://jakub.forejt.it)
