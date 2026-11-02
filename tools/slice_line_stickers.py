#!/usr/bin/env python3
"""
tools/slice_line_stickers.py
Ann Cheng 16 宮格 AI 似顏繪 LINE 貼圖自動切圖與規格驗證工具。
對應規範：docs/line-sticker-16-grid-prompt-spec.md
對應任務：T-20261031-02

功能：
1. 讀取 1480x1280 的透明排列圖，自動切出 16 張 370x320 PNG (01.png ~ 16.png)。
2. 檢查 Alpha Channel 透明通道、尺寸與四周 10px 安全邊距合規性。
3. 自動等比例縮放合成 main.png (240x240) 與 tab.png (96x74)。
4. 可選打包輸出為 LINE 上架 ZIP 壓縮包。

結束碼：
0: 成功且檢驗通過
1: 規格檢驗失敗（例如缺少 Alpha 通道、尺寸不符、或 --strict 模式下邊距違規）
2: 參數錯誤、檔案不存在、或缺少必要套件 Pillow
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None  # type: ignore
    PIL_AVAILABLE = False


def _utf8_stdio() -> None:
    """防止 Windows 終端在 cp950 編碼下因輸出特殊符號或中文崩潰。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


@dataclass
class MarginViolation:
    top: int = 0
    bottom: int = 0
    left: int = 0
    right: int = 0

    @property
    def total(self) -> int:
        return self.top + self.bottom + self.left + self.right

    def as_dict(self) -> Dict[str, int]:
        return {
            "top": self.top,
            "bottom": self.bottom,
            "left": self.left,
            "right": self.right,
            "total": self.total,
        }


@dataclass
class CellReport:
    index: int
    filename: str
    width: int
    height: int
    has_alpha: bool
    margin_ok: bool
    violations: MarginViolation

    def as_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "filename": self.filename,
            "width": self.width,
            "height": self.height,
            "has_alpha": self.has_alpha,
            "margin_ok": self.margin_ok,
            "violations": self.violations.as_dict(),
        }


@dataclass
class SlicingReport:
    input_path: str
    image_width: int
    image_height: int
    mode: str
    has_alpha: bool
    expected_cells: int
    sliced_cells: int
    main_created: bool
    tab_created: bool
    zip_created: Optional[str]
    all_margin_ok: bool
    cells: List[CellReport]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "input_path": self.input_path,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "mode": self.mode,
            "has_alpha": self.has_alpha,
            "expected_cells": self.expected_cells,
            "sliced_cells": self.sliced_cells,
            "main_created": self.main_created,
            "tab_created": self.tab_created,
            "zip_created": self.zip_created,
            "all_margin_ok": self.all_margin_ok,
            "cells": [c.as_dict() for c in self.cells],
        }


def check_cell_margins(cell_img: Any, margin: int = 10, alpha_threshold: int = 0) -> MarginViolation:
    """檢查單格貼圖四周 margin 像素內是否有非透明像素 (alpha > alpha_threshold)。"""
    if cell_img.mode != "RGBA":
        return MarginViolation()

    w, h = cell_img.size
    alpha = cell_img.getchannel("A")
    get_data_fn = getattr(alpha, "get_flattened_data", None)
    if get_data_fn is not None:
        alpha_data = list(get_data_fn())
    else:
        alpha_data = list(alpha.getdata())

    top_count = 0
    bottom_count = 0
    left_count = 0
    right_count = 0

    # 檢查上方 (y < margin)
    for y in range(min(margin, h)):
        row_offset = y * w
        for x in range(w):
            if alpha_data[row_offset + x] > alpha_threshold:
                top_count += 1

    # 檢查下方 (y >= h - margin)
    for y in range(max(0, h - margin), h):
        row_offset = y * w
        for x in range(w):
            if alpha_data[row_offset + x] > alpha_threshold:
                bottom_count += 1

    # 檢查左方 (x < margin，排除上下邊界避免重複計數)
    for y in range(margin, max(margin, h - margin)):
        row_offset = y * w
        for x in range(min(margin, w)):
            if alpha_data[row_offset + x] > alpha_threshold:
                left_count += 1

    # 檢查右方 (x >= w - margin，排除上下邊界避免重複計數)
    for y in range(margin, max(margin, h - margin)):
        row_offset = y * w
        for x in range(max(0, w - margin), w):
            if alpha_data[row_offset + x] > alpha_threshold:
                right_count += 1

    return MarginViolation(
        top=top_count,
        bottom=bottom_count,
        left=left_count,
        right=right_count,
    )


def create_fitted_canvas(
    source_img: Any, target_size: Tuple[int, int]
) -> Any:
    """將 source_img 等比例縮放並置中貼於指定 target_size 的全新全透明 RGBA 畫布。"""
    target_w, target_h = target_size
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))

    src_w, src_h = source_img.size
    if src_w == 0 or src_h == 0:
        return canvas

    ratio = min(target_w / src_w, target_h / src_h)
    new_w = max(1, int(round(src_w * ratio)))
    new_h = max(1, int(round(src_h * ratio)))

    resample_filter = getattr(Image, "Resampling", Image).LANCZOS
    resized = source_img.resize((new_w, new_h), resample=resample_filter)

    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y), mask=resized if resized.mode == "RGBA" else None)
    return canvas


def slice_line_stickers(
    input_path: Path | str,
    out_dir: Path | str,
    rows: int = 4,
    cols: int = 4,
    cell_width: int = 370,
    cell_height: int = 320,
    margin: int = 10,
    main_index: int = 1,
    tab_index: int = 1,
    skip_main: bool = False,
    skip_tab: bool = False,
    zip_path: Optional[Path | str] = None,
) -> SlicingReport:
    """執行 16 宮格切圖、驗證與縮圖合成。"""
    if not PIL_AVAILABLE or Image is None:
        raise RuntimeError("缺少必要第三方套件 Pillow (PIL)。請執行 pip install Pillow 安裝依賴。")

    src_file = Path(input_path)
    if not src_file.is_file():
        raise FileNotFoundError(f"輸入檔案不存在：{src_file}")

    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_file)
    w, h = img.size
    has_alpha = img.mode == "RGBA"

    expected_total = rows * cols
    expected_w = cols * cell_width
    expected_h = rows * cell_height

    # 若輸入影像小於網格總尺寸，貼上足額畫布以防 crop 座標越界，同時維持原尺寸記錄
    if w < expected_w or h < expected_h:
        padded_canvas = Image.new("RGBA", (max(w, expected_w), max(h, expected_h)), (0, 0, 0, 0))
        padded_canvas.paste(img, (0, 0), mask=img if img.mode == "RGBA" else None)
        working_img = padded_canvas
    else:
        working_img = img

    cells_reports: List[CellReport] = []
    sliced_images: Dict[int, Any] = {}
    all_margin_ok = True

    # 執行單格裁切與驗證
    for idx in range(1, expected_total + 1):
        col = (idx - 1) % cols
        row = (idx - 1) // cols

        left = col * cell_width
        top = row * cell_height
        right = left + cell_width
        bottom = top + cell_height

        box = (left, top, right, bottom)
        cell_img = working_img.crop(box)

        # 確保單格尺寸精確為 cell_width x cell_height
        if cell_img.size != (cell_width, cell_height):
            fixed_cell = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))
            fixed_cell.paste(cell_img, (0, 0), mask=cell_img if cell_img.mode == "RGBA" else None)
            cell_img = fixed_cell

        violations = check_cell_margins(cell_img, margin=margin)
        margin_ok = violations.total == 0
        if not margin_ok:
            all_margin_ok = False

        fname = f"{idx:02d}.png"
        out_path = target_dir / fname
        cell_img.save(out_path, format="PNG")
        sliced_images[idx] = cell_img

        cells_reports.append(
            CellReport(
                index=idx,
                filename=fname,
                width=cell_img.size[0],
                height=cell_img.size[1],
                has_alpha=cell_img.mode == "RGBA",
                margin_ok=margin_ok,
                violations=violations,
            )
        )

    # 產生 main.png (240x240)
    main_created = False
    if not skip_main:
        src_for_main = sliced_images.get(main_index) or sliced_images.get(1)
        if src_for_main:
            main_canvas = create_fitted_canvas(src_for_main, (240, 240))
            main_path = target_dir / "main.png"
            main_canvas.save(main_path, format="PNG")
            main_created = True

    # 產生 tab.png (96x74)
    tab_created = False
    if not skip_tab:
        src_for_tab = sliced_images.get(tab_index) or sliced_images.get(1)
        if src_for_tab:
            tab_canvas = create_fitted_canvas(src_for_tab, (96, 74))
            tab_path = target_dir / "tab.png"
            tab_canvas.save(tab_path, format="PNG")
            tab_created = True

    # 打包 ZIP
    created_zip_file: Optional[str] = None
    if zip_path:
        zip_p = Path(zip_path)
        zip_p.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_p, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for c in cells_reports:
                fpath = target_dir / c.filename
                if fpath.exists():
                    zf.write(fpath, arcname=c.filename)
            if main_created and (target_dir / "main.png").exists():
                zf.write(target_dir / "main.png", arcname="main.png")
            if tab_created and (target_dir / "tab.png").exists():
                zf.write(target_dir / "tab.png", arcname="tab.png")
        created_zip_file = str(zip_p)

    return SlicingReport(
        input_path=str(src_file),
        image_width=w,
        image_height=h,
        mode=img.mode,
        has_alpha=has_alpha,
        expected_cells=expected_total,
        sliced_cells=len(cells_reports),
        main_created=main_created,
        tab_created=tab_created,
        zip_created=created_zip_file,
        all_margin_ok=all_margin_ok,
        cells=cells_reports,
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Ann Cheng 16 宮格 AI 似顏繪 LINE 貼圖自動切圖與規格驗證工具"
    )
    ap.add_argument("input", help="輸入的大圖檔案路徑 (例如 1480x1280 PNG)")
    ap.add_argument("-o", "--out-dir", default="output", help="輸出目錄 (預設: output)")
    ap.add_argument("--rows", type=int, default=4, help="橫列數 (預設: 4)")
    ap.add_argument("--cols", type=int, default=4, help="直行數 (預設: 4)")
    ap.add_argument("--cell-width", type=int, default=370, help="單格寬度 (預設: 370)")
    ap.add_argument("--cell-height", type=int, default=320, help="單格高度 (預設: 320)")
    ap.add_argument("--margin", type=int, default=10, help="安全邊距像素 (預設: 10)")
    ap.add_argument("--main-index", type=int, default=1, help="指定合成 main.png 之貼圖序號 (1-16, 預設: 1)")
    ap.add_argument("--tab-index", type=int, default=1, help="指定合成 tab.png 之貼圖序號 (1-16, 預設: 1)")
    ap.add_argument("--skip-main", action="store_true", help="跳過產生 main.png")
    ap.add_argument("--skip-tab", action="store_true", help="跳過產生 tab.png")
    ap.add_argument("--zip", dest="zip_path", default=None, help="打包上架 ZIP 檔案路徑")
    ap.add_argument("--strict", action="store_true", help="嚴格模式：邊距違規或格式不符直接回傳 exit 1")
    ap.add_argument("--json", action="store_true", help="輸出 JSON 格式報告")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    _utf8_stdio()
    args = build_parser().parse_args(argv)

    if not PIL_AVAILABLE or Image is None:
        err_msg = "錯誤：缺少必要第三方套件 'Pillow' (PIL)。請執行 'pip install Pillow' 安裝依賴。"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "MISSING_PILLOW"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    in_path = Path(args.input)
    if not in_path.is_file():
        err_msg = f"錯誤：輸入檔案不存在或不是檔案：{in_path}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "FILE_NOT_FOUND"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    expected_w = args.cols * args.cell_width
    expected_h = args.rows * args.cell_height

    try:
        report = slice_line_stickers(
            input_path=in_path,
            out_dir=args.out_dir,
            rows=args.rows,
            cols=args.cols,
            cell_width=args.cell_width,
            cell_height=args.cell_height,
            margin=args.margin,
            main_index=args.main_index,
            tab_index=args.tab_index,
            skip_main=args.skip_main,
            skip_tab=args.skip_tab,
            zip_path=args.zip_path,
        )
    except Exception as ex:
        err_msg = f"錯誤：切圖執行異常：{ex}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "EXECUTION_ERROR"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    is_size_exact = (report.image_width == expected_w and report.image_height == expected_h)
    has_alpha = report.has_alpha
    all_margin_ok = report.all_margin_ok

    passed = has_alpha and is_size_exact and (all_margin_ok or not args.strict)

    if args.json:
        data = report.as_dict()
        data["is_size_exact"] = is_size_exact
        data["passed"] = passed
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"[*] 讀取影像: {report.input_path} ({report.image_width}x{report.image_height}, 模式: {report.mode})")
        if not has_alpha:
            print(f"[FAIL] ❌ 缺少 Alpha 通道！目前模式為 {report.mode}，LINE 貼圖必須為 RGBA 透明背景。")
        if not is_size_exact:
            print(f"[WARN] ⚠️ 影像尺寸 ({report.image_width}x{report.image_height}) 與預期 ({expected_w}x{expected_h}) 不一致。")

        print(f"[*] 切割 {args.rows}x{args.cols} 宮格 (單格 {args.cell_width}x{args.cell_height})...")
        for c in report.cells:
            status = "[PASS] ✅" if c.margin_ok else "[WARN] ⚠️"
            margin_info = "10px 安全邊距合規" if c.margin_ok else f"邊距溢出 {c.violations.total} px (T:{c.violations.top} B:{c.violations.bottom} L:{c.violations.left} R:{c.violations.right})"
            print(f"  {status} {c.filename} ({c.width}x{c.height}) - {margin_info}")

        if report.main_created:
            print(f"[*] 合成主圖: {Path(args.out_dir) / 'main.png'} (240x240, 來源: {args.main_index:02d}.png) [OK]")
        if report.tab_created:
            print(f"[*] 合成標籤: {Path(args.out_dir) / 'tab.png'} (96x74, 來源: {args.tab_index:02d}.png) [OK]")
        if report.zip_created:
            print(f"[*] 打包壓縮檔: {report.zip_created} [OK]")

        if passed:
            print("[SUCCESS] 🎉 全數貼圖與上架檔案切圖合規完成！")
        else:
            print("[FAIL] ❌ 切圖完成但未通過合規檢查，請檢視上述警示。")

    # 判定 exit code
    if not has_alpha:
        return 1
    if not is_size_exact and args.strict:
        return 1
    if not all_margin_ok and args.strict:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
