# LinkedIn post — drafty

Tři varianty + tipy na hashtagy a obrázek.

---

## 🇨🇿 VARIANTA A — krátká, sebevědomá (300 znaků)

> Postavil jsem open-source nástroj pro IT/DevOps lidi: **778 linuxových příkazů ve 12 jazycích**, vyhledávání obyčejným jazykem, jedním klikem do schránky. FastAPI + SQLite FTS5, samohostované, bez AI.
>
> Repo: https://github.com/JackForest84/Linux-Admin-Assistant
>
> #linux #devops #opensource #selfhosted

---

## 🇨🇿 VARIANTA B — příběh, delší (1500 znaků)

> Pravidelně potřebuju příkazy, které nepoužívám denně — `find` s exec, `tar` flagy, `rsync` na vzdálený server. Místo googlení nebo ptaní AI jsem si postavil vlastní cheatsheet.
>
> **linuxcmd** — webová appka, kde napíšeš česky (nebo v 11 dalších jazycích) co potřebuješ, a dostaneš příkazy k jednomu kliknutí.
>
> 🔹 778 příkazů ve 36 kategoriích (disk, procesy, síť, systemd, docker, k8s, proxmox, …)
> 🔹 12 jazyků: 🇬🇧 🇨🇿 🇸🇰 🇩🇪 🇪🇸 🇫🇷 🇮🇹 🇵🇱 🇹🇷 🇵🇹 🇳🇱 🇭🇺
> 🔹 Fulltext s diakritikou per jazyk (SQLite FTS5)
> 🔹 Žádná AI, žádný cloud, žádná telemetrie
> 🔹 Samohostované — `curl ... | sudo bash` a běží
>
> **Stack**: Python (FastAPI) + vanilla JS + nginx + systemd, vše v LXC kontejneru na Proxmoxu. 200 řádků backend, 100 řádků frontend, zbytek YAML data.
>
> Nasazeno za víkend, používám denně.
>
> Repo (MIT): https://github.com/JackForest84/Linux-Admin-Assistant
>
> #linux #devops #sysadmin #opensource #selfhosted #fastapi #python #proxmox

---

## 🇬🇧 VARIANTA C — anglická, kratší (1000 znaků)

> I built a multilingual Linux cheatsheet for sysadmins & DevOps engineers.
>
> Type in plain language ("free disk space", "freier Speicherplatz", "tüm açık portlar"…) and get the commands you need — one click to copy.
>
> 🔹 778 commands across 36 categories
> 🔹 12 languages (EN, CS, SK, DE, ES, FR, IT, PL, TR, PT, NL, HU)
> 🔹 SQLite FTS5 full-text search with per-language diacritics
> 🔹 Self-hosted, no AI, no telemetry
> 🔹 One-command install on any Debian/Ubuntu box
>
> Stack: FastAPI + vanilla JS + nginx + systemd, deployed in an LXC container on Proxmox. Open source under MIT.
>
> Repo: https://github.com/JackForest84/Linux-Admin-Assistant
>
> #linux #devops #sysadmin #opensource #selfhosted #fastapi

---

## Tipy

### Obrázek / GIF
- Udělej screenshot domovské stránky se search boxem a 2-3 výsledky (např. hledání "disk" v němčině — vizuálně silné, ukazuje multi-lang).
- Ještě lepší: 5-sekundový GIF, kde přepínáš jazyky a vidíš překlady. Použij Kap (macOS) nebo Gifox.

### Časování
- **Úterý-čtvrtek dopoledne** (9-11 SEČ) má nejlepší engagement na LinkedIn pro IT obsah.

### Hashtagy
Doporučuju 3-5 hashtagů (víc = horší dosah). Nejlepší výběr:
- `#linux` `#devops` `#opensource` `#selfhosted` `#sysadmin`

### Engagement boost
- V prvních 30 minutách po publikaci sám reaguj na komentáře — algoritmus to zaboduje.
- Tag relevantní lidi: někdo z FastAPI komunity, někdo z Proxmox komunity.

### Reposty
- Po týdnu repost jako "update" — např. "778 commands, 12 languages, 200+ stars" (pokud chytíš stars).

---

## Po publikaci

1. Přidej projekt do **LinkedIn → Featured** sekce na profilu (pinne se nahoru)
2. Přidej do **Projects** sekce s URL na GitHub
3. Do **About** přidej řádek: "Built linuxcmd — open-source multilingual Linux cheatsheet (12 langs, 800 commands)"
