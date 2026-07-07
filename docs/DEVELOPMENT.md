# Development

維護者與 AI 接手用的單一開發文件：架構、本機指令、打包發行、legacy 邊界。使用者導向的說明在根目錄 [`README.md`](../README.md)；決策紀錄在 [`DECISIONS.md`](DECISIONS.md)；上架流程在 [`LINE_SUBMISSION.md`](LINE_SUBMISSION.md)；最新 review 在 [`../REVIEW.md`](../REVIEW.md)。

## 架構

```text
Native GUI / exe  (或 CLI / 本機 HTML fallback)
  │  產生 prompt
  ▼
使用者複製 prompt 到 ChatGPT / Gemini / 其他生圖工具，下載 3x3 grid
  │  匯入
  ▼
split → cleanup → resize → preview → export ZIP
```

不需要 hosted backend。AI 生成發生在使用者自選的外部工具，`sticker-forge` 只處理提示詞與本機圖片加工。三條入口（CLI / 原生 GUI / HTML）共用同一套規格與演算法，行為應保持一致。

### 模組（`src/sticker_forge/`）

| 模組 | 職責 |
|------|------|
| `spec` | LINE 尺寸、張數、chroma-key 與去背 tune profile 的單一來源 |
| `prompts` | 提示詞欄位渲染（中英文模板、有字／無字） |
| `splitter` | 3x3 grid 切圖，3% inset；尺寸不整除時向下取整丟餘數 |
| `cleanup` | green / magenta chroma-key 去背 + despill |
| `exporter` | LINE ZIP、PNG-only ZIP 匯出與 ZIP 驗證、尺寸整理與 padding |
| `preview` | 貼圖預覽 metadata 與選圖檢查 |
| `cli` | 命令列入口（`python -m sticker_forge`） |
| `gui` | 原生 tkinter GUI（`sticker-forge.exe`） |
| `app_launcher` | 從 CLI / exe 開啟本機 HTML 介面 |

本機 HTML fallback（`app/index.html` + `app.js` + `styles.css`）在瀏覽器端用純 JavaScript 產生 ZIP，不依賴 CDN。

## 本機開發

```powershell
python -m pip install -e ".[dev,packaging]"
git diff --check
python -m pytest
```

常用指令：

```powershell
python -m sticker_forge prompt
python -m sticker_forge --lang en prompt
python -m sticker_forge prompt --character "原創柴犬" --chroma-key magenta --output outputs\prompt.md
python -m sticker_forge split examples\grid.png -o outputs\cells --inset-ratio 0.03
python -m sticker_forge cleanup examples\cell.png -o outputs\cell-clean.png --key-color 00ff00
python -m sticker_forge preview examples\grid.png --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\line-stickers.zip --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\raw.zip --keep-background
python -m sticker_forge stickers examples\grid.png -o outputs\transparent-stickers.zip
python -m sticker_forge validate outputs\line-stickers.zip
python -m sticker_forge app --print-path
start .\app\index.html
```

> **去背預設開啟**：`export` / `stickers` / `preview` 因為切圖會用 key 色填背景、且 LINE 要求透明背景，預設就會去背。加 `--keep-background` 可保留實心底色（少數非 LINE 用途）。
>
> `--key-color` 只在 `cleanup` 有效（distance-based 去背）。`export` / `stickers` / `preview` 固定走 `--key-name` 的 green/magenta score-based 去背，不接受 `--key-color`。

修改 JavaScript 時可加跑語法檢查：

```powershell
node --check app/app.js
```

## 測試涵蓋

`python -m pytest`（目前 29 passed）。最小涵蓋：prompt CLI 輸出與渲染、中英文語系、3x3 inset 切圖（含 1024×1024 非整除尺寸）、選 8 張、green/magenta 去背、main/tab image、ZIP 結構與 validator、PNG-only ZIP、padding。

## 打包與發行

打包工具固定為 PyInstaller，設定在 `packaging/`：

- `packaging/sticker-forge.spec`：同時產出 GUI 與 CLI 兩個 exe（onedir COLLECT）。
- `packaging/build-windows.ps1`：安裝 `.[dev,packaging]` → 跑 pytest → PyInstaller build → smoke test。

產物（build script 把 PyInstaller cache 與 dist 放到 `%TEMP%`，避開 OneDrive 對 repo 內 `build/`、`dist/` 的鎖檔）：

```text
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe       # 原生 GUI，無 console
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe   # 命令列
```

`app/` 與 `prompts/` 會一起打進 bundle（`_internal/app`、`_internal/prompts`），`sticker-forge-cli.exe app` 可開啟。因為是 onedir，`_MEIPASS` 指向持久資料夾，沒有 onefile 的臨時檔清理問題。

### Release checklist

- `python -m pytest` 通過、`git diff --check` 通過。
- `sticker-forge.exe --smoke` 與 `sticker-forge-cli.exe --help` 通過。
- 用範例 3x3 grid 匯出 ZIP 並 `validate`。
- 確認沒有 API key、使用者圖片、生成 ZIP 或暫存檔進版控。

### Artifact 命名

```text
sticker-forge-v{VERSION}-windows-x64.zip
sticker-forge-v{VERSION}-windows-x64.zip.sha256
```

已發行：`v0.1.0`、`v0.2.0`。

## Legacy 邊界

upstream web app 與 Worker 已集中在 `reference/upstream-line-sticker-studio/`，只作邏輯參考，不是目標架構。Worker、Turnstile、quota、Gemini proxy 一律視為待移除／封存，不要再往 server 方向投入。硬性禁令見 [`../CLAUDE.md`](../CLAUDE.md) 與 [`../AGENTS.md`](../AGENTS.md)。
