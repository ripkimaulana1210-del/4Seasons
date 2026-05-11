import math

from ..data.scene_config import SCENE_LAYOUT
from ..models import (
    ColorCube,
    ColorPlane,
    FireflyGlow,
    NightGlow,
    PondRock,
    SunDisc,
    TexturedCube,
    TexturedGableRoof,
    TexturedPlane,
    WindStreak,
)


class SceneBuildingAdditionsMixin:
    def add_building_additions(self, app, pond_radius_scale):
        layout = SCENE_LAYOUT["building_additions"]
        self._add_scaled_building(self.add_tea_house, app, layout["tea_house"])
        self._add_scaled_building(self.add_open_pavilion, app, layout["pavilion"])
        self._add_scaled_building(self.add_water_mill, app, layout["water_mill"])
        self._add_scaled_building(self.add_secondary_torii_gate, app, layout["secondary_torii"])
        self._add_scaled_building(self.add_yatai_market_row, app, layout["yatai_row"])
        self._add_scaled_building(self.add_bathhouse_onsen, app, layout["bathhouse"])
        self._add_scaled_building(self.add_storage_shed, app, layout["storage_shed"])
        self._add_scaled_building(self.add_viewing_deck, app, layout["viewing_deck"])
        self._add_scaled_bridge_roof(app, pond_radius_scale, layout["covered_bridge"])
        self._add_scaled_building(self.add_rice_field, app, layout["rice_field"])

    def _add_scaled_building(self, builder, app, config):
        previous = getattr(self, "_building_scale", 1.0)
        self._building_scale = config.get("scale", 1.0)
        try:
            builder(app, config["pos"], config["yaw"])
        finally:
            self._building_scale = previous

    def _add_scaled_bridge_roof(self, app, pond_radius_scale, config):
        previous = getattr(self, "_building_scale", 1.0)
        self._building_scale = config.get("scale", 1.0)
        try:
            self.add_covered_bridge_roof(app, pond_radius_scale)
        finally:
            self._building_scale = previous

    def _add_scene_object(self, obj, tag, layer="village"):
        self.add_object(obj, tag=tag, layer=layer)

    def _scale_value(self):
        return getattr(self, "_building_scale", 1.0)

    def _y(self, value):
        return value * self._scale_value()

    def _shape(self, scale):
        size = self._scale_value()
        return tuple(component * size for component in scale)

    def _flat_shape(self, scale):
        size = self._scale_value()
        return (scale[0] * size, scale[1], scale[2] * size)

    def _local_y_pos(self, value):
        return value * self._scale_value()

    def _local_pos(self, base_x, base_z, yaw, local_x, local_z):
        size = self._scale_value()
        local_x *= size
        local_z *= size
        angle = math.radians(yaw)
        return (
            base_x + local_x * math.cos(angle) + local_z * math.sin(angle),
            base_z - local_x * math.sin(angle) + local_z * math.cos(angle),
        )

    def _box(self, app, tag, base_x, base_z, yaw, local_x, y, local_z, scale, color, layer="village", rot=(0, 0, 0)):
        x, z = self._local_pos(base_x, base_z, yaw, local_x, local_z)
        self._add_scene_object(
            ColorCube(
                app,
                pos=(x, self._y(y), z),
                rot=(rot[0], yaw + rot[1], rot[2]),
                scale=self._shape(scale),
                color=color,
            ),
            tag,
            layer,
        )
        return x, z

    def _textured_box(
        self,
        app,
        tag,
        base_x,
        base_z,
        yaw,
        local_x,
        y,
        local_z,
        scale,
        texture_name,
        tint,
        layer="village",
        repeat=(1.2, 1.0),
    ):
        x, z = self._local_pos(base_x, base_z, yaw, local_x, local_z)
        self._add_scene_object(
            TexturedCube(
                app,
                pos=(x, self._y(y), z),
                rot=(0, yaw, 0),
                scale=self._shape(scale),
                texture_name=texture_name,
                tint=tint,
                repeat=repeat,
            ),
            tag,
            layer,
        )
        return x, z

    def _roof(self, app, tag, base_x, base_z, yaw, local_x, y, local_z, scale, tint, layer="village"):
        x, z = self._local_pos(base_x, base_z, yaw, local_x, local_z)
        self._add_scene_object(
            TexturedGableRoof(
                app,
                pos=(x, self._y(y), z),
                rot=(0, yaw, 0),
                scale=self._shape(scale),
                texture_name="roof",
                tint=tint,
                repeat=(1.1, 1.35),
            ),
            tag,
            layer,
        )
        if self.is_winter():
            snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
            self._box(app, tag, base_x, base_z, yaw, local_x - scale[0] * 0.20, y + scale[1] * 0.52, local_z, (scale[0] * 0.34, 0.018, scale[2] * 0.56), snow, layer, rot=(0, 0, -13))
            self._box(app, tag, base_x, base_z, yaw, local_x + scale[0] * 0.20, y + scale[1] * 0.52, local_z, (scale[0] * 0.34, 0.018, scale[2] * 0.56), snow, layer, rot=(0, 0, 13))

    def _lamp(self, app, tag, base_x, base_z, yaw, local_x, y, local_z, color=(1.0, 0.64, 0.30), layer="village"):
        x, z = self._box(app, tag, base_x, base_z, yaw, local_x, y - 0.10, local_z, (0.028, 0.12, 0.028), (0.24, 0.12, 0.06), layer)
        self._box(app, tag, base_x, base_z, yaw, local_x, y + 0.03, local_z, (0.075, 0.080, 0.060), color, layer)
        self._add_scene_object(
            NightGlow(app, pos=(x, self._y(y + 0.03), z), scale=(0.22 * self._scale_value(), 0.22 * self._scale_value(), 1.0), color=color, alpha=0.30, pulse=0.035),
            tag,
            "atmosphere",
        )

    def _season_scatter(self, app, tag, base_x, base_z, yaw, points, layer="vegetation"):
        effect = self.season_value("seasonal_effect", "spring")
        if effect == "winter":
            color = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
            for i, (lx, lz, sx, sz) in enumerate(points):
                self._add_disc(app, tag, base_x, base_z, yaw, lx, 0.052 + 0.002 * (i % 2), lz, (sx, sz, 1.0), color, 0.20, "scene")
        elif effect == "spring":
            colors = [(1.0, 0.66, 0.86), (1.0, 0.86, 0.94), (0.96, 0.82, 0.40)]
            for i, (lx, lz, sx, sz) in enumerate(points):
                self._box(app, tag, base_x, base_z, yaw, lx, 0.065, lz, (sx * 0.12, 0.006, sz * 0.12), colors[i % len(colors)], layer, rot=(0, i * 29.0, 0))
        elif effect == "autumn":
            colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
            for i, (lx, lz, sx, sz) in enumerate(points):
                self._box(app, tag, base_x, base_z, yaw, lx, 0.058, lz, (sx * 0.15, 0.006, sz * 0.09), colors[i % len(colors)], layer, rot=(0, i * 37.0, 0))

    def _add_disc(self, app, tag, base_x, base_z, yaw, local_x, y, local_z, scale, color, alpha, layer):
        x, z = self._local_pos(base_x, base_z, yaw, local_x, local_z)
        self._add_scene_object(
            SunDisc(
                app,
                pos=(x, self._y(y), z),
                rot=(90, yaw, 0),
                scale=(scale[0] * self._scale_value(), scale[1] * self._scale_value(), scale[2]),
                color=color,
                alpha=alpha,
            ),
            tag,
            layer,
        )

    def add_tea_house(self, app, pos, yaw):
        x, z = pos
        tag = "tea_house"
        wall = (0.74, 0.63, 0.48)
        wood = (0.28, 0.17, 0.08)
        dark = (0.16, 0.09, 0.05)
        paper = (0.92, 0.86, 0.70)
        roof = (0.42, 0.12, 0.08)

        self._add_scene_object(TexturedPlane(app, pos=(x, 0.012, z), rot=(0, yaw, 0), scale=self._flat_shape((1.35, 1.0, 1.10)), texture_name="mossy_stone", tint=(0.58, 0.56, 0.46), repeat=(2.0, 1.8)), tag, "terrain")
        self._textured_box(app, tag, x, z, yaw, 0.0, 0.42, 0.0, (0.78, 0.42, 0.58), "wall", wall, repeat=(1.6, 1.1))
        self._box(app, tag, x, z, yaw, 0.0, 0.22, 0.64, (0.92, 0.12, 0.08), wood)
        for lx in (-0.72, 0.72):
            for lz in (-0.54, 0.58):
                self._box(app, tag, x, z, yaw, lx, 0.52, lz, (0.045, 0.52, 0.045), dark)
        self._roof(app, tag, x, z, yaw, 0.0, 0.94, 0.0, (1.16, 0.38, 0.88), roof)

        for lx in (-0.28, 0.28):
            self._box(app, tag, x, z, yaw, lx, 0.48, 0.63, (0.22, 0.26, 0.018), paper)
            self._box(app, tag, x, z, yaw, lx, 0.48, 0.66, (0.012, 0.28, 0.022), dark)
        self._box(app, tag, x, z, yaw, 0.0, 0.22, -0.66, (0.66, 0.08, 0.16), wood)
        self._box(app, tag, x, z, yaw, 0.0, 0.34, -0.70, (0.48, 0.04, 0.12), (0.78, 0.54, 0.28))
        self._lamp(app, tag, x, z, yaw, -0.86, 0.62, 0.72)
        self._lamp(app, tag, x, z, yaw, 0.86, 0.62, 0.72)

        for i in range(5):
            self._box(app, tag, x, z, yaw, -0.52 + i * 0.26, 0.072, 0.98 + 0.05 * math.sin(i), (0.12, 0.030, 0.09), (0.46, 0.43, 0.38), "terrain", rot=(0, i * 11.0, 0))
        self._season_scatter(app, tag, x, z, yaw, [(-0.82, 0.96, 0.18, 0.12), (0.72, 0.92, 0.16, 0.10), (0.0, -0.88, 0.22, 0.14)])

    def add_open_pavilion(self, app, pos, yaw):
        x, z = pos
        tag = "open_pavilion"
        wood = (0.33, 0.19, 0.09)
        dark = (0.15, 0.08, 0.04)
        roof = (0.58, 0.16, 0.10)
        mat = self.season_color("garden_path_color", (0.56, 0.48, 0.34))

        self._add_scene_object(TexturedPlane(app, pos=(x, self._local_y_pos(0.020), z), rot=(0, yaw, 0), scale=self._flat_shape((1.18, 1.0, 0.92)), texture_name="wood", tint=(0.66, 0.48, 0.28), repeat=(3.0, 2.0)), tag, "village")
        for lx in (-0.94, 0.94):
            for lz in (-0.68, 0.68):
                self._box(app, tag, x, z, yaw, lx, 0.58, lz, (0.055, 0.58, 0.055), wood)
                self._box(app, tag, x, z, yaw, lx, 1.18, lz, (0.090, 0.045, 0.090), dark)
        self._roof(app, tag, x, z, yaw, 0.0, 1.22, 0.0, (1.34, 0.32, 1.02), roof)
        self._box(app, tag, x, z, yaw, 0.0, 0.40, -0.78, (0.74, 0.055, 0.055), wood)
        self._box(app, tag, x, z, yaw, -0.86, 0.40, 0.0, (0.055, 0.055, 0.60), wood)
        self._box(app, tag, x, z, yaw, 0.0, 0.135, 0.0, (0.34, 0.055, 0.25), mat)
        for lx in (-0.30, 0.30):
            self._lamp(app, tag, x, z, yaw, lx, 0.88, 0.62, color=(1.00, 0.52, 0.28))
        self._season_scatter(app, tag, x, z, yaw, [(-0.62, -0.82, 0.18, 0.10), (0.58, -0.78, 0.18, 0.10), (0.85, 0.20, 0.14, 0.08)])

    def add_water_mill(self, app, pos, yaw):
        x, z = pos
        tag = "water_mill"
        size = self._scale_value()
        wood = (0.36, 0.20, 0.10)
        dark = (0.18, 0.10, 0.05)
        water = (0.36, 0.66, 0.78) if not self.is_winter() else (0.72, 0.86, 0.94)

        self._textured_box(app, tag, x, z, yaw, 0.0, 0.38, 0.0, (0.54, 0.38, 0.46), "wall", (0.68, 0.54, 0.38), repeat=(1.2, 1.0))
        self._roof(app, tag, x, z, yaw, 0.0, 0.82, 0.0, (0.78, 0.30, 0.64), (0.36, 0.10, 0.07))
        self._box(app, tag, x, z, yaw, 0.0, 0.15, 0.62, (0.32, 0.06, 0.10), wood)

        wheel_x, wheel_z = self._local_pos(x, z, yaw, -0.66, 0.04)
        self._add_scene_object(ColorCube(app, pos=(wheel_x, self._y(0.46), wheel_z), rot=(90, yaw, 0), scale=self._shape((0.045, 0.045, 0.045)), color=dark), tag)
        for i in range(12):
            angle = i * math.tau / 12.0
            px = wheel_x + math.cos(angle) * 0.34 * size
            py = self._y(0.46) + math.sin(angle) * 0.34 * size
            self._add_scene_object(ColorCube(app, pos=(px, py, wheel_z), rot=(0, yaw, math.degrees(angle)), scale=self._shape((0.060, 0.020, 0.030)), color=wood), tag)
            if i % 3 == 0:
                self._add_scene_object(ColorCube(app, pos=(wheel_x + math.cos(angle) * 0.18 * size, self._y(0.46) + math.sin(angle) * 0.18 * size, wheel_z), rot=(0, yaw, math.degrees(angle)), scale=self._shape((0.020, 0.22, 0.020)), color=dark), tag)
        for i in range(5):
            self._box(app, tag, x, z, yaw, -0.92 + i * 0.12, 0.72 - i * 0.05, 0.34 + i * 0.05, (0.055, 0.018, 0.22), water, "water", rot=(0, 8, 0))
        for i in range(6):
            self._add_scene_object(WindStreak(app, pos=(wheel_x + 0.10 * size * math.sin(i), self._y(0.28 + i * 0.055), wheel_z + 0.04 * size), rot=(0, yaw + 12, 0), scale=self._shape((0.040, 0.008, 0.14)), color=(0.86, 0.96, 1.0), travel=(0.04 * size, -0.04 * size, 0.08 * size), speed=0.15 + i * 0.01, phase=i * 0.12, bob=0.02 * size), tag, "water")

    def add_secondary_torii_gate(self, app, pos, yaw):
        x, z = pos
        tag = "secondary_torii"
        red = (0.78, 0.10, 0.07)
        dark_red = (0.42, 0.06, 0.04)
        black = (0.07, 0.05, 0.04)
        for lx in (-0.82, 0.82):
            self._box(app, tag, x, z, yaw, lx, 0.78, 0.0, (0.075, 0.78, 0.075), red)
            self._box(app, tag, x, z, yaw, lx, 1.58, 0.0, (0.11, 0.055, 0.11), black)
        self._box(app, tag, x, z, yaw, 0.0, 1.48, 0.0, (1.10, 0.055, 0.080), dark_red)
        self._box(app, tag, x, z, yaw, 0.0, 1.68, 0.0, (1.32, 0.070, 0.105), red)
        self._box(app, tag, x, z, yaw, 0.0, 1.82, 0.0, (1.44, 0.030, 0.120), black)
        for i in range(9):
            self._box(app, tag, x, z, yaw, 0.0, 0.055, -1.10 - i * 0.42, (0.28, 0.035, 0.16), (0.48, 0.46, 0.40), "terrain", rot=(0, i * 5.0, 0))
        self._lamp(app, tag, x, z, yaw, -1.18, 0.62, -0.42)
        self._lamp(app, tag, x, z, yaw, 1.18, 0.62, -0.42)

    def add_yatai_market_row(self, app, pos, yaw):
        x, z = pos
        tag = "yatai_row"
        cloth = [(0.90, 0.18, 0.12), (0.96, 0.78, 0.22), (0.18, 0.44, 0.76), (0.82, 0.24, 0.52)]
        wood = (0.34, 0.20, 0.10)
        dark = (0.16, 0.09, 0.05)
        for stall in range(4):
            lx = (stall - 1.5) * 0.92
            tint = cloth[stall % len(cloth)]
            self._textured_box(app, tag, x, z, yaw, lx, 0.34, 0.0, (0.36, 0.26, 0.34), "wood", (0.62, 0.42, 0.22))
            self._box(app, tag, x, z, yaw, lx, 0.66, 0.0, (0.42, 0.035, 0.38), tint)
            self._box(app, tag, x, z, yaw, lx, 0.80, -0.10, (0.44, 0.035, 0.32), tint)
            for px in (-0.32, 0.32):
                self._box(app, tag, x, z, yaw, lx + px, 0.52, -0.22, (0.025, 0.52, 0.025), dark)
            self._box(app, tag, x, z, yaw, lx, 0.42, -0.38, (0.30, 0.035, 0.05), (0.82, 0.62, 0.34))
            for item in range(3):
                self._box(app, tag, x, z, yaw, lx - 0.18 + item * 0.18, 0.49, -0.42, (0.050, 0.045, 0.040), (0.92, 0.48, 0.16) if item % 2 else (0.96, 0.86, 0.42))
            self._lamp(app, tag, x, z, yaw, lx + 0.34, 0.80, -0.30, color=(1.0, 0.54, 0.28))
        if self.season_value("seasonal_effect", "") == "summer":
            size = self._scale_value()
            for i in range(10):
                center_x, center_z = self._local_pos(x, z, yaw, -1.6 + i * 0.36, -0.72 + 0.05 * math.sin(i))
                self._add_scene_object(FireflyGlow(app, center=(center_x, self._y(0.72 + 0.05 * (i % 3)), center_z), orbit=(0.10 * size, 0.05 * size, 0.10 * size), scale=(0.018 * size, 0.018 * size, 1.0), color=(1.0, 0.92, 0.36), alpha=0.42, speed=0.10 + i * 0.004, phase=i * 0.11), tag, "atmosphere")

    def add_bathhouse_onsen(self, app, pos, yaw):
        x, z = pos
        tag = "bathhouse_onsen"
        size = self._scale_value()
        wood = (0.38, 0.23, 0.12)
        dark = (0.18, 0.10, 0.05)
        steam = (0.80, 0.90, 0.94)
        self._textured_box(app, tag, x, z, yaw, 0.0, 0.44, 0.0, (0.66, 0.44, 0.52), "wood", (0.62, 0.42, 0.24))
        self._roof(app, tag, x, z, yaw, 0.0, 0.93, 0.0, (0.94, 0.36, 0.74), (0.28, 0.10, 0.07))
        self._box(app, tag, x, z, yaw, 0.0, 0.42, 0.56, (0.24, 0.28, 0.022), (0.92, 0.84, 0.62))
        self._box(app, tag, x, z, yaw, 0.0, 0.22, 0.61, (0.62, 0.08, 0.10), dark)
        pool_x, pool_z = self._local_pos(x, z, yaw, 0.92, -0.28)
        self._add_scene_object(ColorPlane(app, pos=(pool_x, self._local_y_pos(0.040), pool_z), rot=(0, yaw, 0), scale=self._flat_shape((0.56, 1.0, 0.38)), color=(0.34, 0.62, 0.70)), tag, "water")
        for i in range(14):
            angle = i * math.tau / 14.0
            self._add_scene_object(PondRock(app, pos=(pool_x + math.cos(angle) * 0.68 * size, self._y(0.080), pool_z + math.sin(angle) * 0.46 * size), rot=(0, i * 23.0, 0), scale=self._shape((0.16, 0.055, 0.11)), color=(0.40, 0.38, 0.34)), tag, "terrain")
        for i in range(10):
            self._add_scene_object(WindStreak(app, pos=(pool_x + (-0.35 + i * 0.08) * size, self._y(0.32 + 0.06 * (i % 4)), pool_z + 0.08 * size * math.sin(i)), rot=(0, yaw + 84, 0), scale=self._shape((0.050, 0.010, 0.15)), color=steam, travel=(0.04 * size, 0.42 * size, -0.04 * size), speed=0.055 + i * 0.004, phase=i * 0.09, bob=0.10 * size), tag, "atmosphere")
        self._lamp(app, tag, x, z, yaw, -0.74, 0.68, 0.58)

    def add_storage_shed(self, app, pos, yaw):
        x, z = pos
        tag = "storage_shed"
        wood = (0.36, 0.21, 0.10)
        self._textured_box(app, tag, x, z, yaw, 0.0, 0.32, 0.0, (0.50, 0.32, 0.42), "wood", (0.58, 0.38, 0.20))
        self._roof(app, tag, x, z, yaw, 0.0, 0.70, 0.0, (0.70, 0.24, 0.58), (0.35, 0.12, 0.08))
        for side in (-1, 1):
            for i in range(5):
                self._box(app, tag, x, z, yaw, side * 0.64, 0.09 + i * 0.06, -0.22 + (i % 2) * 0.10, (0.24, 0.028, 0.028), wood, rot=(0, 0, 90))
        for i in range(4):
            self._box(app, tag, x, z, yaw, -0.26 + i * 0.18, 0.10, 0.58, (0.075, 0.075, 0.075), (0.42, 0.28, 0.14))
        self._box(app, tag, x, z, yaw, 0.28, 0.22, 0.48, (0.11, 0.16, 0.08), (0.24, 0.14, 0.08))

    def add_viewing_deck(self, app, pos, yaw):
        x, z = pos
        tag = "viewing_deck"
        wood = (0.40, 0.25, 0.12)
        dark = (0.18, 0.10, 0.05)
        self._add_scene_object(TexturedPlane(app, pos=(x, self._y(0.32), z), rot=(0, yaw, 0), scale=self._flat_shape((1.12, 1.0, 0.74)), texture_name="wood", tint=(0.64, 0.44, 0.24), repeat=(3.0, 1.8)), tag)
        for lx in (-1.02, 1.02):
            for lz in (-0.64, 0.64):
                self._box(app, tag, x, z, yaw, lx, 0.18, lz, (0.045, 0.18, 0.045), dark)
                self._box(app, tag, x, z, yaw, lx, 0.70, lz, (0.045, 0.36, 0.045), wood)
        for lz in (-0.72, 0.72):
            self._box(app, tag, x, z, yaw, 0.0, 0.76, lz, (0.98, 0.035, 0.035), wood)
        self._box(app, tag, x, z, yaw, -0.92, 0.76, 0.0, (0.035, 0.035, 0.64), wood)
        self._box(app, tag, x, z, yaw, 0.0, 0.43, -0.88, (0.36, 0.055, 0.12), wood)
        self._box(app, tag, x, z, yaw, 0.0, 0.56, -0.88, (0.26, 0.050, 0.10), (0.72, 0.50, 0.26))
        self._box(app, tag, x, z, yaw, 0.52, 0.62, 0.20, (0.030, 0.26, 0.030), dark)
        self._box(app, tag, x, z, yaw, 0.52, 0.80, 0.20, (0.17, 0.030, 0.030), (0.22, 0.18, 0.12), rot=(0, 24, 0))

    def add_covered_bridge_roof(self, app, pond_radius_scale):
        tag = "covered_bridge"
        size = self._scale_value()
        deck_width = 1.30 * size
        island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]
        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)

        def bridge_point(t):
            inv_t = 1.0 - t
            x = inv_t * inv_t * start[0] + 2.0 * inv_t * t * control[0] + t * t * end[0]
            z = inv_t * inv_t * start[1] + 2.0 * inv_t * t * control[1] + t * t * end[1]
            y = 0.16 + math.sin(math.pi * t) * 0.88
            return x, y, z

        points = [bridge_point(t) for t in (0.12, 0.30, 0.48, 0.66, 0.84)]
        for i, point in enumerate(points):
            if i < len(points) - 1:
                nxt = points[i + 1]
            else:
                nxt = points[i]
                point = points[i - 1]
            dx = nxt[0] - point[0]
            dz = nxt[2] - point[2]
            yaw = math.degrees(math.atan2(dx, dz))
            length = math.sqrt(dx * dx + dz * dz)
            lat_x = -dz / (length + 1e-6)
            lat_z = dx / (length + 1e-6)
            px, py, pz = points[i]
            for side in (-1, 1):
                self._add_scene_object(ColorCube(app, pos=(px + lat_x * side * deck_width * 0.46, py + 0.46 * size, pz + lat_z * side * deck_width * 0.46), rot=(0, yaw, 0), scale=(0.045 * size, 0.44 * size, 0.045 * size), color=(0.24, 0.12, 0.06)), tag)
            self._add_scene_object(ColorCube(app, pos=(px, py + 0.88 * size, pz), rot=(0, yaw, 0), scale=(deck_width * 0.54, 0.040 * size, 0.11 * size), color=(0.22, 0.10, 0.06)), tag)

        for i in range(len(points) - 1):
            a = points[i]
            b = points[i + 1]
            dx = b[0] - a[0]
            dz = b[2] - a[2]
            length = math.sqrt(dx * dx + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            xm = (a[0] + b[0]) * 0.5
            ym = (a[1] + b[1]) * 0.5 + 1.02 * size
            zm = (a[2] + b[2]) * 0.5
            self._add_scene_object(TexturedGableRoof(app, pos=(xm, ym, zm), rot=(0, yaw, 0), scale=(0.96 * size, 0.26 * size, length * 0.58), texture_name="roof", tint=(0.44, 0.12, 0.08), repeat=(1.0, 1.0)), tag)

    def add_rice_field(self, app, pos, yaw):
        x, z = pos
        tag = "rice_field"
        size = self._scale_value()
        effect = self.season_value("seasonal_effect", "spring")
        crop_color = {
            "spring": (0.44, 0.72, 0.26),
            "summer": (0.32, 0.58, 0.18),
            "autumn": (0.88, 0.62, 0.18),
            "winter": self.season_color("winter_snow_color", (0.94, 0.97, 1.0)),
        }.get(effect, (0.44, 0.72, 0.26))
        soil = (0.30, 0.20, 0.12) if effect != "winter" else (0.78, 0.86, 0.92)
        water = (0.26, 0.48, 0.54)
        straw = (0.72, 0.54, 0.22)

        for row in range(2):
            for col in range(3):
                lx = (col - 1) * 0.86
                lz = (row - 0.5) * 0.72
                px, pz = self._local_pos(x, z, yaw, lx, lz)
                self._add_scene_object(
                    ColorPlane(
                        app,
                        pos=(px, self._local_y_pos(0.026), pz),
                        rot=(0, yaw, 0),
                        scale=self._flat_shape((0.36, 1.0, 0.28)),
                        color=soil,
                    ),
                    tag,
                    "terrain",
                )
                if effect in ("spring", "summer"):
                    self._add_scene_object(
                        SunDisc(
                            app,
                            pos=(px, self._local_y_pos(0.034), pz),
                            rot=(90, yaw, 0),
                            scale=(0.38 * size, 0.28 * size, 1.0),
                            color=water,
                            alpha=0.13 if effect == "spring" else 0.08,
                        ),
                        tag,
                        "water",
                    )
                for blade in range(5):
                    offset = -0.24 + blade * 0.12
                    self._box(
                        app,
                        tag,
                        x,
                        z,
                        yaw,
                        lx + offset,
                        0.080 + 0.035 * (effect != "winter"),
                        lz + 0.03 * math.sin(blade + col),
                        (0.012, 0.090 if effect != "winter" else 0.018, 0.012),
                        crop_color,
                        "vegetation",
                        rot=(0, blade * 7.0, 5.0 * math.sin(blade)),
                    )

        for lz in (-1.16, 1.16):
            self._box(app, tag, x, z, yaw, 0.0, 0.08, lz, (1.52, 0.040, 0.040), (0.34, 0.20, 0.10))
        for lx in (-1.72, 1.72):
            self._box(app, tag, x, z, yaw, lx, 0.08, 0.0, (0.040, 0.040, 1.06), (0.34, 0.20, 0.10))
        for lx in (-1.72, 0.0, 1.72):
            for lz in (-1.16, 1.16):
                self._box(app, tag, x, z, yaw, lx, 0.24, lz, (0.035, 0.24, 0.035), (0.30, 0.18, 0.09))

        if effect == "autumn":
            for i in range(6):
                self._box(app, tag, x, z, yaw, -1.08 + i * 0.42, 0.30, 1.42, (0.050, 0.24, 0.030), straw, "vegetation", rot=(0, i * 5.0, 12))
                self._box(app, tag, x, z, yaw, -1.08 + i * 0.42, 0.44, 1.42, (0.095, 0.025, 0.030), (0.84, 0.62, 0.24), "vegetation", rot=(0, i * 9.0, 0))
        elif effect == "winter":
            for i in range(8):
                self._add_disc(
                    app,
                    tag,
                    x,
                    z,
                    yaw,
                    -1.36 + i * 0.38,
                    0.055,
                    -1.35 + 0.10 * math.sin(i),
                    (0.16, 0.08, 1.0),
                    self.season_color("winter_snow_color", (0.94, 0.97, 1.0)),
                    0.18,
                    "terrain",
                )
