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

> 本技能範本收錄於 `templates/avatar-sticker-factory-skill.md`。可直接複製至 Agent 技能目錄（如 `%USERPROFILE%\.gemini\config\skills\avatar-sticker-factory\SKILL.md` 或各專案技能目錄）中引入使用。  
> 【自包含與依賴說明】：本技能依賴切圖驗證腳本 `examples/slice_line_stickers.py`（僅用 Python 標準函式庫加第三方套件 Pillow，需 `pip install Pillow`；缺套件時腳本 exit 2 並提示）。若獨立複製至其他環境或專案，請將該腳本一併複製至技能目錄下的 `scripts/` 或確保其已加入系統 PATH。其判定門檻與已知抓不到的情況見 `docs/line-sticker-16-grid-prompt-spec.md` 第 6.3 節。  
> 核心規範對照：[`docs/line-sticker-16-grid-prompt-spec.md`](line-sticker-16-grid-prompt-spec.md)  
> 查證日期：2026-11-02

---

## 1. 技能定位與管線全貌（Pipeline Architecture）

本技能為 AI Coding Agent（Antigravity、Claude Code、Codex 等）提供一套「生成走單張 16 宮格、切圖與規格檢查走確定性腳本」的個人品牌與企業似顏繪貼圖管線（單張生成能否讓風格較一致是經驗推測，沒有實測數據）：

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
│            │                         (16 格共用同一次生成，風格較易一致，未驗證)               │
│            ▼                                                                                   │
│  [ Step 4：調用機械切圖與檢驗工具 ] ──► 執行 slice_line_stickers.py (repo 或 scripts/)         │
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
- 將組裝之 Prompt 傳入生成模型。各模型的長寬比參數（例如 Midjourney 的 `--ar 37:32`）與是否支援輸出透明 PNG，本 repo 沒有逐一實測，【未驗證】，請以所用平台當下的文件為準。
- 【去背處理】：【未驗證】本 repo 沒有對任何特定模型實測它的「透明背景」輸出是不是真的有 Alpha 通道；原作者貼文本身也同時要求「純白背景」與「透明排列圖」（見規範文件第 2.2 節）。因此不要假設模型輸出是真透明：一律先跑階段四的切圖工具，它回報缺 Alpha、無透明像素、或安全區被填滿／疑似白底棋盤格時，再用去背工具（例如 `rembg`、Photoshop，工具效果未在本 repo 驗證）處理成真正透明的 RGBA PNG，處理後重跑工具。
- 工具是否通過只是機械檢查，不代表背景乾淨、不代表上架審核會過。

### 階段四：自動化切圖與機械合規驗證
調用切圖工具（本專案位於 `examples/slice_line_stickers.py`；若獨立使用技能請調用同技能目錄下的 `scripts/slice_line_stickers.py`）：

```bash
# 執行嚴格切圖驗證並直接打包為上架 ZIP
python examples/slice_line_stickers.py \
  "input_avatar_1480x1280.png" \
  --out-dir "output/line_stickers" \
  --strict \
  --zip "output/line_stickers.zip"
```

檢核清單（空白框，需在實際執行後逐項勾選；工具能查的以 exit 0 與 `--json` 報告為證據，查不到的要人工看圖）：
- [ ] （工具）`01.png` ~ `16.png` 皆為 370×320 px 的 RGBA。
- [ ] （工具）`main.png`（240×240 px）與 `tab.png`（96×74 px）已產出。
- [ ] （工具）每張圖四周 10px 安全邊距內沒有不透明像素（0 violations）。
- [ ] （工具）沒有空白貼圖、實心底、疑似白底或棋盤格（工具有已知抓不到的情況，見規範文件 6.3）。
- [ ] （工具）exit 0 且 ZIP 確實產生（`--zip` 沒產出時工具會 exit 1）。
- [ ] （人工）肉眼看過每張圖：背景沒有殘留雜色或光暈、繁體字正確、人物特徵一致。工具查不到這三項。

### 階段五：交付與上架審查
Agent 回報上架壓縮檔路徑及規格驗證摘要：
- 上架 ZIP 包包含 18 個檔案（16 張貼圖 + main.png + tab.png），且總容量小於 60MB（單張 < 1MB）。
- 【上架流程標註未驗證】：提醒使用者登入 [LINE Creators Market](https://creator.line.me/zh-hant/)，點選「新增貼圖」 $\rightarrow$ 選擇「靜態貼圖」 $\rightarrow$ 設定 16 張貼圖 $\rightarrow$ 於貼圖圖片區塊「上傳壓縮檔 (ZIP)」；或使用「LINE 拍貼」App 匯入。（此流程與介面標註為未驗證，請依 LINE 官方後台最新版本操作指引為準）。

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
| `安全區可見覆蓋率 …%（實心底／假透明）`、`疑似白底或棋盤格` | 去背沒做、做了假透明（把棋盤格圖樣畫進圖裡）、或整格鋪了白底 | 用去背工具重做真正的透明，再重跑；不要調低工具門檻 |
| `可見像素僅 N 個…視為空白貼圖` | 該格沒畫出東西、只剩雜點，或內容幾乎透明 | 重新生成該格，或在繪圖軟體補畫 |
| `已要求 --zip 但未產出 ZIP：…` | 有格子不合格、缺 main／tab、張數不是 8/16/24/32/40、單格尺寸不是偶數或超過 370×320、`--margin` 小於 10 | 照訊息逐項修正；舊 ZIP 已被工具刪除，不會殘留 |
| `10px 邊距溢出警告` | 模型將手勢或文字畫得太靠邊緣 | 1. 調整提示詞強調「手勢與文字內縮置中，預留四周 10px 留白」<br>2. 在繪圖或去背軟體中微調圖層縮小置中（切勿放寬工具檢查） |
| `缺少 Alpha 通道 (RGB)` | 生圖平台輸出為純白底 JPG 或 RGB PNG | 使用去背工具（如 `rembg`、Photoshop）完成去背並轉存為 RGBA PNG |
| `大圖尺寸非 1480x1280` | 模型生成長寬比不符（例如 1536x1024 或 1024x1024） | 1536×1024 (3:2) 與 1480×1280 (37:32) 長寬比不符，無法直接等比縮放！切圖工具僅做網格切分，不負責全局縮放；需在生圖時指定 `--ar 37:32`，或在切圖前先手動裁切/補畫布至 37:32 比例後，再調整尺寸為 1480×1280 |
| `繁體字體出現簡體` | 基礎生圖模型中文偏誤 | 使用繁體字專用 LoRA，或在生圖後由圖像工具換上繁體中文向量字型 |
