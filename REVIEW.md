# Project Review 2026-07-12

## 結論

`sticker-forge` v0.18.0 是可用的 local-first 貼圖工具：CLI 與 pywebview 桌面 GUI 共用 Python core，支援 LINE 靜態貼圖、Big Stickers、emoji、訊息貼圖、動態貼圖、pop-up stickers、effect stickers 與多平台尺寸匯出。專案仍符合不架 server、不代管 AI API、不上傳使用者圖片、不自動送 LINE 審核的邊界。

v0.13.1 已補發 Windows exe，讓 GUI 匯出錯誤顯示修正進入正式 Release。v0.14.0 補齊一般使用者指南與可重現範例素材流程。v0.15.0 補上 Signal manifest pack 與 `validate --signal`。v0.16.0 補上 LINE Big Stickers 匯出與 `validate --big`。v0.17.0 補上 LINE pop-up / effect stickers CLI 匯出與 validator。v0.18.0 把 pop-up / effect 接進 GUI。

## 已修正

| 項目 | 狀態 | 修正 |
| --- | --- | --- |
| v0.13.0 exe 缺少 GUI 匯出錯誤顯示 | ✅ 已補發 | `v0.13.1` Windows Release 已包含 `app/app.js` 的 `reportExport()` 錯誤顯示修正。 |
| 缺一般使用者流程文件 | ✅ 已修 | 新增 `docs/USER_GUIDE.md`，整理 exe 啟動、靜態貼圖、emoji、訊息貼圖、動態貼圖、多平台匯出與常見問題。 |
| 缺可公開測試素材 | ✅ 已修 | 新增 `examples/create_sample_assets.py`，本機產生非侵權 3x3 grid 與 8 個 GIF；生成素材與 ZIP 不進版控。 |
| 範例 CLI 流程太少 | ✅ 已修 | `examples/README.md` 補齊 export、emoji、message、animated 與 validate 指令。 |
| Signal 多平台匯出缺 metadata | ✅ 已修 | `platform --target signal` 產出 `cover.png` 與 `signal_manifest.json`，`validate --signal` 可檢查 ZIP。 |
| LINE Big Stickers 尚未落地 | ✅ 已修 | 新增 `big` CLI、GUI「匯出 Big Stickers」與 `validate --big`。 |
| LINE pop-up / effect stickers 尚未落地 | ✅ 已修 | 新增 `popup` / `effect` CLI 與 `validate --popup` / `validate --effect`。 |
| pop-up / effect 只能用 CLI | ✅ 已修 | GUI 新增「匯入畫面動畫」、「匯出 pop-up」、「匯出 effect」。 |

## 覆核證據

- `v0.13.1` 是把 `v0.13.0` 後的 GUI 錯誤顯示修正與文件清理補發成 Windows exe 的 patch release。
- `v0.14.0` 加入 user guide 與 sample asset generator，讓使用者能在不提交生成素材的前提下重現基本流程。
- `v0.15.0` 加入 Signal manifest pack 與 validator。
- `v0.16.0` 加入 LINE Big Stickers export 與 validator。
- `v0.17.0` 加入 LINE pop-up / effect stickers CLI export 與 validator。
- `v0.18.0` 加入 LINE pop-up / effect stickers GUI flow。
- `python -m pytest`：73 passed。
- `.\packaging\build-windows.ps1`：通過。
- `git diff --check`：無 whitespace error。
- 打包後 GUI `--smoke` 與 CLI `--help` 通過。
- GitHub Release 含 `sticker-forge-v0.18.0-windows-x64.zip` 與 `.sha256`。

## 目前風險

### P2：APNG 類 LINE 規格仍需真實上傳抽驗

程式已用 APNG、影格數、尺寸與 ZIP 結構做基本檢查，並新增 `examples/create_line_trial_packs.py` 產生非侵權抽驗 ZIP；但 LINE Creators Market 對動態、pop-up、effect APNG 的檔案大小、播放行為、重複影格等仍可能有平台端判定。下一步是用該腳本產物做一次手動上傳抽驗。

### P2：pywebview 依賴 Windows WebView2

Windows 10/11 通常已內建 WebView2，但少數環境可能缺 runtime。若使用者回報 GUI 無法開啟，要優先檢查 WebView2 runtime，而不是回到架 server 或重做 web backend。

### P3：REVIEW.md 需要跟版本一起維護

之後每次重大版本或 release 後，README / README.en.md / REVIEW.md / docs/DEVELOPMENT.md 都要同步更新，避免入口文件互相矛盾。

## 不做

- 不新增 Cloudflare Worker、Turnstile、quota、Gemini proxy 或 hosted backend。
- 不提交 API key、使用者圖片、生成 ZIP 或暫存資料。
- 不宣稱 LINE 官方、LINE 認證或保證上架通過。
- 不做 LINE Creators Market 自動上架或送審自動化。
- 不移除 MIT 授權與原作者 attribution。
