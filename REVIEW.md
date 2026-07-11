# Project Review 2026-07-11

## 結論

`sticker-forge` v0.13.0 是可用的 local-first 貼圖工具：CLI 與 pywebview 桌面 GUI 共用 Python core，支援 LINE 靜態貼圖、emoji、訊息貼圖、動態貼圖與多平台尺寸匯出。專案仍符合不架 server、不代管 AI API、不上傳使用者圖片、不自動送 LINE 審核的邊界。

本輪覆核發現 3 個問題，其中 2 個是文件落後，1 個是 GUI 錯誤回報缺口；已全部修正。

## 已修正

| 項目 | 狀態 | 修正 |
| --- | --- | --- |
| GUI bridge error 被吞掉 | ✅ 已修 | `app/app.js` 的 `reportExport()` 會顯示 `result.error`，避免匯出失敗時停在「匯出中」。 |
| 英文 README 保留已移除的 `app` 子命令 | ✅ 已修 | `README.en.md` 改成 `sticker-forge-gui --lang en`。 |
| REVIEW.md 仍描述 v0.2.0 / Tkinter / 32 passed | ✅ 已修 | 本檔更新為 v0.13.0 現況、pywebview GUI 與 58 passed。 |

## 覆核證據

- `main` / `origin/main` / `v0.13.0` 均指向 `21b3572`。
- `python -m pytest`：58 passed。
- `.\packaging\build-windows.ps1`：通過。
- `git diff --check`：無 whitespace error。
- 打包後 GUI 實際啟動 5 秒仍存活，非立即閃退。
- `v0.13.0` GitHub Release 存在，含 `sticker-forge-v0.13.0-windows-x64.zip` 與 `.sha256`。

## 目前風險

### P2：動態貼圖與 LINE 規格仍需真實上傳抽驗

程式已用 APNG、影格數、尺寸與 ZIP 結構做基本檢查，但 LINE Creators Market 對 APNG 檔案大小、播放行為、重複影格等仍可能有平台端判定。下一步應用非侵權素材做一次手動上傳抽驗。

### P2：pywebview 依賴 Windows WebView2

Windows 10/11 通常已內建 WebView2，但少數環境可能缺 runtime。若使用者回報 GUI 無法開啟，要優先檢查 WebView2 runtime，而不是回到架 server 或重做 web backend。

### P3：REVIEW.md 需要跟版本一起維護

本專案已快速從 v0.2.0 推到 v0.13.0。之後每次重大版本或 release 後，README / README.en.md / REVIEW.md / docs/DEVELOPMENT.md 都要同步更新，避免入口文件互相矛盾。

## 不做

- 不新增 Cloudflare Worker、Turnstile、quota、Gemini proxy 或 hosted backend。
- 不提交 API key、使用者圖片、生成 ZIP 或暫存資料。
- 不宣稱 LINE 官方、LINE 認證或保證上架通過。
- 不做 LINE Creators Market 自動上架或送審自動化。
- 不移除 MIT 授權與原作者 attribution。
