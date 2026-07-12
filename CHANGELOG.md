# Changelog

本檔記錄 `sticker-forge` 的版本變更。專案方向、使用方式與路線圖見 [`README.md`](README.md)；架構與打包流程見 [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)。

## v0.17.0

- **LINE pop-up stickers**：新增 `popup` CLI 指令，使用靜態 3x3 grid 搭配 8/16/24 個動態 GIF/APNG，輸出靜態貼圖、480x480 APNG pop-up images、`popup-main.png`、`main.png`、`tab.png` 與 README。
- **LINE effect stickers**：新增 `effect` CLI 指令，輸出 480x480 APNG effect images 與同套靜態貼圖結構。
- **Pop-up / effect validator**：新增 `validate --popup` 與 `validate --effect`，檢查張數、檔名、尺寸、APNG 影格數、透明背景與 ZIP 結構。
- **正式版門檻**：文件明確把 `v1.0.0` 留給手動 LINE 上傳抽驗、GUI smoke、Windows exe 發行檢查與文件一致性覆核完成後。

## v0.16.0

- **LINE Big Stickers**：新增 `big` CLI 指令與 GUI「匯出 Big Stickers」按鈕，輸出 396x660 貼圖圖檔、main.png、tab.png 與 README。
- **Big Sticker validator**：`validate --big` 以 LINE Big Stickers 尺寸檢查 ZIP。
- **官方規格依據**：依 LINE Creators Market Big Stickers guideline 補文件與決策紀錄；pop-up / effect stickers 留待下一輪 APNG 規格實作。

## v0.15.0

- **Signal manifest pack**：`platform --target signal` 會輸出 512x512 PNG、`cover.png`、`signal_manifest.json` 與 README，manifest 含 title、author、cover、每張貼圖檔名與 emoji 指派。
- **Signal validator**：`validate --signal` 檢查 Signal ZIP 的 manifest、cover、貼圖尺寸、透明背景、檔名與 emoji 指派。
- **CLI metadata**：`platform` 新增 `--title`、`--author`、`--emoji`；GUI 多平台匯出會沿用套組標題與作者欄位。

## v0.14.0

- **使用者指南**：新增 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)，整理 exe 啟動、LINE 靜態貼圖、emoji、訊息貼圖、動態貼圖、多平台匯出、常見問題與手動送審邊界。
- **可重現範例素材**：新增 [`examples/create_sample_assets.py`](examples/create_sample_assets.py)，本機產生非侵權 3x3 grid 與 8 個 GIF 測試素材；`examples/generated/` 與輸出 ZIP 不進版控。
- **範例 CLI 流程**：[`examples/README.md`](examples/README.md) 補齊 export、emoji、message、animated 與 validate 指令。

## v0.13.1

- **GUI 匯出錯誤顯示**：pywebview bridge 回傳 `error` 時，HTML GUI 會顯示錯誤訊息，不再停在「匯出中」。
- **文件同步**：README、README.en、NOTICE、DEVELOPMENT、REVIEW 與 agent 指引同步到 v0.13.1 現況。
- **Source cleanup**：移除不再使用的 upstream vendored reference source；保留 MIT attribution、外部 fork 連結與 git history。

## v0.13.0

- **動態貼圖改為「匯入多個動態 GIF」＋GUI**：匯入 8／16／24 個動態 GIF/APNG（每個一張），逐格去背、resize 到 <=320x270（一邊 >=270），轉 APNG（5-20 影格），外加動畫 main 240x240 與靜態 tab 96x74。
- GUI 新增「匯入動態貼圖」與「匯出動態貼圖」；動態模式下會擋下靜態匯出。
- CLI：`sticker-forge animated a.gif b.gif ... -o out.zip`。

## v0.12.0

- **LINE 動態貼圖匯出（CLI 首版）**：依官方規格產出 APNG 動態貼圖包（<=320x270、5-20 影格、動畫 main + 靜態 tab）。

## v0.11.0

- **LINE 訊息貼圖匯出**：支援 8／16／24 張、貼圖 max 370x320、不預留邊距、main 240x240 + tab 96x74。
- GUI 新增「匯出訊息貼圖」；CLI：`sticker-forge message <grid...> -o out.zip`。

## v0.10.0

- **LINE 原創貼圖 emoji 匯出**：8-40 張、180x180 PNG 透明、檔名 `001.png...`，外加 96x74 聊天縮圖。
- GUI 新增「匯出 LINE emoji」；CLI：`sticker-forge emoji <grid...> -o out.zip --thumb 1`、`validate --emoji`。

## v0.9.0

- **主題預設包**：提供療癒白熊、上班族貓、情侶小熊、節慶祝福等主題，填入角色／主題／語氣／風格與 8 句文字＋8 動作。
- **套組標題／作者（GUI）**：GUI 可填 LINE 套組標題與作者，寫進 ZIP 內 README。

## v0.8.0

- **更大的 LINE 套組**：支援 8／16／24／32／40 張，透過多個 3x3 grid 累積貼圖池。
- **自選主圖／聊天標籤**：可指定 `main.png` 與 `tab.png`。
- **貼圖排序**：每張可調整順序，決定 `01...NN` 輸出順序。
- CLI：`sticker-forge export grid1.png grid2.png -o out.zip --select 1,...,16 --main 2 --tab 3`。

## v0.7.0

- **多平台匯出**：支援 Telegram（512 PNG）、WhatsApp（512 WebP + 96 tray）、Discord（320 PNG）、Signal（512 PNG）尺寸與格式。
- GUI 可選平台匯出；CLI：`sticker-forge platform <grid> -o out.zip --target telegram`。

## v0.6.0

- **單張放大檢視**：點貼圖縮圖可放大檢查透明背景。
- **單張去背／還原**：可對單張去背或還原；全部去背與單張去背都從原始切圖計算，避免重跑疊加髒邊。

## v0.5.0

- **UI 收斂成一套**：桌面 GUI 從 tkinter 改為 pywebview 原生視窗載入 HTML 介面，切圖、去背、匯出與 prompt 全部由本機 Python core 處理。

## v0.4.0

- **Prompt 下拉建議**：角色、主題、語氣、風格、語言與 8 句文字、8 個動作欄位提供下拉建議，並支援中英文語系切換。

## v0.3.0

- **拖放匯入**：本機 HTML 工作台可直接拖放 3x3 圖。
- **Windows icon**：GUI / CLI exe 使用 `packaging/icon.ico`。
- **Legacy 清理**：移除 legacy Cloudflare/Gemini 後端、campaign-checker CI，以及後續不再使用的 upstream vendored reference source；保留外部 fork 來源連結與 attribution。

## 2026-07-07 一致性修正

- **切圖尺寸**：`split_grid` 不再要求邊長可被 3 整除，改向下取整丟餘數，最常見的 1024x1024 AI 生圖在 CLI / GUI / web 都能處理。
- **`--key-color`**：從 `export` / `stickers` / `preview` 移除死參數，保留在 `cleanup`。
- **web 去背 despill**：`app/app.js` 對齊 Python 的 despill，三入口去背輸出一致。
- **打包驗證**：實測 PyInstaller build，GUI `--smoke`、CLI export/validate、bundle 資源皆通過；`python -m sticker_forge.cli` 補上 `__main__` guard。
- **匯出預設去背**：`export` / `stickers` / `preview` 改為預設去背；需要保留實心底色時改用 `--keep-background`。
- **validate 檢查透明背景**：`validate` 會標記完全不透明的貼圖，擋下常見 LINE 退件原因。
