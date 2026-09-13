# Decisions

## 2026-08-23（補）：PR 水位改記 #76——上一輪只查了 open

**決定**：`reviewed_pr_through` 由 0 改為 76。

**理由**：上一輪盤點寫「0 個 open PR」，那是對的，但問錯了問題——只查 `--state open` 看不到
已關閉的項目。`--state all` 顯示上游共 **55 個 PR、最大編號 #76，全部 merged**，沒有任何
「未合併就關閉」的 PR。已合併的 PR 都會變成 `main` 的 commit，而 commit 水位 `1c5d448` 正是
`upstream/main` 的 tip，所以這 55 筆全部落在已審過的 commit 範圍內，不需要另外逐筆讀。

**判準補一條**：PR 與 issue 一律用 `--state all` 查。未合併就關閉的 PR 永遠不會進 commit
清單，而那類項目（上游拒收但對本 fork 可能有價值的修正）只有查 PR 才看得到。

## 2026-08-23：複查上游，維持原結論

**決定**：`reviewed_date` 推進到 2026-08-23，`reviewed_through` 不動。

**理由**：`1c5d448` 之後上游 `main` **0 個新 commit**；open PR 仍為 0、open issue 最大仍是 #62，
兩者都未越過水位；3 條分支中帶獨佔 commit 的仍是 `feat/credits-redeem` 與 `fix/selfhost-fonts`
兩條，內容未變（見本檔末「附：上游分支」）。今天重跑 `grep -rn "fonts.googleapis\|fonts.gstatic"`
再次確認本 repo 零命中，`fix/selfhost-fonts` 沒有可移植的目標依然成立。

## 2026-08-22：續審上游 515fe98 之後的 5 個 commit——全數不採用

**決定**：`reviewed_through` 推進到 `1c5d448`。五個 commit 全部落在 PWA shell、SEO 與店面素材
（manifest、robots/sitemap、canonical、service worker 版本、截圖 webp），本 fork 是 Windows
桌面 Python 工具，沒有對應層，全數不採用。

**順帶修掉一個誤報**：`1c5d448` 原本被分類器判為「需要審查」，只因為它的截圖 `.webp` 放在
repo 根目錄而不是 `assets/`。分類器補上副檔名規則（`.webp`／`.avif`），下次上游把素材丟在
哪裡都不會再誤報——規則綁的是檔案性質，不是它剛好被放在哪個資料夾。

## 2026-08-22：上游 PR／issue 盤點——沒有可引用的項目

**決定**：盤點上游 `yazelin/line-sticker-studio` 當時的 **0 個 open PR、2 個 open issue、3 個分支**，
沒有引用任何項目。水位記進 `tools/upstream_baseline.json`（PR 0、issue #62），之後只看更大的編號。

**理由**：兩個 issue（[#59](https://github.com/yazelin/line-sticker-studio/issues/59) MVP 收費上線、
[#62](https://github.com/yazelin/line-sticker-studio/issues/62) Shopline 收款自動發兌換碼）都是上游
把免費工具轉成收費產品的商業化路線：額度包、兌換碼、金流 webhook、共用它自己的後端。本 fork 的
定位是**本機生產流程**（Windows-first，把 AI 圖轉成 LINE 貼圖包），沒有計費、沒有後端、不收款，
這條線整段不適用，也不該被它牽動輸出契約。

上游沒有 open PR；分支都是它自己的工作線。

## 2026-08-09：GUI 進階 tune 滑桿（先前暫緩，重新評估後實作）

- 先前以「避免一次加太多旋鈕」暫緩。重新評估後翻案，決定性的理由是：v0.20.0
  移植的 `make_chroma_tune()` 與漸層去溢色**在出貨的 exe 裡完全碰不到**——CLI 與
  GUI 都只吃 preset 名稱，自訂 profile 只有 Python API 進得去。等於把程式碼打包
  進 binary 卻沒有任何使用者路徑，那才是真正的浪費。
- 另一個理由是四個 preset 只是 5 維參數空間的四個點，而 AI 生圖背景差異極大；
  「背景沒清乾淨」與「角色邊緣被吃掉」正是 preset 調不到的兩種失敗。
- **降低誤用風險的設計**：面板 `<details>` 預設收合、且要另外勾「使用自訂參數」
  才生效（兩道關），預設輸出完全不變；提供「重設為目前強度」；`soft > hard`
  會自動夾住（否則 alpha 漸層反向）。
- **滑桿預設值由 `bootstrap().tuneProfiles` 從 Python core 取得**，preset 數值仍
  只定義在 `spec`，不在 JS 複製第二份。
- **CLI 維持只吃 preset**：CLI 的價值在可重現的腳本化，逐張視覺微調本來就該在
  GUI 做（上游也是把滑桿放在 tile editor）。若日後真有腳本化需求再加單一
  `--tune-json` 逃生口，不要加六個旗標。
- 驗證：同一張霧狀綠幕，preset `balanced` 保留 14.0%、寬鬆自訂 12.9%（清掉霧霾）、
  保守自訂 34.6%（保邊緣）——確實是 preset 到不了的範圍。

## 2026-08-09：上游更新改為自動排程檢查；移植白色描邊

- 先前只有人工 `git fetch upstream`，實際上就是「想到才看」。改為
  `.github/workflows/upstream-check.yml` 每週一自動跑。
- **檢查器刻意不判斷該不該移植**：上游與本 repo 無共同 git history，永遠不可能
  直接 merge，能拿的只有概念與修正，這種判斷需要人。因此工具只回答「有沒有沒
  看過的 commit」，並在有待 review 時讓 workflow 失敗；已看過的進度存在
  `tools/upstream_baseline.json`。全部落在 Worker／PWA shell／行銷素材（本專案
  依規則不可能有）的 commit 歸為 known-irrelevant 以降雜訊，但仍列出。
- **移植 `applyOutlineAndShadow`**：白色描邊是聊天貼圖經典外觀，也解決深色角色
  在 LINE 深色主題下看不清的問題。我方原本只在 prompt 裡請 AI「畫白色描邊」，
  生圖模型不保證照做——改成本機後製才可靠。以 Pillow `MaxFilter`／`BoxBlur`
  對應上游的可分離 box dilation／blur，常數（7px 描邊、2px 羽化、位移 2,3、
  陰影上限 alpha 70）沿用上游以維持一致外觀。預設 `none`，不改變既有輸出。
- **仍未移植且判定不值得**：上游的 `console.log` 統計（除錯用）、`fitWithPadding`
  （我方 exporter 已有等價 padding 邏輯）。GUI 進階 tune 滑桿暫緩——自訂 profile
  已可由 Python API 使用，先確認四個 preset 是否夠用，避免一次加太多旋鈕。

## 2026-08-09：移植上游 chroma tune 系統（strict／continuous＋erode＋自訂 profile）

- 重新評估上游 JS tune 系統後判定**確實比我方完整**，因此整套移植，而非只取 gating。
- 比對發現我方四個數值 preset 與上游**完全相同**（safe 0.32/0.12/60/100/1.9、
  balanced 0.25/0.05/50/110/1.7、aggressive 0.20/0.04/40/125/1.45）；缺的是
  **結構**：`mode`、`erode`、`continuous` preset 與自訂 profile。
- **`continuous` 是真正的能力補強**：`strict` 只對通過 pure-key 測試的像素去背，
  遇到 AI 生圖常見的「帶光暈／褪色的不純綠幕」會整片保留 → 正是 LINE 退件主因。
  已用合成圖驗證：hazy 綠幕在 `balanced` 下殘留一塊灰色三角（kept 20%），
  `continuous` 與 `aggressive` 清乾淨（kept 19%）。
- **`despillStrength` 的真相**：上游公式 `1 - 0.35 * conservativeNorm` 中，
  `conservativeNorm` 只在 `customTune`（物件）時非 0，四個 preset 一律得 1.0
  ——**對 preset 而言與舊的硬去溢色完全等價**。所以「移植漸層去溢色」必然要
  一併實作自訂 profile，否則是死碼。已一併實作 `make_chroma_tune()`。
- **順帶修掉一個我方獨有的 bug**：原本 partial-alpha 分支直接覆寫 alpha，
  忽略來源透明度；半透明來源（APNG 影格）會被去背變得**更不透明**。改為
  `key_alpha × 來源 alpha` 合成（上游一直是這樣）。
- **未移植**：上游的 `console.log` 統計、`applyOutlineAndShadow`、
  `fitWithPadding`（我方 exporter 已有等價 padding 邏輯）與 GUI 進階滑桿 UI。
  自訂 profile 目前只開放 Python API，CLI／GUI 仍只給 preset——先確認 preset
  夠用再決定要不要加滑桿，避免一次塞太多旋鈕。

## 2026-08-08：上游 `line-sticker-studio` 更新評估與選擇性移植

- 本專案**沒有**針對上游 fork（`yazelin/line-sticker-studio`）的自動排程檢查；
  `.github/workflows/` 的 Dependabot／freshness 只追 PyPI 直接依賴，不追上游
  commit。上游更新以人工 `git fetch upstream` + 逐 commit 評估處理。
- 逐一評估 2026-07-11（移除 vendored 上游後）至 2026-08-07 的上游新 commit，
  結論多數不適用 local-first Python 架構：PWA／字型自架、promo-footer／BMC
  抖內、OG 圖、campaigns、預付額度＋兌換碼（明確禁止的 hosted backend）、
  Cloudflare worker prompt 皆 N/A。
- 兩項看似相關但**本專案已正確、無需移植**：(1) 無字模式短語外洩（上游
  `67b6975`）——我方 `## 無字版` 模板本就以 `動作：{action_N}` 驅動、零引號短語；
  (2) 售價／審核天數／AI 勾選文案（上游 tutorial 修正）——我方 `LINE_SUBMISSION.md`
  刻意不寫死價格與審核天數，無過期宣稱。
- **唯一移植項**：上游 `1b94d69`「strict chroma removal」的 despill gating。
  我方 `cleanup.py` 原本對每個保留像素無條件 despill（比上游舊碼還寬鬆——上游
  一直是 `if pureKey` 才 despill），使藍／紅等非 key 前景被硬拉通道。改為只對
  `_key_score > 0` 的偏 key 像素去溢色。**未**移植上游 `despillStrength`／
  strict-vs-continuous matte 的漸層重構——那與其 JS tune 系統耦合，對我方較簡單
  的模型屬過度設計；gating 已解決前景失真主因。以合成圖 old/new 目視 + 像素差
  驗證（藍 30,60,220 / 紅 220,40,40 前景保色，背景仍去除）。

## 2026-07-28：依賴維護採風險分類與 guarded merge

- 每週由 Dependabot 檢查 pip 與 GitHub Actions，每月由 freshness workflow
  比較 `pyproject.toml` 直接依賴與 PyPI，避免只等實際故障才發現版本落後。
- push／PR 由 Python 3.11–3.14 pytest 與 Windows PyInstaller build／smoke
  作為更新門檻。
- `pytest`、`packaging`、`setuptools`、`wheel` 與 GitHub Actions minor／patch
  可在 trusted-base 分類、綁定目前 head SHA 的政策 check、完整 CI 與序列化
  rebase gate 全部通過後自動核准並 squash merge。
- Pillow、pywebview、PyInstaller 會影響圖片、GUI 或 Windows exe；這三項、
  未知依賴／檔案範圍與所有 major 更新一律人工審查。
- GitHub Issues 維持關閉；需要維護時以 Dependabot PR、失敗的 freshness run
  與 Actions summary 通知，不新增 tracker issue。

## 2026-07-26：Windows／Computer Use 驗收與語系啟動

- Windows Release 不能只用 pytest、PyInstaller 或 `--smoke` 判定完成；新增
  `docs/WINDOWS_VALIDATION.md`，把 source、local build、GitHub Release 資產、
  Computer Use GUI 與 LINE Creators Market 平台證據分開記錄。
- Computer Use 只做受監督的桌面操作；視窗 id、accessibility index、座標與檔案
  對話框焦點每一步重新取得，不建立盲目重播巨集。
- LINE 登入、OTP、CAPTCHA、安全提示與最終送審由維護者操作；上傳前再次確認
  非侵權抽驗包與目標帳號。
- `v0.18.0` 實機發現 `--lang en` 被前端繁中預設值覆蓋。`f2fdbee`
  改由 Python bridge 的 initial locale 決定啟動語系，並讓匯出 actions 自動換行。
- 語系偏好不跨啟動保存；GUI 使用 WebView2 `private_mode`，每次啟動由
  `--lang zh-Hant|en` 決定初始值，啟動後仍可在介面內切換。

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
- 本機 HTML 工作台提供語言選單；初始語系由 `--lang` 與 Python bridge 決定。
- prompt template 維持中英文各一份，全部打包進 PyInstaller bundle。
- README 維持繁體中文主入口，另建 `README.en.md`。

## 2026-07-06：Windows exe 入口策略

決定主程式改為原生 GUI，不再讓使用者雙擊 console CLI。此節的 tkinter 實作已於 2026-07-07 的 v0.5.0 決策被 pywebview GUI 取代；保留本節作歷史脈絡。

決策：

- `sticker-forge.exe` 是無 console 的 GUI 主程式。
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
- **Legacy 清理**：移除當時保留的 legacy Worker（Cloudflare/Gemini/Turnstile/quota 後端，明確禁止項）與 campaign-checker（CI workflow＋script）。當時暫保留 upstream UI 與 assets 作 provenance 與邏輯參考；後續已於 2026-07-11 移除，不再 vendored。
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
- pywebview 選型見上一則 GUI 決策（維護者 2026-07-07 指示「收斂成一套，直接做」）。

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

參考 fork 來源與文件列出的其他專案（sticker-convert、StampNyaa、signal-sticker-tool、LINE Creators Market），當時把候選功能寫進入口文件；後續版本細節已收斂到根目錄 `CHANGELOG.md`，README 只保留簡化路線圖。v0.7.0 先實作最強、最 local-first 的一項：

- **多平台匯出**：`exporter.PLATFORM_SPECS` + `export_platform_zip()`，支援 Telegram（512 PNG）、WhatsApp（512 WebP＋96 tray）、Discord（320 PNG）、Signal（512 PNG）。CLI `platform --target`、`webapi.Api.export_platform`、GUI 平台下拉＋按鈕。全部 contain-fit 到目標尺寸、保留透明。
- 驗證：核心 unit test（4 平台檔名/尺寸/格式/tray）＋CLI test＋webapi bridge test＋live pywebview（按鈕收集 included tiles 呼叫 bridge）。41 passed。
- 候選未做（當時留待後續版本評估）：更大 LINE 套組（多 grid）、自選 main/tab、貼圖排序/命名、更多 prompt 模板、Signal manifest、ML 去背（rembg 相依重）、grid 歷史（與 private_mode 不寫持久資料衝突）。

## 2026-07-07：LINE 套組組合（v0.8.0）

修正 README 第一段與 GitHub About（原只寫 LINE，已改為「LINE 及多平台」）。再從候選清單挑「值得做」的一批實作（pack composition）：

- **可變 LINE 套組 8/16/24/32/40**：`exporter.LINE_PACK_SIZES`；`export_line_zip` 接受這些張數並可指定 `main_index`/`tab_index`；`validate_line_zip` 依實際 NN.png 數自動判斷套組大小。
- **多張 grid 累積**：GUI「加入 grid」把每張 3×3 的 9 格 append 進貼圖池；CLI `export` 改 `nargs='+'` 多檔輸入，`--select` 編號跨 grid 連續累加。
- **自選 main/tab**：CLI `--main`/`--tab`（1-based，指向選取中的第幾張）；GUI 兩個下拉；bridge `mainIndex`/`tabIndex`。
- **貼圖排序**：GUI 每張 ▲▼；輸出順序＝貼圖列表順序中的 included 子集。
- 驗證：核心/CLI/webapi unit test（含 16 張套組、main/tab、多 grid）＋ live pywebview（import→9、加 grid→18、選 16、main/tab 下拉、▲▼、清空、export 帶 main/tab）。43 passed。
- 「值得做就全做」的判斷：**做**了 pack composition（上述）；**傾向不做並記錄理由**——ML 去背（首次下載模型破壞離線＋相依重）、grid 歷史（需持久儲存，與 private_mode 衝突）、animated（超出靜態範圍）；**留候選**——更多 prompt 模板（LINE emoji，需模板選擇機制，另開一次做）、Signal manifest。

## 2026-07-07：主題預設包＋套組標題／作者（v0.9.0）

繼續清「可做但還沒完成」的候選：

- **主題預設包（其他主題模板）**：`prompts.PROMPT_PRESETS`（中英各 4 組：healing-bear／office-cat／couple-bears／festive），一鍵填入角色／主題／語氣／風格／語言＋8 文字＋8 動作。CLI `prompt --preset <key>`（其他旗標仍可覆寫，欄位預設改 None 讓 preset 生效）；webapi bootstrap 帶 presets；GUI 下拉套用。
- **套組標題／作者（GUI）**：GUI 補 title/author 輸入，經 bridge 傳進 `export_line_zip`（CLI 早有 `--title/--author`）。這是「命名」候選的可行部分；**單張命名不做**——LINE 檔名固定 01..NN，對輸出無效果。
- 驗證：unit（preset 結構、CLI --preset、bootstrap presets、title/author 寫入 README）＋live pywebview（下拉套用填欄位/prompt、export 帶 title/author）。47 passed。
- **LINE emoji／訊息貼圖仍留候選**：需先查證 LINE emoji 正確 ZIP/尺寸規格（180×180、獨立送審）再實作，不憑記憶捏規格（不模擬原則）。

## 2026-07-07：LINE 原創貼圖 emoji（v0.10.0）

先用 firecrawl 查證官方規格（creator.line.me/en/guideline/emoji/ 與 /detail/）再實作，不捏規格：

- **Regular Emoji：8–40 張、180×180 PNG 透明、檔名 `001.png`…`0NN.png`（3 位數）、Chat Thumbnail Icon 96×74（另欄上傳）、ZIP <20MB。**
- 實作：`exporter.export_emoji_zip`（001..0NN.png 180×180 ＋ `chat-thumbnail.png` 96×74 ＋ README 說明手動上架）、`validate_emoji_zip`（數量 8–40、3 位數連號、尺寸、透明）。CLI `emoji`（多 grid、`--select` 8–40、`--thumb`）、`validate --emoji`；webapi `Api.export_emoji`；GUI「匯出 LINE emoji」按鈕（主圖下拉當縮圖、8–40 gating）。
- 驗證：unit（結構/尺寸/縮圖/validate/拒絕<8）＋CLI（emoji＋validate --emoji）＋live pywebview（按鈕呼叫 bridge、7 張被擋）。51 passed。chat thumbnail 放進 ZIP 但 ZIP 內說明會標註於「聊天縮圖」欄另傳（emoji ZIP 官方檔名表只列 001..NN，不含縮圖檔名，故不假設縮圖在同一 ZIP 上傳）。
- 仍留候選：訊息貼圖（editable-text，需另一套版位規格）。

## 2026-07-07：LINE 訊息貼圖（v0.11.0）＋動態貼圖規格查證

先查證官方規格再做：

- **訊息貼圖**（creator.line.me/en/guideline/messagesticker/）：**8／16／24 張**、貼圖 max 370×320、main 240×240、tab 96×74、PNG 透明、**不需留邊（LINE 自動加邊）→ padding 0**。結構同一般貼圖（main/tab/NN），差別是張數 8/16/24＋padding 0＋送審類型。實作把 `export_line_zip` 參數化（`pack_sizes`、`readme`），`export_message_zip` 復用它（padding 0 spec、訊息貼圖 README）。CLI `message`（多 grid、`--select` 8/16/24、`--main/--tab`）、webapi `Api.export_message`、GUI「匯出訊息貼圖」按鈕。文字位置/字型於 LINE 編輯器設定，不在 ZIP。驗證：unit（結構/validate/拒絕 32）＋CLI＋live pywebview（8 張呼叫、7 張被擋）。55 passed。

- **動態貼圖再評估**（creator.line.me/en/guideline/animationsticker/，維護者問「最小 8 張是否可申請」）：查證結果 quantity 最小 **8（成立）**，但每張是 **APNG、5–20 影格、≤320×270、loop 4000ms**。→ **「最小 8 張」不是卡點；卡點是每張需 5–20 影格動畫，而本工具產靜態圖。** 要做動態貼圖必須「程序化動畫」（給靜圖套內建循環效果生成影格，Pillow 可寫 APNG）或改支援動畫來源匯入。這是設計取捨（canned 效果可能是 gimmick），待與維護者確認方向再做，不硬上。DECISIONS 依維護者指示可改，但實作卡在「動畫內容從何來」。

## 2026-07-07：LINE 動態貼圖 CLI（v0.12.0）

維護者選「匯入動畫來源」。先查證完整官方規格（creator.line.me/en/guideline/animationsticker/）：貼圖 **8/16/24、≤320×270、APNG、每格 5–20 影格、一邊 ≥270、loop 1–4 次總長 ≤4 秒**；**main 240×240 也是 APNG（動畫）**，**tab 96×74 靜態 PNG**；**所有影格相同會被拒**。

實作（採「動態 3×3 grid」輸入，最貼合本工具、重用切圖管線）：

- `splitter.split_animated_grid`：讀動態 grid（GIF/APNG）逐影格 `split_grid`，轉置成每格的 frame stack ＋ 保留來源 frame 時間。
- `exporter.export_animated_zip`：每格 frames 逐格去背後 contain-resize 到 ≤320×270（**會放大小圖，確保一邊 ≥270**，非 thumbnail 只縮小）、寫 APNG（loop 依 4000ms/一輪算 1–4）、main 為動畫 APNG、tab 為第一格靜態 PNG。常數 `LINE_ANIM_*`。
- CLI `animated`（**單一動態 grid → 8 張**；`--main/--tab`、去背選項）。
- 驗證：unit（split→去背→APNG，`is_animated`/`n_frames`/尺寸一邊≥270≤320；拒絕 <5 影格）＋CLI＋小圖放大/大圖縮小尺寸實測。58 passed。

**範圍**：v0.12.0 **CLI-only**。GUI 動畫匯入/預覽（APNG 在 webview 可動，但要避免和現有靜態 tile UI 糾纏，需獨立 flow）＋16/24（多 grid）為下一增量。若維護者其實想要「多個 GIF 各一張」的輸入形狀，看成品再調整。

## 2026-07-07：動態貼圖改「匯入多個 GIF」＋GUI（v0.13.0）

**維護者指正**：非專業使用者用 AI 生圖，結果是**每張一個動態 GIF**（一次生一個主體），不是「動態 3×3 grid」（那是專業/罕見產物）。v0.12.0 的 grid 輸入模型錯了。→ 改為**匯入多個動態 GIF/APNG（每個檔＝一張動態貼圖）**。這也順解 16/24（匯入更多檔即可，不用多 grid）。

- `splitter.split_animated_grid` 換成 `load_animated_frames(source)`（讀單一動態檔→影格＋時間）。`export_animated_zip` 的 `durations` 改成每張各自的時間 list（不同檔可不同影格數）。
- CLI `animated` 改 `nargs='+'`（8/16/24 個檔）、去 `--select`、`--main/--tab` 指向檔。
- GUI：新增「匯入動態貼圖」（多檔 input）→ `Api.prepare_animated`（逐格去背＋resize＋轉 APNG 回傳預覽 dataURL）→ 動態 tile（webview 直接動）；「匯出動態貼圖」→ `Api.export_animated`（decode APNG→frames→export）。新增 `state.mode='static'|'animated'`：動態模式擋掉靜態匯出（ZIP/emoji/message/platform/PNG/去背），並在切一般 grid 時切回 static。
- 驗證：unit（8 檔→APNG、拒絕 <5 影格）＋CLI（多檔）＋**live pywebview**（注入 8 個 APNG File→prepare→8 動態 tile、靜態匯出被擋、export_animated 帶 8＋main/tab）。58 passed。
- 教訓：**輸入/輸出形狀要從「真實使用者手上有什麼」反推**，別預設專業產物。

## 2026-07-11：移除 upstream vendored reference source

確認 `src/`、`app/`、`packaging/`、`tests/` 與 `pyproject.toml` 都沒有引用 upstream reference 目錄後，決定刪除該目錄。

理由：

- 目前產品已收斂為 Python core + pywebview GUI，原 upstream web app / Worker 不再是可維護架構的一部分。
- 後續若需要查原始來源，可看 git history 或外部 `yazelin/line-sticker-studio`，不需要在 repo 內保留一份會過期的舊碼。
- 留下 stale upstream source 容易讓後續維護者或 agent 誤以為可直接沿用舊 web / Worker 方向，與 local-first 邊界衝突。

保留：

- 根目錄 MIT `LICENSE`。
- `NOTICE.md` 的 `yazelin/line-sticker-studio` attribution。
- README / docs 中對 fork 來源與設計啟發的外部連結。

## 2026-07-12：Signal manifest pack（v0.15.0）

依 README 簡化路線圖補齊 Signal 多平台匯出。Signal 官方支援文件（https://support.signal.org/hc/en-us/articles/360031836512-Stickers）列出的重點是：貼圖為獨立 PNG/WebP、512x512、透明背景、每張指定 emoji、最多 200 張、封面 512x512、title 與 author。`sticker-forge` 維持 local-first，因此不做 Signal 上傳、不串 Signal 伺服器，只輸出可人工匯入 Signal Desktop 的本機素材包。

實作：

- `platform --target signal` 維持輸出 `01.png...`，並新增 `cover.png` 與 `signal_manifest.json`。
- manifest 內容含 `title`、`author`、`cover`、每張貼圖 `file` 與 `emoji`。
- CLI `platform` 新增 `--title`、`--author`、`--emoji`；GUI 多平台匯出沿用套組標題與作者欄位。
- `validate --signal` 檢查 manifest、cover、貼圖尺寸、格式、透明背景、emoji 指派與 manifest/ZIP 一致性。

邊界：

- 不產生 Signal 分享連結。
- 不上傳貼圖到 Signal server。
- 不處理 Signal Desktop 或手機端自動操作。

## 2026-07-12：LINE Big Stickers（v0.16.0）

依 README 簡化路線圖查證 LINE Big Stickers。官方 guideline（https://creator.line.me/en/guideline/bigsticker/）列出的 Big Sticker 圖片需求是：main 240x240、貼圖 8/16/24/32/40 張、貼圖尺寸最小 80x524、最大 396x660、chat thumbnail 96x74、PNG、透明背景。Big Stickers 仍是靜態 PNG 套組，不需要 APNG pipeline，因此可直接在現有 Python core 上新增獨立匯出。

實作：

- `export_big_zip()` 以 396x660 canvas 輸出 numbered PNGs、`main.png`、`tab.png` 與 README。
- CLI 新增 `big` 指令；GUI 新增「匯出 Big Stickers」按鈕。
- `validate --big` 用 LINE Big Stickers 尺寸檢查 ZIP。

邊界：

- 不把 Big Stickers 混進一般 `export`，避免 370x320 靜態貼圖與 396x660 Big Stickers 混淆。
- 不宣稱已通過 LINE 審核；仍需手動上傳抽驗。
- Pop-up / effect stickers 是 APNG 全螢幕動畫，留待下一輪獨立實作。

## 2026-07-12：LINE pop-up / effect stickers（v0.17.0）

依 README 簡化路線圖查證 LINE pop-up / effect stickers。官方 guideline（https://creator.line.me/en/guideline/popupsticker/ 與 https://creator.line.me/en/guideline/effectsticker/）列出的共同需求是：main 240x240、靜態貼圖 8/16/24 張且最大 370x320、screen animation 8/16/24 個且最大 480x480 APNG、pop-up/effect main 480x480 APNG、tab 96x74、APNG 5-20 frames、1-3 loops 且總長不超過 3 秒、透明背景。

實作：

- 新增 `export_popup_zip()` 與 `export_effect_zip()`，輸出靜態 numbered PNGs、`popup-01.png...` 或 `effect-01.png...`、`popup-main.png` 或 `effect-main.png`、`main.png`、`tab.png` 與 README。
- APNG screen animation 固定放進 480x480 透明 canvas，符合「寬或高必須剛好 480」與最小邊條件。
- CLI 新增 `popup` / `effect` 指令：使用靜態 3x3 grid 加上 8/16/24 個動態 GIF/APNG，每個動態檔對應一張貼圖。
- `validate --popup` / `validate --effect` 檢查張數、檔名、尺寸、APNG 影格數、透明背景、單檔 1 MB 與 ZIP 結構。

邊界：

- v0.17.0 先做 CLI-first，因為使用者手上的資料形狀是「一張靜態 grid + 多個動態檔」，GUI 流程需要另外整理匯入、預覽與錯誤提示。
- 不宣稱 pop-up / effect 已通過 LINE 審核；仍需以非侵權素材做手動上傳抽驗。
- `v1.0.0` 不在本輪切出。正式版門檻是主要 LINE 類型完成手動上傳抽驗、GUI smoke、Windows exe 發行檢查與文件一致性覆核。

## 2026-07-12：LINE pop-up / effect GUI（v0.18.0）

v0.17.0 已有 pop-up / effect 的核心與 CLI，但一般使用者不應被迫跑命令列。v0.18.0 把同一套 exporter 接進 pywebview GUI。

實作：

- HTML GUI 新增「匯入畫面動畫」、「匯出 pop-up」、「匯出 effect」。
- JS 狀態拆成靜態貼圖池 `tiles` 與畫面動畫池 `screenAnimations`；匯入畫面動畫不切換到一般動態貼圖 mode，也不覆蓋靜態貼圖。
- `webapi.Api` 新增 `prepare_screen_animations()`，把 GIF/APNG 逐格去背並轉成 480x480 APNG 預覽。
- `webapi.Api` 新增 `export_popup()` / `export_effect()`，GUI 與 CLI 共用 `export_popup_zip()` / `export_effect_zip()`。
- GUI 只在選取 8/16/24 張靜態貼圖且畫面動畫數量相同時允許匯出 pop-up / effect。

邊界：

- 不做 LINE 自動送審；匯出後仍由使用者到 LINE Creators Market 手動上傳。
- 不把 pop-up / effect 混進一般「匯出 ZIP」按鈕，避免使用者分不清一般靜態貼圖與 screen animation 類型。
- 仍需用非侵權素材做 LINE 平台端手動上傳抽驗，才能考慮 `v1.0.0`。

## 2026-07-12：LINE 手動上傳抽驗包產生器

`v1.0.0` 的主要未完成門檻是 LINE Creators Market 實際上傳表單抽驗。這件事需要外部帳號與人工操作，不能由 repo 內程式自動完成；但 repo 可以把抽驗材料準備好。

決策：

- 新增 `examples/create_line_trial_packs.py`，用 `examples/create_sample_assets.py` 的非侵權範例圖產生靜態、Big、emoji、訊息、動態、pop-up、effect 的 ZIP。
- 腳本執行後會立即跑本機 validator；動態貼圖目前做基本 APNG 結構檢查，其他類型使用既有 validator。
- 產物放在 `examples/generated/line-trial-packs/`，不進版控。
- 腳本不登入 LINE、不送審、不上傳檔案；只協助人工 smoke test 準備檔案。

邊界：

- 若 LINE 平台端拒絕 APNG 或 ZIP，需把拒絕原因回寫 `REVIEW.md` / `CHANGELOG.md` / 對應 exporter 測試，再修正。
- 沒有平台端抽驗證據前，不切 `v1.0.0`。

### 附：上游分支（2026-08-22 一併比對）

上游 3 個分支，2 個不是 PR head，都逐一比對過：

- `feat/credits-redeem`（ahead 1）：額度／兌換碼的商業化實作，動的是 `app.js`、`index.html`、
  `worker/`——上游是 Web PWA，本 fork 是 Windows 桌面 Python 工具，結構上沒有對應層，且本線不收款。
- `fix/selfhost-fonts`（ahead 1）：把 Google Fonts CDN 換成自架 woff2，動的是 `index.html`、`sw.js`
  與 `assets/fonts/`。**方向與本 fork 的離線優先一致，但本 fork 沒有 PWA 層**（無 `index.html`／
  `sw.js`），`grep` 也確認本 repo 沒有任何 `fonts.googleapis` 引用，因此沒有東西可移植。

## 2026-08-29：上游檢查補上 PR 與 issue 兩個面向

**決定**：`check_upstream_updates.py` 補上以 `--state all` 收集上游 PR／issue 的邏輯，
`upstream-check.yml` 補 `GH_TOKEN: ${{ github.token }}`，新增 `tests/test_upstream_updates.py`。
Baseline 既有的水位不動。

**理由**：`docs/UPSTREAM.md` 早就寫著「四個面向都要看」，`upstream_baseline.json` 也記著
`reviewed_pr_through` 與 `reviewed_issue_through`——但**沒有任何程式讀那兩個欄位**，檢查器只比對
commit 水位。那兩個面向不是「查過沒發現」，是根本沒查，而每週的排程報告長得跟查過一樣綠。
這是艦隊層級的問題：24 個 fork 裡 21 個都這樣（`SanHsien/repo-fleet-ops` 的 `docs/INCIDENTS.md`
第十條）。參考實作是 `SanHsien/harness-guard`。

三個性質，缺一不可：

- **`--state all`**：只查 `open` 看不到「開了又關、沒有合併」的 PR，而那正是「上游拒收、但可能對
  本 fork 有價值」的一類——已合併的遲早會經由 commit 抵達，被關掉的永遠不會。
- **`gh` 失敗時回 `None` 不回 `[]`**，報告寫 `Not checked` 並 **fail closed**（exit 2）。
  「沒查到」和「沒有」在綠色報告裡長得一樣，只有一個是真的。
- **`GH_TOKEN`**：`gh` 在 Actions 裡沒有憑證就列舉不到，配上 fail closed 會讓紅燈的意思變成
  「檢查器壞了」而不是「上游有東西」。

**證據**：落地後實跑 `python tools/check_upstream_updates.py`，三個面向都印出水位與待辦數；
本 repo 的 gate 全綠。

**已知代價**：水位以上真的有東西時，每週的 upstream-check 會回 exit 1。那是它該做的事——先前的
綠燈不是「沒有待辦」，是沒有人看。

**觸發條件**：報告列出項目時逐筆讀 diff、把採用／略過理由寫進本檔，然後才推進 baseline 的水位。

**本 repo 額外一點**：這支檢查器不是用 exit code 表達紅燈，而是寫 `needs_attention` 到
GITHUB_OUTPUT 讓 workflow 判斷。所以 ticket 數要加進 `to_review`，`gh` 列舉不到時要併進
`check_failed`——否則 commit 軸安靜的那幾週，報告照樣是綠的。ticket 沒有 relevant/irrelevant
之分：本 fork 從沒 triage 過，水位以上每一筆都還要人讀。


## 2026-08-30：上游 #77–#80 四筆全部不適用

commit 水位 1c5d448 → 0506621（upstream/main tip）、PR 水位 76 → 80；issue 水位維持 62（實查為空）。
commit 軸上的四筆（4c97c24／4ea049d／446b931／0506621）就是同樣那四個 PR，結論一致，理由在下面。

### 共同的根因：本 fork 沒有 Worker 那一層

上游是「瀏覽器 app + Cloudflare Worker」架構，`app.js` 用 `fetch()` 打自家 Worker，錯誤處理、
Turnstile、配額都在那條線上。**本 fork 不是**：`app/app.js` 第 2 行就寫著
`// Python core via window.pywebview.api (see src/sticker_forge/webapi.py)`，
`grep "fetch(\|https://"` 在該檔 0 命中——它透過 pywebview 直接呼叫本機 Python，沒有 HTTP、
沒有 Worker、沒有 Turnstile。`worker/` 早就列在
`tools/check_upstream_commits.py` 的 `IRRELEVANT_PREFIXES` 裡。

| PR | 上游做了什麼 | 為什麼不適用 |
| --- | --- | --- |
| `#77` | 新增 `errorMessage(resp)`，把 Worker 回的 JSON 錯誤取出那句人話，取不到才退回 HTTP 狀態碼 | 那個函式的參數是 `Response`，整段只在 `fetchGrid` 的 HTTP 路徑上用。本 fork 沒有 HTTP 呼叫，也沒有 `resp.status` 可讀 |
| `#80` | 同一條線的收斂：上游錯誤只留一句話 | 同上 |
| `#78` | README 的部署說明措辭改成「對外 IP 變動」＋ `worker/src/index.js` 註解 | 兩個檔案本 fork 都沒有對應內容；README 是本線自己的版本 |
| `#79` | 撤掉誤提交進 README 的**管理員腳本說明**（`lss-reg`／`lss-code`、`ADMIN_TOKEN` 讀取路徑、Cloudflare D1 查詢） | **實查本 fork README／README.en：0 命中**。那段從來沒有進到本線，沒有東西要撤 |

`#79` 特別查過而不是只看標題——它撤掉的是含管理員 token 讀取路徑的內容，如果本 fork 也有就要
一起清掉。查過確認沒有。

**觸發條件**：本 fork 若哪天加上遠端服務呼叫（目前架構是本機 Python core），`#77`／`#80` 的
「錯誤訊息只給人話、不要把原始 JSON 丟到畫面上」這個做法值得回來取用。
