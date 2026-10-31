---
id: 2026-10-31-line-sticker-16-grid-ai-avatar-prompt-spec
title: "Ann Cheng AI 似顏繪 16 宮格 LINE 貼圖 Prompt 工程：角色定裝、透明排列圖與自動切圖上架規格"
source_url: "https://www.threads.com/share/BAgCwYB05Y/"
source_platform: "Threads (@anncheng_ann101) / YouTube"
author: "Ann Cheng (安總監 / 安老師, @anncheng_ann101)"
analyzed_at: 2026-10-31
analyzed_by: "Antigravity"
status: pending
cluster: 2
cluster_role: "貼圖工程"
short_title: "Ann Cheng 16宮格似顏繪貼圖規格"
tags:
  - line-stickers
  - avatar-prompt-engineering
  - 16-grid-layout
  - identity-consistency
  - alpha-channel-transparency
  - automated-image-slicing
  - visual-generation
---

# Ann Cheng AI 似顏繪 16 宮格 LINE 貼圖 Prompt 工程：角色定裝、透明排列圖與自動切圖上架規格

- **來源連結**：[Threads 原文分享 (@anncheng_ann101)](https://www.threads.com/share/BAgCwYB05Y/) ｜ [貼文永久網址](https://www.threads.com/@anncheng_ann101/post/DfEB-BIEUGF) ｜ [作者 YouTube 實戰教學 (Line透明貼圖16宮格+Line拍貼上架)](https://www.youtube.com/@ANNChengANN101)
- **核心作者**：Ann Cheng（安總監 / 安老師，企業數位長、雙軌轉型顧問與生成式 AI 實戰講師）
- **分析主題**：利用單一 Prompt 達成高一致性似顏繪（Q版 chibi 2.8 頭身）角色定裝、鎖定真實人物五官髮型、1480×1280 總尺寸精確劃分 16 宮格透明排列圖（單格 370×320）、四周 10px 安全邊距防裁切、粗白貼圖外框可讀性規範、16 組高頻日常繁體中文字情境搭配、以及將多宮格排列圖自動化切割為 LINE 官方規範檔案（01~16.png、main.png 240×240、tab.png 96×74）的端到端工程管線
- **當前狀態**：`🔴 待辦處理中 (Pending)`
- **相關交叉參照**：
  - [`notes/2026-10-28-motion-design-agent-harness-opus-55.md`](./2026-10-28-motion-design-agent-harness-opus-55.md)（0xalpha 代碼驅動動效與視覺 Anti-Slop 規範）
  - [`notes/2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md`](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md)（Going Li 五路工具流：ROAD 02 做圖像、公仔與 LINE 貼圖流程）
  - [`notes/2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md`](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md)（Thorsten Ball 15 條 Agent 實戰哲學：為 Agent 打造試錯工具與確定性交付）

---

## 1. 核心內容摘要：問題背景與 16 宮格提示詞全貌（Executive Summary）

在利用 AI 製作個人品牌似顏繪或商業 LINE 貼圖時，創作者常面臨兩大核心障礙：
1. **單張生成導致風格漂移（Style & Identity Drift）**：若逐張獨立生成 16 或 24 張貼圖，模型在不同會話中容易產生臉型胖瘦不一、髮型變異、色彩風格迥異等問題，難以維持角色識別度。
2. **切圖與上架規格繁瑣**：LINE Creators Market 對貼圖的尺寸（最大 W370 × H320）、邊緣留白（四周 10px）、透明背景（Alpha Channel）以及主圖（main.png 240×240）、標籤圖（tab.png 96×74）有嚴格機械要求，人工手動裁切去背耗時且極易出錯。

企業數位長 Ann Cheng（安老師）提出了一套極致標準化的 **「AI 似顏繪 16 宮格透明貼圖 Prompt 工程」**，透過單張圖一次性生成 16 格統一角色風格的排列圖：

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                     Ann Cheng AI 似顏繪 16 宮格貼圖端到端工程管線全貌                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  [ 輸入端：真人參考照片 ] ──► 鎖定真實五官、髮型與眼鏡特徵                                     │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 提示詞工程約束 (Prompt Engineering) ]                                                        │
│  ├─ 角色定裝：Q版 chibi、約 2.5～3 頭身 (最佳 2.8 頭身)、頭大身小、可愛中帶霸氣                │
│  ├─ 排列圖尺寸：整體 1480 × 1280 px，劃分 4 × 4 = 16 宮格                                       │
│  ├─ 單格尺寸：每格透明貼圖精確佔比 370 × 320 px                                                 │
│  ├─ 安全邊界：每格四周嚴格保留各 10px 安全距離，文字與手勢嚴禁超出格線                          │
│  ├─ 視覺可讀性：角色保留粗白貼圖外框 (Sticker Outline)，支援深色/淺色/壁紙聊天背景              │
│  └─ 繁體中文字：16 組高頻日常詞彙，字體醒目清晰，手勢與服裝隨文意微調                          │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 生成產物：1480 × 1280 透明 PNG 排列圖 ]                                                      │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 自動化切圖與規格轉換工具 (slice_line_stickers.py) ]                                          │
│  ├─ 自動機械切分：沿 (370×320) 格線切出 16 張獨立 PNG (01.png ~ 16.png)                        │
│  ├─ 自動合成主圖：挑選代表性貼圖自動縮放為 main.png (240 × 240 px)                             │
│  ├─ 自動合成標籤：挑選頭部特寫縮放為 tab.png (96 × 74 px)                                      │
│  └─ 格式合規校驗：檢查每張圖四周 10px 餘白與 Alpha Channel 透明通道                             │
│      │                                                                                          │
│      ▼                                                                                          │
│  [ 交付輸出：LINE 上架專用 ZIP 包 ] ──► 一鍵匯入 LINE 拍貼或 Creators Market 上架             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 深入技術拆解：三大核心實戰規範（Deep Dive）

### 2.1 規範一：角色鎖臉（Identity Retention）與 2.8 頭身視覺語法
- **唯一身份約束（Single Identity Reference）**：
  - 提示詞首句開門見山：「請使用我上傳的真人照片作為唯一人物身份參考，保留本人真實五官和髮型。」
  - 杜絕模型隨機引入訓練集大眾臉，鎖定使用者的真實長相特徵（眼形、臉型特徵、髮流與眼鏡）。
- **黃金比例頭身比**：
  - 約 2.5～3 頭身（實測 2.8 頭身最佳），頭大身小。
  - 特色：既具備 Q 版的親和力與幽默感，又因保留真人五官而具備強烈的個人 IP 辨識度。

### 2.2 規範二：16 宮格精確數學比例與貼圖可讀性設計
- **像素尺寸與網格數學**：
  $$\text{總寬度} = 370 \text{ px} \times 4 \text{ 列} = 1480 \text{ px}$$
  $$\text{總高度} = 320 \text{ px} \times 4 \text{ 行} = 1280 \text{ px}$$
  此尺寸正好滿足 LINE 官方貼圖單張最大寬高上限（W370 × H320），切割後無需重複放大失真。
- **四周 10px 安全邊界（Safety Margin）**：
  - LINE 官方審核規定貼圖與邊框必須保留至少 10px 餘白，避免貼圖在聊天室貼齊氣泡時被截斷。
  - 提示詞硬性規定：「務必遵守手勢文字不要超出格線，每格間保持安全距離（上下左右各 10px）。」
- **粗白外框（White Sticker Outline）**：
  - 由於使用者的手機聊天室背景多變（淺色、深色夜間模式、風景照片等），貼圖邊緣帶有柔和粗白描邊，是確保黑色頭髮與深色文字在任何壁紙下皆清晰可見的行業標準實踐。

### 2.3 規範三：16 組高頻繁體中文字庫與動作對照表
Ann Cheng 提煉之 16 組高頻日常繁體中文字庫，完全覆蓋職場溝通、朋友問候與禮貌社交情境：

| 編號 | 繁體中文文案 | 推薦情境手勢與動作設計 | 角色表情氛圍 |
| :---: | :--- | :--- | :--- |
| `01` | **早安** | 精神飽滿揮手、手持熱咖啡或陽光灑落 | 微笑、朝氣蓬勃 |
| `02` | **晚安** | 抱枕頭、拉棉被或帶睡帽打呵欠 | 甜美放鬆、眼帶倦意 |
| `03` | **收到** | 立正敬禮或雙手比「了解」手勢 | 俐落認真、值得信賴 |
| `04` | **謝謝** | 雙手合十、微微鞠躬點頭 | 誠懇溫暖 |
| `05` | **感恩** | 手放胸前、眼帶感動閃爍亮光 | 溫柔真誠 |
| `06` | **辛苦了** | 遞上熱茶、敲肩膀或比打氣手勢 | 貼心撫慰 |
| `07` | **不客氣** | 擺擺手、大方爽朗笑開 | 瀟灑親切 |
| `08` | **太棒了** | 雙手高舉歡呼、背景帶小彩帶 | 興奮喝采 |
| `09` | **加油** | 握拳打氣、手部帶動態速度線 | 堅定熱情 |
| `10` | **稍後回覆** | 手指飛快敲鍵盤或看手錶趕路 | 專注急忙 |
| `11` | **好心肝** | 雙手比大愛心、眨眼幽默 | 幽默霸氣、可愛撩人 |
| `12` | **OK** | 雙手或單手比出清晰標準 OK 圈圈手勢 | 信心滿滿 |
| `13` | **週休快樂** | 墨鏡、拿冷飲或背旅行背包 | 悠閒度假風 |
| `14` | **假期愉快** | 揮動小旗子或比出歡慶手勢 | 放鬆愉悅 |
| `15` | **生日快樂** | 戴生日帽、捧著插蠟燭的蛋糕 | 喜慶燦爛 |
| `16` | **恭喜** | 雙手抱拳拱手祝賀或拉彩炮 | 熱鬧喜氣 |

---

## 3. 本地化評估與採用決策（Adoption Decision）

- **與現有體系（`ai-inbox` / `agent-assets`）的契合度**：
  1. **補齊個人工作台的「視覺資產生成」缺口**：
     - 在 Going Li 的五路工具流中，ROAD 02 明確定義了「做圖像、LINE 貼圖、角色表」的管線；Ann Cheng 的 16 宮格規範正好提供了最高效的 Prompt 工法。
  2. **工程化閉環（Automated Slicing & Verification）**：
     - 現況下多數使用者卡在「生出大圖卻不會切圖、切完不合規格被退件」。
     - 透過開發專屬 Python 切圖與驗證工具（`tools/slice_line_stickers.py`），可機械化裁切 16 宮格並產出 `main.png` 與 `tab.png`，補上交付的最後一哩路。

---

## 4. 拆解待辦事項（Action Items）

> ⚠️ 本節是任務的唯一資料來源：改完執行 `python tools/build_index.py` 重產 [`README.md`](../README.md) 總表。

- [ ] **`T-20261031-01`**｜**[優先級：高]** 撰寫「AI 似顏繪 LINE 16 宮格貼圖 Prompt 工程與視覺規範」收錄於 `docs/line-sticker-16-grid-prompt-spec.md`
  - **目標範圍**：`docs/line-sticker-16-grid-prompt-spec.md`（規範文檔；不修改其他專案程式）
  - **具體做法**：
    1. 詳細定義角色鎖臉（Face Retention）提示詞結構與 2.8 頭身 Q 版風格約束。
    2. 制定 1480×1280 (單格 370×320) 排列圖、10px 安全邊距、粗白邊框與 Alpha Channel 透明規格。
    3. 整理 16 組繁體中文高頻社交詞與對應情境動作設計表。
    4. 納入 LINE Creators Market 上架技術規範清單（主圖 240×240、標籤圖 96×74、貼圖 370×320）。
  - **驗收標準（DoD）**：產出 `docs/line-sticker-16-grid-prompt-spec.md`，內含完整提示詞範本、尺寸規格表與上架規範；以 `Test-Path docs/line-sticker-16-grid-prompt-spec.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-02`**｜**[優先級：中]** 實作「LINE 16 宮格貼圖自動切圖與規格驗證工具」於 `tools/slice_line_stickers.py`
  - **目標範圍**：`tools/slice_line_stickers.py` 與 `tests/test_slice_line_stickers.py`
  - **具體做法**：
    1. 實作命令列工具，讀取 1480×1280 的透明排列圖，自動切出 16 張 370×320 PNG（命名為 `01.png`~`16.png`）。
    2. 支援自動生成 `main.png`（240×240）與 `tab.png`（96×74）。
    3. 檢查 Alpha Channel 透明通道、尺寸與邊緣安全距離合規性。
    4. 撰寫單元測試覆蓋有效切割、非法尺寸防禦與透明通道檢查。
  - **驗收標準（DoD）**：產出 `tools/slice_line_stickers.py` 與單元測試，執行 `python -m unittest discover -s tests` 全綠通過。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

- [ ] **`T-20261031-03`**｜**[優先級：低]** 產出標準化「AI 似顏繪貼圖工廠 Skill 範本（Avatar-Sticker-Factory）」收錄於 `templates/avatar-sticker-factory-skill.md`
  - **目標範圍**：`templates/avatar-sticker-factory-skill.md`
  - **具體做法**：
    1. 產出可直接供 Claude Code、Antigravity 或其他 Agent 引入的 Skill 範本。
    2. 整合「真人照片輸入 $\rightarrow$ 16宮格 Prompt 生成 $\rightarrow$ 切圖腳本調用 $\rightarrow$ LINE 上架 ZIP 包輸出」端到端指令流。
  - **驗收標準（DoD）**：產出 `templates/avatar-sticker-factory-skill.md`，具備標準 YAML frontmatter 與完整執行步驟；以 `Test-Path templates/avatar-sticker-factory-skill.md` 驗證存在。
  - **實作紀錄 / 證據**：*（待完成後由執行 Agent 填寫）*

---

## 5. 關聯筆記與相關任務（Related Notes & Tasks）

- **多 Agent 協同與產出路徑**：
  - [Going Li 四 Agent 派工協定與五路工具流](./2026-10-28-multi-agent-team-dispatch-five-roads-going-li.md) ｜ 關聯任務：`T-20261028-10`、`T-20261028-11`
- **動效與視覺 Anti-Slop 規範**：
  - [0xalpha 代碼驅動 Motion Design Agent Harness 解構](./2026-10-28-motion-design-agent-harness-opus-55.md) ｜ 關聯任務：`T-20261028-16`、`T-20261028-17`
- **確定性交付與工具打造**：
  - [Thorsten Ball 15 條 Agent 實戰哲學](./2026-10-28-thorsten-ball-how-i-work-with-agents-2026.md) ｜ 關聯任務：`T-20261028-04`、`T-20261028-05`
