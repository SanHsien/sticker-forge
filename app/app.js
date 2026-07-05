const STICKER_W = 370;
const STICKER_H = 320;
const MAIN_SIZE = 240;
const TAB_W = 96;
const TAB_H = 74;
const SPLIT_INSET_RATIO = 0.03;
const PACK_SIZE = 8;

const chromaKeys = {
  green: {
    label: "PURE NEON GREEN",
    hex: "#00FF00",
    rgb: [0, 255, 0],
    avoid: "green, neon green, chroma green, green-tinted colors",
    substitutions: "red, orange, blue, purple, yellow, pink, or neutral colors",
  },
  magenta: {
    label: "PURE NEON MAGENTA",
    hex: "#FF00FF",
    rgb: [255, 0, 255],
    avoid: "magenta, hot pink, fuchsia, neon pink, purple-pink, magenta-tinted colors",
    substitutions: "green, blue, orange, yellow, red, teal, or neutral colors",
  },
};

const defaultTexts = ["早安", "謝謝", "收到", "加油", "辛苦了", "太棒了", "等一下", "晚安"];
const defaultActions = [
  "開心揮手",
  "雙手比心",
  "點頭確認",
  "握拳打氣",
  "擦汗微笑",
  "跳起來歡呼",
  "舉手示意暫停",
  "抱著枕頭打呵欠",
];

const chromaTuneProfiles = {
  safe: { hard: 0.32, soft: 0.12, minKey: 60, maxOther: 100, dominance: 1.9 },
  balanced: { hard: 0.25, soft: 0.05, minKey: 50, maxOther: 110, dominance: 1.7 },
  aggressive: { hard: 0.20, soft: 0.04, minKey: 40, maxOther: 125, dominance: 1.45 },
};

const localeData = {
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
    split: "切圖",
    cleanup: "去背",
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
    needGrid: "請先匯入 3x3 圖",
    splitDone: "已切成 9 張 LINE 尺寸貼圖",
    selectedCount: (count) => `目前選 ${count} 張`,
    firstEight: "已選前 8 張",
    noTilesCleanup: "沒有可去背的貼圖",
    cleanupDone: (hex) => `已去除 ${hex} 背景`,
    needEight: (count) => `LINE 最小套組需選 8 張，目前 ${count} 張`,
    needGridForExport: "請先匯入並切圖。",
    zipDone: "ZIP 已匯出",
    noTilesExport: "沒有可匯出的貼圖",
    pngDone: "9 張 PNG 已匯出",
    spareCell: "空白備用格，保持同一角色與風格，不加文字。",
    spareCellNoText: "空白備用格，保持同一角色與風格。",
    selectedSummary: (count) => `${count} / 8 已選`,
    previewPlaceholder: "匯入 3x3 圖後會列出 01.png 到 08.png、main.png、tab.png。",
    previewSticker: (index, included) => `${String(index).padStart(2, "0")}.png：370 x 320${included ? "" : "（未選）"}`,
    previewMain: "main.png：240 x 240",
    previewTab: "tab.png：96 x 74",
    defaultFields: {
      character: "原創可愛角色",
      theme: "日常聊天貼圖",
      tone: "可愛、清楚、友善",
      style: "粗黑線、扁平上色、適合聊天視窗縮圖閱讀",
      language: "繁體中文",
    },
    texts: defaultTexts,
    actions: defaultActions,
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
    split: "Split",
    cleanup: "Clean up",
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
    needGrid: "Import a 3x3 image first",
    splitDone: "Split into 9 LINE-size stickers",
    selectedCount: (count) => `${count} selected`,
    firstEight: "Selected first 8",
    noTilesCleanup: "No stickers to clean up",
    cleanupDone: (hex) => `Removed ${hex} background`,
    needEight: (count) => `LINE minimum set needs 8 stickers; ${count} selected`,
    needGridForExport: "Import and split a grid first.",
    zipDone: "ZIP exported",
    noTilesExport: "No stickers to export",
    pngDone: "9 PNG stickers exported",
    spareCell: "Blank spare cell, same character and style, no text.",
    spareCellNoText: "Blank spare cell, same character and style.",
    selectedSummary: (count) => `${count} / 8 selected`,
    previewPlaceholder: "Import a 3x3 image to list 01.png to 08.png, main.png, and tab.png.",
    previewSticker: (index, included) => `${String(index).padStart(2, "0")}.png: 370 x 320${included ? "" : " (not selected)"}`,
    previewMain: "main.png: 240 x 240",
    previewTab: "tab.png: 96 x 74",
    defaultFields: {
      character: "an original cute character",
      theme: "everyday chat stickers",
      tone: "cute, clear, friendly",
      style: "bold black outlines, flat colors, readable at chat thumbnail size",
      language: "English",
    },
    texts: ["Good morning", "Thanks", "Got it", "You can do it", "Nice work", "Great", "Wait a sec", "Good night"],
    actions: [
      "happily waving",
      "making a heart with both hands",
      "nodding in confirmation",
      "cheering with a clenched fist",
      "smiling while wiping sweat",
      "jumping in celebration",
      "raising one hand to pause",
      "yawning while hugging a pillow",
    ],
  },
};

const state = {
  locale: localeData[localStorage.getItem("stickerForgeLocale")] ? localStorage.getItem("stickerForgeLocale") : "zh-Hant",
  sourceImage: null,
  tiles: [],
};

const $ = (id) => document.getElementById(id);
const currentLocale = () => localeData[state.locale] || localeData["zh-Hant"];

function setStatus(text, danger = false) {
  const status = $("status");
  status.textContent = text;
  status.style.color = danger ? "#fecaca" : "#e5e7eb";
}

function setFieldIfDefault(id, nextValue, previousValues) {
  const input = $(id);
  if (!input.value || previousValues.includes(input.value)) input.value = nextValue;
}

function applyLocale(previousLocale = state.locale) {
  const data = currentLocale();
  const previous = localeData[previousLocale] || localeData["zh-Hant"];
  document.documentElement.lang = state.locale;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (typeof data[key] === "string") node.textContent = data[key];
  });
  setFieldIfDefault("character", data.defaultFields.character, Object.values(localeData).map((item) => item.defaultFields.character));
  setFieldIfDefault("theme", data.defaultFields.theme, Object.values(localeData).map((item) => item.defaultFields.theme));
  setFieldIfDefault("tone", data.defaultFields.tone, Object.values(localeData).map((item) => item.defaultFields.tone));
  setFieldIfDefault("style", data.defaultFields.style, Object.values(localeData).map((item) => item.defaultFields.style));
  setFieldIfDefault("language", data.defaultFields.language, Object.values(localeData).map((item) => item.defaultFields.language));
  document.querySelectorAll(".slot-text").forEach((input, index) => {
    if (!input.value || previous.texts.includes(input.value)) input.value = data.texts[index];
  });
  document.querySelectorAll(".slot-action").forEach((input, index) => {
    if (!input.value || previous.actions.includes(input.value)) input.value = data.actions[index];
  });
  $("ui-language").value = state.locale;
  setStatus(data.statusReady);
  renderPrompt();
}

function setLocale(locale) {
  const previousLocale = state.locale;
  state.locale = localeData[locale] ? locale : "zh-Hant";
  localStorage.setItem("stickerForgeLocale", state.locale);
  applyLocale(previousLocale);
  updatePreview();
}

function setupSlots() {
  const slots = $("slots");
  const tpl = $("slot-template");
  const data = currentLocale();
  for (let i = 0; i < PACK_SIZE; i++) {
    const row = tpl.content.firstElementChild.cloneNode(true);
    row.querySelector(".slot-num").textContent = String(i + 1).padStart(2, "0");
    row.querySelector(".slot-text").value = data.texts[i];
    row.querySelector(".slot-action").value = data.actions[i];
    slots.appendChild(row);
  }
}

function selectedKey() {
  return chromaKeys[$("chroma-key").value] || chromaKeys.green;
}

function slotValues(selector) {
  return Array.from(document.querySelectorAll(selector)).map((input) => input.value.trim());
}

function renderPrompt() {
  const key = selectedKey();
  const data = currentLocale();
  const texts = slotValues(".slot-text");
  const actions = slotValues(".slot-action");
  const withText = $("with-text").checked;
  const common = state.locale === "en"
    ? [
      "Generate one 3x3 grid image for LINE static sticker source art.",
      "",
      `Character: ${$("character").value}`,
      `Theme: ${$("theme").value}`,
      `Tone: ${$("tone").value}`,
      `Style: ${$("style").value}`,
      `Language: ${$("language").value}`,
      "Layout: 3 columns x 3 rows, 9 cells total, each cell is an independent sticker composition.",
      `Background: solid ${key.label} (${key.hex}) for later chroma-key cleanup.`,
      `Do not use ${key.avoid} in the character, clothing, props, shadows, or highlights; use ${key.substitutions} if needed.`,
      "Keep the character consistent in every cell. Use one main character per cell; avoid complex backgrounds.",
      "Do not use existing IP, trademarks, brand characters, celebrities, political figures, or real-person likenesses.",
      "Do not generate sexual, hateful, violent, scam, personal-data, QR code, or infringing content.",
      "",
      "Grid content:",
    ]
    : [
      "請生成一張 3x3 grid 的 LINE 靜態貼圖素材圖。",
      "",
      `角色：${$("character").value}`,
      `主題：${$("theme").value}`,
      `語氣：${$("tone").value}`,
      `風格：${$("style").value}`,
      `語言：${$("language").value}`,
      "版面：3 欄 x 3 列，共 9 格，每格是獨立貼圖構圖。",
      `背景：純色 ${key.label} (${key.hex})，方便後續 chroma-key 去背。`,
      `角色、衣服、道具、陰影與反光都不要使用 ${key.avoid}；必要時改用 ${key.substitutions}。`,
      "每格角色保持一致，只放一個主要角色，不要複雜場景。",
      "不要使用既有 IP、商標、品牌角色、名人、政治人物或真人肖像。",
      "不要生成色情、仇恨、暴力、詐騙、個資、QR code 或可能侵權的內容。",
      "",
      "九宮格內容：",
    ];
  const rows = actions.map((action, i) => {
    if (state.locale === "en") {
      if (withText) return `${i + 1}. Text: "${texts[i]}", action: ${action}`;
      return `${i + 1}. Action: ${action}, do not add text`;
    }
    if (withText) return `${i + 1}. 文字：「${texts[i]}」，動作：${action}`;
    return `${i + 1}. 動作：${action}，不要加入文字`;
  });
  rows.push(`9. ${withText ? data.spareCell : data.spareCellNoText}`);
  $("prompt-output").value = [...common, ...rows].join("\n");
}

async function copyPrompt() {
  await navigator.clipboard.writeText($("prompt-output").value);
  setStatus(currentLocale().copied);
}

function loadGrid(file) {
  const img = new Image();
  img.onload = () => {
    state.sourceImage = img;
    drawSourcePreview(img);
    splitGrid();
    setStatus(currentLocale().imported(file.name));
  };
  img.src = URL.createObjectURL(file);
}

function drawSourcePreview(img) {
  const canvas = $("source-canvas");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const scale = Math.min(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);
  const w = img.naturalWidth * scale;
  const h = img.naturalHeight * scale;
  ctx.drawImage(img, (canvas.width - w) / 2, (canvas.height - h) / 2, w, h);
}

function splitGrid() {
  if (!state.sourceImage) {
    setStatus(currentLocale().needGrid, true);
    return;
  }
  const key = selectedKey();
  const img = state.sourceImage;
  const tileW = Math.floor(img.naturalWidth / 3);
  const tileH = Math.floor(img.naturalHeight / 3);
  const insetX = Math.round(tileW * SPLIT_INSET_RATIO);
  const insetY = Math.round(tileH * SPLIT_INSET_RATIO);
  state.tiles = [];

  for (let row = 0; row < 3; row++) {
    for (let col = 0; col < 3; col++) {
      const canvas = document.createElement("canvas");
      canvas.width = STICKER_W;
      canvas.height = STICKER_H;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = key.hex;
      ctx.fillRect(0, 0, STICKER_W, STICKER_H);

      const sx = col * tileW + insetX;
      const sy = row * tileH + insetY;
      const sw = tileW - insetX * 2;
      const sh = tileH - insetY * 2;
      const scale = Math.min(STICKER_W / sw, STICKER_H / sh);
      const dw = sw * scale;
      const dh = sh * scale;
      ctx.drawImage(img, sx, sy, sw, sh, (STICKER_W - dw) / 2, (STICKER_H - dh) / 2, dw, dh);
      state.tiles.push({ canvas, included: state.tiles.length < PACK_SIZE });
    }
  }
  renderTiles();
  updatePreview();
  setStatus(currentLocale().splitDone);
}

function renderTiles() {
  const grid = $("tile-grid");
  grid.innerHTML = "";
  state.tiles.forEach((tile, i) => {
    const item = document.createElement("div");
    item.className = `tile${tile.included ? "" : " excluded"}`;
    item.appendChild(tile.canvas);
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
      setStatus(currentLocale().selectedCount(includedTiles().length));
    });
    label.append(checkbox, ` ${String(i + 1).padStart(2, "0")}`);
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "PNG";
    button.addEventListener("click", () => downloadCanvas(tile.canvas, `sticker-${String(i + 1).padStart(2, "0")}.png`));
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
  setStatus(currentLocale().firstEight);
}

function cleanupAll() {
  if (!state.tiles.length) {
    setStatus(currentLocale().noTilesCleanup, true);
    return;
  }
  const keyName = $("chroma-key").value;
  state.tiles.forEach((tile) => chromaKeyCanvas(tile.canvas, keyName));
  renderTiles();
  updatePreview();
  setStatus(currentLocale().cleanupDone(selectedKey().hex));
}

function chromaKeyCanvas(canvas, keyName) {
  const ctx = canvas.getContext("2d");
  const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = img.data;
  const profile = chromaTuneProfiles[$("cleanup-tune").value] || chromaTuneProfiles.balanced;
  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const score = keyName === "magenta" ? (Math.min(r, b) - g) / 255 : (g - Math.max(r, b)) / 255;
    const pure = keyName === "magenta"
      ? Math.min(r, b) >= profile.minKey && g <= profile.maxOther && r >= g * profile.dominance && b >= g * profile.dominance
      : g >= profile.minKey && r <= profile.maxOther && b <= profile.maxOther && g >= r * profile.dominance && g >= b * profile.dominance;
    if (pure && score > profile.hard) {
      data[i + 3] = 0;
    } else if (pure && score > profile.soft) {
      data[i + 3] = Math.round(255 * (profile.hard - score) / Math.max(0.01, profile.hard - profile.soft));
    }
  }
  ctx.putImageData(img, 0, 0);
}

function fitCanvas(source, width, height, padding) {
  const out = document.createElement("canvas");
  out.width = width;
  out.height = height;
  const ctx = out.getContext("2d");
  const scale = Math.min((width - padding * 2) / source.width, (height - padding * 2) / source.height);
  const dw = source.width * scale;
  const dh = source.height * scale;
  ctx.drawImage(source, (width - dw) / 2, (height - dh) / 2, dw, dh);
  return out;
}

function canvasToBlob(canvas) {
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

async function exportZip() {
  const selected = includedTiles();
  if (selected.length !== PACK_SIZE) {
    setStatus(currentLocale().needEight(selected.length), true);
    return;
  }
  const padding = Number($("sticker-padding").value);
  const files = [];
  for (let i = 0; i < PACK_SIZE; i++) {
    files.push({
      name: `${String(i + 1).padStart(2, "0")}.png`,
      data: await canvasToBlob(fitCanvas(selected[i].canvas, STICKER_W, STICKER_H, padding)),
    });
  }
  files.push({ name: "main.png", data: await canvasToBlob(fitCanvas(selected[0].canvas, MAIN_SIZE, MAIN_SIZE, 12)) });
  files.push({ name: "tab.png", data: await canvasToBlob(fitCanvas(selected[0].canvas, TAB_W, TAB_H, 4)) });
  files.push({ name: "README.txt", data: readmeText() });
  const blob = await createZipBlob(files);
  downloadBlob(blob, `line-stickers-${Date.now()}.zip`);
  setStatus(currentLocale().zipDone);
}

async function exportStickersOnly() {
  if (!state.tiles.length) {
    setStatus(currentLocale().noTilesExport, true);
    return;
  }
  const files = [];
  for (let i = 0; i < state.tiles.length; i++) {
    files.push({
      name: `${String(i + 1).padStart(2, "0")}.png`,
      data: await canvasToBlob(fitCanvas(state.tiles[i].canvas, STICKER_W, STICKER_H, Number($("sticker-padding").value))),
    });
  }
  const blob = await createZipBlob(files);
  downloadBlob(blob, `transparent-stickers-${Date.now()}.zip`);
  setStatus(currentLocale().pngDone);
}

function updatePreview() {
  const data = currentLocale();
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

const crcTable = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) crc = crcTable[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

function writeUint16(view, offset, value) {
  view.setUint16(offset, value, true);
}

function writeUint32(view, offset, value) {
  view.setUint32(offset, value >>> 0, true);
}

async function fileBytes(data) {
  if (typeof data === "string") return new TextEncoder().encode(data);
  return new Uint8Array(await data.arrayBuffer());
}

async function createZipBlob(files) {
  const encoder = new TextEncoder();
  const chunks = [];
  const central = [];
  let offset = 0;

  for (const file of files) {
    const name = encoder.encode(file.name);
    const data = await fileBytes(file.data);
    const crc = crc32(data);
    const local = new Uint8Array(30 + name.length);
    const localView = new DataView(local.buffer);
    writeUint32(localView, 0, 0x04034b50);
    writeUint16(localView, 4, 20);
    writeUint16(localView, 6, 0x0800);
    writeUint16(localView, 8, 0);
    writeUint16(localView, 10, 0);
    writeUint16(localView, 12, 0);
    writeUint32(localView, 14, crc);
    writeUint32(localView, 18, data.length);
    writeUint32(localView, 22, data.length);
    writeUint16(localView, 26, name.length);
    writeUint16(localView, 28, 0);
    local.set(name, 30);
    chunks.push(local, data);

    const entry = new Uint8Array(46 + name.length);
    const entryView = new DataView(entry.buffer);
    writeUint32(entryView, 0, 0x02014b50);
    writeUint16(entryView, 4, 20);
    writeUint16(entryView, 6, 20);
    writeUint16(entryView, 8, 0x0800);
    writeUint16(entryView, 10, 0);
    writeUint16(entryView, 12, 0);
    writeUint16(entryView, 14, 0);
    writeUint32(entryView, 16, crc);
    writeUint32(entryView, 20, data.length);
    writeUint32(entryView, 24, data.length);
    writeUint16(entryView, 28, name.length);
    writeUint16(entryView, 30, 0);
    writeUint16(entryView, 32, 0);
    writeUint16(entryView, 34, 0);
    writeUint16(entryView, 36, 0);
    writeUint32(entryView, 38, 0);
    writeUint32(entryView, 42, offset);
    entry.set(name, 46);
    central.push(entry);
    offset += local.length + data.length;
  }

  const centralOffset = offset;
  let centralSize = 0;
  for (const entry of central) centralSize += entry.length;
  const end = new Uint8Array(22);
  const endView = new DataView(end.buffer);
  writeUint32(endView, 0, 0x06054b50);
  writeUint16(endView, 4, 0);
  writeUint16(endView, 6, 0);
  writeUint16(endView, 8, files.length);
  writeUint16(endView, 10, files.length);
  writeUint32(endView, 12, centralSize);
  writeUint32(endView, 16, centralOffset);
  writeUint16(endView, 20, 0);

  return new Blob([...chunks, ...central, end], { type: "application/zip" });
}

function readmeText() {
  if (state.locale === "en") {
    return `sticker-forge LINE static sticker ZIP

ZIP contents
- main.png: 240 x 240
- tab.png: 96 x 74
- 01.png to 08.png: 370 x 320

LINE Creators Market manual submission
1. Sign in at https://creator.line.me/ with a LINE account.
2. Create a Sticker item and fill in description, image, and sales information.
3. Upload the full ZIP on the image editing page, or upload main.png, tab.png, and 01.png to 08.png one by one.
4. After all three sections are complete, request review. After approval, publish manually.

Before review, check the latest LINE Creators Market rules, licensing, trademark, and likeness rights yourself.
`;
  }
  return `sticker-forge LINE 靜態貼圖 ZIP

ZIP 內容
- main.png：240 x 240
- tab.png：96 x 74
- 01.png 到 08.png：370 x 320

LINE Creators Market 手動上架
1. 到 https://creator.line.me/zh-hant/ 用 LINE 帳號登入。
2. 新增 Sticker，填寫貼圖介紹、圖片編輯、販售資訊。
3. 在圖片編輯頁上傳整包 ZIP，或逐張上傳 main.png、tab.png、01.png 到 08.png。
4. 三個區段完成後點「申請販售」。通過後再手動點「上架」。

送審前請自行確認 LINE Creators Market 最新規則、授權、商標與肖像權。
`;
}

function downloadCanvas(canvas, filename) {
  canvas.toBlob((blob) => downloadBlob(blob, filename), "image/png");
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
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
  $("split-grid").addEventListener("click", splitGrid);
  $("cleanup-all").addEventListener("click", cleanupAll);
  $("select-first-eight").addEventListener("click", selectFirstEight);
  $("export-stickers").addEventListener("click", exportStickersOnly);
  $("export-zip").addEventListener("click", exportZip);
}

$("ui-language").value = state.locale;
setupSlots();
bindEvents();
applyLocale();
updatePreview();
