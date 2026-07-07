# Decisions

## 2026-07-05：Repo 命名

決定使用 `sticker-forge` 作為 fork 後 repo 名稱。

## 2026-07-05：產品方向

決定改成 local-first 工具。

工具只負責：

- 產生提示詞。
- 接收使用者自行生成的 3x3 貼圖圖。
- 本機切圖、去背、尺寸整理、預覽與 ZIP 匯出。

工具不負責：

- 架 server。
- 代管 AI API。
- 儲存使用者圖片。
- 自動上架 LINE Creators Market。

## 2026-07-05：發行方向

長期目標是可下載的本機程式，優先考慮 Windows `.exe`。

## 2026-07-05：Repo Description

建議使用：

```text
Local toolkit for preparing LINE sticker packs: prompt templates, image cleanup, slicing, and export.
```

## 2026-07-05：保留 MIT Attribution

本 repo 來自 `yazelin/line-sticker-studio`，原專案使用 MIT License。

決策：

- 保留根目錄 `LICENSE` 的原作者 MIT notice。
- 新增 `NOTICE.md` 說明 fork 來源、授權義務、第三方服務聲明與 AI 內容責任。

## 2026-07-06：語系策略

決定使用單一 exe 內建繁體中文與 English，不拆兩份安裝包。

決策：

- CLI 使用 `--lang zh-Hant|en` 切換 help、prompt 與狀態輸出。
- 本機 HTML 工作台提供語言選單，並以 localStorage 記住使用者選擇。
- prompt template 維持中英文各一份，全部打包進 PyInstaller bundle。
- README 維持繁體中文主入口，另建 `README.en.md`。

## 2026-07-06：Windows exe 入口策略

決定主程式改為原生 GUI，不再讓使用者雙擊 console CLI。

決策：

- `sticker-forge.exe` 是無 console 的 tkinter GUI。
- `sticker-forge-cli.exe` 是命令列工具，保留所有 CLI 指令。
- `app/index.html` 保留為本機 HTML fallback，不再作為主要 exe 體驗。
- build script 必須同時 smoke test GUI 與 CLI。

## 2026-07-07：切圖尺寸容忍與去背參數收斂

依 2026-07-07 review 修正三個一致性問題：

- **切圖尺寸**：`split_grid` 不再要求邊長可被 3 整除。改為向下取整、丟掉右／下邊餘數（對齊 web 版 `Math.floor`），讓最常見的 1024×1024 AI 生圖在 CLI/GUI/web 都能處理；僅在圖太小到切不出格時才報錯。
- **`--key-color`**：從 `export`/`stickers`/`preview` 移除。這些指令的 `--key-name` 恆有預設 green/magenta，永遠走 score-based 去背路徑，`--key-color` 從未生效。保留在 `cleanup`（distance-based 真的會用）。不為了保留旗標而把任意色塞進 score-based 演算法。
- **web 去背 despill**：`app/app.js` 補上與 Python 相同的 despill（green→`green=(r+b)/2`、magenta→灰階），三條路徑輸出一致（60/60 像素交叉比對通過）。

另註記：`cleanup.py` 的 `get_flattened_data` 分支是 Pillow 14 前向相容 shim（`getdata()` 將於 2027 移除），**不是**死碼，勿刪。

## 2026-07-07：匯出預設去背

`export` / `stickers` / `preview` 改為**預設去背**，新增 `--keep-background` opt-out（等於把原本 opt-in 的 `--chroma-key` 反轉為預設）。

依據：

- LINE Creators Market 官方要求貼圖背景**必須透明**（creator.line.me guideline、Sales Manual、Submission Guide 三處明載）。不去背的匯出 = LINE 必退，見 `LINE_SUBMISSION.md`。
- 切圖步驟本來就刻意用 key 色填滿背景（`split_grid_to_stickers` 的 `background=(*key.rgb,255)`），**就是為了後續去背**；split 填色 + 不去背 = 內部不一致。upstream `line-sticker-studio` 同樣把去背當明示步驟（step 3 + 「全部去背」）。
- 假設輸入是 green/magenta 綠幕素材（prompt 明確要求），對此輸入自動去背是正確的；非綠幕素材本來就產不出合格 LINE 貼圖。

範圍：只改 headless 的 CLI（無視覺回饋、最容易踩雷）。原生 GUI 與 web 是互動式、使用者看得到綠底縮圖又有明確「去背」鈕，維持明示模式不變。
