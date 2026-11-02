#!/usr/bin/env python3
"""
tests/test_slice_line_stickers.py
單元測試：tools/slice_line_stickers.py
覆蓋合規切割、邊距溢出反例、缺少 Alpha 通道、非標準尺寸、缺套件報錯與 ZIP 打包。
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

from PIL import Image, ImageDraw

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

    def _create_test_grid_image(
        self,
        size: tuple[int, int] = (1480, 1280),
        mode: str = "RGBA",
        pad_inside_margin: bool = True,
        corrupt_margin_cell_1: bool = False,
    ) -> Path:
        """建立測試用的 1480x1280 (4x4) 網格圖像。"""
        img = Image.new(mode, size, (0, 0, 0, 0) if mode == "RGBA" else (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # 4x4 格子，每格 370x320
        for row in range(4):
            for col in range(4):
                cell_left = col * 370
                cell_top = row * 320
                cell_right = cell_left + 370
                cell_bottom = cell_top + 320

                if corrupt_margin_cell_1 and row == 0 and col == 0:
                    # 在第 1 格頂端邊界 5px 處畫不透明線條（破壞 10px 安全邊距）
                    draw.rectangle(
                        [cell_left + 20, cell_top + 2, cell_left + 50, cell_top + 5],
                        fill=(255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0),
                    )

                # 在內部安全區繪製中心方塊
                if pad_inside_margin:
                    safe_left = cell_left + 30
                    safe_top = cell_top + 30
                    safe_right = cell_right - 30
                    safe_bottom = cell_bottom - 30
                    fill_color = (
                        (col * 50) % 255,
                        (row * 50) % 255,
                        150,
                        255,
                    ) if mode == "RGBA" else (100, 100, 100)
                    draw.rectangle([safe_left, safe_top, safe_right, safe_bottom], fill=fill_color)

        img_path = Path(self.temp_dir) / f"grid_{mode}_{size[0]}x{size[1]}.png"
        img.save(img_path, format="PNG")
        return img_path

    def test_slice_valid_16_grid_success(self) -> None:
        """驗證有效 1480x1280 RGBA 圖像的完整切割與 ZIP 封包。"""
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
        self.assertEqual(report.sliced_cells, 16)
        self.assertTrue(report.main_created)
        self.assertTrue(report.tab_created)
        self.assertTrue(report.all_margin_ok)

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

    def test_margin_violation_detection_and_strict_cli_exit(self) -> None:
        """反例測試：安全邊距溢出時能精準抓出，並在 --strict 下 exit 1。"""
        img_path = self._create_test_grid_image(corrupt_margin_cell_1=True)
        out_dir = Path(self.temp_dir) / "output_corrupt"

        # 模組層級斷言
        report = slice_line_stickers(img_path, out_dir=out_dir)
        self.assertFalse(report.all_margin_ok)
        self.assertFalse(report.cells[0].margin_ok)
        self.assertGreater(report.cells[0].violations.top, 0)
        self.assertTrue(report.cells[1].margin_ok)

        # CLI 非 strict 模式：exit 0 (帶警告)
        exit_code_normal = main([str(img_path), "-o", str(out_dir)])
        self.assertEqual(exit_code_normal, 0)

        # CLI --strict 模式：exit 1
        exit_code_strict = main([str(img_path), "-o", str(out_dir), "--strict"])
        self.assertEqual(exit_code_strict, 1)

    def test_missing_alpha_channel_detection(self) -> None:
        """反例測試：缺少 Alpha 通道 (RGB) 必須判定失敗且 exit 1。"""
        img_path = self._create_test_grid_image(mode="RGB")
        out_dir = Path(self.temp_dir) / "output_rgb"

        report = slice_line_stickers(img_path, out_dir=out_dir)
        self.assertFalse(report.has_alpha)
        self.assertEqual(report.mode, "RGB")

        # CLI exit code 必須為 1
        exit_code = main([str(img_path), "-o", str(out_dir)])
        self.assertEqual(exit_code, 1)

    def test_invalid_dimension_handling(self) -> None:
        """反例測試：尺寸不符合 1480x1280 時在 --strict 模式下 exit 1。"""
        img_path = self._create_test_grid_image(size=(800, 600))
        out_dir = Path(self.temp_dir) / "output_bad_size"

        exit_code_strict = main([str(img_path), "-o", str(out_dir), "--strict"])
        self.assertEqual(exit_code_strict, 1)

    def test_file_not_found_cli(self) -> None:
        """參數與檔案不存在防禦測試：exit 2。"""
        non_existent = Path(self.temp_dir) / "not_found.png"
        exit_code = main([str(non_existent)])
        self.assertEqual(exit_code, 2)

    def test_json_output_mode(self) -> None:
        """驗證 --json 輸出包含結構化報告。"""
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

    def test_create_fitted_canvas_aspect_ratio(self) -> None:
        """測試不同長寬比縮放至指定畫布之置中性與尺寸。"""
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
