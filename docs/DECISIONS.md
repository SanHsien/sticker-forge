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

## 2026-07-07：v0.3.0 收尾與剩餘路線圖決策

清掉剩餘路線圖，版本推進到 `v0.3.0`（本輪含 P0 切圖修正、去背預設翻轉、`validate` 透明檢查、文件收斂等行為與介面變更，pre-1.0 以 minor 進版）。

- **拖放匯入**：本機 HTML 工作台 `app/` 加原生拖放（zero-dep，已於瀏覽器實測）。**原生 tkinter GUI 不加拖放**——tkinter 需 `tkinterdnd2`/`windnd` 外部相依，違反 local-first 輕量原則；GUI 已有「匯入 3x3」按鈕，成本效益不划算。
- **Windows icon**：以 PIL 產 `packaging/icon.ico`（多尺寸），接進 spec 兩個 EXE。
- **Legacy 清理**：移除 `reference/.../worker/`（Cloudflare/Gemini/Turnstile/quota 後端，明確禁止項）與 campaign-checker（CI workflow＋script）。保留 upstream UI 參考（`app.js`/`index.html`/`styles.css`）與 assets 作 provenance 與邏輯參考。
- **Installer / 自動更新**：**決定不做**。自動更新需要更新伺服器與版本 endpoint，與「不架 server」的 local-first 原則衝突；installer（Inno/NSIS）＋程式碼簽章屬額外發行基建，目前以「下載 zip、解壓即用」的 onedir 發行足夠。未來若有需求再評估 portable installer（不含線上更新）。
- **使用者資料 / 暫存檔位置**：**決定不引入**。工具不寫隱藏使用者資料；所有輸出由使用者以 `-o`（CLI）或存檔對話框（GUI）指定路徑；打包用 onedir，`_MEIPASS` 為持久路徑，無 onefile 臨時檔問題。故無需額外的 user-data 目錄設計。

## 2026-07-07：UI 收斂成一套（pywebview，v0.5.0）

原本核心邏輯有兩套實作：Python（CLI＋tkinter GUI）與 JavaScript（HTML app 自己做切圖/去背/ZIP/prompt）。這是 despill parity bug、以及每次改動要手動同步兩份（如 SUGGESTIONS）的根源。

決策：**桌面 GUI 改用 pywebview 原生視窗載入 `app/index.html`，前端只做 UI，切圖/去背/匯出/prompt/資料全透過 `webapi.Api` bridge 呼叫 Python core。** 砍掉 tkinter `gui.py` 實作與 JS 的平行演算法。CLI 不變。

依據與取捨：

- 一個 Python core = 單一事實來源，parity 問題根除；JS 從 ~660 行的完整實作縮成純 UI。
- 相依：`pywebview`（Windows 用系統內建 WebView2，Win10/11 預裝）。已驗證 Python 3.14 可裝可跑。
- 取捨：**放棄「純瀏覽器離線開 index.html」的能力**——前端現在需要 pywebview bridge，直接用 file:// 開會顯示「請用 sticker-forge.exe 開啟」。移除了 CLI `app` 指令與 `app_launcher.open_local_app`。
- 驗證：`webapi.Api` 全 unit test（36 passed）＋實際驅動 pywebview 視窗確認 bootstrap/prompt/split/locale 端到端可用；exe 打包後的視窗需在 Windows 桌面實跑確認。
- pywebview 選型見上一則 GUI 決策（主人 2026-07-07 指示「收斂成一套，直接做」）。

## 2026-07-07：v0.6.0 GUI 細節與「已決定不做」再評估

新增（GUI，webview HTML）：

- **單張放大檢視**：點縮圖跳出放大 modal（透明格背景）。
- **單張去背／還原**：modal 內可只對該張去背或還原回原始切圖。每張保留 `raw`（原始切圖），「全部去背」與單張去背都從 `raw` 計算，改去背強度重跑不疊加髒邊。
- 實測：live pywebview drive + 像素驗證（raw 角落 alpha 255 → 單張去背 0 → 還原 255）。

「已決定不做」再評估結果：

- **tkinter GUI 拖放** → **需求消失**。GUI 已是 webview，HTML dropzone 拖放已內建（v0.3.0 做的），桌面版直接有。
- **使用者資料／暫存目錄** → **以 `private_mode` 處理**。WebView2 一定要 profile 資料夾，改用 pywebview `private_mode=True`（臨時 profile、離開清除），不寫持久隱藏資料，符合原則。取捨：UI 語言偏好不跨啟動記憶（可接受）。
- **自動更新** → **維持不做**。需更新伺服器，違反 local-first。
- **installer** → **維持不做**。可下載 zip 解壓即用（portable、免安裝、免管理員），比 Inno/NSIS 安裝流程更符合 local-first；未來真有需求再評估不含線上更新的 portable installer。

## 2026-07-07：多平台匯出（v0.7.0）＋參考來源功能盤點

參考 fork 來源與 README 列的其他專案（sticker-convert、StampNyaa、signal-sticker-tool、LINE Creators Market），把候選功能寫進 README 路線圖「參考來源啟發的候選功能」，並先實作最強、最 local-first 的一項：

- **多平台匯出**：`exporter.PLATFORM_SPECS` + `export_platform_zip()`，支援 Telegram（512 PNG）、WhatsApp（512 WebP＋96 tray）、Discord（320 PNG）、Signal（512 PNG）。CLI `platform --target`、`webapi.Api.export_platform`、GUI 平台下拉＋按鈕。全部 contain-fit 到目標尺寸、保留透明。
- 驗證：核心 unit test（4 平台檔名/尺寸/格式/tray）＋CLI test＋webapi bridge test＋live pywebview（按鈕收集 included tiles 呼叫 bridge）。41 passed。
- 候選未做（留路線圖）：更大 LINE 套組（多 grid）、自選 main/tab、貼圖排序/命名、更多 prompt 模板、Signal manifest、ML 去背（rembg 相依重）、grid 歷史（與 private_mode 不寫持久資料衝突）。

## 2026-07-07：LINE 套組組合（v0.8.0）

修正 README 第一段與 GitHub About（原只寫 LINE，已改為「LINE 及多平台」）。再從候選清單挑「值得做」的一批實作（pack composition）：

- **可變 LINE 套組 8/16/24/32/40**：`exporter.LINE_PACK_SIZES`；`export_line_zip` 接受這些張數並可指定 `main_index`/`tab_index`；`validate_line_zip` 依實際 NN.png 數自動判斷套組大小。
- **多張 grid 累積**：GUI「加入 grid」把每張 3×3 的 9 格 append 進貼圖池；CLI `export` 改 `nargs='+'` 多檔輸入，`--select` 編號跨 grid 連續累加。
- **自選 main/tab**：CLI `--main`/`--tab`（1-based，指向選取中的第幾張）；GUI 兩個下拉；bridge `mainIndex`/`tabIndex`。
- **貼圖排序**：GUI 每張 ▲▼；輸出順序＝貼圖列表順序中的 included 子集。
- 驗證：核心/CLI/webapi unit test（含 16 張套組、main/tab、多 grid）＋ live pywebview（import→9、加 grid→18、選 16、main/tab 下拉、▲▼、清空、export 帶 main/tab）。43 passed。
- 「值得做就全做」的判斷：**做**了 pack composition（上述）；**傾向不做並記錄理由**——ML 去背（首次下載模型破壞離線＋相依重）、grid 歷史（需持久儲存，與 private_mode 衝突）、animated（超出靜態範圍）；**留候選**——更多 prompt 模板（LINE emoji，需模板選擇機制，另開一次做）、Signal manifest。
