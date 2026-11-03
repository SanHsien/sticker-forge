# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-11-03 查的快照，開工前先重查 GitHub。

## 現況

`sticker-forge` 是 Windows-first、local-first 的聊天貼圖工具（Python core＋pywebview GUI＋CLI），是 `yazelin/line-sticker-studio` 的 MIT fork（`AGENTS.md:7,11`）。最近 release 是 v0.23.0（tag 指向 `839aed0`，2026-11-03 發佈，資產經下載驗證），`pyproject.toml:7` 也是 0.23.0。
健康：open PR 0、Dependabot 與 code scanning 告警 0，CI、CodeQL、Dependabot guarded merge、Dependency freshness、Upstream commit check 在 `main` 最近一次皆 success；issues 在 GitHub 上已停用，所以 open issue 數是「未查到」，不是 0（2026-10-29 `gh` 查詢）。
v0.23.0 的 Windows GUI 實機驗收（以 agent-desktop 操作原始碼版 GUI 的按鈕與原生對話框）與 Release 資產驗證紀錄在 `docs/WINDOWS_VALIDATION.md`；LINE Creators Market 手動上傳仍未做，只擋 v1.0.0。上游水位在 commit `1a1e903`、PR 81、issue 62（`tools/upstream_baseline.json`），2026-10-26 的 Upstream commit check 為 success，代表沒有未審項目。

4×4／16 張規格已整合至 CLI／GUI，預設仍為 3×3／8 張；靜態 ZIP 驗證已共用空白與假透明內容啟發式。動態／pop-up／effect 影格數錯誤依 GUI 目前語系顯示。

## 近期：可以直接動手

| 項目 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- |


## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 切 v1.0.0 | `docs/WINDOWS_VALIDATION.md` 第四節 GUI 驗收清單在 `main` 上跑完（2026-11-03 v0.23.0 紀錄裡標 BLOCKED 或未驗的項目：英文 GUI、continuous／進階面板、fancy 描邊、靜態 16–40 張、訊息貼圖、Signal／Telegram／WhatsApp／Discord、動態類目視播放、D 節失敗情境，以及 v0.23.0 之後進 main 的 4×4 規格） | 該版驗收紀錄除「LINE 手動上傳」外皆 PASS；`pyproject.toml`＝tag＝Release；下載資產 SHA-256 與本機 build 相符 | 維運長（GUI 用 agent-desktop，實體點擊等維護者不在電腦前） | 2026-11-03 維護者決定：LINE 實機上傳不影響程式結果，不再擋 v1.0.0 |
| LINE Creators Market 七類型手動上傳抽驗 | 先有一套維護者認可、外觀可上架的正式貼圖（2026-11-03 維護者決定：程式產生的抽驗包太醜，不拿去上傳） | 七類型以正式貼圖上傳為草稿且無退件，結果記入 `docs/WINDOWS_VALIDATION.md` | 維護者 | `docs/LINE_SUBMISSION.md`「手動上傳抽驗包」；`docs/WINDOWS_VALIDATION.md` 第五節 |
| 取得 Dependabot guarded merge 的端到端證據 | Dependabot 提出第一個符合政策的 minor／patch PR（查：`gh pr list --repo SanHsien/sticker-forge --author app/dependabot`） | 該 PR 實際出現 label、綁定 head SHA 的 `Dependabot policy` check、自動核准與 squash merge；把結果寫回 `REVIEW.md` 並刪除該 P2 段落 | Claude Sonnet | `REVIEW.md` P2「guarded merge 尚待第一個真實低風險 Dependabot PR」；`docs/DEVELOPMENT.md:96-100` |
| 審查上游新項目並判斷採用與否 | `Upstream commit check` 週排程（週一）紅燈，代表上游有水位之後的新 commit、PR 或 issue | 依 `docs/DECISIONS.md` 格式新增一筆決定（採用／不採用及理由）；`tools/upstream_baseline.json` 水位推進；採用者先有紅燈測試，`python -m pytest` 綠 | Claude Opus | `tools/upstream_baseline.json`；`.github/workflows/upstream-check.yml:12`；`docs/DECISIONS.md:41,123` 的既有判斷方式 |
| 把自訂幕色 prompt 的 avoid 文字改成依通道列出具體色名 | 實際生圖時發現模型誤用與幕色相近的色相 | 同一組自訂色在修改前後各生一次圖，附對照；prompt 相關測試綠；README／USER_GUIDE 若有該段文字同步 | Claude Sonnet | `b913dd6`；接續開發報告（2026-10-2x）「刻意不做／延後」第一條 |

## 刻意不做

| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 補推本機 v0.1.0–v0.21.0 共 22 個舊 tag 到 GitHub | 這些 tag 的 commit 與 `origin/main` 沒有共同祖先，推上去等於引入與 main 無關的孤兒歷史；版本紀錄已在 `CHANGELOG.md`。此建議來自 2026-10-26 深掃，維護者尚未明確確認 | 維護者明確要求遠端要有完整 tag，並接受孤兒歷史 |
| hosted backend、Cloudflare Worker、Turnstile、quota、Gemini proxy；LINE Creators Market 自動上傳或自動送審；宣稱 LINE 官方或保證過審 | 產品邊界（`AGENTS.md:13-19`、`REVIEW.md` 「不做」段） | 維護者改變產品定位並先更新 `AGENTS.md` |
| 移植上游的 PWA、SEO、Worker、店面與行銷素材 | 本 fork 沒有對應層（pywebview 呼叫本機 Python，沒有 HTTP 也沒有 Worker）；歷次審查結論一致 | 上游出現與本機圖片處理或匯出規格有關的改動時，走上面「審查上游新項目」那一列 |
| CLI 為自訂 tune 加一串旗標 | 逐張視覺微調本來就該在 GUI 做，CLI 的價值在可重現（`REVIEW.md` P2「CLI 無自訂 tune 逃生口」） | 出現腳本化需求時，只加單一 `--tune-json`，不加六個旗標 |

## 維護方式

自有 repo（上游為 `yazelin/line-sticker-studio`），直接推 `main`（`AGENTS.md:36`）。上游每週一由 `Upstream commit check` 檢查，紅燈代表有未審項目、不是工具壞；Dependabot 每週一開 PR，依賴新鮮度每月 1 日檢查；發版只在真的有新版本時同步版本號、CHANGELOG、tag 與 Release。
