# AGENTS.md

給 Codex 與其他 AI coding agents 在本專案工作時的指引。

## 專案宗旨

`sticker-forge` 是 local-first 的 LINE 貼圖製作工具。目標是做成使用者可下載的本機程式，例如 Windows `.exe`。

核心流程：

1. 程式提供提示詞模板。
2. 使用者自行到 ChatGPT / Gemini / 其他生圖工具產生 3x3 貼圖圖案。
3. 使用者把生成圖匯回本機程式。
4. 程式在本機切圖、去背、整理尺寸、預覽、匯出 LINE sticker ZIP。

本專案不打算架 server、不代管 AI API、不處理使用者圖片上傳服務。

## 硬性邊界

- 不新增 hosted backend、Cloudflare Worker 服務、Turnstile quota 或集中式 Gemini proxy。
- 不提交 API key、token、`.dev.vars`、使用者圖片、生成 ZIP 或本機暫存資料。
- 不宣稱本工具為 LINE 官方、LINE 認證或保證上架通過。
- 不移除 MIT 授權與原作者 `yazelin` attribution；見 `NOTICE.md`。
- 不鼓勵生成侵害 IP、商標、真人肖像、政治人物、色情、仇恨、暴力、詐騙、個資等高風險內容。
- 不做 LINE Creators Market 自動上架或送審自動化。

## 目前狀態

本 repo 已把 upstream web app 與 Worker 搬到 `reference/upstream-line-sticker-studio/`。這些是參考資料，不是新方向。

後續應往這個結構整理：

- `src/sticker_forge/`：本機工具主程式。
- `prompts/`：提示詞模板。
- `packaging/`：exe 打包與發行流程。
- `tests/`：切圖、去背、ZIP 檢查等測試。
- `examples/`：範例說明，不放侵權素材。
- `docs/`：架構、規劃、交接文件。
- `reference/upstream-line-sticker-studio/`：原專案保留參考，維持目錄結構。

## 開發原則

- 先把產品路線改清楚，再搬功能。
- 優先保留可本地化的能力：prompt、切圖、去背、尺寸整理、ZIP 匯出。
- Worker、quota、Turnstile、線上 API proxy 僅作為 reference，不要當成新架構延伸。
- 若選技術棧，優先考慮易打包 Windows exe 的方案。
- 新增圖片處理邏輯時要補測試。
- 使用繁體中文回覆與撰寫維護文件；程式命名維持英文。

## 驗證方向

本機工具已建立（CLI + pywebview 桌面 GUI，共用同一套 Python core + PyInstaller 打包）。改動後至少確認：

```powershell
git diff --check
python -m pytest
```

最小涵蓋：prompt CLI 輸出與渲染、3x3 切圖（含非整除尺寸）、green/magenta 去背、ZIP 結構與 validator、exe smoke test。

## 文件入口

- `README.md` / `README.en.md`：使用者入口、產品方向與路線圖（含最新狀態）。
- `REVIEW.md`：最新專案 review。
- `docs/DEVELOPMENT.md`：架構、本機指令、打包發行、legacy 邊界。
- `docs/DECISIONS.md`：決策紀錄。
- `docs/LINE_SUBMISSION.md`：LINE 手動上架與送審說明。
- `NOTICE.md`：fork 來源、MIT 授權與第三方聲明。
