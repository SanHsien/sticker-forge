---
name: sticker-forge
description: 維護 SanHsien/sticker-forge。本專案目標是本機 LINE 貼圖製作工具：產生提示詞，讓使用者自行生圖，再匯回程式做切圖、去背、尺寸整理與 ZIP 匯出；不架 server、不代管 AI API，長期以 Windows exe 發行。
---

# sticker-forge

## 何時使用

使用者要維護 `SanHsien/sticker-forge`，或開發本機 LINE 貼圖製作流程：

- 產生給 ChatGPT / Gemini / 其他工具使用的貼圖 prompt。
- 匯入使用者生成的 3x3 grid。
- 切圖、挑選 8 張、去背、尺寸整理。
- 匯出 LINE Creators Market 靜態貼圖 ZIP。
- 建立 Windows exe 打包流程。

## 不適用

- 架 Cloudflare Worker、Turnstile、quota、Gemini proxy 或任何 hosted backend。
- 代管使用者圖片或 API key。
- 自動送審 LINE Creators Market。
- 宣稱官方背書或保證上架通過。
- 鼓勵侵權 IP、商標、真人肖像、政治、色情、仇恨、暴力、個資等高風險內容。

## 快速定位

- `README.md`：產品方向。
- `NOTICE.md`：fork 來源與授權聲明。
- `AGENTS.md` / `CLAUDE.md`：AI 接手規則。
- `src/sticker_forge/`：未來本機工具主程式。
- `prompts/`：提示詞模板。
- `packaging/`：exe 打包流程。
- `tests/`：測試。
- `docs/HANDOFF.md`：目前接手狀態。
- `reference/upstream-line-sticker-studio/`：upstream legacy，保留目錄結構作參考。

## 完成回報

回報時列出：

- 修改了哪些檔案。
- 是否改到產品方向、prompt、圖片處理、ZIP 規格或打包流程。
- 執行過哪些驗證。
- 是否仍引用 legacy web/worker 內容。
