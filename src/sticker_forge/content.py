"""Shared conservative content heuristics (not official LINE thresholds)."""
from typing import Any, Dict

from PIL import ImageChops

from .spec import LINE_MIN_MARGIN, VISIBLE_ALPHA_MIN


def measure_cell_content(cell_img: Any, margin: int = LINE_MIN_MARGIN) -> Dict[str, float]:
    """量測單格內容：可見像素數、安全區覆蓋率、可見像素中淺色無彩色佔比。

    可見 = alpha >= VISIBLE_ALPHA_MIN；安全區 = 扣掉四周 margin 後的內部矩形。
    """
    if cell_img.mode != "RGBA":
        cell_img = cell_img.convert("RGBA")
    w, h = cell_img.size

    alpha = cell_img.getchannel("A")
    visible = sum(alpha.histogram()[VISIBLE_ALPHA_MIN:])

    # 淺色無彩色：min(r,g,b) >= 192 且 max-min <= 12，且該像素可見（用整張影像運算，避免逐像素 Python 迴圈）
    r, g, b = cell_img.getchannel("R"), cell_img.getchannel("G"), cell_img.getchannel("B")
    lo = ImageChops.darker(ImageChops.darker(r, g), b)
    hi = ImageChops.lighter(ImageChops.lighter(r, g), b)
    is_light = lo.point(lambda v: 255 if v >= 192 else 0)
    is_gray = ImageChops.subtract(hi, lo).point(lambda v: 255 if v <= 12 else 0)
    is_visible = alpha.point(lambda v: 255 if v >= VISIBLE_ALPHA_MIN else 0)
    both = ImageChops.multiply(ImageChops.multiply(is_light, is_gray), is_visible)
    light = both.histogram()[255]

    safe_box = (margin, margin, w - margin, h - margin)
    if safe_box[2] > safe_box[0] and safe_box[3] > safe_box[1]:
        safe_alpha = cell_img.getchannel("A").crop(safe_box)
        hist = safe_alpha.histogram()
        safe_total = (safe_box[2] - safe_box[0]) * (safe_box[3] - safe_box[1])
        coverage = sum(hist[VISIBLE_ALPHA_MIN:]) / safe_total
    else:
        coverage = 0.0

    return {
        "visible_pixels": visible,
        "safe_area_coverage": coverage,
        "light_neutral_ratio": (light / visible) if visible else 0.0,
    }
