# Roadmap

## P0：產品方向固定

- [x] README 改成 local-first。
- [x] 明確排除 hosted backend。
- [x] 建立 `src/`、`app/`、`prompts/`、`packaging/`、`tests/`、`examples/` 骨架。
- [x] 保留 MIT attribution。

## P1：提示詞系統

- [x] `prompts/line-static-3x3.md` 建立 prompt template 格式。
- [x] `prompts/line-static-3x3.en.md` 建立英文 prompt template。
- [x] 提供 LINE 靜態貼圖 3x3 grid prompt。
- [x] 支援有字 / 無字。
- [x] 支援語言、角色、主題、動作、風格。
- [x] 支援 green / magenta chroma-key 背景。
- [x] 加入高風險內容提醒。

## P2：圖片處理核心

- [x] `src/sticker_forge/splitter.py` 匯入 3x3 grid。
- [x] 依 upstream 規則支援 3% inset 切 9 格。
- [x] CLI export 支援選 8 張。
- [x] `src/sticker_forge/cleanup.py` chroma-key 去背。
- [x] 支援 green / magenta chroma-key profile。
- [x] `src/sticker_forge/exporter.py` 尺寸整理與 padding。
- [x] 生成 main / tab image。
- [x] 預覽資料模型。

## P3：ZIP 匯出

- [x] `src/sticker_forge/exporter.py` 產生 LINE 靜態貼圖包 ZIP。
- [x] 產生 9 張 PNG-only ZIP，供非 LINE 上架用途使用。
- [x] 檔名、張數與尺寸檢查。
- [x] `validate` 指令檢查 ZIP 結構。
- [x] 保留 LINE Creators Market 手動上架/送審說明。
- [ ] 匯出前預覽。
- [ ] 更完整錯誤提示。

## P4：本機 app 與 exe

- [x] CLI 技術棧固定為 Python + Pillow。
- [x] 已建立最小可用 CLI。
- [x] CLI 支援 `--lang zh-Hant|en`。
- [x] 建立可直接開啟的本機 HTML 介面。
- [x] 本機 HTML 介面支援繁體中文 / English 切換。
- [x] 本機 HTML 介面可離線匯出 ZIP，不依賴 JSZip CDN。
- [x] 本機 HTML 介面可匯出 9 張 PNG-only ZIP。
- [x] 補 Windows exe 打包設定。
- [x] `sticker-forge app` 可從 CLI / exe 開啟本機 HTML 介面。
- [x] 補 release checklist。
- [x] 產生正式 Windows release artifact：`v0.1.0`。
- [x] GUI 或簡單本機介面封裝進 exe。
- [x] 建立英文 README：`README.en.md`。

## P5：Legacy 清理

- [x] 從 `reference/upstream-line-sticker-studio/` 抽出尺寸、切圖 inset、chroma-key、ZIP 與上架說明。
- [ ] 刪除不再需要的 `worker/` 參考。
- [ ] 移除 upstream hosted API 設定。
- [ ] 重製 icon、manifest、OG image。
- [ ] 清掉不符合 local-first 方向的 UI 文案。
