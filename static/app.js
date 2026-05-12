const iconCopy = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
const iconCheck = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;

// UI strings per language
const T = {
  en: { placeholder: "Search: disk, processes, network, archive…", empty: "Nothing found.", hint: n => `${n} command${n === 1 ? "" : "s"}`, copy: "Copy" },
  cs: { placeholder: "Hledej: disk, procesy, síť, archiv…", empty: "Nic nenalezeno.", hint: n => `${n} ${n === 1 ? "příkaz" : (n < 5 ? "příkazy" : "příkazů")}`, copy: "Kopírovat" },
  sk: { placeholder: "Hľadaj: disk, procesy, sieť, archív…", empty: "Nič sa nenašlo.", hint: n => `${n} ${n === 1 ? "príkaz" : (n < 5 ? "príkazy" : "príkazov")}`, copy: "Kopírovať" },
  de: { placeholder: "Suchen: Festplatte, Prozesse, Netzwerk, Archiv…", empty: "Nichts gefunden.", hint: n => `${n} Befehl${n === 1 ? "" : "e"}`, copy: "Kopieren" },
  es: { placeholder: "Buscar: disco, procesos, red, archivo…", empty: "No se encontró nada.", hint: n => `${n} comando${n === 1 ? "" : "s"}`, copy: "Copiar" },
  fr: { placeholder: "Rechercher : disque, processus, réseau, archive…", empty: "Rien trouvé.", hint: n => `${n} commande${n === 1 ? "" : "s"}`, copy: "Copier" },
  it: { placeholder: "Cerca: disco, processi, rete, archivio…", empty: "Niente trovato.", hint: n => `${n} comando${n === 1 ? "" : "i"}`, copy: "Copia" },
  pl: { placeholder: "Szukaj: dysk, procesy, sieć, archiwum…", empty: "Nic nie znaleziono.", hint: n => `${n} ${n === 1 ? "polecenie" : "poleceń"}`, copy: "Kopiuj" },
  tr: { placeholder: "Ara: disk, süreçler, ağ, arşiv…", empty: "Bir şey bulunamadı.", hint: n => `${n} komut`, copy: "Kopyala" },
  pt: { placeholder: "Pesquisar: disco, processos, rede, arquivo…", empty: "Nada encontrado.", hint: n => `${n} comando${n === 1 ? "" : "s"}`, copy: "Copiar" },
  nl: { placeholder: "Zoeken: schijf, processen, netwerk, archief…", empty: "Niets gevonden.", hint: n => `${n} commando${n === 1 ? "" : "'s"}`, copy: "Kopiëren" },
  hu: { placeholder: "Keresés: lemez, folyamatok, hálózat, archívum…", empty: "Nem található.", hint: n => `${n} parancs`, copy: "Másolás" },
};

let lang = localStorage.getItem("lang") || (navigator.language || "en").slice(0, 2);
if (!T[lang]) lang = "en";

const $q = document.getElementById("q");
const $hint = document.getElementById("hint");
const $results = document.getElementById("results");
const $lang = document.getElementById("lang");

function setLang(l) {
  if (!T[l]) l = "en";
  lang = l;
  localStorage.setItem("lang", l);
  document.documentElement.lang = l;
  $q.placeholder = T[l].placeholder;
  $lang.value = l;
  fetchResults($q.value);
}

$lang.addEventListener("change", () => setLang($lang.value));

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}

function render(items) {
  const t = T[lang];
  if (!items.length) {
    $results.innerHTML = `<div class="empty">${t.empty}</div>`;
    $hint.textContent = "";
    return;
  }
  $hint.textContent = t.hint(items.length);
  $results.innerHTML = items.map(it => {
    const title = it.title || it.id;
    const cmds = (it.commands || []).map(c => {
      const desc = c.desc || "";
      return `
        ${desc ? `<div class="desc">${escapeHtml(desc)}</div>` : ""}
        <div class="cmd">
          <code>${escapeHtml(c.cmd)}</code>
          <button class="copy" data-cmd="${escapeHtml(c.cmd)}" title="${t.copy}">${iconCopy}</button>
        </div>`;
    }).join("");
    return `<div class="card">
      <h2>${escapeHtml(title)}</h2>
      <div class="meta">${escapeHtml(it.category || "")}</div>
      ${cmds}
    </div>`;
  }).join("");

  $results.querySelectorAll(".copy").forEach(btn => {
    btn.addEventListener("click", async () => {
      const text = btn.dataset.cmd;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(text);
        } else {
          const ta = document.createElement("textarea");
          ta.value = text;
          ta.style.cssText = "position:fixed;opacity:0";
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
        }
        btn.innerHTML = iconCheck;
        btn.classList.add("ok");
        setTimeout(() => { btn.innerHTML = iconCopy; btn.classList.remove("ok"); }, 1200);
      } catch (e) { console.error(e); }
    });
  });
}

let timer;
async function fetchResults(q) {
  clearTimeout(timer);
  timer = setTimeout(async () => {
    const r = await fetch(`/api/search?q=${encodeURIComponent(q)}&lang=${lang}&limit=50`);
    const data = await r.json();
    render(data.results);
  }, 80);
}

$q.addEventListener("input", e => fetchResults(e.target.value));
setLang(lang);
