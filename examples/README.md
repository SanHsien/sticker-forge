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

## Signal

```powershell
python -m sticker_forge platform examples\generated\static-grid.png -o outputs\signal.zip --target signal --title "Signal Pack" --author "sticker-forge" --emoji "🙂"
python -m sticker_forge validate outputs\signal.zip --signal
```

## 原則

- 不放使用者私有圖片。
- 不放生成貼圖包。
- 不放侵權角色、品牌、商標或真人肖像素材。
