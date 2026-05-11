import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneVillageUpgradeMixin:
    def add_extra_house_details(self, app):
        detail_specs = [
            (-9.7, 8.0, 12.0),
            (-5.7, -10.1, -8.0),
            (6.6, 10.0, 6.0),
            (10.4, -4.9, 18.0),
        ]
        for idx, (x, z, yaw) in enumerate(detail_specs):
            self.add_house_side_props(app, x, z, yaw, idx)

    def add_house_side_props(self, app, x, z, yaw, idx):
        add = self.add_object
        wood = (0.38, 0.22, 0.11)
        cloth_colors = [(0.84, 0.32, 0.28), (0.92, 0.82, 0.54), (0.42, 0.62, 0.84)]
        self.add_local_cube(app, x, z, yaw, -0.42, 0.34, 0.62, (0.030, 0.34, 0.030), wood)
        self.add_local_cube(app, x, z, yaw, 0.42, 0.34, 0.62, (0.030, 0.34, 0.030), wood)
        self.add_local_cube(app, x, z, yaw, 0.0, 0.62, 0.62, (0.46, 0.018, 0.018), wood)
        for i, local_x in enumerate((-0.24, 0.00, 0.24)):
            self.add_local_cube(app, x, z, yaw, local_x, 0.49, 0.64, (0.070, 0.11, 0.012), cloth_colors[(idx + i) % len(cloth_colors)])

        for i, local_x in enumerate((-0.55, 0.55)):
            px, pz = self.local_house_pos(x, z, yaw, local_x, -0.48)
            add(ColorCube(app, pos=(px, 0.10, pz), rot=(0, yaw, 0), scale=(0.095, 0.080, 0.095), color=(0.36, 0.20, 0.11)))
            add(PondRock(app, pos=(px, 0.24, pz), rot=(0, yaw + i * 24, 0), scale=(0.14, 0.10, 0.12), color=self.season_color("garden_hedge_color", (0.24, 0.42, 0.18))))

    def add_extra_vegetation(self, app):
        bamboo_sites = [(-13.6, 2.4), (13.2, 3.6), (-12.8, -7.2)]
        for idx, (x, z) in enumerate(bamboo_sites):
            self.add_bamboo_cluster(app, x, z, idx * 17.0)

        for idx, (x, z, color) in enumerate(
            [
                (-15.0, -11.0, self.season_color("transition_color", (0.86, 0.34, 0.14))),
                (15.4, -9.4, self.season_color("sakura_canopy_deep_color", (0.72, 0.25, 0.11))),
                (14.8, 8.8, (0.20, 0.38, 0.18) if not self.is_winter() else (0.82, 0.88, 0.90)),
            ]
        ):
            self.add_flat_season_tree(app, x, z, color, idx)

    def add_bamboo_cluster(self, app, x, z, phase):
        add = self.add_object
        stem = (0.30, 0.46, 0.18) if not self.is_winter() else (0.62, 0.72, 0.68)
        leaf = (0.20, 0.40, 0.16) if not self.is_winter() else (0.84, 0.90, 0.92)
        for i in range(7):
            offset = (i - 3) * 0.12
            height = 0.95 + 0.12 * (i % 3)
            add(ColorCube(app, pos=(x + offset, height, z + 0.08 * math.sin(i)), rot=(0, phase + i * 9.0, 5.0 * math.sin(i)), scale=(0.026, height, 0.026), color=stem))
            for j in range(2):
                add(ColorCube(app, pos=(x + offset + 0.10 * (-1 if j else 1), height * 1.55, z), rot=(20, phase + 40 + j * 90, 0), scale=(0.16, 0.018, 0.045), color=leaf))

    def add_flat_season_tree(self, app, x, z, color, idx):
        add = self.add_object
        add(ColorCube(app, pos=(x, 0.62, z), scale=(0.10, 0.62, 0.10), color=(0.28, 0.17, 0.09)))
        for layer in range(4):
            add(
                PondRock(
                    app,
                    pos=(x + 0.18 * math.sin(layer + idx), 1.16 + layer * 0.14, z + 0.12 * math.cos(layer)),
                    rot=(0, idx * 31.0 + layer * 18.0, 0),
                    scale=(0.60 - layer * 0.06, 0.24, 0.46 - layer * 0.04),
                    color=color,
                )
            )

    def _local_pos3(self, base_x, base_z, yaw, local_x, y, local_z):
        x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        return (x, y, z)
