import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneSpringObjectUpgradeMixin:
    def add_spring_flower_arch(self, app):
        colors = [(1.00, 0.64, 0.84), (1.00, 0.82, 0.92), (0.86, 0.62, 1.00), (0.92, 0.94, 0.46)]
        pond_radius_scale = SCENE_LAYOUT["pond"]["radius_scale"]
        base_x, base_z, yaw = (2.77 * pond_radius_scale, 4.80 * pond_radius_scale, -34.0)
        wood = (0.28, 0.18, 0.09)
        for side in (-1, 1):
            self.add_local_cube(app, base_x, base_z, yaw, side * 0.54, 0.64, 0.0, (0.030, 0.64, 0.030), wood)
        for i in range(9):
            t = i / 8.0
            local_x = -0.54 + t * 1.08
            y = 1.12 + math.sin(t * math.pi) * 0.36
            self.add_local_cube(app, base_x, base_z, yaw, local_x, y, 0.0, (0.085, 0.035, 0.035), colors[i % len(colors)])
            if i % 2 == 0:
                self.add_local_cube(app, base_x, base_z, yaw, local_x, y - 0.10, 0.035, (0.024, 0.090, 0.018), (0.32, 0.62, 0.24), rot=(0, 0, -14))

    def add_spring_petal_road(self, app):
        add = self.add_object
        petal = self.season_color("floating_petal_color", (1.0, 0.64, 0.84))
        pale = (1.00, 0.82, 0.94)
        for i in range(34):
            angle = math.radians(8.0 + i * 9.4)
            radius = 8.35 + 0.20 * math.sin(i * 0.7)
            add(
                ColorCube(
                    app,
                    pos=(math.cos(angle) * radius, 0.040 + 0.002 * (i % 3), math.sin(angle) * radius),
                    rot=(0, math.degrees(angle) + i * 23.0, 0),
                    scale=(0.045, 0.004, 0.020),
                    color=petal if i % 3 else pale,
                )
            )

    def add_spring_butterflies(self, app):
        add = self.add_object
        wing_colors = [(1.00, 0.72, 0.24), (0.94, 0.56, 0.86), (0.62, 0.76, 1.00)]
        sites = [(-4.4, 1.00, 6.2), (-2.8, 1.24, 7.4), (2.8, 1.10, 5.4), (5.5, 0.92, -3.2), (-7.2, 0.86, 3.0), (1.0, 1.35, -5.8)]
        for i, (x, y, z) in enumerate(sites):
            yaw = i * 47.0
            color = wing_colors[i % len(wing_colors)]
            add(ColorCube(app, pos=(x, y, z), rot=(0, yaw, 0), scale=(0.010, 0.055, 0.010), color=(0.16, 0.10, 0.06)))
            add(ColorCube(app, pos=(x - 0.038, y + 0.006, z), rot=(18, yaw - 24, 28), scale=(0.050, 0.008, 0.028), color=color))
            add(ColorCube(app, pos=(x + 0.038, y + 0.006, z), rot=(18, yaw + 24, -28), scale=(0.050, 0.008, 0.028), color=color))

    def add_spring_rain_puddles(self, app):
        add = self.add_object
        for i, (x, z, yaw, scale_x) in enumerate(((-8.4, 1.9, 10, 0.44), (-1.2, 8.9, -18, 0.36), (7.9, 2.0, 28, 0.32), (4.8, -7.7, 6, 0.38))):
            add(SunDisc(app, pos=(x, 0.040, z), rot=(90, yaw, 0), scale=(scale_x, 0.14, 1.0), color=(0.54, 0.74, 0.88), alpha=0.14 + 0.02 * (i % 2)))

    def add_spring_tea_corner(self, app):
        add = self.add_object
        base_x, base_z, yaw = (-4.35, 7.82, 18.0)
        mat_color = (0.44, 0.64, 0.28)
        wood = (0.34, 0.20, 0.10)
        ceramic = (0.96, 0.88, 0.72)
        tea_green = (0.42, 0.62, 0.28)
        add(ColorPlane(app, pos=(base_x, 0.038, base_z), rot=(0, yaw, 0), scale=(0.56, 1, 0.34), color=mat_color))
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.105, 0.0, (0.28, 0.030, 0.18), wood)
        add(ColorCube(app, pos=self._local_pos3(base_x, base_z, yaw, -0.10, 0.175, -0.04), rot=(0, yaw, 0), scale=(0.060, 0.045, 0.050), color=ceramic))
        add(ColorCube(app, pos=self._local_pos3(base_x, base_z, yaw, -0.10, 0.220, -0.04), rot=(0, yaw, 0), scale=(0.070, 0.010, 0.060), color=tea_green))
        for i, local_x in enumerate((0.02, 0.16, 0.30)):
            add(ColorCube(app, pos=self._local_pos3(base_x, base_z, yaw, local_x, 0.165, 0.055), rot=(0, yaw + i * 16.0, 0), scale=(0.035, 0.022, 0.035), color=ceramic))
            add(ColorCube(app, pos=self._local_pos3(base_x, base_z, yaw, local_x, 0.190, 0.055), rot=(0, yaw, 0), scale=(0.025, 0.006, 0.025), color=tea_green))
        for i in range(8):
            add(
                WindStreak(
                    app,
                    pos=self._local_pos3(base_x, base_z, yaw, -0.14 + i * 0.018, 0.30 + i * 0.018, -0.05),
                    rot=(0, yaw + 8.0, 0),
                    scale=(0.020, 0.006, 0.040),
                    color=(0.94, 0.96, 0.92),
                    travel=(0.04, 0.10, -0.02),
                    speed=0.055 + i * 0.004,
                    phase=i * 0.08,
                    bob=0.04,
                )
            )

    def add_spring_wishing_tags(self, app):
        add = self.add_object
        base_x, base_z, yaw = (4.65, 4.92, -24.0)
        wood = (0.28, 0.17, 0.08)
        tag_colors = [(1.00, 0.76, 0.88), (0.96, 0.90, 0.62), (0.76, 0.94, 0.72), (0.78, 0.78, 1.00)]
        for local_x in (-0.52, 0.52):
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.58, 0.0, (0.026, 0.58, 0.026), wood)
        self.add_local_cube(app, base_x, base_z, yaw, 0.0, 1.08, 0.0, (0.62, 0.020, 0.018), wood)
        for i in range(9):
            local_x = -0.44 + i * 0.11
            swing = 0.03 * math.sin(i * 1.7)
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.92 + swing, 0.020, (0.030, 0.11, 0.006), tag_colors[i % len(tag_colors)], rot=(0, 0, -6.0 + i * 1.5))
            self.add_local_cube(app, base_x, base_z, yaw, local_x, 1.00 + swing, 0.018, (0.004, 0.045, 0.004), wood)
