# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `5052f7f46b88` 查的快照，開工前先重查 GitHub。

## 現況

`sticker-forge` 是 Windows-first、local-first 的聊天貼圖工具（Python core＋pywebview GUI＋CLI），是 `yazelin/line-sticker-studio` 的 MIT fork（`AGENTS.md:7,11`）。最近 release 是 v0.22.0，`pyproject.toml:7` 也是 0.22.0；`main` 帶有未發行的多幕色與四項缺陷修正（`CHANGELOG.md` Unreleased 段）。
健康：open PR 0、Dependabot 與 code scanning 告警 0，CI、CodeQL、Dependabot guarded merge、Dependency freshness、Upstream commit check 在 `main` 最近一次皆 success；issues 在 GitHub 上已停用，所以 open issue 數是「未查到」，不是 0（2026-10-29 `gh` 查詢）。
Windows GUI 實機驗收尚未完成，是否發 v0.23.0 也未定。本檔不替它決定發版與否；下面與發版有關的列都標為等待。上游水位在 commit `1a1e903`、PR 81、issue 62（`tools/upstream_baseline.json`），2026-10-26 的 Upstream commit check 為 success，代表沒有未審項目。

## 近期：可以直接動手

目前無待動工項目。

## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 發 v0.23.0（同步 `pyproject.toml` 版本、`CHANGELOG.md` 把 Unreleased 改成版本段、tag、Release 與資產） | Windows GUI 實機驗收通過，且維護者決定發版 | `pyproject.toml` 版本＝tag＝Release；`docs/WINDOWS_VALIDATION.md` 的驗收紀錄模板補上本版一筆；Release 資產 SHA-256 與本機 build 相符 | 維護者 | `AGENTS.md:41`、`docs/WINDOWS_VALIDATION.md:76-106,192`、接續開發報告（2026-10-2x）「需要維護者決定的事」 |
| 切 v1.0.0 | 維護者有時間在登入狀態下做 LINE Creators Market 七類型手動上傳抽驗，並完成 GUI 匯出矩陣（原生儲存對話框）與 WebView2／SmartScreen 記錄 | `docs/WINDOWS_VALIDATION.md` 該版驗收紀錄每項為 PASS，沒有 BLOCKED；七種 trial pack（`python examples\create_line_trial_packs.py`）皆已手動上傳且無退件；Release 資產齊備 | 維護者 | `REVIEW.md` 尚未通過 P1「LINE Creators Market」、P2「GUI 匯出矩陣」「WebView2」；`REVIEW.md` 發行判定 |
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
