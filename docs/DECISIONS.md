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

