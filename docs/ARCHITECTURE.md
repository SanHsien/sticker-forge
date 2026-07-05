# Architecture

## 目標架構

```text
Local desktop app / exe
  |
  | or local HTML app opened from disk
  |
  | generates prompt
  v
User copies prompt to ChatGPT / Gemini / other image tool
  |
  | user downloads generated image
  v
Local desktop app / exe
  |
  | imports 3x3 grid
  v
split -> cleanup -> resize -> preview -> export ZIP
```

本專案不需要 hosted backend。AI 生成發生在使用者自行選擇的外部工具，`sticker-forge` 只處理提示詞與本機圖片加工。

## 模組規劃

- Prompt templates / renderer
  - 角色設定
  - 貼圖文字
  - 動作描述
  - 風格
  - LINE 審核風險提醒
- Image import
  - 匯入 3x3 grid
  - 檢查解析度與比例
- Grid split
  - 切 9 格
  - 選 8 張
- Cleanup
  - chroma-key 去背
  - 邊緣清理
  - padding
- Export
  - sticker images
  - main image
  - tab image
  - README / 上架說明
  - ZIP 結構檢查
- Local HTML app
  - 直接開啟 `app/index.html`
  - 產 prompt
  - 匯入 3x3 grid
  - 切圖、去背、選 8 張
  - 瀏覽器端 ZIP 匯出
- Packaging
  - Windows `.exe`
  - release artifact

## Legacy

目前仍保留 upstream web app 作為參考：

- `reference/upstream-line-sticker-studio/app.js`
- `reference/upstream-line-sticker-studio/index.html`
- `reference/upstream-line-sticker-studio/styles.css`
- `reference/upstream-line-sticker-studio/worker/`

這些檔案可作為邏輯參考，但不代表目標架構。Worker、Turnstile、quota、Gemini proxy 應視為待移除或封存。
