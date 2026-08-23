# CLAUDE.md

本檔補充 Claude Code 在 **SanHsien/sticker-forge** 工作時的快速指引；共通規則以 [`AGENTS.md`](AGENTS.md) 為準。

## 產品定位

Sticker Forge 是 Windows-first、local-first 的聊天貼圖製作工具。使用者自行在外部 AI 服務產圖，再把 grid / PNG / GIF / APNG 匯回本機程式，由 Python core 完成切圖、去背、描邊、尺寸整理、預覽、驗證與 LINE／多平台匯出。

固定邊界：

- 不架 Sticker Forge hosted backend。
- 不代管 AI API key / token。
- 不上傳或保存使用者圖片。
- 不自動操作 LINE Creators Market。
- 不宣稱 LINE 官方或保證審核通過。
- 保留 MIT `LICENSE`、`NOTICE.md` 與上游 attribution。

## 架構

- `src/sticker_forge/`：產品核心與 CLI / GUI bridge。
- `app/`：pywebview HTML / CSS / JS UI；產品規則不要在 JS 重複實作。
- `prompts/`：prompt templates。
- `packaging/`：Windows PyInstaller build。
- `tests/`：圖片處理、export、validator、bridge 與 workflow contract。
- `docs/`：使用、開發、Windows / LINE 驗收與決策。

上游 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 只作 fork 來源與概念參考。不要把已移除的 Worker、Turnstile、quota 或集中式 Gemini proxy 重新接回正式產品。

## 工作方式

一般變更直接推 `origin/main`，不開功能分支、不開維護 PR（主人 2026-08-22 指示）；需要他人審查或高風險改動才退回 **branch → PR → CI → merge**。優先最小修改並補針對性測試；純文件或 metadata 變更不用 bump version 或製造 Release。

程式修改至少驗證：

```powershell
git diff --check
python -m pytest
```

PR CI 另會跑 Python 3.11–3.14，並在 Windows 建置 / smoke-test EXE。GUI、packaging 或 LINE 特殊格式的實機判定依 [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) 執行。

`REVIEW.md` 只有在修到既有 review 項目或新發現改變整體風險結論時更新；不要把它當成每個 bug 都必須回填的流水帳。

## 回覆

使用繁體中文，直接列出修改、驗證與仍存在的限制。沒有實際驗證過的 LINE 平台、Windows GUI 或 Release 行為，不要宣稱已通過。
