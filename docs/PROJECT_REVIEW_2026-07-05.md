# Project Review 2026-07-05

## 結論

`sticker-forge` 已完成第一步方向收斂：從 upstream 的線上 AI web app，改成 local-first 的 LINE 貼圖製作工具。repo 現在適合作為改寫起點，但還不是可執行產品。

下一輪應優先做 prompt template 與圖片處理核心，而不是繼續整理文件。

## 目前狀態

- `README.md` 已改成本機工具定位。
- 原專案 web frontend / Worker / workflow / assets 已搬到 `reference/upstream-line-sticker-studio/`，保留目錄結構。
- 新增 `src/`、`prompts/`、`packaging/`、`tests/`、`examples/` 骨架。
- 新增 AI 接手文件與授權聲明。
- GitHub repo 已關閉 Issues、Projects、Wiki、Discussions、Actions。

## 主要風險

### P0：目前沒有可執行產品

`src/sticker_forge/` 還只有 README，尚未有 CLI、GUI、圖片處理或 ZIP 匯出程式。使用者現在無法下載工具完成任何本機處理。

處理：下一步直接做最小 CLI，先支援「讀 3x3 圖 -> 切 9 張 -> 匯出資料夾」，再補 ZIP。

### P0：核心邏輯仍在 reference

切圖、chroma-key、ZIP 等可重用邏輯仍在 `reference/upstream-line-sticker-studio/app.js`，尚未抽成可測試模組。

處理：只抽純邏輯，不搬 UI state、Turnstile、quota、Worker API。

### P1：prompt template 尚未成形

目前 `prompts/` 只有資料夾說明。產品的第一個使用者價值應該是產出穩定 prompt。

處理：先建立一份 LINE 靜態貼圖 3x3 prompt template，包含有字版與無字版。

### P1：測試與驗證還沒建立

目前沒有自動測試。未來圖片處理很容易因尺寸、透明背景、padding、檔名而壞掉。

處理：先建立 grid split 與 ZIP 結構測試，測試素材使用簡單合成圖，不放真實或侵權素材。

### P2：reference 內仍有 upstream hosted 設定

`reference/upstream-line-sticker-studio/worker/` 保留了 Cloudflare / Gemini 相關設定。這是參考資料，不應被新架構引用。

處理：等可重用邏輯抽完後，刪除 Worker reference 或保留一份更小的摘錄說明。

## 改作順序

1. `prompts/line-static-3x3.md`：第一版提示詞模板。
2. `src/sticker_forge/splitter.py`：切 3x3 grid。
3. `tests/test_splitter.py`：用合成圖驗證切圖尺寸。
4. `src/sticker_forge/exporter.py`：輸出 LINE ZIP。
5. `tests/test_exporter.py`：驗證 ZIP 結構。
6. 最小 CLI：`python -m sticker_forge ...`。
7. Windows exe 打包。

## 不做

- 不要再新增 Cloudflare Worker、Turnstile、quota、Gemini proxy。
- 不要先做完整 GUI；先把圖片處理核心做穩。
- 不要把生成圖或真實使用者素材放進 repo。
- 不要宣稱能保證 LINE 審核通過。

## Review 後判斷

repo 現在的方向是正確的，但還處於「可接手、不可使用」階段。最短可交付路線是：

```text
prompt template -> grid splitter -> LINE ZIP exporter -> minimal CLI -> exe
```
