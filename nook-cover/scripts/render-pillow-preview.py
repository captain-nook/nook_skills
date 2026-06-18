#!/usr/bin/env python
"""Render a controlled Chinese Xiaohongshu cover preview with Pillow.

This is a temporary fallback for local preview when Node/Playwright file output
is blocked by the current sandbox.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "xhs-v01"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1440
RED = (241, 17, 54, 255)
MUTED = (95, 95, 95, 255)


def get_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\simhei.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_center(draw: ImageDraw.ImageDraw, x1: int, x2: int, y: int, text: str, font, fill) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((x1 + (x2 - x1 - (box[2] - box[0])) / 2, y), text, font=font, fill=fill)


def main() -> None:
    img = Image.new("RGBA", (W, H), "#a72d29")
    draw = ImageDraw.Draw(img)

    for y in range(H):
        t = y / (H - 1)
        r = int(142 + (255 - 142) * t)
        g = int(36 + (126 - 36) * t)
        b = int(36 + (103 - 36) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    for x in range(0, W, 54):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 36), width=1)
    for y in range(0, H, 54):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 36), width=1)

    card_w, card_h = 904, 1292
    card_x, card_y = 88, 74
    shadow = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle([0, 0, card_w, card_h], radius=62, fill=(60, 20, 16, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(35))
    img.alpha_composite(shadow, (card_x, card_y + 24))

    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle([0, 0, card_w, card_h], radius=62, fill=(255, 255, 255, 248))
    for x in range(0, card_w, 42):
        card_draw.line([(x, 0), (x, card_h)], fill=(241, 17, 54, 10), width=1)
    for y in range(0, card_h, 42):
        card_draw.line([(0, y), (card_w, y)], fill=(241, 17, 54, 10), width=1)
    img.alpha_composite(card, (card_x, card_y))

    draw = ImageDraw.Draw(img)
    f_top = get_font(32)
    f_tag = get_font(36)
    f_title = get_font(106)
    f_sub = get_font(48)
    f_num = get_font(30)
    f_flow = get_font(34)
    f_footer = get_font(24)

    draw.text((126, 136), "封面实验室", font=f_top, fill=MUTED)

    def pill(x: int, y: int, text: str) -> None:
        box = draw.textbbox((0, 0), text, font=f_tag)
        tw, th = box[2] - box[0], box[3] - box[1]
        draw.rounded_rectangle(
            [x, y, x + tw + 48, y + th + 24],
            radius=28,
            fill=(255, 255, 255, 220),
            outline=(210, 210, 210, 255),
            width=1,
        )
        draw.text((x + 24, y + 8), text, font=f_tag, fill=MUTED)

    pill(602, 119, "AI 工作流")
    pill(795, 119, "封面设计")

    draw.rounded_rectangle([442, 294, 638, 364], radius=35, fill=RED)
    draw.ellipse([464, 319, 484, 339], fill=(255, 255, 255, 255))
    draw.text((493, 307), "教程实测", font=f_top, fill=(255, 255, 255, 255))

    y = 410
    for line in ["一句话生成", "小红书封面"]:
        draw_center(draw, 88, 992, y, line, f_title, RED)
        y += 112

    draw.rounded_rectangle([160, 668, 920, 766], radius=28, fill=(245, 29, 60, 255))
    draw_center(draw, 160, 920, 690, "AI 视觉工作流实测", f_sub, (255, 255, 255, 255))

    boxes = [(160, "01", "brief"), (409, "02", "HTML"), (694, "03", "PNG")]
    for x, num, label in boxes:
        draw.rounded_rectangle([x, 1172, x + 228, 1320], radius=28, fill=(255, 236, 230, 245))
        draw.rounded_rectangle([x + 85, 1198, x + 143, 1256], radius=19, fill=(255, 255, 255, 245))
        draw_center(draw, x + 85, x + 143, 1206, num, f_num, RED)
        draw_center(draw, x, x + 228, 1271, label, f_flow, RED)

    for ax in [389, 674]:
        ay = 1246
        draw.line([(ax, ay), (ax + 32, ay)], fill=RED, width=6)
        draw.polygon([(ax + 32, ay - 12), (ax + 32, ay + 12), (ax + 50, ay)], fill=RED)

    draw.text((126, 1331), "nook-cover / 小红书封面 v0.1", font=f_footer, fill=(150, 150, 150, 255))
    right = "中文可控渲染"
    box = draw.textbbox((0, 0), right, font=f_footer)
    draw.text((954 - (box[2] - box[0]), 1331), right, font=f_footer, fill=(150, 150, 150, 255))

    path = OUT / "cover_final_pillow_v03.png"
    img.convert("RGB").save(path)
    print(path)


if __name__ == "__main__":
    main()
