# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
[![LINE static stickers](https://img.shields.io/badge/LINE-static_stickers-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | [English](README.en.md)

Local-first toolkit for making chat sticker packs: prompt templates, image cleanup, slicing, and export for LINE, Telegram, WhatsApp, Discord and Signal.

`sticker-forge` 是本機優先的貼圖包製作工具。以 LINE 靜態貼圖為主，也能一鍵匯出成 Telegram、WhatsApp、Discord、Signal 的尺寸與格式。它不架 AI server、不代管 API key，也不收集使用者圖片；使用者自行用 ChatGPT、Gemini 或其他生圖工具產圖，再把圖片匯回本機程式加工與匯出。

## 目標流程

1. 在 `sticker-forge` 選擇貼圖主題、語氣、角色設定、文字與輸出規格。
2. 程式產生可複製的提示詞。
3. 使用者自行到外部 AI 生圖工具產生 3x3 貼圖 grid。
4. 使用者把生成好的圖片匯回 `sticker-forge`。
5. 程式在本機切圖、去背、整理尺寸、預覽。
6. 程式匯出符合 LINE Creators Market 靜態貼圖規格的 ZIP。

現階段只鎖定 LINE 靜態貼圖包，不做 LINE 自動上架，也不保證審核通過。

## 產品原則

- 本機處理：不新增 hosted backend。
- 使用者自備 AI：不集中管理 ChatGPT / Gemini / 其他生圖服務的帳號或 API key。
- 隱私優先：不收集、上傳或保存使用者圖片。
- 可下載發行：長期目標是 Windows `.exe`。
- 上架保守：提示詞與檢查流程要提醒使用者避開侵權、商標、真人肖像、政治、色情、暴力、仇恨、個資等高風險內容。

## 功能範圍

- **提示詞**：依 LINE 規格產生 3x3 grid prompt，支援主題／角色／語氣／語言／8 句文字／8 個動作，有字與無字兩版，可複製微調。
- **圖片加工**：匯入 3x3 grid、切 9 格選 8 張、green/magenta chroma-key 去背、尺寸與 padding 整理、main/tab image、逐張預覽。
- **匯出**：LINE Creators Market 靜態貼圖 ZIP、9 張獨立 PNG 的一般貼圖 ZIP、尺寸／張數／檔名／結構檢查、簡短上架說明。

## 使用入口

| 入口 | 說明 |
|------|------|
| `sticker-forge.exe` | 桌面 GUI：pywebview 原生視窗載入 `app/` 的 HTML 介面，切圖/去背/匯出全由本機 Python core 處理，無 console，雙擊即用 |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | 命令列，支援 `--lang zh-Hant\|en` |

GUI 與 CLI 共用同一套 Python core（`app/` 只負責畫面，透過 bridge 呼叫 Python）。從原始碼安裝與打包步驟見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 目前狀態

本 repo 來自 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 的 MIT fork。原專案 web app 與 Worker 已集中搬到 `reference/upstream-line-sticker-studio/` 作為邏輯參考，不是新架構。

## 專案結構

```text
.
├── src/sticker_forge/      # 本機工具主程式
├── app/                    # 可直接開啟的本機 HTML 介面
├── prompts/                # 提示詞模板
├── packaging/              # exe 打包設定與發行流程
├── tests/                  # 自動化測試
├── examples/               # 範例輸入位置，不放侵權素材
├── docs/                   # 維護文件（DEVELOPMENT / DECISIONS / LINE_SUBMISSION）
├── reference/upstream-line-sticker-studio/   # upstream 參考，非目標架構
├── README.md / README.en.md / REVIEW.md
├── AGENTS.md / CLAUDE.md / SKILL.md          # AI 接手指引
└── NOTICE.md / LICENSE
```

## 專案狀態與路線圖

目前版本 **v0.13.0**：local-first 貼圖包工具（LINE 貼圖／emoji／訊息貼圖／動態貼圖 及多平台），桌面 GUI（pywebview 載入 HTML）與 CLI 共用同一套 Python core，`python -m pytest` 全數通過。

### ✅ 已完成

- 產品方向固定為 local-first；從 upstream 抽出可重用邏輯（切圖 inset、chroma-key、ZIP spec、LINE 尺寸）。
- prompt 模板：中英文、有字／無字、green/magenta 背景、高風險內容提醒。
- 圖片處理核心：3x3 切圖、去背、尺寸／padding、main/tab image、預覽 metadata 與選圖檢查。
- 匯出：LINE ZIP、9 張 PNG-only ZIP、`validate` 與 `preview` 指令、上架說明。
- 桌面 GUI（pywebview HTML）與 CLI 共用 Python core（`--lang` 中英）。
- PyInstaller Windows 打包與發行，已發行到 `v0.8.0`（正式 GitHub Release，含 SHA256 checksum）。
- 桌面拖放匯入（webview 的 HTML dropzone 內建）；WebView2 用 `private_mode` 臨時 profile，不寫持久隱藏資料。
- 中英文 README。

### 🔧 2026-07-07 一致性修正

- **切圖尺寸**：`split_grid` 不再要求邊長可被 3 整除，改向下取整丟餘數（對齊 web `Math.floor`），最常見的 1024×1024 AI 生圖在 CLI / GUI / web 都能處理。
- **`--key-color`**：從 `export` / `stickers` / `preview` 移除死參數（那條路徑固定走 green/magenta score-based 去背），保留在 `cleanup`。
- **web 去背 despill**：`app/app.js` 對齊 Python 的 despill，三入口去背輸出一致（60/60 像素交叉比對）。
- **打包驗證**：實測 PyInstaller build，GUI `--smoke`、CLI export/validate、bundle 資源皆通過；`python -m sticker_forge.cli` 補上 `__main__` guard。
- **匯出預設去背**：`export` / `stickers` / `preview` 改為預設去背（LINE 強制要求透明背景，且切圖本就用 key 色填背景配對去背）。想保留實心底色改用 `--keep-background`。
- **validate 檢查透明背景**：`validate` 新增透明度檢查，完全不透明（背景未去）的貼圖會被標記，擋下 LINE 第一大退件原因。

細節見 [`REVIEW.md`](REVIEW.md) 與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

### 🚀 v0.13.0 新增

- **動態貼圖：改用「匯入多個動態 GIF」＋GUI**。修正 v0.12.0 的輸入形狀——非專業使用者用 AI 生圖，拿到的是**每張一個動態 GIF**，不是動態 grid。現在**匯入 8／16／24 個動態 GIF/APNG（每個一張）** → 逐格去背、resize 到 ≤320×270（一邊 ≥270）、轉 **APNG（5–20 影格）**，外加動畫 main 240×240＋靜態 tab 96×74，依官方規格（[creator.line.me/en/guideline/animationsticker](https://creator.line.me/en/guideline/animationsticker/)）。GUI「匯入動態貼圖」（多檔）＋「匯出動態貼圖」按鈕（動態模式下靜態匯出會擋下）；CLI `sticker-forge animated a.gif b.gif … -o out.zip`。**16/24 靠匯入更多檔**，不需多 grid。

### 🚀 v0.12.0 新增

- **LINE 動態貼圖匯出（CLI，首版）**：依官方規格產出 APNG 動態貼圖包（≤320×270、5–20 影格、動畫 main＋靜態 tab）。（v0.13.0 把輸入改為「匯入多個動態 GIF」並加 GUI。）

### 🚀 v0.11.0 新增

- **LINE 訊息貼圖匯出**：訊息貼圖（發送者可在貼圖上打字）——**8／16／24 張、貼圖 max 370×320、不需留邊（LINE 自動加邊）、main 240×240＋tab 96×74**，依官方規格（[creator.line.me/en/guideline/messagesticker](https://creator.line.me/en/guideline/messagesticker/)）。GUI「匯出訊息貼圖」按鈕；CLI `sticker-forge message <grid…> -o out.zip`。文字位置／字型於 LINE 編輯器設定。

### 🚀 v0.10.0 新增

- **LINE 原創貼圖 emoji 匯出**：把貼圖池匯出成 LINE emoji 規格——**8–40 張、180×180 PNG 透明、檔名 `001.png…` 外加 96×74 聊天縮圖**，依官方規格（[creator.line.me/en/guideline/emoji](https://creator.line.me/en/guideline/emoji/)）實作。GUI「匯出 LINE emoji」按鈕；CLI `sticker-forge emoji <grid…> -o out.zip --thumb 1`、`validate --emoji` 檢查。

### 🚀 v0.9.0 新增

- **主題預設包**：一鍵套用「療癒白熊／上班族貓／情侶小熊／節慶祝福」等主題，自動填入角色／主題／語氣／風格與 8 句文字＋8 動作，再自行微調。GUI 下拉選單；CLI `sticker-forge prompt --preset office-cat`。
- **套組標題／作者（GUI）**：GUI 可填 LINE 套組的標題與作者，寫進 ZIP 內的 README（CLI 原本就有 `--title` / `--author`）。

### 🚀 v0.8.0 新增

- **更大的 LINE 套組（8／16／24／32／40）**：用「加入 grid」把多張 3×3 累積成更大的貼圖池，勾選要出的張數，匯出對應大小的 LINE 套組。
- **自選主圖／聊天標籤**：不再固定第 1 張，可指定哪張當 `main.png`、哪張當 `tab.png`。
- **貼圖排序**：每張可 ▲▼ 調整順序（決定 `01…NN` 的輸出順序）。
- CLI：`sticker-forge export grid1.png grid2.png -o out.zip --select 1,…,16 --main 2 --tab 3`。

### 🚀 v0.7.0 新增

- **多平台匯出**：除了 LINE，還能把貼圖匯出成 **Telegram（512 PNG）、WhatsApp（512 WebP＋96 tray）、Discord（320 PNG）、Signal（512 PNG）** 的尺寸與格式。GUI 選平台按「匯出到平台」；CLI 用 `sticker-forge platform <grid> -o out.zip --target telegram`。（靈感來自參考專案 sticker-convert、StampNyaa。）

### 🚀 v0.6.0 新增

- **單張放大檢視**：點任一張貼圖縮圖，跳出放大視窗（透明格背景），可看清去背結果。
- **單張去背／還原**：放大視窗可只對這一張去背，或還原回原始切圖；「全部去背」與單張去背都從原始切圖計算，改去背強度重跑不會疊加髒邊。

### 🚀 v0.5.0 新增

- **UI 收斂成一套**：桌面 GUI 從 tkinter 改為 **pywebview 原生視窗載入 HTML 介面**，切圖/去背/匯出/prompt 全部由本機 Python core 處理（JS 只負責畫面）。原本 tkinter GUI 與 JavaScript 各一套的重複實作收斂成單一 core，parity 問題根除。相依：pywebview（Windows 用內建 WebView2）。

### 🚀 v0.4.0 新增

- **Prompt 下拉建議**：角色／主題／語氣／風格／語言與 8 句文字、8 個動作欄位都提供下拉建議，沒靈感可直接選、也能自己打字。原生 GUI 用可編輯下拉（Combobox）、HTML 用 `datalist`，建議會隨中/英語系切換。

### 🚀 v0.3.0 新增

- **拖放匯入**：本機 HTML 工作台可直接把 3x3 圖拖放進來（原生、zero-dep，已於瀏覽器實測）。
- **Windows icon**：GUI / CLI exe 使用自製 `packaging/icon.ico`。
- **Legacy 清理**：移除 `reference/.../worker/`（Cloudflare/Gemini 後端）與 campaign-checker CI；保留 upstream UI 參考作 provenance。

### 💡 參考來源啟發的候選功能

看 fork 來源（[yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio)）與其他參考專案（sticker-convert、StampNyaa、signal-sticker-tool、LINE Creators Market）整理的候選：

- **更多平台格式**：Signal 完整 pack（含 manifest）。
- **big stickers／pop-up／effect**：LINE 其他貼圖類型，各有規格，可依需求逐一查證後加。
- **ML 去背**：非綠幕來源用 rembg 之類。**傾向不做**：首次執行需下載模型（破壞離線）＋相依重，違反 local-first 輕量原則。
- **grid 歷史**：保留匯入過的 grid 可重用。**傾向不做**：需持久儲存，與現行 `private_mode` 不寫持久資料的決策衝突。

### ⏳ 已定案

- **已決定不做**（見 [`docs/DECISIONS.md`](docs/DECISIONS.md)）：自動更新（需更新伺服器，違反 local-first）、installer（下載 zip 解壓即用，portable 比安裝流程更符合 local-first）。

## 維護文件

- [`REVIEW.md`](REVIEW.md)：最新專案 review（僅保留最新版）。
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)：架構、本機指令、打包發行、legacy 邊界。
- [`docs/DECISIONS.md`](docs/DECISIONS.md)：重要決策紀錄。
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md)：LINE Creators Market 手動上架與送審說明。
- [`NOTICE.md`](NOTICE.md)：授權、fork 來源與第三方聲明。
- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) / [`SKILL.md`](SKILL.md)：AI 接手規則與硬性邊界。

## 其他可參考專案

這些服務與專案只作概念、格式或流程參考，不是 `sticker-forge` 的執行依賴。**除了 fork 來源 `yazelin/line-sticker-studio`（MIT，程式碼在 `reference/upstream-line-sticker-studio/`）外，本專案沒有複製其中任何一個的程式碼**——GPL／無授權的專案無法併入 MIT repo，只作概念參考。完整 credit 見 [`NOTICE.md`](NOTICE.md)。

| 名稱 | 授權 | 可參考點 |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) | 官方平台 | LINE 貼圖規格、套組張數、透明背景與送審流程。 |
| [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | 官方手機 app | 手機製作與送審流程；本專案只保留手動送審說明，不代送審。 |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | MIT（**fork 來源**） | 3x3 grid、chroma-key、ZIP 結構、上架說明與 UI 流程；程式碼保留在 `reference/`。 |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | GPL-2.0 | 「一組貼圖匯出到多平台」的概念；本專案多平台匯出照公開規格自行實作。 |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | 未宣告 | 「LINE 貼圖轉用到其他平台」的桌面流程。 |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | GPL-3.0 | Signal 貼圖包打包（未來功能參考）。 |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | MIT | 從 LINE Store 下載既有貼圖（未來匯入功能參考）。 |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | WTFPL | browser / CLI 下載與 ZIP 輸出方式。 |

## 授權

本專案保留原始 fork 的 MIT License。授權與完整 attribution／credit 見 [`LICENSE`](LICENSE) 與 [`NOTICE.md`](NOTICE.md)。
