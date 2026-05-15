from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PREVIEW_DIR = ROOT / "docs" / "previews"
OUTPUT_DIR = ROOT / "docs"
UI_DIR = ROOT / "assets" / "ui"

SEASONS = [
    ("SEMI", "season_spring.png", (235, 126, 168)),
    ("PANAS", "season_summer.png", (238, 180, 80)),
    ("GUGUR", "season_autumn.png", (202, 104, 52)),
    ("DINGIN", "season_winter.png", (111, 172, 220)),
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def crop_fill(image: Image.Image, size: tuple[int, int], centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=centering)


def alpha_rect(size: tuple[int, int], color: tuple[int, int, int], alpha: int) -> Image.Image:
    return Image.new("RGBA", size, (*color, alpha))


def vertical_gradient(size: tuple[int, int], top: int, middle: int, bottom: int) -> Image.Image:
    width, height = size
    gradient = Image.new("RGBA", size)
    pixels = gradient.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        if t < 0.5:
            local = t / 0.5
            alpha = int(top + (middle - top) * local)
        else:
            local = (t - 0.5) / 0.5
            alpha = int(middle + (bottom - middle) * local)
        for x in range(width):
            pixels[x, y] = (4, 8, 15, alpha)
    return gradient


def text_bbox(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox(xy, text, font=font)


def centered_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    canvas_width: int,
    shadow: bool = True,
) -> int:
    bbox = text_bbox(draw, (0, 0), text, font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = (canvas_width - width) // 2
    if shadow:
        draw.text((x + 4, y + 5), text, font=font, fill=(0, 0, 0, 130))
    draw.text((x, y), text, font=font, fill=fill)
    return y + height


def draw_tag(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int] = (255, 255, 255, 230),
    outline: tuple[int, int, int, int] = (255, 255, 255, 60),
) -> tuple[int, int]:
    x, y = xy
    pad_x, pad_y = 18, 9
    bbox = text_bbox(draw, (0, 0), text, font)
    width = bbox[2] - bbox[0] + pad_x * 2
    height = bbox[3] - bbox[1] + pad_y * 2
    draw.rounded_rectangle((x, y, x + width, y + height), radius=18, fill=(11, 18, 28, 160), outline=outline, width=1)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=fill)
    return x + width, y + height


def generate_wide_cover() -> Path:
    width, height = 1920, 1080
    panel_width = width // len(SEASONS)
    canvas = Image.new("RGBA", (width, height), (5, 9, 16, 255))

    for index, (label, filename, accent) in enumerate(SEASONS):
        source = Image.open(PREVIEW_DIR / filename)
        panel = crop_fill(source, (panel_width + 2, height), centering=(0.5, 0.5)).convert("RGBA")
        panel.alpha_composite(alpha_rect(panel.size, accent, 34))
        panel.alpha_composite(alpha_rect(panel.size, (0, 0, 0), 44))
        x = index * panel_width
        canvas.alpha_composite(panel, (x, 0))

    canvas.alpha_composite(vertical_gradient((width, height), 150, 42, 185), (0, 0))

    draw = ImageDraw.Draw(canvas)
    for x in range(panel_width, width, panel_width):
        draw.line((x, 0, x, height), fill=(255, 255, 255, 38), width=2)

    label_font = load_font(25, bold=True)
    small_font = load_font(30)
    title_font = load_font(104, bold=True)
    subtitle_font = load_font(43)
    feature_font = load_font(28, bold=True)

    centered_text(draw, 150, "OPENGL BASIC 3D", label_font, (255, 229, 238, 225), width)
    centered_text(draw, 235, "SEASONAL SAKURA SCENE", title_font, (255, 255, 255, 255), width)
    centered_text(
        draw,
        365,
        "Simulasi taman Jepang 3D interaktif dengan transisi empat musim",
        subtitle_font,
        (232, 241, 246, 235),
        width,
    )
    centered_text(draw, 436, "Python - Pygame - ModernGL - GLSL", small_font, (224, 229, 236, 210), width)

    tags = ["Sakura", "Fuji", "Jembatan", "Kolam", "HUD", "Shader", "Audio"]
    tag_widths = []
    for tag in tags:
        bbox = text_bbox(draw, (0, 0), tag, feature_font)
        tag_widths.append((bbox[2] - bbox[0]) + 36)
    total_width = sum(tag_widths) + (len(tags) - 1) * 14
    x = (width - total_width) // 2
    y = 900
    for tag in tags:
        x, _ = draw_tag(draw, (x, y), tag, feature_font)
        x += 14

    season_font = load_font(26, bold=True)
    for index, (label, _, accent) in enumerate(SEASONS):
        bbox = text_bbox(draw, (0, 0), label, season_font)
        text_width = bbox[2] - bbox[0]
        x = index * panel_width + (panel_width - text_width) // 2
        draw.text((x + 2, 811), label, font=season_font, fill=(0, 0, 0, 130))
        draw.text((x, 809), label, font=season_font, fill=(*accent, 255))

    output = OUTPUT_DIR / "cover_project_16x9.png"
    canvas.convert("RGB").save(output, quality=95, optimize=True)
    return output


def generate_a4_cover() -> Path:
    width, height = 2480, 3508
    canvas = Image.new("RGBA", (width, height), (5, 9, 16, 255))
    draw = ImageDraw.Draw(canvas)

    hero = Image.open(PREVIEW_DIR / "season_spring.png")
    hero = crop_fill(hero, (width, height), centering=(0.48, 0.48)).filter(ImageFilter.GaussianBlur(1.1)).convert("RGBA")
    hero.alpha_composite(alpha_rect(hero.size, (0, 0, 0), 72))
    canvas.alpha_composite(hero, (0, 0))
    canvas.alpha_composite(vertical_gradient((width, height), 170, 56, 210), (0, 0))

    thumb_margin = 180
    thumb_gap = 24
    thumb_width = (width - thumb_margin * 2 - thumb_gap * 3) // 4
    thumb_height = 430
    thumb_y = 2140
    for index, (label, filename, accent) in enumerate(SEASONS):
        image = crop_fill(Image.open(PREVIEW_DIR / filename), (thumb_width, thumb_height)).convert("RGBA")
        image.alpha_composite(alpha_rect(image.size, accent, 26))
        x = thumb_margin + index * (thumb_width + thumb_gap)
        canvas.alpha_composite(image, (x, thumb_y))
        draw.rounded_rectangle((x, thumb_y, x + thumb_width, thumb_y + thumb_height), radius=28, outline=(*accent, 210), width=6)
        label_font = load_font(34, bold=True)
        bbox = text_bbox(draw, (0, 0), label, label_font)
        label_x = x + (thumb_width - (bbox[2] - bbox[0])) // 2
        draw.text((label_x + 2, thumb_y + thumb_height - 68), label, font=label_font, fill=(0, 0, 0, 160))
        draw.text((label_x, thumb_y + thumb_height - 71), label, font=label_font, fill=(255, 255, 255, 245))

    top_font = load_font(45, bold=True)
    title_font = load_font(112, bold=True)
    subtitle_font = load_font(48)
    body_font = load_font(38)
    field_font = load_font(42)

    centered_text(draw, 530, "LAPORAN PROJECT GRAFIKA KOMPUTER", top_font, (255, 229, 238, 225), width)
    centered_text(draw, 690, "SEASONAL SAKURA SCENE", title_font, (255, 255, 255, 255), width)
    centered_text(draw, 840, "OpenGL Basic 3D - Python, Pygame, ModernGL, GLSL", subtitle_font, (232, 241, 246, 235), width)
    centered_text(
        draw,
        940,
        "Taman Jepang 3D dengan siklus siang-malam, cuaca, HUD, audio, dan transisi empat musim",
        body_font,
        (224, 229, 236, 220),
        width,
    )

    info_x = 445
    info_y = 2760
    line_gap = 105
    info_fields = ["Nama", "NIM", "Kelas", "Dosen"]
    for offset, field in enumerate(info_fields):
        y = info_y + offset * line_gap
        draw.text((info_x, y), f"{field:<7}: ", font=field_font, fill=(255, 255, 255, 235))
        draw.line((info_x + 230, y + 55, width - info_x, y + 55), fill=(255, 255, 255, 160), width=3)

    centered_text(draw, 3300, "2026", load_font(42, bold=True), (255, 255, 255, 220), width)

    output = OUTPUT_DIR / "cover_laporan_a4.png"
    canvas.convert("RGB").save(output, quality=95, optimize=True)
    return output


def generate_game_cover() -> Path:
    width, height = 1920, 1080
    panel_width = width // len(SEASONS)
    canvas = Image.new("RGBA", (width, height), (5, 9, 16, 255))

    for index, (_label, filename, accent) in enumerate(SEASONS):
        source = Image.open(PREVIEW_DIR / filename)
        panel = crop_fill(source, (panel_width + 2, height), centering=(0.5, 0.5)).convert("RGBA")
        panel.alpha_composite(alpha_rect(panel.size, accent, 26))
        panel.alpha_composite(alpha_rect(panel.size, (0, 0, 0), 70))
        canvas.alpha_composite(panel, (index * panel_width, 0))

    canvas.alpha_composite(vertical_gradient((width, height), 176, 52, 204), (0, 0))
    draw = ImageDraw.Draw(canvas)

    for x in range(panel_width, width, panel_width):
        draw.line((x, 0, x, height), fill=(255, 255, 255, 34), width=2)

    eyebrow_font = load_font(30, bold=True)
    title_font = load_font(124, bold=True)
    subtitle_font = load_font(42)
    tagline_font = load_font(28)
    small_font = load_font(24)
    season_font = load_font(25, bold=True)

    centered_text(draw, 176, "OPENGL BASIC 3D", eyebrow_font, (255, 229, 238, 220), width)
    centered_text(draw, 290, "SEASONAL SAKURA", title_font, (255, 255, 255, 255), width)
    centered_text(draw, 432, "FOUR SEASONS GARDEN", subtitle_font, (226, 239, 246, 232), width)
    centered_text(
        draw,
        505,
        "Jelajahi taman Jepang, Fuji, jembatan, kolam, dan cuaca musiman",
        tagline_font,
        (218, 229, 238, 214),
        width,
    )
    centered_text(draw, 970, "Python - Pygame - ModernGL - GLSL", small_font, (217, 226, 234, 206), width)

    for index, (label, _filename, accent) in enumerate(SEASONS):
        bbox = text_bbox(draw, (0, 0), label, season_font)
        text_width = bbox[2] - bbox[0]
        x = index * panel_width + (panel_width - text_width) // 2
        draw.text((x + 2, 742), label, font=season_font, fill=(0, 0, 0, 140))
        draw.text((x, 740), label, font=season_font, fill=(*accent, 255))

    UI_DIR.mkdir(parents=True, exist_ok=True)
    output = UI_DIR / "game_cover.png"
    canvas.convert("RGB").save(output, quality=95, optimize=True)
    return output


def generate_menu_background() -> Path:
    width, height = 1920, 1080
    source = Image.open(PREVIEW_DIR / "season_spring.png")
    clean_source = source.crop((0, 0, source.width, int(source.height * 0.78)))
    canvas = crop_fill(clean_source, (width, height), centering=(0.50, 0.42)).filter(ImageFilter.GaussianBlur(0.8)).convert("RGBA")
    canvas.alpha_composite(alpha_rect((width, height), (4, 8, 15), 58))
    canvas.alpha_composite(vertical_gradient((width, height), 86, 28, 150), (0, 0))

    UI_DIR.mkdir(parents=True, exist_ok=True)
    output = UI_DIR / "menu_background.png"
    canvas.convert("RGB").save(output, quality=95, optimize=True)
    return output


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    wide = generate_wide_cover()
    a4 = generate_a4_cover()
    game = generate_game_cover()
    menu = generate_menu_background()
    print(f"Generated {wide.relative_to(ROOT)}")
    print(f"Generated {a4.relative_to(ROOT)}")
    print(f"Generated {game.relative_to(ROOT)}")
    print(f"Generated {menu.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
