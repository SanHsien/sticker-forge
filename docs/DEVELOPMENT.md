# Development

## 目前階段

目前已建立最小 Python CLI、核心模組、本機 HTML 介面與 Windows `.exe` 打包流程。

短期任務：

- 擴充圖片處理核心：預覽資料與互動選圖。
- 擴充 ZIP 匯出前錯誤提示。
- 強化本機 HTML 介面的去背、padding 與預覽控制。

## 基礎檢查

```powershell
git diff --check
python -m pytest
```

本機執行：

```powershell
python -m sticker_forge prompt
python -m sticker_forge --lang en prompt
python -m sticker_forge prompt --character "原創柴犬" --output outputs\prompt.md
python -m sticker_forge split examples\grid.png -o outputs\cells
python -m sticker_forge cleanup examples\cell.png -o outputs\cell-clean.png --key-color 00ff00
python -m sticker_forge export examples\grid.png -o outputs\line-stickers.zip --select 1,2,3,4,5,6,7,8 --chroma-key
python -m sticker_forge stickers examples\grid.png -o outputs\transparent-stickers.zip --chroma-key
python -m sticker_forge validate outputs\line-stickers.zip
python -m sticker_forge app --print-path
python -m sticker_forge --lang en app --print-path
start .\app\index.html
.\packaging\build-windows.ps1
```

若修改 JavaScript，可加跑：

```powershell
node --check app/app.js
node --check reference/upstream-line-sticker-studio/app.js
node --check reference/upstream-line-sticker-studio/worker/src/index.js
```

## 未來驗證

最小測試應包含：

- prompt template CLI 輸出與渲染。
- CLI / HTML 工作台中英文語系。
- 3x3 grid inset 切圖。
- 選 8 張貼圖。
- green / magenta chroma-key 去背。
- main/tab image 生成。
- ZIP 檔案結構與 validator。
- PNG-only stickers ZIP。
- padding。
- Windows exe 啟動 smoke test。

## 打包方向

目標是使用者下載後可在本機處理，不需要自行架 server。

`packaging/` 已固定使用 PyInstaller：

- `packaging/sticker-forge.spec`
- `packaging/build-windows.ps1`

首版 release：

- 版本：`v0.1.0`
- 產物：`sticker-forge-v0.1.0-windows-x64.zip`
- checksum：`sticker-forge-v0.1.0-windows-x64.zip.sha256`

目前 build script 的實際行為：

- 安裝 `.[dev,packaging]`。
- 跑 `python -m pytest`。
- 使用 `packaging/sticker-forge.spec`。
- PyInstaller workpath 使用 `%TEMP%\sticker-forge-pyinstaller-build`。
- PyInstaller distpath 使用 `%TEMP%\sticker-forge-pyinstaller-dist`。
- 產物在 `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe`。
- 跑 `sticker-forge.exe --help` smoke test。

這和最早的 repo-local `build/`、`dist/` 草稿不同；目前版本刻意避開 OneDrive 對 repo 內 build cache 的鎖檔問題。

後續仍要決定使用者資料 / 暫存檔位置。

## Legacy 開發

`reference/upstream-line-sticker-studio/worker/`、Cloudflare、Turnstile、quota、Gemini proxy 都是 upstream legacy。除非任務明確要求維護舊版 web app，否則不要再往 server 方向投入。
