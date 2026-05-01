import moderngl as mgl
import pygame as pg

from .paths import TEXTURE_DIR


class TextureManager:
    def __init__(self, ctx):
        self.ctx = ctx
        self.textures = {}
        self.load_defaults()

    def load_defaults(self):
        defaults = {
            "grass": ("grass.png", (0.30, 0.48, 0.20)),
            "spring_grass": ("spring_grass.png", (0.36, 0.62, 0.24)),
            "summer_grass": ("summer_grass.png", (0.32, 0.52, 0.18)),
            "dry_grass": ("dry_grass.png", (0.58, 0.50, 0.22)),
            "autumn_grass": ("autumn_grass.png", (0.52, 0.42, 0.16)),
            "flower_meadow": ("flower_meadow.png", (0.42, 0.66, 0.28)),
            "leaf_litter": ("leaf_litter.png", (0.48, 0.32, 0.14)),
            "petal_ground": ("petal_ground.png", (0.44, 0.60, 0.28)),
            "road": ("road.png", (0.38, 0.35, 0.30)),
            "sunbaked_road": ("sunbaked_road.png", (0.54, 0.47, 0.35)),
            "leafy_road": ("leafy_road.png", (0.43, 0.32, 0.22)),
            "icy_road": ("icy_road.png", (0.72, 0.82, 0.86)),
            "snow": ("snow.png", (0.92, 0.95, 0.98)),
            "wall": ("wall.png", (0.72, 0.62, 0.46)),
            "wood": ("wood.png", (0.42, 0.24, 0.12)),
            "bark_dark": ("bark_dark.png", (0.40, 0.22, 0.12)),
            "roof": ("roof.png", (0.46, 0.14, 0.10)),
            "stone": ("stone.png", (0.50, 0.49, 0.45)),
            "mossy_stone": ("mossy_stone.png", (0.45, 0.50, 0.38)),
            "cloud_soft": ("cloud_soft.png", (1.00, 1.00, 1.00)),
            "cloud_streak": ("cloud_streak.png", (1.00, 1.00, 1.00)),
            "moon_disc": ("moon_disc.png", (0.86, 0.90, 1.00)),
            "aurora_band": ("aurora_band.png", (0.48, 1.00, 0.78)),
            "white": ("white.png", (1.00, 1.00, 1.00)),
        }

        for name, (filename, fallback_color) in defaults.items():
            self.textures[name] = self.load_texture(
                TEXTURE_DIR / filename,
                fallback_color=fallback_color,
            )

    def make_fallback_surface(self, color, size=(32, 32)):
        surface = pg.Surface(size, flags=pg.SRCALPHA)
        rgba = tuple(int(max(0.0, min(1.0, channel)) * 255) for channel in color)
        surface.fill((*rgba, 255))
        return surface

    def load_texture(self, path, fallback_color=(1.0, 1.0, 1.0)):
        if path.exists():
            surface = pg.image.load(str(path)).convert_alpha()
        else:
            surface = self.make_fallback_surface(fallback_color)

        surface = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(surface, "RGBA")
        texture = self.ctx.texture(surface.get_size(), 4, data)
        texture.repeat_x = True
        texture.repeat_y = True
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        return texture

    def get(self, name):
        return self.textures.get(name, self.textures["white"])

    def destroy(self):
        for texture in self.textures.values():
            texture.release()
