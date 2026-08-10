---
name: sticker-forge
description: 維護 SanHsien/sticker-forge。本專案目標是本機聊天貼圖包製作工具：產生提示詞，讓使用者自行生圖或動態 GIF/APNG，再匯回程式做切圖、去背、尺寸整理與 ZIP 匯出；不架 server、不代管 AI API，長期以 Windows exe 發行。
---

# sticker-forge

## 何時使用

使用者要維護 `SanHsien/sticker-forge`，或開發本機貼圖包製作流程：

- 產生給 ChatGPT / Gemini / 其他工具使用的貼圖 prompt。
- 匯入使用者生成的 3x3 grid 或多個動態 GIF/APNG。
- 切圖、選圖／排序、去背（strict／continuous、邊緣侵蝕、自訂 profile）、白色描邊／陰影、尺寸整理。
- 匯出 LINE 靜態貼圖、Big Stickers、emoji、訊息貼圖、動態貼圖、pop-up、
  effect 或多平台 ZIP。
- 建立 Windows exe 打包流程。

## 不適用

- 架 Cloudflare Worker、Turnstile、quota、Gemini proxy 或任何 hosted backend。
- 代管使用者圖片或 API key。
- 自動送審 LINE Creators Market。
- 宣稱官方背書或保證上架通過。
- 鼓勵侵權 IP、商標、真人肖像、政治、色情、仇恨、暴力、個資等高風險內容。

## 快速定位

- `README.md` / `README.en.md`：產品方向與簡化路線圖。
- `CHANGELOG.md`：版本變更紀錄。
- `REVIEW.md`：最新專案 review。
- `NOTICE.md`：fork 來源與授權聲明。
- `AGENTS.md` / `CLAUDE.md`：AI 接手規則。
- `src/sticker_forge/`：本機工具主程式。
- `tools/`：維護腳本（依賴 freshness、Dependabot 分類、上游 commit 檢查）。
- `prompts/`：提示詞模板。
- `docs/DEVELOPMENT.md`：架構、本機指令、打包發行。
- `docs/WINDOWS_VALIDATION.md`：Windows Release、Computer Use GUI 與 LINE 平台驗收。
- `docs/DECISIONS.md`：決策紀錄。
- `docs/USER_GUIDE.md`：一般使用者指南。
- `docs/LINE_SUBMISSION.md`：LINE 手動上架與送審說明。
- `app/`：pywebview 載入的本機 HTML GUI。
- `packaging/`：PyInstaller 打包與 release 腳本。

## 完成回報

回報時列出：

- 修改了哪些檔案。
- 是否改到產品方向、prompt、圖片處理、ZIP 規格或打包流程。
- 執行過哪些驗證。
- 是否仍引用 legacy web/worker 內容或已重新引入 hosted backend 方向。
