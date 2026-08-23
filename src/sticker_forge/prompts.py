from __future__ import annotations

from pathlib import Path
import sys

from .spec import resolve_chroma_key


SUPPORTED_LOCALES = ("zh-Hant", "en")

DEFAULT_FIELDS = {
    "zh-Hant": {
        "character": "原創可愛角色",
        "theme": "日常聊天貼圖",
        "tone": "可愛、清楚、友善",
        "style": "粗黑線、扁平上色、適合聊天視窗縮圖閱讀",
        "language": "繁體中文",
    },
    "en": {
        "character": "an original cute character",
        "theme": "everyday chat stickers",
        "tone": "cute, clear, friendly",
        "style": "bold black outlines, flat colors, readable at chat thumbnail size",
        "language": "English",
    },
}

DEFAULT_TEXTS = {
    "zh-Hant": ["早安", "謝謝", "收到", "加油", "辛苦了", "太棒了", "等一下", "晚安"],
    "en": ["Good morning", "Thanks", "Got it", "You can do it", "Nice work", "Great", "Wait a sec", "Good night"],
}

DEFAULT_ACTIONS = {
    "zh-Hant": [
        "開心揮手",
        "雙手比心",
        "點頭確認",
        "握拳打氣",
        "擦汗微笑",
        "跳起來歡呼",
        "舉手示意暫停",
        "抱著枕頭打呵欠",
    ],
    "en": [
        "happily waving",
        "making a heart with both hands",
        "nodding in confirmation",
        "cheering with a clenched fist",
        "smiling while wiping sweat",
        "jumping in celebration",
        "raising one hand to pause",
        "yawning while hugging a pillow",
    ],
}


SUGGESTIONS = {
    "zh-Hant": {
        "character": ["原創可愛角色", "原創柴犬", "原創貓咪", "圓臉小人", "Q版女孩", "療癒白熊", "上班族貓", "貓耳少女", "小恐龍"],
        "theme": ["日常聊天貼圖", "上班族日常", "情侶對話", "學生生活", "節慶祝福", "療癒安慰", "搞笑吐槽", "寵物日常"],
        "tone": ["可愛、清楚、友善", "活潑、搞笑、有活力", "溫暖、療癒、安心", "酷、簡約、有個性", "傲嬌、吐槽、幽默"],
        "style": ["粗黑線、扁平上色、適合聊天視窗縮圖閱讀", "日系可愛、柔和色彩", "韓系簡約、線條乾淨", "手繪水彩風", "像素風、復古", "貼紙風、白色描邊"],
        "language": ["繁體中文", "English", "日本語", "한국어", "粵語"],
        "texts": ["早安", "晚安", "謝謝", "抱歉", "收到", "OK", "加油", "辛苦了", "太棒了", "等一下", "在嗎", "哈哈哈", "愛你", "生日快樂", "恭喜", "掰掰"],
        "actions": ["開心揮手", "雙手比心", "點頭確認", "握拳打氣", "大哭", "大笑", "跳起來歡呼", "比讚", "鞠躬道謝", "舉手發問", "睡覺打呼", "震驚張嘴", "翻白眼", "送花", "灑花", "托腮思考"],
    },
    "en": {
        "character": ["an original cute character", "an original shiba dog", "an original cat", "a round-faced blob", "a chibi girl", "a healing polar bear", "an office-worker cat", "a cat-ear girl", "a little dinosaur"],
        "theme": ["everyday chat stickers", "office worker life", "couple chat", "student life", "holiday greetings", "comfort and healing", "funny reactions", "pet daily life"],
        "tone": ["cute, clear, friendly", "lively, funny, energetic", "warm, healing, reassuring", "cool, minimal, stylish", "tsundere, snarky, witty"],
        "style": ["bold black outlines, flat colors, readable at chat thumbnail size", "soft Japanese kawaii colors", "clean minimal Korean style", "hand-drawn watercolor", "retro pixel art", "sticker style with a white outline"],
        "language": ["English", "繁體中文", "日本語", "한국어"],
        "texts": ["Good morning", "Good night", "Thanks", "Sorry", "Got it", "OK", "You can do it", "Nice work", "Great", "Wait a sec", "You there?", "Haha", "Love you", "Happy birthday", "Congrats", "Bye"],
        "actions": ["happily waving", "making a heart with both hands", "nodding in confirmation", "cheering with a clenched fist", "crying", "laughing", "jumping in celebration", "thumbs up", "bowing in thanks", "raising a hand to ask", "sleeping and snoring", "shocked with mouth open", "rolling eyes", "giving flowers", "throwing confetti", "resting chin while thinking"],
    },
}


# Full-field starter packs: pick one to fill character/theme/tone/style plus the
# 8 texts and 8 actions with a coherent set, then tweak.
PROMPT_PRESETS = {
    "zh-Hant": {
        "healing-bear": {
            "label": "療癒白熊",
            "character": "療癒白熊",
            "theme": "溫暖療癒日常",
            "tone": "溫暖、療癒、安心",
            "style": "圓潤線條、柔和粉彩、適合聊天縮圖閱讀",
            "language": "繁體中文",
            "texts": ["早安", "晚安", "抱抱", "辛苦了", "沒關係", "謝謝你", "加油", "愛你"],
            "actions": ["張開雙手討抱", "蓋棉被睡覺", "遞上熱茶", "拍拍肩膀", "雙手比愛心", "揮手道別", "豎起大拇指", "臉紅害羞"],
        },
        "office-cat": {
            "label": "上班族貓",
            "character": "上班族貓",
            "theme": "辦公室日常",
            "tone": "幽默、無奈、有活力",
            "style": "粗黑線、扁平上色、表情誇張",
            "language": "繁體中文",
            "texts": ["收到", "開會中", "已讀", "加班中", "下班囉", "再一下", "交給我", "喝杯咖啡"],
            "actions": ["猛敲鍵盤", "癱在桌上", "舉手發問", "比 OK 手勢", "翻白眼", "伸懶腰", "端著咖啡", "歡呼下班"],
        },
        "couple-bears": {
            "label": "情侶小熊",
            "character": "情侶小熊",
            "theme": "情侶對話",
            "tone": "甜蜜、俏皮、撒嬌",
            "style": "柔和色彩、圓潤可愛",
            "language": "繁體中文",
            "texts": ["想你了", "在幹嘛", "晚安啾", "今天好嗎", "等你喔", "吃飯沒", "愛你喔", "抱一個"],
            "actions": ["飛吻", "雙手比心", "撒嬌拉衣角", "害羞摀臉", "開心揮手", "托腮想念", "張手討抱", "親一下"],
        },
        "festive": {
            "label": "節慶祝福",
            "character": "節慶小福",
            "theme": "節慶祝福",
            "tone": "喜氣、熱情、祝福",
            "style": "鮮明色彩、喜氣元素、粗線條",
            "language": "繁體中文",
            "texts": ["新年快樂", "恭喜發財", "生日快樂", "聖誕快樂", "節日愉快", "平安喜樂", "萬事如意", "謝謝招待"],
            "actions": ["放鞭炮", "舉杯慶祝", "灑花瓣", "捧著禮物", "比讚祝福", "開心跳躍", "鞠躬拜年", "揮手祝福"],
        },
    },
    "en": {
        "healing-bear": {
            "label": "Healing bear",
            "character": "a healing white bear",
            "theme": "warm everyday comfort",
            "tone": "warm, healing, reassuring",
            "style": "rounded lines, soft pastels, readable at chat thumbnail size",
            "language": "English",
            "texts": ["Good morning", "Good night", "Hugs", "Nice work", "It's okay", "Thank you", "You can do it", "Love you"],
            "actions": ["arms open for a hug", "sleeping under a blanket", "offering hot tea", "patting a shoulder", "making a heart with both hands", "waving goodbye", "thumbs up", "blushing shyly"],
        },
        "office-cat": {
            "label": "Office cat",
            "character": "an office-worker cat",
            "theme": "office life",
            "tone": "funny, weary, energetic",
            "style": "bold outlines, flat colors, exaggerated expressions",
            "language": "English",
            "texts": ["Got it", "In a meeting", "Seen", "Working late", "Off work!", "One moment", "Leave it to me", "Coffee break"],
            "actions": ["typing furiously", "slumped on the desk", "raising a hand to ask", "an OK sign", "rolling eyes", "stretching", "carrying coffee", "cheering after work"],
        },
        "couple-bears": {
            "label": "Couple bears",
            "character": "a couple of little bears",
            "theme": "couple chat",
            "tone": "sweet, playful, affectionate",
            "style": "soft colors, round and cute",
            "language": "English",
            "texts": ["Miss you", "What's up", "Night kiss", "How was your day", "Waiting for you", "Have you eaten", "Love you", "Hug me"],
            "actions": ["blowing a kiss", "making a heart", "tugging a sleeve cutely", "hiding face shyly", "waving happily", "resting chin missing you", "arms open for a hug", "a little kiss"],
        },
        "festive": {
            "label": "Festive",
            "character": "a lucky festive mascot",
            "theme": "holiday greetings",
            "tone": "festive, warm, celebratory",
            "style": "bright colors, festive motifs, bold lines",
            "language": "English",
            "texts": ["Happy New Year", "Best wishes", "Happy Birthday", "Merry Christmas", "Happy Holidays", "Peace and joy", "All the best", "Thanks for having me"],
            "actions": ["lighting firecrackers", "toasting", "throwing confetti", "holding a gift", "thumbs up blessing", "jumping happily", "bowing in greeting", "waving a blessing"],
        },
    },
}


def normalize_locale(locale: str | None) -> str:
    if locale in SUPPORTED_LOCALES:
        return str(locale)
    return "zh-Hant"


def template_path(locale: str | None = None) -> Path:
    locale = normalize_locale(locale)
    filename = "line-static-3x3.en.md" if locale == "en" else "line-static-3x3.md"
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / "prompts" / filename
    return Path(__file__).resolve().parents[2] / "prompts" / filename


def load_template(locale: str | None = None) -> str:
    return template_path(locale).read_text(encoding="utf-8")


def render_line_static_prompt(
    *,
    with_text: bool = True,
    locale: str | None = "zh-Hant",
    character: str | None = None,
    theme: str | None = None,
    tone: str | None = None,
    style: str | None = None,
    language: str | None = None,
    texts: list[str] | None = None,
    actions: list[str] | None = None,
    chroma_key: str = "green",
) -> str:
    locale = normalize_locale(locale)
    defaults = DEFAULT_FIELDS[locale]
    values = {
        "character": character or defaults["character"],
        "theme": theme or defaults["theme"],
        "tone": tone or defaults["tone"],
        "style": style or defaults["style"],
        "language": language or defaults["language"],
    }
    key = resolve_chroma_key(chroma_key)
    values.update(
        {
            "chroma_key_label": key.label,
            "chroma_key_hex": key.hex,
            "chroma_key_avoid": key.avoid,
            "chroma_key_substitutions": key.substitutions,
        }
    )

    resolved_texts = (texts or DEFAULT_TEXTS[locale])[:8]
    resolved_actions = (actions or DEFAULT_ACTIONS[locale])[:8]
    if len(resolved_texts) != 8:
        raise ValueError("texts must contain exactly 8 entries")
    if len(resolved_actions) != 8:
        raise ValueError("actions must contain exactly 8 entries")

    for index, text in enumerate(resolved_texts, start=1):
        values[f"text_{index}"] = text
    for index, action in enumerate(resolved_actions, start=1):
        values[f"action_{index}"] = action

    template = _selected_section(load_template(locale), with_text=with_text, locale=locale)
    return template.format(**values).strip() + "\n"


def _selected_section(template: str, *, with_text: bool, locale: str) -> str:
    if locale == "en":
        marker = "## Text version" if with_text else "## No-text version"
        next_marker = "## No-text version" if with_text else "## "
    else:
        marker = "## 有字版" if with_text else "## 無字版"
        next_marker = "## 無字版" if with_text else "## "
    start = template.index(marker)
    if with_text:
        end = template.index(next_marker, start + len(marker))
        return template[start:end]
    return template[start:]
