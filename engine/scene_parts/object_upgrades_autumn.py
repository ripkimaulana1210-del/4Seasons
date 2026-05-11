import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneAutumnObjectUpgradeMixin:
    def add_autumn_work_corner(self, app):
        add = self.add_object
        colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
        base_x, base_z = (6.8, 6.8)
        for i in range(32):
            angle = i * 0.73
            add(ColorCube(app, pos=(base_x + math.cos(angle) * 0.55, 0.046 + 0.004 * (i % 4), base_z + math.sin(angle) * 0.34), rot=(0, i * 21.0, 0), scale=(0.060, 0.008, 0.030), color=colors[i % len(colors)]))
        add(PondRock(app, pos=(base_x + 0.62, 0.16, base_z - 0.14), rot=(0, 18, 0), scale=(0.18, 0.13, 0.14), color=(0.48, 0.26, 0.10)))
        add(ColorCube(app, pos=(base_x + 0.66, 0.31, base_z - 0.13), rot=(0, 18, 0), scale=(0.15, 0.030, 0.11), color=(0.76, 0.50, 0.22)))
        add(ColorCube(app, pos=(base_x - 0.58, 0.32, base_z + 0.05), rot=(0, 32, 28), scale=(0.016, 0.34, 0.016), color=(0.36, 0.20, 0.08)))
        for i in range(5):
            add(ColorCube(app, pos=(base_x - 0.48 + i * 0.055, 0.62, base_z - 0.06), rot=(0, 32, 28), scale=(0.008, 0.070, 0.008), color=(0.58, 0.35, 0.12)))

    def add_autumn_mushrooms(self, app):
        add = self.add_object
        sites = [(-5.4, -3.4), (-6.0, -2.9), (5.2, -6.2), (6.0, -6.0), (10.4, 1.6), (-10.0, 2.0)]
        for i, (x, z) in enumerate(sites):
            add(ColorCube(app, pos=(x, 0.105, z), scale=(0.026, 0.070, 0.026), color=(0.88, 0.76, 0.56)))
            add(PondRock(app, pos=(x, 0.190, z), rot=(0, i * 25.0, 0), scale=(0.085, 0.040, 0.070), color=(0.72, 0.20, 0.10) if i % 2 else (0.94, 0.52, 0.16)))

    def add_autumn_bare_branches(self, app):
        add = self.add_object
        for idx, (x, z, yaw) in enumerate(((12.4, -2.8, -16.0), (-12.1, 5.2, 22.0))):
            add(ColorCube(app, pos=(x, 0.72, z), rot=(0, yaw, 8), scale=(0.070, 0.72, 0.060), color=(0.28, 0.16, 0.08)))
            for branch in range(7):
                side = -1 if branch % 2 else 1
                add(ColorCube(app, pos=(x + side * 0.18 * (branch + 1) / 7.0, 1.18 + branch * 0.10, z + 0.08 * math.sin(branch)), rot=(18, yaw + side * (34 + branch * 7), side * 22), scale=(0.18 + 0.02 * (branch % 3), 0.016, 0.018), color=(0.30, 0.17, 0.08)))
            for leaf in range(8):
                add(ColorCube(app, pos=(x + 0.45 * math.sin(leaf), 1.22 + 0.08 * math.cos(leaf), z + 0.36 * math.cos(leaf * 0.7)), rot=(0, leaf * 33, 0), scale=(0.045, 0.006, 0.024), color=(0.86, 0.42, 0.12) if (leaf + idx) % 2 else (0.94, 0.64, 0.18)))

    def add_autumn_wet_path(self, app):
        add = self.add_object
        puddles = [(-2.2, 8.35, -8, 0.38), (4.5, 7.25, 18, 0.32), (8.2, -1.2, 32, 0.30), (-8.1, -1.8, -22, 0.36)]
        for x, z, yaw, scale_x in puddles:
            add(SunDisc(app, pos=(x, 0.042, z), rot=(90, yaw, 0), scale=(scale_x, 0.12, 1.0), color=(0.18, 0.26, 0.28), alpha=0.16))
        colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
        for i in range(30):
            t = i / 29.0
            x = -1.6 + t * 5.8
            z = 8.35 - math.sin(t * math.pi) * 0.72
            add(ColorCube(app, pos=(x, 0.047, z), rot=(0, i * 17.0, 0), scale=(0.050, 0.006, 0.026), color=colors[i % len(colors)]))

    def add_autumn_harvest_display(self, app):
        add = self.add_object
        base_x, base_z, yaw = (-10.15, -4.10, 42.0)
        wood = (0.34, 0.18, 0.08)
        straw = (0.78, 0.58, 0.24)
        pumpkin_colors = [(0.90, 0.42, 0.10), (0.76, 0.30, 0.08), (0.96, 0.60, 0.16)]
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.20, 0.0, (0.58, 0.090, 0.34), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.34, 0.0, (0.50, 0.045, 0.30), straw)
        for i, local_x in enumerate((-0.34, -0.12, 0.14, 0.36)):
            px, pz = self.local_house_pos(base_x, base_z, yaw, local_x, 0.07 * math.sin(i))
            add(PondRock(app, pos=(px, 0.47 + 0.02 * (i % 2), pz), rot=(0, yaw + i * 18.0, 0), scale=(0.13, 0.095, 0.11), color=pumpkin_colors[i % len(pumpkin_colors)]))
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.58 + 0.02 * (i % 2), 0.07 * math.sin(i), (0.012, 0.030, 0.012), (0.26, 0.34, 0.10))
        for i in range(8):
            self.add_local_cube(app, base_x, base_z, yaw, -0.46 + i * 0.13, 0.66 + 0.02 * math.sin(i), -0.30, (0.030, 0.12, 0.010), straw, rot=(0, 0, -18 + i * 5))

    def add_autumn_maple_tunnel(self, app):
        colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
        base_x, base_z, yaw = (0.2, 8.55, 4.0)
        wood = (0.26, 0.14, 0.07)
        for post in range(5):
            local_x = -1.40 + post * 0.70
            for side in (-1, 1):
                self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.78, side * 0.46, (0.030, 0.78, 0.030), wood)
                self.add_local_cube(app, base_x, base_z, yaw, local_x + side * 0.11, 1.42, side * 0.34, (0.24, 0.018, 0.020), wood, rot=(0, side * 18, side * 24))

        for i in range(34):
            t = i / 33.0
            local_x = -1.50 + t * 3.0
            local_z = math.sin(t * math.pi) * 0.16
            y = 1.54 + 0.22 * math.sin(t * math.pi)
            self.add_local_cube(
                app,
                base_x,
                base_z,
                yaw,
                local_x,
                y,
                local_z,
                (0.070, 0.008, 0.034),
                colors[i % len(colors)],
                rot=(0, i * 17.0, 12.0 * math.sin(i)),
            )
