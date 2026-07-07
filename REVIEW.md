# Project Review 2026-07-07

## 結論

`sticker-forge` 已從上一輪（2026-07-05）的「可接手、不可使用」進到**可用產品**：v0.2.0 具備 CLI、Tkinter GUI、純前端 web app 三條路徑，涵蓋 prompt 產生 → 切圖 → 去背 → LINE ZIP 匯出 → 驗證，28 個測試全過，PyInstaller 打包腳本齊備。方向與 CLAUDE.md/AGENTS.md 的 local-first 定位一致，沒有違反禁令（無 Worker/Turnstile/quota、保留 MIT attribution、不做自動送審）。

但有一個**真實可用性阻斷**：Python 版切圖要求邊長可被 3 整除，導致最常見的 AI 生圖尺寸（1024×1024）在 CLI 與 GUI 直接失敗，而 web 版卻可以。這是下一輪第一優先。

---

## 驗證方式

- `python -m pytest -q` → `28 passed`（exit 0）。
- 實測 `split_grid`：`1024×1024` 拋錯、`1200×1200` 正常（見 P0 證據）。
- 逐檔閱讀 `src/sticker_forge/*.py`、`app/app.js`、`packaging/sticker-forge.spec`。
- `git status` 乾淨，working tree 與 `origin/main` 同步（HEAD `4f4d01a`）。

---

## 主要問題

### P0：Python 切圖對 1024×1024 直接失敗（與 web 版行為不一致）

`splitter.split_grid` 在寬或高不能被 3 整除時 `raise ValueError`：

```
1024x1024 FAIL: image size 1024x1024 is not evenly divisible by 3x3
1200x1200 OK  9
```

- 影響：ChatGPT / Gemini / DALL·E 等預設輸出多為 1024×1024（1024 % 3 = 1）。使用者拿最典型的生圖丟進 **CLI `split`/`export`** 會直接錯誤退出；丟進 **GUI「匯入 3x3」** 會被 `open_grid` 的 try/except 攔下、只跳一個錯誤對話框，使用者不知所措。
- 反差：`app/app.js` 的 `splitGrid()` 用 `Math.floor(naturalWidth/3)` 取整，多餘幾個像素自動忽略，因此 web 版對 1024×1024 正常運作。三條路徑對「同一張圖」給出不同結果，違反 CLAUDE.md「CLI/GUI/web 應等價」的隱含期待。
- 位置：[src/sticker_forge/splitter.py:24-27](src/sticker_forge/splitter.py#L24)。
- 建議：改成向下取整 + 置中裁掉餘數（對齊 JS 行為），或提供 `--allow-crop` 之類的容忍模式；把「不可整除」從硬錯誤降級為預設可處理。務必補一條 1024×1024 的回歸測試。

### P1：`--key-color` 在 export / stickers / preview 是死參數

`cli.py` 對 export/stickers/preview 都提供 `--key-color`，但呼叫 `remove_chroma_background(key_color=..., key_name=args.key_name, ...)` 時，`--key-name` 永遠有預設值 `"green"`（恆為 truthy）。而 `remove_chroma_background` 內只要 `key_name` 有值就走 score-based 分支，**完全忽略 `key_color`**：

- 位置：[src/sticker_forge/cleanup.py:52](src/sticker_forge/cleanup.py#L52)（`if key_name:` 分支）＋ [cli.py:147-148](src/sticker_forge/cli.py#L147)。
- 結果：使用者在 export 傳 `--key-color #123456` 沒有任何效果，也沒有警告。屬於「介面承諾但不實作」的陷阱參數。
- 建議：二選一——(a) 若要支援自訂色，讓 `key_color` 存在時優先於 `key_name`；(b) 若不支援，就從 export/stickers/preview 移除 `--key-color`，避免誤導。

### P1：web 去背缺少 despill，與 Python 版結果不一致

Python `remove_chroma_background` 在保留的像素上會做 `_despill`（抑制邊緣綠/洋紅溢色）；`app/app.js` 的 `chromaKeyCanvas()` 只調整 alpha，**沒有 despill**。

- 位置：[cleanup.py:105-116](src/sticker_forge/cleanup.py#L105) vs [app/app.js:420-440](app/app.js#L420)。
- 影響：同一張圖、同一個 tune profile，web 版留下的貼圖邊緣會有一圈綠邊，Python 版沒有。對主打「本機、跨路徑一致」的產品是品質落差。
- 建議：把 despill 移植到 JS，或在文件明確標註 web 版為「快速預覽、品質以 CLI/GUI 為準」。

### P2：未使用 `--chroma-key` 時，匯出的貼圖底色是實心綠/洋紅

CLI `export`/`stickers` 若不加 `--chroma-key`，`split_grid_to_stickers` 用 `(*key.rgb, 255)` 把每格背景填滿 key 色，之後不去背就直接匯出，成品是實心綠底貼圖。

- 位置：[cli.py:241](src/sticker_forge/cli.py#L241)、[cli.py:261](src/sticker_forge/cli.py#L261)。
- 這在邏輯上「正確」（設計預期使用者會去背），但對只跑一次 export 的人是踩雷點。
- 建議：`export`/`stickers` 預設就做去背，或在 `preview`/輸出訊息提示「尚未去背，成品為實心底色」。

### P2：打包 exe 用 webbrowser 開啟臨時解壓的 HTML 可能有 race

`app` 指令與 GUI 皆以 `webbrowser.open(file_uri)` 開啟 `_MEIPASS` 下解壓的 `app/index.html`。CLI `app` 指令 `open` 完就 return、行程結束，PyInstaller onefile 的臨時目錄可能在瀏覽器載入前被清掉。

- 位置：[app_launcher.py:15-18](src/sticker_forge/app_launcher.py#L15)。
- 建議：實機用打包後的 onefile exe 驗一次 `app` 指令；若會 race，改用 onedir 佈局或把 HTML 寫到穩定路徑再開。

---

## 小問題 / 觀察

- `cleanup.py:45` 的 `hasattr(source, "get_flattened_data")` 不是標準 Pillow API，實務上永遠走 `getdata()` 分支——確認是否為未落地的最佳化殘留，是的話刪掉。
- `cleanup.py:6-7` 有多餘空行；純風格，可略。
- 去背是逐像素 Python 迴圈（370×320×8 張 ≈ 75 萬像素/張），大量匯出時偏慢。目前可接受，未來若要加速可考慮 numpy 向量化（會多一個相依，需權衡 local-first 的輕量原則）。
- `reference/upstream-line-sticker-studio/worker/` 仍在（上一輪 P2）。CLAUDE.md 明訂僅供參考、不得引用；現況也確實無引用，維持即可，不急著刪。

---

## 建議下一輪順序

1. 修 P0：`split_grid` 容忍非整除尺寸 + 補 1024×1024 回歸測試（一次解掉最痛的可用性問題）。
2. 決定 P1（`--key-color`）：支援或移除，二擇一並同步文件。
3. 對齊 P1（web despill）：移植或明確標註差異。
4. 用打包後的 exe 實機走一遍 import→split→cleanup→export→validate，補一份實測紀錄（P2 的 webbrowser race 一併驗）。

## 不做（延續既有禁令）

- 不新增 Cloudflare Worker / Turnstile / quota / Gemini proxy。
- 不提交生成圖、使用者素材、ZIP 或暫存檔。
- 不宣稱 LINE 官方或保證上架、不做自動送審。
- 不移除 MIT 授權與原作者 attribution。
