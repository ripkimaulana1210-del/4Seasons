from __future__ import annotations

import argparse
import math
import string
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.data.scene_config import HOUSE_SPECS, POND_FENCE_ARCS, SCENE_LAYOUT


DEFAULT_OUTPUT = ROOT / "docs" / "previews" / "sectors"
DEFAULT_BOUNDS = (-22.0, -22.0, 22.0, 22.0)
CONTENT_PLAN = {
    "A1": ("Buffer kiri", ["Batu + semak rendah", "Transisi ke kebun bambu", "Kelopak tipis di tanah"]),
    "B1": ("Tepi desa", ["Detail rumah kecil", "Batu jalan", "Pagar + lampu taman"]),
    "C1": ("Desa atas", ["2 halaman rumah", "Sumur / gerobak / jemuran", "Props kecil saja"]),
    "D1": ("Lapangan kosong", ["Rumput tinggi", "Orang-orangan / tunggul", "Sedikit batu / pohon"]),
    "A2": ("Desa bamboo mill", ["Bambu lebih padat", "Jalan H7-Bath-Mill", "Pagar kayu + stone lantern"]),
    "B2": ("Stream ke kolam", ["Stepping stones", "Reed + lily pad", "Boat / koi focus"]),
    "C2": ("Area shrine", ["Jalur torii", "Offering + ema board", "Lentera merah"]),
    "D2": ("Sawah / farm", ["Baris tanaman padi", "Tool shed", "Pagar + alat tani"]),
    "A3": ("Desa bamboo tea", ["Bambu padat dekat H6/Tea", "Jalan tanah + stone path", "Sumur kecil + petal tanah"]),
    "B3": ("Piknik hanami", ["Payung + tikar piknik", "Bento / bench", "Tumpukan petal"]),
    "C3": ("Hero core", ["Sakura + island", "Landing bridge", "Props musim utama"]),
    "D3": ("Utility desa", ["Storage shed", "Bambu", "Side path kecil"]),
    "A4": ("Pojok taman kiri", ["Secret path dari tea", "Pagar kecil + batu", "Petal tipis, tetap lega"]),
    "B4": ("Viewing deck", ["Pavilion / deck", "Bench + railing", "Props arah kolam"]),
    "C4": ("Main entrance", ["Secondary torii", "Jalur lurus", "Stone lantern / sign"]),
    "D4": ("Tepi rumah", ["Satu rumah kecil", "Pagar + kebun dapur", "Tree filler"]),
}


@dataclass(frozen=True)
class Feature:
    label: str
    x: float
    z: float
    kind: str
    yaw: float = 0.0
    width: float = 0.8
    depth: float = 0.8


class MapProjection:
    def __init__(self, bounds: tuple[float, float, float, float], size: int, padding: int) -> None:
        self.x_min, self.z_min, self.x_max, self.z_max = bounds
        self.size = size
        self.padding = padding
        self.inner = size - padding * 2
        self.scale = self.inner / max(self.x_max - self.x_min, self.z_max - self.z_min)
        map_width = (self.x_max - self.x_min) * self.scale
        map_height = (self.z_max - self.z_min) * self.scale
        self.left = (size - map_width) * 0.5
        self.top = (size - map_height) * 0.5
        self.right = self.left + map_width
        self.bottom = self.top + map_height

    def to_px(self, x: float, z: float) -> tuple[float, float]:
        # Top of the map is negative Z, matching the Fuji/background side.
        px = self.left + (x - self.x_min) * self.scale
        py = self.top + (z - self.z_min) * self.scale
        return px, py

    def world_radius(self, value: float) -> float:
        return value * self.scale

    def ellipse_bbox(self, x: float, z: float, rx: float, rz: float | None = None) -> tuple[float, float, float, float]:
        rz = rx if rz is None else rz
        px, py = self.to_px(x, z)
        return (
            px - self.world_radius(rx),
            py - self.world_radius(rz),
            px + self.world_radius(rx),
            py + self.world_radius(rz),
        )


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


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, int, int]:
    return draw.textbbox((0, 0), text, font=font)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: float) -> list[str]:
    lines = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        bbox = text_bbox(draw, candidate, font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def label_for(col: int, row: int) -> str:
    if col >= len(string.ascii_uppercase):
        return f"{col + 1}-{row + 1}"
    return f"{string.ascii_uppercase[col]}{row + 1}"


def draw_label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    *,
    fill: tuple[int, int, int, int] = (18, 24, 30, 226),
    outline: tuple[int, int, int, int] = (255, 210, 130, 230),
    text_fill: tuple[int, int, int, int] = (255, 255, 255, 255),
    radius: int = 10,
) -> None:
    x, y = xy
    bbox = text_bbox(draw, text, font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    pad_x, pad_y = 12, 7
    draw.rounded_rectangle(
        (x, y, x + width + pad_x * 2, y + height + pad_y * 2),
        radius=radius,
        fill=fill,
        outline=outline,
        width=2,
    )
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=text_fill)


def local_to_world(base_x: float, base_z: float, yaw: float, local_x: float, local_z: float) -> tuple[float, float]:
    angle = math.radians(yaw)
    return (
        base_x + local_x * math.cos(angle) + local_z * math.sin(angle),
        base_z - local_x * math.sin(angle) + local_z * math.cos(angle),
    )


def rotated_rect_points(
    projection: MapProjection,
    x: float,
    z: float,
    yaw: float,
    width: float,
    depth: float,
) -> list[tuple[float, float]]:
    corners = [
        (-width * 0.5, -depth * 0.5),
        (width * 0.5, -depth * 0.5),
        (width * 0.5, depth * 0.5),
        (-width * 0.5, depth * 0.5),
    ]
    return [projection.to_px(*local_to_world(x, z, yaw, local_x, local_z)) for local_x, local_z in corners]


def draw_rotated_rect(
    draw: ImageDraw.ImageDraw,
    projection: MapProjection,
    feature: Feature,
    fill: tuple[int, int, int, int],
    outline: tuple[int, int, int, int],
) -> None:
    points = rotated_rect_points(projection, feature.x, feature.z, feature.yaw, feature.width, feature.depth)
    draw.polygon(points, fill=fill, outline=outline)


def bridge_points() -> list[tuple[float, float]]:
    pond_radius_scale = SCENE_LAYOUT["pond"]["radius_scale"]
    island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]
    start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
    control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
    end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)
    points = []
    for index in range(25):
        t = index / 24.0
        inv_t = 1.0 - t
        x = inv_t * inv_t * start[0] + 2.0 * inv_t * t * control[0] + t * t * end[0]
        z = inv_t * inv_t * start[1] + 2.0 * inv_t * t * control[1] + t * t * end[1]
        points.append((x, z))
    return points


def house_features() -> list[Feature]:
    features = []
    for idx, (angle_deg, radius, body_scale, _body_color, _roof_color, _trim_color, yaw_offset, _variant) in enumerate(HOUSE_SPECS, 1):
        angle = math.radians(angle_deg)
        radial_x = math.cos(angle)
        radial_z = math.sin(angle)
        x = radial_x * radius
        z = radial_z * radius
        front_x = -radial_x
        front_z = -radial_z
        yaw = math.degrees(math.atan2(front_x, front_z)) + yaw_offset
        width, _height, depth = body_scale
        features.append(Feature(f"H{idx:02d}", x, z, "house", yaw, width * 1.5, depth * 1.5))
    return features


def building_features() -> list[Feature]:
    layout = SCENE_LAYOUT["building_additions"]
    sizes = {
        "tea_house": (2.0, 1.5),
        "pavilion": (1.5, 1.5),
        "water_mill": (1.8, 1.3),
        "secondary_torii": (2.2, 0.7),
        "yatai_row": (2.7, 1.0),
        "bathhouse": (2.2, 1.7),
        "storage_shed": (1.4, 1.0),
        "viewing_deck": (1.8, 1.2),
        "rice_field": (3.2, 2.4),
    }
    labels = {
        "tea_house": "Tea",
        "pavilion": "Pav",
        "water_mill": "Mill",
        "secondary_torii": "Torii2",
        "yatai_row": "Yatai",
        "bathhouse": "Bath",
        "storage_shed": "Shed",
        "viewing_deck": "Deck",
        "rice_field": "Rice",
    }
    features = []
    for name, config in layout.items():
        if "pos" not in config:
            continue
        width, depth = sizes.get(name, (1.5, 1.2))
        scale = config.get("scale", 1.0)
        x, z = config["pos"]
        features.append(Feature(labels.get(name, name), x, z, "building", config.get("yaw", 0.0), width * scale, depth * scale))
    return features


def landmark_features() -> list[Feature]:
    return [
        Feature("Sakura", 0.0, 0.0, "tree", 0.0, 3.6, 3.6),
        Feature("Torii", 8.9, -6.9, "shrine", -30.0, 1.7, 0.8),
        Feature("Shrine", 10.3, -8.2, "shrine", -20.0, 1.4, 1.1),
        Feature("Stream", -7.4, -3.8, "water", -38.0, 2.3, 0.7),
        Feature("Boat", -2.8 * SCENE_LAYOUT["pond"]["radius_scale"], -2.6 * SCENE_LAYOUT["pond"]["radius_scale"], "water", 24.0, 0.9, 1.4),
        Feature("Bamboo", -13.6, 2.4, "tree", 0.0, 0.9, 0.9),
        Feature("Bamboo", 13.2, 3.6, "tree", 0.0, 0.9, 0.9),
        Feature("Bamboo", -12.8, -7.2, "tree", 0.0, 0.9, 0.9),
        Feature("Tree", -15.0, -11.0, "tree", 0.0, 1.3, 1.3),
        Feature("Tree", 15.4, -9.4, "tree", 0.0, 1.3, 1.3),
        Feature("Tree", 14.8, 8.8, "tree", 0.0, 1.3, 1.3),
        Feature("Umbrella", -6.1, 6.8, "season", 0.0, 1.4, 1.4),
        Feature("Festival", 10.4, 9.8, "season", -24.0, 2.5, 1.3),
        Feature("Leaves", 3.4, 8.2, "season", 0.0, 2.2, 1.0),
        Feature("Snow", 2.8, 5.4, "season", 0.0, 2.3, 1.0),
    ]


def all_features() -> list[Feature]:
    return house_features() + building_features() + landmark_features()


def draw_polyline(
    draw: ImageDraw.ImageDraw,
    projection: MapProjection,
    points: list[tuple[float, float]],
    fill: tuple[int, int, int, int],
    width: int,
) -> None:
    draw.line([projection.to_px(x, z) for x, z in points], fill=fill, width=width, joint="curve")


def draw_road_segment(
    draw: ImageDraw.ImageDraw,
    projection: MapProjection,
    start: tuple[float, float],
    end: tuple[float, float],
    width_world: float,
    fill: tuple[int, int, int, int],
) -> None:
    draw.line([projection.to_px(*start), projection.to_px(*end)], fill=fill, width=max(1, round(width_world * projection.scale)))


def draw_base_map(
    draw: ImageDraw.ImageDraw,
    projection: MapProjection,
    cols: int,
    rows: int,
    *,
    include_title: bool = True,
) -> None:
    title_font = load_font(36, bold=True)
    label_font = load_font(22, bold=True)
    small_font = load_font(17, bold=True)
    tiny_font = load_font(14)

    draw.rectangle((0, 0, projection.size, projection.size), fill=(242, 238, 222, 255))
    draw.rounded_rectangle(
        (projection.left, projection.top, projection.right, projection.bottom),
        radius=18,
        fill=(118, 147, 94, 255),
        outline=(70, 86, 58, 255),
        width=4,
    )

    for world in range(-20, 25, 5):
        if projection.x_min <= world <= projection.x_max:
            x, _ = projection.to_px(world, projection.z_min)
            draw.line((x, projection.top, x, projection.bottom), fill=(255, 255, 255, 58), width=1)
            draw.text((x + 4, projection.bottom + 12), f"X {world}", font=tiny_font, fill=(54, 68, 48, 255))
        if projection.z_min <= world <= projection.z_max:
            _, y = projection.to_px(projection.x_min, world)
            draw.line((projection.left, y, projection.right, y), fill=(255, 255, 255, 58), width=1)
            draw.text((projection.left - 56, y - 8), f"Z {world}", font=tiny_font, fill=(54, 68, 48, 255))

    road = SCENE_LAYOUT["road"]
    road_outer = road["radius"] + road["width"] * 0.5
    road_inner = road["radius"] - road["width"] * 0.5
    draw.ellipse(projection.ellipse_bbox(0.0, 0.0, road_outer), fill=(95, 87, 74, 255))
    draw.ellipse(projection.ellipse_bbox(0.0, 0.0, road_inner), fill=(118, 147, 94, 255))

    draw_road_segment(draw, projection, (0.0, road["radius"] + 0.20), (0.0, 23.4), 1.45, (95, 87, 74, 255))
    draw_road_segment(draw, projection, (road["radius"] + 0.20, 0.0), (22.4, 1.65), 1.14, (95, 87, 74, 255))
    draw_road_segment(draw, projection, (-road["radius"] - 0.20, 0.0), (-22.4, -1.35), 1.14, (95, 87, 74, 255))
    draw_road_segment(draw, projection, (0.0, -road["radius"] - 0.20), (-1.95, -23.2), 1.14, (95, 87, 74, 255))

    pond_radius = 4.80 * SCENE_LAYOUT["pond"]["radius_scale"]
    island_radius = 1.95 * SCENE_LAYOUT["island"]["radius_scale"]
    draw.ellipse(projection.ellipse_bbox(0.0, 0.0, pond_radius), fill=(80, 151, 175, 255), outline=(39, 103, 128, 255), width=4)
    draw.ellipse(projection.ellipse_bbox(0.0, 0.0, island_radius), fill=(122, 162, 88, 255), outline=(69, 108, 54, 255), width=3)

    fence_radius = pond_radius + 0.36
    fence_box = projection.ellipse_bbox(0.0, 0.0, fence_radius)
    for start, end, _count in POND_FENCE_ARCS:
        draw.arc(fence_box, start=start, end=end, fill=(102, 63, 36, 255), width=5)

    stream_points = [(-9.25, -5.45), (-8.35, -4.92), (-7.30, -4.30), (-6.45, -3.42), (-5.78, -2.35), (-5.12, -1.25)]
    draw_polyline(draw, projection, stream_points, (63, 142, 168, 255), max(3, round(0.38 * projection.scale)))

    bridge_line = bridge_points()
    draw_polyline(draw, projection, bridge_line, (80, 36, 28, 255), max(4, round(1.15 * projection.scale)))
    draw_polyline(draw, projection, bridge_line, (188, 64, 45, 255), max(2, round(0.72 * projection.scale)))

    bridge_start = bridge_line[0]
    bridge_angle = math.atan2(bridge_start[1], bridge_start[0])
    bridge_ring = (math.cos(bridge_angle) * road["radius"], math.sin(bridge_angle) * road["radius"])
    draw_road_segment(draw, projection, bridge_start, bridge_ring, 0.92, (125, 105, 74, 255))

    colors = {
        "house": ((170, 135, 87, 255), (85, 54, 32, 255)),
        "building": ((196, 145, 76, 255), (92, 56, 29, 255)),
        "shrine": ((194, 39, 28, 255), (81, 16, 14, 255)),
        "season": ((238, 164, 76, 255), (114, 63, 22, 255)),
    }

    for feature in house_features():
        draw_rotated_rect(draw, projection, feature, colors["house"][0], colors["house"][1])

    for feature in building_features():
        color = colors["building"]
        if feature.label == "Rice":
            color = ((108, 170, 111, 255), (47, 95, 53, 255))
        draw_rotated_rect(draw, projection, feature, color[0], color[1])

    for feature in landmark_features():
        px, py = projection.to_px(feature.x, feature.z)
        if feature.kind == "tree":
            radius = max(8, round(feature.width * projection.scale * 0.38))
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(204, 112, 148, 230), outline=(88, 58, 55, 255), width=2)
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(82, 48, 30, 255))
        elif feature.kind == "water":
            draw_rotated_rect(draw, projection, feature, (74, 145, 169, 220), (30, 91, 116, 255))
        elif feature.kind == "shrine":
            draw_rotated_rect(draw, projection, feature, colors["shrine"][0], colors["shrine"][1])
        elif feature.kind == "season":
            draw_rotated_rect(draw, projection, feature, colors["season"][0], colors["season"][1])

    for col in range(1, cols):
        x_world = projection.x_min + (projection.x_max - projection.x_min) * col / cols
        x, _ = projection.to_px(x_world, projection.z_min)
        draw.line((x + 2, projection.top, x + 2, projection.bottom), fill=(0, 0, 0, 98), width=5)
        draw.line((x, projection.top, x, projection.bottom), fill=(255, 255, 255, 220), width=3)

    for row in range(1, rows):
        z_world = projection.z_min + (projection.z_max - projection.z_min) * row / rows
        _, y = projection.to_px(projection.x_min, z_world)
        draw.line((projection.left, y + 2, projection.right, y + 2), fill=(0, 0, 0, 98), width=5)
        draw.line((projection.left, y, projection.right, y), fill=(255, 255, 255, 220), width=3)

    for row in range(rows):
        for col in range(cols):
            label = label_for(col, row)
            x0 = projection.x_min + (projection.x_max - projection.x_min) * col / cols
            x1 = projection.x_min + (projection.x_max - projection.x_min) * (col + 1) / cols
            z0 = projection.z_min + (projection.z_max - projection.z_min) * row / rows
            z1 = projection.z_min + (projection.z_max - projection.z_min) * (row + 1) / rows
            px, py = projection.to_px((x0 + x1) * 0.5, (z0 + z1) * 0.5)
            draw_label(
                draw,
                (px - 26, py - 22),
                label,
                small_font,
                fill=(18, 24, 30, 200),
                outline=(255, 210, 130, 240),
                radius=9,
            )

    for feature in all_features():
        px, py = projection.to_px(feature.x, feature.z)
        label = feature.label
        if feature.kind == "house":
            label = label.replace("H0", "H")
        bbox = text_bbox(draw, label, tiny_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.rounded_rectangle((px - tw * 0.5 - 5, py - th * 0.5 - 3, px + tw * 0.5 + 5, py + th * 0.5 + 4), radius=5, fill=(255, 255, 255, 215))
        draw.text((px - tw * 0.5, py - th * 0.5 - 1), label, font=tiny_font, fill=(25, 30, 28, 255))

    if include_title:
        draw_label(draw, (28, 24), "Scene map sectors - denah top-down", title_font)

    draw.text((projection.left, projection.top - 34), "Z- / Fuji side", font=label_font, fill=(50, 61, 54, 255))
    draw.text((projection.right - 118, projection.bottom + 38), "Z+", font=label_font, fill=(50, 61, 54, 255))
    draw.text((projection.left - 54, projection.bottom + 10), "X-", font=label_font, fill=(50, 61, 54, 255))
    draw.text((projection.right + 12, projection.bottom + 10), "X+", font=label_font, fill=(50, 61, 54, 255))

    legend_lines = [
        "Legend",
        "Blue: pond/stream",
        "Pink: trees/sakura",
        "Brown: houses/buildings",
        "Red: bridge/shrine",
        "Orange: seasonal props",
    ]
    legend_x, legend_y = projection.left + 18, projection.bottom - 156
    draw.rounded_rectangle((legend_x, legend_y, legend_x + 230, legend_y + 126), radius=12, fill=(255, 255, 255, 212), outline=(80, 90, 72, 180), width=2)
    for i, text in enumerate(legend_lines):
        font = small_font if i == 0 else tiny_font
        draw.text((legend_x + 14, legend_y + 12 + i * 19), text, font=font, fill=(38, 48, 38, 255))


def sector_bounds(projection: MapProjection, cols: int, rows: int, col: int, row: int) -> tuple[float, float, float, float]:
    x_step = (projection.x_max - projection.x_min) / cols
    z_step = (projection.z_max - projection.z_min) / rows
    x0 = projection.x_min + col * x_step
    x1 = projection.x_min + (col + 1) * x_step
    z0 = projection.z_min + row * z_step
    z1 = projection.z_min + (row + 1) * z_step
    return x0, z0, x1, z1


def features_in_bounds(features: list[Feature], bounds: tuple[float, float, float, float], is_last_col: bool = False, is_last_row: bool = False) -> list[Feature]:
    x0, z0, x1, z1 = bounds
    selected = []
    for feature in features:
        in_x = x0 <= feature.x < x1 or (is_last_col and math.isclose(feature.x, x1))
        in_z = z0 <= feature.z < z1 or (is_last_row and math.isclose(feature.z, z1))
        if in_x and in_z:
            selected.append(feature)
    return selected


def generate_map(output_dir: Path, prefix: str, cols: int, rows: int, size: int, padding: int, bounds: tuple[float, float, float, float]) -> tuple[Path, list[Path], Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    projection = MapProjection(bounds, size, padding)
    overview = output_dir / f"{prefix}_grid.png"

    canvas = Image.new("RGBA", (size, size), (242, 238, 222, 255))
    draw = ImageDraw.Draw(canvas)
    draw_base_map(draw, projection, cols, rows)
    canvas.convert("RGB").save(overview, quality=94, optimize=True)

    sectors = []
    sector_font = load_font(max(20, size // 54), bold=True)
    detail_font = load_font(max(14, size // 92))
    crop_padding = max(20, round(projection.scale * 1.05))

    for row in range(rows):
        for col in range(cols):
            label = label_for(col, row)
            x0, z0, x1, z1 = sector_bounds(projection, cols, rows, col, row)
            left, top = projection.to_px(x0, z0)
            right, bottom = projection.to_px(x1, z1)
            crop_box = (
                max(0, round(left - crop_padding)),
                max(0, round(top - crop_padding)),
                min(size, round(right + crop_padding)),
                min(size, round(bottom + crop_padding)),
            )
            crop = canvas.crop(crop_box).convert("RGBA")
            crop_draw = ImageDraw.Draw(crop)
            subtitle = f"{label} | X {x0:.1f}..{x1:.1f} | Z {z0:.1f}..{z1:.1f}"
            draw_label(crop_draw, (18, 16), subtitle, sector_font)
            crop_draw.text((22, 70), "Top-down denah crop", font=detail_font, fill=(42, 52, 42, 255))
            sector_path = output_dir / f"{prefix}_{label}.png"
            crop.convert("RGB").save(sector_path, quality=94, optimize=True)
            sectors.append(sector_path)

    gallery = write_gallery(output_dir, overview, sectors, projection, cols, rows, prefix)
    return overview, sectors, gallery


def draw_plan_card(
    draw: ImageDraw.ImageDraw,
    box: tuple[float, float, float, float],
    sector: str,
    title: str,
    items: list[str],
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
    colors: tuple[tuple[int, int, int, int], tuple[int, int, int, int]],
) -> None:
    left, top, right, bottom = box
    fill, outline = colors
    draw.rounded_rectangle((left, top, right, bottom), radius=14, fill=fill, outline=outline, width=2)
    draw.rounded_rectangle((left + 10, top + 10, left + 54, top + 42), radius=8, fill=(18, 24, 30, 230), outline=(255, 210, 130, 245), width=2)
    draw.text((left + 20, top + 15), sector, font=title_font, fill=(255, 255, 255, 255))
    draw.text((left + 66, top + 14), title, font=title_font, fill=(24, 35, 28, 255))

    y = top + 54
    max_width = right - left - 34
    for item in items:
        for index, line in enumerate(wrap_text(draw, item, body_font, max_width - 12)):
            prefix = "- " if index == 0 else "  "
            draw.text((left + 18, y), prefix + line, font=body_font, fill=(38, 48, 39, 255))
            y += 23


def generate_content_plan(output_dir: Path, prefix: str, projection: MapProjection, cols: int, rows: int) -> tuple[Path, Path]:
    plan_image = output_dir / f"{prefix}_content_plan.png"
    plan_doc = output_dir / f"{prefix}_content_plan.md"
    canvas = Image.new("RGBA", (projection.size, projection.size), (242, 238, 222, 255))
    draw = ImageDraw.Draw(canvas)
    draw_base_map(draw, projection, cols, rows, include_title=False)

    veil = Image.new("RGBA", (projection.size, projection.size), (246, 243, 232, 122))
    canvas = Image.alpha_composite(canvas, veil)
    draw = ImageDraw.Draw(canvas)

    title_font = load_font(34, bold=True)
    subtitle_font = load_font(18)
    card_title_font = load_font(18, bold=True)
    body_font = load_font(15)
    draw_label(draw, (28, 24), "Sector content plan - apa yang diisi tiap kotak", title_font)
    draw.text(
        (38, 86),
        "Gunakan gambar ini sebagai sketsa isi map: sektor tengah tetap hero, pojok dibuat ringan supaya komposisi tidak penuh.",
        font=subtitle_font,
        fill=(48, 58, 48, 255),
    )

    palette = [
        ((255, 251, 235, 232), (143, 105, 54, 230)),
        ((232, 246, 236, 232), (71, 122, 78, 230)),
        ((231, 244, 250, 232), (48, 111, 136, 230)),
        ((251, 234, 238, 232), (152, 71, 92, 230)),
    ]

    x_step = (projection.x_max - projection.x_min) / cols
    z_step = (projection.z_max - projection.z_min) / rows
    for row in range(rows):
        for col in range(cols):
            sector = label_for(col, row)
            title, items = CONTENT_PLAN.get(sector, ("Fill detail", ["Small props", "Keep composition balanced"]))
            x0 = projection.x_min + col * x_step
            x1 = projection.x_min + (col + 1) * x_step
            z0 = projection.z_min + row * z_step
            z1 = projection.z_min + (row + 1) * z_step
            left, top = projection.to_px(x0, z0)
            right, bottom = projection.to_px(x1, z1)
            margin = 13
            box = (left + margin, top + margin, right - margin, bottom - margin)
            colors = palette[(row + col) % len(palette)]
            draw_plan_card(draw, box, sector, title, items, card_title_font, body_font, colors)

    canvas.convert("RGB").save(plan_image, quality=94, optimize=True)

    lines = [
        "# Sector Content Plan",
        "",
        "Ini sketsa isi map per sektor. Pakai bersama denah top-down supaya gampang memilih area yang mau diedit.",
        "",
        f"![sector content plan]({plan_image.name})",
        "",
        "| Sector | Theme | Suggested content |",
        "| --- | --- | --- |",
    ]
    for row in range(rows):
        for col in range(cols):
            sector = label_for(col, row)
            title, items = CONTENT_PLAN.get(sector, ("Fill detail", ["Small props", "Keep composition balanced"]))
            lines.append(f"| {sector} | {title} | {'; '.join(items)} |")
    plan_doc.write_text("\n".join(lines), encoding="utf-8")
    return plan_image, plan_doc


def write_gallery(
    output_dir: Path,
    overview: Path,
    sectors: list[Path],
    projection: MapProjection,
    cols: int,
    rows: int,
    prefix: str,
) -> Path:
    features = all_features()
    gallery = output_dir / f"{prefix}_sector_gallery.md"
    lines = [
        "# Map Sector Preview Gallery",
        "",
        "Preview ini berbentuk denah top-down, bukan potongan kamera 3D.",
        "",
        f"Bounds: `X {projection.x_min:.1f}..{projection.x_max:.1f}`, `Z {projection.z_min:.1f}..{projection.z_max:.1f}`",
        f"Grid: `{cols} x {rows}`",
        "",
        "## Overview",
        "",
        f"![map sector overview]({overview.name})",
        "",
        "## Content Plan",
        "",
        f"![sector content plan]({prefix}_content_plan.png)",
        "",
        f"Detail: [{prefix}_content_plan.md]({prefix}_content_plan.md)",
        "",
        "## Sector Index",
        "",
        "| Sector | X range | Z range | Main labels |",
        "| --- | --- | --- | --- |",
    ]

    sector_feature_names: dict[str, str] = {}
    for row in range(rows):
        for col in range(cols):
            label = label_for(col, row)
            bounds = sector_bounds(projection, cols, rows, col, row)
            selected = features_in_bounds(features, bounds, col == cols - 1, row == rows - 1)
            names = ", ".join(feature.label for feature in selected[:8])
            if len(selected) > 8:
                names += ", ..."
            sector_feature_names[label] = names or "-"
            x0, z0, x1, z1 = bounds
            lines.append(f"| {label} | `{x0:.1f}..{x1:.1f}` | `{z0:.1f}..{z1:.1f}` | {sector_feature_names[label]} |")

    lines.extend(["", "## Sectors", ""])
    for sector in sectors:
        label = sector.stem.removeprefix(prefix + "_")
        lines.extend(
            [
                f"### {label}",
                "",
                f"Main labels: {sector_feature_names.get(label, '-')}",
                "",
                f"![{sector.stem}]({sector.name})",
                "",
            ]
        )

    gallery.write_text("\n".join(lines), encoding="utf-8")
    return gallery


def parse_bounds(value: str) -> tuple[float, float, float, float]:
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("Bounds must be x_min,z_min,x_max,z_max")
    x_min, z_min, x_max, z_max = parts
    if x_min >= x_max or z_min >= z_max:
        raise argparse.ArgumentTypeError("Bounds minimums must be lower than maximums")
    return x_min, z_min, x_max, z_max


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate top-down map/denah previews split into editable sectors.")
    parser.add_argument("--source", type=Path, default=None, help="Deprecated; kept so the old screenshot command still runs. Ignored.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT, help="Output directory for map sector previews.")
    parser.add_argument("--cols", type=int, default=4, help="Number of vertical map sectors.")
    parser.add_argument("--rows", type=int, default=4, help="Number of horizontal map sectors.")
    parser.add_argument("--prefix", default="scene_map", help="Output file prefix.")
    parser.add_argument("--size", type=int, default=1600, help="Square output size in pixels.")
    parser.add_argument("--padding", type=int, default=116, help="Outer padding around the world map.")
    parser.add_argument("--bounds", type=parse_bounds, default=DEFAULT_BOUNDS, help="World bounds as x_min,z_min,x_max,z_max.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.out if args.out.is_absolute() else ROOT / args.out
    cols = max(1, args.cols)
    rows = max(1, args.rows)
    size = max(900, args.size)
    padding = max(60, args.padding)

    overview, sectors, gallery = generate_map(output_dir, args.prefix, cols, rows, size, padding, args.bounds)
    plan_image, plan_doc = generate_content_plan(output_dir, args.prefix, MapProjection(args.bounds, size, padding), cols, rows)

    print(f"Generated {rel(overview)}")
    print(f"Generated {rel(plan_image)}")
    print(f"Generated {rel(plan_doc)}")
    for sector in sectors:
        print(f"Generated {rel(sector)}")
    print(f"Generated {rel(gallery)}")


if __name__ == "__main__":
    main()
