from pathlib import Path
import math
import random

import pygame as pg


ROOT_DIR = Path(__file__).resolve().parents[1]
TEXTURE_DIR = ROOT_DIR / "assets" / "textures"
SIZE = 256


def clamp(value):
    return max(0, min(255, int(value)))


def rgb(color):
    return tuple(clamp(channel) for channel in color)


def mix(a, b, t):
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(3))


def surface(base_a, base_b, seed):
    rng = random.Random(seed)
    target = pg.Surface((SIZE, SIZE), flags=pg.SRCALPHA)

    for y in range(SIZE):
        for x in range(SIZE):
            wave = (
                math.sin((x / SIZE) * math.tau * 3.0 + seed)
                + math.cos((y / SIZE) * math.tau * 4.0 + seed * 0.7)
            ) * 0.5
            grain = rng.random() - 0.5
            t = max(0.0, min(1.0, 0.50 + wave * 0.16 + grain * 0.16))
            target.set_at((x, y), (*rgb(mix(base_a, base_b, t)), 255))

    return target, rng


def draw_grass(name, base_a, base_b, blade_colors, flower_colors=(), seed=1):
    target, rng = surface(base_a, base_b, seed)

    for _ in range(520):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        length = rng.randint(7, 20)
        lean = rng.randint(-5, 6)
        color = rng.choice(blade_colors)
        pg.draw.line(target, rgb(color), (x, y), ((x + lean) % SIZE, (y - length) % SIZE), 1)

    for _ in range(160):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        color = rng.choice(blade_colors)
        pg.draw.circle(target, rgb(color), (x, y), rng.randint(1, 2))

    for _ in range(len(flower_colors) * 55):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        color = rng.choice(flower_colors)
        pg.draw.circle(target, rgb(color), (x, y), rng.choice((1, 1, 2)))

    save(target, name)


def draw_scattered_leaves(name, base_a, base_b, leaf_colors, seed=1, count=430):
    target, rng = surface(base_a, base_b, seed)

    for _ in range(count):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        w = rng.randint(5, 14)
        h = rng.randint(2, 6)
        color = rgb(rng.choice(leaf_colors))
        rect = pg.Rect(x - w // 2, y - h // 2, w, h)
        pg.draw.ellipse(target, color, rect)
        if rng.random() < 0.35:
            pg.draw.line(target, rgb((color[0] * 0.7, color[1] * 0.7, color[2] * 0.7)), (x - w // 3, y), (x + w // 3, y), 1)

    save(target, name)


def draw_road(name, base_a, base_b, accent_colors, seed=1, cracks=True, leaves=False, ice=False):
    target, rng = surface(base_a, base_b, seed)

    for _ in range(190):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        color = rng.choice(accent_colors)
        pg.draw.circle(target, rgb(color), (x, y), rng.randint(1, 3))

    if cracks:
        for _ in range(24):
            x = rng.randrange(SIZE)
            y = rng.randrange(SIZE)
            points = [(x, y)]
            for _ in range(rng.randint(3, 6)):
                x = (x + rng.randint(-18, 19)) % SIZE
                y = (y + rng.randint(8, 24)) % SIZE
                points.append((x, y))
            pg.draw.lines(target, rgb((48, 44, 40)), False, points, 1)

    if leaves:
        leaf_colors = [(170, 70, 18), (218, 128, 28), (128, 54, 18), (202, 160, 44)]
        for _ in range(135):
            x = rng.randrange(SIZE)
            y = rng.randrange(SIZE)
            pg.draw.ellipse(target, rgb(rng.choice(leaf_colors)), pg.Rect(x, y, rng.randint(5, 12), rng.randint(2, 5)))

    if ice:
        for _ in range(46):
            x = rng.randrange(SIZE)
            y = rng.randrange(SIZE)
            length = rng.randint(18, 62)
            pg.draw.line(target, rgb((218, 242, 255)), (x, y), ((x + length) % SIZE, (y + rng.randint(-7, 8)) % SIZE), 1)
        for _ in range(22):
            x = rng.randrange(SIZE)
            y = rng.randrange(SIZE)
            pg.draw.line(target, rgb((118, 164, 188)), (x, y), ((x + rng.randint(-28, 29)) % SIZE, (y + rng.randint(10, 38)) % SIZE), 1)

    save(target, name)


def draw_mossy_stone():
    target, rng = surface((98, 100, 92), (150, 148, 132), 80)

    for _ in range(65):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        w = rng.randint(30, 70)
        h = rng.randint(18, 48)
        color = rgb(rng.choice([(122, 124, 114), (80, 84, 78), (164, 160, 145)]))
        pg.draw.ellipse(target, color, pg.Rect(x - w // 2, y - h // 2, w, h), 2)

    for _ in range(110):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        pg.draw.circle(target, rgb(rng.choice([(45, 92, 44), (62, 118, 54), (34, 72, 36)])), (x, y), rng.randint(2, 7))

    save(target, "mossy_stone.png")


def draw_bark():
    target, rng = surface((74, 40, 22), (130, 72, 36), 90)

    for x in range(0, SIZE, 8):
        offset = rng.randint(-4, 4)
        color = rgb(rng.choice([(58, 30, 16), (104, 58, 30), (160, 94, 48)]))
        points = []
        for y in range(0, SIZE + 24, 24):
            points.append(((x + offset + rng.randint(-5, 5)) % SIZE, y % SIZE))
        pg.draw.lines(target, color, False, points, 2)

    for _ in range(120):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        pg.draw.line(target, rgb((42, 24, 16)), (x, y), ((x + rng.randint(-4, 5)) % SIZE, (y + rng.randint(8, 22)) % SIZE), 1)

    save(target, "bark_dark.png")


def draw_cloud(name, seed, streak=False):
    rng = random.Random(seed)
    target = pg.Surface((SIZE, SIZE), flags=pg.SRCALPHA)
    target.fill((255, 255, 255, 0))

    count = 52 if streak else 38
    for _ in range(count):
        cx = rng.randint(-16, SIZE + 16)
        cy = rng.randint(44, 204)
        rx = rng.randint(22, 58) if streak else rng.randint(18, 44)
        ry = rng.randint(7, 22) if streak else rng.randint(12, 34)
        alpha = rng.randint(22, 72) if streak else rng.randint(35, 108)
        color = (255, 255, 255, alpha)
        pg.draw.ellipse(target, color, pg.Rect(cx - rx, cy - ry, rx * 2, ry * 2))

    for _ in range(22):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        pg.draw.circle(target, (230, 236, 246, rng.randint(8, 28)), (x, y), rng.randint(10, 28))

    target = pg.transform.smoothscale(pg.transform.smoothscale(target, (128, 128)), (SIZE, SIZE))
    save(target, name)


def draw_moon():
    target = pg.Surface((SIZE, SIZE), flags=pg.SRCALPHA)
    target.fill((255, 255, 255, 0))
    center = SIZE // 2
    radius = 84

    for r in range(radius, 0, -1):
        t = r / radius
        alpha = int(245 * (1.0 - t * t * 0.20))
        color = (222, 230, 246, alpha)
        pg.draw.circle(target, color, (center, center), r)

    craters = [
        (96, 86, 16, 44),
        (142, 116, 24, 34),
        (120, 154, 18, 28),
        (168, 156, 12, 24),
        (82, 142, 10, 22),
    ]
    for x, y, r, alpha in craters:
        pg.draw.circle(target, (150, 160, 182, alpha), (x, y), r)
        pg.draw.circle(target, (246, 248, 255, alpha // 2), (x - r // 3, y - r // 3), max(2, r // 4))

    for r in range(radius + 8, radius + 30):
        alpha = max(0, int(72 * (1.0 - (r - radius) / 30.0)))
        pg.draw.circle(target, (190, 212, 255, alpha), (center, center), r, 2)

    save(target, "moon_disc.png")


def draw_aurora():
    target = pg.Surface((SIZE, SIZE), flags=pg.SRCALPHA)
    target.fill((255, 255, 255, 0))

    for band in range(5):
        points = []
        base_y = 74 + band * 22
        for x in range(-20, SIZE + 28, 8):
            wave = math.sin(x * 0.045 + band * 1.3) * (18 + band * 3)
            points.append((x, base_y + wave))
        color = [(98, 255, 190, 44), (96, 220, 255, 34), (180, 126, 255, 26)][band % 3]
        pg.draw.lines(target, color, False, points, 8 + band * 2)

    target = pg.transform.smoothscale(pg.transform.smoothscale(target, (128, 128)), (SIZE, SIZE))
    save(target, "aurora_band.png")


def save(target, filename):
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    pg.image.save(target, str(TEXTURE_DIR / filename))


def main():
    pg.init()
    draw_grass(
        "spring_grass.png",
        (64, 118, 45),
        (130, 176, 62),
        [(38, 100, 36), (76, 144, 48), (118, 178, 58)],
        [(255, 164, 214), (255, 222, 238), (244, 222, 92)],
        seed=12,
    )
    draw_grass(
        "summer_grass.png",
        (52, 104, 34),
        (112, 148, 38),
        [(34, 82, 28), (74, 124, 34), (142, 154, 44)],
        [(250, 210, 42), (255, 132, 34)],
        seed=22,
    )
    draw_grass(
        "dry_grass.png",
        (116, 106, 48),
        (184, 154, 64),
        [(92, 86, 36), (152, 132, 54), (210, 178, 78)],
        [],
        seed=32,
    )
    draw_grass(
        "autumn_grass.png",
        (94, 92, 38),
        (160, 116, 42),
        [(74, 82, 32), (132, 102, 36), (178, 108, 32)],
        [],
        seed=42,
    )
    draw_grass(
        "flower_meadow.png",
        (58, 122, 46),
        (120, 178, 70),
        [(38, 108, 38), (80, 150, 54), (112, 170, 66)],
        [(255, 126, 190), (255, 236, 132), (186, 122, 255), (255, 255, 238)],
        seed=52,
    )
    draw_scattered_leaves(
        "leaf_litter.png",
        (92, 70, 38),
        (146, 104, 38),
        [(174, 70, 20), (228, 126, 28), (126, 48, 18), (210, 168, 42), (96, 60, 22)],
        seed=62,
        count=560,
    )
    draw_scattered_leaves(
        "petal_ground.png",
        (78, 118, 58),
        (126, 166, 76),
        [(255, 126, 184), (255, 174, 216), (255, 220, 238), (238, 86, 152)],
        seed=72,
        count=310,
    )
    draw_road("sunbaked_road.png", (94, 84, 68), (142, 122, 88), [(72, 64, 54), (174, 150, 100), (110, 98, 78)], seed=82)
    draw_road("leafy_road.png", (74, 66, 54), (112, 84, 56), [(62, 54, 46), (146, 108, 66), (96, 78, 58)], seed=92, leaves=True)
    draw_road("icy_road.png", (164, 184, 190), (216, 238, 246), [(132, 164, 178), (238, 250, 255), (188, 210, 218)], seed=102, cracks=False, ice=True)
    draw_mossy_stone()
    draw_bark()
    draw_cloud("cloud_soft.png", seed=112)
    draw_cloud("cloud_streak.png", seed=122, streak=True)
    draw_moon()
    draw_aurora()
    pg.quit()


if __name__ == "__main__":
    main()
