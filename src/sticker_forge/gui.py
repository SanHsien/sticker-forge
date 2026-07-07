from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk

from .cleanup import remove_chroma_background
from .exporter import export_line_zip, export_stickers_zip
from .prompts import DEFAULT_ACTIONS, DEFAULT_FIELDS, DEFAULT_TEXTS, SUGGESTIONS, normalize_locale, render_line_static_prompt
from .spec import LINE_STATIC_SPEC, resolve_chroma_key
from .splitter import split_grid_to_stickers


TEXT = {
    "zh-Hant": {
        "title": "sticker-forge",
        "subtitle": "LINE 靜態貼圖本機製作台",
        "language": "語言",
        "character": "角色",
        "theme": "主題",
        "tone": "語氣",
        "style": "風格",
        "prompt_language": "Prompt 語言",
        "with_text": "有字版",
        "copy_prompt": "複製 Prompt",
        "open_grid": "匯入 3x3",
        "split": "重新切圖",
        "cleanup": "去背",
        "select_first": "選前 8 張",
        "export_line": "匯出 LINE ZIP",
        "export_png": "匯出 9 張 PNG",
        "key": "背景色",
        "tune": "去背強度",
        "padding": "Padding",
        "preview": "匯出前預覽",
        "status_ready": "等待素材",
        "copied": "Prompt 已複製",
        "loaded": "已匯入並切圖：{name}",
        "cleaned": "已去背",
        "selected": "已選前 8 張",
        "need_grid": "請先匯入 3x3 圖。",
        "need_eight": "LINE 最小套組需選 8 張，目前 {count} 張。",
        "saved": "已匯出：{path}",
        "error": "錯誤",
        "done": "完成",
        "selected_count": "已選 {count} / 8",
    },
    "en": {
        "title": "sticker-forge",
        "subtitle": "Local LINE static sticker workspace",
        "language": "Language",
        "character": "Character",
        "theme": "Theme",
        "tone": "Tone",
        "style": "Style",
        "prompt_language": "Prompt language",
        "with_text": "Text version",
        "copy_prompt": "Copy Prompt",
        "open_grid": "Import 3x3",
        "split": "Split again",
        "cleanup": "Clean up",
        "select_first": "Select first 8",
        "export_line": "Export LINE ZIP",
        "export_png": "Export 9 PNG",
        "key": "Background",
        "tune": "Cleanup strength",
        "padding": "Padding",
        "preview": "Pre-export preview",
        "status_ready": "Waiting for artwork",
        "copied": "Prompt copied",
        "loaded": "Imported and split: {name}",
        "cleaned": "Background cleaned",
        "selected": "Selected first 8",
        "need_grid": "Import a 3x3 image first.",
        "need_eight": "LINE minimum set needs 8 stickers; {count} selected.",
        "saved": "Exported: {path}",
        "error": "Error",
        "done": "Done",
        "selected_count": "{count} / 8 selected",
    },
}


class StickerForgeApp:
    def __init__(self, root: tk.Tk, locale: str = "zh-Hant") -> None:
        self.root = root
        self.locale = normalize_locale(locale)
        self.source_path: Path | None = None
        self.source_image: Image.Image | None = None
        self.tiles: list[Image.Image] = []
        self.selected = [index < LINE_STATIC_SPEC.sticker_count for index in range(9)]
        self.thumbnails: list[ImageTk.PhotoImage] = []

        self.fields = {
            name: tk.StringVar(value=value)
            for name, value in DEFAULT_FIELDS[self.locale].items()
        }
        self.with_text = tk.BooleanVar(value=True)
        self.chroma_key = tk.StringVar(value="green")
        self.tune = tk.StringVar(value="balanced")
        self.padding = tk.IntVar(value=LINE_STATIC_SPEC.sticker_padding)
        self.text_vars = [tk.StringVar(value=value) for value in DEFAULT_TEXTS[self.locale]]
        self.action_vars = [tk.StringVar(value=value) for value in DEFAULT_ACTIONS[self.locale]]

        self.labels: dict[str, ttk.Label | ttk.LabelFrame | ttk.Button | ttk.Checkbutton] = {}
        self.field_combos: dict[str, ttk.Combobox] = {}
        self.text_combos: list[ttk.Combobox] = []
        self.action_combos: list[ttk.Combobox] = []
        self.status = tk.StringVar(value=self._t("status_ready"))
        self._build()
        self._bind_prompt_updates()
        self.render_prompt()
        self.update_preview()

    def _t(self, key: str, **kwargs: object) -> str:
        text = TEXT[self.locale][key]
        return text.format(**kwargs) if kwargs else text

    def _build(self) -> None:
        self.root.title(self._t("title"))
        self.root.geometry("1120x760")
        self.root.minsize(960, 640)

        top = ttk.Frame(self.root, padding=(12, 10))
        top.pack(fill="x")
        ttk.Label(top, text=self._t("title"), font=("Segoe UI", 18, "bold")).pack(side="left")
        self.labels["subtitle"] = ttk.Label(top, text=self._t("subtitle"))
        self.labels["subtitle"].pack(side="left", padx=(12, 0))
        self.labels["language"] = ttk.Label(top, text=self._t("language"))
        self.labels["language"].pack(side="right", padx=(8, 0))
        self.lang_var = tk.StringVar(value=self.locale)
        lang = ttk.Combobox(top, textvariable=self.lang_var, values=("zh-Hant", "en"), width=10, state="readonly")
        lang.pack(side="right")
        lang.bind("<<ComboboxSelected>>", lambda _event: self.change_locale(self.lang_var.get()))

        body = ttk.PanedWindow(self.root, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        left = ttk.Frame(body, padding=(0, 0, 8, 0))
        right = ttk.Frame(body, padding=(8, 0, 0, 0))
        body.add(left, weight=2)
        body.add(right, weight=3)

        form = ttk.LabelFrame(left, text="Prompt", padding=10)
        form.pack(fill="x")
        for row, key in enumerate(("character", "theme", "tone", "prompt_language", "style")):
            field_key = "language" if key == "prompt_language" else key
            self.labels[key] = ttk.Label(form, text=self._t(key))
            self.labels[key].grid(row=row, column=0, sticky="w", pady=3)
            combo = ttk.Combobox(
                form,
                textvariable=self.fields[field_key],
                values=SUGGESTIONS[self.locale][field_key],
            )
            combo.grid(row=row, column=1, sticky="ew", pady=3)
            self.field_combos[field_key] = combo
        form.columnconfigure(1, weight=1)

        options = ttk.Frame(left)
        options.pack(fill="x", pady=8)
        self.labels["with_text"] = ttk.Checkbutton(options, text=self._t("with_text"), variable=self.with_text)
        self.labels["with_text"].pack(side="left")
        self.labels["copy_prompt"] = ttk.Button(options, text=self._t("copy_prompt"), command=self.copy_prompt)
        self.labels["copy_prompt"].pack(side="right")

        slots = ttk.Frame(left)
        slots.pack(fill="x")
        for index in range(8):
            ttk.Label(slots, text=f"{index + 1:02d}").grid(row=index, column=0, padx=(0, 4), pady=2)
            text_combo = ttk.Combobox(
                slots, textvariable=self.text_vars[index], values=SUGGESTIONS[self.locale]["texts"], width=14
            )
            text_combo.grid(row=index, column=1, sticky="ew", pady=2)
            self.text_combos.append(text_combo)
            action_combo = ttk.Combobox(
                slots, textvariable=self.action_vars[index], values=SUGGESTIONS[self.locale]["actions"], width=24
            )
            action_combo.grid(row=index, column=2, sticky="ew", pady=2, padx=(4, 0))
            self.action_combos.append(action_combo)
        slots.columnconfigure(1, weight=1)
        slots.columnconfigure(2, weight=2)

        self.prompt_text = ScrolledText(left, height=14, wrap="word")
        self.prompt_text.pack(fill="both", expand=True, pady=(8, 0))

        controls = ttk.LabelFrame(right, text="Grid", padding=10)
        controls.pack(fill="x")
        self.labels["open_grid"] = ttk.Button(controls, text=self._t("open_grid"), command=self.open_grid)
        self.labels["open_grid"].grid(row=0, column=0, padx=3, pady=3)
        self.labels["split"] = ttk.Button(controls, text=self._t("split"), command=self.split_current)
        self.labels["split"].grid(row=0, column=1, padx=3, pady=3)
        self.labels["cleanup"] = ttk.Button(controls, text=self._t("cleanup"), command=self.cleanup_all)
        self.labels["cleanup"].grid(row=0, column=2, padx=3, pady=3)
        self.labels["select_first"] = ttk.Button(controls, text=self._t("select_first"), command=self.select_first)
        self.labels["select_first"].grid(row=0, column=3, padx=3, pady=3)

        self.labels["key"] = ttk.Label(controls, text=self._t("key"))
        self.labels["key"].grid(row=1, column=0, sticky="w", padx=3, pady=3)
        ttk.Combobox(controls, textvariable=self.chroma_key, values=("green", "magenta"), width=10, state="readonly").grid(row=1, column=1, sticky="w")
        self.labels["tune"] = ttk.Label(controls, text=self._t("tune"))
        self.labels["tune"].grid(row=1, column=2, sticky="e", padx=3, pady=3)
        ttk.Combobox(controls, textvariable=self.tune, values=("safe", "balanced", "aggressive"), width=12, state="readonly").grid(row=1, column=3, sticky="w")
        self.labels["padding"] = ttk.Label(controls, text=self._t("padding"))
        self.labels["padding"].grid(row=2, column=0, sticky="w", padx=3, pady=3)
        ttk.Scale(controls, variable=self.padding, from_=0, to=40, command=lambda _value: self.update_preview()).grid(row=2, column=1, columnspan=3, sticky="ew")
        controls.columnconfigure(3, weight=1)

        self.tile_frame = ttk.Frame(right)
        self.tile_frame.pack(fill="both", expand=True, pady=8)

        bottom = ttk.Frame(right)
        bottom.pack(fill="x")
        self.labels["export_line"] = ttk.Button(bottom, text=self._t("export_line"), command=self.export_line)
        self.labels["export_line"].pack(side="left", padx=(0, 6))
        self.labels["export_png"] = ttk.Button(bottom, text=self._t("export_png"), command=self.export_png)
        self.labels["export_png"].pack(side="left")

        self.labels["preview"] = ttk.LabelFrame(right, text=self._t("preview"), padding=8)
        self.labels["preview"].pack(fill="x", pady=(8, 0))
        self.preview_text = tk.Text(self.labels["preview"], height=5, wrap="word")
        self.preview_text.pack(fill="x")

        status = ttk.Label(self.root, textvariable=self.status, anchor="w", padding=(12, 4))
        status.pack(fill="x", side="bottom")

    def _bind_prompt_updates(self) -> None:
        variables = list(self.fields.values()) + self.text_vars + self.action_vars + [self.with_text, self.chroma_key]
        for variable in variables:
            variable.trace_add("write", lambda *_args: self.render_prompt())

    def change_locale(self, locale: str) -> None:
        previous = self.locale
        self.locale = normalize_locale(locale)
        self.lang_var.set(self.locale)
        for key, var in self.fields.items():
            if var.get() == DEFAULT_FIELDS[previous][key]:
                var.set(DEFAULT_FIELDS[self.locale][key])
        for index, var in enumerate(self.text_vars):
            if var.get() == DEFAULT_TEXTS[previous][index]:
                var.set(DEFAULT_TEXTS[self.locale][index])
        for index, var in enumerate(self.action_vars):
            if var.get() == DEFAULT_ACTIONS[previous][index]:
                var.set(DEFAULT_ACTIONS[self.locale][index])
        suggest = SUGGESTIONS[self.locale]
        for field_key, combo in self.field_combos.items():
            combo.configure(values=suggest[field_key])
        for combo in self.text_combos:
            combo.configure(values=suggest["texts"])
        for combo in self.action_combos:
            combo.configure(values=suggest["actions"])
        for key, widget in self.labels.items():
            if key in TEXT[self.locale]:
                if isinstance(widget, ttk.LabelFrame):
                    widget.configure(text=self._t(key))
                else:
                    widget.configure(text=self._t(key))
        self.status.set(self._t("status_ready"))
        self.render_prompt()
        self.update_preview()

    def render_prompt(self) -> None:
        prompt = render_line_static_prompt(
            locale=self.locale,
            with_text=self.with_text.get(),
            character=self.fields["character"].get(),
            theme=self.fields["theme"].get(),
            tone=self.fields["tone"].get(),
            style=self.fields["style"].get(),
            language=self.fields["language"].get(),
            texts=[var.get() for var in self.text_vars],
            actions=[var.get() for var in self.action_vars],
            chroma_key=self.chroma_key.get(),
        )
        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", prompt)

    def copy_prompt(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(self.prompt_text.get("1.0", "end-1c"))
        self.status.set(self._t("copied"))

    def open_grid(self) -> None:
        filename = filedialog.askopenfilename(
            title=self._t("open_grid"),
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.webp;*.bmp"), ("All files", "*.*")],
        )
        if not filename:
            return
        try:
            self.source_path = Path(filename)
            self.source_image = Image.open(filename).convert("RGBA")
            self.split_current()
            self.status.set(self._t("loaded", name=self.source_path.name))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self._t("error"), str(exc))

    def split_current(self) -> None:
        if self.source_image is None:
            messagebox.showinfo(self._t("error"), self._t("need_grid"))
            return
        spec = replace(LINE_STATIC_SPEC, sticker_padding=self.padding.get())
        key = resolve_chroma_key(self.chroma_key.get())
        self.tiles = split_grid_to_stickers(self.source_image, spec=spec, background=(*key.rgb, 255))
        self.selected = [index < spec.sticker_count for index in range(len(self.tiles))]
        self.render_tiles()
        self.update_preview()

    def cleanup_all(self) -> None:
        if not self.tiles:
            messagebox.showinfo(self._t("error"), self._t("need_grid"))
            return
        self.tiles = [
            remove_chroma_background(tile, key_name=self.chroma_key.get(), tune=self.tune.get())
            for tile in self.tiles
        ]
        self.render_tiles()
        self.update_preview()
        self.status.set(self._t("cleaned"))

    def select_first(self) -> None:
        self.selected = [index < LINE_STATIC_SPEC.sticker_count for index in range(len(self.tiles) or 9)]
        self.render_tiles()
        self.update_preview()
        self.status.set(self._t("selected"))

    def render_tiles(self) -> None:
        for child in self.tile_frame.winfo_children():
            child.destroy()
        self.thumbnails = []
        for index, tile in enumerate(self.tiles):
            cell = ttk.Frame(self.tile_frame, padding=4)
            cell.grid(row=index // 3, column=index % 3, sticky="nsew")
            preview = _thumbnail(tile)
            photo = ImageTk.PhotoImage(preview)
            self.thumbnails.append(photo)
            ttk.Label(cell, image=photo).pack()
            var = tk.BooleanVar(value=self.selected[index])
            check = ttk.Checkbutton(cell, text=f"{index + 1:02d}.png", variable=var)
            check.pack()
            var.trace_add("write", lambda *_args, i=index, v=var: self.set_selected(i, v.get()))
        for column in range(3):
            self.tile_frame.columnconfigure(column, weight=1)

    def set_selected(self, index: int, value: bool) -> None:
        self.selected[index] = value
        self.update_preview()

    def selected_tiles(self) -> list[Image.Image]:
        return [tile for tile, selected in zip(self.tiles, self.selected, strict=False) if selected]

    def update_preview(self) -> None:
        count = sum(1 for item in self.selected if item)
        lines = [self._t("selected_count", count=count)]
        if self.tiles:
            lines.extend(
                f"{index + 1:02d}.png  370 x 320  {'✓' if self.selected[index] else '-'}"
                for index in range(len(self.tiles))
            )
            lines.append("main.png  240 x 240")
            lines.append("tab.png   96 x 74")
        else:
            lines.append(self._t("need_grid"))
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "\n".join(lines))
        self.preview_text.configure(state="disabled")

    def export_line(self) -> None:
        selected = self.selected_tiles()
        if len(selected) != LINE_STATIC_SPEC.sticker_count:
            messagebox.showwarning(self._t("error"), self._t("need_eight", count=len(selected)))
            return
        filename = filedialog.asksaveasfilename(
            title=self._t("export_line"),
            defaultextension=".zip",
            filetypes=[("ZIP", "*.zip")],
            initialfile="line-stickers.zip",
        )
        if not filename:
            return
        try:
            spec = replace(LINE_STATIC_SPEC, sticker_padding=self.padding.get())
            output = export_line_zip(selected, filename, spec=spec)
            self.status.set(self._t("saved", path=output))
            messagebox.showinfo(self._t("done"), self._t("saved", path=output))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self._t("error"), str(exc))

    def export_png(self) -> None:
        if not self.tiles:
            messagebox.showinfo(self._t("error"), self._t("need_grid"))
            return
        filename = filedialog.asksaveasfilename(
            title=self._t("export_png"),
            defaultextension=".zip",
            filetypes=[("ZIP", "*.zip")],
            initialfile="transparent-stickers.zip",
        )
        if not filename:
            return
        try:
            spec = replace(LINE_STATIC_SPEC, sticker_padding=self.padding.get())
            output = export_stickers_zip(self.tiles, filename, spec=spec)
            self.status.set(self._t("saved", path=output))
            messagebox.showinfo(self._t("done"), self._t("saved", path=output))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror(self._t("error"), str(exc))


def _thumbnail(image: Image.Image) -> Image.Image:
    base = Image.new("RGBA", image.size, (248, 250, 252, 255))
    base.alpha_composite(image.convert("RGBA"))
    base.thumbnail((160, 140), Image.Resampling.LANCZOS)
    return base


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lang", choices=["zh-Hant", "en"], default="zh-Hant")
    parser.add_argument("--smoke", action="store_true")
    args, _ = parser.parse_known_args(argv)
    if args.smoke:
        return 0
    root = tk.Tk()
    StickerForgeApp(root, locale=args.lang)
    return int(root.mainloop() or 0)
