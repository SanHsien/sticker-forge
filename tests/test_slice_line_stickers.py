#!/usr/bin/env python3
"""
tests/test_slice_line_stickers.py
單元測試：tools/slice_line_stickers.py
覆蓋合規切割、頂/底/左/右四向邊距溢出反例、缺少 Alpha 通道、全透明空圖、全實心無去背、
非標準尺寸、參數防禦驗證、主圖指定 index、缺套件報錯與非合規防打包。
"""

import contextlib
import io
import json
import os
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zipfile

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    HAS_PIL = False

from tools.slice_line_stickers import (
    LINE_MAX_FILE_BYTES,
    MarginViolation,
    check_cell_margins,
    create_fitted_canvas,
    main,
    slice_line_stickers,
)


class TestSliceLineStickers(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="test_line_stickers_")
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)

    def _require_pil(self) -> None:
        if not HAS_PIL:
            self.skipTest("Pillow (PIL) 未安裝，跳過需要影像處理之測試")

    def _create_test_grid_image(
        self,
        size: tuple[int, int] = (1480, 1280),
        mode: str = "RGBA",
        pad_inside_margin: bool = True,
        corrupt_margin_dir: str | None = None,
        empty_cell_index: int | None = None,
        custom_colors: dict[int, tuple[int, int, int, int]] | None = None,
    ) -> Path:
        """建立測試用的 1480x1280 (4x4) 網格圖像。"""
        self._require_pil()
        img = Image.new(mode, size, (0, 0, 0, 0) if mode == "RGBA" else (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 4x4 格子，每格 370x320
        for row in range(4):
            for col in range(4):
                idx = row * 4 + col + 1
                cell_left = col * 370
                cell_top = row * 320
                cell_right = cell_left + 370
                cell_bottom = cell_top + 320

                if empty_cell_index == idx:
                    # 故意留空（全透明）
                    continue

                # 依方向破壞第 1 格的安全邊距
                if corrupt_margin_dir and idx == 1:
                    if corrupt_margin_dir == "top":
                        draw.rectangle(
                            [cell_left + 50, cell_top + 2, cell_left + 100, cell_top + 5],
                            fill=(255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0),
                        )
                    elif corrupt_margin_dir == "bottom":
                        draw.rectangle(
                            [cell_left + 50, cell_bottom - 5, cell_left + 100, cell_bottom - 2],
                            fill=(255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0),
                        )
                    elif corrupt_margin_dir == "left":
                        draw.rectangle(
                            [cell_left + 2, cell_top + 50, cell_left + 5, cell_top + 100],
                            fill=(255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0),
                        )
                    elif corrupt_margin_dir == "right":
                        draw.rectangle(
                            [cell_right - 5, cell_top + 50, cell_right - 2, cell_top + 100],
                            fill=(255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0),
                        )

                # 在內部安全區繪製中心方塊 (左右預留 30px, 上下預留 30px)
                if pad_inside_margin:
                    safe_left = cell_left + 30
                    safe_top = cell_top + 30
                    safe_right = cell_right - 30
                    safe_bottom = cell_bottom - 30
                    if custom_colors and idx in custom_colors:
                        fill_color = custom_colors[idx]
                    else:
                        fill_color = (
                            (col * 50) % 255,
                            (row * 50) % 255,
                            150,
                            255,
                        ) if mode == "RGBA" else (100, 100, 100)
                    draw.rectangle([safe_left, safe_top, safe_right, safe_bottom], fill=fill_color)

        img_path = Path(self.temp_dir) / f"grid_{mode}_{size[0]}x{size[1]}_{corrupt_margin_dir or 'clean'}.png"
        img.save(img_path, format="PNG")
        return img_path

    def test_slice_valid_16_grid_success(self) -> None:
        """驗證有效 1480x1280 RGBA 圖像的完整切割與 ZIP 封包。"""
        self._require_pil()
        img_path = self._create_test_grid_image()
        out_dir = Path(self.temp_dir) / "output_valid"
        zip_file = Path(self.temp_dir) / "stickers.zip"

        report = slice_line_stickers(
            input_path=img_path,
            out_dir=out_dir,
            rows=4,
            cols=4,
            cell_width=370,
            cell_height=320,
            margin=10,
            zip_path=zip_file,
        )

        self.assertEqual(report.image_width, 1480)
        self.assertEqual(report.image_height, 1280)
        self.assertTrue(report.has_alpha)
        self.assertTrue(report.has_transparent_pixels)
        self.assertEqual(report.sliced_cells, 16)
        self.assertTrue(report.main_created)
        self.assertTrue(report.tab_created)
        self.assertTrue(report.all_margin_ok)
        self.assertTrue(report.all_cells_valid)
        self.assertEqual(len(report.errors), 0)

        # 斷言 16 張貼圖檔案均存在且尺寸正確
        for i in range(1, 17):
            fpath = out_dir / f"{i:02d}.png"
            self.assertTrue(fpath.is_file(), f"{fpath} 應存在")
            with Image.open(fpath) as cell:
                self.assertEqual(cell.size, (370, 320))
                self.assertEqual(cell.mode, "RGBA")

        # 斷言 main.png (240x240) 與 tab.png (96x74)
        main_path = out_dir / "main.png"
        tab_path = out_dir / "tab.png"
        self.assertTrue(main_path.is_file())
        self.assertTrue(tab_path.is_file())
        with Image.open(main_path) as m_img:
            self.assertEqual(m_img.size, (240, 240))
            self.assertEqual(m_img.mode, "RGBA")
        with Image.open(tab_path) as t_img:
            self.assertEqual(t_img.size, (96, 74))
            self.assertEqual(t_img.mode, "RGBA")

        # 斷言 ZIP 內容包含 18 個檔案 (16 + main + tab)
        self.assertTrue(zip_file.is_file())
        with zipfile.ZipFile(zip_file, "r") as zf:
            namelist = zf.namelist()
            self.assertEqual(len(namelist), 18)
            self.assertIn("01.png", namelist)
            self.assertIn("16.png", namelist)
            self.assertIn("main.png", namelist)
            self.assertIn("tab.png", namelist)

    def test_four_direction_margin_violations(self) -> None:
        """邊距反例測試：獨立測試頂、底、左、右四個方向的邊距溢出，確保每一側改壞皆能精確被抓出。"""
        self._require_pil()

        # 1. 測試頂端邊距溢出 (Top)
        top_img = self._create_test_grid_image(corrupt_margin_dir="top")
        report_top = slice_line_stickers(top_img, out_dir=Path(self.temp_dir) / "out_top")
        cell_1_top = report_top.cells[0]
        self.assertFalse(cell_1_top.margin_ok)
        self.assertGreater(cell_1_top.violations.top, 0, "頂部邊距溢出必須被偵測出")
        self.assertEqual(cell_1_top.violations.bottom, 0)
        self.assertEqual(cell_1_top.violations.left, 0)
        self.assertEqual(cell_1_top.violations.right, 0)

        # 2. 測試底部邊距溢出 (Bottom)
        bot_img = self._create_test_grid_image(corrupt_margin_dir="bottom")
        report_bot = slice_line_stickers(bot_img, out_dir=Path(self.temp_dir) / "out_bot")
        cell_1_bot = report_bot.cells[0]
        self.assertFalse(cell_1_bot.margin_ok)
        self.assertGreater(cell_1_bot.violations.bottom, 0, "底部邊距溢出必須被偵測出")
        self.assertEqual(cell_1_bot.violations.top, 0)
        self.assertEqual(cell_1_bot.violations.left, 0)
        self.assertEqual(cell_1_bot.violations.right, 0)

        # 3. 測試左側邊距溢出 (Left)
        left_img = self._create_test_grid_image(corrupt_margin_dir="left")
        report_left = slice_line_stickers(left_img, out_dir=Path(self.temp_dir) / "out_left")
        cell_1_left = report_left.cells[0]
        self.assertFalse(cell_1_left.margin_ok)
        self.assertGreater(cell_1_left.violations.left, 0, "左側邊距溢出必須被偵測出")
        self.assertEqual(cell_1_left.violations.top, 0)
        self.assertEqual(cell_1_left.violations.bottom, 0)
        self.assertEqual(cell_1_left.violations.right, 0)

        # 4. 測試右側邊距溢出 (Right)
        right_img = self._create_test_grid_image(corrupt_margin_dir="right")
        report_right = slice_line_stickers(right_img, out_dir=Path(self.temp_dir) / "out_right")
        cell_1_right = report_right.cells[0]
        self.assertFalse(cell_1_right.margin_ok)
        self.assertGreater(cell_1_right.violations.right, 0, "右側邊距溢出必須被偵測出")
        self.assertEqual(cell_1_right.violations.top, 0)
        self.assertEqual(cell_1_right.violations.bottom, 0)
        self.assertEqual(cell_1_right.violations.left, 0)

    def test_main_index_parameter_selection(self) -> None:
        """主圖來源指定測試：驗證 --main-index 指定不同格子時，main.png 確實合成自該指定格。"""
        self._require_pil()
        # 第 1 格塗紅色 (255, 0, 0, 255)，第 2 格塗藍色 (0, 0, 255, 255)
        custom_colors = {
            1: (255, 0, 0, 255),
            2: (0, 0, 255, 255),
        }
        img_path = self._create_test_grid_image(custom_colors=custom_colors)
        out_dir = Path(self.temp_dir) / "output_main_idx"

        # 指定 main_index = 2
        report = slice_line_stickers(
            img_path,
            out_dir=out_dir,
            main_index=2,
        )
        self.assertTrue(report.main_created)
        main_path = out_dir / "main.png"
        self.assertTrue(main_path.is_file())

        with Image.open(main_path) as m_img:
            # 取主圖中心點像素 (120, 120)，應為第 2 格之藍色而非第 1 格之紅色
            center_pixel = m_img.getpixel((120, 120))
            self.assertEqual(center_pixel[0], 0, "主圖不應取自第 1 格（紅色）")
            self.assertEqual(center_pixel[2], 255, "主圖必須取自第 2 格（藍色）")

    def test_strict_mode_and_no_zip_on_failure(self) -> None:
        """反例測試：安全邊距溢出時，--strict 下 exit 1，且不合格時不可打包 ZIP。"""
        self._require_pil()
        img_path = self._create_test_grid_image(corrupt_margin_dir="top")
        out_dir = Path(self.temp_dir) / "output_corrupt"
        zip_path_normal = Path(self.temp_dir) / "no_zip_normal.zip"
        zip_path_strict = Path(self.temp_dir) / "no_zip_strict.zip"

        # 非 strict、沒要求 ZIP：邊距違規只是警告，exit 0
        self.assertEqual(main([str(img_path), "-o", str(out_dir)]), 0)

        # 非 strict 但要求 --zip：ZIP 產不出來，不可 exit 0 讓人以為上架包做好了
        exit_code_normal = main([str(img_path), "-o", str(out_dir), "--zip", str(zip_path_normal)])
        self.assertEqual(exit_code_normal, 1)
        self.assertFalse(zip_path_normal.exists(), "邊距不合格時不可打包 ZIP")

        # CLI --strict 模式：exit 1，且不可打包 ZIP
        exit_code_strict = main([str(img_path), "-o", str(out_dir), "--strict", "--zip", str(zip_path_strict)])
        self.assertEqual(exit_code_strict, 1)
        self.assertFalse(zip_path_strict.exists(), "strict 模式合規失敗時絕對不可打包輸出 ZIP")

    def test_empty_cell_detection(self) -> None:
        """反例測試：全透明空白貼圖（無內容）必須判定失敗且 exit 1。"""
        self._require_pil()
        img_path = self._create_test_grid_image(empty_cell_index=16)
        out_dir = Path(self.temp_dir) / "output_empty"

        report = slice_line_stickers(img_path, out_dir=out_dir)
        self.assertFalse(report.all_cells_valid)
        self.assertTrue(report.cells[15].is_empty)
        self.assertIn("視為空白貼圖", "".join(report.errors))

        exit_code = main([str(img_path), "-o", str(out_dir)])
        self.assertEqual(exit_code, 1)

    def test_fully_opaque_image_detection(self) -> None:
        """反例測試：全不透明實心底（無去背透明度）必須判定失敗且 exit 1。"""
        self._require_pil()
        img_path = self._create_test_grid_image(mode="RGB")
        out_dir = Path(self.temp_dir) / "output_opaque"

        report = slice_line_stickers(img_path, out_dir=out_dir)
        self.assertFalse(report.has_alpha)
        self.assertFalse(report.has_transparent_pixels)

        # CLI exit code 必須為 1
        exit_code = main([str(img_path), "-o", str(out_dir)])
        self.assertEqual(exit_code, 1)

    def test_invalid_dimension_handling(self) -> None:
        """反例測試：尺寸不符合 1480x1280 時（如 800x600），無論是否 strict 均 exit 1 並印 [FAIL]。"""
        self._require_pil()
        img_path = self._create_test_grid_image(size=(800, 600))
        out_dir = Path(self.temp_dir) / "output_bad_size"

        # 非 strict 模式
        exit_code_normal = main([str(img_path), "-o", str(out_dir)])
        self.assertEqual(exit_code_normal, 1)

        # strict 模式
        exit_code_strict = main([str(img_path), "-o", str(out_dir), "--strict"])
        self.assertEqual(exit_code_strict, 1)

    def test_invalid_parameters_defensive_exit(self) -> None:
        """參數防禦測試：負數 margin 或超出範圍的 main-index 必須報錯退出 (exit 2)。"""
        self._require_pil()
        img_path = self._create_test_grid_image()
        out_dir = Path(self.temp_dir) / "output_params"

        # 1. 負數 margin (-5)
        exit_code_neg_margin = main([str(img_path), "-o", str(out_dir), "--margin", "-5"])
        self.assertEqual(exit_code_neg_margin, 2)

        # 2. 超出範圍的 main-index (99)
        exit_code_bad_main = main([str(img_path), "-o", str(out_dir), "--main-index", "99"])
        self.assertEqual(exit_code_bad_main, 2)

        # 3. 0 或負數 main-index
        exit_code_zero_main = main([str(img_path), "-o", str(out_dir), "--main-index", "0"])
        self.assertEqual(exit_code_zero_main, 2)

    def test_file_not_found_cli(self) -> None:
        """檔案不存在防禦測試：exit 2（需有 Pillow，否則 exit 2 的理由是缺套件而非檔案不存在）。"""
        self._require_pil()
        non_existent = Path(self.temp_dir) / "not_found.png"
        exit_code = main([str(non_existent)])
        self.assertEqual(exit_code, 2)

    def test_json_output_mode(self) -> None:
        """驗證 --json 輸出包含結構化報告。"""
        self._require_pil()
        img_path = self._create_test_grid_image()
        out_dir = Path(self.temp_dir) / "output_json"

        stdout_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture):
            exit_code = main([str(img_path), "-o", str(out_dir), "--json"])

        self.assertEqual(exit_code, 0)
        output_str = stdout_capture.getvalue()
        data = json.loads(output_str)
        self.assertTrue(data.get("passed"))
        self.assertEqual(data.get("sliced_cells"), 16)
        self.assertTrue(data.get("has_alpha"))
        self.assertTrue(data.get("has_transparent_pixels"))

    def test_create_fitted_canvas_aspect_ratio(self) -> None:
        """測試不同長寬比縮放至指定畫布之置中性與尺寸。"""
        self._require_pil()
        tall_img = Image.new("RGBA", (100, 300), (255, 0, 0, 255))
        canvas_main = create_fitted_canvas(tall_img, (240, 240))
        self.assertEqual(canvas_main.size, (240, 240))
        self.assertEqual(canvas_main.mode, "RGBA")

        wide_img = Image.new("RGBA", (400, 100), (0, 255, 0, 255))
        canvas_tab = create_fitted_canvas(wide_img, (96, 74))
        self.assertEqual(canvas_tab.size, (96, 74))
        self.assertEqual(canvas_tab.mode, "RGBA")

    def test_missing_pillow_dependency_graceful_exit(self) -> None:
        """驗證當 Pillow 缺失時清晰報錯並以 code 2 退出。"""
        with patch("tools.slice_line_stickers.PIL_AVAILABLE", False):
            with patch("tools.slice_line_stickers.Image", None):
                stderr_capture = io.StringIO()
                with patch("sys.stderr", stderr_capture):
                    exit_code = main(["some_dummy_file.png"])
                self.assertEqual(exit_code, 2)
                self.assertIn("Pillow", stderr_capture.getvalue())


class TestSliceHeuristics(unittest.TestCase):
    """第二輪複審補強：可見像素／覆蓋率啟發式、打包閘門、舊 ZIP、色彩模式、1MB、參數與 strict。"""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_line_stickers_h_"))
        self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)
        if not HAS_PIL:
            self.skipTest("Pillow (PIL) 未安裝，跳過需要影像處理之測試")

    # ---- helpers ----
    def _grid(self, name, rows=4, cols=4, cw=370, ch=320, inner=True, color=(200, 50, 50, 255), edit=None):
        """建立 rows x cols 透明排列圖；inner=True 時每格內縮 30px 填色。edit(img, draw, box) 可再修改。"""
        img = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        def box(i, inset=0):
            c = (i - 1) % cols
            r = (i - 1) // cols
            return [c * cw + inset, r * ch + inset, c * cw + cw - 1 - inset, r * ch + ch - 1 - inset]

        if inner:
            for i in range(1, rows * cols + 1):
                draw.rectangle(box(i, 30), fill=color)
        if edit:
            edit(img, draw, box)
        path = self.temp_dir / f"{name}.png"
        img.save(path)
        return path

    def _run(self, path, *extra, zip_name=None, out_name="out"):
        out = self.temp_dir / out_name
        args = [str(path), "-o", str(out), "--json"]
        zip_path = None
        if zip_name:
            zip_path = self.temp_dir / zip_name
            args += ["--zip", str(zip_path)]
        args += list(extra)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(args)
        data = json.loads(buf.getvalue())
        return code, data, zip_path

    # ---- 1. 實心白框／假透明 ----
    def test_white_solid_frame_filling_safe_area_is_rejected_everywhere(self) -> None:
        def edit(img, d, box):
            for i in range(1, 17):
                d.rectangle(box(i, 10), fill=(255, 255, 255, 255))
        path = self._grid("white_frame", inner=False, edit=edit)
        for extra in ((), ("--strict",)):
            code, data, z = self._run(path, *extra, zip_name="w.zip")
            self.assertEqual(code, 1, extra)
            self.assertFalse(data["passed"])
            self.assertFalse(z.exists())
            self.assertTrue(all(c["is_fully_opaque"] for c in data["cells"]))

    def test_single_solid_cell_flagged_only_for_that_cell(self) -> None:
        """單格實心（其餘正常）：改壞「單格 is_fully_opaque」判定必紅。"""
        def edit(img, d, box):
            d.rectangle(box(6), fill=(255, 255, 255, 255))
            img.putpixel((box(6)[0] + 100, box(6)[1] + 100), (0, 0, 0, 0))  # 挖一個洞仍應失敗
        path = self._grid("one_solid", edit=edit)
        report = slice_line_stickers(path, self.temp_dir / "o")
        flags = [c.is_fully_opaque for c in report.cells]
        self.assertEqual(flags, [i == 5 for i in range(16)])
        self.assertFalse(report.all_cells_valid)
        code, data, _ = self._run(path, "--strict")
        self.assertEqual(code, 1)

    def test_alpha_254_white_sheet_rejected_without_strict(self) -> None:
        img = Image.new("RGBA", (1480, 1280), (255, 255, 255, 254))
        path = self.temp_dir / "a254.png"
        img.save(path)
        code, data, _ = self._run(path)
        self.assertEqual(code, 1)
        self.assertFalse(data["has_transparent_pixels"])

    def test_coverage_threshold_boundary(self) -> None:
        """安全區覆蓋率 94% 放行、96% 擋下（顏色用深紅避免觸發淺色檢查，只量覆蓋率）。"""
        def mk(height):
            def edit(img, d, box):
                d.rectangle(box(1), fill=(0, 0, 0, 0))
                x0, y0, _, _ = box(1)
                d.rectangle([x0 + 10, y0 + 10, x0 + 359, y0 + 10 + height - 1], fill=(120, 0, 0, 255))
            return edit
        ok = slice_line_stickers(self._grid("cov94", edit=mk(282)), self.temp_dir / "o94")  # 350x282 / 350x300 = 94%
        self.assertFalse(ok.cells[0].is_fully_opaque)
        self.assertAlmostEqual(ok.cells[0].safe_area_coverage, 0.94, places=3)
        bad = slice_line_stickers(self._grid("cov96", edit=mk(288)), self.temp_dir / "o96")  # 96%
        self.assertTrue(bad.cells[0].is_fully_opaque)

    def test_checkerboard_fake_transparency_rejected(self) -> None:
        """棋盤格假透明：填滿安全區（被覆蓋率擋）與只畫一塊（被淺色無彩色檢查擋）都要失敗。"""
        def checker(img, x0, y0, x1, y1):
            px = img.load()
            for y in range(y0, y1):
                for x in range(x0, x1):
                    v = 255 if ((x - x0) // 10 + (y - y0) // 10) % 2 == 0 else 204
                    px[x, y] = (v, v, v, 255)

        def full(img, d, box):
            for i in range(1, 17):
                b = box(i, 10)
                checker(img, b[0], b[1], b[2] + 1, b[3] + 1)
        code, data, _ = self._run(self._grid("chk_full", inner=False, edit=full), "--strict", zip_name="c.zip")
        self.assertEqual(code, 1)

        def patch_only(img, d, box):
            b = box(3)
            d.rectangle(b, fill=(0, 0, 0, 0))
            checker(img, b[0] + 80, b[1] + 60, b[0] + 280, b[1] + 260)
        patch_path = self._grid("chk_patch", edit=patch_only)
        report = slice_line_stickers(patch_path, self.temp_dir / "o_patch")
        self.assertTrue(report.cells[2].looks_like_backdrop)
        self.assertFalse(report.cells[2].is_fully_opaque)
        self.assertEqual(sum(c.looks_like_backdrop for c in report.cells), 1)
        code, _, _ = self._run(patch_path)
        self.assertEqual(code, 1)

    # ---- 2. 空白／雜點 ----
    def test_dust_and_invisible_cells_are_empty(self) -> None:
        def dust(img, d, box):
            for i in range(1, 17):
                b = box(i)
                img.putpixel((b[0] + 100, b[1] + 100), (255, 0, 0, 255))
        code, data, z = self._run(self._grid("dust16", inner=False, edit=dust), "--strict", zip_name="d.zip")
        self.assertEqual(code, 1)
        self.assertEqual(sum(c["is_empty"] for c in data["cells"]), 16)
        self.assertFalse(z.exists())

        def one_dust(img, d, box):
            b = box(5)
            d.rectangle(b, fill=(0, 0, 0, 0))
            img.putpixel((b[0] + 100, b[1] + 100), (255, 0, 0, 255))
        report = slice_line_stickers(self._grid("dust1", edit=one_dust), self.temp_dir / "o1")
        self.assertEqual([c.is_empty for c in report.cells], [i == 4 for i in range(16)])

        def alpha1(img, d, box):
            b = box(5)
            d.rectangle(b, fill=(0, 0, 0, 0))
            d.rectangle(box(5, 10), fill=(255, 0, 0, 1))
        report = slice_line_stickers(self._grid("alpha1", edit=alpha1), self.temp_dir / "o2")
        self.assertTrue(report.cells[4].is_empty, "alpha=1 肉眼不可見，不能算有內容")
        self.assertEqual(report.cells[4].visible_pixels, 0)

    def test_visible_pixel_threshold_boundary(self) -> None:
        """可見像素 1% 門檻（370x320 -> 1184）：900 個擋下、1225 個放行；證明門檻不是固定放行或固定擋。"""
        def mk(side):
            def edit(img, d, box):
                b = box(2)
                d.rectangle(b, fill=(0, 0, 0, 0))
                d.rectangle([b[0] + 100, b[1] + 100, b[0] + 100 + side - 1, b[1] + 100 + side - 1], fill=(0, 90, 200, 255))
            return edit
        small = slice_line_stickers(self._grid("s30", edit=mk(30)), self.temp_dir / "os")
        self.assertTrue(small.cells[1].is_empty)
        self.assertEqual(small.cells[1].visible_pixels, 900)
        big = slice_line_stickers(self._grid("s35", edit=mk(35)), self.temp_dir / "ob")
        self.assertFalse(big.cells[1].is_empty)
        self.assertEqual(big.cells[1].visible_pixels, 1225)

    # ---- 3. 色彩模式 ----
    def test_palette_and_la_modes_with_real_transparency_pass(self) -> None:
        base = Image.open(self._grid("mode_base"))
        p_path = self.temp_dir / "mode_p.png"
        base.quantize(colors=16).save(p_path)
        reopened = Image.open(p_path)
        self.assertEqual(reopened.mode, "P")
        self.assertIn("transparency", reopened.info)
        code, data, z = self._run(p_path, "--strict", zip_name="p.zip", out_name="op")
        self.assertEqual((code, data["mode"], data["has_alpha"]), (0, "P", True), data["errors"])
        self.assertTrue(z.exists())
        with Image.open(self.temp_dir / "op" / "01.png") as c:
            self.assertEqual(c.getpixel((0, 0))[3], 0, "P 模式的透明在切片後必須仍為透明")

        la_path = self.temp_dir / "mode_la.png"
        base.convert("LA").save(la_path)
        code, data, z = self._run(la_path, "--strict", zip_name="la.zip", out_name="ola")
        self.assertEqual((code, data["mode"], data["has_alpha"]), (0, "LA", True), data["errors"])
        self.assertTrue(z.exists())

    def test_palette_without_transparency_and_opaque_la_fail(self) -> None:
        p_path = self.temp_dir / "p_opaque.png"
        Image.new("P", (1480, 1280), 0).save(p_path)
        code, data, _ = self._run(p_path)
        self.assertEqual(code, 1)
        self.assertFalse(data["has_alpha"])
        la_path = self.temp_dir / "la_opaque.png"
        Image.new("LA", (1480, 1280), (128, 255)).save(la_path)
        code, data, _ = self._run(la_path)
        self.assertEqual(code, 1)
        self.assertTrue(data["has_alpha"])
        self.assertFalse(data["has_transparent_pixels"])

    # ---- 4. ZIP 閘門 ----
    def test_stale_zip_is_removed_when_new_run_fails(self) -> None:
        good = self._grid("good")
        code, _, z = self._run(good, "--strict", zip_name="same.zip")
        self.assertEqual(code, 0)
        self.assertTrue(z.is_file())
        bad = self._grid("bad", edit=lambda img, d, box: img.putpixel((100, 5), (255, 0, 0, 255)))
        code, data, z2 = self._run(bad, "--strict", zip_name="same.zip")
        self.assertEqual(code, 1)
        self.assertIsNone(data["zip_created"])
        self.assertFalse(z2.exists(), "同路徑上一輪的舊 ZIP 必須被清掉")

    def test_zip_refused_for_incomplete_or_noncompliant_package(self) -> None:
        good = self._grid("good2")
        for extra in (("--skip-main",), ("--skip-tab",), ("--skip-main", "--skip-tab")):
            code, data, z = self._run(good, *extra, zip_name="inc.zip")
            self.assertEqual(code, 1, extra)
            self.assertFalse(z.exists(), extra)
            self.assertTrue(any("--zip" in e for e in data["errors"]))
        # 3x3 = 9 張：LINE 只收 8/16/24/32/40
        g9 = self._grid("g9", rows=3, cols=3)
        code, data, z = self._run(g9, "--rows", "3", "--cols", "3", zip_name="g9.zip")
        self.assertEqual(code, 1)
        self.assertFalse(z.exists())
        self.assertIn("9", " ".join(data["package_blockers"]))
        # 奇數寬
        odd = self._grid("odd", cw=369)  # 369 <= 370，只有「奇數」這一個問題
        code, data, z = self._run(odd, "--cell-width", "369", zip_name="odd.zip")
        self.assertEqual(code, 1)
        self.assertFalse(z.exists())
        self.assertIn("偶數", " ".join(data["package_blockers"]))
        self.assertNotIn("超過", " ".join(data["package_blockers"]))
        odd_h = self._grid("odd_h", ch=319)
        code, data, z = self._run(odd_h, "--cell-height", "319", zip_name="odd_h.zip")
        self.assertEqual(code, 1)
        self.assertIn("偶數", " ".join(data["package_blockers"]))
        # 超過 370x320 上限
        big = self._grid("toobig", rows=2, cols=4, cw=400, ch=320)
        code, data, z = self._run(big, "--rows", "2", "--cols", "4", "--cell-width", "400", zip_name="big.zip")
        self.assertEqual(code, 1)
        self.assertFalse(z.exists())

    def test_eight_sticker_package_is_allowed(self) -> None:
        """正向：8 張（2x4）是 LINE 可選張數，應可打包成 10 個檔案。"""
        g8 = self._grid("g8", rows=2, cols=4)
        code, data, z = self._run(g8, "--rows", "2", "--cols", "4", "--strict", zip_name="g8.zip")
        self.assertEqual(code, 0, data["errors"])
        with zipfile.ZipFile(z) as zf:
            self.assertEqual(len(zf.namelist()), 10)

    def test_margin_below_line_minimum_never_packages_and_message_uses_actual_margin(self) -> None:
        y9 = self._grid("y9", edit=lambda img, d, box: img.putpixel((100, 9), (255, 0, 0, 255)))
        code, data, z = self._run(y9, "--strict", "--margin", "8", zip_name="m8.zip")
        self.assertEqual(code, 1)
        self.assertFalse(z.exists())
        # --strict 且沒要求 ZIP：margin 小於 10 本身就要失敗（不是只靠打包閘門）
        code, data, _ = self._run(self._grid("clean_s"), "--strict", "--margin", "8")
        self.assertEqual(code, 1)
        self.assertTrue(any("--strict" in e for e in data["errors"]))
        code, data, z = self._run(self._grid("clean"), "--margin", "0", zip_name="m0.zip")
        self.assertEqual(code, 1, "margin 0 即使內容乾淨也不可打包")
        self.assertFalse(z.exists())
        # 非 strict 且沒要求 ZIP：可執行但要警告；訊息用實際 margin 而不是寫死 10px
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main([str(self._grid("clean2")), "-o", str(self.temp_dir / "o8"), "--margin", "8"])
        text = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("8px 安全邊距合規", text)
        self.assertNotIn("10px 安全邊距合規", text)
        self.assertIn("小於 LINE 官方 10px", text)

    def test_zip_over_size_limit_is_removed_and_reported(self) -> None:
        """ZIP 總容量上限 60MB 無法用小圖真實達成，所以把上限暫改小，驗證超限會刪檔並失敗。"""
        import tools.slice_line_stickers as mod
        good = self._grid("zipsize")
        with patch.object(mod, "LINE_MAX_ZIP_BYTES", 1000):
            code, data, z = self._run(good, "--strict", zip_name="zs.zip")
        self.assertEqual(code, 1)
        self.assertFalse(z.exists())
        self.assertIn("ZIP 容量", " ".join(data["errors"]))
        code, data, z = self._run(good, "--strict", zip_name="zs.zip")
        self.assertEqual(code, 0)
        self.assertTrue(z.exists())

    def test_zip_requested_but_not_produced_is_never_exit_zero(self) -> None:
        y9 = self._grid("y9b", edit=lambda img, d, box: img.putpixel((100, 9), (255, 0, 0, 255)))
        code, data, z = self._run(y9, zip_name="nz.zip")  # 非 strict
        self.assertEqual(code, 1)
        self.assertFalse(data["passed"])
        self.assertFalse(z.exists())

    def test_strict_parameter_is_honoured_by_library_function(self) -> None:
        y9 = self._grid("y9c", edit=lambda img, d, box: img.putpixel((100, 9), (255, 0, 0, 255)))
        lenient = slice_line_stickers(y9, self.temp_dir / "ol")
        strict = slice_line_stickers(y9, self.temp_dir / "os", strict=True)
        self.assertEqual(lenient.errors, [])
        self.assertTrue(any("邊距" in e for e in strict.errors))

    # ---- 5. 1MB ----
    def test_cell_over_1mb_is_flagged(self) -> None:
        """370x320 的原始 RGBA 只有 473,600 bytes 不可能超過 1MB，所以用 1x1 的 600x600 雜訊格測。"""
        rng = random.Random(7)
        raw = rng.getrandbits(8 * 600 * 600 * 4).to_bytes(600 * 600 * 4, "little")
        img = Image.frombytes("RGBA", (600, 600), raw)
        alpha = Image.new("L", (600, 600), 0)
        ImageDraw.Draw(alpha).rectangle([10, 10, 589, 589], fill=255)
        img.putalpha(alpha)
        path = self.temp_dir / "noise.png"
        img.save(path)
        report = slice_line_stickers(path, self.temp_dir / "on", rows=1, cols=1, cell_width=600, cell_height=600)
        self.assertGreater(report.cells[0].file_size_bytes, LINE_MAX_FILE_BYTES)
        self.assertTrue(report.cells[0].exceeds_1mb)
        self.assertIn("1MB", " ".join(report.errors))
        self.assertFalse(report.all_cells_valid)
        # 對照：同尺寸、容量小的實色格不應被標 1MB
        small = slice_line_stickers(self._grid("solid600", rows=1, cols=1, cw=600, ch=600), self.temp_dir / "oo",
                                    rows=1, cols=1, cell_width=600, cell_height=600)
        self.assertFalse(small.cells[0].exceeds_1mb)

    def test_main_and_tab_over_1mb_are_flagged(self) -> None:
        """main/tab 縮圖不可能真的超過 1MB，所以替換 getsize 模擬超大檔案，驗證檢查本身有作用。"""
        import tools.slice_line_stickers as mod
        real = os.path.getsize

        def fake_for(target):
            def fake(path):
                return 2 * 1024 * 1024 if Path(path).name == target else real(path)
            return fake

        for target in ("main.png", "tab.png"):
            with patch.object(mod.os.path, "getsize", fake_for(target)):
                report = slice_line_stickers(self._grid("g_" + target[:3]), self.temp_dir / ("o_" + target[:3]))
            self.assertTrue(any(target in e and "1MB" in e for e in report.errors), (target, report.errors))
            self.assertFalse(report.all_cells_valid)
        # 對照：沒替換時不該有 1MB 錯誤
        clean = slice_line_stickers(self._grid("g_clean"), self.temp_dir / "o_clean")
        self.assertEqual(clean.errors, [])

    # ---- 6. 尺寸 / index / 參數 ----
    def test_oversized_sheet_is_an_error(self) -> None:
        img = Image.new("RGBA", (1490, 1290), (0, 0, 0, 0))
        ImageDraw.Draw(img).rectangle([30, 30, 339, 289], fill=(200, 50, 50, 255))
        path = self.temp_dir / "over.png"
        img.save(path)
        code, data, _ = self._run(path)
        self.assertEqual(code, 1)
        self.assertFalse(data["is_size_exact"])
        self.assertTrue(any("不一致" in e for e in data["errors"]))

    def test_tab_index_selects_source_cell_and_is_range_checked(self) -> None:
        def edit(img, d, box):
            d.rectangle(box(1, 30), fill=(255, 0, 0, 255))
            d.rectangle(box(2, 30), fill=(0, 0, 255, 255))
        path = self._grid("tabidx", edit=edit)
        slice_line_stickers(path, self.temp_dir / "ot", tab_index=2)
        with Image.open(self.temp_dir / "ot" / "tab.png") as t:
            px = t.getpixel((48, 37))
        self.assertEqual((px[0], px[2]), (0, 255), "tab 必須取自第 2 格（藍）")
        with Image.open(self.temp_dir / "ot" / "main.png") as m:
            self.assertEqual(m.getpixel((120, 120))[0], 255, "main 預設仍取第 1 格（紅）")
        for bad in ("0", "17", "99"):
            code, data, _ = self._run(path, "--tab-index", bad)
            self.assertEqual(code, 2, bad)
            self.assertEqual(data["code"], "INVALID_TAB_INDEX")
        with self.assertRaises(ValueError):
            slice_line_stickers(path, self.temp_dir / "ox", tab_index=17)
        for bad in ("0", "17"):
            code, data, _ = self._run(path, "--main-index", bad)
            self.assertEqual((code, data["code"]), (2, "INVALID_MAIN_INDEX"))

    def test_zip_path_must_not_be_input_or_directory(self) -> None:
        good = self._grid("zipinput")
        with self.assertRaises(ValueError):
            slice_line_stickers(good, self.temp_dir / "oz", zip_path=good)
        self.assertTrue(good.is_file(), "輸入圖不可被當 ZIP 刪掉")
        with self.assertRaises(ValueError):
            slice_line_stickers(good, self.temp_dir / "oz", zip_path=self.temp_dir)


if __name__ == "__main__":
    unittest.main()
