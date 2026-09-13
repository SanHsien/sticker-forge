# Sticker Forge

[![Release](https://img.shields.io/github/v/release/SanHsien/sticker-forge?sort=semver)](https://github.com/SanHsien/sticker-forge/releases/latest)
[![CI](https://github.com/SanHsien/sticker-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/SanHsien/sticker-forge/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Local-first](https://img.shields.io/badge/architecture-local--first-2E7D32.svg)](#隱私與產品邊界)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**把 AI 產出的角色圖，整理成可交付的聊天貼圖包。**

繁體中文 · [English](README.en.md)

Sticker Forge 是 Windows 優先、本機處理的貼圖製作工具。它不替你經營 AI 帳號，也不把圖片送到自己的伺服器；你可以用 ChatGPT、Gemini 或其他生圖工具產圖，再把結果匯回 Sticker Forge，完成切圖、去背、描邊、尺寸整理、預覽與多平台匯出。

## 快速開始

1. 從 [Latest Release](https://github.com/SanHsien/sticker-forge/releases/latest) 下載 Windows ZIP。
2. 解壓後執行 `sticker-forge.exe`。
3. 在 GUI 建立提示詞，或直接匯入已生成的圖片／GIF／APNG。
4. 本機完成切圖、去背、排序、後製與格式檢查。
5. 匯出 LINE 或其他聊天平台需要的 ZIP／圖片檔。

不需要安裝服務端，也不需要把 AI API key 交給 Sticker Forge。

## 核心流程

```text
主題 / 角色 / 文案
        │
        ▼
 Sticker Forge 產生 prompt
        │
        ▼
使用者自行選擇 AI 生圖工具
        │
        ▼
匯回 grid / PNG / GIF / APNG
        │
        ▼
切圖 → 去背 → 描邊 → 排序 → 預覽 → 驗證
        │
        ▼
LINE / Telegram / WhatsApp / Discord / Signal
```

這個分工刻意把「生成圖片」和「整理可交付資產」拆開：Sticker Forge 專注在後者，因此沒有 hosted AI backend、共享 quota 或集中式金鑰管理。

## 能做什麼

- **提示詞產生**：依角色、主題、語氣、語言、文字與動作產生可複製的貼圖 prompt，支援有字／無字版本。
- **3×3 grid 切圖**：把常見 AI 貼圖九宮格拆成獨立素材，處理非整除尺寸並支援選圖與排序。
- **去背與邊緣修整**：green / magenta chroma key、`safe` / `balanced` / `aggressive` / `continuous` 模式，以及 GUI 進階參數。
- **描邊與陰影**：`simple` 白邊或 `fancy` 白邊＋羽化＋陰影，改善深色聊天背景上的辨識度。
- **LINE 匯出**：靜態貼圖、Big Stickers、emoji、訊息貼圖、動態貼圖、pop-up stickers、effect stickers。
- **多平台匯出**：Telegram、WhatsApp、Discord、Signal 的尺寸與檔案結構。
- **驗證與預覽**：檢查尺寸、張數、命名與 ZIP 結構，並提供 main / tab image 與逐張預覽資料。
- **GUI + CLI**：桌面 GUI 與 `python -m sticker_forge` / `sticker-forge` 共用同一套 Python core。

## 隱私與產品邊界

Sticker Forge 的圖片處理與匯出在本機執行：

- 不架設 Sticker Forge 圖片上傳服務。
- 不代管 ChatGPT、Gemini 或其他 AI 服務的 API key。
- 不把使用者圖片、生成 ZIP 或本機暫存資料提交到本專案。
- 使用哪個 AI 生圖服務由使用者自行決定；當你把內容交給第三方 AI 服務時，資料處理由該服務自己的政策決定。
- 不自動上傳或送審 LINE Creators Market。

本工具不是 LINE 官方產品，也不保證任何貼圖一定通過平台審核。商標、著作權、真人肖像與其他內容權利仍由使用者自行確認。

## LINE 與多平台支援

| 類型 | 支援 |
|---|---|
| LINE 靜態貼圖 | ✅ |
| LINE Big Stickers | ✅ |
| LINE emoji | ✅ |
| LINE 訊息貼圖 | ✅ |
| LINE 動態貼圖 | ✅ |
| LINE pop-up / effect | ✅ |
| Telegram / WhatsApp / Discord / Signal | ✅ |

本機 validator 能檢查已知規格，但不能取代 LINE Creators Market 的實際平台判定。送審流程與手動抽驗見 [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md) 與 [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md)。

## 從原始碼執行

需求：Python 3.11+

```powershell
python -m pip install -e ".[dev,gui]"
python -m sticker_forge
python -m pytest
```

Windows 發行版由 PyInstaller 建置；CI 同時測試 Python 3.11–3.14，並在 Windows runner 實際建置與 smoke-test EXE。

開發、打包與架構細節見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 文件

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)：一般操作、各類匯出與常見問題。
- [`docs/LINE_SUBMISSION.md`](docs/LINE_SUBMISSION.md)：LINE Creators Market 手動送審流程。
- [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md)：Windows GUI、Release 與平台抽驗。
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)：架構、測試與打包。
- [`docs/DECISIONS.md`](docs/DECISIONS.md)：重要產品與工程取捨。
- [`CHANGELOG.md`](CHANGELOG.md)：版本變更。

## 專案來源與授權

本 repo 是 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 的 MIT fork。原專案以「單張圖片 → AI 生成 LINE 貼圖」為起點；本 fork 已轉向 Windows local-first 的 Python / pywebview 工具，並移除原本 web app / Worker 的 vendored reference source。

上游 attribution、修改脈絡與第三方聲明見 [`NOTICE.md`](NOTICE.md)。本專案依 [MIT License](LICENSE) 發布。
