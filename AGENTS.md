# AGENTS.md

給 Codex 與其他 AI coding agents 在本專案工作時的指引。

## 專案宗旨

`sticker-forge` 是 local-first 的聊天貼圖包製作工具，支援 LINE 靜態貼圖、Big Stickers、emoji、訊息貼圖、動態貼圖、pop-up、effect 與多平台尺寸匯出。已以 Windows `.exe` 發行（onedir，解壓即用）。

核心流程：

1. 程式提供提示詞模板。
2. 使用者自行到 ChatGPT / Gemini / 其他生圖工具產生 3x3 貼圖 grid 或多個動態 GIF/APNG。
3. 使用者把生成圖匯回本機程式。
4. 程式在本機切圖、去背、整理尺寸、預覽、匯出 LINE 或其他平台貼圖 ZIP。

本專案不打算架 server、不代管 AI API、不處理使用者圖片上傳服務。

## 硬性邊界

- 不新增 hosted backend、Cloudflare Worker 服務、Turnstile quota 或集中式 Gemini proxy。
- 不提交 API key、token、`.dev.vars`、使用者圖片、生成 ZIP 或本機暫存資料。
- 不宣稱本工具為 LINE 官方、LINE 認證或保證上架通過。
- 不移除 MIT 授權與原作者 `yazelin` attribution；見 `NOTICE.md`。
- 不鼓勵生成侵害 IP、商標、真人肖像、政治人物、色情、仇恨、暴力、詐騙、個資等高風險內容。
- 不做 LINE Creators Market 自動上架或送審自動化。

## 目前狀態

本 repo 已移除 upstream web app / Worker 的 vendored reference source。保留 `yazelin/line-sticker-studio` 的 MIT attribution 與歷史決策紀錄，但後續不再依賴 repo 內的 upstream reference 目錄。

目前結構：

- `src/sticker_forge/`：本機工具主程式（`spec` / `prompts` / `splitter` / `cleanup` / `decorate` / `exporter` / `preview` / `cli` / `webapi` / `gui`）。
- `prompts/`：提示詞模板。
- `packaging/`：exe 打包與發行流程。
- `tests/`：切圖、去背、ZIP 檢查等測試。
- `examples/`：範例說明，不放侵權素材。
- `app/`：pywebview GUI 載入的 HTML/CSS/JS，純畫面，透過 bridge 呼叫 Python。
- `tools/`：維護腳本（依賴 freshness、Dependabot 分類、上游 commit 檢查）。
- `docs/`：使用、開發、Windows 驗收、決策與 LINE 送審文件。

## 開發原則

- 先把產品路線改清楚，再搬功能。
- 優先保留可本地化的能力：prompt、切圖、去背、尺寸整理、ZIP 匯出。
- Worker、quota、Turnstile、線上 API proxy 只作為歷史背景，不要當成新架構延伸。
- 若選技術棧，優先考慮易打包 Windows exe 的方案。
- 新增圖片處理邏輯時要補測試。
- 使用繁體中文回覆與撰寫維護文件；程式命名維持英文。

## 驗證方向

本機工具已建立（CLI + pywebview 桌面 GUI，共用同一套 Python core + PyInstaller 打包）。改動後至少確認：

```powershell
git diff --check
python -m pytest
```

最小涵蓋：prompt CLI 輸出與渲染、3x3 切圖（含非整除尺寸）、green/magenta 去背（含 strict／continuous、erode、自訂 profile）、白色描邊／陰影、ZIP 結構與 validator、`webapi` bridge、維護 workflow 契約、exe smoke test。

上游 `yazelin/line-sticker-studio` 與本 repo **沒有共同 git history**，永遠不能直接 merge；只移植概念與修正。triage 後要更新 `tools/upstream_baseline.json` 並把結論寫進 `docs/DECISIONS.md`。

## 文件入口

- `README.md` / `README.en.md`：使用者入口、產品方向與簡化路線圖。
- `docs/USER_GUIDE.md`：一般使用者指南（安裝、各類型匯出、常見問題）。
- `CHANGELOG.md`：版本變更紀錄。
- `REVIEW.md`：最新專案 review。**修 bug 必回註（適用所有 AI agent：Claude、Codex 等，維護者 2026-07-19 指示）**：每修復 REVIEW.md 列出的問題，須回到對應項目標註修復 commit hash 與日期；修復過程中額外發現並修掉的 bug 也要補註。REVIEW 維持 latest-only，但修復狀態必須跟上現況。
- `docs/DEVELOPMENT.md`：架構、本機指令、打包發行、legacy 邊界。
- `docs/WINDOWS_VALIDATION.md`：Windows Release、Computer Use GUI 與 LINE 平台驗收。
- `docs/DECISIONS.md`：決策紀錄。
- `docs/LINE_SUBMISSION.md`：LINE 手動上架與送審說明。
- `NOTICE.md`：fork 來源、MIT 授權與第三方聲明。
