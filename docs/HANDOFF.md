# Handoff

最後更新：2026-07-06

## 目前方向

`sticker-forge` 要改成 local-first 的 LINE 貼圖製作工具。

使用者不想自行架 server，也不想代管 AI 生成服務。工具應提供 prompt，讓使用者自行到 ChatGPT / Gemini / 其他生圖工具產圖，再把圖片匯回本機程式處理。

長期交付形式以 Windows `.exe` 為主。

## 已完成

- 新增 `NOTICE.md`。
- 新增 `AGENTS.md`、`CLAUDE.md`、`SKILL.md`。
- 新增 `docs/` 維護文件。
- 新增 `pyproject.toml`。
- 新增後續資料夾骨架：
  - `src/sticker_forge/`
  - `app/`
  - `prompts/`
  - `packaging/`
  - `tests/`
  - `examples/`
- 改寫 `README.md`，移除原本「架 AI server」的產品敘事。
- 新增 `prompts/line-static-3x3.md`，提供有字版與無字版 prompt。
- 新增 `prompts/line-static-3x3.en.md`，提供英文有字版與無字版 prompt。
- 新增 `src/sticker_forge/prompts.py`，可渲染 prompt 欄位。
- 新增 `src/sticker_forge/spec.py`，集中 LINE 尺寸與 chroma-key 規格。
- 新增 `src/sticker_forge/splitter.py`，可切 3x3 grid，支援 upstream 3% inset。
- 新增 `src/sticker_forge/cleanup.py`，可 green / magenta chroma-key 去背。
- 新增 `src/sticker_forge/exporter.py`，可匯出 8 張 sticker、main image、tab image 與 README 的 LINE ZIP，可匯出 9 張 PNG-only ZIP，並驗證 LINE ZIP。
- 新增 `src/sticker_forge/preview.py`，提供貼圖預覽 metadata 與選圖檢查。
- 新增 `src/sticker_forge/cli.py`，支援 `prompt`、`split`、`cleanup`、`export`、`stickers`、`validate`、`app`。
- CLI 支援 `--lang zh-Hant|en`，可切換中文 / 英文 help、prompt 與狀態輸出。
- CLI 新增 `preview` 指令。
- 新增 `src/sticker_forge/gui.py`，提供原生 tkinter GUI。
- PyInstaller 目前產出兩個 exe：`sticker-forge.exe` 是無 console GUI，`sticker-forge-cli.exe` 是命令列。
- 新增 `src/sticker_forge/app_launcher.py`，可從 CLI / exe 開啟本機 HTML 介面。
- 新增 `app/index.html`、`app/styles.css`、`app/app.js`，提供可直接開啟的本機 HTML fallback；ZIP 由本機 JavaScript 產生，不依賴 CDN，支援 LINE ZIP 與 9 張 PNG-only ZIP，並支援繁體中文 / English 切換。
- 新增 `README.en.md`。
- 新增 `docs/LINE_SUBMISSION.md`，保留 upstream 的 LINE Creators Market 手動上架/送審說明。
- 新增 `packaging/sticker-forge.spec` 與 `packaging/build-windows.ps1`。
- 新增 pytest 測試。

## 目前 legacy

這些仍來自 upstream，已集中搬到 `reference/upstream-line-sticker-studio/`：

- `reference/upstream-line-sticker-studio/app.js`
- `reference/upstream-line-sticker-studio/index.html`
- `reference/upstream-line-sticker-studio/styles.css`
- `reference/upstream-line-sticker-studio/worker/`
- icons / OG image / manifest

## 下一步

1. 強化原生 GUI：拖放匯入、單張預覽縮放、icon。
2. 建立 Windows installer。
3. 決定使用者資料與暫存檔位置。
4. 清理不再需要的 legacy hosted backend reference。

## 注意

- 不要新增 server 架構。
- 不要代管使用者圖片或 API key。
- 不要移除 MIT attribution。
- 不要把 upstream Worker URL 當作正式設定。
