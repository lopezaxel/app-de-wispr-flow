function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

function formatTime(isoUtc) {
  try {
    const d = new Date(isoUtc);
    return d.toLocaleString(undefined, {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoUtc;
  }
}

function setupTabs() {
  const tabs = document.querySelectorAll(".tab");
  const views = document.querySelectorAll(".view");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;

      tabs.forEach((t) => {
        t.classList.toggle("is-active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });
      views.forEach((v) => {
        v.classList.toggle("is-active", v.id === `view-${target}`);
      });

      if (target === "historial") loadHistory();
      if (target === "diccionario") loadDictionary();
    });
  });
}

async function loadStats() {
  const stats = await window.pywebview.api.get_stats();
  document.getElementById("stat-total").textContent = stats.total_dictations;
  document.getElementById("stat-edited").textContent = stats.edited_dictations;
  document.getElementById("stat-words").textContent = stats.total_words;
  document.getElementById("resumen-empty").hidden = stats.total_dictations > 0;
}

async function loadHistory() {
  const list = document.getElementById("history-list");
  const empty = document.getElementById("history-empty");
  const items = await window.pywebview.api.get_history();

  empty.hidden = items.length > 0;
  list.innerHTML = items
    .map((item) => {
      const diff =
        item.was_edited && item.raw_text !== item.final_text
          ? `<div class="history-diff">
               <span class="diff-label">Antes</span>
               <span class="diff-before">${escapeHtml(item.raw_text)}</span>
             </div>`
          : "";
      return `<li class="history-row">
        <div class="history-time">${formatTime(item.created_at)}</div>
        <div class="history-text">${escapeHtml(item.final_text)}</div>
        ${diff}
      </li>`;
    })
    .join("");
}

async function loadDictionary() {
  await Promise.all([loadWords(), loadSuggestions()]);
}

async function loadWords(existingWords) {
  const list = document.getElementById("word-list");
  const empty = document.getElementById("dictionary-empty");
  const words = existingWords ?? (await window.pywebview.api.get_dictionary());

  empty.hidden = words.length > 0;
  list.innerHTML = words
    .map(
      (word) => `<li class="word-chip">
        <span>${escapeHtml(word)}</span>
        <button type="button" data-word="${escapeHtml(word)}" aria-label="Eliminar ${escapeHtml(word)}">✕</button>
      </li>`
    )
    .join("");

  list.querySelectorAll("button[data-word]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const updated = await window.pywebview.api.remove_dictionary_word(btn.dataset.word);
      loadWords(updated);
    });
  });
}

async function loadSuggestions() {
  const list = document.getElementById("suggestion-list");
  const empty = document.getElementById("suggestions-empty");
  const corrections = await window.pywebview.api.get_corrections();

  empty.hidden = corrections.length > 0;
  list.innerHTML = corrections
    .map(
      (c, i) => `<li class="suggestion-row">
        <div class="suggestion-text">
          <span class="diff-before">${escapeHtml(c.original_phrase)}</span>
          → ${escapeHtml(c.corrected_phrase)}
          <span class="suggestion-count">×${c.count}</span>
        </div>
        <button type="button" class="suggestion-add" data-index="${i}">Agregar</button>
      </li>`
    )
    .join("");

  list.querySelectorAll("button.suggestion-add").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const correction = corrections[Number(btn.dataset.index)];
      const updated = await window.pywebview.api.add_dictionary_word(correction.corrected_phrase);
      await loadWords(updated);
      btn.closest("li").remove();
    });
  });
}

function setupWordForm() {
  const form = document.getElementById("word-form");
  const input = document.getElementById("word-input");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const word = input.value.trim();
    if (!word) return;
    const updated = await window.pywebview.api.add_dictionary_word(word);
    input.value = "";
    loadWords(updated);
  });
}

function init() {
  setupTabs();
  setupWordForm();
  loadStats();
}

if (window.pywebview) {
  init();
} else {
  window.addEventListener("pywebviewready", init);
}
