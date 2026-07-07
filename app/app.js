// UI layer only. All prompt text, splitting, cleanup and export run in the
// Python core via window.pywebview.api (see src/sticker_forge/webapi.py).

const UI = {
  "zh-Hant": {
    subtitle: "LINE 靜態貼圖本機製作台",
    languageLabel: "語言",
    statusReady: "等待素材",
    copy: "複製",
    character: "角色",
    theme: "主題",
    tone: "語氣",
    promptLanguage: "語言",
    style: "風格",
    withText: "有字版",
    background: "背景色",
    importGrid: "匯入 3x3",
    dropHint: "把 3x3 圖拖放到這裡，或用上方「匯入 3x3」",
    split: "切圖",
    cleanup: "去背",
    cleanupOne: "去背這張",
    resetOne: "還原",
    savePng: "存 PNG",
    zoomHint: "點擊放大檢視",
    selectFirstEight: "選前 8 張",
    exportPng: "匯出 9 張 PNG",
    exportZip: "匯出 ZIP",
    cleanupTune: "去背強度",
    tuneSafe: "保守",
    tuneBalanced: "平衡",
    tuneAggressive: "強力",
    padding: "Padding",
    exportPreview: "匯出前預覽",
    submissionTitle: "LINE Creators Market 上架",
    submission1: "到 creator.line.me 登入 LINE 帳號。",
    submission2: "新增 Sticker，填寫貼圖介紹、圖片編輯、販售資訊。",
    submission3: "在圖片編輯頁上傳整包 ZIP，或逐張上傳 main.png、tab.png、01.png 到 08.png。",
    submission4: "三個區段完成後點「申請販售」。通過後再手動點「上架」。",
    copied: "Prompt 已複製",
    imported: (name) => `已匯入 ${name}`,
    splitting: "切圖中…",
    needGrid: "請先匯入 3x3 圖",
    splitDone: "已切成 9 張 LINE 尺寸貼圖",
    selectedCount: (count) => `目前選 ${count} 張`,
    firstEight: "已選前 8 張",
    noTilesCleanup: "沒有可去背的貼圖",
    cleaning: "去背中…",
    cleanupDone: "已去背",
    needEight: (count) => `LINE 最小套組需選 8 張，目前 ${count} 張`,
    exporting: "匯出中…",
    exportCancelled: "已取消",
    saved: (path) => `已儲存：${path}`,
    noTilesExport: "沒有可匯出的貼圖",
    selectedSummary: (count) => `${count} / 8 已選`,
    previewPlaceholder: "匯入 3x3 圖後會列出 01.png 到 08.png、main.png、tab.png。",
    previewSticker: (index, included) => `${String(index).padStart(2, "0")}.png：370 x 320${included ? "" : "（未選）"}`,
    previewMain: "main.png：240 x 240",
    previewTab: "tab.png：96 x 74",
    bridgeMissing: "請用 sticker-forge.exe 開啟（此頁需要本機程式）。",
  },
  en: {
    subtitle: "Local LINE static sticker workspace",
    languageLabel: "Language",
    statusReady: "Waiting for artwork",
    copy: "Copy",
    character: "Character",
    theme: "Theme",
    tone: "Tone",
    promptLanguage: "Prompt language",
    style: "Style",
    withText: "Text version",
    background: "Background",
    importGrid: "Import 3x3",
    dropHint: "Drag a 3x3 image here, or use Import 3x3 above",
    split: "Split",
    cleanup: "Clean up",
    cleanupOne: "Clean this",
    resetOne: "Reset",
    savePng: "Save PNG",
    zoomHint: "Click to zoom",
    selectFirstEight: "Select first 8",
    exportPng: "Export 9 PNG",
    exportZip: "Export ZIP",
    cleanupTune: "Cleanup strength",
    tuneSafe: "Safe",
    tuneBalanced: "Balanced",
    tuneAggressive: "Aggressive",
    padding: "Padding",
    exportPreview: "Pre-export preview",
    submissionTitle: "LINE Creators Market submission",
    submission1: "Sign in to creator.line.me with a LINE account.",
    submission2: "Create a Sticker item and fill in description, image, and sales information.",
    submission3: "Upload the ZIP on the image editing page, or upload main.png, tab.png, and 01.png to 08.png one by one.",
    submission4: "After all three sections are complete, request review. After approval, publish manually.",
    copied: "Prompt copied",
    imported: (name) => `Imported ${name}`,
    splitting: "Splitting…",
    needGrid: "Import a 3x3 image first",
    splitDone: "Split into 9 LINE-size stickers",
    selectedCount: (count) => `${count} selected`,
    firstEight: "Selected first 8",
    noTilesCleanup: "No stickers to clean up",
    cleaning: "Cleaning up…",
    cleanupDone: "Background cleaned",
    needEight: (count) => `LINE minimum set needs 8 stickers; ${count} selected`,
    exporting: "Exporting…",
    exportCancelled: "Cancelled",
    saved: (path) => `Saved: ${path}`,
    noTilesExport: "No stickers to export",
    selectedSummary: (count) => `${count} / 8 selected`,
    previewPlaceholder: "Import a 3x3 image to list 01.png to 08.png, main.png, and tab.png.",
    previewSticker: (index, included) => `${String(index).padStart(2, "0")}.png: 370 x 320${included ? "" : " (not selected)"}`,
    previewMain: "main.png: 240 x 240",
    previewTab: "tab.png: 96 x 74",
    bridgeMissing: "Please open with sticker-forge.exe (this page needs the local app).",
  },
};

const PACK_SIZE = 8;
const state = {
  locale: UI[localStorage.getItem("stickerForgeLocale")] ? localStorage.getItem("stickerForgeLocale") : "zh-Hant",
  sourceDataUrl: null,
  tiles: [],
  zoomIndex: -1,
};
// bootstrap data (defaults, suggestions, spec) per locale, from Python
const boots = {};

const $ = (id) => document.getElementById(id);
const ui = () => UI[state.locale] || UI["zh-Hant"];
const boot = () => boots[state.locale] || boots["zh-Hant"];
const api = () => (window.pywebview && window.pywebview.api) || null;

function setStatus(text, danger = false) {
  const status = $("status");
  status.textContent = text;
  status.style.color = danger ? "#fecaca" : "#e5e7eb";
}

function applyLocale(previousLocale = state.locale) {
  const data = ui();
  const cur = boot();
  const prev = boots[previousLocale] || cur;
  document.documentElement.lang = state.locale;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (typeof data[key] === "string") node.textContent = data[key];
  });
  const swap = (id, nextValues, prevValues) => {
    const input = $(id);
    if (!input.value || prevValues.includes(input.value)) input.value = nextValues;
  };
  const fieldNames = ["character", "theme", "tone", "style", "language"];
  fieldNames.forEach((name) => {
    const others = Object.values(boots).map((b) => b.defaults[name]);
    swap(name, cur.defaults[name], others);
  });
  document.querySelectorAll(".slot-text").forEach((input, i) => {
    if (!input.value || prev.texts.includes(input.value)) input.value = cur.texts[i];
  });
  document.querySelectorAll(".slot-action").forEach((input, i) => {
    if (!input.value || prev.actions.includes(input.value)) input.value = cur.actions[i];
  });
  populateDatalists();
  $("ui-language").value = state.locale;
  setStatus(data.statusReady);
  renderPrompt();
}

function populateDatalists() {
  const s = boot().suggestions;
  const fill = (id, items) => {
    const list = $(id);
    if (!list) return;
    list.innerHTML = "";
    (items || []).forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      list.appendChild(option);
    });
  };
  fill("dl-character", s.character);
  fill("dl-theme", s.theme);
  fill("dl-tone", s.tone);
  fill("dl-style", s.style);
  fill("dl-language", s.language);
  fill("dl-text", s.texts);
  fill("dl-action", s.actions);
}

function setLocale(locale) {
  const previousLocale = state.locale;
  state.locale = UI[locale] ? locale : "zh-Hant";
  localStorage.setItem("stickerForgeLocale", state.locale);
  applyLocale(previousLocale);
  updatePreview();
}

function setupSlots() {
  const slots = $("slots");
  const tpl = $("slot-template");
  const cur = boot();
  for (let i = 0; i < PACK_SIZE; i++) {
    const row = tpl.content.firstElementChild.cloneNode(true);
    row.querySelector(".slot-num").textContent = String(i + 1).padStart(2, "0");
    row.querySelector(".slot-text").value = cur.texts[i];
    row.querySelector(".slot-action").value = cur.actions[i];
    slots.appendChild(row);
  }
}

function slotValues(selector) {
  return Array.from(document.querySelectorAll(selector)).map((input) => input.value.trim());
}

async function renderPrompt() {
  const bridge = api();
  if (!bridge) return;
  const payload = {
    locale: state.locale,
    withText: $("with-text").checked,
    character: $("character").value,
    theme: $("theme").value,
    tone: $("tone").value,
    style: $("style").value,
    language: $("language").value,
    texts: slotValues(".slot-text"),
    actions: slotValues(".slot-action"),
    chromaKey: $("chroma-key").value,
  };
  try {
    $("prompt-output").value = await bridge.render_prompt(payload);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function copyPrompt() {
  await navigator.clipboard.writeText($("prompt-output").value);
  setStatus(ui().copied);
}

function options() {
  return {
    keyName: $("chroma-key").value,
    tune: $("cleanup-tune").value,
    padding: Number($("sticker-padding").value),
  };
}

function loadGrid(file) {
  const reader = new FileReader();
  reader.onload = () => {
    state.sourceDataUrl = reader.result;
    drawSourcePreview(reader.result);
    setStatus(ui().imported(file.name));
    splitGrid();
  };
  reader.readAsDataURL(file);
}

function drawSourcePreview(dataUrl) {
  const canvas = $("source-canvas");
  const ctx = canvas.getContext("2d");
  const img = new Image();
  img.onload = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const scale = Math.min(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
    const w = img.naturalWidth * scale;
    const h = img.naturalHeight * scale;
    ctx.drawImage(img, (canvas.width - w) / 2, (canvas.height - h) / 2, w, h);
  };
  img.src = dataUrl;
}

async function splitGrid() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (!state.sourceDataUrl) return setStatus(ui().needGrid, true);
  setStatus(ui().splitting);
  try {
    const urls = await bridge.split(state.sourceDataUrl, { ...options(), cleanup: false });
    state.tiles = urls.map((url, i) => ({ raw: url, url, included: i < PACK_SIZE }));
    renderTiles();
    updatePreview();
    setStatus(ui().splitDone);
  } catch (err) {
    setStatus(String(err), true);
  }
}

function renderTiles() {
  const grid = $("tile-grid");
  grid.innerHTML = "";
  state.tiles.forEach((tile, i) => {
    const item = document.createElement("div");
    item.className = `tile${tile.included ? "" : " excluded"}`;
    const img = document.createElement("img");
    img.src = tile.url;
    img.alt = `${i + 1}`;
    img.title = ui().zoomHint;
    img.addEventListener("click", () => openZoom(i));
    item.appendChild(img);
    const footer = document.createElement("div");
    footer.className = "tile-footer";
    const label = document.createElement("label");
    label.className = "check";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = tile.included;
    checkbox.addEventListener("change", () => {
      tile.included = checkbox.checked;
      item.classList.toggle("excluded", !tile.included);
      updatePreview();
      setStatus(ui().selectedCount(includedTiles().length));
    });
    label.append(checkbox, ` ${String(i + 1).padStart(2, "0")}`);
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "PNG";
    button.addEventListener("click", () => savePng(tile.url, `sticker-${String(i + 1).padStart(2, "0")}.png`));
    footer.append(label, button);
    item.appendChild(footer);
    grid.appendChild(item);
  });
}

function includedTiles() {
  return state.tiles.filter((tile) => tile.included);
}

function selectFirstEight() {
  state.tiles.forEach((tile, index) => {
    tile.included = index < PACK_SIZE;
  });
  renderTiles();
  updatePreview();
  setStatus(ui().firstEight);
}

async function cleanupAll() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (!state.tiles.length) return setStatus(ui().noTilesCleanup, true);
  setStatus(ui().cleaning);
  try {
    // Clean from the original split so re-cleaning (e.g. after changing the
    // strength) never stacks on an already-cleaned tile.
    const urls = await bridge.cleanup(state.tiles.map((t) => t.raw), options());
    state.tiles.forEach((tile, i) => {
      tile.url = urls[i];
    });
    renderTiles();
    updatePreview();
    setStatus(ui().cleanupDone);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function cleanupOne(index) {
  const bridge = api();
  if (!bridge || !state.tiles[index]) return;
  try {
    const [url] = await bridge.cleanup([state.tiles[index].raw], options());
    state.tiles[index].url = url;
    renderTiles();
    if (state.zoomIndex === index) $("zoom-img").src = url;
    setStatus(ui().cleanupDone);
  } catch (err) {
    setStatus(String(err), true);
  }
}

function resetOne(index) {
  const tile = state.tiles[index];
  if (!tile) return;
  tile.url = tile.raw;
  renderTiles();
  if (state.zoomIndex === index) $("zoom-img").src = tile.url;
}

function openZoom(index) {
  const tile = state.tiles[index];
  if (!tile) return;
  state.zoomIndex = index;
  $("zoom-title").textContent = `${String(index + 1).padStart(2, "0")}.png · 370 x 320`;
  $("zoom-img").src = tile.url;
  $("zoom-modal").hidden = false;
}

function closeZoom() {
  state.zoomIndex = -1;
  $("zoom-modal").hidden = true;
}

async function exportZip() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  const selected = includedTiles();
  if (selected.length !== PACK_SIZE) return setStatus(ui().needEight(selected.length), true);
  setStatus(ui().exporting);
  try {
    const result = await bridge.export_line(selected.map((t) => t.url), options());
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportStickersOnly() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (!state.tiles.length) return setStatus(ui().noTilesExport, true);
  setStatus(ui().exporting);
  try {
    const result = await bridge.export_stickers(state.tiles.map((t) => t.url), options());
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function savePng(dataUrl, defaultName) {
  const bridge = api();
  if (!bridge) return;
  try {
    reportExport(await bridge.save_png(dataUrl, defaultName));
  } catch (err) {
    setStatus(String(err), true);
  }
}

function reportExport(result) {
  if (result && result.saved) setStatus(ui().saved(result.saved));
  else if (result && result.cancelled) setStatus(ui().exportCancelled);
}

function updatePreview() {
  const data = ui();
  const selected = includedTiles();
  $("selection-summary").textContent = data.selectedSummary(selected.length);
  $("padding-value").textContent = `${$("sticker-padding").value} px`;
  const errors = $("preview-errors");
  errors.innerHTML = "";
  if (!state.tiles.length) {
    const item = document.createElement("li");
    item.textContent = data.previewPlaceholder;
    errors.appendChild(item);
  } else if (selected.length !== PACK_SIZE) {
    const item = document.createElement("li");
    item.textContent = data.needEight(selected.length);
    errors.appendChild(item);
  }
  $("export-zip").disabled = selected.length !== PACK_SIZE;
  const files = $("preview-files");
  files.innerHTML = "";
  if (!state.tiles.length) return;
  state.tiles.forEach((tile, index) => {
    const item = document.createElement("div");
    item.className = "preview-file";
    item.textContent = data.previewSticker(index + 1, tile.included);
    files.appendChild(item);
  });
  for (const text of [data.previewMain, data.previewTab]) {
    const item = document.createElement("div");
    item.className = "preview-file";
    item.textContent = text;
    files.appendChild(item);
  }
}

function setupDropzone() {
  const zone = $("dropzone");
  if (!zone) return;
  const stop = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };
  ["dragenter", "dragover"].forEach((type) =>
    zone.addEventListener(type, (event) => {
      stop(event);
      zone.classList.add("dragover");
    })
  );
  ["dragleave", "dragend"].forEach((type) =>
    zone.addEventListener(type, (event) => {
      stop(event);
      zone.classList.remove("dragover");
    })
  );
  zone.addEventListener("drop", (event) => {
    stop(event);
    zone.classList.remove("dragover");
    const file = Array.from(event.dataTransfer?.files || []).find((item) => item.type.startsWith("image/"));
    if (file) loadGrid(file);
  });
}

function bindEvents() {
  document.querySelectorAll("input, select").forEach((node) => node.addEventListener("input", renderPrompt));
  $("sticker-padding").addEventListener("input", updatePreview);
  $("cleanup-tune").addEventListener("change", updatePreview);
  $("ui-language").addEventListener("change", (event) => setLocale(event.target.value));
  $("copy-prompt").addEventListener("click", copyPrompt);
  $("grid-file").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) loadGrid(file);
  });
  setupDropzone();
  $("split-grid").addEventListener("click", splitGrid);
  $("cleanup-all").addEventListener("click", cleanupAll);
  $("select-first-eight").addEventListener("click", selectFirstEight);
  $("export-stickers").addEventListener("click", exportStickersOnly);
  $("export-zip").addEventListener("click", exportZip);
  $("zoom-close").addEventListener("click", closeZoom);
  $("zoom-modal").addEventListener("click", (event) => {
    if (event.target === $("zoom-modal")) closeZoom();
  });
  $("zoom-clean").addEventListener("click", () => cleanupOne(state.zoomIndex));
  $("zoom-reset").addEventListener("click", () => resetOne(state.zoomIndex));
  $("zoom-png").addEventListener("click", () => {
    const tile = state.tiles[state.zoomIndex];
    if (tile) savePng(tile.url, `sticker-${String(state.zoomIndex + 1).padStart(2, "0")}.png`);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("zoom-modal").hidden) closeZoom();
  });
}

async function init() {
  const bridge = api();
  if (!bridge) {
    setStatus(ui().bridgeMissing, true);
    return;
  }
  boots["zh-Hant"] = await bridge.bootstrap("zh-Hant");
  boots.en = await bridge.bootstrap("en");
  $("ui-language").value = state.locale;
  setupSlots();
  bindEvents();
  applyLocale();
  updatePreview();
}

if (window.pywebview && window.pywebview.api) init();
else window.addEventListener("pywebviewready", init);
