# prompts

放提示詞模板與範例。

目標：

- 讓使用者複製 prompt 到 ChatGPT / Gemini / 其他生圖工具。
- 產出適合匯回 `sticker-forge` 的 3x3 grid。
- 明確提醒避免侵權、商標、真人肖像、政治、色情、仇恨、暴力、個資等高風險內容。

不要在這裡放 API key 或服務憑證。

## 目前模板

- `line-static-3x3.md`：LINE 靜態貼圖 3x3 grid，有字版與無字版。
- `line-static-3x3.en.md`：英文版 LINE static sticker 3x3 grid，有字版與無字版。

CLI 可直接渲染：

```powershell
python -m sticker_forge prompt --character "原創柴犬" --chroma-key magenta
python -m sticker_forge prompt --character "原創柴犬" --output outputs\prompt.md
python -m sticker_forge --lang en prompt --character "an original corgi" --output outputs\prompt.en.md
```
