# sticker-forge

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/local--first-no_backend-brightgreen.svg)](docs/DEVELOPMENT.md)
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

- **提示詞**：依 LINE 規格產生 3x3 grid prompt，支援主題／角色／語氣／語言／8 句文字／8 個動作，有字與無字兩版，可複製微調。
- **圖片加工**：匯入 3x3 grid、切 9 格選 8 張、green/magenta chroma-key 去背、尺寸與 padding 整理、main/tab image、逐張預覽。
- **匯出**：LINE Creators Market 靜態貼圖 ZIP、9 張獨立 PNG 的一般貼圖 ZIP、尺寸／張數／檔名／結構檢查、簡短上架說明。

## 使用入口

| 入口 | 說明 |
|------|------|
| `sticker-forge.exe` | 原生 Windows GUI，無 console，雙擊即用 |
| `sticker-forge-cli.exe` / `python -m sticker_forge` | 命令列，支援 `--lang zh-Hant\|en` |
| `app/index.html` | 離線 HTML 工作台，瀏覽器直接開，ZIP 本機產生不依賴 CDN |

從原始碼安裝與打包步驟見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

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

目前版本 **v0.2.0**：local-first LINE 靜態貼圖工具，CLI + 原生 Windows GUI + 本機 HTML fallback 三條入口皆可用，`python -m pytest` 全數通過。

### ✅ 已完成

- 產品方向固定為 local-first；從 upstream 抽出可重用邏輯（切圖 inset、chroma-key、ZIP spec、LINE 尺寸）。
- prompt 模板：中英文、有字／無字、green/magenta 背景、高風險內容提醒。
- 圖片處理核心：3x3 切圖、去背、尺寸／padding、main/tab image、預覽 metadata 與選圖檢查。
- 匯出：LINE ZIP、9 張 PNG-only ZIP、`validate` 與 `preview` 指令、上架說明。
- 三入口：CLI（`--lang` 中英）、原生 tkinter GUI、離線 HTML 工作台。
- PyInstaller Windows 打包，已發行 `v0.1.0`、`v0.2.0`，含 SHA256 checksum。
- 中英文 README。

### 🔧 2026-07-07 一致性修正

- **切圖尺寸**：`split_grid` 不再要求邊長可被 3 整除，改向下取整丟餘數（對齊 web `Math.floor`），最常見的 1024×1024 AI 生圖在 CLI / GUI / web 都能處理。
- **`--key-color`**：從 `export` / `stickers` / `preview` 移除死參數（那條路徑固定走 green/magenta score-based 去背），保留在 `cleanup`。
- **web 去背 despill**：`app/app.js` 對齊 Python 的 despill，三入口去背輸出一致（60/60 像素交叉比對）。
- **打包驗證**：實測 PyInstaller build，GUI `--smoke`、CLI export/validate、bundle 資源皆通過；`python -m sticker_forge.cli` 補上 `__main__` guard。
- **匯出預設去背**：`export` / `stickers` / `preview` 改為預設去背（LINE 強制要求透明背景，且切圖本就用 key 色填背景配對去背）。想保留實心底色改用 `--keep-background`。

細節見 [`REVIEW.md`](REVIEW.md) 與 [`docs/DECISIONS.md`](docs/DECISIONS.md)。

### ⏳ 待辦

- **介面強化**：拖放匯入、單張重切與預覽縮放、Windows icon / installer / 自動更新檢查。
- **使用者資料位置**：決定使用者資料與暫存檔存放位置。
- **Legacy 清理**：移除不再需要的 `reference/.../worker/` 與 upstream hosted 設定。

## 維護文件

- [`REVIEW.md`](REVIEW.md)：最新專案 review（僅保留最新版）。
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)：架構、本機指令、打包發行、legacy 邊界。
- [`docs/DECISIONS.md`](docs/DECISIONS.md)：重要決策紀錄。
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md)：LINE Creators Market 手動上架與送審說明。
- [`NOTICE.md`](NOTICE.md)：授權、fork 來源與第三方聲明。
- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md) / [`SKILL.md`](SKILL.md)：AI 接手規則與硬性邊界。

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
