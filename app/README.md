# Local HTML App

這是 `sticker-forge` 的本機 HTML 介面原型，可直接用瀏覽器開啟：

```powershell
start .\app\index.html
```

功能：

- 產生 LINE 靜態貼圖 3x3 prompt。
- 支援繁體中文 / English 介面切換，並依語系產出 prompt 與 ZIP 內 README。
- 匯入使用者自行生成的 3x3 grid。
- 依 upstream 規則做 3% inset 切圖，輸出 370 x 320。
- 支援 green / magenta chroma-key 去背。
- 選 8 張貼圖，匯出 LINE ZIP：`01.png` 到 `08.png`、`main.png`、`tab.png`、`README.txt`。
- 匯出 9 張獨立 PNG 的 ZIP，供 Slack、Discord、Notion、簡報等非 LINE 上架用途使用。
- ZIP 由本機 JavaScript 產生，不需要 CDN 或網路。

限制：

- 不上傳圖片、不連接 AI API、不架 server。
