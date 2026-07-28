# Project Review 2026-07-28

## 結論

`sticker-forge` 的 Python core、CLI、pywebview GUI 與 Windows onedir 打包架構一致，
local-first 邊界也仍成立：不架 hosted backend、不代管 AI API、不上傳使用者圖片、
不自動送 LINE 審核。

目前 `main` 可繼續作為 `v0.18.x` 修正版候選，但還不能切 `v1.0.0`。2026-07-26 已重跑
自動化、下載並檢查 `v0.18.0` Release 資產，也用 Computer Use 操作真實 Windows
視窗。找到的 GUI 英文啟動與水平溢位問題已在 `f2fdbee`（2026-07-26）修復；
修正版本機 PyInstaller build 與打包後英文 GUI 已通過，仍須發布新 GitHub Release，
並完成各匯出類型與 LINE Creators Market 的平台抽驗。

2026-07-28 再比對 `yt_fetch`、`gpt-ai-assistant`、`voicetype` 與 `openshelf`
的依賴維護流程後，本 repo 已補上 Dependabot、CI 與直接依賴 freshness 排程。
後續再補 guarded merge：只自動處理四個 CI 維護工具與 GitHub Actions 的
minor／patch；圖片、GUI、打包、未知範圍與 major 更新維持人工審查。

## 本輪實證

- `HEAD` 與 `origin/main` 在 review 開始時同步於 `bfde266`，工作樹乾淨。
- Python 3.14.6：GUI 修正前 73 passed；GUI 修正後 74 passed；依賴維護、
  Windows code-page 與 guarded merge 政策測試新增後完成 92 passed。
- `node --check app/app.js`、`python -m compileall`、
  `git diff --check` 通過。
- `examples/create_line_trial_packs.py` 產生 static、Big、emoji、message、
  animated、pop-up、effect 七種 ZIP，本機 validator 全部 `OK`。
- GitHub `v0.18.0` ZIP 下載與 Windows `Expand-Archive` 通過，共 243 entries。
- Release ZIP SHA-256 與 sidecar 一致：
  `720c9678f487ad4f15f9c4a7b24c0d6c9fdde5f110b16abc747fb7e379cb2b94`。
- Release CLI `--help`、`--lang en --help` exit 0；GUI `--smoke` exit 0。
- `v0.18.0` 真實 GUI 可啟動，繁中控制項、prompt 與 WebView2 視窗可見。
- 修正版 source 以 `--lang en` 啟動後，英文 UI、預設欄位與英文 prompt 生效。
- 修正版 source 匯入非侵權 3x3 範例後，自動切成 9 張、選取前 8 張，
  預覽列出 8 張貼圖與 main/tab；全體去背流程完成。
- 修正版 `packaging/build-windows.ps1` 通過：81 tests、PyInstaller 6.21.0、
  GUI `--smoke`、CLI help 與 bundle 資源均正常。
- 修正版 `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe
  --lang en` 已用 Computer Use 驗證英文 UI 與英文 prompt 生效。
- 最新穩定基線 Pillow 12.3.0、pytest 9.1.1、packaging 26.2、
  pywebview 6.2.1、PyInstaller 6.21.0、setuptools 83.0.0、wheel 0.47.0
  已通過本機完整 build；GitHub CI 再覆蓋 Python 3.11–3.14 與 Windows exe。
- [Dependency freshness run 30366971010](https://github.com/SanHsien/sticker-forge/actions/runs/30366971010)
  已確認八筆直接依賴全為 `OK`，且沒有 open Dependabot PR。
- [CI run 30367569318](https://github.com/SanHsien/sticker-forge/actions/runs/30367569318)
  已在 `e7ad2ab` 通過 Python 3.11–3.14 與 Windows Server 2025 exe build／smoke。
- guarded merge 本機測試涵蓋安全工具、圖片／GUI／打包套件、major、混合群組、
  超出範圍檔案、GitHub Actions 與未知 metadata；workflow 契約另檢查 trusted
  base、head SHA、五個 CI job、rebase、squash 與 `--match-head-commit`。

## 已修復

| 問題 | 嚴重度 | 修復 |
| --- | --- | --- |
| `v0.18.0` 的 `sticker-forge.exe --lang en` 仍以繁中啟動 | P1 | `f2fdbee`（2026-07-26）讓前端以 Python bridge 的 initial locale 為準，並新增回歸測試。 |
| GUI 匯出工具列在 1180px 視窗寬度形成水平捲軸 | P2 | `f2fdbee`（2026-07-26）讓 actions 自動換行；修正版 Windows 視窗已目視確認。 |
| 非 UTF-8 Windows console 執行繁中 CLI help 會 `UnicodeEncodeError` | P1 | `e7ad2ab`（2026-07-28）保留目前 code page 並替換無法表示的字元；cp1252 source／exe 與遠端 Windows CI 均通過。 |

## 尚未通過

### P1：正式 Release 尚未包含 `f2fdbee`

最新 Release 仍是 `v0.18.0`，其 Windows exe 帶有英文啟動 bug。本機修正版 build
已通過，但仍必須發布 `v0.18.1` 或下一個版本，再從 GitHub Release 重新下載驗證，
不能用本機 dist 代替正式資產。

### P1：LINE Creators Market 平台抽驗仍未完成

本機 validator 不能代替 LINE 平台判定。靜態、Big、emoji、訊息、動態、pop-up、
effect 都要以非侵權抽驗包做手動上傳；動態、pop-up、effect 還要確認 APNG
播放、循環與平台預覽。

### P2：完整 GUI 匯出矩陣仍待真實檔案對話框驗證

本輪已驗啟動、英文 locale、匯入、切圖、選取、預覽與去背。原生儲存對話框的
焦點在 Computer Use 下不穩定，因此未把 GUI 寫出 ZIP 列為 PASS。要依
[`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) 逐項驗靜態大套組、
Big、emoji、訊息、動態、pop-up、effect 與多平台輸出。

### P2：WebView2 與 Windows 安全提示是外部環境 gate

少數 Windows 10/11 可能缺 WebView2 Runtime；SmartScreen、Defender 或 runtime
安裝提示也不能由自動測試代替。這些項目須由維護者在旁監督並記錄
`PASS`、`FAIL` 或 `BLOCKED`。

### P2：guarded merge 尚待第一個真實低風險 Dependabot PR

分類器、workflow 契約、遠端 CI 與無 PR queue 的安全退出都可自動驗證，但實際
label、head-bound policy check、自動核准與 squash merge 必須等 Dependabot
提出符合政策的 minor／patch PR 後才能取得端到端證據。在此之前不能宣稱真實
PR lifecycle 已完成驗收。

## 發行判定

- `v0.18.1`：修正版 build、GitHub Release 重新下載、繁中/英文 GUI 與靜態
  匯出主流程通過後即可發布。
- `v1.0.0`：上述項目，加上完整 GUI 匯出矩陣與 LINE Creators Market
  七種類型手動上傳證據全部通過後才發布。

## 不做

- 不新增 hosted backend、Cloudflare Worker、Turnstile、quota 或 Gemini proxy。
- 不提交 API key、使用者圖片、生成 ZIP 或暫存資料。
- 不宣稱 LINE 官方、LINE 認證或保證上架通過。
- 不做 LINE Creators Market 自動上架或自動送審。
- 不移除 MIT 授權與原作者 attribution。
