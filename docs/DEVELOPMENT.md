# Development

維護者與 AI 接手用的單一開發文件：架構、本機指令、打包發行、legacy 邊界。使用者導向的說明在根目錄 [`README.md`](../README.md)；決策紀錄在 [`DECISIONS.md`](DECISIONS.md)；上架流程在 [`LINE_SUBMISSION.md`](LINE_SUBMISSION.md)；最新 review 在 [`../REVIEW.md`](../REVIEW.md)。

## 架構

```text
桌面 GUI（pywebview 視窗載入 app/ HTML）    CLI（python -m sticker_forge）
        │                                        │
        └──────────► 同一套 Python core ◄────────┘
                     產生 prompt
                        ▼
使用者複製 prompt 到 ChatGPT / Gemini / 其他生圖工具，下載 3x3 grid
        │  匯入
        ▼
split → cleanup → resize → preview → export ZIP
```

不需要 hosted backend。AI 生成發生在使用者自選的外部工具，`sticker-forge` 只處理提示詞與本機圖片加工。**GUI 與 CLI 共用同一套 Python core**：GUI 的 `app/` HTML 只負責畫面，切圖/去背/匯出/prompt 全透過 pywebview bridge 呼叫 Python（`webapi.Api`），不再有 JavaScript 平行實作。

### 模組（`src/sticker_forge/`）

| 模組 | 職責 |
|------|------|
| `spec` | LINE 尺寸、張數、chroma-key 與去背 tune profile 的單一來源 |
| `prompts` | 提示詞欄位渲染（中英文模板、有字／無字）、`SUGGESTIONS` 下拉建議、`PROMPT_PRESETS` 主題預設包 |
| `splitter` | 3x3 grid 切圖，3% inset；尺寸不整除時向下取整丟餘數；`load_animated_frames` 讀單一動態檔（GIF/APNG）→ 影格＋時間 |
| `cleanup` | green / magenta chroma-key 去背 + despill |
| `exporter` | LINE 貼圖 ZIP（`LINE_PACK_SIZES` 8/16/24/32/40、可選 main/tab index）、LINE 訊息貼圖 ZIP（`LINE_MESSAGE_PACK_SIZES` 8/16/24、padding 0）、LINE emoji ZIP（8–40×180×180＋96×74 縮圖）、LINE 動態貼圖 ZIP（`export_animated_zip`：8/16/24 APNG≤320×270＋動畫 main＋靜態 tab）、PNG-only ZIP、多平台 ZIP（`PLATFORM_SPECS`：Telegram/WhatsApp/Discord/Signal）匯出與 ZIP 驗證（貼圖／emoji、含透明背景檢查）、尺寸整理與 padding |
| `preview` | 貼圖預覽 metadata 與選圖檢查 |
| `cli` | 命令列入口（`python -m sticker_forge`） |
| `webapi` | pywebview bridge：`Api`（JS 呼叫的 render_prompt/split/cleanup/export）＋ `run()` 開視窗 |
| `gui` | 桌面 GUI 入口（`sticker-forge.exe`），呼叫 `webapi.run()` |
| `app_launcher` | 定位打包後的 `app/index.html`（供 webview 載入） |

前端 `app/`（`index.html` + `app.js` + `styles.css`）是純 UI，透過 `window.pywebview.api` 呼叫 Python core，不含影像演算法。

## 本機開發

```powershell
python -m pip install -e ".[dev,gui,packaging]"
git diff --check
python -m pytest
```

常用指令：

```powershell
python -m sticker_forge prompt
python -m sticker_forge prompt --preset office-cat
python -m sticker_forge --lang en prompt
python -m sticker_forge prompt --character "原創柴犬" --chroma-key magenta --output outputs\prompt.md
python -m sticker_forge split examples\grid.png -o outputs\cells --inset-ratio 0.03
python -m sticker_forge cleanup examples\cell.png -o outputs\cell-clean.png --key-color 00ff00
python -m sticker_forge preview examples\grid.png --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\line-stickers.zip --select 1,2,3,4,5,6,7,8
python -m sticker_forge export examples\grid.png -o outputs\raw.zip --keep-background
python -m sticker_forge export g1.png g2.png -o outputs\pack16.zip --select 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16 --main 2 --tab 3
python -m sticker_forge stickers examples\grid.png -o outputs\transparent-stickers.zip
python -m sticker_forge platform examples\grid.png -o outputs\telegram.zip --target telegram
python -m sticker_forge emoji examples\grid.png -o outputs\line-emoji.zip --thumb 1
python -m sticker_forge message examples\grid.png -o outputs\line-message.zip
python -m sticker_forge animated a.gif b.gif c.gif ... -o outputs\line-animated.zip   # 8/16/24 animated files
python -m sticker_forge validate outputs\line-stickers.zip
python -m sticker_forge validate outputs\line-emoji.zip --emoji
sticker-forge-gui --lang en          # or: python -m sticker_forge.gui  (opens the pywebview desktop app)
```

> **去背預設開啟**：`export` / `stickers` / `preview` 因為切圖會用 key 色填背景、且 LINE 要求透明背景，預設就會去背。加 `--keep-background` 可保留實心底色（少數非 LINE 用途）。
>
> `--key-color` 只在 `cleanup` 有效（distance-based 去背）。`export` / `stickers` / `preview` 固定走 `--key-name` 的 green/magenta score-based 去背，不接受 `--key-color`。

修改 JavaScript 時可加跑語法檢查：

```powershell
node --check app/app.js
```

## 測試涵蓋

`python -m pytest`（目前 58 passed）。最小涵蓋：prompt CLI 輸出與渲染、中英文語系、3x3 inset 切圖（含 1024×1024 非整除尺寸）、選圖／排序、green/magenta 去背、匯出預設去背與 `--keep-background`、main/tab image、LINE 靜態／emoji／訊息／動態 ZIP 結構與 validator（含透明背景檢查）、PNG-only ZIP、多平台 ZIP、padding、`webapi.Api` bridge（bootstrap/prompt/split/cleanup/export）。GUI 視窗本身需在 Windows 桌面實跑 `sticker-forge-gui` 或 exe 驗證。

## 打包與發行

打包工具固定為 PyInstaller，設定在 `packaging/`：

- `packaging/sticker-forge.spec`：同時產出 GUI 與 CLI 兩個 exe（onedir COLLECT）。
- `packaging/build-windows.ps1`：安裝 `.[dev,packaging]` → 跑 pytest → PyInstaller build → smoke test。

產物（build script 把 PyInstaller cache 與 dist 放到 `%TEMP%`，避開 OneDrive 對 repo 內 `build/`、`dist/` 的鎖檔）：

```text
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe       # 原生 GUI，無 console
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe   # 命令列
```

`app/` 與 `prompts/` 會一起打進 bundle（`_internal/app`、`_internal/prompts`），GUI 由 pywebview 載入 `_internal/app/index.html`。spec 的 `hiddenimports` 含 `webview.platforms.edgechromium`（Windows WebView2 backend）。因為是 onedir，`_MEIPASS` 指向持久資料夾。

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

已發行：`v0.1.0`…`v0.13.1`。exe 圖示為 `packaging/icon.ico`。

## Legacy 邊界

upstream web app / Worker 的 vendored reference source 已移除。後續維護以本 repo 的 Python core、pywebview GUI、測試與決策文件為準；若需要查原始 fork，可看 git history 或外部 [`yazelin/line-sticker-studio`](https://github.com/yazelin/line-sticker-studio)。

Worker、Turnstile、quota、Gemini proxy 一律視為不符合 local-first 的 legacy 方向，不要重建，也不要再往 server 方向投入。硬性禁令見 [`../CLAUDE.md`](../CLAUDE.md) 與 [`../AGENTS.md`](../AGENTS.md)。
