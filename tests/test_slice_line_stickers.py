#!/usr/bin/env python3
"""
tests/test_slice_line_stickers.py
單元測試：tools/slice_line_stickers.py
覆蓋合規切割、頂/底/左/右四向邊距溢出反例、缺少 Alpha 通道、全透明空圖、全實心無去背、
非標準尺寸、參數防禦驗證、主圖指定 index、缺套件報錯與非合規防打包。
"""

import io
import json
import os
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

        # CLI 非 strict 模式：exit 0 (帶警告)，但因邊距不合格亦不可打包 ZIP
        exit_code_normal = main([str(img_path), "-o", str(out_dir), "--zip", str(zip_path_normal)])
        self.assertEqual(exit_code_normal, 0)
        self.assertFalse(zip_path_normal.exists(), "非 strict 模式但在邊距不合格時亦不可打包 ZIP")

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
        self.assertIn("為完全透明空白圖", "".join(report.errors))

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
        """檔案不存在防禦測試：exit 2。"""
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


if __name__ == "__main__":
    unittest.main()
