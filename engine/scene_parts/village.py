import math

from ..data.scene_config import HOUSE_SPECS
from ..model import (
    AtmosphereSunDisc,
    AuroraBand,
    CloudLayer,
    ColorCube,
    ColorPlane,
    FireflyGlow,
    FloatingPetals,
    FujiPeak,
    FujiSnowcap,
    IceSurface,
    IslandGrass,
    IslandMound,
    NightGlow,
    PondRock,
    RainDrop,
    SakuraBlossomDeep,
    SakuraBlossomLight,
    SakuraCanopyDeep,
    SakuraCanopyLight,
    SakuraWood,
    MoonDisc,
    SkyDome,
    SunDisc,
    TexturedCube,
    TexturedGableRoof,
    TexturedPlane,
    TransitionCube,
    WaterReflection,
    WaterSurface,
    WindStreak,
)


class SceneVillageMixin:
    def add_road_segment(self, app, start, end, width, color, y=0.010):
        dx = end[0] - start[0]
        dz = end[1] - start[1]
        length = math.sqrt(dx * dx + dz * dz)
        if length < 0.001:
            return

        yaw = math.degrees(math.atan2(dx, dz))
        self.add_object(
            TexturedPlane(
                app,
                pos=((start[0] + end[0]) * 0.5, y, (start[1] + end[1]) * 0.5),
                rot=(0, yaw, 0),
                scale=(width * 0.5, 1, length * 0.5),
                texture_name=self.season_value("road_texture", "road"),
                tint=color,
                repeat=(max(1.0, width * 1.6), max(1.0, length * 1.3)),
            )
        )

    def local_house_pos(self, base_x, base_z, yaw, local_x, local_z):
        angle = math.radians(yaw)
        return (
            base_x + local_x * math.cos(angle) + local_z * math.sin(angle),
            base_z - local_x * math.sin(angle) + local_z * math.cos(angle),
        )

    def add_snow_roof_cap(self, app, base_x, base_z, yaw, width, height, depth, roof_base_y, roof_height):
        if not self.is_winter():
            return

        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        slope_angle = math.degrees(math.atan2(roof_height, width * 1.14 + 1e-6))

        for side in (-1, 1):
            cap_x, cap_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                side * width * 0.33,
                0.0,
            )
            add(
                ColorCube(
                    app,
                    pos=(cap_x, roof_base_y + roof_height * 0.54, cap_z),
                    rot=(0, yaw, -side * slope_angle),
                    scale=(width * 0.50, height * 0.045, depth * 1.26),
                    color=snow,
                )
            )

            lip_x, lip_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                side * width * 0.63,
                0.0,
            )
            add(
                ColorCube(
                    app,
                    pos=(lip_x, roof_base_y + roof_height * 0.08, lip_z),
                    rot=(0, yaw, -side * slope_angle),
                    scale=(width * 0.12, height * 0.060, depth * 1.30),
                    color=shadow,
                )
            )

        for local_z in (-depth * 1.20, depth * 1.20):
            eave_x, eave_z = self.local_house_pos(base_x, base_z, yaw, 0.0, local_z)
            add(
                ColorCube(
                    app,
                    pos=(eave_x, roof_base_y + height * 0.05, eave_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.92, height * 0.050, depth * 0.055),
                    color=snow,
                )
            )

    def add_house_volume(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        center_y,
        local_z,
        scale,
        color,
        repeat=(1.30, 1.20),
    ):
        x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            TexturedCube(
                app,
                pos=(x, center_y, z),
                rot=(0, yaw, 0),
                scale=scale,
                texture_name="wall",
                tint=color,
                repeat=repeat,
            )
        )
        return x, z

    def add_house_roof(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        local_z,
        width,
        body_half_height,
        depth,
        roof_base_y,
        roof_height,
        roof_color,
        yaw_offset=0.0,
        overhang_x=1.14,
        overhang_z=1.18,
    ):
        roof_yaw = yaw + yaw_offset
        x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            TexturedGableRoof(
                app,
                pos=(x, roof_base_y, z),
                rot=(0, roof_yaw, 0),
                scale=(width * overhang_x, roof_height, depth * overhang_z),
                texture_name="roof",
                tint=roof_color,
                repeat=(1.2, 1.4),
            )
        )
        self.add_snow_roof_cap(
            app,
            x,
            z,
            roof_yaw,
            width,
            body_half_height,
            depth,
            roof_base_y,
            roof_height,
        )

        ridge_color = (
            self.season_color("winter_snow_color", (0.25, 0.11, 0.08))
            if self.is_winter()
            else (0.25, 0.11, 0.08)
        )
        self.add_object(
            ColorCube(
                app,
                pos=(x, roof_base_y + roof_height + body_half_height * 0.045, z),
                rot=(0, roof_yaw, 0),
                scale=(width * 0.045, body_half_height * 0.035, depth * 1.22),
                color=ridge_color,
            )
        )

    def add_house_window(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        local_z,
        center_y,
        half_width,
        half_height,
        detail_depth,
        trim_color,
        light_color=(0.96, 0.83, 0.45),
    ):
        trim_x, trim_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        pane_x, pane_z = self.local_house_pos(
            base_x,
            base_z,
            yaw,
            local_x,
            local_z + detail_depth * 1.10,
        )
        self.add_object(
            ColorCube(
                app,
                pos=(trim_x, center_y, trim_z),
                rot=(0, yaw, 0),
                scale=(half_width * 1.22, half_height * 1.18, detail_depth * 0.42),
                color=trim_color,
            )
        )
        self.add_object(
            ColorCube(
                app,
                pos=(pane_x, center_y, pane_z),
                rot=(0, yaw, 0),
                scale=(half_width, half_height, detail_depth * 0.78),
                color=light_color,
            )
        )

    def add_house_door(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        local_z,
        center_y,
        half_width,
        half_height,
        detail_depth,
    ):
        door_x, door_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            ColorCube(
                app,
                pos=(door_x, center_y, door_z),
                rot=(0, yaw, 0),
                scale=(half_width, half_height, detail_depth),
                color=(0.22, 0.13, 0.07),
            )
        )

        knob_x, knob_z = self.local_house_pos(
            base_x,
            base_z,
            yaw,
            local_x + half_width * 0.38,
            local_z + detail_depth * 1.45,
        )
        self.add_object(
            ColorCube(
                app,
                pos=(knob_x, center_y + half_height * 0.06, knob_z),
                rot=(0, yaw, 0),
                scale=(half_width * 0.13, half_height * 0.055, detail_depth * 0.55),
                color=(0.86, 0.68, 0.28),
            )
        )

    def add_house_porch(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        local_z,
        width,
        height,
        depth,
        floor_y,
        posts=True,
    ):
        porch_x, porch_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        porch_half_height = height * 0.055
        self.add_object(
            ColorCube(
                app,
                pos=(porch_x, floor_y + porch_half_height, porch_z),
                rot=(0, yaw, 0),
                scale=(width, porch_half_height, depth),
                color=(0.46, 0.43, 0.37),
            )
        )
        if self.is_winter():
            self.add_object(
                ColorCube(
                    app,
                    pos=(porch_x, floor_y + porch_half_height * 2.0 + height * 0.020, porch_z),
                    rot=(0, yaw, 0),
                    scale=(width * 1.04, height * 0.025, depth * 1.08),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

        if posts:
            for side in (-1, 1):
                post_x, post_z = self.local_house_pos(
                    base_x,
                    base_z,
                    yaw,
                    local_x + side * width * 0.82,
                    local_z + depth * 0.46,
                )
                self.add_object(
                    ColorCube(
                        app,
                        pos=(post_x, floor_y + height * 0.40, post_z),
                        rot=(0, yaw, 0),
                        scale=(width * 0.045, height * 0.38, depth * 0.055),
                        color=(0.36, 0.26, 0.18),
                    )
                )

    def add_house_chimney(
        self,
        app,
        base_x,
        base_z,
        yaw,
        local_x,
        local_z,
        center_y,
        scale,
    ):
        chimney_x, chimney_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            ColorCube(
                app,
                pos=(chimney_x, center_y, chimney_z),
                rot=(0, yaw, 0),
                scale=scale,
                color=(0.28, 0.16, 0.12),
            )
        )
        if self.is_winter():
            self.add_object(
                ColorCube(
                    app,
                    pos=(chimney_x, center_y + scale[1] + scale[1] * 0.18, chimney_z),
                    rot=(0, yaw, 0),
                    scale=(scale[0] * 1.18, scale[1] * 0.11, scale[2] * 1.18),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

    def add_two_story_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
    ):
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        detail_depth = max(depth * 0.055, 0.018)
        first_h = height * 0.92
        second_h = height * 0.72
        second_top = floor_y + first_h * 2.0 + second_h * 2.0

        self.add_house_volume(app, base_x, base_z, yaw, 0.0, floor_y + first_h, 0.0, (width, first_h, depth), body_color)
        self.add_house_volume(
            app,
            base_x,
            base_z,
            yaw,
            -width * 0.08,
            floor_y + first_h * 2.0 + second_h,
            -depth * 0.04,
            (width * 0.78, second_h, depth * 0.78),
            tuple(min(1.0, c + 0.05) for c in body_color),
        )
        self.add_house_roof(
            app,
            base_x,
            base_z,
            yaw,
            -width * 0.08,
            -depth * 0.04,
            width * 0.82,
            second_h,
            depth * 0.82,
            second_top,
            height * 0.72,
            roof_color,
        )

        front_z = depth + detail_depth
        self.add_house_door(app, base_x, base_z, yaw, -width * 0.18, front_z, floor_y + first_h * 0.54, width * 0.16, first_h * 0.50, detail_depth)
        for local_x in (width * 0.28, width * 0.58):
            self.add_house_window(app, base_x, base_z, yaw, local_x, front_z, floor_y + first_h * 1.06, width * 0.12, first_h * 0.17, detail_depth, trim_color)
        for local_x in (-width * 0.38, width * 0.18):
            self.add_house_window(app, base_x, base_z, yaw, local_x, front_z, floor_y + first_h * 2.0 + second_h * 1.00, width * 0.12, second_h * 0.18, detail_depth, trim_color)

        balcony_x, balcony_z = self.local_house_pos(base_x, base_z, yaw, -width * 0.10, depth + depth * 0.34)
        self.add_object(
            ColorCube(
                app,
                pos=(balcony_x, floor_y + first_h * 2.0 + second_h * 0.18, balcony_z),
                rot=(0, yaw, 0),
                scale=(width * 0.34, height * 0.035, depth * 0.13),
                color=(0.42, 0.32, 0.23),
            )
        )
        for local_x in (-width * 0.42, width * 0.22):
            rail_x, rail_z = self.local_house_pos(base_x, base_z, yaw, local_x, depth + depth * 0.48)
            self.add_object(
                ColorCube(
                    app,
                    pos=(rail_x, floor_y + first_h * 2.0 + second_h * 0.34, rail_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.026, height * 0.16, depth * 0.025),
                    color=trim_color,
                )
            )

        self.add_house_porch(app, base_x, base_z, yaw, -width * 0.18, depth + depth * 0.44, width * 0.30, height, depth * 0.16, floor_y)
        if has_chimney:
            self.add_house_chimney(app, base_x, base_z, yaw, width * 0.36, -depth * 0.18, second_top + height * 0.48, (width * 0.075, height * 0.30, depth * 0.075))

    def add_l_shaped_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
    ):
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        detail_depth = max(depth * 0.055, 0.018)
        main_h = height * 0.88
        wing_h = height * 0.78

        self.add_house_volume(app, base_x, base_z, yaw, -width * 0.12, floor_y + main_h, 0.0, (width * 0.78, main_h, depth * 0.84), body_color)
        self.add_house_volume(
            app,
            base_x,
            base_z,
            yaw,
            width * 0.58,
            floor_y + wing_h,
            -depth * 0.20,
            (width * 0.45, wing_h, depth * 1.05),
            tuple(max(0.0, c - 0.04) for c in body_color),
            repeat=(1.0, 1.3),
        )
        self.add_house_roof(app, base_x, base_z, yaw, -width * 0.12, 0.0, width * 0.84, main_h, depth * 0.90, floor_y + main_h * 2.0, height * 0.78, roof_color)
        self.add_house_roof(app, base_x, base_z, yaw, width * 0.58, -depth * 0.20, width * 0.50, wing_h, depth * 1.10, floor_y + wing_h * 2.0, height * 0.55, tuple(min(1.0, c + 0.04) for c in roof_color), yaw_offset=90.0)

        front_z = depth * 0.86 + detail_depth
        self.add_house_door(app, base_x, base_z, yaw, -width * 0.36, front_z, floor_y + main_h * 0.55, width * 0.14, main_h * 0.48, detail_depth)
        for local_x in (-width * 0.02, width * 0.54, width * 0.82):
            self.add_house_window(app, base_x, base_z, yaw, local_x, front_z, floor_y + height * 0.95, width * 0.105, height * 0.16, detail_depth, trim_color)

        patio_x, patio_z = self.local_house_pos(base_x, base_z, yaw, width * 0.34, depth * 1.08)
        self.add_object(
            ColorCube(
                app,
                pos=(patio_x, floor_y + height * 0.040, patio_z),
                rot=(0, yaw, 0),
                scale=(width * 0.46, height * 0.040, depth * 0.24),
                color=(0.50, 0.46, 0.38),
            )
        )
        if has_chimney:
            self.add_house_chimney(app, base_x, base_z, yaw, -width * 0.46, -depth * 0.14, floor_y + main_h * 2.0 + height * 0.50, (width * 0.075, height * 0.27, depth * 0.075))

    def add_split_level_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
    ):
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        detail_depth = max(depth * 0.055, 0.018)
        low_h = height * 0.68
        tall_h = height * 1.12
        garage_h = height * 0.46

        self.add_house_volume(app, base_x, base_z, yaw, width * 0.12, floor_y + low_h, 0.0, (width * 0.78, low_h, depth * 0.86), body_color)
        self.add_house_volume(app, base_x, base_z, yaw, -width * 0.55, floor_y + tall_h, -depth * 0.03, (width * 0.42, tall_h, depth * 0.62), tuple(min(1.0, c + 0.06) for c in body_color))
        self.add_house_volume(app, base_x, base_z, yaw, width * 0.64, floor_y + garage_h, depth * 0.06, (width * 0.36, garage_h, depth * 0.56), tuple(max(0.0, c - 0.08) for c in body_color))

        self.add_house_roof(app, base_x, base_z, yaw, width * 0.12, 0.0, width * 0.84, low_h, depth * 0.92, floor_y + low_h * 2.0, height * 0.54, roof_color)
        self.add_house_roof(app, base_x, base_z, yaw, -width * 0.55, -depth * 0.03, width * 0.48, tall_h, depth * 0.68, floor_y + tall_h * 2.0, height * 0.66, tuple(min(1.0, c + 0.03) for c in roof_color))

        garage_x, garage_z = self.local_house_pos(base_x, base_z, yaw, width * 0.64, depth * 0.06)
        self.add_object(
            ColorCube(
                app,
                pos=(garage_x, floor_y + garage_h * 2.0 + height * 0.060, garage_z),
                rot=(0, yaw, 0),
                scale=(width * 0.42, height * 0.060, depth * 0.62),
                color=roof_color,
            )
        )
        self.add_house_door(app, base_x, base_z, yaw, -width * 0.06, depth * 0.88 + detail_depth, floor_y + low_h * 0.56, width * 0.13, low_h * 0.48, detail_depth)
        self.add_house_window(app, base_x, base_z, yaw, width * 0.32, depth * 0.88 + detail_depth, floor_y + low_h * 0.98, width * 0.12, low_h * 0.18, detail_depth, trim_color)
        for y_mul in (0.62, 1.26):
            self.add_house_window(app, base_x, base_z, yaw, -width * 0.55, depth * 0.66 + detail_depth, floor_y + tall_h * y_mul, width * 0.10, tall_h * 0.12, detail_depth, trim_color)

        garage_front_x, garage_front_z = self.local_house_pos(base_x, base_z, yaw, width * 0.64, depth * 0.62 + detail_depth)
        self.add_object(
            ColorCube(
                app,
                pos=(garage_front_x, floor_y + garage_h * 0.74, garage_front_z),
                rot=(0, yaw, 0),
                scale=(width * 0.24, garage_h * 0.42, detail_depth),
                color=(0.34, 0.28, 0.22),
            )
        )
        if has_chimney:
            self.add_house_chimney(app, base_x, base_z, yaw, -width * 0.68, -depth * 0.18, floor_y + tall_h * 2.0 + height * 0.44, (width * 0.070, height * 0.26, depth * 0.070))

    def add_tower_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
    ):
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        detail_depth = max(depth * 0.055, 0.018)
        tower_h = height * 1.34
        annex_h = height * 0.62

        self.add_house_volume(app, base_x, base_z, yaw, -width * 0.15, floor_y + tower_h, 0.0, (width * 0.52, tower_h, depth * 0.62), body_color)
        self.add_house_volume(app, base_x, base_z, yaw, width * 0.48, floor_y + annex_h, depth * 0.05, (width * 0.48, annex_h, depth * 0.72), tuple(max(0.0, c - 0.05) for c in body_color))

        self.add_house_roof(app, base_x, base_z, yaw, -width * 0.15, 0.0, width * 0.58, tower_h, depth * 0.68, floor_y + tower_h * 2.0, height * 0.72, roof_color)
        self.add_house_roof(app, base_x, base_z, yaw, width * 0.48, depth * 0.05, width * 0.54, annex_h, depth * 0.78, floor_y + annex_h * 2.0, height * 0.42, tuple(min(1.0, c + 0.05) for c in roof_color), yaw_offset=90.0)

        self.add_house_door(app, base_x, base_z, yaw, width * 0.44, depth * 0.78 + detail_depth, floor_y + annex_h * 0.58, width * 0.12, annex_h * 0.48, detail_depth)
        for y_mul in (0.48, 0.94, 1.40):
            self.add_house_window(app, base_x, base_z, yaw, -width * 0.15, depth * 0.64 + detail_depth, floor_y + tower_h * y_mul, width * 0.095, tower_h * 0.09, detail_depth, trim_color)
        self.add_house_window(app, base_x, base_z, yaw, width * 0.70, depth * 0.78 + detail_depth, floor_y + annex_h * 1.02, width * 0.10, annex_h * 0.16, detail_depth, trim_color)

        balcony_x, balcony_z = self.local_house_pos(base_x, base_z, yaw, -width * 0.15, depth * 0.82)
        self.add_object(
            ColorCube(
                app,
                pos=(balcony_x, floor_y + tower_h * 1.18, balcony_z),
                rot=(0, yaw, 0),
                scale=(width * 0.20, height * 0.028, depth * 0.10),
                color=(0.38, 0.28, 0.18),
            )
        )
        if has_chimney:
            self.add_house_chimney(app, base_x, base_z, yaw, width * 0.62, -depth * 0.16, floor_y + annex_h * 2.0 + height * 0.34, (width * 0.060, height * 0.22, depth * 0.060))

    def add_wide_veranda_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
    ):
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        detail_depth = max(depth * 0.055, 0.018)
        house_h = height * 0.78

        self.add_house_volume(app, base_x, base_z, yaw, 0.0, floor_y + house_h, 0.0, (width * 1.10, house_h, depth * 0.78), body_color)
        self.add_house_roof(app, base_x, base_z, yaw, 0.0, 0.0, width * 1.18, house_h, depth * 0.88, floor_y + house_h * 2.0, height * 0.58, roof_color)
        self.add_house_porch(app, base_x, base_z, yaw, 0.0, depth * 0.82, width * 0.78, height, depth * 0.18, floor_y, posts=True)

        for local_x in (-width * 0.62, width * 0.62):
            self.add_house_window(app, base_x, base_z, yaw, local_x, depth * 0.78 + detail_depth, floor_y + house_h * 1.00, width * 0.13, house_h * 0.18, detail_depth, trim_color)
        self.add_house_door(app, base_x, base_z, yaw, 0.0, depth * 0.78 + detail_depth, floor_y + house_h * 0.55, width * 0.15, house_h * 0.48, detail_depth)

        for local_x in (-width * 0.52, -width * 0.26, width * 0.26, width * 0.52):
            rail_x, rail_z = self.local_house_pos(base_x, base_z, yaw, local_x, depth * 1.01)
            self.add_object(
                ColorCube(
                    app,
                    pos=(rail_x, floor_y + height * 0.30, rail_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.020, height * 0.20, depth * 0.020),
                    color=trim_color,
                )
            )
        if has_chimney:
            self.add_house_chimney(app, base_x, base_z, yaw, -width * 0.48, -depth * 0.12, floor_y + house_h * 2.0 + height * 0.36, (width * 0.070, height * 0.24, depth * 0.070))

    def add_house(
        self,
        app,
        pos,
        yaw,
        body_scale,
        body_color,
        roof_color,
        trim_color,
        has_chimney=True,
        variant="cottage",
    ):
        if variant == "two_story":
            self.add_two_story_house(app, pos, yaw, body_scale, body_color, roof_color, trim_color, has_chimney)
            return
        if variant == "l_shape":
            self.add_l_shaped_house(app, pos, yaw, body_scale, body_color, roof_color, trim_color, has_chimney)
            return
        if variant == "split_level":
            self.add_split_level_house(app, pos, yaw, body_scale, body_color, roof_color, trim_color, has_chimney)
            return
        if variant == "tower":
            self.add_tower_house(app, pos, yaw, body_scale, body_color, roof_color, trim_color, has_chimney)
            return
        if variant == "wide_veranda":
            self.add_wide_veranda_house(app, pos, yaw, body_scale, body_color, roof_color, trim_color, has_chimney)
            return

        add = self.add_object
        base_x, base_z = pos
        width, height, depth = body_scale
        floor_y = 0.025
        body_center_y = floor_y + height
        roof_base_y = floor_y + height * 2.0
        roof_height = height * 1.03
        detail_depth = max(depth * 0.055, 0.018)
        trim_depth = max(depth * 0.020, 0.008)

        add(
            TexturedCube(
                app,
                pos=(base_x, body_center_y, base_z),
                rot=(0, yaw, 0),
                scale=(width, height, depth),
                texture_name="wall",
                tint=body_color,
                repeat=(1.35, 1.20),
            )
        )

        add(
            TexturedGableRoof(
                app,
                pos=(base_x, roof_base_y, base_z),
                rot=(0, yaw, 0),
                scale=(width * 1.14, roof_height, depth * 1.18),
                texture_name="roof",
                tint=roof_color,
                repeat=(1.2, 1.4),
            )
        )
        self.add_snow_roof_cap(
            app,
            base_x,
            base_z,
            yaw,
            width,
            height,
            depth,
            roof_base_y,
            roof_height,
        )

        ridge_x, ridge_z = self.local_house_pos(base_x, base_z, yaw, 0.0, 0.0)
        add(
            ColorCube(
                app,
                pos=(ridge_x, roof_base_y + roof_height + height * 0.045, ridge_z),
                rot=(0, yaw, 0),
                scale=(width * 0.045, height * 0.035, depth * 1.22),
                color=self.season_color("winter_snow_color", (0.25, 0.11, 0.08))
                if self.is_winter()
                else (0.25, 0.11, 0.08),
            )
        )

        door_x, door_z = self.local_house_pos(
            base_x,
            base_z,
            yaw,
            0.0,
            depth + detail_depth,
        )
        add(
            ColorCube(
                app,
                pos=(door_x, floor_y + height * 0.52, door_z),
                rot=(0, yaw, 0),
                scale=(width * 0.20, height * 0.52, detail_depth),
                color=(0.22, 0.13, 0.07),
            )
        )

        knob_x, knob_z = self.local_house_pos(
            base_x,
            base_z,
            yaw,
            width * 0.075,
            depth + detail_depth * 2.3,
        )
        add(
            ColorCube(
                app,
                pos=(knob_x, floor_y + height * 0.55, knob_z),
                rot=(0, yaw, 0),
                scale=(width * 0.026, height * 0.028, detail_depth * 0.55),
                color=(0.86, 0.68, 0.28),
            )
        )

        for local_x in (-width * 0.50, width * 0.50):
            window_x, window_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                local_x,
                depth + detail_depth * 1.15,
            )
            add(
                ColorCube(
                    app,
                    pos=(window_x, floor_y + height * 1.08, window_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.15, height * 0.20, detail_depth * 0.82),
                    color=(0.96, 0.83, 0.45),
                )
            )

            trim_x, trim_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                local_x,
                depth + trim_depth,
            )
            add(
                ColorCube(
                    app,
                    pos=(trim_x, floor_y + height * 1.08, trim_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.18, height * 0.23, trim_depth),
                    color=trim_color,
                )
            )

        for side in (-1, 1):
            side_x, side_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                side * (width + width * 0.040),
                -depth * 0.10,
            )
            add(
                ColorCube(
                    app,
                    pos=(side_x, floor_y + height * 1.02, side_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.028, height * 0.18, depth * 0.18),
                    color=(0.92, 0.76, 0.42),
                )
            )

        porch_x, porch_z = self.local_house_pos(
            base_x,
            base_z,
            yaw,
            0.0,
            depth + depth * 0.48,
        )
        porch_half_height = height * 0.055
        add(
            ColorCube(
                app,
                pos=(porch_x, floor_y + porch_half_height, porch_z),
                rot=(0, yaw, 0),
                scale=(width * 0.42, porch_half_height, depth * 0.22),
                color=(0.46, 0.43, 0.37),
            )
        )
        if self.is_winter():
            add(
                ColorCube(
                    app,
                    pos=(porch_x, floor_y + porch_half_height * 2.0 + height * 0.020, porch_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.44, height * 0.025, depth * 0.24),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

        if has_chimney:
            chimney_x, chimney_z = self.local_house_pos(
                base_x,
                base_z,
                yaw,
                -width * 0.43,
                -depth * 0.22,
            )
            add(
                ColorCube(
                    app,
                    pos=(chimney_x, roof_base_y + roof_height * 0.70, chimney_z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.095, height * 0.32, depth * 0.090),
                    color=(0.28, 0.16, 0.12),
                )
            )
            if self.is_winter():
                add(
                    ColorCube(
                        app,
                        pos=(chimney_x, roof_base_y + roof_height * 1.04, chimney_z),
                        rot=(0, yaw, 0),
                        scale=(width * 0.115, height * 0.035, depth * 0.110),
                        color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                    )
                )

    def add_house_porch_light(self, app, base_x, base_z, yaw, width, height, depth, variant):
        add = self.add_object
        front_z = depth + depth * (0.70 if variant in ("cottage", "wide_veranda") else 0.58)
        lamp_y = 0.55 + height * 0.42
        fixture_x, fixture_z = self.local_house_pos(base_x, base_z, yaw, -width * 0.24, front_z)
        glow_x, glow_z = self.local_house_pos(base_x, base_z, yaw, 0.0, front_z + depth * 0.16)

        add(
            ColorCube(
                app,
                pos=(fixture_x, lamp_y, fixture_z),
                rot=(0, yaw, 0),
                scale=(width * 0.040, height * 0.040, depth * 0.030),
                color=(1.00, 0.66, 0.34),
            )
        )
        add(
            NightGlow(
                app,
                pos=(glow_x, lamp_y, glow_z),
                rot=(0, yaw, 0),
                scale=(0.30 + width * 0.10, 0.30 + height * 0.11, 1.0),
                color=(1.00, 0.62, 0.32),
                alpha=0.34 if variant in ("cottage", "wide_veranda") else 0.28,
                pulse=0.035,
            )
        )

    def add_local_cube(self, app, base_x, base_z, yaw, local_x, y, local_z, scale, color, rot=(0, 0, 0)):
        x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            ColorCube(
                app,
                pos=(x, y, z),
                rot=(rot[0], yaw + rot[1], rot[2]),
                scale=scale,
                color=color,
            )
        )
        return x, z

    def add_house_yard_details(self, app, idx, base_x, base_z, yaw, width, height, depth):
        add = self.add_object
        wood = (0.36, 0.22, 0.12)
        dark_wood = (0.22, 0.13, 0.07)
        path_color = self.season_color("garden_path_color", (0.66, 0.58, 0.42))
        hedge = self.season_color("garden_hedge_color", (0.24, 0.42, 0.18))
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
        bed_color = self.season_color("garden_bed_color", (0.24, 0.40, 0.18))

        side_x = width * 1.12
        fence_z0 = depth * 0.20
        fence_step = 0.46 + depth * 0.18

        # Pagar rendah hanya di halaman depan, jadi rumah tetap terbuka ke jalan.
        for side in (-1, 1):
            for post_idx in range(4):
                local_z = fence_z0 + post_idx * fence_step
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    side * side_x,
                    0.22,
                    local_z,
                    (0.030, 0.22, 0.030),
                    dark_wood,
                )

            for rail_idx in range(3):
                rail_z = fence_z0 + rail_idx * fence_step + fence_step * 0.5
                rail_len = fence_step * 0.52
                for rail_y in (0.24, 0.39):
                    self.add_local_cube(
                        app,
                        base_x,
                        base_z,
                        yaw,
                        side * side_x,
                        rail_y,
                        rail_z,
                        (0.022, 0.016, rail_len),
                        wood,
                    )

            if self.is_winter():
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    side * side_x,
                    0.465,
                    fence_z0 + fence_step * 1.5,
                    (0.034, 0.014, fence_step * 1.65),
                    snow,
                )

        front_z = fence_z0 + fence_step * 3.0 + 0.10
        for side in (-1, 1):
            self.add_local_cube(
                app,
                base_x,
                base_z,
                yaw,
                side * width * 0.72,
                0.25,
                front_z,
                (width * 0.31, 0.018, 0.022),
                wood,
            )
            self.add_local_cube(
                app,
                base_x,
                base_z,
                yaw,
                side * width * 0.72,
                0.40,
                front_z,
                (width * 0.31, 0.016, 0.022),
                wood,
            )

        for step_idx in range(5):
            local_z = depth * 0.72 + step_idx * 0.32
            local_x = 0.035 * math.sin(idx + step_idx * 1.7)
            x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
            add(
                PondRock(
                    app,
                    pos=(x, 0.034 + 0.003 * (step_idx % 2), z),
                    rot=(0, yaw + step_idx * 7.0, 0),
                    scale=(0.145, 0.022, 0.095),
                    color=path_color if not self.is_winter() else (0.78, 0.84, 0.88),
                )
            )

        shrub_specs = [
            (-width * 0.82, depth * 0.62, 0.94),
            (width * 0.82, depth * 0.78, 0.86),
            (-width * 0.64, depth * 1.52, 0.76),
            (width * 0.66, depth * 1.68, 0.82),
        ]
        for shrub_idx, (local_x, local_z, size) in enumerate(shrub_specs):
            x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
            color = snow if self.is_winter() and shrub_idx % 2 == 0 else hedge
            add(
                PondRock(
                    app,
                    pos=(x, 0.115, z),
                    rot=(0, yaw + shrub_idx * 31.0, 0),
                    scale=(0.20 * size, 0.105 * size, 0.16 * size),
                    color=color,
                )
            )

        if self.season_value("garden_flowers_enabled", True):
            flower_palettes = [
                ((1.00, 0.72, 0.88), (0.96, 0.42, 0.64), (0.98, 0.82, 0.26)),
                ((0.98, 0.88, 0.44), (1.00, 0.58, 0.22), (0.58, 0.34, 0.10)),
                ((0.74, 0.86, 1.00), (0.50, 0.60, 0.94), (0.98, 0.84, 0.34)),
            ]
            outer, inner, center = flower_palettes[idx % len(flower_palettes)]
            for flower_idx in range(4):
                side = -1 if flower_idx < 2 else 1
                local_x = side * (width * 0.55 + 0.06 * (flower_idx % 2))
                local_z = depth * 1.04 + 0.26 * (flower_idx % 2)
                x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
                self.add_garden_flower(
                    app,
                    (x, z),
                    outer,
                    inner,
                    center,
                    scale=0.72 + 0.06 * (idx % 3),
                    spin=math.radians(yaw + flower_idx * 38.0),
                )

        detail_type = idx % 4
        if detail_type == 0:
            bench_x, bench_z = self.local_house_pos(base_x, base_z, yaw, -width * 0.52, depth * 1.54)
            self.add_garden_bench(app, (bench_x, bench_z), yaw + 8.0, scale=0.62)
        elif detail_type == 1:
            bed_x, bed_z = self.local_house_pos(base_x, base_z, yaw, width * 0.54, depth * 1.48)
            add(
                PondRock(
                    app,
                    pos=(bed_x, 0.050, bed_z),
                    rot=(0, yaw - 12.0, 0),
                    scale=(0.32, 0.040, 0.20),
                    color=snow if self.is_winter() else bed_color,
                )
            )
            if not self.is_winter():
                for sprout_idx in range(5):
                    sprout_x = width * 0.54 + (sprout_idx - 2) * 0.085
                    sprout_z = depth * 1.48 + 0.05 * math.sin(sprout_idx)
                    self.add_local_cube(
                        app,
                        base_x,
                        base_z,
                        yaw,
                        sprout_x,
                        0.105,
                        sprout_z,
                        (0.010, 0.055, 0.008),
                        (0.22, 0.50, 0.17),
                        rot=(12, sprout_idx * 16.0, 18),
                    )
        elif detail_type == 2:
            crate_specs = [
                (-width * 0.58, depth * 1.20, (0.13, 0.10, 0.12), (0.45, 0.27, 0.12)),
                (-width * 0.38, depth * 1.26, (0.11, 0.08, 0.10), (0.56, 0.35, 0.15)),
                (-width * 0.49, depth * 1.08, (0.085, 0.07, 0.085), (0.30, 0.18, 0.09)),
            ]
            for local_x, local_z, scale, color in crate_specs:
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    local_x,
                    scale[1],
                    local_z,
                    scale,
                    color,
                    rot=(0, idx * 9.0, 0),
                )
        else:
            post_z = depth * 1.45
            for side in (-1, 1):
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    side * width * 0.58,
                    0.43,
                    post_z,
                    (0.022, 0.43, 0.022),
                    dark_wood,
                )
            self.add_local_cube(
                app,
                base_x,
                base_z,
                yaw,
                0.0,
                0.82,
                post_z,
                (width * 0.58, 0.010, 0.010),
                (0.18, 0.13, 0.09),
            )
            cloth_colors = [
                self.season_color("floating_petal_color", (1.00, 0.64, 0.84)),
                self.season_color("transition_secondary_color", (0.62, 0.86, 0.54)),
                (0.92, 0.82, 0.58),
            ]
            for cloth_idx, cloth_color in enumerate(cloth_colors):
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    -width * 0.24 + cloth_idx * width * 0.22,
                    0.66,
                    post_z,
                    (0.060, 0.13, 0.012),
                    snow if self.is_winter() and cloth_idx == 1 else cloth_color,
                )

    def add_outer_grove(self, app):
        add = self.add_object
        trunk = self.season_color("sakura_wood_color", (0.25, 0.15, 0.08))
        deep = self.season_color("sakura_canopy_deep_color", (0.30, 0.48, 0.22))
        light = self.season_color("sakura_canopy_light_color", (0.50, 0.66, 0.30))
        blossom = self.season_color("sakura_blossom_light_color", (0.95, 0.78, 0.90))
        hedge = self.season_color("garden_hedge_color", (0.24, 0.42, 0.18))
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
        road_exits = (0.0, 90.0, 180.0, 270.0)

        for i in range(30):
            angle_deg = (i * 360.0 / 30.0 + 4.5 * math.sin(i * 1.6)) % 360.0
            gap = min(abs(((angle_deg - road + 180.0) % 360.0) - 180.0) for road in road_exits)
            if gap < 8.0:
                continue

            angle = math.radians(angle_deg)
            radius = 15.6 + 2.35 * (0.5 + 0.5 * math.sin(i * 2.13))
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            tree_scale = 0.24 + 0.08 * (0.5 + 0.5 * math.cos(i * 1.31))
            tree_pos = (x, 0.030, z)
            tree_scale_vec = (tree_scale, tree_scale, tree_scale)

            add(SakuraWood(app, pos=tree_pos, rot=(0, angle_deg + 8.0 * math.sin(i), 0), scale=tree_scale_vec, color=trunk))
            add(SakuraCanopyDeep(app, pos=tree_pos, rot=(0, angle_deg, 0), scale=tree_scale_vec, color=deep))
            add(SakuraCanopyLight(app, pos=tree_pos, rot=(0, angle_deg + 12.0, 0), scale=tree_scale_vec, color=light))
            if i % 3 != 1:
                add(SakuraBlossomLight(app, pos=tree_pos, rot=(0, angle_deg + 24.0, 0), scale=tree_scale_vec, color=blossom))

            if self.is_winter():
                add(
                    PondRock(
                        app,
                        pos=(x, 0.070, z),
                        rot=(0, angle_deg, 0),
                        scale=(0.33, 0.045, 0.24),
                        color=snow,
                    )
                )

        for i in range(72):
            angle_deg = (i * 360.0 / 72.0 + 2.2 * math.sin(i * 0.9)) % 360.0
            gap = min(abs(((angle_deg - road + 180.0) % 360.0) - 180.0) for road in road_exits)
            if gap < 5.0 and i % 2 == 0:
                continue

            angle = math.radians(angle_deg)
            radius = 13.9 + 4.3 * ((i * 37) % 100) / 100.0
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            size = 0.78 + 0.22 * math.sin(i * 1.7) ** 2
            color = snow if self.is_winter() and i % 3 == 0 else hedge

            add(
                PondRock(
                    app,
                    pos=(x, 0.115 + 0.012 * (i % 3), z),
                    rot=(0, angle_deg + i * 11.0, 0),
                    scale=(0.21 * size, 0.095 * size, 0.17 * size),
                    color=color,
                )
            )

    def add_village_activity_details(self, app, road_radius, road_width):
        add = self.add_object
        wood = (0.36, 0.21, 0.11)
        dark_wood = (0.22, 0.13, 0.07)
        path_color = self.season_color("garden_path_color", (0.66, 0.58, 0.42))
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))

        for angle_deg in (28, 86, 150, 334):
            angle = math.radians(angle_deg)
            x = math.cos(angle) * (road_radius + road_width * 1.18)
            z = math.sin(angle) * (road_radius + road_width * 1.18)
            yaw = math.degrees(math.atan2(-x, -z))
            self.add_garden_bench(app, (x, z), yaw, scale=0.72)

        for angle_deg in (2, 88, 182, 272):
            angle = math.radians(angle_deg)
            x = math.cos(angle) * (road_radius + road_width * 0.98)
            z = math.sin(angle) * (road_radius + road_width * 0.98)
            yaw = angle_deg + 90.0
            add(ColorCube(app, pos=(x, 0.43, z), rot=(0, yaw, 0), scale=(0.030, 0.43, 0.030), color=dark_wood))
            add(ColorCube(app, pos=(x, 0.72, z), rot=(0, yaw, 0), scale=(0.28, 0.065, 0.030), color=wood))
            add(ColorCube(app, pos=(x, 0.56, z), rot=(0, yaw + 90.0, 0), scale=(0.23, 0.050, 0.026), color=wood))
            if self.is_winter():
                add(ColorCube(app, pos=(x, 0.800, z), rot=(0, yaw, 0), scale=(0.30, 0.016, 0.040), color=snow))

        stall_specs = [
            (-1.70, 10.45, 8.0),
            (1.85, -10.25, 188.0),
        ]
        canopy_colors = [
            self.season_color("transition_color", (0.92, 0.42, 0.14)),
            self.season_color("transition_secondary_color", (0.62, 0.82, 0.44)),
        ]
        for stall_idx, (base_x, base_z, yaw) in enumerate(stall_specs):
            canopy = canopy_colors[stall_idx % len(canopy_colors)]
            self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.35, 0.0, (0.54, 0.055, 0.25), wood)
            self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.91, 0.0, (0.70, 0.055, 0.37), canopy)
            if self.is_winter():
                self.add_local_cube(app, base_x, base_z, yaw, 0.0, 0.975, 0.0, (0.72, 0.018, 0.39), snow)

            for local_x in (-0.46, 0.46):
                for local_z in (-0.18, 0.18):
                    self.add_local_cube(app, base_x, base_z, yaw, local_x, 0.45, local_z, (0.026, 0.45, 0.026), dark_wood)

            for crate_idx, local_x in enumerate((-0.32, -0.10, 0.18, 0.36)):
                crate_color = (0.52, 0.31, 0.12) if crate_idx % 2 else (0.42, 0.25, 0.10)
                self.add_local_cube(
                    app,
                    base_x,
                    base_z,
                    yaw,
                    local_x,
                    0.115,
                    0.43 + 0.04 * math.sin(crate_idx),
                    (0.105, 0.105, 0.095),
                    crate_color,
                    rot=(0, crate_idx * 8.0, 0),
                )
                if not self.is_winter() and crate_idx % 2 == 0:
                    item_x, item_z = self.local_house_pos(base_x, base_z, yaw, local_x, 0.55)
                    add(
                        PondRock(
                            app,
                            pos=(item_x, 0.245, item_z),
                            rot=(0, yaw + crate_idx * 19.0, 0),
                            scale=(0.050, 0.035, 0.040),
                            color=canopy,
                        )
                    )

            self.add_lantern_post(
                app,
                self.local_house_pos(base_x, base_z, yaw, 0.64, 0.35),
                yaw=yaw,
                height=0.62,
                glow_scale=0.28,
                glow_alpha=0.42,
            )

        well_x, well_z = (-8.35, 4.95)
        for stone_idx in range(12):
            angle = stone_idx * math.tau / 12.0
            add(
                PondRock(
                    app,
                    pos=(well_x + math.cos(angle) * 0.42, 0.080, well_z + math.sin(angle) * 0.42),
                    rot=(0, stone_idx * 31.0, 0),
                    scale=(0.12, 0.060, 0.10),
                    color=(0.46, 0.45, 0.40) if not self.is_winter() else snow,
                )
            )
        add(
            WaterSurface(
                app,
                pos=(well_x, 0.105, well_z),
                scale=(0.064, 1.0, 0.064),
                color=self.season_color("water_color", (0.16, 0.40, 0.56)),
            )
        )
        for local_x in (-0.34, 0.34):
            self.add_local_cube(app, well_x, well_z, 0.0, local_x, 0.70, 0.0, (0.030, 0.56, 0.030), dark_wood)
        self.add_local_cube(app, well_x, well_z, 0.0, 0.0, 1.18, 0.0, (0.54, 0.060, 0.24), wood)
        self.add_local_cube(app, well_x, well_z, 0.0, 0.0, 1.28, 0.0, (0.42, 0.055, 0.20), path_color if not self.is_winter() else snow)

    def add_settlement(self, app, pond_radius_scale):
        add = self.add_object
        road_radius = 8.55
        road_width = 0.90
        road_color = self.season_color("road_color", (0.36, 0.34, 0.30))
        lane_color = self.season_color("lane_color", (0.43, 0.38, 0.30))
        edge_color = self.season_color("road_edge_color", (0.51, 0.49, 0.43))

        ring_segments = 64
        for i in range(ring_segments):
            a0 = 2.0 * math.pi * i / ring_segments
            a1 = 2.0 * math.pi * (i + 1) / ring_segments
            start = (math.cos(a0) * road_radius, math.sin(a0) * road_radius)
            end = (math.cos(a1) * road_radius, math.sin(a1) * road_radius)
            self.add_road_segment(app, start, end, road_width, road_color)

        # Jalan utama dan beberapa cabang keluar dari pemukiman.
        self.add_road_segment(app, (0.0, road_radius + 0.20), (0.0, 18.5), 1.45, road_color)
        self.add_road_segment(app, (road_radius + 0.20, 0.0), (17.7, 1.45), 1.14, road_color)
        self.add_road_segment(app, (-road_radius - 0.20, 0.0), (-17.7, -1.20), 1.14, road_color)
        self.add_road_segment(app, (0.0, -road_radius - 0.20), (-1.65, -18.5), 1.14, road_color)

        bridge_start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        bridge_angle = math.atan2(bridge_start[1], bridge_start[0])
        bridge_ring = (
            math.cos(bridge_angle) * road_radius,
            math.sin(bridge_angle) * road_radius,
        )
        self.add_road_segment(app, bridge_start, bridge_ring, 0.92, lane_color)

        for i in range(48):
            angle = 2.0 * math.pi * i / 48.0
            for side in (-1, 1):
                radius = road_radius + side * road_width * 0.62
                add(
                    PondRock(
                        app,
                        pos=(math.cos(angle) * radius, 0.040, math.sin(angle) * radius),
                        rot=(0, i * 19.0 + side * 11.0, 0),
                        scale=(0.15, 0.052, 0.19),
                        color=edge_color,
                    )
                )

        self.add_beautiful_garden(app, pond_radius_scale, road_radius, road_width)

        for idx, (angle_deg, radius, body_scale, body_color, roof_color, trim_color, yaw_offset, variant) in enumerate(HOUSE_SPECS):
            angle = math.radians(angle_deg)
            radial_x = math.cos(angle)
            radial_z = math.sin(angle)
            x = radial_x * radius
            z = radial_z * radius

            front_x = -radial_x
            front_z = -radial_z
            yaw = math.degrees(math.atan2(front_x, front_z)) + yaw_offset
            width, height, depth = body_scale

            road_start = (
                radial_x * (road_radius + road_width * 0.58),
                radial_z * (road_radius + road_width * 0.58),
            )
            road_end = (
                radial_x * (radius - depth - 0.30),
                radial_z * (radius - depth - 0.30),
            )
            self.add_road_segment(app, road_start, road_end, 0.60, lane_color, y=0.012)

            yard_x = radial_x * (radius - depth * 0.15)
            yard_z = radial_z * (radius - depth * 0.15)
            add(
                TexturedPlane(
                    app,
                    pos=(yard_x, 0.008, yard_z),
                    rot=(0, yaw, 0),
                    scale=(width * 1.65, 1, depth * 1.85),
                    texture_name=self.season_value("yard_texture", "grass"),
                    tint=self.season_color("yard_color", (0.31, 0.39, 0.22)),
                    repeat=(2.2, 2.0),
                )
            )

            self.add_house(
                app,
                (x, z),
                yaw,
                body_scale,
                body_color,
                roof_color,
                trim_color,
                has_chimney=idx % 3 != 1,
                variant=variant,
            )
            self.add_house_porch_light(app, x, z, yaw, width, height, depth, variant)
            self.add_house_yard_details(app, idx, x, z, yaw, width, height, depth)

        self.add_village_activity_details(app, road_radius, road_width)
        self.add_outer_grove(app)

    def add_bridge(self, app):
        add = self.add_object

        deck_base_color = (0.46, 0.28, 0.14)
        deck_highlight = (0.60, 0.38, 0.20)
        deck_shadow = (0.20, 0.12, 0.07)
        rail_color = (0.78, 0.18, 0.12)
        rail_shadow = (0.42, 0.10, 0.08)
        footing_color = (0.44, 0.41, 0.38)
        post_cap_color = (0.90, 0.70, 0.38)

        pond_radius_scale = 5.55 / 4.80
        island_radius_scale = 2.35 / 1.95

        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)

        y_base = 0.16
        arch_height = 0.88
        bridge_width = 1.30
        segments = 20
        plank_count = 5
        plank_gap = 0.03
        plank_full_width = (bridge_width - plank_gap * (plank_count - 1)) / plank_count

        def bridge_point(t):
            inv_t = 1.0 - t
            x = (
                inv_t * inv_t * start[0]
                + 2.0 * inv_t * t * control[0]
                + t * t * end[0]
            )
            z = (
                inv_t * inv_t * start[1]
                + 2.0 * inv_t * t * control[1]
                + t * t * end[1]
            )
            y = y_base + math.sin(math.pi * t) * arch_height
            return (x, y, z)

        def bridge_frame(a, b):
            dx = b[0] - a[0]
            dy = b[1] - a[1]
            dz = b[2] - a[2]
            horizontal = math.sqrt(dx * dx + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            pitch = -math.degrees(math.atan2(dy, horizontal + 1e-6))
            lat_x = -dz / (horizontal + 1e-6)
            lat_z = dx / (horizontal + 1e-6)
            return horizontal, yaw, pitch, lat_x, lat_z

        points = [bridge_point(i / segments) for i in range(segments + 1)]

        # Pondasi batu di awal dan akhir jembatan supaya transisinya lebih rapi.
        for idx, point in ((0, points[0]), (segments - 1, points[-1])):
            ref_a = points[idx]
            ref_b = points[idx + 1]
            _, yaw, _, lat_x, lat_z = bridge_frame(ref_a, ref_b)

            add(
                ColorCube(
                    app,
                    pos=(point[0], point[1] - 0.10, point[2]),
                    rot=(0, yaw, 0),
                    scale=(bridge_width * 0.34, 0.08, 0.24),
                    color=(0.30, 0.22, 0.15),
                )
            )

            for side in (-1, 1):
                side_offset = side * bridge_width * 0.48
                add(
                    ColorCube(
                        app,
                        pos=(
                            point[0] + lat_x * side_offset,
                            point[1] - 0.02,
                            point[2] + lat_z * side_offset,
                        ),
                        rot=(0, yaw, 0),
                        scale=(0.18, 0.12, 0.24),
                        color=footing_color,
                    )
                )

        # Deck berlapis dengan balok bawah agar jembatan lebih terasa tebal.
        for i in range(segments):
            p0 = points[i]
            p1 = points[i + 1]

            xm = (p0[0] + p1[0]) * 0.5
            ym = (p0[1] + p1[1]) * 0.5
            zm = (p0[2] + p1[2]) * 0.5

            horizontal, yaw, pitch, lat_x, lat_z = bridge_frame(p0, p1)
            seg_len = horizontal * 0.52 + 0.06

            add(
                ColorCube(
                    app,
                    pos=(xm, ym - 0.07, zm),
                    rot=(pitch, yaw, 0),
                    scale=(bridge_width * 0.45, 0.03, seg_len + 0.03),
                    color=deck_shadow,
                )
            )

            for beam_offset in (-0.26, 0.26):
                add(
                    ColorCube(
                        app,
                        pos=(
                            xm + lat_x * beam_offset,
                            ym - 0.12,
                            zm + lat_z * beam_offset,
                        ),
                        rot=(pitch, yaw, 0),
                        scale=(0.055, 0.05, seg_len),
                        color=(0.16, 0.10, 0.06),
                    )
                )

            add(
                ColorCube(
                    app,
                    pos=(xm, ym - 0.04, zm),
                    rot=(pitch, yaw, 0),
                    scale=(bridge_width * 0.40, 0.018, 0.05),
                    color=(0.28, 0.18, 0.10),
                )
            )

            for plank_idx in range(plank_count):
                offset = (
                    -bridge_width * 0.5
                    + plank_full_width * 0.5
                    + plank_idx * (plank_full_width + plank_gap)
                )
                plank_color = (
                    deck_highlight if plank_idx in (1, 3) else deck_base_color
                )
                tone = 0.025 * math.sin(i * 1.3 + plank_idx * 0.8)
                plank_color = tuple(
                    max(0.0, min(1.0, channel + tone)) for channel in plank_color
                )

                add(
                    ColorCube(
                        app,
                        pos=(
                            xm + lat_x * offset,
                            ym + 0.01,
                            zm + lat_z * offset,
                        ),
                        rot=(pitch, yaw, 0),
                        scale=(plank_full_width * 0.5, 0.032, seg_len),
                        color=plank_color,
                    )
                )

            for side in (-1, 1):
                rail_offset = side * bridge_width * 0.48
                rail_x = xm + lat_x * rail_offset
                rail_z = zm + lat_z * rail_offset

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.10, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.055, 0.035, seg_len + 0.03),
                        color=rail_shadow,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.42, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.028, 0.028, seg_len + 0.01),
                        color=rail_shadow,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(rail_x, ym + 0.64, rail_z),
                        rot=(pitch, yaw, 0),
                        scale=(0.04, 0.03, seg_len + 0.04),
                        color=rail_color,
                    )
                )

        # Tiang pagar dengan ujung lebih tinggi di kedua sisi masuk.
        for i, point in enumerate(points):
            if i == 0:
                ref_a = points[0]
                ref_b = points[1]
            elif i == len(points) - 1:
                ref_a = points[-2]
                ref_b = points[-1]
            else:
                ref_a = points[i - 1]
                ref_b = points[i + 1]

            _, yaw, _, lat_x, lat_z = bridge_frame(ref_a, ref_b)
            post_half_height = 0.40 if i in (0, len(points) - 1) else 0.34
            cap_scale = 0.09 if i in (0, len(points) - 1) else 0.07

            for side in (-1, 1):
                post_offset = side * bridge_width * 0.48
                px = point[0] + lat_x * post_offset
                pz = point[2] + lat_z * post_offset

                add(
                    ColorCube(
                        app,
                        pos=(px, point[1] + post_half_height, pz),
                        rot=(0, yaw, 0),
                        scale=(0.045, post_half_height, 0.045),
                        color=rail_color,
                    )
                )

                add(
                    ColorCube(
                        app,
                        pos=(px, point[1] + post_half_height * 2.0 + 0.05, pz),
                        rot=(0, yaw, 0),
                        scale=(cap_scale, 0.04, cap_scale),
                        color=post_cap_color,
                    )
                )
