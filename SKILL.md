---
name: sticker-forge
description: 維護 SanHsien/sticker-forge：Windows-first、local-first 的聊天貼圖製作工具。使用者自行選擇 AI 生圖服務，再把 grid / PNG / GIF / APNG 匯回本機程式做切圖、去背、描邊、尺寸整理、驗證與 LINE／多平台匯出。
---

# Sticker Forge

## 適用任務

- 維護 prompt templates 與貼圖文案流程。
- 處理 3×3 grid、PNG、GIF、APNG 匯入。
- 維護切圖、去背、邊緣清理、描邊、尺寸與排序。
- 維護 LINE 靜態／Big／emoji／訊息／動態／pop-up／effect export。
- 維護 Telegram、WhatsApp、Discord、Signal export。
- 維護 pywebview GUI、CLI、validator 或 Windows PyInstaller 發行。

## 不適用

- 建立 hosted backend、Cloudflare Worker、Turnstile quota 或集中式 AI proxy。
- 代管 API key、token 或使用者圖片。
- 自動操作 LINE Creators Market 送審。
- 宣稱 LINE 官方、認證或保證平台審核結果。

## 主要入口

- `README.md` / `README.en.md`：產品首頁。
- `AGENTS.md`：主要維護規則與硬性邊界。
- `src/sticker_forge/`：Python core、CLI 與 GUI bridge。
- `app/`：pywebview 前端。
- `prompts/`：prompt templates。
- `packaging/`：Windows build / smoke test。
- `tests/`：回歸測試。
- `docs/USER_GUIDE.md`：使用說明。
- `docs/DEVELOPMENT.md`：架構與開發。
- `docs/WINDOWS_VALIDATION.md`：Windows / LINE 實機驗收。
- `docs/LINE_SUBMISSION.md`：LINE 手動送審。
- `NOTICE.md`：MIT fork 來源與 attribution。

## 工作規則

- 一般修改使用 branch → PR → CI → merge。
- 圖片處理與 export 規則放在 Python core，不在 JavaScript 複製第二套。
- 改圖片處理、ZIP 結構、validator 或 GUI bridge 時補測試。
- 純文件或 metadata 調整不需要 bump version / Release。
- 測試不要使用真實 secrets、個人圖片或生成 ZIP。
- 上游 `yazelin/line-sticker-studio` 只選擇性移植適合 local-first 方向的概念／修正，不把 hosted Worker 路線帶回來。

## 最小驗證

```powershell
git diff --check
python -m pytest
```

Windows GUI、packaging 或 LINE 特殊格式需要額外實機判定時，依 `docs/WINDOWS_VALIDATION.md` 執行並只回報實際完成的驗證。
