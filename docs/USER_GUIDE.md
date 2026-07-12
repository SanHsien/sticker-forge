# User Guide

這份文件給一般使用者看。維護與打包流程見 [`DEVELOPMENT.md`](DEVELOPMENT.md)，LINE 手動送審流程見 [`LINE_SUBMISSION.md`](LINE_SUBMISSION.md)。

## 下載與啟動

1. 到 GitHub Releases 下載 `sticker-forge-v0.18.0-windows-x64.zip`。
2. 解壓縮到本機資料夾。
3. 雙擊 `sticker-forge.exe` 開啟桌面 GUI。
4. 需要命令列時使用 `sticker-forge-cli.exe`。

GUI 是本機 pywebview 視窗，不會啟動 server，也不會把圖片上傳到任何服務。AI 生圖發生在你自己選擇的 ChatGPT、Gemini 或其他工具。

## LINE 靜態貼圖

1. 在 GUI 填入角色、主題、語氣、風格、文字與動作，或使用主題預設。
2. 複製提示詞，到外部生圖工具產生 3x3 grid。
3. 下載圖片後拖進 GUI，或用「加入 grid」匯入。
4. 檢查九宮格切圖、去背與排序。
5. 選擇要匯出的張數：8、16、24、32 或 40。
6. 選定主圖與聊天標籤圖。
7. 匯出 LINE ZIP。
8. 到 LINE Creators Market 手動建立套組、上傳 ZIP 內容並送審。

CLI 範例：

```powershell
python -m sticker_forge prompt --preset office-cat --output outputs\prompt.md
python -m sticker_forge export examples\generated\static-grid.png -o outputs\line-stickers.zip --title "Sample Pack" --author "SanHsien"
python -m sticker_forge validate outputs\line-stickers.zip
```

## LINE emoji

LINE emoji 使用 180x180 透明 PNG，張數為 8 到 40 張。GUI 可直接匯出；CLI 可用：

```powershell
python -m sticker_forge emoji examples\generated\static-grid.png -o outputs\line-emoji.zip --thumb 1
python -m sticker_forge validate outputs\line-emoji.zip --emoji
```

## LINE Big Stickers

Big Stickers 是 LINE 的大型靜態貼圖類型，匯出尺寸為 396x660。GUI 可直接匯出；CLI 可用：

```powershell
python -m sticker_forge big examples\generated\static-grid.png -o outputs\line-big-stickers.zip --title "Big Pack" --author "sticker-forge"
python -m sticker_forge validate outputs\line-big-stickers.zip --big
```

## LINE 訊息貼圖

訊息貼圖讓使用者在 LINE 端輸入文字，貼圖本身不要預先把文字做死。GUI 可直接匯出；CLI 可用：

```powershell
python -m sticker_forge message examples\generated\static-grid.png -o outputs\line-message.zip
```

## LINE 動態貼圖

動態貼圖匯入的是「每張貼圖一個 GIF 或 APNG」，不是動態九宮格。張數為 8、16 或 24。

```powershell
python -m sticker_forge animated `
  examples\generated\animated\animated-01.gif `
  examples\generated\animated\animated-02.gif `
  examples\generated\animated\animated-03.gif `
  examples\generated\animated\animated-04.gif `
  examples\generated\animated\animated-05.gif `
  examples\generated\animated\animated-06.gif `
  examples\generated\animated\animated-07.gif `
  examples\generated\animated\animated-08.gif `
  -o outputs\line-animated.zip
```

匯出後仍要到 LINE Creators Market 手動上傳抽驗。LINE 可能針對 APNG 檔案大小、播放狀態或內容做平台端判定。

## LINE pop-up / effect stickers

pop-up / effect stickers 同時需要靜態貼圖與每張貼圖對應的 480x480 APNG。GUI 流程：

1. 先匯入 3x3 靜態 grid，選取 8、16 或 24 張。
2. 點「匯入畫面動畫」，選同樣數量的 GIF/APNG。
3. 預覽區確認靜態貼圖數量與畫面動畫數量相同。
4. 點「匯出 pop-up」或「匯出 effect」。

CLI 也可用：

```powershell
python -m sticker_forge popup examples\generated\static-grid.png `
  -a examples\generated\animated\animated-01.gif `
  -a examples\generated\animated\animated-02.gif `
  -a examples\generated\animated\animated-03.gif `
  -a examples\generated\animated\animated-04.gif `
  -a examples\generated\animated\animated-05.gif `
  -a examples\generated\animated\animated-06.gif `
  -a examples\generated\animated\animated-07.gif `
  -a examples\generated\animated\animated-08.gif `
  -o outputs\line-popup.zip
python -m sticker_forge validate outputs\line-popup.zip --popup

python -m sticker_forge effect examples\generated\static-grid.png `
  -a examples\generated\animated\animated-01.gif `
  -a examples\generated\animated\animated-02.gif `
  -a examples\generated\animated\animated-03.gif `
  -a examples\generated\animated\animated-04.gif `
  -a examples\generated\animated\animated-05.gif `
  -a examples\generated\animated\animated-06.gif `
  -a examples\generated\animated\animated-07.gif `
  -a examples\generated\animated\animated-08.gif `
  -o outputs\line-effect.zip
python -m sticker_forge validate outputs\line-effect.zip --effect
```

## 其他平台

多平台匯出會把同一批貼圖整理成 Telegram、WhatsApp、Discord 或 Signal 常用尺寸。這是尺寸整理，不代表自動上架。

```powershell
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\telegram.zip --target telegram
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\whatsapp.zip --target whatsapp
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\discord.zip --target discord
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\signal.zip --target signal --title "Signal Pack" --author "sticker-forge" --emoji "🙂"
python -m sticker_forge validate outputs\signal.zip --signal
```

Signal ZIP 會包含 `cover.png` 與 `signal_manifest.json`。Signal Desktop 仍需手動建立貼圖包、匯入圖片，並依 manifest 填入標題、作者與 emoji。

## 範例素材

repo 不提交生成圖片或 ZIP。需要測試時先產生本機範例素材：

```powershell
python examples\create_sample_assets.py
```

產物會放在 `examples\generated\`，這個資料夾不進版控。

## 常見問題

### GUI 打不開

Windows 10/11 通常已內建 WebView2。若 GUI 無法開啟，先安裝或修復 Microsoft Edge WebView2 Runtime，再重開 `sticker-forge.exe`。

### 匯出失敗

GUI 會顯示 Python core 回傳的錯誤訊息。常見原因是匯入張數不足、動態貼圖張數不是 8/16/24、輸出路徑沒有寫入權限，或圖片不是可讀格式。

### 背景沒有變透明

生圖時請用純綠或純洋紅背景，並避免角色邊緣出現大量相近顏色。`export` 預設會去背；若使用 `--keep-background`，validate 可能會指出貼圖完全不透明。

### 可以自動送 LINE 審核嗎

不做自動送審。`sticker-forge` 只產生本機 ZIP 與上架說明，送審仍由使用者在 LINE Creators Market 手動完成。

### 可以用真人、商標或知名角色嗎

不要。請使用原創角色與自有素材，避開真人肖像、商標、知名 IP、政治人物、色情、仇恨、暴力、詐騙與個資內容。
