# AGENTS.md

本檔是 **SanHsien/sticker-forge** 的主要 AI coding agent 維護規則。產品與使用方式先讀 [`README.md`](README.md)；架構、打包與測試細節見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## 專案定位

Sticker Forge 是 Windows-first、local-first 的聊天貼圖製作工具：產生 prompt，讓使用者自行選擇 AI 生圖工具，再把 grid / PNG / GIF / APNG 匯回本機程式，完成切圖、去背、描邊、尺寸整理、預覽、驗證與 LINE／多平台匯出。

GUI（pywebview）與 CLI 共用 `src/sticker_forge/` 的 Python core；正式 Windows 發行版以 PyInstaller 打包。

本 repo 是 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio) 的 MIT fork。來源與 attribution 以 [`NOTICE.md`](NOTICE.md) 為準。

## 硬性邊界

- **不新增 hosted backend**：不要重建 Cloudflare Worker、Turnstile quota、集中式 Gemini proxy 或任何 Sticker Forge 圖片上傳服務。
- **不代管 AI credential**：不要要求、保存或集中管理 ChatGPT / Gemini / 其他 AI 服務的 API key、token 或登入資料。
- **不提交使用者內容**：圖片、生成 ZIP、真實人物素材、API key、token、本機 cache / temp 不得進 Git。
- **不自動送審 LINE**：可產生符合已知規格的檔案與說明，但不自動操作 LINE Creators Market。
- **不誇大平台保證**：不得宣稱 LINE 官方、認證或保證審核通過。
- **保留授權與來源**：不得移除 MIT `LICENSE`、`NOTICE.md` 或上游 attribution。
- **內容權利保守**：不要把侵權 IP、商標、真人肖像、政治人物、色情、仇恨、暴力、詐騙或個資內容包裝成「可安全送審」。

## 主要結構

- `src/sticker_forge/`：prompt、切圖、cleanup、decorate、export、preview、CLI、GUI bridge。
- `app/`：pywebview 載入的 HTML / CSS / JavaScript UI。
- `prompts/`：貼圖 prompt templates。
- `packaging/`：Windows PyInstaller build / smoke test。
- `tests/`：Python core、webapi、workflow contract、packaging 回歸測試。
- `tools/`：dependency freshness、Dependabot 分類、upstream 檢查。
- `docs/`：使用、開發、LINE 送審、Windows 驗收與決策文件。

## 開發原則

- 一般修改使用 **branch → PR → CI → merge**，不要直接在 `main` 做正常維護。
- 優先最小修補；不要為了「整理架構」把穩定的圖片處理核心大規模重寫。
- GUI 與 CLI 應共用 Python core；不要在 JavaScript 再複製第二套尺寸、去背或 export 規則。
- 新增或修改圖片處理、ZIP 結構、validator、GUI bridge 行為時要補對應測試。
- 純文件、註解或 metadata 調整不需要自動 bump version 或建立 Release。
- 只有真的發行新版本時才同步 `pyproject.toml`、CHANGELOG、tag、Release 與對應資產。
- `REVIEW.md` 是專案健康快照，不是每個 bug 的強制流水帳；只有修到既有 review 項目或新發現改變整體風險結論時才更新。

## 上游處理

本 repo 與上游目前沒有可直接 merge 的共同工作流；`upstream-check` 只負責提醒有新 commit。

需要採用上游內容時：

1. 先判斷是否符合 local-first / Windows-first 方向。
2. 只移植適用的概念或修正，不把 hosted Worker / quota / proxy 路線帶回來。
3. 完成 triage 後依既有流程更新 `tools/upstream_baseline.json`；有重要產品取捨時記錄到 `docs/DECISIONS.md`。

## 驗證

一般程式修改至少：

```powershell
git diff --check
python -m pytest
```

PR CI 會測試 Python 3.11–3.14，並在 Windows runner 建置與 smoke-test EXE。改到 GUI / packaging / LINE 特殊格式時，依 [`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) 補相應實機驗證；沒有實際做過的平台驗證，不要宣稱已通過。

## 文件責任

- `README.md` / `README.en.md`：產品首頁與核心使用流程。
- `docs/USER_GUIDE.md`：一般操作與 troubleshooting。
- `docs/DEVELOPMENT.md`：架構、測試、打包與維護。
- `docs/WINDOWS_VALIDATION.md`：Windows GUI / Release / LINE 實機驗收。
- `docs/LINE_SUBMISSION.md`：LINE 手動送審。
- `docs/DECISIONS.md`：重要取捨。
- `CHANGELOG.md`：已發行版本變更。
- `NOTICE.md`：fork、授權與第三方來源。
