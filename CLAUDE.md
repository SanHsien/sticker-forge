# CLAUDE.md

給 Claude Code 在本專案工作時的指引。主要規則同 [`AGENTS.md`](AGENTS.md)。

## 專案定位

`sticker-forge` 要做成本機 LINE 貼圖製作工具，最好能打包成 Windows `.exe`。

預期流程：

1. 程式產生提示詞。
2. 使用者自行用 ChatGPT / Gemini / 其他工具生圖。
3. 使用者把圖匯回程式。
4. 程式本機切圖、去背、整理尺寸、打包 ZIP。

不架 server，不代管 AI API，不做線上服務。

## 不可違反

- 不新增 Cloudflare Worker / Turnstile / quota / Gemini proxy 服務。
- 不提交 secrets、使用者圖片、生成 ZIP 或本機暫存檔。
- 不移除 MIT 授權與原作者 attribution。
- 不宣稱 LINE 官方或保證上架通過。
- 不做 LINE 自動送審。

## 目前 legacy

- upstream web app / Worker 的 vendored reference source 已移除。
- 保留 `yazelin/line-sticker-studio` 的 MIT attribution 與歷史決策紀錄。
- upstream Cloudflare `worker/`、campaign-checker CI、Turnstile、quota、Gemini proxy 不符合 local-first；不要重建。

## 回覆要求

- 使用繁體中文。
- 直接說修改、驗證、剩餘事項。
- 不要把簡單任務寫成冗長架構分析。
