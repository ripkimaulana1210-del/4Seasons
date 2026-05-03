import math

from ..data.scene_config import POND_FENCE_ARCS
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


class SceneGardenMixin:
    def add_pond_edge_details(self, app, pond_radius_scale):
        self.add_partial_wooden_fence(app, pond_radius_scale)
        self.add_small_pond_edge_rocks(app, pond_radius_scale)
        self.add_wild_grass_at_water_edge(app, pond_radius_scale)

    def add_partial_wooden_fence(self, app, pond_radius_scale):
        add = self.add_object
        wood = (0.42, 0.24, 0.12)
        dark_wood = (0.25, 0.14, 0.08)
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
        fence_radius = 6.70 * pond_radius_scale
        for start_deg, end_deg, count in POND_FENCE_ARCS:
            points = []
            for idx in range(count):
                t = idx / (count - 1)
                angle_deg = start_deg + (end_deg - start_deg) * t
                angle = math.radians(angle_deg)
                radius = fence_radius + 0.10 * math.sin(idx * 1.7 + start_deg)
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                points.append((x, z, angle_deg))

                post_height = 0.38 + 0.035 * (idx % 3)
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.10 + post_height, z),
                        rot=(0, angle_deg + 90.0, 0),
                        scale=(0.045, post_height, 0.045),
                        color=dark_wood,
                    )
                )
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.10 + post_height * 2.05, z),
                        rot=(0, angle_deg + 90.0, 0),
                        scale=(0.060, 0.030, 0.060),
                        color=snow if self.is_winter() else wood,
                    )
                )

            for (x0, z0, _), (x1, z1, _) in zip(points, points[1:]):
                dx = x1 - x0
                dz = z1 - z0
                length = math.sqrt(dx * dx + dz * dz)
                yaw = math.degrees(math.atan2(dx, dz))
                cx = (x0 + x1) * 0.5
                cz = (z0 + z1) * 0.5
                for rail_y, rail_scale in ((0.55, 0.024), (0.78, 0.022)):
                    add(
                        ColorCube(
                            app,
                            pos=(cx, rail_y, cz),
                            rot=(0, yaw, 0),
                            scale=(0.035, rail_scale, length * 0.52),
                            color=wood,
                        )
                    )
                if self.is_winter():
                    add(
                        ColorCube(
                            app,
                            pos=(cx, 0.825, cz),
                            rot=(0, yaw, 0),
                            scale=(0.040, 0.012, length * 0.50),
                            color=snow,
                        )
                    )

    def add_small_pond_edge_rocks(self, app, pond_radius_scale):
        add = self.add_object
        base_colors = [
            (0.38, 0.38, 0.34),
            (0.46, 0.45, 0.40),
            (0.31, 0.33, 0.31),
            (0.52, 0.50, 0.43),
        ]
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))

        for i in range(72):
            angle_deg = (i * 360.0 / 72.0) + 3.0 * math.sin(i * 1.31)
            angle = math.radians(angle_deg)
            radius = (5.18 + 0.16 * math.sin(i * 0.9) + 0.08 * math.cos(i * 2.1)) * pond_radius_scale
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            size = 0.70 + 0.34 * (0.5 + 0.5 * math.sin(i * 1.7))
            color = snow if self.is_winter() and i % 4 == 0 else base_colors[i % len(base_colors)]
            add(
                PondRock(
                    app,
                    pos=(x, 0.040 + 0.012 * (i % 3), z),
                    rot=(0, angle_deg + i * 17.0, 0),
                    scale=(
                        (0.080 + 0.030 * math.sin(i * 0.8) ** 2) * size,
                        (0.030 + 0.010 * math.cos(i * 1.2) ** 2) * size,
                        (0.060 + 0.026 * math.cos(i * 0.7) ** 2) * size,
                    ),
                    color=color,
                )
            )

    def add_wild_grass_at_water_edge(self, app, pond_radius_scale):
        add = self.add_object
        if self.is_winter():
            grass_colors = [
                self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92)),
                (0.70, 0.78, 0.82),
                (0.58, 0.65, 0.62),
            ]
        else:
            grass_colors = [
                self.season_color("garden_lawn_color", (0.34, 0.49, 0.24)),
                self.season_color("garden_rich_lawn_color", (0.25, 0.42, 0.20)),
                (0.44, 0.58, 0.25),
            ]

        for cluster in range(46):
            angle_deg = (cluster * 360.0 / 46.0) + 5.5 * math.sin(cluster * 0.73)
            angle = math.radians(angle_deg)
            base_radius = (5.38 + 0.18 * math.sin(cluster * 1.8)) * pond_radius_scale
            blade_count = 4 + (cluster % 4)

            for blade in range(blade_count):
                blade_angle = angle + math.radians((blade - blade_count * 0.5) * 2.2)
                radius = base_radius + 0.08 * math.sin(blade * 1.4 + cluster)
                x = math.cos(blade_angle) * radius
                z = math.sin(blade_angle) * radius
                height = 0.085 + 0.032 * ((blade + cluster) % 3)
                lean = -18.0 + blade * 8.0 + 8.0 * math.sin(cluster)
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.040 + height, z),
                        rot=(lean, angle_deg + 90.0 + blade * 9.0, 10.0 * math.sin(blade + cluster)),
                        scale=(0.010, height, 0.006),
                        color=grass_colors[(cluster + blade) % len(grass_colors)],
                    )
                )

    def add_pond_flowers(self, app, pond_radius_scale):
        add = self.add_object

        stem_color = (0.22, 0.46, 0.18)
        leaf_color = (0.30, 0.56, 0.22)
        flower_palettes = [
            ((1.00, 0.78, 0.90), (0.96, 0.47, 0.69), (0.98, 0.82, 0.30)),
            ((0.98, 0.90, 0.70), (0.98, 0.64, 0.22), (0.94, 0.76, 0.18)),
            ((0.96, 0.82, 1.00), (0.78, 0.56, 0.94), (0.98, 0.84, 0.36)),
            ((1.00, 0.96, 0.82), (1.00, 0.66, 0.44), (0.92, 0.72, 0.18)),
        ]

        # Kluster bunga diletakkan di tepi luar danau dengan fokus ke area yang terlihat kamera.
        cluster_specs = [
            (84, 5.94 * pond_radius_scale, 6, 0.28, 0, 1.08),
            (104, 5.96 * pond_radius_scale, 7, 0.28, 0, 1.02),
            (128, 6.02 * pond_radius_scale, 6, 0.24, 1, 0.96),
            (154, 6.08 * pond_radius_scale, 5, 0.20, 2, 0.92),
            (188, 6.18 * pond_radius_scale, 7, 0.26, 0, 1.00),
            (222, 6.34 * pond_radius_scale, 6, 0.28, 3, 1.08),
            (256, 6.20 * pond_radius_scale, 5, 0.22, 1, 0.90),
            (292, 6.06 * pond_radius_scale, 6, 0.20, 2, 0.96),
            (330, 6.02 * pond_radius_scale, 5, 0.18, 0, 0.88),
            (16, 6.20 * pond_radius_scale, 6, 0.19, 3, 0.92),
            (34, 6.28 * pond_radius_scale, 4, 0.18, 1, 0.86),
        ]

        for cluster_idx, (angle_deg, radius, count, spread, palette_idx, height_bias) in enumerate(cluster_specs):
            base_angle = math.radians(angle_deg)
            outer_petal, inner_petal, center_color = flower_palettes[
                palette_idx % len(flower_palettes)
            ]
            bed_x = math.cos(base_angle) * (radius + spread * 0.08)
            bed_z = math.sin(base_angle) * (radius + spread * 0.08)

            add(
                PondRock(
                    app,
                    pos=(bed_x, 0.07, bed_z),
                    rot=(0, angle_deg + cluster_idx * 17.0, 0),
                    scale=(
                        0.17 + 0.03 * math.sin(cluster_idx * 0.8),
                        0.055,
                        0.13 + 0.02 * math.cos(cluster_idx * 1.3),
                    ),
                    color=(0.28, 0.47 + 0.03 * math.sin(cluster_idx), 0.22),
                )
            )

            for flower_idx in range(count):
                local_angle = (
                    base_angle
                    + (flower_idx - (count - 1) * 0.5) * 0.09
                    + math.sin(cluster_idx * 1.8 + flower_idx * 1.3) * 0.05
                )
                local_radius = radius + math.cos(cluster_idx + flower_idx * 1.4) * spread
                x = math.cos(local_angle) * local_radius
                z = math.sin(local_angle) * local_radius

                stem_half = (
                    0.095
                    + 0.016 * math.sin(cluster_idx * 0.9 + flower_idx * 1.7)
                ) * height_bias
                base_y = 0.02 + 0.006 * math.cos(cluster_idx * 1.2 + flower_idx)

                add(
                    ColorCube(
                        app,
                        pos=(x, base_y + stem_half, z),
                        scale=(0.012, stem_half, 0.012),
                        color=stem_color,
                    )
                )

                for leaf_side in (-1, 1):
                    leaf_y = base_y + stem_half * (0.84 + 0.12 * leaf_side)
                    add(
                        ColorCube(
                            app,
                            pos=(
                                x + leaf_side * 0.038,
                                leaf_y,
                                z + 0.012 * math.sin(local_angle * 2.0 + leaf_side),
                            ),
                            rot=(12, math.degrees(local_angle) + leaf_side * 34, 26 * leaf_side),
                            scale=(0.030, 0.008, 0.016),
                            color=leaf_color,
                    )
                )

                bloom_y = base_y + stem_half * 2.0 + 0.022
                bloom_size = 0.022 + 0.005 * math.cos(cluster_idx * 1.6 + flower_idx)
                petal_spin = base_angle + flower_idx * 0.55

                add(
                    ColorCube(
                        app,
                        pos=(x, bloom_y, z),
                        rot=(0, math.degrees(petal_spin), 0),
                        scale=(bloom_size * 0.62, bloom_size * 0.62, bloom_size * 0.62),
                        color=center_color,
                    )
                )

                for petal_idx in range(5):
                    petal_angle = petal_spin + petal_idx * (2.0 * math.pi / 5.0)
                    petal_radius = bloom_size * 1.58
                    petal_color = outer_petal if petal_idx % 2 == 0 else inner_petal

                    add(
                        ColorCube(
                            app,
                            pos=(
                                x + math.cos(petal_angle) * petal_radius,
                                bloom_y + 0.003 + 0.002 * math.sin(petal_idx + flower_idx),
                                z + math.sin(petal_angle) * petal_radius,
                            ),
                            rot=(16, math.degrees(petal_angle), 30),
                            scale=(bloom_size * 0.82, bloom_size * 0.28, bloom_size * 0.58),
                            color=petal_color,
                        )
                    )

                # Kelopak jatuh tipis di tanah supaya tepi danau terasa lebih hidup.
                for petal_idx in range(3):
                    ground_angle = petal_spin + petal_idx * 1.9
                    ground_radius = 0.06 + petal_idx * 0.025
                    add(
                        ColorCube(
                            app,
                            pos=(
                                x + math.cos(ground_angle) * ground_radius,
                                base_y + 0.006,
                                z + math.sin(ground_angle) * ground_radius,
                            ),
                            rot=(0, math.degrees(ground_angle), 0),
                            scale=(0.018, 0.004, 0.012),
                            color=outer_petal,
                        )
                    )

    def add_garden_flower(
        self,
        app,
        pos,
        outer_color,
        inner_color,
        center_color,
        scale=1.0,
        spin=0.0,
    ):
        add = self.add_object
        x, z = pos
        stem_half = 0.070 * scale
        bloom_y = 0.030 + stem_half * 2.0

        add(
            ColorCube(
                app,
                pos=(x, 0.030 + stem_half, z),
                scale=(0.010 * scale, stem_half, 0.010 * scale),
                color=(0.20, 0.44, 0.17),
            )
        )

        add(
            ColorCube(
                app,
                pos=(x, bloom_y, z),
                rot=(0, math.degrees(spin), 0),
                scale=(0.020 * scale, 0.020 * scale, 0.020 * scale),
                color=center_color,
            )
        )

        for petal_idx in range(5):
            petal_angle = spin + petal_idx * (2.0 * math.pi / 5.0)
            petal_color = outer_color if petal_idx % 2 == 0 else inner_color
            add(
                ColorCube(
                    app,
                    pos=(
                        x + math.cos(petal_angle) * 0.040 * scale,
                        bloom_y + 0.006,
                        z + math.sin(petal_angle) * 0.040 * scale,
                    ),
                    rot=(16, math.degrees(petal_angle), 26),
                    scale=(0.030 * scale, 0.010 * scale, 0.020 * scale),
                    color=petal_color,
                )
            )

    def add_garden_bench(self, app, pos, yaw, scale=1.0):
        add = self.add_object
        x, z = pos
        wood = (0.42, 0.23, 0.11)
        dark_wood = (0.24, 0.13, 0.07)

        add(
            ColorCube(
                app,
                pos=(x, 0.19 * scale, z),
                rot=(0, yaw, 0),
                scale=(0.52 * scale, 0.055 * scale, 0.16 * scale),
                color=wood,
            )
        )
        if self.is_winter():
            add(
                ColorCube(
                    app,
                    pos=(x, 0.255 * scale, z),
                    rot=(0, yaw, 0),
                    scale=(0.55 * scale, 0.022 * scale, 0.18 * scale),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

        back_x, back_z = self.local_house_pos(x, z, yaw, 0.0, -0.18 * scale)
        add(
            ColorCube(
                app,
                pos=(back_x, 0.38 * scale, back_z),
                rot=(8, yaw, 0),
                scale=(0.55 * scale, 0.060 * scale, 0.055 * scale),
                color=wood,
            )
        )
        if self.is_winter():
            add(
                ColorCube(
                    app,
                    pos=(back_x, 0.445 * scale, back_z),
                    rot=(8, yaw, 0),
                    scale=(0.56 * scale, 0.024 * scale, 0.065 * scale),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

        for local_x in (-0.38 * scale, 0.38 * scale):
            for local_z in (-0.09 * scale, 0.09 * scale):
                leg_x, leg_z = self.local_house_pos(x, z, yaw, local_x, local_z)
                add(
                    ColorCube(
                        app,
                        pos=(leg_x, 0.085 * scale, leg_z),
                        rot=(0, yaw, 0),
                        scale=(0.030 * scale, 0.085 * scale, 0.030 * scale),
                        color=dark_wood,
                    )
                )

    def add_garden_lantern(self, app, pos, scale=1.0, yaw=0.0):
        add = self.add_object
        x, z = pos
        stone = (0.58, 0.57, 0.52)
        glow = (1.00, 0.78, 0.36)

        parts = [
            ((0.16, 0.035, 0.16), (0.00, 0.035, 0.00), stone),
            ((0.065, 0.22, 0.065), (0.00, 0.29, 0.00), stone),
            ((0.17, 0.040, 0.17), (0.00, 0.53, 0.00), stone),
            ((0.105, 0.090, 0.105), (0.00, 0.66, 0.00), glow),
            ((0.20, 0.045, 0.20), (0.00, 0.79, 0.00), stone),
            ((0.12, 0.035, 0.12), (0.00, 0.88, 0.00), stone),
        ]

        for part_scale, offset, color in parts:
            add(
                ColorCube(
                    app,
                    pos=(
                        x + offset[0] * scale,
                        offset[1] * scale,
                        z + offset[2] * scale,
                    ),
                    rot=(0, yaw, 0),
                    scale=(
                        part_scale[0] * scale,
                        part_scale[1] * scale,
                        part_scale[2] * scale,
                    ),
                    color=color,
                )
            )

        if self.is_winter():
            add(
                ColorCube(
                    app,
                    pos=(x, 0.925 * scale, z),
                    rot=(0, yaw, 0),
                    scale=(0.15 * scale, 0.025 * scale, 0.15 * scale),
                    color=self.season_color("winter_snow_color", (0.94, 0.97, 1.00)),
                )
            )

    def add_garden_gateway(self, app, pos, yaw, scale=1.0):
        add = self.add_object
        x, z = pos
        post_color = (0.47, 0.18, 0.10)
        beam_color = (0.62, 0.24, 0.13)
        roof_color = (0.36, 0.12, 0.09)
        half_width = 0.56 * scale
        half_depth = 0.14 * scale
        post_half = 0.56 * scale

        for local_x in (-half_width, half_width):
            for local_z in (-half_depth, half_depth):
                post_x, post_z = self.local_house_pos(x, z, yaw, local_x, local_z)
                add(
                    ColorCube(
                        app,
                        pos=(post_x, post_half, post_z),
                        rot=(0, yaw, 0),
                        scale=(0.055 * scale, post_half, 0.055 * scale),
                        color=post_color,
                    )
                )

        add(
            ColorCube(
                app,
                pos=(x, post_half * 2.0 + 0.08 * scale, z),
                rot=(0, yaw, 0),
                scale=(0.78 * scale, 0.055 * scale, 0.20 * scale),
                color=beam_color,
            )
        )

        add(
            TexturedGableRoof(
                app,
                pos=(x, post_half * 2.0 + 0.14 * scale, z),
                rot=(0, yaw, 0),
                scale=(0.80 * scale, 0.22 * scale, 0.28 * scale),
                texture_name="roof",
                tint=roof_color,
                repeat=(1.0, 1.0),
            )
        )
        self.add_snow_roof_cap(
            app,
            x,
            z,
            yaw,
            0.80 * scale,
            0.22 * scale,
            0.28 * scale,
            post_half * 2.0 + 0.14 * scale,
            0.22 * scale,
        )

    def add_beautiful_garden(self, app, pond_radius_scale, road_radius, road_width):
        add = self.add_object

        def polar(angle_deg, radius):
            angle = math.radians(angle_deg)
            return (math.cos(angle) * radius, math.sin(angle) * radius)

        path_color = self.season_color("garden_path_color", (0.66, 0.58, 0.42))
        lawn_color = self.season_color("garden_lawn_color", (0.34, 0.49, 0.24))
        rich_lawn = self.season_color("garden_rich_lawn_color", (0.25, 0.42, 0.20))
        hedge_color = self.season_color("garden_hedge_color", (0.24, 0.42, 0.18))
        flower_palettes = [
            ((1.00, 0.70, 0.88), (0.95, 0.36, 0.62), (0.98, 0.82, 0.28)),
            ((0.98, 0.88, 0.42), (1.00, 0.56, 0.22), (0.60, 0.36, 0.10)),
            ((0.72, 0.86, 1.00), (0.44, 0.58, 0.95), (0.98, 0.86, 0.34)),
            ((0.88, 0.76, 1.00), (0.68, 0.44, 0.92), (0.98, 0.82, 0.30)),
        ]

        garden_center = polar(252, 7.10)
        lawn_specs = [
            (222, 6.70, 1.20, 0.72, 30, lawn_color),
            (248, 7.10, 1.55, 1.00, 15, rich_lawn),
            (276, 6.85, 1.25, 0.78, -22, lawn_color),
            (246, 7.85, 1.10, 0.65, 50, lawn_color),
            (292, 7.55, 1.00, 0.62, -40, rich_lawn),
        ]

        for angle_deg, radius, sx, sz, rot, color in lawn_specs:
            x, z = polar(angle_deg, radius)
            add(
                TexturedPlane(
                    app,
                    pos=(x, 0.006, z),
                    rot=(0, angle_deg + rot, 0),
                    scale=(sx, 1, sz),
                    texture_name=self.season_value("garden_texture", "grass"),
                    tint=color,
                    repeat=(2.2, 1.6),
                )
            )

        entry = polar(252, road_radius - road_width * 0.54)
        path_points = [
            entry,
            polar(252, 7.85),
            (garden_center[0] - 0.18, garden_center[1] + 0.12),
            polar(238, 6.22),
        ]
        for start, end in zip(path_points, path_points[1:]):
            self.add_road_segment(app, start, end, 0.42, path_color, y=0.014)

        promenade_points = [
            polar(210 + i * 10, 6.34 + 0.12 * math.sin(i * 0.9))
            for i in range(11)
        ]
        for start, end in zip(promenade_points, promenade_points[1:]):
            self.add_road_segment(app, start, end, 0.34, path_color, y=0.014)

        self.add_garden_gateway(
            app,
            entry,
            math.degrees(math.atan2(-entry[0], -entry[1])),
            scale=1.08,
        )

        fountain_x, fountain_z = garden_center
        add(
            PondRock(
                app,
                pos=(fountain_x, 0.105, fountain_z),
                scale=(0.78, 0.145, 0.78),
                color=(0.50, 0.49, 0.45),
            )
        )
        add(
            WaterSurface(
                app,
                pos=(fountain_x, 0.235, fountain_z),
                scale=(0.104, 1.0, 0.104),
                color=(0.18, 0.46, 0.63),
            )
        )
        add(
            ColorCube(
                app,
                pos=(fountain_x, 0.42, fountain_z),
                scale=(0.08, 0.20, 0.08),
                color=(0.60, 0.58, 0.53),
            )
        )
        for jet_idx in range(4):
            jet_angle = jet_idx * math.pi * 0.5 + math.pi * 0.25
            add(
                ColorCube(
                    app,
                    pos=(
                        fountain_x + math.cos(jet_angle) * 0.12,
                        0.67,
                        fountain_z + math.sin(jet_angle) * 0.12,
                    ),
                    rot=(22, math.degrees(jet_angle), 0),
                    scale=(0.018, 0.20, 0.018),
                    color=(0.66, 0.86, 0.95),
                )
            )

        for bed_idx in range(8):
            bed_angle = bed_idx * (2.0 * math.pi / 8.0) + 0.20
            bed_x = fountain_x + math.cos(bed_angle) * 1.04
            bed_z = fountain_z + math.sin(bed_angle) * 1.04
            add(
                PondRock(
                    app,
                    pos=(bed_x, 0.050, bed_z),
                    rot=(0, math.degrees(bed_angle), 0),
                    scale=(0.32, 0.055, 0.22),
                    color=self.season_color("garden_bed_color", (0.24, 0.40, 0.18)),
                )
            )

            if self.season_value("garden_flowers_enabled", True):
                outer, inner, center = flower_palettes[bed_idx % len(flower_palettes)]
                for flower_idx in range(5):
                    offset_angle = bed_angle + (flower_idx - 2) * 0.34
                    offset = 0.15 + 0.035 * math.cos(flower_idx + bed_idx)
                    self.add_garden_flower(
                        app,
                        (
                            bed_x + math.cos(offset_angle) * offset,
                            bed_z + math.sin(offset_angle) * offset,
                        ),
                        outer,
                        inner,
                        center,
                        scale=0.92 + 0.12 * math.sin(bed_idx + flower_idx),
                        spin=offset_angle,
                    )

        for arc_idx in range(24):
            angle_deg = 208 + arc_idx * 4.1
            hedge_x, hedge_z = polar(angle_deg, 7.95 + 0.05 * math.sin(arc_idx))
            add(
                PondRock(
                    app,
                    pos=(hedge_x, 0.14, hedge_z),
                    rot=(0, angle_deg + arc_idx * 9.0, 0),
                    scale=(0.32, 0.17, 0.24),
                    color=hedge_color,
                )
            )

        if self.season_value("garden_flowers_enabled", True):
            for bed_idx, angle_deg in enumerate((214, 228, 286, 302)):
                outer, inner, center = flower_palettes[(bed_idx + 1) % len(flower_palettes)]
                base_x, base_z = polar(angle_deg, 6.62)
                for flower_idx in range(7):
                    fan = math.radians(angle_deg + (flower_idx - 3) * 5.0)
                    spread = 0.16 + 0.05 * (flower_idx % 3)
                    self.add_garden_flower(
                        app,
                        (
                            base_x + math.cos(fan) * spread,
                            base_z + math.sin(fan) * spread,
                        ),
                        outer,
                        inner,
                        center,
                        scale=0.82,
                        spin=fan,
                    )

        for angle_deg, radius, tree_scale in (
            (218, 7.55, 0.36),
            (286, 7.75, 0.34),
            (305, 6.75, 0.30),
        ):
            x, z = polar(angle_deg, radius)
            tree_pos = (x, 0.06, z)
            tree_scale_vec = (tree_scale, tree_scale, tree_scale)
            add(
                SakuraWood(
                    app,
                    pos=tree_pos,
                    scale=tree_scale_vec,
                    color=self.season_color("sakura_wood_color", (0.25, 0.15, 0.08)),
                )
            )
            add(
                SakuraCanopyDeep(
                    app,
                    pos=tree_pos,
                    scale=tree_scale_vec,
                    color=self.season_color("sakura_canopy_deep_color", (0.90, 0.33, 0.58)),
                )
            )
            add(
                SakuraCanopyLight(
                    app,
                    pos=tree_pos,
                    scale=tree_scale_vec,
                    color=self.season_color("sakura_canopy_light_color", (1.00, 0.72, 0.90)),
                )
            )
            add(
                SakuraBlossomLight(
                    app,
                    pos=tree_pos,
                    scale=tree_scale_vec,
                    color=self.season_color("sakura_blossom_light_color", (1.00, 0.80, 0.94)),
                )
            )

        for bench_angle in (230, 276):
            bench_x, bench_z = polar(bench_angle, 7.55)
            yaw = math.degrees(math.atan2(fountain_x - bench_x, fountain_z - bench_z))
            self.add_garden_bench(app, (bench_x, bench_z), yaw, scale=1.05)

        for lantern_angle in (214, 244, 282, 304):
            lantern_x, lantern_z = polar(lantern_angle, 7.25)
            self.add_garden_lantern(
                app,
                (lantern_x, lantern_z),
                scale=0.82,
                yaw=lantern_angle,
            )
