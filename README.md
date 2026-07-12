# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
[![LINE sticker packs](https://img.shields.io/badge/LINE-sticker_packs-00B900.svg)](prompts/line-static-3x3.md)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-blueviolet.svg)](tests)

[繁體中文](README.md) | [English](README.en.md)

Local-first toolkit for making chat sticker packs: prompt templates, image cleanup, slicing, and export for LINE, Telegram, WhatsApp, Discord and Signal.

`sticker-forge` 是本機優先的貼圖包製作工具。支援 LINE 靜態貼圖、emoji、訊息貼圖、動態貼圖，也能一鍵匯出成 Telegram、WhatsApp、Discord、Signal 的尺寸與格式。它不架 AI server、不代管 API key，也不收集使用者圖片；使用者自行用 ChatGPT、Gemini 或其他生圖工具產圖，再把圖片匯回本機程式加工與匯出。

## 目標流程

1. 在 `sticker-forge` 選擇貼圖主題、語氣、角色設定、文字與輸出規格。
2. 程式產生可複製的提示詞。
3. 使用者自行到外部 AI 生圖工具產生 3x3 貼圖 grid，或為動態貼圖產生多個 GIF/APNG。
4. 使用者把生成好的圖片匯回 `sticker-forge`。
5. 程式在本機切圖、去背、整理尺寸、預覽。
6. 程式匯出符合 LINE Creators Market 或其他平台規格的 ZIP。

目前範圍涵蓋 LINE 靜態貼圖、emoji、訊息貼圖、動態貼圖與多平台尺寸匯出。不做 LINE 自動上架，也不保證審核通過。

## 產品原則

- 本機處理：不新增 hosted backend。
- 使用者自備 AI：不集中管理 ChatGPT / Gemini / 其他生圖服務的帳號或 API key。
- 隱私優先：不收集、上傳或保存使用者圖片。
- 可下載發行：長期目標是 Windows `.exe`。
- 上架保守：提示詞與檢查流程要提醒使用者避開侵權、商標、真人肖像、政治、色情、暴力、仇恨、個資等高風險內容。

## 功能範圍

- **提示詞**：依 LINE 規格產生 3x3 grid prompt，支援主題／角色／語氣／語言／8 句文字／8 個動作，有字與無字兩版，可複製微調。
- **圖片加工**：匯入 3x3 grid 或多個動態 GIF/APNG、切圖、選圖、排序、green/magenta chroma-key 去背、尺寸與 padding 整理、main/tab image、逐張預覽。
- **匯出**：LINE 靜態貼圖、emoji、訊息貼圖、動態貼圖 ZIP，9 張獨立 PNG 的一般貼圖 ZIP，多平台尺寸 ZIP，尺寸／張數／檔名／結構檢查、簡短上架說明。

## 使用入口

| 入口 | 說明 |
|------|------|
| `sticker-forge.exe` | 桌面 GUI：pywebview 原生視窗載入 `app/` 的 HTML 介面，切圖/去背/匯出全由本機 Python core 處理，無 console，雙擊即用 |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | 命令列，支援 `--lang zh-Hant\|en` |

GUI 與 CLI 共用同一套 Python core（`app/` 只負責畫面，透過 bridge 呼叫 Python）。一般使用流程見 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)，從原始碼安裝與打包步驟見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 目前狀態

本 repo 來自 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 的 MIT fork。原專案 web app / Worker 的 vendored reference source 已移除；後續維護以本 repo 的 Python core、pywebview GUI、文件決策與 git history 為準。

## 專案結構

```text
.
├── src/sticker_forge/      # 本機工具主程式
├── app/                    # pywebview GUI 載入的 HTML/CSS/JS 前端資源
├── prompts/                # 提示詞模板
├── packaging/              # exe 打包設定與發行流程
├── tests/                  # 自動化測試
├── examples/               # 範例輸入位置，不放侵權素材
├── docs/                   # 使用與維護文件（USER_GUIDE / DEVELOPMENT / DECISIONS / LINE_SUBMISSION）
├── README.md / README.en.md / CHANGELOG.md / REVIEW.md
├── AGENTS.md / CLAUDE.md / SKILL.md          # AI 接手指引
└── NOTICE.md / LICENSE
```

## 專案狀態與路線圖

目前版本 **v0.15.0**：local-first 貼圖包工具（LINE 貼圖／emoji／訊息貼圖／動態貼圖 及多平台），桌面 GUI（pywebview 載入 HTML）與 CLI 共用同一套 Python core，`python -m pytest` 全數通過。

### ✅ 已完成

- 產品方向固定為 local-first；已把需要的 fork 來源概念收斂成本機 Python core、pywebview GUI 與規格文件。
- prompt 模板：中英文、有字／無字、green/magenta 背景、高風險內容提醒。
- 圖片處理核心：3x3 切圖、去背、尺寸／padding、main/tab image、預覽 metadata 與選圖檢查。
- 匯出：LINE 靜態貼圖／emoji／訊息貼圖／動態貼圖 ZIP、9 張 PNG-only ZIP、多平台 ZIP、`validate` 與 `preview` 指令、上架說明。
- 桌面 GUI（pywebview HTML）與 CLI 共用 Python core（`--lang` 中英）。
- PyInstaller Windows 打包與發行，已發行到 `v0.15.0`（正式 GitHub Release，含 SHA256 checksum）。
- 桌面拖放匯入（webview 的 HTML dropzone 內建）；WebView2 用 `private_mode` 臨時 profile，不寫持久隱藏資料。
- 中英文 README。
- 使用者指南與本機範例素材產生器（不提交生成圖片或 ZIP）。
- Signal 多平台匯出已補 `cover.png`、`signal_manifest.json` 與 `validate --signal` 檢查。

詳細版本紀錄見 [`CHANGELOG.md`](CHANGELOG.md)；設計決策見 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

### 下一步

- 用非侵權素材做一次 LINE Creators Market 手動上傳抽驗，特別是動態貼圖 APNG。
- 逐一查證 LINE big stickers／pop-up／effect stickers 規格，再決定是否加入。

### ⏳ 已定案

- **已決定不做**（見 [`docs/DECISIONS.md`](docs/DECISIONS.md)）：自動更新（需更新伺服器，違反 local-first）、installer（下載 zip 解壓即用，portable 比安裝流程更符合 local-first）。

## 維護文件

- [`REVIEW.md`](REVIEW.md)：最新專案 review（僅保留最新版）。
- [`CHANGELOG.md`](CHANGELOG.md)：版本變更紀錄。
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)：一般使用者指南。
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)：架構、本機指令、打包發行、legacy 邊界。
- [`docs/DECISIONS.md`](docs/DECISIONS.md)：重要決策紀錄。
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md)：LINE Creators Market 手動上架與送審說明。
- [`NOTICE.md`](NOTICE.md)：授權、fork 來源與第三方聲明。
- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) / [`SKILL.md`](SKILL.md)：AI 接手規則與硬性邊界。

## 其他可參考專案

這些服務與專案只作概念、格式或流程參考，不是 `sticker-forge` 的執行依賴。fork 來源 `yazelin/line-sticker-studio` 以 MIT attribution、外部連結與 git history 保留來源脈絡；本 repo 不再保留 upstream vendored source。GPL／無授權的專案無法併入 MIT repo，只作概念參考。完整 credit 見 [`NOTICE.md`](NOTICE.md)。

| 名稱 | 授權 | 可參考點 |
| --- | --- | --- |
| [LINE Creators Market](https://creator.line.me/) | 官方平台 | LINE 貼圖規格、套組張數、透明背景與送審流程。 |
| [LINE Sticker Maker](https://creator.line.me/en/stickermaker/) | 官方手機 app | 手機製作與送審流程；本專案只保留手動送審說明，不代送審。 |
| [Signal Stickers Support](https://support.signal.org/hc/en-us/articles/360031836512-Stickers) | 官方支援文件 | Signal 貼圖尺寸、格式、封面、title、author 與 emoji 指派需求。 |
| [yazelin/line-sticker-studio](https://github.com/yazelin/line-sticker-studio) | MIT（**fork 來源**） | 3x3 grid、chroma-key、ZIP 結構、上架說明與 UI 流程；來源脈絡保留於 attribution 與 git history，不再 vendored。 |
| [laggykiller/sticker-convert](https://github.com/laggykiller/sticker-convert) | GPL-2.0 | 「一組貼圖匯出到多平台」的概念；本專案多平台匯出照公開規格自行實作。 |
| [MarvNC/StampNyaa](https://github.com/MarvNC/StampNyaa) | 未宣告 | 「LINE 貼圖轉用到其他平台」的桌面流程。 |
| [ittner/signal-sticker-tool](https://github.com/ittner/signal-sticker-tool) | GPL-3.0 | Signal 貼圖包打包（未來功能參考）。 |
| [suchipi/line-sticker-downloader](https://github.com/suchipi/line-sticker-downloader) | MIT | 從 LINE Store 下載既有貼圖（未來匯入功能參考）。 |
| [curegit/line-sticker-downloader](https://github.com/curegit/line-sticker-downloader) | WTFPL | browser / CLI 下載與 ZIP 輸出方式。 |

## 授權

本專案保留原始 fork 的 MIT License。授權與完整 attribution／credit 見 [`LICENSE`](LICENSE) 與 [`NOTICE.md`](NOTICE.md)。
