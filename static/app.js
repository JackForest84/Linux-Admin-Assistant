const iconCopy = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
const iconCheck = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;

const T = {
  cs: {
    placeholder: "Hledej: disk, procesy, síť, archiv…",
    empty: "Nic nenalezeno.",
    hint: (n) => `${n} ${n === 1 ? "příkaz" : (n < 5 ? "příkazy" : "příkazů")}`,
    copy: "Kopírovat",
    copied: "Zkopírováno",
    title: "title_cs",
    desc: "desc_cs",
  },
  en: {
    placeholder: "Search: disk, processes, network, archive…",
    empty: "Nothing found.",
    hint: (n) => `${n} command${n === 1 ? "" : "s"}`,
    copy: "Copy",
    copied: "Copied",
    title: "title_en",
    desc: "desc_en",
  },
};

let lang = localStorage.getItem("lang") || "cs";
const $q = document.getElementById("q");
const $hint = document.getElementById("hint");
const $results = document.getElementById("results");

function setLang(l) {
  lang = l;
  localStorage.setItem("lang", l);
  document.documentElement.lang = l;
  $q.placeholder = T[l].placeholder;
  document.querySelectorAll(".lang button").forEach(b =>
    b.classList.toggle("active", b.dataset.lang === l));
  fetchResults($q.value);
}

document.querySelectorAll(".lang button").forEach(b =>
  b.addEventListener("click", () => setLang(b.dataset.lang)));

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
    const title = it[t.title] || it.title_cs || it.title_en || it.id;
    const cmds = (it.commands || []).map(c => {
      const desc = c[t.desc] || c.desc_cs || c.desc_en || "";
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
