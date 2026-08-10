# examples

本資料夾放範例說明與可公開使用的測試素材產生器。repo 不提交生成圖片或 ZIP；需要測試時在本機產生。

## 產生範例素材

```powershell
python examples\create_sample_assets.py
```

預設輸出：

```text
examples\generated\static-grid.png
examples\generated\animated\animated-01.gif
...
examples\generated\animated\animated-08.gif
```

`examples\generated\` 不進版控。

## 產生 LINE 手動上傳抽驗包

這個指令會產生非侵權範例素材，並一次輸出 LINE 靜態、Big、emoji、訊息、動態、pop-up、effect 的 ZIP，再跑本機 validator。產物只用於 LINE Creators Market 上傳表單 smoke test，不會自動送審。

```powershell
python examples\create_line_trial_packs.py
```

預設輸出：

```text
examples\generated\line-trial-packs\line-static.zip
examples\generated\line-trial-packs\line-big-stickers.zip
examples\generated\line-trial-packs\line-emoji.zip
examples\generated\line-trial-packs\line-message.zip
examples\generated\line-trial-packs\line-animated.zip
examples\generated\line-trial-packs\line-popup.zip
examples\generated\line-trial-packs\line-effect.zip
```

## 靜態貼圖

```powershell
python -m sticker_forge export examples\generated\static-grid.png -o outputs\line-stickers.zip --title "Sample Pack" --author "sticker-forge"
python -m sticker_forge validate outputs\line-stickers.zip
```

## LINE emoji

```powershell
python -m sticker_forge emoji examples\generated\static-grid.png -o outputs\line-emoji.zip --thumb 1
python -m sticker_forge validate outputs\line-emoji.zip --emoji
```

## LINE Big Stickers

```powershell
python -m sticker_forge big examples\generated\static-grid.png -o outputs\line-big-stickers.zip --title "Big Pack" --author "sticker-forge"
python -m sticker_forge validate outputs\line-big-stickers.zip --big
```

## LINE 訊息貼圖

```powershell
python -m sticker_forge message examples\generated\static-grid.png -o outputs\line-message.zip
```

## LINE 動態貼圖

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

## LINE pop-up / effect stickers

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

## 去背強度與白色描邊

背景是 AI 生圖常見的「帶光暈／褪色綠幕」而 `balanced` 清不乾淨時，改用 `--tune continuous`。
想要聊天貼圖常見的白色描邊，加 `--outline simple` 或 `--outline fancy`（預設 `none`）。

```powershell
python -m sticker_forge export examples\generated\static-grid.png -o outputs\line-stickers.zip --tune continuous
python -m sticker_forge export examples\generated\static-grid.png -o outputs\line-outlined.zip --outline fancy
python -m sticker_forge validate outputs\line-outlined.zip
```

## Signal

```powershell
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\signal.zip --target signal --title "Signal Pack" --author "sticker-forge" --emoji "🙂"
python -m sticker_forge validate outputs\signal.zip --signal
```

## 原則

- 不放使用者私有圖片。
- 不放生成貼圖包。
- 不放侵權角色、品牌、商標或真人肖像素材。
