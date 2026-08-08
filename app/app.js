// UI layer only. All prompt text, splitting, cleanup and export run in the
// Python core via window.pywebview.api (see src/sticker_forge/webapi.py).

const UI = {
  "zh-Hant": {
    subtitle: "LINE 靜態貼圖本機製作台",
    languageLabel: "語言",
    statusReady: "等待素材",
    copy: "複製",
    presetLabel: "主題預設",
    presetNone: "—（自訂）",
    presetApplied: (label) => `已套用主題：${label}`,
    packTitle: "套組標題",
    packAuthor: "作者",
    character: "角色",
    theme: "主題",
    tone: "語氣",
    promptLanguage: "語言",
    style: "風格",
    withText: "有字版",
    background: "背景色",
    importGrid: "匯入 3x3",
    addGrid: "加入 grid",
    clearTiles: "清空",
    mainLabel: "主圖",
    tabLabel: "聊天標籤",
    moveUp: "上移",
    moveDown: "下移",
    needPackSize: (count) => `LINE 套組需 8／16／24／32／40 張，目前 ${count} 張`,
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
    exportEmoji: "匯出 LINE emoji",
    needEmoji: (count) => `LINE emoji 需 8–40 張，目前 ${count} 張`,
    exportMessage: "匯出訊息貼圖",
    needMessage: (count) => `LINE 訊息貼圖需 8／16／24 張，目前 ${count} 張`,
    exportBig: "匯出 Big Stickers",
    importAnimated: "匯入動態貼圖",
    importScreenAnimations: "匯入畫面動畫",
    exportAnimated: "匯出動態貼圖",
    exportPopup: "匯出 pop-up",
    exportEffect: "匯出 effect",
    preparing: "處理動態貼圖中…",
    preparingScreen: "處理畫面動畫中…",
    needAnimated: (count) => `LINE 動態貼圖需 8／16／24 張，目前 ${count} 張`,
    needScreenAnimations: (stickers, animations) => `pop-up / effect 需 8／16／24 張靜態貼圖，且畫面動畫數量需相同；目前 ${stickers} 張靜態、${animations} 個動畫`,
    screenAnimationImported: (count) => `已匯入 ${count} 個畫面動畫`,
    screenAnimationSummary: (count) => `畫面動畫：${count} 個 APNG`,
    animatedModeHint: "目前是動態貼圖模式，請用「匯出動態貼圖」，或重新匯入靜態 3x3 grid",
    staticModeHint: "請先匯入動態貼圖檔（GIF/APNG）",
    platformLabel: "其他平台",
    exportPlatform: "匯出到平台",
    cleanupTune: "去背強度",
    tuneSafe: "保守",
    tuneBalanced: "平衡",
    tuneAggressive: "強力",
    tuneContinuous: "連續清理（背景優先）",
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
    selectedSummary: (count) => `已選 ${count}`,
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
    presetLabel: "Theme preset",
    presetNone: "— (custom)",
    presetApplied: (label) => `Applied preset: ${label}`,
    packTitle: "Pack title",
    packAuthor: "Author",
    character: "Character",
    theme: "Theme",
    tone: "Tone",
    promptLanguage: "Prompt language",
    style: "Style",
    withText: "Text version",
    background: "Background",
    importGrid: "Import 3x3",
    addGrid: "Add grid",
    clearTiles: "Clear",
    mainLabel: "Main",
    tabLabel: "Tab",
    moveUp: "Move up",
    moveDown: "Move down",
    needPackSize: (count) => `LINE packs need 8/16/24/32/40 stickers; ${count} selected`,
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
    exportEmoji: "Export LINE emoji",
    needEmoji: (count) => `LINE emoji needs 8–40 images; ${count} selected`,
    exportMessage: "Export message stickers",
    needMessage: (count) => `LINE message stickers need 8/16/24; ${count} selected`,
    exportBig: "Export Big Stickers",
    importAnimated: "Import animated",
    importScreenAnimations: "Import screen animations",
    exportAnimated: "Export animated",
    exportPopup: "Export pop-up",
    exportEffect: "Export effect",
    preparing: "Preparing animated stickers…",
    preparingScreen: "Preparing screen animations…",
    needAnimated: (count) => `LINE animated stickers need 8/16/24; ${count} selected`,
    needScreenAnimations: (stickers, animations) => `Pop-up / effect needs 8/16/24 static stickers and the same number of screen animations; ${stickers} static, ${animations} animations`,
    screenAnimationImported: (count) => `Imported ${count} screen animations`,
    screenAnimationSummary: (count) => `Screen animations: ${count} APNG files`,
    animatedModeHint: "Animated mode: use Export animated, or re-import a static 3x3 grid",
    staticModeHint: "Import animated files (GIF/APNG) first",
    platformLabel: "Other platform",
    exportPlatform: "Export for platform",
    cleanupTune: "Cleanup strength",
    tuneSafe: "Safe",
    tuneBalanced: "Balanced",
    tuneAggressive: "Aggressive",
    tuneContinuous: "Continuous (background-first)",
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
    selectedSummary: (count) => `${count} selected`,
    previewPlaceholder: "Import a 3x3 image to list 01.png to 08.png, main.png, and tab.png.",
    previewSticker: (index, included) => `${String(index).padStart(2, "0")}.png: 370 x 320${included ? "" : " (not selected)"}`,
    previewMain: "main.png: 240 x 240",
    previewTab: "tab.png: 96 x 74",
    bridgeMissing: "Please open with sticker-forge.exe (this page needs the local app).",
  },
};

const PACK_SIZE = 8;
const LINE_PACK_SIZES = [8, 16, 24, 32, 40];
const isPackSize = (n) => LINE_PACK_SIZES.includes(n);
const state = {
  locale: "zh-Hant",
  sourceDataUrl: null,
  tiles: [],
  screenAnimations: [],
  zoomIndex: -1,
  mode: "static",
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

function blockedInAnimated() {
  if (state.mode === "animated") {
    setStatus(ui().animatedModeHint, true);
    return true;
  }
  return false;
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
  populatePresets();
  $("ui-language").value = state.locale;
  setStatus(data.statusReady);
  renderPrompt();
}

function populatePresets() {
  const select = $("preset-select");
  if (!select) return;
  const presets = boot().presets || {};
  select.innerHTML = "";
  const none = document.createElement("option");
  none.value = "";
  none.textContent = ui().presetNone;
  select.appendChild(none);
  Object.entries(presets).forEach(([key, preset]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = preset.label || key;
    select.appendChild(option);
  });
  select.value = "";
}

function applyPreset(key) {
  const preset = (boot().presets || {})[key];
  if (!preset) return;
  ["character", "theme", "tone", "style", "language"].forEach((field) => {
    if (preset[field] != null) $(field).value = preset[field];
  });
  document.querySelectorAll(".slot-text").forEach((input, i) => {
    if (preset.texts && preset.texts[i] != null) input.value = preset.texts[i];
  });
  document.querySelectorAll(".slot-action").forEach((input, i) => {
    if (preset.actions && preset.actions[i] != null) input.value = preset.actions[i];
  });
  renderPrompt();
  setStatus(ui().presetApplied(preset.label || key));
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

function loadGrid(file, append = false) {
  const reader = new FileReader();
  reader.onload = () => {
    state.sourceDataUrl = reader.result;
    drawSourcePreview(reader.result);
    setStatus(ui().imported(file.name));
    splitGrid(append);
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

async function splitGrid(append = false) {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (!state.sourceDataUrl) return setStatus(ui().needGrid, true);
  if (!append) {
    state.mode = "static";
    state.screenAnimations = [];
  }
  setStatus(ui().splitting);
  try {
    const urls = await bridge.split(state.sourceDataUrl, { ...options(), cleanup: false });
    const newTiles = urls.map((url) => ({ raw: url, url, included: false }));
    if (append) {
      state.tiles.push(...newTiles);
    } else {
      newTiles.forEach((tile, i) => {
        tile.included = i < PACK_SIZE;
      });
      state.tiles = newTiles;
    }
    renderTiles();
    updatePreview();
    setStatus(ui().splitDone);
  } catch (err) {
    setStatus(String(err), true);
  }
}

function moveTile(index, delta) {
  const target = index + delta;
  if (target < 0 || target >= state.tiles.length) return;
  const tiles = state.tiles;
  [tiles[index], tiles[target]] = [tiles[target], tiles[index]];
  renderTiles();
  updatePreview();
}

function clearTiles() {
  state.tiles = [];
  state.screenAnimations = [];
  state.mode = "static";
  renderTiles();
  updatePreview();
  setStatus(ui().statusReady);
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
    const move = document.createElement("div");
    move.className = "tile-move";
    const up = document.createElement("button");
    up.type = "button";
    up.textContent = "▲";
    up.title = ui().moveUp;
    up.addEventListener("click", () => moveTile(i, -1));
    const down = document.createElement("button");
    down.type = "button";
    down.textContent = "▼";
    down.title = ui().moveDown;
    down.addEventListener("click", () => moveTile(i, 1));
    move.append(up, down);
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "PNG";
    button.addEventListener("click", () => savePng(tile.url, `sticker-${String(i + 1).padStart(2, "0")}.png`));
    footer.append(label, move, button);
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
  if (blockedInAnimated()) return;
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
  if (!bridge || !state.tiles[index] || state.mode === "animated") return;
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
  if (blockedInAnimated()) return;
  const selected = includedTiles();
  if (!isPackSize(selected.length)) return setStatus(ui().needPackSize(selected.length), true);
  setStatus(ui().exporting);
  try {
    const mainIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const tabIndex = Math.max(0, (parseInt($("tab-index").value, 10) || 1) - 1);
    const result = await bridge.export_line(selected.map((t) => t.url), {
      ...options(),
      mainIndex,
      tabIndex,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportStickersOnly() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  if (!state.tiles.length) return setStatus(ui().noTilesExport, true);
  setStatus(ui().exporting);
  try {
    const result = await bridge.export_stickers(state.tiles.map((t) => t.url), options());
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

function readFileAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function loadAnimatedFiles(files) {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  const list = Array.from(files).filter((f) => f.type.startsWith("image/") || /\.(gif|apng|png)$/i.test(f.name));
  if (!list.length) return;
  setStatus(ui().preparing);
  try {
    const dataUrls = await Promise.all(list.map(readFileAsDataURL));
    const previews = await bridge.prepare_animated(dataUrls, {
      keyName: $("chroma-key").value,
      tune: $("cleanup-tune").value,
    });
    state.mode = "animated";
    state.screenAnimations = [];
    state.tiles = previews.map((url) => ({ raw: url, url, included: true }));
    renderTiles();
    updatePreview();
    setStatus(ui().splitDone);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function loadScreenAnimationFiles(files) {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  const list = Array.from(files).filter((f) => f.type.startsWith("image/") || /\.(gif|apng|png)$/i.test(f.name));
  if (!list.length) return;
  if (state.mode === "animated") return setStatus(ui().animatedModeHint, true);
  setStatus(ui().preparingScreen);
  try {
    const dataUrls = await Promise.all(list.map(readFileAsDataURL));
    state.screenAnimations = await bridge.prepare_screen_animations(dataUrls, {
      keyName: $("chroma-key").value,
      tune: $("cleanup-tune").value,
    });
    updatePreview();
    setStatus(ui().screenAnimationImported(state.screenAnimations.length));
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportAnimated() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (state.mode !== "animated") return setStatus(ui().staticModeHint, true);
  const selected = includedTiles();
  if (![8, 16, 24].includes(selected.length)) return setStatus(ui().needAnimated(selected.length), true);
  setStatus(ui().exporting);
  try {
    const mainIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const tabIndex = Math.max(0, (parseInt($("tab-index").value, 10) || 1) - 1);
    const result = await bridge.export_animated(selected.map((t) => t.url), {
      mainIndex,
      tabIndex,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportScreenSticker(kind) {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  const selected = includedTiles();
  if (![8, 16, 24].includes(selected.length) || state.screenAnimations.length !== selected.length) {
    return setStatus(ui().needScreenAnimations(selected.length, state.screenAnimations.length), true);
  }
  setStatus(ui().exporting);
  try {
    const mainIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const tabIndex = Math.max(0, (parseInt($("tab-index").value, 10) || 1) - 1);
    const payload = [
      selected.map((t) => t.url),
      state.screenAnimations,
      {
        mainIndex,
        tabIndex,
        title: $("pack-title").value,
        author: $("pack-author").value,
      },
    ];
    const result = kind === "popup"
      ? await bridge.export_popup(...payload)
      : await bridge.export_effect(...payload);
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportMessage() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  const selected = includedTiles();
  if (![8, 16, 24].includes(selected.length)) return setStatus(ui().needMessage(selected.length), true);
  setStatus(ui().exporting);
  try {
    const mainIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const tabIndex = Math.max(0, (parseInt($("tab-index").value, 10) || 1) - 1);
    const result = await bridge.export_message(selected.map((t) => t.url), {
      mainIndex,
      tabIndex,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportBig() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  const selected = includedTiles();
  if (![8, 16, 24, 32, 40].includes(selected.length)) return setStatus(ui().needPackSize(selected.length), true);
  setStatus(ui().exporting);
  try {
    const mainIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const tabIndex = Math.max(0, (parseInt($("tab-index").value, 10) || 1) - 1);
    const result = await bridge.export_big(selected.map((t) => t.url), {
      mainIndex,
      tabIndex,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportEmoji() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  const selected = includedTiles();
  if (selected.length < 8 || selected.length > 40) return setStatus(ui().needEmoji(selected.length), true);
  setStatus(ui().exporting);
  try {
    const thumbIndex = Math.max(0, (parseInt($("main-index").value, 10) || 1) - 1);
    const result = await bridge.export_emoji(selected.map((t) => t.url), {
      thumbIndex,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
    reportExport(result);
  } catch (err) {
    setStatus(String(err), true);
  }
}

async function exportPlatform() {
  const bridge = api();
  if (!bridge) return setStatus(ui().bridgeMissing, true);
  if (blockedInAnimated()) return;
  const chosen = includedTiles();
  const tiles = chosen.length ? chosen : state.tiles;
  if (!tiles.length) return setStatus(ui().noTilesExport, true);
  setStatus(ui().exporting);
  try {
    const result = await bridge.export_platform(tiles.map((t) => t.url), {
      platform: $("platform-target").value,
      title: $("pack-title").value,
      author: $("pack-author").value,
    });
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
  else if (result && result.error) setStatus(result.error, true);
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
  } else if (!isPackSize(selected.length)) {
    const item = document.createElement("li");
    item.textContent = data.needPackSize(selected.length);
    errors.appendChild(item);
  }
  const screenReady = [8, 16, 24].includes(selected.length) && state.screenAnimations.length === selected.length;
  if (state.screenAnimations.length && !screenReady) {
    const item = document.createElement("li");
    item.textContent = data.needScreenAnimations(selected.length, state.screenAnimations.length);
    errors.appendChild(item);
  }
  $("export-zip").disabled = !isPackSize(selected.length);
  $("export-popup").disabled = !screenReady;
  $("export-effect").disabled = !screenReady;
  populateMainTab(selected.length);
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
  if (state.screenAnimations.length) {
    const item = document.createElement("div");
    item.className = "preview-file";
    item.textContent = data.screenAnimationSummary(state.screenAnimations.length);
    files.appendChild(item);
  }
}

function populateMainTab(count) {
  ["main-index", "tab-index"].forEach((id) => {
    const select = $(id);
    const previous = parseInt(select.value, 10) || 1;
    select.innerHTML = "";
    for (let i = 1; i <= count; i++) {
      const option = document.createElement("option");
      option.value = String(i);
      option.textContent = String(i);
      select.appendChild(option);
    }
    select.value = String(Math.min(previous, count || 1));
    select.disabled = count === 0;
  });
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
  $("preset-select").addEventListener("change", (event) => {
    if (event.target.value) applyPreset(event.target.value);
  });
  $("grid-file").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) loadGrid(file);
  });
  $("add-grid-file").addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) loadGrid(file, true);
    event.target.value = "";
  });
  $("animated-files").addEventListener("change", (event) => {
    const files = event.target.files;
    if (files && files.length) loadAnimatedFiles(files);
    event.target.value = "";
  });
  $("screen-animation-files").addEventListener("change", (event) => {
    const files = event.target.files;
    if (files && files.length) loadScreenAnimationFiles(files);
    event.target.value = "";
  });
  setupDropzone();
  $("split-grid").addEventListener("click", () => splitGrid(false));
  $("cleanup-all").addEventListener("click", cleanupAll);
  $("select-first-eight").addEventListener("click", selectFirstEight);
  $("clear-tiles").addEventListener("click", clearTiles);
  $("export-stickers").addEventListener("click", exportStickersOnly);
  $("export-emoji").addEventListener("click", exportEmoji);
  $("export-message").addEventListener("click", exportMessage);
  $("export-big").addEventListener("click", exportBig);
  $("export-animated").addEventListener("click", exportAnimated);
  $("export-popup").addEventListener("click", () => exportScreenSticker("popup"));
  $("export-effect").addEventListener("click", () => exportScreenSticker("effect"));
  $("export-zip").addEventListener("click", exportZip);
  $("export-platform").addEventListener("click", exportPlatform);
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
  const initial = await bridge.bootstrap();
  boots["zh-Hant"] = initial.locale === "zh-Hant" ? initial : await bridge.bootstrap("zh-Hant");
  boots.en = initial.locale === "en" ? initial : await bridge.bootstrap("en");
  state.locale = UI[initial.locale] ? initial.locale : "zh-Hant";
  $("ui-language").value = state.locale;
  setupSlots();
  bindEvents();
  applyLocale();
  updatePreview();
}

if (window.pywebview && window.pywebview.api) init();
else window.addEventListener("pywebviewready", init);
