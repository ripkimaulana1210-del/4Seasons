import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneShrineUpgradeMixin:
    def add_torii_and_shrine(self, app):
        add = self.add_object
        red = (0.78, 0.10, 0.07)
        dark_red = (0.42, 0.07, 0.05)
        black = (0.08, 0.06, 0.05)
        x, z, yaw = (8.9, -6.9, -30.0)

        for local_x in (-0.62, 0.62):
            px = x + math.cos(math.radians(yaw)) * local_x
            pz = z - math.sin(math.radians(yaw)) * local_x
            add(ColorCube(app, pos=(px, 0.76, pz), rot=(0, yaw, 0), scale=(0.07, 0.76, 0.07), color=red))
            add(ColorCube(app, pos=(px, 1.56, pz), rot=(0, yaw, 0), scale=(0.10, 0.05, 0.10), color=black))

        add(ColorCube(app, pos=(x, 1.48, z), rot=(0, yaw, 0), scale=(0.88, 0.055, 0.075), color=dark_red))
        add(ColorCube(app, pos=(x, 1.66, z), rot=(0, yaw, 0), scale=(1.08, 0.065, 0.095), color=red))
        add(ColorCube(app, pos=(x, 1.78, z), rot=(0, yaw, 0), scale=(1.16, 0.030, 0.110), color=black))

        shrine_x, shrine_z = (10.3, -8.2)
        add(ColorCube(app, pos=(shrine_x, 0.24, shrine_z), rot=(0, -20, 0), scale=(0.46, 0.24, 0.38), color=(0.46, 0.30, 0.16)))
        add(ColorCube(app, pos=(shrine_x, 0.58, shrine_z), rot=(0, -20, 0), scale=(0.54, 0.08, 0.46), color=dark_red))
        add(ColorCube(app, pos=(shrine_x, 0.73, shrine_z), rot=(0, -20, 0), scale=(0.42, 0.08, 0.34), color=black))
        add(NightGlow(app, pos=(shrine_x, 0.48, shrine_z + 0.05), scale=(0.24, 0.24, 1.0), color=(1.0, 0.58, 0.24), alpha=0.32, pulse=0.03))

    def add_shrine_path_and_offerings(self, app):
        add = self.add_object
        torii_x, torii_z, torii_yaw = (8.9, -6.9, -30.0)
        shrine_x, shrine_z, shrine_yaw = (10.3, -8.2, -20.0)
        path_color = self.season_color("garden_path_color", (0.62, 0.54, 0.40))
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone_color = snow if self.is_winter() else path_color
        wood = (0.36, 0.22, 0.12)
        dark_wood = (0.18, 0.10, 0.06)
        straw = (0.78, 0.62, 0.34)
        paper = (0.96, 0.92, 0.78)
        red = (0.78, 0.10, 0.07)

        dx = shrine_x - torii_x
        dz = shrine_z - torii_z
        length = math.sqrt(dx * dx + dz * dz)
        lat_x = -dz / (length + 1e-6)
        lat_z = dx / (length + 1e-6)
        yaw = math.degrees(math.atan2(dx, dz))

        for i in range(9):
            t = 0.08 + i * 0.10
            wiggle = math.sin(i * 1.7) * 0.08
            x = torii_x + dx * t + lat_x * wiggle
            z = torii_z + dz * t + lat_z * wiggle
            add(
                PondRock(
                    app,
                    pos=(x, 0.075, z),
                    rot=(0, yaw + i * 11.0, 0),
                    scale=(0.22 + 0.02 * (i % 2), 0.040, 0.15),
                    color=stone_color,
                )
            )

        for idx, (t, side) in enumerate(((0.24, -1), (0.42, 1), (0.62, -1), (0.78, 1))):
            x = torii_x + dx * t + lat_x * side * 0.56
            z = torii_z + dz * t + lat_z * side * 0.56
            add(ColorCube(app, pos=(x, 0.10, z), rot=(0, yaw, 0), scale=(0.12, 0.08, 0.12), color=dark_wood))
            add(ColorCube(app, pos=(x, 0.38, z), rot=(0, yaw, 0), scale=(0.030, 0.30, 0.030), color=wood))
            add(ColorCube(app, pos=(x, 0.72, z), rot=(0, yaw, 0), scale=(0.10, 0.045, 0.10), color=red if idx % 2 else dark_wood))
            add(ColorCube(app, pos=(x, 0.58, z), rot=(0, yaw, 0), scale=(0.070, 0.080, 0.070), color=paper))
            add(NightGlow(app, pos=(x, 0.58, z), scale=(0.20, 0.20, 1.0), color=(1.0, 0.64, 0.30), alpha=0.28, pulse=0.035))

        self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, 0.0, 0.18, 0.54, (0.30, 0.13, 0.18), dark_wood)
        self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, 0.0, 0.33, 0.54, (0.32, 0.028, 0.20), wood)
        for i, local_x in enumerate((-0.20, -0.07, 0.07, 0.20)):
            self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, local_x, 0.38, 0.42, (0.018, 0.022, 0.13), straw if i % 2 else paper)

        board_x, board_z, board_yaw = (9.55, -8.55, 16.0)
        for local_x in (-0.42, 0.42):
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.34, 0.0, (0.026, 0.34, 0.026), wood)
        self.add_local_cube(app, board_x, board_z, board_yaw, 0.0, 0.60, 0.0, (0.48, 0.020, 0.018), dark_wood)
        self.add_local_cube(app, board_x, board_z, board_yaw, 0.0, 0.31, 0.0, (0.44, 0.020, 0.018), dark_wood)
        for i, local_x in enumerate((-0.30, -0.15, 0.0, 0.15, 0.30)):
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.45, -0.03, (0.055, 0.070, 0.012), paper if i % 2 else (0.86, 0.68, 0.38))
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.53, -0.03, (0.010, 0.030, 0.010), straw)

        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.28, 0.0, (0.52, 0.014, 0.016), straw)
        for i, local_x in enumerate((-0.28, -0.09, 0.10, 0.30)):
            self.add_local_cube(app, torii_x, torii_z, torii_yaw, local_x, 1.14 - 0.03 * (i % 2), 0.02, (0.034, 0.10, 0.008), paper, rot=(0, 0, 5.0 * (-1 if i % 2 else 1)))
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.10, 0.03, (0.040, 0.050, 0.030), (0.88, 0.66, 0.22))
