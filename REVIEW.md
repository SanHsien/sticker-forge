# Project Review 2026-07-07

## 結論

`sticker-forge` v0.2.0 是**可用產品**：CLI、Tkinter GUI、純前端 web 三條路徑涵蓋 prompt 產生 → 切圖 → 去背 → LINE ZIP 匯出 → 驗證，符合 local-first 定位，無違反禁令。本輪 review 找到的三個一致性問題已全部修掉並驗證；打包 exe 也實測可用。

剩下的都是 P2 等級、且多半是「要不要改預設行為」的產品決策，交給主人拍板即可。

---

## 本輪已修（皆有實測證據）

| 項目 | 狀態 | 驗證 |
|------|------|------|
| **P0**：`split_grid` 對 1024×1024 直接失敗 | ✅ 已修 | 改向下取整丟餘數（對齊 web `Math.floor`）；1024² 現可 split/export/validate，打包 exe 也 OK；補回歸測試 |
| **P1**：`--key-color` 在 export/stickers/preview 是死參數 | ✅ 已修 | 從三個指令移除、保留在 cleanup；`export --key-color` 現報錯 exit 2 |
| **P1**：web 去背缺 despill、與 Python 不一致 | ✅ 已修 | 移植 despill 到 `app.js`；Node×Python 60/60 像素交叉比對一致 |
| 附帶：`python -m sticker_forge.cli` 靜默 no-op | ✅ 已修 | 補 `__main__` guard |
| 附帶：打包 exe 實機驗證（roadmap item 4） | ✅ 已驗 | `pyinstaller` build 成功，GUI `--smoke` exit 0、CLI export/validate OK、bundle 含 app/+prompts/ |
| **P2**：未去背時匯出成品是實心底色 | ✅ 已修 | 研究 LINE 官方＋upstream 後，`export`/`stickers`/`preview` 改預設去背，加 `--keep-background` opt-out；補測試（預設→透明、opt-out→實心） |
| 強化：`validate` 未檢查透明背景 | ✅ 已加 | 新增透明度檢查，完全不透明的貼圖被標記（LINE 第一大退件原因）；補測試 |

現況：`python -m pytest -q` → **32 passed**，無 DeprecationWarning。

---

## 仍開放

### P2：去背是逐像素 Python 迴圈

370×320×8 張約 75 萬像素/張，大量匯出偏慢。目前可接受。若要加速可考慮 numpy 向量化，但會多一個相依，與 local-first 輕量原則有取捨——不建議現在做。

### 觀察：webbrowser 開 bundled HTML 的 race —— 非問題

上一版曾懷疑打包 exe 用 `webbrowser.open` 開臨時解壓的 HTML 會有 race。實測釐清：目前 spec 是 **onedir**（`COLLECT` 產生資料夾，`_internal/app/index.html` 為持久路徑），沒有 onefile 的 temp 清理 race。若未來改 `--onefile` 才需重新評估。

---

## 更正上一版 review 的錯誤

上一版把 `cleanup.py` 的 `get_flattened_data` 分支列為「疑似殘留、建議刪」——**這是錯的**。它是 Pillow 14 的前向相容 shim（`Image.getdata()` 將於 2027-10 移除，改用 `get_flattened_data()`）。移除會重新引入 DeprecationWarning 並在 Pillow 14 壞掉。已在原碼加註解，勿刪。

---

## 不做（延續既有禁令）

- 不新增 Cloudflare Worker / Turnstile / quota / Gemini proxy。
- 不提交生成圖、使用者素材、ZIP 或暫存檔。
- 不宣稱 LINE 官方或保證上架、不做自動送審。
- 不移除 MIT 授權與原作者 attribution。
