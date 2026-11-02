# AI 似顏繪 LINE 16 宮格貼圖 Prompt 工程與視覺規範

> 對應任務：`T-20261031-01`
> 來源筆記：[`notes/2026-10-31-line-sticker-16-grid-ai-avatar-prompt-spec.md`](../notes/2026-10-31-line-sticker-16-grid-ai-avatar-prompt-spec.md)
> 核心原創：Ann Cheng（安總監 / 安老師，@anncheng_ann101）
> 查證日期：2026-11-02

---

## 0. 一頁規格摘要（Quick Reference）

| 項目 | 規格值 | 技術約束與目的 |
| :--- | :--- | :--- |
| **生成大圖總尺寸** | `1480 × 1280 px` | 劃分為 $4 \times 4 = 16$ 宮格，每格剛好為 LINE 貼圖上限 $370 \times 320 \text{ px}$ |
| **單格貼圖尺寸** | `W 370 × H 320 px` | 官方標準上限（寬度或高度其一需為最大值，長寬皆為偶數） |
| **主圖（main.png）** | `W 240 × H 240 px` | 1 張，商品列表與貼圖小舖封面，由單格貼圖縮放居中貼上全透明畫布 |
| **標籤圖（tab.png）** | `W 96 × H 74 px` | 1 張，聊天室鍵盤貼圖切換頁籤，由角色頭部特寫或單格縮放合成 |
| **安全邊距（Margin）** | 四周保留 $\ge 10\text{ px}$ | 防裁切安全區，貼圖實體邊緣與單格邊界必須留白，避免聊天氣泡遮蔽 |
| **背景透明度** | `Alpha Channel (RGBA)` | 必須去背透明（PNG-24 / 32-bit RGBA），無雜色底色 |
| **描邊規範** | 粗白外框（White Outline） | 約 $4 \sim 8\text{ px}$ 平滑白色貼圖描邊，確保深色/淺色/相片聊天室皆具備高對比 |
| **頭身比例** | 約 $2.5 \sim 3.0$ 頭身（推薦 $2.8$） | Q 版 Chibi 風格，頭大身小，兼具可愛度與五官辨識度 |
| **文案語言** | 繁體中文（台灣日常用語） | 筆劃醒目、字體圓潤清晰，與肢體動作語意嚴格對齊 |

---

## 1. 問題背景：為何採用「單張 16 宮格」一次性生成

在利用生成式 AI（Midjourney, Stable Diffusion, DALL-E, Imagen 等）製作個人品牌似顏繪或 LINE 貼圖時，常見兩種實作路徑：

```text
路徑 A：逐張獨立生成 16 次
真人照 ──▶ Prompt 1 ──▶ 貼圖 01 (臉微胖、短髮)
       ──▶ Prompt 2 ──▶ 貼圖 02 (臉變瘦、髮色偏淡)   ──▶ 風格漂移、特徵失真、需反覆抽卡
       ──▶ ...
       ──▶ Prompt 16 ──▶ 貼圖 16 (眼鏡樣式改變)

路徑 B：單張 16 宮格排列圖一次性生成 (Ann Cheng 方案)
真人照 ──▶ 單一結構化 Prompt ──▶ 1480×1280 (4×4 排列圖) ──▶ 自動切圖 ──▶ 01~16.png + main + tab
         (統一 Seed/上下文)      (五官、比例、光影完全一致)    (機械裁切)   (零風格漂移、合規交付)
```

### 1.1 核心痛點
1. **風格與身份漂移（Identity Drift）**：不同次生成會隨機取樣模型權重中的大眾臉，導致眼型、髮流、臉頰肉感與配件在每張貼圖間產生不一致。
2. **切圖與邊界失真**：手動裁剪往往因尺寸不固定、忘記預留 10px 餘白或去背殘留雜訊，被 LINE Creators Market 審核系統退件。
3. **文字排版破碎**：逐張生圖若讓模型自由發揮中文文字，容易出現缺字、簡體字或錯別字。

### 1.2 16 宮格提示詞工法價值
透過在單張畫布（$1480 \times 1280$）內定義 $4 \times 4$ 網格，強迫模型在同一注意力（Self-Attention）上下文中輸出 16 種姿勢與表情。這鎖定了全域特徵（人物長相、髮型、服飾基調、白邊風格），同時在各分格賦予指定的情境動作與繁體中文字。

---

## 2. 深入視覺工程規範

### 2.1 角色特徵鎖定（Identity Retention）
- **單一真人照片參考**：在提示詞開頭強制錨定照片，明言「以提供之真人照片為唯一人物臉部特徵參考」。
- **不可變特徵清單**：
  - 眼型與眼神（如內雙、杏眼、下垂眼、眼尾特徵）。
  - 髮型與髮色（如中分短波浪、黑棕色、瀏海長度與髮流）。
  - 配件與臉部標記（如細黑框眼鏡、痣、笑紋）。
- **2.8 頭身比例（Chibi 2.8 Ratio）**：
  - 頭部約佔整體高度的 $35\% \sim 40\%$。
  - 身體與四肢適度簡化為圓潤流暢線條，手掌保留拇指與手指輪廓但弱化關節細節。
  - 避免 1:1 極端 Q 版導致無法辨識臉部特徵；亦避免 4~5 頭身失去貼圖的活潑趣味性。

### 2.2 1480×1280 網格數學與安全留白
- **整體畫布**：寬度 $1480\text{ px}$、高度 $1280\text{ px}$。
- **網格劃分**：4 列（Rows）$\times$ 4 行（Cols），每格精確佔比為：
  $$\text{單格寬度} = \frac{1480}{4} = 370\text{ px}$$
  $$\text{單格高度} = \frac{1280}{4} = 320\text{ px}$$
- **四周 10px 安全邊界（Safety Margin）**：
  - 單格四周各 $10\text{ px}$（Top, Bottom, Left, Right）內**嚴禁出現任何不透明像素**。
  - 有效繪製內容安全區域：$X \in [10, 360)$，寬度 $350\text{ px}$；$Y \in [10, 310)$，高度 $300\text{ px}$。
  - 作用：LINE 聊天室在顯示貼圖時，邊界會受到氣泡遮罩或邊角圓弧影響；若貼圖緊貼邊界，文字筆劃或手部會被直接切除。
- **粗白外框（White Sticker Outline）**：
  - 角色本體與文字外圍必須具有 $4 \sim 8\text{ px}$ 的純白色實心描邊（`#FFFFFF`）。
  - 描邊邊緣平滑、無半透明羽化雜訊，確保在黑色聊天背景或複雜照片背景中依然具備清晰的輪廓分離度。

---

## 3. 16 組高頻繁體中文字庫與動作對照表

Ann Cheng 整理之 16 組高頻日常詞彙涵蓋工作回覆、禮貌致意、日常生活與祝福情境：

| 格位 | 檔名 | 繁體中文文案 | 肢體動作與手勢設計 | 表情氛圍與眼神 |
| :---: | :---: | :--- | :--- | :--- |
| **01** | `01.png` | **早安** | 精神飽滿揮手打招呼，單手持冒煙熱咖啡杯或陽光背景光暈 | 燦爛微笑、朝氣蓬勃 |
| **02** | `02.png` | **晚安** | 雙手抱著柔軟星空抱枕，或拉棉被戴睡帽打呵欠 | 甜美放鬆、眼帶微倦意 |
| **03** | `03.png` | **收到** | 右手俐落立正敬禮，或雙手在胸前比出「清楚了解」手勢 | 眼神認真、專業值得信賴 |
| **04** | `04.png` | **謝謝** | 雙手合十、微微鞠躬點頭致意 | 誠懇溫暖、眼角含笑 |
| **05** | `05.png` | **感恩** | 雙手輕撫胸口，背景帶有柔和微光亮點 | 感動溫柔、真摯真誠 |
| **06** | `06.png` | **辛苦了** | 雙手遞上一杯熱茶，或做出輕輕敲肩膀、捏手打氣手勢 | 貼心撫慰、體貼關懷 |
| **07** | `07.png` | **不客氣** | 單手輕輕擺動、大方爽朗揮動手腕 | 瀟灑自得、親切隨和 |
| **08** | `08.png` | **太棒了** | 雙手高舉歡呼跳躍，四周帶小彩帶或閃亮小星星 | 興奮喝采、驚喜張嘴笑 |
| **09** | `09.png` | **加油** | 雙手握拳置於胸前，手臂帶動態衝刺線條 | 堅定熱情、充滿活力 |
| **10** | `10.png` | **稍後回覆** | 手指在筆電鍵盤上飛快敲擊，或低頭看手錶手刀趕路 | 專注急忙、認真負責 |
| **11** | `11.png` | **好心肝** | 雙手於頭頂比出大愛心，或單手比臉頰愛心 | 俏皮眨眼、幽默可愛 |
| **12** | `12.png` | **OK** | 單手或雙手比出圓潤清晰的標準 OK 手勢 | 信心十足、從容自信 |
| **13** | `13.png` | **週休快樂** | 戴墨鏡、手持冰涼手搖飲或身背輕便旅行背包 | 悠閒愜意、度假放鬆風 |
| **14** | `14.png` | **假期愉快** | 雙手揮動野餐小旗幟或吹派對吹捲 | 歡樂雀躍、元氣滿滿 |
| **15** | `15.png` | **生日快樂** | 頭戴派對尖角生日帽，雙手端著插有蠟燭的精緻小蛋糕 | 喜慶燦爛、幸福笑容 |
| **16** | `16.png` | **恭喜** | 雙手抱拳拱手作揖祝賀，身旁伴隨雙色彩炮迸發 | 熱鬧喜氣、盛大祝賀 |

---

## 4. 結構化 Prompt 實戰範本（模板）

以下為可直接填空使用的 16 宮格生成提示詞模板：

```text
[Role & Context Constraints]
A professional sticker sheet design, 4x4 grid layout featuring 16 different chibi avatar stickers of the same character, based on the provided reference photo.
Total image size: 1480x1280 pixels.
Layout: Exact 4 rows and 4 columns, each cell strictly occupying 370x320 pixels.
Character proportions: Cute 2.8 head-to-body chibi ratio, head large and expressive, body petite, consistent identity across all 16 cells.
Identity features (Locked to reference photo):
- Face & Hair: [填入人物特徵：例如 oval face shape, natural Asian black layered medium bob hair, clear eyeglasses with thin black frame]
- Clothing baseline: [填入基礎服裝：例如 smart-casual navy blue blazer with white inner t-shirt]

[Art Style & Rendering Rules]
- Art style: Clean 2D digital vector sticker illustration, vibrant color palette, smooth flat shading.
- Sticker border: A thick, solid clean white sticker contour outline (4-8px) around every character and text element.
- Background: Pure solid transparent background with transparent alpha channel (PNG RGBA). Absolutely NO background patterns, grids, or background scenery.
- Safety Margins: Strict 10px empty transparent margin on all four sides of each 370x320 grid cell. Hand gestures and text must NOT touch or exceed cell boundaries.
- Typography: Clear, legible Traditional Chinese (繁體中文) characters integrated organically with each character pose, rendered in bold rounded comic typography with white outline.

[16 Grid Scene Assignments (Row 1 to Row 4)]:
- Cell 01 (Row 1, Col 1): Text "早安". Energetic waving hand, holding a steaming coffee cup, bright cheerful smile.
- Cell 02 (Row 1, Col 2): Text "晚安". Hugging a fluffy starry pillow, yawning peacefully, wearing a nightcap.
- Cell 03 (Row 1, Col 3): Text "收到". Crisp military salute gesture, focused reliable expression.
- Cell 04 (Row 1, Col 4): Text "謝謝". Hands clasped together in gratitude, gentle bow, sincere warm smile.
- Cell 05 (Row 2, Col 1): Text "感恩". Hands over heart, touched and emotional expression with sparkling eyes.
- Cell 06 (Row 2, Col 2): Text "辛苦了". Handing over a hot teacup with two hands, caring and comforting face.
- Cell 07 (Row 2, Col 3): Text "不客氣". Playfully waving hand sideways, carefree open laugh.
- Cell 08 (Row 2, Col 4): Text "太棒了". Both arms raised jumping in excitement, celebratory mini confetti.
- Cell 09 (Row 3, Col 1): Text "加油". Both fists clenched in determination, dynamic action speed lines.
- Cell 10 (Row 3, Col 2): Text "稍後回覆". Typing furiously on a miniature laptop, focused and hurried expression.
- Cell 11 (Row 3, Col 3): Text "好心肝". Making a big heart sign over head, cheeky wink.
- Cell 12 (Row 3, Col 4): Text "OK". Distinct standard OK finger circle gesture, confident nod.
- Cell 13 (Row 4, Col 1): Text "週休快樂". Wearing sunglasses, holding an iced beverage, relaxed weekend vibe.
- Cell 14 (Row 4, Col 2): Text "假期愉快". Waving a cute festival flag, carefree celebratory mood.
- Cell 15 (Row 4, Col 3): Text "生日快樂". Wearing a festive birthday cone hat, holding a cake with a lit candle.
- Cell 16 (Row 4, Col 4): Text "恭喜". Traditional clasped hands greeting (拱手), party popper bursting with joy.

[Negative Constraints]
No watermark, no photography realism, no 3D uncanny valley rendering, no merged cells, no overlapping across 370x320 grid borders, no simplified Chinese characters, no spelling typos, no solid color or textured backgrounds, no background clutter.
```

---

## 5. LINE Creators Market 上架技術規範清單

依據 LINE Creators Market 官方貼圖製作準則，製作與上架貼圖檔案時必須通過以下機械式檢核：

```text
上架 ZIP 包結構
├── 01.png ~ 16.png  (貼圖本體，每張 W 370 × H 320 px，最大尺寸範圍)
├── main.png         (主圖 1 張，W 240 × H 240 px)
└── tab.png          (頁籤標籤圖 1 張，W 96 × H 74 px)
```

### 5.1 檔案規格表

| 檔案項目 | 檔名規則 | 寬高尺寸 | 檔案格式 | 背景要求 | 數量 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **主圖 (Main)** | `main.png` | `240 × 240 px` | PNG (RGBA) | 去背透明 | 1 張 |
| **貼圖圖片 (Stickers)** | `01.png` ~ `16.png` | `370 × 320 px`（最大） | PNG (RGBA) | 去背透明 | 16 張（可選 8/16/24/32/40） |
| **標籤圖 (Tab)** | `tab.png` | `96 × 74 px` | PNG (RGBA) | 去背透明 | 1 張 |

### 5.2 審核規則與避坑要點
1. **尺寸必須為偶數**：寬度與高度像素值均需為偶數數值；單張貼圖最大尺寸為 $370 \times 320\text{ px}$，寬度或高度其中之一必須為最大尺寸（即寬 370 或高 320）。
2. **邊距餘白（Safety Margin）**：貼圖內容與圖片四周必須保留至少 $10\text{ px}$ 空間，避免手機聊天室裁剪。
3. **色彩模式**：必須為 RGB / RGBA 模式，不可使用 CMYK 模式。
4. **解析度**：至少 $72\text{ dpi}$ 以上。
5. **單檔與封包容量**：單張 PNG 容量小於 $1\text{ MB}$；包含所有貼圖與縮圖的 ZIP 封包總容量小於 $20\text{ MB}$。
6. **文字內容限制**：不可出現侵權商標、不可含有暴力血腥、不雅字眼或未授權人物肖像。

---

## 6. 自動切圖工具對接操作手冊

本 repo 提供專用切圖與規格驗證工具 [`tools/slice_line_stickers.py`](../tools/slice_line_stickers.py)，可一鍵將生圖模型輸出的 $1480 \times 1280$ 排列圖切分並驗證合規：

### 6.1 基本執行指令
```bash
# 自動切分 16 宮格、檢查 10px 餘白與 Alpha 通道，並輸出 main.png 與 tab.png
python tools/slice_line_stickers.py avatar_grid_1480x1280.png --out-dir output/stickers

# 嚴格模式（若任何一格邊距內含不透明像素則報錯中斷）並自動打包為上架 ZIP
python tools/slice_line_stickers.py avatar_grid_1480x1280.png -o output/stickers --strict --zip output/line_stickers.zip
```

### 6.2 輸出報告範例
```text
[*] 讀取影像: avatar_grid_1480x1280.png (1480x1280, 模式: RGBA)
[*] 切割 4x4 宮格 (單格 370x320)...
  [PASS] 01.png (370x320) - 10px 安全邊距合規
  [PASS] 02.png (370x320) - 10px 安全邊距合規
  ...
  [PASS] 16.png (370x320) - 10px 安全邊距合規
[*] 合成主圖 main.png (240x240, 來源: 01.png) [OK]
[*] 合成標籤 tab.png (96x74, 來源: 01.png) [OK]
[*] 打包上架壓縮檔: output/line_stickers.zip (共 18 個檔案) [OK]
[SUCCESS] 全數 16 張貼圖與上架檔案切圖合規完成！
```

---

## 7. 一手來源與查證紀錄

| 項目 | 來源名稱 | 官方連結 / 一手網址 | 查證日期 | 查證事實說明 |
| :--- | :--- | :--- | :---: | :--- |
| **貼圖官方準則** | LINE Creators Market | [貼圖製作準則 (LINE Guideline)](https://creator.line.me/zh-hant/guideline/sticker/) | 2026-11-02 | 確認 main (240x240)、tab (96x74)、stickers (max 370x320)、PNG-RGBA、四周 10px 餘白、單張 1MB 與 ZIP 20MB 上限 |
| **16宮格工法原創** | Ann Cheng (安老師) | [Threads 分享文 (@anncheng_ann101)](https://www.threads.com/share/BAgCwYB05Y/) ｜ [貼文連結](https://www.threads.com/@anncheng_ann101/post/DfEB-BIEUGF) | 2026-11-02 | 確認 1480x1280 (單格 370x320)、2.8 頭身 Q 版、粗白貼圖外框與 16 組繁體中文文案表 |
| **影音實戰教學** | Ann Cheng YouTube | [ANNChengANN101 頻道實戰教學](https://www.youtube.com/@ANNChengANN101) | 2026-11-02 | 確認 Line 透明貼圖 16 宮格生圖與 Line 拍貼上架流程 |
