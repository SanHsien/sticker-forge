---
name: avatar-sticker-factory
description: 端到端 AI 似顏繪 LINE 16 宮格貼圖工廠技能範本。涵蓋真人照片特徵鎖定、16 宮格結構化提示詞組裝、1480x1280 排列圖生成、自動機械切圖驗證與 LINE Creators Market 上架 ZIP 打包流程。
triggers:
  - "avatar sticker"
  - "line sticker"
  - "16 宮格貼圖"
  - "似顏繪貼圖"
  - "LINE 貼圖製作"
  - "slice_line_stickers"
version: 1.0.0
author: "SanHsien / Ann Cheng Prompt Engineering Framework"
---

# AI 似顏繪貼圖工廠技能範本 (Avatar Sticker Factory Skill)

> 本技能範本收錄於 `templates/avatar-sticker-factory-skill.md`，可直接複製至 Agent 技能目錄（如 `~/.gemini/config/skills/avatar-sticker-factory/SKILL.md` 或 Claude Code 專案技能）中引入使用。  
> 核心規範對照：[`docs/line-sticker-16-grid-prompt-spec.md`](../docs/line-sticker-16-grid-prompt-spec.md)  
> 切圖工具實作：[`tools/slice_line_stickers.py`](../tools/slice_line_stickers.py)  
> 查證日期：2026-11-02

---

## 1. 技能定位與管線全貌（Pipeline Architecture）

本技能為 AI Coding Agent（Antigravity、Claude Code、Codex 等）提供一套確定性、零風格漂移的個人品牌與企業似顏繪貼圖生成管線：

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           AI 似顏繪 16 宮格貼圖工廠端到端管線流程                               │
├────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                │
│  [ Step 1：輸入真人參考照 ] ──► 鎖定臉型、髮流、眼型、配件與代表性服裝 (Identity Anchoring)    │
│            │                                                                                   │
│            ▼                                                                                   │
│  [ Step 2：組裝 16 宮格 Prompt ] ──► 注入 1480×1280 畫布、2.8 頭身 Q 版、粗白外框、四周 10px 餘白│
│            │                         與 16 組高頻日常繁體中文字庫（早安~恭喜）                 │
│            ▼                                                                                   │
│  [ Step 3：單張生圖一次性交付 ] ──► 產出單張 1480 × 1280 像素 RGBA 透明背景排列圖              │
│            │                         (同一 Attention 上下文，風格與人物長相零漂移)             │
│            ▼                                                                                   │
│  [ Step 4：調用機械切圖與檢驗工具 ] ──► 執行 tools/slice_line_stickers.py                       │
│            ├─ 沿 370×320 網格切分出 01.png ~ 16.png (單張最大 370×320 px)                     │
│            ├─ 嚴格機械檢驗每張貼圖四周 10px 安全邊界（防聊天氣泡切除）與 Alpha 通道             │
│            ├─ 自動等比例縮放合成主圖 main.png (240×240 px)                                      │
│            ├─ 自動縮放合成頁籤標籤圖 tab.png (96×74 px)                                        │
│            └─ 自動打包為上架專用 ZIP (line_stickers.zip)                                       │
│            │                                                                                   │
│            ▼                                                                                   │
│  [ Step 5：交付上架 ] ──► 直接匯入 LINE Creators Market 或 LINE 拍貼 App 完成審核上架          │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 階段作業標準步驟 (SOP)

### 階段一：真人肖像特徵鎖定（Identity Anchoring）
當使用者提供照片或指定人物特徵時，Agent 首先提取並結構化記錄不可變特徵：
1. **臉部骨骼與眼型**：例如「長橢圓臉型、內雙細長眼睛、眼角帶笑紋」。
2. **髮型細節與顏色**：例如「深黑棕色短髮、中分微捲波浪、長度至下顎」。
3. **識別特徵與配件**：例如「黑色細框圓眼鏡、右嘴角旁小痣」。
4. **預設服飾基調**：例如「深藍色休閒西裝外套內搭簡約白 T 恤」。

### 階段二：提示詞組裝（Prompt Construction）
Agent 套用 Ann Cheng 16 宮格工法，組合出結構化 Prompt：
- **畫布與網格規格**：總尺寸 `1480x1280`，4 列 $\times$ 4 行，單格精確 `370x320`。
- **身形與風格約束**：2.8 頭身 Q 版 chibi，頭大身小，平滑向量風格。
- **安全邊距與描邊**：四周保留各 `10px` 留白；角色與文字皆有 `4~8px` 粗白外框。
- **16 組繁體中文文案表**：
  - Row 1: `01 早安`（揮手拿咖啡）、`02 晚安`（抱枕呵欠）、`03 收到`（敬禮認真）、`04 謝謝`（合十鞠躬）
  - Row 2: `05 感恩`（撫胸微光）、`06 辛苦了`（奉茶打氣）、`07 不客氣`（擺手爽朗）、`08 太棒了`（歡呼彩帶）
  - Row 3: `09 加油`（握拳速度線）、`10 稍後回覆`（筆電趕路）、`11 好心肝`（頭頂大愛心）、`12 OK`（標準OK手勢）
  - Row 4: `13 週休快樂`（墨鏡冰飲）、`14 假期愉快`（小旗幟慶祝）、`15 生日快樂`（生日帽蛋糕）、`16 恭喜`（抱拳彩炮）

### 階段三：圖像生成與取得
- 將組裝之 Prompt 傳入生成模型（Midjourney `--ar 37:32`、DALL-E 或 SD 模型），產生 1480×1280 透明背景圖。
- 檢查產出檔案確認為 RGBA 格式。

### 階段四：自動化切圖與機械合規驗證
調用本專案 `tools/slice_line_stickers.py` 工具進行裁切與驗收：

```bash
# 執行嚴格切圖驗證並直接打包為上架 ZIP
python tools/slice_line_stickers.py \
  "input_avatar_1480x1280.png" \
  --out-dir "output/line_stickers" \
  --strict \
  --zip "output/line_stickers.zip"
```

檢核清單：
- [x] 是否產出 `01.png` ~ `16.png` 且皆為 370×320 px。
- [x] 是否產出 `main.png`（240×240 px）。
- [x] 是否產出 `tab.png`（96×74 px）。
- [x] 每張圖四周 10px 安全邊距內是否皆為透明像素（0 violations）。
- [x] 檔案模式是否全為 RGBA，背景無雜色。

### 階段五：交付與上架審查
Agent 回報上架壓縮檔路徑及規格驗證摘要：
- 上架 ZIP 包包含 18 個檔案（16 張貼圖 + main.png + tab.png）。
- 提醒使用者登入 [LINE Creators Market](https://creator.line.me/zh-hant/)，點選「新增貼圖」 $\rightarrow$ 選擇「靜態貼圖」 $\rightarrow$ 設定 16 張貼圖 $\rightarrow$ 於貼圖圖片區塊「上傳壓縮檔 (ZIP)」，即可一次性完成所有圖片配置。

---

## 3. 實戰提示詞範本（Prompt Template）

```text
[Role & Context Constraints]
Professional sticker sheet design, 4x4 grid layout containing 16 different chibi avatar stickers of the same character based on the uploaded reference photo.
Canvas Resolution: Exactly 1480x1280 pixels.
Layout Grid: Strict 4 rows and 4 columns, each cell perfectly occupying 370x320 pixels.
Proportions: Chibi 2.8 head-to-body ratio, expressive oversized head, petite body, highly consistent identity.

[Identity Anchors]
- Facial features: {USER_FACE_FEATURES}
- Hairstyle: {USER_HAIR_STYLE}
- Accessories: {USER_ACCESSORIES}
- Outfit: {USER_OUTFIT}

[Visual Rules]
- Art style: Crisp 2D digital vector sticker illustration, smooth flat shading.
- Sticker border: Solid thick clean white contour outline (6px) around character and text.
- Alpha channel: Pure 100% transparent background (RGBA), no background scenery.
- Margin requirement: Strict 10px empty transparent margin on all 4 sides of each 370x320 grid cell. Hand gestures and text must NOT touch cell edges.
- Typography: Bold rounded Traditional Chinese (繁體中文) characters with white outline.

[16 Grid Cells (Row 1 to Row 4)]
Row 1:
- 01: "早安" (Waving with a steaming morning coffee mug, energetic smile)
- 02: "晚安" (Hugging a starry pillow, peaceful yawn with a nightcap)
- 03: "收到" (Formal salute gesture, reliable focused eyes)
- 04: "謝謝" (Hands clasped in gratitude, polite bow)
Row 2:
- 05: "感恩" (Both hands over heart, touched tears of joy)
- 06: "辛苦了" (Handing over hot tea, gentle comfort)
- 07: "不客氣" (Friendly wave, carefree laughing)
- 08: "太棒了" (Jumping arms raised, celebration confetti)
Row 3:
- 09: "加油" (Double clenched fists, energetic action lines)
- 10: "稍後回覆" (Typing fast on mini laptop, rushing in a hurry)
- 11: "好心肝" (Big heart sign above head, playful wink)
- 12: "OK" (Classic OK finger ring gesture, confident nod)
Row 4:
- 13: "週休快樂" (Sunglasses, cold drink in hand, weekend breeze)
- 14: "假期愉快" (Waving party flag, happy picnic smile)
- 15: "生日快樂" (Party hat, holding mini birthday cake with candle)
- 16: "恭喜" (Clasped hands greeting, party confetti bursting)

[Negative Prompt]
watermark, realistic photo, 3D render, cell border overlap, touching 370x320 edges, simplified Chinese, typo, background texture, white background square.
```

---

## 4. 常見問題與自動補救策略（Troubleshooting）

| 異常現象 | 機械原因 | 補救處方 |
| :--- | :--- | :--- |
| `10px 邊距溢出警告` | 模型將手勢或文字畫得太靠邊緣 | 1. 調整提示詞強調「手勢內縮置中」<br>2. 執行切圖工具 `--margin 8` 或微調裁切位移<br>3. 在繪圖軟體微調透明圖層邊緣 |
| `缺少 Alpha 通道 (RGB)` | 生圖平台輸出為純白底 JPG 或 RGB PNG | 執行去背工具或於提示詞加強 `transparent alpha channel PNG` |
| `大圖尺寸非 1480x1280` | 模型自適應長寬比（例如 1024x1024） | 工具自動補齊透明畫布以防崩潰；但最佳作法是指定模型生成固定尺寸或等比縮放為 1480x1280 |
| `繁體字體出現簡體` | 基礎生圖模型中文偏誤 | 使用繁體字專用 LoRA，或在生圖後由圖像工具換上繁體中文向量字型 |
