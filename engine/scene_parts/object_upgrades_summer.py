import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneSummerObjectUpgradeMixin:
    def add_summer_yatai(self, app):
        base_x, base_z, yaw = (9.8, 10.2, -24.0)
        wood = (0.38, 0.22, 0.10)
        dark = (0.18, 0.10, 0.05)
        red = (0.82, 0.12, 0.08)
        gold = (1.00, 0.76, 0.24)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.24, 0.0, (0.72, 0.10, 0.36), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.54, -0.20, (0.64, 0.030, 0.045), dark)
        for local_x in (-0.64, 0.64):
            for local_z in (-0.32, 0.32):
                self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.74, local_z, (0.030, 0.62, 0.030), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 1.34, 0.0, (0.84, 0.080, 0.46), red)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 1.44, 0.0, (0.76, 0.030, 0.40), gold)
        for panel in range(4):
            self.add_local_cube(app, base_x, base_z, yaw, -0.36 + panel * 0.24, 0.93, 0.36, (0.080, 0.18, 0.012), gold if panel % 2 else red)
        for i, local_x in enumerate((-0.48, 0.0, 0.48)):
            lx, lz = self.local_house_pos(base_x, base_z, yaw, local_x, 0.44)
            self.add_object(ColorCube(app, pos=(lx, 0.86, lz), rot=(0, yaw, 0), scale=(0.070, 0.095, 0.060), color=(0.96, 0.82, 0.52)))
            self.add_object(NightGlow(app, pos=(lx, 0.86, lz), scale=(0.22, 0.22, 1.0), color=(1.00, 0.62, 0.24), alpha=0.32, pulse=0.045 + i * 0.005))

    def add_summer_firefly_clusters(self, app):
        add = self.add_object
        centers = [(9.2, 0.92, 9.8), (10.5, 1.05, 10.5), (8.0, 0.84, 8.6), (4.6, 1.10, 5.9), (-3.4, 0.96, 5.8), (7.6, 1.20, -2.0)]
        for i in range(18):
            cx, cy, cz = centers[i % len(centers)]
            add(
                FireflyGlow(
                    app,
                    center=(cx + 0.18 * math.sin(i), cy + 0.05 * (i % 3), cz + 0.22 * math.cos(i * 0.7)),
                    orbit=(0.36 + 0.04 * (i % 3), 0.20, 0.30 + 0.03 * (i % 2)),
                    scale=(0.022, 0.022, 1.0),
                    alpha=0.52,
                    speed=0.14 + (i % 5) * 0.012,
                    phase=(i * 0.137) % 1.0,
                )
            )

    def add_summer_heat_shimmer(self, app):
        add = self.add_object
        for i in range(14):
            angle = math.radians(18 + i * 18.0)
            radius = 8.45 + 0.12 * math.sin(i)
            add(
                SunDisc(
                    app,
                    pos=(math.cos(angle) * radius, 0.052, math.sin(angle) * radius),
                    rot=(90, math.degrees(angle) + 4.0, 0),
                    scale=(0.54 + 0.06 * (i % 2), 0.090, 1.0),
                    color=(1.00, 0.86, 0.38),
                    alpha=0.060,
                )
            )

    def add_summer_festival_banners(self, app):
        add = self.add_object
        start = (8.2, 1.38, 10.9)
        end = (13.2, 1.38, 9.9)
        dx = end[0] - start[0]
        dz = end[2] - start[2]
        length = math.sqrt(dx * dx + dz * dz)
        yaw = math.degrees(math.atan2(dx, dz))
        add(ColorCube(app, pos=((start[0] + end[0]) * 0.5, start[1], (start[2] + end[2]) * 0.5), rot=(0, yaw, 0), scale=(0.018, 0.018, length * 0.52), color=(0.24, 0.14, 0.06)))
        for i in range(11):
            t = i / 10.0
            x = start[0] + dx * t
            z = start[2] + dz * t
            color = (0.92, 0.18, 0.10) if i % 3 == 0 else (1.00, 0.78, 0.28) if i % 3 == 1 else (0.20, 0.44, 0.74)
            add(ColorCube(app, pos=(x, 1.20 - 0.04 * (i % 2), z), rot=(0, yaw, 0), scale=(0.070, 0.13, 0.012), color=color))

    def add_summer_fireworks(self, app):
        add = self.add_object
        burst_specs = [
            ((-5.6, 5.8, -18.5), (1.00, 0.46, 0.18), 0.78),
            ((0.4, 6.6, -20.2), (1.00, 0.84, 0.28), 0.92),
            ((5.9, 5.9, -18.9), (0.42, 0.70, 1.00), 0.72),
        ]
        for idx, (center, color, radius) in enumerate(burst_specs):
            add(NightGlow(app, pos=center, scale=(0.70 + radius * 0.18, 0.70 + radius * 0.18, 1.0), color=color, alpha=0.30, pulse=0.12))
            for ray in range(12):
                angle = ray * math.tau / 12.0
                length = 0.18 + radius * (0.10 + 0.018 * (ray % 3))
                add(
                    ColorCube(
                        app,
                        pos=(center[0] + math.cos(angle) * radius * 0.26, center[1] + math.sin(angle) * radius * 0.18, center[2]),
                        rot=(0, idx * 18.0, math.degrees(angle)),
                        scale=(length, 0.010, 0.010),
                        color=color if ray % 2 else (1.00, 0.94, 0.68),
                    )
                )

        for i in range(10):
            x = -0.8 + i * 0.18
            z = 7.35 + 0.10 * math.sin(i)
            add(ColorCube(app, pos=(x, 0.32, z), rot=(0, 18, -8), scale=(0.010, 0.28, 0.010), color=(0.36, 0.20, 0.08)))
            add(NightGlow(app, pos=(x, 0.63, z), scale=(0.12, 0.12, 1.0), color=(1.00, 0.74, 0.24), alpha=0.28, pulse=0.16))

    def add_summer_kakigori_counter(self, app):
        base_x, base_z, yaw = (11.0, 9.2, -24.0)
        wood = (0.36, 0.20, 0.10)
        ice = (0.86, 0.96, 1.00)
        syrup_colors = [(0.94, 0.12, 0.18), (0.22, 0.58, 0.92), (0.36, 0.78, 0.32)]
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.22, 0.0, (0.42, 0.10, 0.22), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.39, 0.0, (0.46, 0.030, 0.26), (0.95, 0.86, 0.52))
        for i, local_x in enumerate((-0.22, 0.0, 0.22)):
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.49, 0.02, (0.055, 0.055, 0.055), ice)
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.555, 0.02, (0.045, 0.014, 0.045), syrup_colors[i])
        for i, local_x in enumerate((-0.30, 0.30)):
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.78, -0.02, (0.016, 0.34, 0.016), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 1.04, -0.02, (0.40, 0.050, 0.23), (0.90, 0.18, 0.12))
