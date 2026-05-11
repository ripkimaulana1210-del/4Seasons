import math

from ..data.scene_config import HOUSE_SPECS
from ..models import (
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


class SceneVillageHouseVariantMixin:
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
