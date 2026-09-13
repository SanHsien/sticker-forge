# Windows 與 Computer Use 實機驗證

本文件是 `sticker-forge` Windows 可攜版的正式驗收流程。目的不是只確認
pytest 或 PyInstaller 顯示成功，而是證明使用者下載到的 ZIP 可以解壓、啟動，
並在真實桌面完成匯入、切圖、去背、預覽與匯出。

## 判定方式

- `PASS`：本輪實際執行，結果符合預期。
- `FAIL`：本輪實際執行，結果不符合預期；不得發布或宣稱完成。
- `BLOCKED`：缺外部條件、帳號或人工判斷；不得用單元測試代替。
- source、local build、GitHub Release 資產與 LINE Creators Market 分開記錄。
- 每輪記錄 commit、版本、Windows/Python 版本、產物來源、開始時間與結束時間。

## 操作邊界

### AI 可直接完成

- 確認 `HEAD`、`origin/main`、tag 與工作樹狀態。
- 跑 pytest、JavaScript 語法檢查、sample/trial pack generator 與 PyInstaller build。
- 下載 GitHub Release ZIP、核對 SHA-256、解壓、跑 CLI help 與 GUI `--smoke`。
- 使用 Computer Use 啟動本機 GUI，逐步檢查繁中/英文、匯入、切圖、去背、
  選取、排序、預覽、錯誤訊息與取消流程。
- 使用 repo 產生的非侵權素材匯出暫存 ZIP，再用 CLI validator 檢查。

### 需要維護者在旁監督

- Windows SmartScreen、Defender、WebView2 或其他系統提示。
- Computer Use 操作原生檔案對話框時，確認目標路徑與焦點。
- 檢查透明邊緣、字體裁切、動畫播放與整體視覺品質。
- LINE Creators Market 已登入頁面的上傳抽驗。

### 只能由維護者完成

- LINE 登入、密碼、OTP、CAPTCHA 與帳號安全操作。
- 接受 Windows 安全或隱私權限。
- LINE Creators Market 的最終送審、申請販售與上架。
- 刪除 LINE 草稿、作品或其他遠端資料。

本專案不把帳號登入、上傳或送審包成自動化巨集。上傳檔案會把內容傳到 LINE；
執行前必須再次確認目標檔案與帳號。最終送審一律由維護者操作。

## 一、版本與自動化基線

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
python --version
node --check app\app.js
python -m pytest
git diff --check
python examples\create_line_trial_packs.py
```

記錄 pytest 數量、trial pack 七種 ZIP 是否全部為 `OK`。只有在 `HEAD` 與
`origin/main` 的差異已被理解時，才能把結果歸到遠端 `main`。

## 二、本機 Windows build

```powershell
.\packaging\build-windows.ps1
```

預期產物：

```text
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge.exe
%TEMP%\sticker-forge-pyinstaller-dist\sticker-forge\sticker-forge-cli.exe
```

build script 會跑 pytest、PyInstaller、GUI `--smoke` 與 CLI `--help`。這只能證明
程序可啟動，不代表視窗、WebView2、檔案對話框與匯出流程已通過。

## 三、GitHub Release 資產

以下把 `vX.Y.Z` 換成待驗版本：

```powershell
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$VerifyRoot = Join-Path $env:TEMP "sticker-forge-release-verify-vX.Y.Z-$Stamp"
New-Item -ItemType Directory -Path $VerifyRoot | Out-Null

gh release download vX.Y.Z -R SanHsien/sticker-forge `
  -p "sticker-forge-vX.Y.Z-windows-x64.zip" `
  -p "sticker-forge-vX.Y.Z-windows-x64.zip.sha256" `
  -D $VerifyRoot

$Zip = Join-Path $VerifyRoot "sticker-forge-vX.Y.Z-windows-x64.zip"
$Expected = ((Get-Content "$Zip.sha256" -Raw) -split "\s+")[0].ToLowerInvariant()
$Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Zip).Hash.ToLowerInvariant()
if ($Actual -ne $Expected) { throw "SHA-256 mismatch" }

$Extract = Join-Path $VerifyRoot "expanded"
Expand-Archive -LiteralPath $Zip -DestinationPath $Extract
& "$Extract\sticker-forge-cli.exe" --lang en --help

$Smoke = Start-Process -FilePath "$Extract\sticker-forge.exe" `
  -ArgumentList "--smoke" -PassThru -Wait
if ($Smoke.ExitCode -ne 0) { throw "GUI smoke failed: $($Smoke.ExitCode)" }
```

另確認 `_internal\app`、`_internal\prompts`、GUI exe 與 CLI exe 都存在。驗收
GitHub Release 時只能執行這份解壓後資產，不得用 repo source 代替。

## 四、AI 操作 Windows GUI

這是受監督的桌面驗收，不是 CI headless E2E。Computer Use 的視窗 id、
accessibility index、畫面座標與檔案對話框焦點都不是穩定 API。

操作規則：

1. 每輪先列出目前 app/window，只選唯一的 `sticker-forge` 視窗。
2. 每次點擊、輸入、捲動後立即重新擷取畫面；不得重用舊 index 或座標。
3. 原生檔案對話框先確認 `focused_element`，再輸入路徑。
4. 結果不確定時先重新觀察，不得盲目重點或重存，以免覆寫檔案。
5. 測試輸出固定放新的 `%TEMP%` 子目錄，不使用真實作品或私人圖片。
6. 每個狀態轉移保存一項證據：畫面文字、產物路徑、validator 結果或 exit code。

### A. 啟動與語系

1. 雙擊 `sticker-forge.exe`，確認沒有 console 閃現、文字後閃退或背景殘留程序。
2. 確認繁中標題、Prompt、Grid、匯出按鈕與狀態文字可見。
3. 關閉後執行 `sticker-forge.exe --lang en`，確認英文預設值與 prompt 全部生效。
4. 在 GUI 內切回繁中，再切英文，確認欄位、預設文字與 prompt 同步切換。
5. 在一般視窗與最大化視窗確認沒有水平捲軸、按鈕裁切或文字重疊。

### B. 靜態貼圖主流程

1. 先跑 `python examples\create_sample_assets.py`。
2. 匯入 `examples\generated\static-grid.png`。
3. 確認自動切成 9 張、前 8 張已選取、預覽列出 `01.png` 到 `08.png`、
   `main.png` 與 `tab.png`。
4. 執行「去背」，確認狀態顯示完成；放大至少第一、中央、最後一張，目視透明邊緣。
5. 改變去背強度與 padding，確認預覽更新且不破壞版面。
6. 交換貼圖順序、變更主圖/聊天標籤，確認預覽與輸出順序一致。
7. 匯出 LINE ZIP 到 `%TEMP%`，再執行：

```powershell
sticker-forge-cli.exe validate <輸出 ZIP>
```

8. 取消一次儲存對話框，確認狀態顯示「已取消／Cancelled」，程式不閃退。

### C. 大套組與各匯出類型

逐項驗證，不用某一種成功推定其他類型成功：

| 類型 | GUI 操作 | 本機驗證 |
| --- | --- | --- |
| 靜態 16/24/32/40 | 使用「加入 grid」累積並選取 | `validate` |
| Big Stickers | 匯出 Big Stickers | `validate --big` |
| emoji | 匯出 LINE emoji | `validate --emoji` |
| 訊息貼圖 | 匯出訊息貼圖 | 解壓檢查 + trial pack 結果 |
| 動態貼圖 | 匯入 8 個 GIF/APNG，匯出動態貼圖 | 解壓檢查 APNG 影格/尺寸 |
| pop-up | 靜態 8 張 + 8 個畫面動畫 | `validate --popup` |
| effect | 靜態 8 張 + 8 個畫面動畫 | `validate --effect` |
| Signal | 選 Signal 後匯出 | `validate --signal` |
| Telegram/WhatsApp/Discord | 各匯出一次 | 解壓檢查格式與尺寸 |

動態、pop-up、effect 還要目視至少第一張 APNG 能播放，不可只看 ZIP 結構。

### D. 失敗與恢復

- 未匯入素材就按切圖、去背或匯出，應顯示可理解的錯誤。
- 動態檔數量不是 8/16/24 時，匯出應被阻擋。
- pop-up/effect 靜態張數與畫面動畫數不同時，按鈕應停用或顯示錯誤。
- 選擇損壞圖片、錯誤副檔名或無寫入權限路徑時，GUI 應顯示錯誤且不閃退。
- 關閉所有檔案對話框與 GUI 後，確認 `sticker-forge.exe` 沒有殘留。

## 五、LINE Creators Market 手動上傳抽驗

先產生非侵權抽驗包：

```powershell
python examples\create_line_trial_packs.py
```

產物在 `examples\generated\line-trial-packs\`。依序建立草稿並上傳靜態、Big、
emoji、訊息、動態、pop-up、effect。每一類記錄：

- 上傳日期與 LINE 表單類型。
- ZIP 是否被接受；若拒絕，記錄原始錯誤文字。
- main/tab/sticker/APNG 預覽是否正確。
- 動畫播放、循環與畫面範圍是否符合預期。
- 草稿是否保留；若要刪除，先由維護者確認。

只要 APNG 類型還沒有平台接受證據，`v1.0.0` gate 就維持 `BLOCKED`。抽驗成功
也不代表 LINE 保證送審通過；內容、著作權與銷售資訊仍由維護者負責。

## 驗收紀錄模板

```markdown
## vX.Y.Z / commit <sha> / YYYY-MM-DD

| 項目 | 結果 | 證據或阻塞原因 |
| --- | --- | --- |
| pytest / node / diff | PASS | <N> passed；node/diff clean |
| Windows build | PASS | GUI smoke 0；CLI help 0 |
| Release SHA-256 / Expand-Archive | PASS | <sha256> |
| 繁中 GUI | PASS | <觀察> |
| 英文 GUI | PASS | <觀察> |
| 靜態匯入→去背→ZIP | PASS | <path + validator> |
| 動態 / pop-up / effect | PASS/FAIL/BLOCKED | <證據> |
| 去背強度（含 continuous）／進階面板 | PASS/FAIL/BLOCKED | <觀察> |
| 白色描邊 none / simple / fancy | PASS/FAIL/BLOCKED | <觀察> |
| LINE 手動上傳 | PASS/FAIL/BLOCKED | <平台訊息> |
```
