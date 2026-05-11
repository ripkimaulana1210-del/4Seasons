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


class SceneVillagePropMixin:
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
