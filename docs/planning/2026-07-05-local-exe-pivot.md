# 2026-07-05 Local EXE Pivot

## 決定

`sticker-forge` 改走本機工具方向。

## 目標流程

1. 程式產生 prompt。
2. 使用者自行用外部 AI 生圖。
3. 使用者匯入 3x3 grid。
4. 程式本機切圖、去背、尺寸整理。
5. 程式匯出 LINE sticker ZIP。

## 排除

- 不架 server。
- 不代管 Gemini / OpenAI API。
- 不做 Cloudflare Worker / Turnstile / quota。
- 不自動送審 LINE Creators Market。

## 優先工作

1. prompt templates。
2. image processing core。
3. LINE ZIP exporter。
4. local GUI / CLI。
5. Windows exe packaging。

