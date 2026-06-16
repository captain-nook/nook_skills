#!/usr/bin/env python
"""Render a Xiaohongshu cover from a generated background and deterministic text."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont


CANVAS = (1080, 1440)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default(size=size)


def cover_crop(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    src = image.convert("RGB")
    src_ratio = src.width / src.height
    dst_ratio = size[0] / size[1]
    if src_ratio > dst_ratio:
        new_width = int(src.height * dst_ratio)
        left = (src.width - new_width) // 2
        src = src.crop((left, 0, left + new_width, src.height))
    else:
        new_height = int(src.width / dst_ratio)
        top = (src.height - new_height) // 2
        src = src.crop((0, top, src.width, top + new_height))
    return src.resize(size, Image.Resampling.LANCZOS)


def rounded_rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    fill,
    shadow=(255, 255, 255, 180),
    offset=(0, 5),
) -> None:
    x, y = xy
    draw.text((x + offset[0], y + offset[1]), text, font=font_obj, fill=shadow)
    draw.text((x, y), text, font=font_obj, fill=fill)


def text_width(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font_obj)
    return box[2] - box[0]


def render(background: Path, output: Path, title: str, subtitle: str) -> None:
    bg = cover_crop(Image.open(background), CANVAS)
    canvas = bg.convert("RGBA")

    # Calm the center so the title survives phone-thumbnail scale.
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    mask = Image.new("L", CANVAS, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((50, 44, 1030, 1218), radius=54, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    panel = Image.new("RGBA", CANVAS, (255, 249, 239, 244))
    overlay.alpha_composite(panel, (0, 0))
    canvas = Image.composite(overlay, canvas, mask).convert("RGBA")

    draw = ImageDraw.Draw(canvas)
    title_font = font(126, bold=True)
    title_font_small = font(112, bold=True)
    subtitle_font = font(54, bold=True)
    tag_font = font(34, bold=True)
    small_font = font(28, bold=True)
    mono_font = font(32, bold=True)

    # Hard-clean the title-safe zone in case the generated background contains pseudo text.
    rounded_rect(draw, (94, 52, 986, 704), 18, (255, 249, 239, 248))

    # Top identity row.
    rounded_rect(draw, (72, 74, 306, 130), 28, (21, 21, 21, 235))
    draw.text((100, 86), "AI 出图", font=tag_font, fill=(255, 255, 255, 255))
    rounded_rect(draw, (776, 74, 1008, 130), 28, (255, 255, 255, 210), outline=(20, 20, 20, 36), width=2)
    draw.text((808, 87), "免费模型", font=small_font, fill=(34, 34, 34, 235))

    # Main title: fixed manual break for the requested phrase.
    lines = ["魔搭社区", "免费出图"]
    y = 268
    for idx, line in enumerate(lines):
        current_font = title_font if idx == 0 else title_font_small
        width = text_width(draw, line, current_font)
        x = (CANVAS[0] - width) // 2
        color = (21, 21, 21, 255) if idx == 0 else (255, 76, 48, 255)
        draw_text_with_shadow(draw, (x, y), line, current_font, color, shadow=(255, 255, 255, 210), offset=(0, 7))
        y += 136

    # Subtitle pill.
    subtitle_text = subtitle
    sub_w = text_width(draw, subtitle_text, subtitle_font)
    pill_w = sub_w + 86
    pill_x = (CANVAS[0] - pill_w) // 2
    rounded_rect(draw, (pill_x, 588, pill_x + pill_w, 678), 45, (18, 18, 18, 238))
    draw.text((pill_x + 43, 604), subtitle_text, font=subtitle_font, fill=(255, 255, 255, 255))

    # Value bullets.
    card = (116, 812, 964, 1092)
    rounded_rect(draw, card, 38, (255, 255, 255, 218), outline=(20, 20, 20, 28), width=2)
    bullets = ["中文封面更稳", "高质量主视觉", "适合海报首图"]
    for i, item in enumerate(bullets):
        cy = 856 + i * 78
        rounded_rect(draw, (154, cy, 208, cy + 54), 18, (9, 143, 132, 245))
        draw.text((168, cy + 8), f"{i + 1}", font=mono_font, fill=(255, 255, 255, 255))
        draw.text((232, cy + 6), item, font=tag_font, fill=(28, 28, 28, 242))

    # Bottom note.
    rounded_rect(draw, (164, 1214, 916, 1288), 36, (255, 78, 48, 238))
    draw.text((215, 1230), "Z-Image 测试 / Qwen 做成品", font=tag_font, fill=(255, 255, 255, 255))
    draw.text((76, 1344), "nook-qwen-image · xhs cover validation", font=small_font, fill=(24, 24, 24, 160))

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=95)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a Xiaohongshu cover with deterministic Chinese text.")
    parser.add_argument("--background", required=True, help="Generated background image path")
    parser.add_argument("--output", required=True, help="Output cover path")
    parser.add_argument("--title", default="魔搭社区免费出图", help="Cover title")
    parser.add_argument("--subtitle", default="Qwen-image", help="Cover subtitle")
    args = parser.parse_args(argv)
    render(Path(args.background), Path(args.output), args.title, args.subtitle)
    print(f"OUTPUT_PATH={Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
