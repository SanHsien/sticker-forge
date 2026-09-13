# Project Review 2026-08-09

## 結論

`sticker-forge` 的 Python core、CLI、pywebview GUI 與 Windows onedir 打包架構一致，
local-first 邊界仍然成立：不架 hosted backend、不代管 AI API、不上傳使用者圖片、
不自動送 LINE 審核。

本輪（`v0.19.0`–`v0.22.0`）把上游 `yazelin/line-sticker-studio` 的 chroma tune 系統
整套移植完成、補上白色描邊／陰影後製，並把上游更新檢查自動化。自動化測試
121 passed，Windows 打包與打包後 exe 抽驗通過。

**但還不能切 `v1.0.0`**，而且發現一個必須先處理的發行面問題：GitHub 上目前
只剩 `v0.22.0` 一個 tag 與一個 Release，`v0.18.0`–`v0.21.0` 都不在遠端（本機 tag
完好）。詳見「尚未通過」。

## 本輪實證

- `HEAD`、`origin/main` 與 `v0.22.0` 同步於 `006aee2`。
- Python 3.14：`python -m pytest` **121 passed**。
- `node --check app/app.js`、`git diff --check` 通過。
- `packaging/build-windows.ps1` 通過：121 tests、PyInstaller、GUI `--smoke`、CLI help。
- 打包後 exe 抽驗：`--tune {safe,balanced,aggressive,continuous}`、
  `--outline {none,simple,fancy}` 都在；`_internal/app` 內含進階面板的
  HTML／JS／CSS 資源。
- 去背修正以合成圖與像素差驗證：
  - despill gating——藍 `(30,60,220)`、紅 `(220,40,40)` 前景保色，背景仍去除。
  - strict vs continuous——霧狀綠幕在 `balanced` 殘留（kept 20%），
    `continuous`／`aggressive` 清乾淨（kept 19%）。
  - 來源 alpha 合成——半透明紅前景維持 alpha 128，不再被拉成 255。
  - erode——12 個 partial-alpha fringe 像素在 `erode=1` 歸零，角色不受損。
- 描邊 CLI 端到端：`--outline fancy` 的 `01.png` 白色不透明像素 1527 → 20122，
  且 `validate` 仍回報 `OK`（背景維持透明，未違反 LINE 規格）。
- GUI 進階面板實機驗證：bridge 供 4 個 preset、預設未啟用、啟用後送出完整自訂
  profile、`soft=0.39/hard=0.12` 正確夾成 `0.12`、無水平溢位、滑桿吃到
  `balanced` 值（0.25 / 0.05 / 50 / 110 / 1.70 / 0）。
- 自訂 profile 確實改變結果（同一張霧狀綠幕）：`balanced` 保留 14.0%、
  寬鬆自訂 12.9%、保守自訂 34.6%——是 preset 到不了的範圍。
- [Upstream check run 31269260345](https://github.com/SanHsien/sticker-forge/actions/runs/31269260345)
  已在 GitHub 實際執行並成功；workflow 以 `Upstream commit check` 註冊為 active。
- 上游檢查器以「把 baseline 倒退 12 個 commit」實測：正確把 `1b94d69`
  列入需 review，並把 worker／campaigns／PWA 的 commit 歸入 known-irrelevant。

## 本輪修復

| 問題 | 嚴重度 | 修復 |
| --- | --- | --- |
| despill 套用到每個保留像素，非 key 前景被硬拉通道（藍→帶綠、紅→橘、藍在洋紅底下→黑） | P1 | `12cc80c`（`v0.19.0`）改為只對 `_key_score > 0` 的偏 key 像素去溢色。 |
| partial-alpha 分支直接覆寫 alpha，忽略來源透明度；半透明 APNG 影格會變得更不透明 | P1 | `007408b`（`v0.20.0`）改為 `key_alpha × 來源 alpha` 合成。 |
| 不純綠幕（AI 生圖的光暈／褪色背景）在 strict 模式整片保留，是 LINE 退件主因 | P1 | `007408b`（`v0.20.0`）新增 `continuous` preset。 |
| 上游更新只靠人工想到才看 | P2 | `9d0bd44`（`v0.21.0`）新增每週 `upstream-check` workflow 與 baseline。 |
| 深色角色在 LINE 深色聊天主題下看不清；prompt 要求白色描邊不可靠 | P2 | `9d0bd44`（`v0.21.0`）新增本機描邊／陰影後製。 |
| `make_chroma_tune()` 與漸層去溢色在出貨 exe 中無使用者路徑（死碼） | P2 | `006aee2`（`v0.22.0`）新增 GUI 進階去背面板。 |

## 尚未通過

### P1：GitHub 上只剩 `v0.22.0` 一個 tag 與 Release

`git ls-remote --tags origin` 與 GitHub Releases API 都只回報 `v0.22.0`；
`v0.18.0`–`v0.21.0`（以及更早的 `v0.1.0`–`v0.17.0`）都不在遠端。本機 23 個 tag
完好，且指向的 commit 全都仍在 `origin/main` 歷史中，因此可以還原。

還原前需要先確認原因，避免把使用者刻意移除的東西又推回去。在確認之前，
不應對外宣稱這些版本「有正式 Release」。

### P1：LINE Creators Market 平台抽驗仍未完成

本機 validator 不能代替 LINE 平台判定。靜態、Big、emoji、訊息、動態、pop-up、
effect 都要以非侵權抽驗包（`python examples\create_line_trial_packs.py`）手動
上傳；動態、pop-up、effect 還要確認 APNG 播放、循環與平台預覽。這是 `v1.0.0`
的主要缺口。

### P2：完整 GUI 匯出矩陣仍待真實檔案對話框驗證

已驗啟動、語系、匯入、切圖、選取、預覽、去背、進階面板與錯誤顯示。原生儲存
對話框的焦點在 Computer Use 下不穩定，因此 GUI 寫出 ZIP 尚未列為 PASS。依
[`docs/WINDOWS_VALIDATION.md`](docs/WINDOWS_VALIDATION.md) 逐項補齊。

### P2：WebView2 與 Windows 安全提示是外部環境 gate

少數 Windows 10/11 可能缺 WebView2 Runtime；SmartScreen、Defender 或 runtime
安裝提示不能由自動測試代替，須由維護者在旁監督並記錄 `PASS`／`FAIL`／`BLOCKED`。

### P2：guarded merge 尚待第一個真實低風險 Dependabot PR

分類器、workflow 契約、遠端 CI 與無 PR queue 的安全退出都可自動驗證，但實際
label、head-bound policy check、自動核准與 squash merge 必須等 Dependabot 提出
符合政策的 minor／patch PR 後才能取得端到端證據。

### P2：CLI 無自訂 tune 逃生口（刻意）

自訂 profile 目前只有 GUI 進階面板與 Python API 能用。CLI 的價值在可重現的
腳本化，逐張視覺微調本來就該在 GUI 做。若日後有腳本化需求，加單一
`--tune-json`，不要加六個旗標。

## 發行判定

- 下一個 patch／minor：本機驗證與打包已足夠，但需先解決上面的 Release／tag
  問題，確保發行歷史一致。
- `v1.0.0`：需完成 LINE Creators Market 七種類型手動上傳抽驗、完整 GUI 匯出
  矩陣，並確認 Release 資產齊備後才發布。

## 不做

- 不新增 hosted backend、Cloudflare Worker、Turnstile、quota 或 Gemini proxy。
- 不提交 API key、使用者圖片、生成 ZIP 或暫存資料。
- 不宣稱 LINE 官方、LINE 認證或保證上架通過。
- 不做 LINE Creators Market 自動上架或自動送審。
- 不移除 MIT 授權與原作者 attribution。
