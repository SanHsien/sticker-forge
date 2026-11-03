from io import BytesIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

import pytest
from PIL import Image, ImageDraw

from sticker_forge.cli import main
from sticker_forge.exporter import export_line_zip, validate_line_zip
from sticker_forge.webapi import Api, _decode, _encode
from test_webapi import _animated_data_url


@pytest.mark.parametrize("kind", ["blank", "dust", "invisible", "white", "gray", "valid"])
def test_validate_rejects_blank_dust_white_gray_tiles(tmp_path, kind):
    tile = Image.new("RGBA", (370, 320))
    draw = ImageDraw.Draw(tile)
    if kind == "dust":
        tile.putpixel((100, 100), (200, 0, 0, 255))
    elif kind == "invisible":
        draw.rectangle((30, 30, 200, 200), fill=(200, 0, 0, 1))
    elif kind == "white":
        draw.rectangle((10, 10, 359, 309), fill=(255, 255, 255, 254))
    elif kind == "gray":
        draw.rectangle((80, 60, 280, 260), fill=(220, 220, 220, 255))
    elif kind == "valid":
        draw.rectangle((80, 60, 280, 260), fill=(200, 0, 0, 255))
    path = export_line_zip([tile] * 8, tmp_path / "pack.zip")
    errors = validate_line_zip(path)
    assert bool(errors) == (kind != "valid"), errors
    if errors:
        assert any("01.png" in e for e in errors)


def test_4x4_grid_yields_16_valid_stickers_while_default_stays_3x3(tmp_path):
    from sticker_forge.spec import LINE_STATIC_16_SPEC, LINE_STATIC_SPEC
    assert (LINE_STATIC_16_SPEC.sticker_count, LINE_STATIC_16_SPEC.grid_rows,
            LINE_STATIC_16_SPEC.grid_columns) == (16, 4, 4)
    assert (LINE_STATIC_SPEC.sticker_count, LINE_STATIC_SPEC.grid_rows) == (8, 3)
    grid = Image.new("RGBA", (1480, 1280))
    draw = ImageDraw.Draw(grid)
    for i in range(16):
        x, y = i % 4 * 370, i // 4 * 320
        draw.rectangle((x+80, y+60, x+280, y+260), fill=(200, 0, 0, 255))
    source = tmp_path / "grid.png"
    grid.save(source)
    assert main(["split", str(source), "--grid", "4x4",
                 "-o", str(tmp_path / "split")]) == 0
    assert len(list((tmp_path / "split").glob("*.png"))) == 16
    with Image.open(tmp_path / "split" / "sticker-16.png") as last:
        assert last.size == (370, 320)
    assert main(["export", str(source), "--grid", "4x4", "--keep-background",
                 "-o", str(tmp_path / "cli.zip")]) == 0
    with ZipFile(tmp_path / "cli.zip") as archive:
        assert "16.png" in archive.namelist()
    assert validate_line_zip(tmp_path / "cli.zip") == []
    api = Api()
    tiles = api.split(_encode(grid), {"grid": "4x4"})
    assert len(tiles) == 16
    api._write_line_zip(
        [_decode(url) for url in tiles], tmp_path / "gui.zip", {"grid": "4x4"},
    )
    assert validate_line_zip(tmp_path / "gui.zip") == []
    assert len(api.split(_encode(grid), {})) == 9


@pytest.mark.parametrize("kind", ["animated", "popup", "effect"])
@pytest.mark.parametrize("locale", ["zh-Hant", "en"])
def test_short_animation_error_uses_current_gui_language(tmp_path, kind, locale):
    api = Api("en" if locale == "zh-Hant" else "zh-Hant")
    api._ask_save_path = lambda *a: tmp_path / "bad.zip"
    animations = [_animated_data_url(2)] * 8
    options = {"locale": locale}
    if kind == "animated":
        result = api.export_animated(animations, options)
    else:
        tiles = [_encode(Image.new("RGBA", (370, 320)))] * 8
        result = getattr(api, "export_" + kind)(tiles, animations, options)
    error = result["error"]
    assert ("\u5f71\u683c" in error) if locale == "zh-Hant" else ("frames" in error)
    assert "2" in error and "5" in error and "20" in error
    assert not (tmp_path / "bad.zip").exists()

    # Exercise the actual UI export handlers and status renderer with the
    # bridge response, including a language switch after app startup.
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the GUI JavaScript runtime check")
    script = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const [kind, locale, error] = JSON.parse(process.argv[1]);
const status = {textContent: '', style: {}};
const fields = {'status': status, 'main-index': {value: '1'},
  'tab-index': {value: '1'}, 'pack-title': {value: ''}, 'pack-author': {value: ''}};
const context = vm.createContext({
  window: {addEventListener() {}},
  document: {getElementById(id) {return fields[id];}},
});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
context.payload = {kind, locale, error};
context.checkLocale = (actual) => assert.equal(actual, locale);
vm.runInContext(`(async () => {
  state.locale = payload.locale;
  state.mode = payload.kind === 'animated' ? 'animated' : 'static';
  state.tiles = Array.from({length: 8}, () => ({included: true, url: 'tile'}));
  state.screenAnimations = Array(8).fill('animation');
  window.pywebview = {api: {
    async export_animated(tiles, options) {
      checkLocale(options.locale); return {error: payload.error};
    },
    async export_popup(tiles, animations, options) {
      checkLocale(options.locale); return {error: payload.error};
    },
    async export_effect(tiles, animations, options) {
      checkLocale(options.locale); return {error: payload.error};
    },
  }};
  if (payload.kind === 'animated') await exportAnimated();
  else await exportScreenSticker(payload.kind);
})()`, context).then(() => {
  assert.equal(status.textContent, error);
  assert.equal(status.style.color, '#fecaca');
}).catch(e => {console.error(e); process.exitCode = 1;});
"""
    subprocess.run(
        [node, "-e", script, json.dumps([kind, locale, error])],
        cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True,
        timeout=15,
    )


@pytest.mark.parametrize("visible_pixels, rejected", [(1183, True), (1184, False)])
def test_zip_visible_ratio_boundary(tmp_path, visible_pixels, rejected):
    tile = Image.new("RGBA", (370, 320))
    for index in range(visible_pixels):
        tile.putpixel((50 + index % 40, 50 + index // 40), (200, 0, 0, 16))
    errors = _validate_raw_tile(tmp_path, tile)
    assert any("01.png is blank" in e for e in errors) == rejected


@pytest.mark.parametrize("width, rejected", [(329, False), (333, True)])
def test_zip_safe_coverage_boundary(tmp_path, width, rejected):
    tile = Image.new("RGBA", (370, 320))
    ImageDraw.Draw(tile).rectangle((10, 10, 10 + width - 1, 309), fill=(200, 0, 0, 255))
    errors = _validate_raw_tile(tmp_path, tile)
    assert any("01.png has a solid backdrop" in e for e in errors) == rejected


def _validate_raw_tile(tmp_path, tile):
    """Keep exact source pixels; export normally resizes to add padding."""
    valid = Image.new("RGBA", (370, 320))
    ImageDraw.Draw(valid).ellipse((80, 60, 280, 260), fill=(200, 0, 0, 255))
    original = export_line_zip([valid] * 8, tmp_path / "original.zip")
    buffer = BytesIO()
    tile.save(buffer, format="PNG")
    path = tmp_path / "raw.zip"
    with ZipFile(original) as source, ZipFile(path, "w") as target:
        for name in source.namelist():
            target.writestr(name, buffer.getvalue() if name == "01.png" else source.read(name))
    return validate_line_zip(path)


def test_compatibility_entry_reports_missing_pillow():
    script = """
import runpy
import sys
sys.modules['PIL'] = None
sys.argv = ['examples/slice_line_stickers.py', 'dummy.png', '--json']
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", script], cwd=Path(__file__).parents[1],
        capture_output=True, timeout=15,
    )
    assert result.returncode == 2, result.stderr.decode("utf-8", errors="replace")
    assert json.loads(result.stdout.decode("utf-8"))["code"] == "MISSING_PILLOW"
    assert b"Traceback" not in result.stderr


@pytest.mark.parametrize("layout, count, selected", [("3x3", 9, 8), ("4x4", 16, 16)])
def test_gui_grid_selection_uses_core_spec(layout, count, selected):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is required for the GUI JavaScript runtime check")
    script = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const [layout, count, selected, bootstrap] = JSON.parse(process.argv[1]);
const status = {textContent: '', style: {}};
const fields = {'status': status, 'grid-layout': {value: layout},
  'cleanup-outline': {value: 'none'}, 'sticker-padding': {value: '10'}};
const context = vm.createContext({
  window: {addEventListener() {}},
  document: {getElementById(id) {return fields[id];}},
});
vm.runInContext(fs.readFileSync('app/app.js', 'utf8'), context);
context.payload = {layout, count, selected, bootstrap};
context.assert = assert;
vm.runInContext(`(async () => {
  boots['zh-Hant'] = payload.bootstrap;
  state.sourceDataUrl = 'grid';
  chromaKeyValue = () => 'green';
  tuneValue = () => 'balanced';
  renderTiles = () => {};
  updatePreview = () => {};
  window.pywebview = {api: {async split(source, options) {
    assert.equal(source, 'grid');
    assert.equal(options.grid, payload.layout);
    return Array(payload.count).fill('tile');
  }}};
  await splitGrid();
  assert.equal(state.tiles.length, payload.count);
  assert.equal(state.tiles.filter(t => t.included).length, payload.selected);
})()`, context).then(() => {
  assert.ok(status.textContent.includes(String(count)), status.textContent);
  assert.equal(status.style.color, '#e5e7eb');
}).catch(e => {console.error(e); process.exitCode = 1;});
"""
    subprocess.run(
        [node, "-e", script, json.dumps([layout, count, selected, Api().bootstrap()])],
        cwd=Path(__file__).parents[1], check=True, capture_output=True, text=True,
        timeout=15,
    )


@pytest.mark.parametrize("light_pixels, rejected", [(1799, False), (1800, True)])
def test_zip_light_neutral_boundary(tmp_path, light_pixels, rejected):
    tile = Image.new("RGBA", (370, 320))
    for index in range(2000):
        color = (220, 220, 220, 255) if index < light_pixels else (120, 0, 0, 255)
        tile.putpixel((50 + index % 50, 50 + index // 50), color)
    errors = _validate_raw_tile(tmp_path, tile)
    assert any("01.png is almost entirely light neutral" in e for e in errors) == rejected


def test_zip_checkerboard_patch_is_rejected(tmp_path):
    tile = Image.new("RGBA", (370, 320))
    for y in range(60, 260):
        for x in range(80, 280):
            shade = 255 if (x // 10 + y // 10) % 2 else 220
            tile.putpixel((x, y), (shade, shade, shade, 255))
    errors = _validate_raw_tile(tmp_path, tile)
    assert any("01.png is almost entirely light neutral" in e for e in errors)
    assert not any("01.png has a solid backdrop" in e for e in errors)


def test_unknown_grid_returns_error_dict_not_keyerror(tmp_path):
    api = Api()
    grid = Image.new("RGBA", (1110, 960))
    result = api.split(_encode(grid), {"grid": "5x5"})
    assert isinstance(result, dict) and "5x5" in result["error"]
    assert api.export_line([], {"grid": "5x5"})["error"] == result["error"]
    assert api.export_stickers([], {"grid": "5x5"})["error"] == result["error"]
    assert "unknown grid" in Api("en").split(_encode(grid), {"grid": "5x5"})["error"]
