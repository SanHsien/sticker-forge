# AI 似顏繪 LINE 16 宮格貼圖 Prompt 工程與視覺規範

> 對應任務：`T-20261031-01`
> 來源筆記：[`docs/research/2026-10-31-line-sticker-16-grid-ai-avatar-prompt-spec.md`](research/2026-10-31-line-sticker-16-grid-ai-avatar-prompt-spec.md)
> 核心原創：Ann Cheng（安總監 / 安老師，@anncheng_ann101）
> 查證日期：2026-11-02（LINE 官方準則與 Threads 貼文都在這天實際開頁核對，範圍見第 7 節）

---

## 0. 一頁規格摘要（Quick Reference）

| 項目 | 規格值 | 技術約束與目的 |
| :--- | :--- | :--- |
| **生成大圖總尺寸** | `1480 × 1280 px` | 劃分為 $4 \times 4 = 16$ 宮格，每格剛好為 LINE 貼圖上限 $370 \times 320 \text{ px}$ |
| **單格貼圖尺寸** | `W 370 × H 320 px`（最大） | 官方標示為「上限」，並要求尺寸設為偶數（官方頁面未見「寬或高其一須達上限」的規定；取上限是本 repo 為了清晰度的選擇） |
| **主圖（main.png）** | `W 240 × H 240 px` | 1 張，商品列表與貼圖小舖封面，由單格貼圖縮放居中貼上全透明畫布 |
| **標籤圖（tab.png）** | `W 96 × H 74 px` | 1 張，聊天室鍵盤貼圖切換頁籤，由角色頭部特寫或單格縮放合成 |
| **安全邊距（Margin）** | 四周保留約 $10\text{ px}$ 留白 | 官方原句：「剪裁後的圖片與貼圖圖案之間必須有一定程度（10px左右）的留白」。本工具把 10px 當硬門檻，是本 repo 的嚴格解讀 |
| **背景透明度** | `Alpha Channel (RGBA)` | 官方原句：「請為圖片進行去背透明處理」，圖檔均為 PNG。「用 RGBA／alpha 通道實作」與「無雜色底色」是本 repo 的實作解讀，不是官方逐字規定 |
| **描邊規範** | 粗白外框（White Outline） | 約 $4 \sim 8\text{ px}$ 平滑白色貼圖描邊（本 repo 實踐推薦，防深色模式吃圖；非 Ann Cheng 原文原句） |
| **頭身比例** | 約 $2.5 \sim 3.0$ 頭身（$2.8$ 取自同作者另一則貼文，見第 7 節） | 頭大身小，兼具可愛度與五官辨識度；「Q 版 chibi」「2D 向量」是本 repo prompt 範本的選擇，原貼文的風格寫的是「超寫實精緻 Line 貼圖風」 |
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
         (同一生成批次上下文)    (特徵與風格較易一致，未驗證)   (機械裁切)   (合規交付)
```

### 1.1 核心痛點
1. **風格與身份漂移（Identity Drift）**：不同次生成會隨機取樣模型權重中的大眾臉，導致眼型、髮流、臉頰肉感與配件在每張貼圖間產生不一致。
2. **切圖與邊界失真**：手動裁剪往往因尺寸不固定、忘記預留 10px 餘白或去背殘留雜訊，被 LINE Creators Market 審核系統退件。
3. **文字排版破碎**：逐張生圖若讓模型自由發揮中文文字，容易出現缺字、簡體字或錯別字。

### 1.2 16 宮格提示詞工法價值
透過在單張畫布（$1480 \times 1280$）內定義 $4 \times 4$ 網格，讓模型在單次生成任務中輸出 16 種姿勢與表情。這是為了讓 16 格共用同一次生成的上下文，預期能降低分開多次獨立生成時的人物漂移（此為經驗推測，沒有對照實驗或一手數據；模型仍可能出現細微特徵浮動），同時在各分格賦予指定的情境動作與繁體中文字。

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
  - 官方貼圖製作準則（「圖片留白」一節）原句：「剪裁後的圖片與貼圖圖案之間必須有一定程度（10px左右）的留白，因此請在設計貼圖的同時考量上下左右的位置平衡。」官方用的是「必須」，數字寫「10px左右」。
  - 官方沒有說明留白的用意，也沒寫留白內容必須是透明像素；「避免被聊天氣泡遮蔽或圓角裁切」是本 repo 的推測用途。
  - 本 repo 的工具把單格四周各 $10\text{ px}$（Top, Bottom, Left, Right）內出現任何 alpha > 0 的像素視為違規，比官方「10px左右」更嚴格，是實作取捨。
  - 有效繪製內容安全區域建議為：$X \in [10, 360)$，寬度 $350\text{ px}$；$Y \in [10, 310)$，高度 $300\text{ px}$。
- **粗白外框（White Sticker Outline）**：
  - 角色本體與文字外圍建議具有 $4 \sim 8\text{ px}$ 的純白色實心描邊（`#FFFFFF`）。
  - 【原貼文內部的矛盾】：Ann Cheng 同一則貼文的主文既寫了「純白背景，間距清楚」，也寫了「一張完整透明排列圖(1480×1280)」與「輸出透明背景功能(png檔)可下載」。矛盾在貼文自己的前後兩句，不是貼文與 LINE 官方之間的差異：官方要求去背透明，貼文後半也要求透明。照做時以「透明背景」為準；貼文沒說如何從白底變透明，本 repo 也沒有驗證任何去背做法。
  - 查證範圍：貼文頁面（登出狀態）的主文與 var1、var2、var4 中找不到「外框」「白邊」「描邊」字樣，所以白色描邊與其 $4 \sim 8\text{ px}$ 寬度是本 repo 的建議（用意是避免深色聊天背景吃掉深色頭髮），沒有一手來源；var3 在該狀態看不到，沒有檢查。

---

## 3. 16 組高頻繁體中文字庫與動作對照表

本 repo 依台灣日常社群情境整理之 16 組高頻日常詞彙（原貼文的 var1、var2、var4 各列了 16 句，內容是「撥髮」「別蓋天花板」「恭喜」「生日快樂」等，與下表大部分不同，僅「感恩」「辛苦了」「OK」「加油」「太棒了」「恭喜」「生日快樂」等少數詞重疊；下表是本 repo 自行整理的擴充範例，不是原文詞庫）：

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

依據 LINE Creators Market 官方貼圖製作準則（2026-11-02 開頁核對，見第 7 節），製作與上架貼圖檔案時需符合以下項目：

```text
上架 ZIP 包結構
├── 01.png ~ 16.png  (貼圖本體，每張 W 370 × H 320 px，最大尺寸範圍)
├── main.png         (主圖 1 張，W 240 × H 240 px)
└── tab.png          (頁籤標籤圖 1 張，W 96 × H 74 px)
```

### 5.1 檔案規格表

| 檔案項目 | 檔名規則 | 寬高尺寸 | 檔案格式 | 背景要求 | 數量 |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **主圖 (Main)** | `main.png` | `240 × 240 px` | PNG（本 repo 輸出 RGBA） | 去背透明 | 1 張 |
| **貼圖圖片 (Stickers)** | `01.png` ~ `16.png` | `370 × 320 px`（上限） | PNG（本 repo 輸出 RGBA） | 去背透明 | 16 張（官方可選 8/16/24/32/40） |
| **標籤圖 (Tab)** | `tab.png` | `96 × 74 px` | PNG（本 repo 輸出 RGBA） | 去背透明 | 1 張 |

### 5.2 審核規則與避坑要點
1. **尺寸設為偶數**：官方原句「貼圖圖片大小將會自動縮小，故請將尺寸設為偶數」；單張貼圖大小標示為 $370 \times 320\text{ px}$「上限」（官方頁面沒有規定寬高其一必須達到上限）。
2. **邊距餘白（Safety Margin）**：官方原句「必須有一定程度（10px左右）的留白」。
3. **色彩模式**：官方原句「色彩模式請設為RGB」，並要求「去背透明處理」、圖檔均為 PNG。本 repo 以 RGBA PNG 實作透明；官方頁面沒有提到 CMYK。
4. **解析度**：至少 $72\text{ dpi}$ 以上。
5. **單檔與封包容量**：每張圖（含 main、tab）容量 1MB 以下；若把所有圖片壓成 1 個 ZIP 上傳，ZIP 須小於 60MB。
6. **內容限制**：官方製作準則頁寫明違規內容包含「違反善良風俗、教唆未成年者飲酒吸菸、猥褻、暴力、煽動民族主義的內容」，並禁止在貼圖圖片或文字內置入公告或企業商標；完整規則在另一頁「貼圖審核準則」，本次沒有開啟該頁，其餘審核細節未驗證。

---

## 6. 自動切圖工具對接操作手冊

本 repo 提供專用切圖與規格驗證工具 [`examples/slice_line_stickers.py`](../examples/slice_line_stickers.py)，可一鍵將生圖模型輸出的 $1480 \times 1280$ 排列圖切分並驗證合規：

### 6.1 基本執行指令
```bash
# 自動切分 16 宮格、檢查 10px 餘白與 Alpha 通道，並輸出 main.png 與 tab.png（不打包）
python examples/slice_line_stickers.py avatar_grid_1480x1280.png --out-dir output/stickers

# 嚴格模式並打包為上架 ZIP。任何一格不合格（含邊距溢出）時：仍會寫出 01~16.png 供檢視，
# 但 exit 1、不產生 ZIP，並會先刪掉同路徑上一輪留下的舊 ZIP
python examples/slice_line_stickers.py avatar_grid_1480x1280.png -o output/stickers --strict --zip output/line_stickers.zip
```

非 `--strict` 時，邊距溢出只是警告（exit 0）；但只要加了 `--zip` 而 ZIP 沒有產出，一律 exit 1，不會出現「通過卻沒有檔案」。

### 6.2 輸出報告範例
以下是對一張乾淨的 1480x1280 排列圖實跑的輸出（`--strict --zip`，exit 0；02~15 行格式同 01 與 16，省略）：

```text
[*] 讀取影像: avatar_grid_1480x1280.png (1480x1280, 模式: RGBA)
[*] 切割 4x4 宮格 (單格 370x320)...
  [PASS] ✅ 01.png (370x320) - 10px 安全邊距合規
  ...
  [PASS] ✅ 16.png (370x320) - 10px 安全邊距合規
[*] 合成主圖: output\stickers\main.png (240x240, 來源: 01.png) [OK]
[*] 合成標籤: output\stickers\tab.png (96x74, 來源: 01.png) [OK]
[*] 打包壓縮檔: output\line_stickers.zip [OK]
[SUCCESS] 🎉 全數貼圖與上架檔案切圖合規完成！
```

把第 2 格換成純白實心後的輸出（exit 1，沒有 ZIP，只節錄關鍵行）：

```text
  [FAIL] ❌ 02.png (370x320) - 安全區可見覆蓋率 100.0%（實心底／假透明）
[FAIL] ❌ 已要求 --zip 但未產生 ZIP 打包檔：output/line_stickers.zip（檢驗有 3 項錯誤；有格子邊距溢出）
[ERROR] 單格 02.png 安全區可見覆蓋率 100.0%（>= 95%），實心底或假透明，未去背
[FAIL] ❌ 未通過合規檢查，請檢視上述錯誤與警示。
```

### 6.3 判定規則與已知極限
下列門檻是本 repo 自訂的啟發式取捨，不是 LINE 官方數字；寧可誤擋也不放行明顯瑕疵。

| 檢查 | 判定 | 抓得到 | 抓不到或會誤擋 |
| :--- | :--- | :--- | :--- |
| 空白貼圖 | 單格「可見像素」（alpha ≥ 16）少於整格 1%（370x320 約 1184 個） | 完全透明、只剩 1 個雜點、整格 alpha=1 肉眼看不見 | 只佔整格 1% 以上的雜訊或碎屑仍會放行；真的很小的貼圖（低於 1%）會被誤擋 |
| 實心底／假透明 | 安全區（扣掉四周 margin）內可見像素覆蓋率 ≥ 95% | 16 格實心白框、整張 alpha=254 的白底、單格填滿 | 覆蓋率 95% 以下的大面積底色 |
| 疑似白底／棋盤格 | 可見像素有 ≥ 90% 是淺色無彩色（最小通道 ≥ 192、三通道差 ≤ 12） | 白色或淺灰（如 255/204 交替）的棋盤格，不論是否填滿安全區 | 深色或彩色的棋盤格、混有彩色內容使淺色佔比低於 90% 的假底；全白角色（如白色幽靈）會被誤擋 |
| 邊距 | 四周 margin 內任何 alpha > 0 的像素 | 見 `tests/test_slice_line_stickers.py` 的四向反例 | 官方只寫「10px左右」，工具以 10px 為硬門檻 |
| 色彩模式 | RGBA、LA、帶 transparency 的 P 視為有 alpha | 缺 alpha 的 RGB／L／P | 帶 tRNS 透明的 L／RGB 會被誤判為無 alpha（偏保守） |
| 打包閘門 | 無錯誤、邊距合規、`--margin` ≥ 10、main 與 tab 都產出、張數為 8/16/24/32/40、單格寬高為偶數且不超過 370x320、ZIP < 60MB | `--skip-main`／`--skip-tab`、3x3 九張、奇數寬、`--margin 0` | 圖片內容是否違反審核準則（要人工看） |

另外：`--strict` 搭配小於 10 的 `--margin` 直接失敗；輸出訊息顯示實際使用的 margin。「背景是否有雜色」這類肉眼項目工具查不到，需要人工看圖。

---

## 7. 一手來源與查證紀錄

| 項目 | 來源名稱 | 官方連結 / 一手網址 | 查證日期 | 查證事實說明 |
| :--- | :--- | :--- | :---: | :--- |
| **貼圖官方準則** | LINE Creators Market | [貼圖製作準則](https://creator.line.me/zh-hant/guideline/sticker/) | 2026-11-02 | 實際開頁（zh-hant）核對：主要圖片 240x240、聊天室標籤圖片 96x74、貼圖圖片 370x320「上限」、數量可選 8/16/24/32/40、各檔 1MB 以下、圖檔均為 PNG、請將尺寸設為偶數、72dpi 以上且色彩模式設為 RGB、ZIP 須小於 60MB、請做去背透明處理、留白原句「必須有一定程度（10px左右）的留白」。**未開啟**「貼圖審核準則」頁，審核細節未驗證 |
| **16宮格工法原創** | Ann Cheng | [貼文](https://www.threads.com/@anncheng_ann101/post/DfEB-BIEUGF)（短連結 [share](https://www.threads.com/share/BAgCwYB05Y/)） | 2026-11-02 | 以瀏覽器（登出狀態）開啟，讀到主文 (1/2) 與回覆 var1、var2、var4（各 16 句）；**var3 在登出狀態看不到，未檢查**。主文原句含：「約2.5～3頭身」「超寫實精緻Line貼圖風」「純白背景」「一張完整透明排列圖(1480×1280)，每一格透明貼圖比例為(370×320)」「上下左右各10px」「輸出透明背景功能(png檔)可下載」，「純白背景」與「透明」在同一則貼文並存。主文與 var1、var2、var4 中沒有「外框」「白邊」「描邊」。「2.8 頭身」出現在頁面「相關串文」中同作者另一則較新的貼文（3D 娃娃風格），不是本貼文。頁面上另有留言問「如何切割！」，貼文本身沒有提供切圖工具 |
| **影音實戰教學** | Ann Cheng YouTube | [頻道首頁](https://www.youtube.com/@ANNChengANN101) | 2026-11-02 | 頻道首頁無法佐證具體 16 宮格與拍貼教學細節，標為未驗證 |
