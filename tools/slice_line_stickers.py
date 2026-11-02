#!/usr/bin/env python3
"""
tools/slice_line_stickers.py
Ann Cheng 16 宮格 AI 似顏繪 LINE 貼圖自動切圖與規格驗證工具。
對應規範：docs/line-sticker-16-grid-prompt-spec.md
對應任務：T-20261031-02

功能：
1. 讀取 1480x1280 的透明排列圖，自動切出 16 張 370x320 PNG (01.png ~ 16.png)。
2. 檢查 Alpha Channel 透明通道、實質去背透明度、尺寸與四周 10px 安全邊距合規性。
3. 檢查單張檔案大小不超過 1MB 上限，防範全透明空白或全不透明實心貼圖。
4. 自動等比例縮放合成 main.png (240x240) 與 tab.png (96x74)。
5. 檢驗全數合規時可選打包輸出為 LINE 上架 ZIP 壓縮包（未通過合規不予打包）。

結束碼：
0: 成功且檢驗通過（或非 strict 模式下僅邊距警告放行）
1: 規格檢驗失敗（缺少 Alpha 通道、全無透明去背、尺寸不符、空圖、全實心圖、超限 1MB、或 --strict 模式下邊距違規）
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
    is_empty: bool
    is_fully_opaque: bool
    margin_ok: bool
    violations: MarginViolation
    file_size_bytes: int
    exceeds_1mb: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "filename": self.filename,
            "width": self.width,
            "height": self.height,
            "has_alpha": self.has_alpha,
            "is_empty": self.is_empty,
            "is_fully_opaque": self.is_fully_opaque,
            "margin_ok": self.margin_ok,
            "violations": self.violations.as_dict(),
            "file_size_bytes": self.file_size_bytes,
            "exceeds_1mb": self.exceeds_1mb,
        }


@dataclass
class SlicingReport:
    input_path: str
    image_width: int
    image_height: int
    mode: str
    has_alpha: bool
    has_transparent_pixels: bool
    expected_cells: int
    sliced_cells: int
    main_created: bool
    tab_created: bool
    zip_created: Optional[str]
    all_margin_ok: bool
    all_cells_valid: bool
    cells: List[CellReport]
    errors: List[str]
    warnings: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "input_path": self.input_path,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "mode": self.mode,
            "has_alpha": self.has_alpha,
            "has_transparent_pixels": self.has_transparent_pixels,
            "expected_cells": self.expected_cells,
            "sliced_cells": self.sliced_cells,
            "main_created": self.main_created,
            "tab_created": self.tab_created,
            "zip_created": self.zip_created,
            "all_margin_ok": self.all_margin_ok,
            "all_cells_valid": self.all_cells_valid,
            "cells": [c.as_dict() for c in self.cells],
            "errors": self.errors,
            "warnings": self.warnings,
        }


def check_cell_margins(cell_img: Any, margin: int = 10, alpha_threshold: int = 0) -> MarginViolation:
    """檢查單格貼圖四周 margin 像素內是否有非透明像素 (alpha > alpha_threshold)。"""
    if cell_img.mode != "RGBA":
        cell_img = cell_img.convert("RGBA")

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
    strict: bool = False,
) -> SlicingReport:
    """執行 16 宮格切圖、驗證與縮圖合成。"""
    if not PIL_AVAILABLE or Image is None:
        raise RuntimeError("缺少必要第三方套件 Pillow (PIL)。請執行 pip install Pillow 安裝依賴。")

    if margin < 0:
        raise ValueError(f"安全邊距 (--margin) 必須為非負整數，收到: {margin}")

    expected_total = rows * cols
    if not (1 <= main_index <= expected_total):
        raise ValueError(f"--main-index 必須介於 1 到 {expected_total} 之間，收到: {main_index}")
    if not (1 <= tab_index <= expected_total):
        raise ValueError(f"--tab-index 必須介於 1 到 {expected_total} 之間，收到: {tab_index}")

    src_file = Path(input_path)
    if not src_file.is_file():
        raise FileNotFoundError(f"輸入檔案不存在：{src_file}")

    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    img = Image.open(src_file)
    w, h = img.size
    orig_mode = img.mode

    errors: List[str] = []
    warnings: List[str] = []

    # 辨識並處理 Alpha 通道（支援 RGBA, LA, 具備 transparency 之 P 模式）
    has_alpha_channel = False
    if orig_mode == "RGBA":
        has_alpha_channel = True
        working_base = img
    elif orig_mode == "LA":
        has_alpha_channel = True
        working_base = img.convert("RGBA")
    elif orig_mode == "P" and "transparency" in img.info:
        has_alpha_channel = True
        working_base = img.convert("RGBA")
    else:
        has_alpha_channel = False
        working_base = img.convert("RGBA")
        errors.append(f"影像缺少 Alpha 通道（目前模式為 {orig_mode}，LINE 貼圖強制要求 RGBA 透明背景）")

    # 檢查實質去背透明度：若全圖所有像素 Alpha 均為 255，屬於未去背的假透明圖
    alpha_channel = working_base.getchannel("A")
    alpha_min, alpha_max = alpha_channel.getextrema()
    has_transparent_pixels = (alpha_min < 255)
    if not has_transparent_pixels:
        errors.append("影像完全無任何透明像素（所有像素皆為不透明實心），未去背處理")

    expected_w = cols * cell_width
    expected_h = rows * cell_height
    if w != expected_w or h != expected_h:
        errors.append(f"影像尺寸 ({w}x{h}) 與預期網格規格 ({expected_w}x{expected_h}) 不一致")

    # 若輸入影像小於網格總尺寸，補齊透明畫布以防 crop 越界
    if w < expected_w or h < expected_h:
        padded_canvas = Image.new("RGBA", (max(w, expected_w), max(h, expected_h)), (0, 0, 0, 0))
        padded_canvas.paste(working_base, (0, 0), mask=working_base)
        working_img = padded_canvas
    else:
        working_img = working_base

    cells_reports: List[CellReport] = []
    sliced_images: Dict[int, Any] = {}
    all_margin_ok = True
    all_cells_valid = True

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
            fixed_cell.paste(cell_img, (0, 0), mask=cell_img)
            cell_img = fixed_cell

        # 檢查單格內容實質性
        cell_bbox = cell_img.getbbox()
        is_empty = (cell_bbox is None)
        if is_empty:
            all_cells_valid = False
            errors.append(f"單格 {idx:02d}.png 為完全透明空白圖，無貼圖內容")

        cell_alpha = cell_img.getchannel("A")
        c_min, c_max = cell_alpha.getextrema()
        is_fully_opaque = (c_min == 255)
        if is_fully_opaque:
            all_cells_valid = False
            errors.append(f"單格 {idx:02d}.png 完全無透明背景（全像素不透明），未去背")

        violations = check_cell_margins(cell_img, margin=margin)
        margin_ok = (violations.total == 0) and not is_empty and not is_fully_opaque
        if violations.total > 0:
            all_margin_ok = False

        fname = f"{idx:02d}.png"
        out_path = target_dir / fname
        cell_img.save(out_path, format="PNG")
        sliced_images[idx] = cell_img

        file_size = os.path.getsize(out_path)
        exceeds_1mb = file_size > 1024 * 1024
        if exceeds_1mb:
            all_cells_valid = False
            errors.append(f"單格 {idx:02d}.png 容量 ({file_size} bytes) 超過 1MB 官方上限")

        cells_reports.append(
            CellReport(
                index=idx,
                filename=fname,
                width=cell_img.size[0],
                height=cell_img.size[1],
                has_alpha=has_alpha_channel,
                is_empty=is_empty,
                is_fully_opaque=is_fully_opaque,
                margin_ok=margin_ok,
                violations=violations,
                file_size_bytes=file_size,
                exceeds_1mb=exceeds_1mb,
            )
        )

    # 產生 main.png (240x240)
    main_created = False
    if not skip_main:
        src_for_main = sliced_images.get(main_index)
        if src_for_main:
            main_canvas = create_fitted_canvas(src_for_main, (240, 240))
            main_path = target_dir / "main.png"
            main_canvas.save(main_path, format="PNG")
            main_size = os.path.getsize(main_path)
            if main_size > 1024 * 1024:
                all_cells_valid = False
                errors.append(f"主圖 main.png 容量 ({main_size} bytes) 超過 1MB 上限")
            main_created = True

    # 產生 tab.png (96x74)
    tab_created = False
    if not skip_tab:
        src_for_tab = sliced_images.get(tab_index)
        if src_for_tab:
            tab_canvas = create_fitted_canvas(src_for_tab, (96, 74))
            tab_path = target_dir / "tab.png"
            tab_canvas.save(tab_path, format="PNG")
            tab_size = os.path.getsize(tab_path)
            if tab_size > 1024 * 1024:
                all_cells_valid = False
                errors.append(f"標籤 tab.png 容量 ({tab_size} bytes) 超過 1MB 上限")
            tab_created = True

    # 打包 ZIP：僅在無重大錯誤且全數邊距與規格皆合規時才打包（瑕疵圖絕不打包）
    created_zip_file: Optional[str] = None
    can_package = (len(errors) == 0) and all_cells_valid and all_margin_ok

    if zip_path:
        if can_package:
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
        else:
            warnings.append("檢驗未達合規標準，取消打包上架 ZIP 壓縮包以防上架被退件")

    return SlicingReport(
        input_path=str(src_file),
        image_width=w,
        image_height=h,
        mode=orig_mode,
        has_alpha=has_alpha_channel,
        has_transparent_pixels=has_transparent_pixels,
        expected_cells=expected_total,
        sliced_cells=len(cells_reports),
        main_created=main_created,
        tab_created=tab_created,
        zip_created=created_zip_file,
        all_margin_ok=all_margin_ok,
        all_cells_valid=all_cells_valid,
        cells=cells_reports,
        errors=errors,
        warnings=warnings,
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

    # 參數防禦驗證
    if args.margin < 0:
        err_msg = f"錯誤：安全邊距 (--margin) 必須為非負整數，收到: {args.margin}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "INVALID_MARGIN"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    expected_total = args.rows * args.cols
    if not (1 <= args.main_index <= expected_total):
        err_msg = f"錯誤：--main-index 必須介於 1 到 {expected_total} 之間，收到: {args.main_index}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "INVALID_MAIN_INDEX"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    if not (1 <= args.tab_index <= expected_total):
        err_msg = f"錯誤：--tab-index 必須介於 1 到 {expected_total} 之間，收到: {args.tab_index}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "INVALID_TAB_INDEX"}, ensure_ascii=False))
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
            strict=args.strict,
        )
    except Exception as ex:
        err_msg = f"錯誤：切圖執行異常：{ex}"
        if args.json:
            print(json.dumps({"error": err_msg, "code": "EXECUTION_ERROR"}, ensure_ascii=False))
        else:
            print(err_msg, file=sys.stderr)
        return 2

    is_size_exact = (report.image_width == expected_w and report.image_height == expected_h)
    has_fatal_errors = (len(report.errors) > 0) or (not report.all_cells_valid) or (not is_size_exact)
    has_margin_violations = not report.all_margin_ok

    passed = (not has_fatal_errors) and ((not has_margin_violations) or (not args.strict))

    if args.json:
        data = report.as_dict()
        data["is_size_exact"] = is_size_exact
        data["passed"] = passed
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"[*] 讀取影像: {report.input_path} ({report.image_width}x{report.image_height}, 模式: {report.mode})")
        if not report.has_alpha:
            print(f"[FAIL] ❌ 缺少 Alpha 通道！目前模式為 {report.mode}，LINE 貼圖必須為 RGBA 透明背景。")
        if not report.has_transparent_pixels:
            print(f"[FAIL] ❌ 缺少透明去背！整張圖無任何透明像素（假透明白底）。")
        if not is_size_exact:
            print(f"[FAIL] ❌ 影像尺寸 ({report.image_width}x{report.image_height}) 與預期 ({expected_w}x{expected_h}) 不一致。")

        print(f"[*] 切割 {args.rows}x{args.cols} 宮格 (單格 {args.cell_width}x{args.cell_height})...")
        for c in report.cells:
            if c.is_empty:
                print(f"  [FAIL] ❌ {c.filename} ({c.width}x{c.height}) - 完全透明空白圖（無貼圖內容）")
            elif c.is_fully_opaque:
                print(f"  [FAIL] ❌ {c.filename} ({c.width}x{c.height}) - 完全無透明背景（全像素不透明）")
            elif c.exceeds_1mb:
                print(f"  [FAIL] ❌ {c.filename} ({c.width}x{c.height}) - 容量 {c.file_size_bytes} bytes 超過 1MB 上限")
            else:
                status = "[PASS] ✅" if c.margin_ok else "[WARN] ⚠️"
                margin_info = "10px 安全邊距合規" if c.margin_ok else f"邊距溢出 {c.violations.total} px (T:{c.violations.top} B:{c.violations.bottom} L:{c.violations.left} R:{c.violations.right})"
                print(f"  {status} {c.filename} ({c.width}x{c.height}) - {margin_info}")

        if report.main_created:
            print(f"[*] 合成主圖: {Path(args.out_dir) / 'main.png'} (240x240, 來源: {args.main_index:02d}.png) [OK]")
        if report.tab_created:
            print(f"[*] 合成標籤: {Path(args.out_dir) / 'tab.png'} (96x74, 來源: {args.tab_index:02d}.png) [OK]")
        if report.zip_created:
            print(f"[*] 打包壓縮檔: {report.zip_created} [OK]")
        elif args.zip_path and not report.zip_created:
            print(f"[WARN] ⚠️ 未通過合規驗證，未產生 ZIP 打包檔：{args.zip_path}")

        if passed and not has_margin_violations:
            print("[SUCCESS] 🎉 全數貼圖與上架檔案切圖合規完成！")
        elif passed and has_margin_violations:
            print("[WARN] ⚠️ 切圖完成，但存在邊距違規，請檢視警示（非 strict 模式放行）。")
        else:
            print("[FAIL] ❌ 未通過合規檢查，請檢視上述錯誤與警示。")

    # 判定 exit code
    if has_fatal_errors:
        return 1
    if has_margin_violations and args.strict:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
