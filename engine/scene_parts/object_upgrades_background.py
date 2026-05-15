import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneBackgroundUpgradeMixin:
    def add_background_object(self, obj):
        obj.is_background = True
        self.add_object(obj)

    def add_distant_background_layers(self, app):
        hill_colors = [
            self.season_color("fuji_peak_color", (0.38, 0.46, 0.54)),
            self.season_color("garden_hedge_color", (0.18, 0.34, 0.18)),
            self.season_color("night_fog_color", (0.09, 0.12, 0.18)),
        ]
        layer_specs = [
            ((4.5, 1.0, -51.5), (13.0, 1.15, 0.030), hill_colors[0]),
            ((-10.5, 0.72, -49.0), (11.0, 0.92, 0.030), hill_colors[1]),
            ((11.8, 0.58, -47.4), (9.0, 0.62, 0.030), hill_colors[2]),
        ]
        for pos, scale, color in layer_specs:
            self.add_background_object(ColorCube(app, pos=pos, scale=scale, color=color))

        fog_color = self.season_color("winter_snow_shadow_color", (0.80, 0.88, 0.94))
        for i in range(6):
            x = -18.0 + i * 7.2
            y = 0.22 + 0.06 * math.sin(i)
            self.add_background_object(
                SunDisc(
                    app,
                    pos=(x, y, -46.0 - i * 0.30),
                    rot=(90, 0, 0),
                    scale=(2.4 + 0.4 * (i % 2), 0.34, 1.0),
                    color=fog_color,
                    alpha=0.10,
                )
            )

    def add_foreground_plants(self, app):
        add = self.add_object
        colors = [
            self.season_color("garden_lawn_color", (0.34, 0.49, 0.24)),
            self.season_color("garden_rich_lawn_color", (0.25, 0.42, 0.20)),
            self.season_color("garden_hedge_color", (0.24, 0.42, 0.18)),
        ]
        framing_clusters = [
            (-10.8, 17.8),
            (-8.4, 18.2),
            (-6.1, 17.5),
            (6.1, 17.4),
            (8.7, 18.0),
            (11.0, 17.6),
        ]
        for cluster, (base_x, base_z) in enumerate(framing_clusters):
            for blade in range(5):
                angle = -28.0 + blade * 9.0 + cluster * 3.0
                height = 0.14 + 0.045 * ((cluster + blade) % 3)
                add(
                    ColorCube(
                        app,
                        pos=(
                            base_x + 0.20 * math.cos(blade),
                            0.05 + height,
                            base_z + 0.12 * math.sin(blade * 1.7),
                        ),
                        rot=(12.0 * math.sin(blade), angle, 10.0 * math.cos(cluster)),
                        scale=(0.018, height, 0.010),
                        color=colors[(cluster + blade) % len(colors)],
                    )
                )
            if cluster % 2 == 0:
                add(
                    PondRock(
                        app,
                        pos=(base_x + 0.32, 0.085, base_z - 0.08),
                        rot=(0, cluster * 23.0, 0),
                        scale=(0.26, 0.10, 0.20),
                        color=(0.38, 0.38, 0.34),
                    )
                )
