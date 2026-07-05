# packaging

放本機執行檔打包設定與發行流程。

目標：

- Windows `.exe`。
- 使用者下載後可本機處理圖片。
- 不需要架 server。
- 不需要使用者設定 AI API key。

目前打包工具固定為 PyInstaller。

CLI 與 exe 內建繁體中文 / English：

```powershell
sticker-forge.exe --lang zh-Hant
sticker-forge.exe --lang en
sticker-forge-cli.exe --lang zh-Hant prompt
sticker-forge-cli.exe --lang en prompt
sticker-forge-cli.exe --lang en app
```

## Build

```powershell
.\packaging\build-windows.ps1
```

流程：

- 安裝 `.[dev,packaging]`。
- 跑 `python -m pytest`。
- 使用 `packaging/sticker-forge.spec` 產生 `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe`。
- 同時產生 `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe`。
- PyInstaller workpath 使用 `%TEMP%\sticker-forge-pyinstaller-build`，distpath 使用 `%TEMP%\sticker-forge-pyinstaller-dist`，避免 OneDrive 鎖住 build / dist cache。
- 執行 `sticker-forge.exe --smoke` 與 `sticker-forge-cli.exe --help` smoke test。
- `sticker-forge.exe` 是原生 GUI，無 console，雙擊不會出現文字視窗後關閉。
- `sticker-forge-cli.exe` 是命令列工具。
- `app/` 本機 HTML 介面會一起打進 PyInstaller bundle，可用 `sticker-forge-cli.exe app` 開啟。
- `app/` 介面內建語言切換，支援繁體中文與 English。
- Windows console 若顯示繁中亂碼，可用 `sticker-forge-cli.exe prompt --output prompt.md` 寫出 UTF-8 prompt 檔。

目前腳本和最早的 repo-local `build/`、`dist/` 草稿不同；正式腳本把 PyInstaller cache 與產物放到 `%TEMP%`，避免 OneDrive 鎖住 repo 內的 build / dist 目錄。

## Release checklist

- `python -m pytest` 通過。
- `git diff --check` 通過。
- `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe --smoke` 通過。
- `%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe --help` 通過。
- 使用範例 3x3 grid 匯出 ZIP，並執行 `sticker-forge validate`。
- 確認沒有 API key、使用者圖片、生成 ZIP 或本機暫存檔進版控。

## Artifact naming

- `sticker-forge-v0.1.0-windows-x64.zip`
- `sticker-forge-v0.1.0-windows-x64.zip.sha256`
- `sticker-forge-v0.2.0-windows-x64.zip`
- `sticker-forge-v0.2.0-windows-x64.zip.sha256`
