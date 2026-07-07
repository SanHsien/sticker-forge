# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/ARCHITECTURE.md)
[![LINE static stickers](https://img.shields.io/badge/LINE-static_stickers-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | [English](README.en.md)

Local toolkit for preparing LINE sticker packs: prompt templates, image cleanup, slicing, and export.

`sticker-forge` 是本機優先的 LINE 靜態貼圖包製作工具。它不架 AI server、不代管 API key，也不收集使用者圖片；使用者自行用 ChatGPT、Gemini 或其他生圖工具產圖，再把圖片匯回本機程式加工與匯出。

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

### 提示詞

- 依 LINE 貼圖規格產生 3x3 grid prompt。
- 支援主題、角色設定、語氣、語言、貼圖文字、動作描述。
- 支援「有字 / 無字」兩種提示詞。
- 提供可複製、可手動微調的 prompt。

### 圖片加工

- 匯入使用者生成的 3x3 grid。
- 切成 9 格，讓使用者選出 LINE 最小套組需要的 8 張。
- chroma-key 去背或其他背景清理。
- 尺寸整理、padding、main image、tab image。
- 預覽每張貼圖。

### 匯出

- 匯出 LINE Creators Market 靜態貼圖 ZIP。
- 匯出 9 張獨立 PNG 的一般貼圖 ZIP。
- 檢查基本尺寸、張數、檔名與 ZIP 結構。
- 產生簡短上架說明。

## 目前狀態

本 repo 來自 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 的 MIT fork。原專案 web app 與 Worker 已集中搬到 `reference/upstream-line-sticker-studio/`，作為邏輯參考，不是新架構。

目前已完成：

- 建立 local-first 方向文件。
- 建立 AI 接手文件：`AGENTS.md`、`CLAUDE.md`、`SKILL.md`。
- 建立授權與第三方聲明：`NOTICE.md`。
- 建立後續目錄骨架：`src/`、`prompts/`、`packaging/`、`tests/`、`examples/`、`docs/`。
- 建立第一版 LINE 靜態貼圖 3x3 prompt：`prompts/line-static-3x3.md`。
- 建立 Python package 設定：`pyproject.toml`。
- 建立最小 CLI：`python -m sticker_forge prompt|split|cleanup|export|stickers|validate|app`。
- 建立本機 HTML 介面原型：`app/index.html`，可離線匯出 ZIP。
- 建立 `sticker-forge app` 指令，可從 CLI / exe 開啟本機 HTML 介面。
- 建立原生 Windows GUI 入口：雙擊 `sticker-forge.exe` 直接開啟圖形介面，不再閃 console 視窗。
- 建立 `sticker-forge-cli.exe` 作為命令列入口。
- 建立 CLI / HTML 工作台中英文語系切換。
- 建立英文 README：`README.en.md`。
- 建立 prompt 欄位渲染、3x3 grid inset 切圖、chroma-key 去背、LINE ZIP exporter、PNG-only stickers ZIP exporter 與 ZIP validator。
- 建立預覽資料模型：`src/sticker_forge/preview.py`。
- 保留 upstream 的 LINE Creators Market 手動上架/送審說明：`docs/LINE_SUBMISSION.md`。
- 建立 PyInstaller Windows 打包腳本與 spec。
- 建立 pytest 測試，覆蓋 prompt CLI、prompt 渲染、切圖、去背、ZIP 結構與 ZIP validator。
- 關閉 GitHub Issues、Projects、Wiki、Discussions、Actions。

目前尚未完成：

- 原生 GUI 還是首版，後續可強化拖放、更多預覽細節與 icon / installer。

## 專案結構

```text
.
├── src/sticker_forge/      # 本機工具主程式
├── app/                    # 可直接開啟的本機 HTML 介面
├── prompts/                # 提示詞模板與範例
├── packaging/              # exe 打包設定與發行流程
├── tests/                  # 自動化測試
├── examples/               # 範例輸入/輸出說明，不放侵權素材
├── docs/                   # 維護文件與 review
├── reference/
│   └── upstream-line-sticker-studio/
│       ├── app.js          # 原專案 web frontend 參考
│       ├── index.html      # 原專案 web frontend 參考
│       ├── styles.css      # 原專案 web frontend 參考
│       ├── worker/         # 原專案 Cloudflare Worker 參考
│       ├── assets/         # 原專案素材
│       └── scripts/        # 原專案檢查腳本
├── AGENTS.md
├── CLAUDE.md
├── NOTICE.md
├── SKILL.md
└── LICENSE
```

## 改作路線圖

目前進度：**Phase 0–6 已完成可發佈流程；`v0.2.0` 修正 Windows exe 啟動方式並加入原生 GUI。**

### ✅ 已完成

- [x] **Phase 0：收斂專案邊界**
  - [x] 維持 local-first，不再延伸 Worker / quota / Turnstile / AI proxy。
  - [x] 從 reference 中抽出可重用邏輯：grid split、chroma-key、ZIP spec、LINE 尺寸。
  - [x] 清楚分離使用者文件、維護文件與原專案參考資料。

- [x] **Phase 1：提示詞模板**
  - [x] `prompts/line-static-3x3.md` 提供第一版 LINE 靜態貼圖 prompt。
  - [x] `prompts/line-static-3x3.en.md` 提供英文 prompt template。
  - [x] 支援角色、主題、語氣、語言、8 句貼圖文字、8 個動作描述與 chroma-key 背景。
  - [x] 提供有字版、無字版、3x3 grid 輸出規則。
  - [x] 加入上架風險提醒與禁止事項。

- [x] **Phase 2：圖片處理核心**
  - [x] `src/sticker_forge/` 已建立可測試模組。
  - [x] `splitter.py` 已實作 3x3 grid 匯入、3% inset 切圖與 LINE 尺寸輸出。
  - [x] CLI export 已支援 9 選 8。
  - [x] `cleanup.py` 已實作 green / magenta chroma-key 去背。
  - [x] `exporter.py` 已實作透明 padding 與尺寸輸出。
  - [x] `preview.py` 已建立貼圖預覽 metadata 與選圖檢查。
  - [x] `tests/` 已覆蓋切圖、去背與輸出。

- [x] **Phase 3：LINE ZIP exporter**
  - [x] `exporter.py` 已產生 8 張 sticker image。
  - [x] 已產生 main image 與 tab image。
  - [x] 已檢查 LINE 靜態貼圖包的張數、檔名與 ZIP 結構。
  - [x] 已匯出 ZIP 與簡短上架說明。
  - [x] 已支援 9 張 PNG-only ZIP，供非 LINE 上架用途使用。
  - [x] 已提供 `validate` 指令檢查 ZIP。
  - [x] 已保留手動上架與送審說明。

- [x] **Phase 4：本機介面**
  - [x] 已建立最小 CLI。
  - [x] CLI 流程包含：產 prompt、匯入 grid、切圖、去背、選 8 張、匯出 LINE ZIP、匯出 9 張 PNG-only ZIP、驗證 ZIP。
  - [x] CLI 支援 `--lang zh-Hant|en`，可切換中文 / 英文 help、prompt 與狀態輸出。
  - [x] `app/index.html` 提供本機 HTML 工作台，作為 exe GUI 前的可用介面。
  - [x] HTML 工作台支援繁體中文 / English 語系切換。
  - [x] HTML 工作台可離線匯出 ZIP，不依賴 CDN。
  - [x] HTML 工作台支援匯出前預覽、padding 與去背強度控制。
  - [x] 所有圖片處理都在本機完成。

- [x] **Phase 5：Windows exe 打包基礎**
  - [x] `packaging/` 已建立 PyInstaller 打包設定。
  - [x] 已建立 Windows build script。
  - [x] 已補 release checklist 與 smoke test。
  - [x] `sticker-forge app` 可從 CLI / exe 開啟本機 HTML 介面。
  - [x] 已本機驗證 `sticker-forge.exe --smoke`、`sticker-forge-cli.exe --help` 與 `prompt --output`。
  - [x] 主程式 `sticker-forge.exe` 改為無 console 原生 GUI。
  - [x] 命令列工具分離為 `sticker-forge-cli.exe`。

- [x] **正式 Windows release artifact**
  - [x] 第一版版本號固定為 `v0.1.0`。
  - [x] 第二版版本號固定為 `v0.2.0`。
  - [x] 產生可發佈的 Windows zip artifact。
  - [x] release 檔名：`sticker-forge-v0.2.0-windows-x64.zip`。
  - [x] 發佈 SHA256 checksum。
  - [x] 發行前確認沒有 API key、使用者圖片、生成 ZIP 或本機暫存檔進版控。

- [x] **英文文件**
  - [x] 建立 `README.en.md`。
  - [x] 中文 README 與英文 README 都寫明打包方式與 roadmap 狀態。

- [x] **Phase 6：原生 GUI 與 exe 啟動修正**
  - [x] 新增 `src/sticker_forge/gui.py`，使用 tkinter 提供原生圖形介面。
  - [x] GUI 支援 prompt、3x3 匯入、切圖、去背、選 8 張、padding、匯出 LINE ZIP 與 9 張 PNG ZIP。
  - [x] GUI 支援繁體中文 / English。
  - [x] 新增 `preview` CLI 指令，可檢查匯出前檔名、尺寸、選取狀態。
  - [x] PyInstaller 產出 GUI exe 與 CLI exe，修正雙擊主 exe 閃退問題。

### ⏳ 待完成

- [ ] **介面強化**
  - [ ] 補拖放匯入。
  - [ ] 補更細的預覽縮放與單張重切控制。
  - [ ] 補 Windows icon、installer 與自動更新檢查。

## 維護文件

- [`REVIEW.md`](REVIEW.md)：最新專案 review（僅保留最新版）。
- [`docs/ROADMAP.md`](docs/ROADMAP.md)：內部 roadmap。
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)：目標架構。
- [`docs/HANDOFF.md`](docs/HANDOFF.md)：接手狀態。
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md)：LINE Creators Market 手動上架與送審說明。
- [`NOTICE.md`](NOTICE.md)：授權、fork 來源與第三方聲明。

## 其他可參考專案

這些服務與專案只作產品、格式、打包或 UI 流程參考，不是 `sticker-forge` 的執行依賴。

| 名稱 | 類型 | 可參考點 |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) | 官方平台 | LINE 官方的貼圖、表情貼與主題建立/販售入口。 |
| [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | 官方手機 app | 可在手機製作貼圖並送審；本專案保留手動送審說明，但不代送審。 |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | upstream fork 來源 | 3x3 grid、chroma-key、ZIP 結構、上架說明與 UI 流程的主要參考來源。 |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | 跨平台貼圖轉換工具 | GUI + CLI、跨平台打包與貼圖格式轉換；LINE 目前以下載支援為主。 |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | LINE 素材下載工具 | 從 LINE Store 下載 stickers / emojis 的 CLI 流程與檔案輸出方式。 |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | LINE 素材下載工具 | PHP browser / CLI 雙模式與 ZIP 輸出方式。 |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | LINE 貼圖桌面工具 | 跨平台桌面 app 介面與「下載後轉用到其他平台」流程。 |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | Signal 貼圖 CLI | 以資料夾、metadata 與命令列包裝貼圖包的設計可作 CLI 架構參考。 |

## 授權

本專案保留原始 fork 的 MIT License。授權與 attribution 見 [`LICENSE`](LICENSE) 與 [`NOTICE.md`](NOTICE.md)。
