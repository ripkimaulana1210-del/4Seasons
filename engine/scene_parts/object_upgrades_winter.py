import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneWinterObjectUpgradeMixin:
    def add_winter_snow_lantern(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        x, z = (7.45, -6.00)
        add(ColorCube(app, pos=(x, 0.12, z), scale=(0.16, 0.08, 0.16), color=stone))
        add(ColorCube(app, pos=(x, 0.40, z), scale=(0.038, 0.26, 0.038), color=stone))
        add(ColorCube(app, pos=(x, 0.68, z), scale=(0.18, 0.055, 0.18), color=stone))
        add(ColorCube(app, pos=(x, 0.82, z), scale=(0.13, 0.095, 0.13), color=(0.95, 0.90, 0.72)))
        add(ColorCube(app, pos=(x, 0.95, z), scale=(0.24, 0.055, 0.24), color=snow))
        add(NightGlow(app, pos=(x, 0.82, z), scale=(0.32, 0.32, 1.0), color=(1.00, 0.66, 0.34), alpha=0.36, pulse=0.025))

    def add_winter_torii_and_bridge_snow(self, app):
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        ice_shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        torii_x, torii_z, torii_yaw = (8.9, -6.9, -30.0)
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.84, 0.0, (1.22, 0.035, 0.13), snow)
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.54, 0.0, (0.94, 0.030, 0.10), snow)
        for i, local_x in enumerate((-0.52, -0.30, -0.08, 0.14, 0.38, 0.58)):
            self.add_local_cube(app, torii_x, torii_z, torii_yaw, local_x, 1.38 - 0.02 * (i % 3), 0.055, (0.016, 0.10 + 0.02 * (i % 2), 0.012), ice_shadow)

        pond_radius_scale = SCENE_LAYOUT["pond"]["radius_scale"]
        island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]
        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)

        def bridge_point(t):
            inv_t = 1.0 - t
            x = inv_t * inv_t * start[0] + 2.0 * inv_t * t * control[0] + t * t * end[0]
            z = inv_t * inv_t * start[1] + 2.0 * inv_t * t * control[1] + t * t * end[1]
            y = 0.16 + math.sin(math.pi * t) * 0.88
            return (x, y, z)

        for i, t in enumerate((0.12, 0.25, 0.38, 0.52, 0.66, 0.80)):
            point = bridge_point(t)
            next_point = bridge_point(min(1.0, t + 0.03))
            dx = next_point[0] - point[0]
            dz = next_point[2] - point[2]
            yaw = math.degrees(math.atan2(dx, dz))
            self.add_object(ColorCube(app, pos=(point[0], point[1] + 0.15, point[2]), rot=(0, yaw, 0), scale=(0.48, 0.018, 0.12), color=snow))
            if i % 2 == 0:
                self.add_object(ColorCube(app, pos=(point[0] + 0.28, point[1] - 0.18, point[2]), rot=(0, yaw, 0), scale=(0.014, 0.12, 0.014), color=ice_shadow))

    def add_winter_frozen_koi(self, app):
        add = self.add_object
        koi_colors = [(0.86, 0.34, 0.12), (0.96, 0.82, 0.34), (0.90, 0.88, 0.78)]
        for i in range(8):
            angle = i * 0.78 + 0.25
            radius = 1.62 + 0.28 * (i % 3)
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            yaw = math.degrees(angle) + 90.0
            add(ColorCube(app, pos=(x, 0.071, z), rot=(0, yaw, 0), scale=(0.115, 0.006, 0.028), color=koi_colors[i % len(koi_colors)]))
            add(ColorCube(app, pos=(x - math.sin(angle) * 0.09, 0.072, z + math.cos(angle) * 0.09), rot=(0, yaw + 28, 0), scale=(0.035, 0.005, 0.020), color=(0.48, 0.58, 0.62)))

    def add_winter_footprints_and_drifts(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        for i in range(18):
            t = i / 17.0
            x = -5.0 + t * 4.2
            z = -7.35 + 0.18 * math.sin(i * 0.8)
            side = -1 if i % 2 else 1
            add(ColorPlane(app, pos=(x + side * 0.08, 0.043, z), rot=(0, 14 + i * 3.0, 0), scale=(0.050, 1, 0.090), color=shadow))
        for i, (x, z) in enumerate(((-8.8, -7.2), (-7.6, 4.8), (-2.8, 8.3), (4.8, 8.0), (8.8, 3.2), (7.0, -7.0))):
            add(PondRock(app, pos=(x, 0.080, z), rot=(0, i * 23.0, 0), scale=(0.42 + 0.04 * (i % 2), 0.075, 0.22), color=snow if i % 2 else shadow))

    def add_winter_onsen_corner(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        water = (0.54, 0.78, 0.86)
        center_x, center_z = (-11.1, -7.1)
        add(SunDisc(app, pos=(center_x, 0.062, center_z), rot=(90, -18, 0), scale=(0.62, 0.28, 1.0), color=water, alpha=0.30))
        for i in range(14):
            angle = i * math.tau / 14.0
            add(
                PondRock(
                    app,
                    pos=(center_x + math.cos(angle) * 0.72, 0.105, center_z + math.sin(angle) * 0.42),
                    rot=(0, i * 21.0, 0),
                    scale=(0.16 + 0.02 * (i % 3), 0.070, 0.12),
                    color=stone if i % 2 else snow,
                )
            )
        for i in range(12):
            angle = -0.70 + i * 0.12
            add(
                WindStreak(
                    app,
                    pos=(center_x + math.cos(angle) * 0.28, 0.34 + 0.05 * (i % 4), center_z + math.sin(angle) * 0.18),
                    rot=(0, -34 + i * 7.0, 0),
                    scale=(0.055, 0.010, 0.070),
                    color=(0.90, 0.96, 0.98),
                    travel=(0.10, 0.18, -0.04),
                    speed=0.055 + i * 0.004,
                    phase=i * 0.09,
                    bob=0.10,
                )
            )
        add(NightGlow(app, pos=(center_x, 0.18, center_z), scale=(0.70, 0.38, 1.0), color=(0.74, 0.92, 1.00), alpha=0.18, pulse=0.020))

    def add_winter_frozen_waterfall_detail(self, app):
        add = self.add_object
        ice = (0.74, 0.90, 0.98)
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        ledge_x, ledge_z, yaw = (-11.5, -6.8, -38.0)
        add(SunDisc(app, pos=(ledge_x - 0.24, 0.070, ledge_z - 0.40), rot=(90, yaw, 0), scale=(0.52, 0.20, 1.0), color=ice, alpha=0.24))
        for i, offset in enumerate((-0.30, -0.16, -0.02, 0.14, 0.30)):
            add(
                ColorCube(
                    app,
                    pos=(ledge_x + offset, 0.34 + 0.03 * (i % 2), ledge_z - 0.08 + 0.05 * i),
                    rot=(8, yaw, 0),
                    scale=(0.026, 0.22 + 0.04 * (i % 3), 0.044),
                    color=ice if i % 2 else shadow,
                )
            )
            add(
                ColorCube(
                    app,
                    pos=(ledge_x + offset * 0.92, 0.18, ledge_z + 0.02 + 0.04 * i),
                    rot=(0, yaw + i * 6.0, 0),
                    scale=(0.018, 0.13 + 0.02 * (i % 2), 0.018),
                    color=ice,
                )
            )
        for i in range(9):
            add(
                PondRock(
                    app,
                    pos=(ledge_x - 0.54 + i * 0.12, 0.082, ledge_z + 0.28 + 0.05 * math.sin(i)),
                    rot=(0, yaw + i * 15.0, 0),
                    scale=(0.11, 0.040, 0.075),
                    color=ice if i % 2 else shadow,
                )
            )
