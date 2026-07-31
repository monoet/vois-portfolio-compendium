
const state = {
  references: [],
  candidates: [],
  captures: [],
  principles: [],
  activeTab: "references",
};

const el = (id) => document.getElementById(id);
const normalize = (value) => String(value ?? "").toLowerCase();

async function loadJson(path, fallback = []) {
  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`${path}: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn(error);
    return fallback;
  }
}

function allSearchableText(item) {
  return normalize([
    item.title,
    item.creator,
    item.summary,
    item.takeaway,
    item.vois_application,
    item.status,
    ...(item.disciplines || []),
    ...(item.tags || []),
    ...(item.changed_files || []),
  ].join(" "));
}

function currentFilters() {
  return {
    search: normalize(el("searchInput").value),
    discipline: el("disciplineFilter").value,
    status: el("statusFilter").value,
  };
}

function passesFilters(item) {
  const filters = currentFilters();
  const disciplineMatch =
    filters.discipline === "all" ||
    (item.disciplines || []).includes(filters.discipline);
  const statusMatch =
    filters.status === "all" ||
    item.status === filters.status;
  const searchMatch =
    !filters.search || allSearchableText(item).includes(filters.search);
  return disciplineMatch && statusMatch && searchMatch;
}

function tagList(tags = []) {
  return `<div class="tags">${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderReferences() {
  const items = state.references.filter(passesFilters);
  el("referenceGrid").innerHTML = items.map(item => `
    <article class="card">
      <div class="card-topline">
        <span class="badge">${escapeHtml((item.disciplines || []).join(" · "))}</span>
        <span class="status">${escapeHtml(item.status)}</span>
      </div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.summary)}</p>
      <p class="takeaway"><strong>Why it matters:</strong> ${escapeHtml(item.takeaway)}</p>
      <ul class="meta-list">
        <li><strong>VOIS use:</strong> ${escapeHtml(item.vois_application)}</li>
        <li><strong>Source:</strong> ${item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.creator || item.url)}</a>` : escapeHtml(item.creator || "Local capture")}</li>
      </ul>
      ${tagList(item.tags)}
    </article>
  `).join("");
  el("referenceEmpty").hidden = items.length > 0;
}

function renderCandidates() {
  const combined = [...state.candidates.manual, ...state.candidates.harvested].filter(passesFilters);
  el("candidateGrid").innerHTML = combined.map(item => `
    <article class="card">
      <div class="card-topline">
        <span class="badge">${escapeHtml((item.disciplines || []).join(" · "))}</span>
        <span class="status">${escapeHtml(item.status)}</span>
      </div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.summary || item.rationale)}</p>
      <ul class="meta-list">
        ${item.commit ? `<li><strong>Commit:</strong> <code>${escapeHtml(item.commit.slice(0, 8))}</code></li>` : ""}
        ${item.date ? `<li><strong>Date:</strong> ${escapeHtml(item.date)}</li>` : ""}
        ${item.suggested_output ? `<li><strong>Could become:</strong> ${escapeHtml(item.suggested_output)}</li>` : ""}
        ${item.media_needed?.length ? `<li><strong>Capture next:</strong> ${escapeHtml(item.media_needed.join(", "))}</li>` : ""}
      </ul>
      ${tagList(item.tags)}
    </article>
  `).join("");
  el("candidateEmpty").hidden = combined.length > 0;
}

function renderCaptures() {
  const items = state.captures.filter(passesFilters);
  el("captureGrid").innerHTML = items.map(item => `
    <article class="card">
      <div class="card-topline">
        <span class="badge">${escapeHtml(item.type)}</span>
        <span class="status">${escapeHtml(item.status)}</span>
      </div>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.note)}</p>
      <ul class="meta-list">
        <li><strong>Source:</strong> ${escapeHtml(item.source)}</li>
        <li><strong>Next action:</strong> ${escapeHtml(item.next_action)}</li>
      </ul>
      ${tagList(item.tags)}
    </article>
  `).join("");
  el("captureEmpty").hidden = items.length > 0;
}

function renderPrinciples() {
  el("principleGrid").innerHTML = state.principles.map(item => `
    <article class="principle">
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.description)}</p>
    </article>
  `).join("");
}

function renderMetrics() {
  const candidates = [...state.candidates.manual, ...state.candidates.harvested];
  const needsCapture = candidates.filter(item => item.status === "needs-capture").length;
  const metrics = [
    ["References", state.references.length],
    ["VOIS candidates", candidates.length],
    ["Pending captures", state.captures.length + needsCapture],
    ["Disciplines", new Set([...state.references, ...candidates].flatMap(x => x.disciplines || [])).size],
  ];
  el("metrics").innerHTML = metrics.map(([label, value]) => `
    <article class="metric"><strong>${value}</strong><span>${label}</span></article>
  `).join("");
}

function populateFilters() {
  const candidates = [...state.candidates.manual, ...state.candidates.harvested];
  const all = [...state.references, ...candidates, ...state.captures];
  const disciplines = [...new Set(all.flatMap(item => item.disciplines || []))].sort();
  const statuses = [...new Set(all.map(item => item.status).filter(Boolean))].sort();

  el("disciplineFilter").innerHTML += disciplines.map(value =>
    `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
  ).join("");

  el("statusFilter").innerHTML += statuses.map(value =>
    `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`
  ).join("");
}

function rerender() {
  renderReferences();
  renderCandidates();
  renderCaptures();
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach(button => {
    button.addEventListener("click", () => {
      state.activeTab = button.dataset.tab;
      document.querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", tab === button));
      document.querySelectorAll(".panel").forEach(panel =>
        panel.classList.toggle("active-panel", panel.id === state.activeTab)
      );
    });
  });
}

async function init() {
  const referencesData = await loadJson("./data/references.json", { references: [], principles: [] });
  const candidatesData = await loadJson("./data/showcase-candidates.json", { candidates: [] });
  const harvestedData = await loadJson("./data/harvested-commits.json", { candidates: [] });
  const capturesData = await loadJson("./data/capture-queue.json", { captures: [] });

  state.references = referencesData.references || [];
  state.principles = referencesData.principles || [];
  state.candidates = {
    manual: candidatesData.candidates || [],
    harvested: harvestedData.candidates || [],
  };
  state.captures = capturesData.captures || [];

  populateFilters();
  renderMetrics();
  renderPrinciples();
  rerender();
  setupTabs();

  ["searchInput", "disciplineFilter", "statusFilter"].forEach(id =>
    el(id).addEventListener("input", rerender)
  );

  el("themeToggle").addEventListener("click", () => {
    document.documentElement.classList.toggle("light");
    localStorage.setItem("compendium-theme", document.documentElement.classList.contains("light") ? "light" : "dark");
  });

  if (localStorage.getItem("compendium-theme") === "light") {
    document.documentElement.classList.add("light");
  }
}

init();
