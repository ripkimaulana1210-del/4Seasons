import math

from .model import (
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


class Scene:
    def __init__(self, app):
        self.app = app
        transition = app.season_controller.transition_snapshot()
        self.season = transition["from"] if transition is not None else app.season_controller.current
        self.objects = []
        self.load()

    def add_object(self, obj):
        self.objects.append(obj)

    def season_color(self, key, default):
        return self.season.get(key, default)

    def season_value(self, key, default):
        return self.season.get(key, default)

    def is_winter(self):
        return self.season_value("seasonal_effect", "") == "winter"

    def load(self):
        add = self.add_object
        app = self.app
        pond_radius_scale = 5.55 / 4.80
        island_radius_scale = 2.35 / 1.95

        self.add_sky(app)

        # Tanah besar. Ini jadi area utama map.
        add(
            TexturedPlane(
                app,
                pos=(0, -0.055, 0),
                scale=(21, 1, 21),
                texture_name=self.season_value("ground_texture", "grass"),
                tint=self.season_color("ground_color", (0.23, 0.33, 0.17)),
                repeat=(18.0, 18.0),
            )
        )

        # Kolam lingkaran di tengah. Sisanya tetap tanah dari ColorPlane di atas.
        add(
            WaterSurface(
                app,
                pos=(0, 0.0, 0),
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("water_color", (0.16, 0.38, 0.54)),
            )
        )

        self.add_fuji_background(app)

        add(
            WaterReflection(
                app,
                pos=(0, 0.0, 0),
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("water_reflection_color", (0.96, 0.42, 0.70)),
            )
        )

        # Pulau kecil lingkaran di tengah kolam untuk pohon sakura.
        add(
            IslandMound(
                app,
                pos=(0, 0.0, 0),
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("island_mound_color", (0.25, 0.34, 0.16)),
            )
        )

        add(
            IslandGrass(
                app,
                pos=(0, 0.0, 0),
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("island_grass_color", (0.42, 0.56, 0.20)),
            )
        )

        tree_pos = (0, 0.24, 0)
        tree_rot = (0, 0, 0)
        tree_scale = (1.28, 1.28, 1.28)

        add(
            SakuraWood(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_wood_color", (0.26, 0.16, 0.09)),
            )
        )

        add(
            SakuraCanopyDeep(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_canopy_deep_color", (0.92, 0.34, 0.60)),
            )
        )

        add(
            SakuraCanopyLight(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_canopy_light_color", (1.00, 0.70, 0.90)),
            )
        )

        add(
            SakuraBlossomDeep(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_blossom_deep_color", (0.98, 0.42, 0.66)),
            )
        )

        add(
            SakuraBlossomLight(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_blossom_light_color", (1.00, 0.78, 0.92)),
            )
        )

        self.add_swing(app)
        self.add_bridge(app)
        self.add_settlement(app, pond_radius_scale)
        self.add_pond_edge_details(app, pond_radius_scale)
        
        # Batu di tepian pulau.
        island_rocks = [
            (1.55, 0.25, 0.10, (0.32, 0.18, 0.24)),
            (1.62, 1.05, 0.06, (0.25, 0.15, 0.20)),
            (1.58, 2.15, 0.08, (0.34, 0.18, 0.25)),
            (1.50, 3.08, 0.04, (0.24, 0.14, 0.18)),
            (1.65, 4.10, 0.07, (0.30, 0.16, 0.22)),
            (1.54, 5.10, 0.03, (0.25, 0.14, 0.18)),
            (1.82, 0.68, 0.07, (0.22, 0.12, 0.16)),
            (1.74, 1.62, 0.06, (0.28, 0.12, 0.18)),
            (1.88, 2.68, 0.05, (0.24, 0.11, 0.16)),
            (1.76, 3.62, 0.06, (0.27, 0.12, 0.18)),
            (1.86, 4.62, 0.07, (0.23, 0.11, 0.17)),
            (1.72, 5.72, 0.05, (0.29, 0.13, 0.18)),
        ]

        for radius, angle, y, scale in island_rocks:
            add(
                PondRock(
                    app,
                    pos=(
                        math.cos(angle) * radius * island_radius_scale,
                        y,
                        math.sin(angle) * radius * island_radius_scale,
                    ),
                    rot=(0, angle * 57.2958, 0),
                    scale=scale,
                    color=(0.44, 0.43, 0.39),
                )
            )

        # Batu kecil di tepi luar kolam lingkaran, di atas tanah.
        pond_edge_rocks = [
            (4.85, 0.15, 0.03, (0.35, 0.14, 0.23)),
            (4.95, 1.35, 0.03, (0.28, 0.12, 0.20)),
            (4.75, 2.75, 0.03, (0.34, 0.13, 0.22)),
            (5.00, 4.05, 0.03, (0.28, 0.12, 0.19)),
            (4.80, 5.25, 0.03, (0.33, 0.13, 0.21)),
            (5.12, 0.82, 0.02, (0.22, 0.10, 0.17)),
            (5.18, 2.05, 0.02, (0.24, 0.10, 0.18)),
            (5.08, 3.40, 0.02, (0.21, 0.10, 0.16)),
            (5.22, 4.72, 0.02, (0.25, 0.10, 0.18)),
        ]

        for radius, angle, y, scale in pond_edge_rocks:
            add(
                PondRock(
                    app,
                    pos=(
                        math.cos(angle) * radius * pond_radius_scale,
                        y,
                        math.sin(angle) * radius * pond_radius_scale,
                    ),
                    rot=(0, angle * 57.2958, 0),
                    scale=scale,
                    color=(0.42, 0.42, 0.38),
                )
            )

        # Semak rendah di sisi belakang kolam agar frame tidak kosong.
        bush_color = self.season_color("bush_color", (0.25, 0.40, 0.20))
        for i in range(18):
            angle = math.radians(188 + i * 10.0)
            radius = (5.85 + 0.35 * math.sin(i * 1.7)) * pond_radius_scale
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.18, math.sin(angle) * radius),
                    rot=(0, i * 23.0, 0),
                    scale=(
                        0.75 + 0.18 * math.sin(i * 0.9),
                        0.30 + 0.07 * math.cos(i * 1.3),
                        0.55 + 0.16 * math.cos(i * 0.8),
                    ),
                    color=(
                        min(1.0, bush_color[0] + 0.03 * math.sin(i)),
                        min(1.0, bush_color[1] + 0.03 * math.cos(i)),
                        min(1.0, bush_color[2] + 0.03 * math.sin(i * 0.7)),
                    ),
                )
            )

        for i in range(9):
            angle = math.radians(202 + i * 15.0)
            radius = (5.35 + 0.20 * math.cos(i)) * pond_radius_scale
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.24, math.sin(angle) * radius),
                    rot=(0, i * 31.0, 0),
                    scale=(0.28, 0.10, 0.24) if self.is_winter() else (0.26, 0.12, 0.22),
                    color=self.season_color("winter_snow_color", (0.68, 0.42, 0.72))
                    if self.is_winter()
                    else (0.68, 0.42, 0.72),
                )
            )

        if self.season_value("pond_flowers_enabled", True):
            self.add_pond_flowers(app, pond_radius_scale)

        # Lentera batu kecil seperti taman Jepang di sisi kiri belakang.
        lantern_x = -4.45 * pond_radius_scale
        lantern_z = -2.55 * pond_radius_scale
        lantern_color = (0.62, 0.61, 0.55)
        lantern_parts = [
            ((0.38, 0.06, 0.38), (0.00, 0.01, 0.00), (0, 0, 0)),
            ((0.18, 0.36, 0.18), (0.00, 0.43, 0.00), (0, 0, 0)),
            ((0.34, 0.07, 0.34), (0.00, 0.84, 0.00), (0, 0, 0)),
            ((0.22, 0.20, 0.22), (0.00, 1.02, 0.00), (0, 0, 0)),
            ((0.46, 0.06, 0.46), (0.00, 1.24, 0.00), (0, 45, 0)),
            ((0.24, 0.08, 0.24), (0.00, 1.38, 0.00), (0, 45, 0)),
        ]
        for scale, offset, rot in lantern_parts:
            add(
                ColorCube(
                    app,
                    pos=(lantern_x + offset[0], offset[1], lantern_z + offset[2]),
                    rot=rot,
                    scale=scale,
                    color=lantern_color,
                )
            )

        self.add_temperature_indicator(app)
        self.add_seasonal_effects(app, pond_radius_scale)
        self.add_natural_elements(app)
        self.add_emotional_season_marks(app, pond_radius_scale)
        self.add_emotional_transition(app)

        # Petal hanya di area kolam lingkaran.
        if self.season_value("floating_petals_enabled", True):
            add(
                FloatingPetals(
                    app,
                    pos=(0, 0.0, 0),
                    scale=(1.0, 1.0, 1.0),
                    color=self.season_color("floating_petal_color", (1.00, 0.64, 0.84)),
                )
            )

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
        arcs = [
            (110, 176, 11),
            (214, 292, 13),
            (318, 354, 7),
        ]

        for start_deg, end_deg, count in arcs:
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

    def add_swing(self, app):
        rope_color = (0.23, 0.16, 0.09)
        seat_color = (0.36, 0.20, 0.10)

        anchor_y = 2.55
        seat_y = 1.35
        x = -0.95
        z = 0.20
        rope_gap = 0.32

        # Tali kiri
        self.add_object(
            ColorCube(
                app,
                pos=(x - rope_gap, (anchor_y + seat_y) * 0.5, z),
                scale=(0.018, (anchor_y - seat_y) * 0.5, 0.018),
                color=rope_color,
            )
        )

        # Tali kanan
        self.add_object(
            ColorCube(
                app,
                pos=(x + rope_gap, (anchor_y + seat_y) * 0.5, z),
                scale=(0.018, (anchor_y - seat_y) * 0.5, 0.018),
                color=rope_color,
            )
        )

        # Papan ayunan
        self.add_object(
            ColorCube(
                app,
                pos=(x, seat_y, z),
                scale=(0.46, 0.055, 0.18),
                color=seat_color,
            )
        )

    def add_fuji_background(self, app):
        add = self.add_object

        # Gunung Fuji dibuat cukup jauh dan besar, tapi tetap hanya sebagai pemandangan.
        fuji_pos = (-11.8, -0.26, -34.4)

        add(
            FujiPeak(
                app,
                pos=fuji_pos,
                scale=(10.8, 12.8, 10.4),
                color=self.season_color("fuji_peak_color", (0.42, 0.49, 0.60)),
            )
        )

        add(
            FujiSnowcap(
                app,
                pos=fuji_pos,
                scale=(10.8, 12.8, 10.4),
                color=self.season_color("fuji_snow_color", (0.96, 0.98, 1.00)),
            )
        )

    def add_temperature_indicator(self, app):
        add = self.add_object
        temp = self.app.season_controller.temperature_c
        temp_t = max(0.0, min(1.0, (temp + 5.0) / 40.0))
        fill_height = 0.16 + 0.96 * temp_t
        x = 14.10
        z = 12.60

        add(
            ColorCube(
                app,
                pos=(x, 0.78, z),
                rot=(0, -24, 0),
                scale=(0.34, 0.84, 0.06),
                color=(0.20, 0.22, 0.22),
            )
        )

        add(
            ColorCube(
                app,
                pos=(x, 0.76, z + 0.045),
                rot=(0, -24, 0),
                scale=(0.060, 0.58, 0.035),
                color=(0.90, 0.92, 0.88),
            )
        )

        add(
            ColorCube(
                app,
                pos=(x, 0.21, z + 0.055),
                rot=(0, -24, 0),
                scale=(0.13, 0.13, 0.055),
                color=self.season_color("temperature_bar_color", (0.46, 0.78, 0.36)),
            )
        )

        add(
            ColorCube(
                app,
                pos=(x, 0.21 + fill_height * 0.5, z + 0.060),
                rot=(0, -24, 0),
                scale=(0.040, fill_height * 0.5, 0.040),
                color=self.season_color("temperature_bar_color", (0.46, 0.78, 0.36)),
            )
        )

        for tick_idx in range(5):
            tick_y = 0.34 + tick_idx * 0.24
            add(
                ColorCube(
                    app,
                    pos=(x + 0.13, tick_y, z + 0.065),
                    rot=(0, -24, 0),
                    scale=(0.050, 0.010, 0.020),
                    color=(0.74, 0.76, 0.72),
                )
            )

        add(
            ColorCube(
                app,
                pos=(x, 0.055, z),
                rot=(0, -24, 0),
                scale=(0.46, 0.055, 0.18),
                color=(0.34, 0.33, 0.30),
            )
        )

    def add_natural_elements(self, app):
        self.add_sun(app)
        self.add_night_lights(app)
        self.add_wind(app)
        self.add_rain(app)

    def add_lantern_post(
        self,
        app,
        pos,
        yaw=0.0,
        height=0.78,
        glow_scale=0.36,
        glow_alpha=0.54,
        post_color=(0.22, 0.17, 0.12),
        lamp_color=(1.00, 0.70, 0.34),
    ):
        add = self.add_object
        x, z = pos
        add(
            ColorCube(
                app,
                pos=(x, height * 0.50, z),
                rot=(0, yaw, 0),
                scale=(0.035, height * 0.50, 0.035),
                color=post_color,
            )
        )
        add(
            ColorCube(
                app,
                pos=(x, height + 0.045, z),
                rot=(0, yaw, 0),
                scale=(0.105, 0.055, 0.105),
                color=lamp_color,
            )
        )
        add(
            NightGlow(
                app,
                pos=(x, height + 0.080, z + 0.012),
                rot=(0, 0, 0),
                scale=(glow_scale, glow_scale, 1.0),
                color=lamp_color,
                alpha=glow_alpha,
            )
        )

    def add_night_lights(self, app):
        road_lamps = [
            (0.68, 11.2, 6),
            (12.7, 0.56, 90),
            (-12.8, -0.54, -90),
            (-0.78, -12.9, 178),
            (4.95, 7.35, 32),
        ]
        for i, (x, z, yaw) in enumerate(road_lamps):
            self.add_lantern_post(
                app,
                (x, z),
                yaw=yaw,
                height=0.80,
                glow_scale=0.38,
                glow_alpha=0.48 if i % 2 else 0.56,
                lamp_color=(1.00, 0.68, 0.34),
            )

        self.add_sakura_hanging_lanterns(app)

    def add_sakura_hanging_lanterns(self, app):
        add = self.add_object
        lantern_specs = [
            (-0.78, 2.04, 0.18, -12, 0.34),
            (0.66, 2.15, -0.28, 16, 0.31),
            (-0.24, 2.28, -0.82, 8, 0.28),
            (0.32, 1.86, 0.92, -18, 0.26),
            (1.02, 1.92, 0.42, 22, 0.24),
        ]

        for i, (x, y, z, yaw, glow_scale) in enumerate(lantern_specs):
            cord_height = 0.34 + 0.04 * (i % 2)
            add(
                ColorCube(
                    app,
                    pos=(x, y + cord_height * 0.50, z),
                    rot=(0, yaw, 0),
                    scale=(0.010, cord_height * 0.50, 0.010),
                    color=(0.16, 0.10, 0.07),
                )
            )
            add(
                ColorCube(
                    app,
                    pos=(x, y, z),
                    rot=(0, yaw, 0),
                    scale=(0.115, 0.145, 0.095),
                    color=(0.94, 0.34, 0.16),
                )
            )
            add(
                ColorCube(
                    app,
                    pos=(x, y + 0.15, z),
                    rot=(0, yaw, 0),
                    scale=(0.135, 0.025, 0.110),
                    color=(0.28, 0.12, 0.08),
                )
            )
            add(
                NightGlow(
                    app,
                    pos=(x, y + 0.02, z + 0.016),
                    rot=(0, yaw, 0),
                    scale=(glow_scale, glow_scale, 1.0),
                    color=(1.00, 0.58, 0.26),
                    alpha=0.44 + 0.04 * (i % 2),
                    pulse=0.05,
                )
            )

    def add_sky(self, app):
        add = self.add_object
        add(SkyDome(app))
        add(MoonDisc(app))

        if self.season_value("aurora_intensity", 0.0) > 0.0:
            add(AuroraBand(app))

        cloud_specs = [
            ("cloud_soft", (-12.0, 11.2, -12.5), (8.0, 1.0, 3.2), (0, 18, 0), (2.8, 0.0, -1.0), 0.010, 0.04),
            ("cloud_streak", (8.0, 12.6, -17.8), (9.6, 1.0, 2.4), (0, -16, 0), (3.4, 0.0, -0.8), 0.013, 0.22),
            ("cloud_soft", (-5.0, 13.0, 5.6), (6.2, 1.0, 2.8), (0, 42, 0), (2.2, 0.0, -1.4), 0.009, 0.48),
            ("cloud_streak", (13.8, 10.8, 4.4), (7.2, 1.0, 2.0), (0, -36, 0), (2.7, 0.0, -1.2), 0.015, 0.68),
            ("cloud_soft", (-15.6, 12.0, 11.6), (5.8, 1.0, 2.5), (0, 8, 0), (2.4, 0.0, -0.7), 0.011, 0.86),
        ]
        atmosphere = app.season_controller.atmosphere_state()
        cloud_tint = atmosphere["cloud_color"]
        for texture_name, pos, scale, rot, travel, speed, phase in cloud_specs:
            add(
                CloudLayer(
                    app,
                    pos=pos,
                    rot=rot,
                    scale=scale,
                    texture_name=texture_name,
                    tint=cloud_tint,
                    repeat=(1.0, 1.0),
                    alpha=0.70,
                    travel=travel,
                    speed=speed,
                    phase=phase,
                )
            )

    def add_emotional_transition(self, app):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return

        add = self.add_object
        from_season = transition["from"]
        to_season = transition["to"]
        progress = transition["progress"]
        eased = transition["eased"]
        from_color = from_season.get("transition_color", (1.0, 1.0, 1.0))
        to_color = to_season.get("transition_color", (1.0, 1.0, 1.0))
        secondary = to_season.get("transition_secondary_color", to_color)

        def blend(a, b, t):
            return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(3))

        veil_color = blend(from_color, to_color, eased)

        # A soft memory glow above the lake during the handoff between seasons.
        for layer in range(4):
            add(
                SunDisc(
                    app,
                    pos=(0.0, 4.2 + layer * 0.10, 4.8 - layer * 0.05),
                    scale=(3.6 + layer * 0.9, 1.05 + layer * 0.26, 1.0),
                    color=veil_color if layer % 2 == 0 else secondary,
                    alpha=max(0.045, 0.14 - layer * 0.026),
                )
            )

        # Particles move as if the old season is being carried into the new one.
        for i in range(42):
            angle = i * 0.47 + progress * math.pi * 1.6
            radius = 3.3 + (i % 9) * 0.46
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            y = 0.75 + (i % 6) * 0.28 + 0.45 * eased
            particle_color = blend(from_color, to_color, (i % 7) / 6.0)
            add(
                WindStreak(
                    app,
                    pos=(x, y, z),
                    rot=(0, 58 + i * 8.0, 12 * math.sin(angle)),
                    scale=(0.070 + 0.018 * (i % 3), 0.009, 0.028),
                    color=particle_color,
                    travel=(1.60 + eased * 0.65, 0.0, -0.72 - eased * 0.35),
                    speed=0.20 + eased * 0.08 + (i % 4) * 0.010,
                    phase=(i * 0.061 + progress * 0.35) % 1.0,
                    bob=0.20 + eased * 0.12,
                )
            )

        # Ground trail: a quiet visual "before and after" along the road.
        for i in range(18):
            t = i / 17.0
            angle = math.radians(205 + i * 8.4)
            radius = 8.35 + 0.12 * math.sin(i)
            add(
                ColorCube(
                    app,
                    pos=(math.cos(angle) * radius, 0.044, math.sin(angle) * radius),
                    rot=(0, math.degrees(angle), 0),
                    scale=(0.075, 0.012, 0.040),
                    color=blend(from_color, to_color, t),
                )
            )

        self.add_story_transition(app, transition)

    def add_story_transition(self, app, transition):
        pair = transition["pair"]

        if pair == "spring->summer":
            self.add_spring_to_summer_heat(app, transition)
        elif pair == "summer->autumn":
            self.add_summer_to_autumn_fall(app, transition)
        elif pair == "autumn->winter":
            self.add_autumn_to_winter_snow(app, transition)
        elif pair == "winter->spring":
            self.add_winter_to_spring_thaw(app, transition)

    def add_spring_to_summer_heat(self, app, transition):
        add = self.add_object
        heat_yellow = (1.00, 0.86, 0.20)
        heat_orange = (1.00, 0.38, 0.08)
        dry_grass = (0.62, 0.52, 0.18)

        for layer in range(5):
            add(
                SunDisc(
                    app,
                    pos=(10.8, 13.8, -14.4 - layer * 0.05),
                    scale=(1.75 + layer * 0.55, 1.75 + layer * 0.55, 1.0),
                    color=heat_yellow if layer % 2 == 0 else heat_orange,
                    alpha=0.10 + layer * 0.015,
                )
            )

        # Heat shimmer rises from the ground as the spring air becomes too hot.
        for i in range(38):
            col = i % 10
            row = i // 10
            x = -8.2 + col * 1.82 + 0.22 * math.sin(i * 1.4)
            z = -5.8 + row * 2.85 + 0.30 * math.cos(i * 1.1)
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.12, z),
                    end_pos=(x + 0.12 * math.sin(i), 0.68 + (i % 5) * 0.12, z),
                    rot=(0, 18 + i * 11.0, 0),
                    scale=(0.010, 0.020, 0.010),
                    end_scale=(0.026 + 0.006 * (i % 3), 0.42 + 0.08 * (i % 4), 0.012),
                    color=heat_yellow,
                    end_color=heat_orange,
                    progress_start=0.03 + (i % 5) * 0.035,
                    progress_end=0.78 + (i % 3) * 0.040,
                    pulse=0.18,
                )
            )

        # Small dry patches show the heat wave touching the garden.
        for i in range(24):
            angle = math.radians(25 + i * 13.0)
            radius = 6.35 + 3.65 * ((i * 29) % 100) / 100.0
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.032, z),
                    rot=(0, i * 31.0, 0),
                    scale=(0.020, 0.004, 0.014),
                    end_scale=(0.18 + 0.04 * (i % 3), 0.006, 0.10 + 0.03 * (i % 2)),
                    color=(0.42, 0.68, 0.24),
                    end_color=dry_grass,
                    progress_start=0.24 + (i % 4) * 0.035,
                    progress_end=0.96,
                )
            )

    def add_summer_to_autumn_fall(self, app, transition):
        add = self.add_object
        leaf_colors = [
            (0.82, 0.32, 0.08),
            (0.94, 0.52, 0.12),
            (0.62, 0.22, 0.08),
            (0.88, 0.66, 0.18),
            (0.50, 0.28, 0.10),
        ]

        # Leaves begin green, then turn brittle while falling toward the path.
        for i in range(86):
            angle = math.radians((i * 17.0 + 28.0) % 360.0)
            radius = 3.7 + (i % 9) * 0.70
            start_x = math.cos(angle) * radius
            start_z = math.sin(angle) * radius
            drift = 0.75 + 0.35 * math.sin(i * 1.7)
            end_x = start_x + math.cos(angle + 0.9) * drift
            end_z = start_z + math.sin(angle - 0.6) * drift
            start = 0.02 + (i % 11) * 0.045
            end = min(1.0, start + 0.48 + (i % 4) * 0.05)
            add(
                TransitionCube(
                    app,
                    pos=(start_x, 2.25 + (i % 8) * 0.27, start_z),
                    end_pos=(end_x, 0.040 + (i % 3) * 0.004, end_z),
                    rot=(0, 36 + i * 13.0, 16 * math.sin(i)),
                    scale=(0.046, 0.006, 0.020),
                    end_scale=(0.058, 0.004, 0.024),
                    color=(0.38, 0.58, 0.20),
                    end_color=leaf_colors[i % len(leaf_colors)],
                    progress_start=start,
                    progress_end=end,
                    pulse=0.06,
                )
            )

        # Summer flowers bend down and lose their color.
        for i in range(28):
            angle = math.radians(118 + i * 5.5)
            radius = 7.20 + 0.42 * math.sin(i * 1.4)
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            start = 0.16 + (i % 5) * 0.045
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.15, z),
                    end_pos=(x + 0.055 * math.sin(i), 0.080, z + 0.040 * math.cos(i)),
                    rot=(18, math.degrees(angle), 20),
                    scale=(0.018, 0.16, 0.012),
                    end_scale=(0.014, 0.055, 0.010),
                    color=(0.38, 0.66, 0.24),
                    end_color=(0.48, 0.34, 0.14),
                    progress_start=start,
                    progress_end=0.92,
                )
            )
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.35, z),
                    end_pos=(x + 0.070 * math.sin(i), 0.13, z + 0.050 * math.cos(i)),
                    rot=(0, i * 29.0, 25),
                    scale=(0.058, 0.018, 0.058),
                    end_scale=(0.030, 0.008, 0.030),
                    color=(1.00, 0.84, 0.20),
                    end_color=(0.55, 0.30, 0.10),
                    progress_start=start + 0.10,
                    progress_end=0.98,
                )
            )

    def add_autumn_to_winter_snow(self, app, transition):
        add = self.add_object
        snow = (0.94, 0.97, 1.00)
        snow_shadow = (0.76, 0.86, 0.94)

        # First snow: sparse flakes at first, staggered so they arrive little by little.
        for i in range(96):
            col = i % 12
            row = i // 12
            x = -9.2 + col * 1.65 + 0.34 * math.sin(i * 1.9)
            z = -7.4 + row * 1.82 + 0.31 * math.cos(i * 1.2)
            start = (i % 14) * 0.040
            end = min(1.0, start + 0.35 + (i % 4) * 0.040)
            add(
                TransitionCube(
                    app,
                    pos=(x, 5.8 + (i % 7) * 0.34, z),
                    end_pos=(x + 0.28 * math.sin(i), 0.070 + (i % 4) * 0.006, z - 0.22),
                    rot=(0, i * 37.0, 0),
                    scale=(0.018, 0.018, 0.018),
                    end_scale=(0.040 + 0.006 * (i % 3), 0.006, 0.034),
                    color=snow,
                    end_color=snow if i % 3 else snow_shadow,
                    progress_start=start,
                    progress_end=end,
                    pulse=0.05,
                )
            )

        # Accumulation starts as tiny cold marks, then spreads over leaves and paths.
        for i in range(48):
            angle = math.radians(i * 360.0 / 48.0 + 5.0)
            radius = 5.95 + 4.10 * ((i * 23) % 100) / 100.0
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.038, z),
                    rot=(0, i * 27.0, 0),
                    scale=(0.020, 0.004, 0.016),
                    end_scale=(0.28 + 0.06 * (i % 3), 0.010, 0.16 + 0.04 * (i % 2)),
                    color=snow_shadow,
                    end_color=snow,
                    progress_start=0.22 + (i % 6) * 0.045,
                    progress_end=1.0,
                )
            )

        for i in range(20):
            angle = math.radians(210 + i * 5.8)
            radius = 6.12 + 0.70 * math.sin(i * 0.45) ** 2
            add(
                TransitionCube(
                    app,
                    pos=(math.cos(angle) * radius, 0.052, math.sin(angle) * radius),
                    rot=(0, i * 19.0, 0),
                    scale=(0.035, 0.006, 0.020),
                    end_scale=(0.26, 0.030, 0.16),
                    color=(0.82, 0.44, 0.18),
                    end_color=snow,
                    progress_start=0.42 + (i % 3) * 0.035,
                    progress_end=1.0,
                )
            )

    def add_winter_to_spring_thaw(self, app, transition):
        add = self.add_object
        snow = (0.94, 0.97, 1.00)
        puddle = (0.30, 0.58, 0.66)
        sprout = (0.38, 0.74, 0.28)

        # Snow caps collapse into small blue puddles before the spring scene takes over.
        for i in range(44):
            angle = math.radians(i * 360.0 / 44.0 + 12.0)
            radius = 5.75 + 4.85 * ((i * 31) % 100) / 100.0
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            start = (i % 7) * 0.030
            add(
                TransitionCube(
                    app,
                    pos=(x, 0.056, z),
                    rot=(0, i * 33.0, 0),
                    scale=(0.24 + 0.05 * (i % 3), 0.030, 0.16 + 0.04 * (i % 2)),
                    end_scale=(0.060, 0.004, 0.036),
                    color=snow,
                    end_color=puddle,
                    progress_start=start,
                    progress_end=0.62 + (i % 3) * 0.05,
                )
            )
            add(
                TransitionCube(
                    app,
                    pos=(x + 0.04 * math.sin(i), 0.030, z + 0.04 * math.cos(i)),
                    rot=(0, i * 21.0, 0),
                    scale=(0.020, 0.003, 0.014),
                    end_scale=(0.16 + 0.04 * (i % 2), 0.004, 0.10 + 0.03 * (i % 3)),
                    color=puddle,
                    end_color=(0.16, 0.42, 0.50),
                    progress_start=0.18 + (i % 5) * 0.030,
                    progress_end=0.78,
                )
            )

        # New sprouts and blossoms rise after the melt.
        bloom_colors = [
            ((1.00, 0.62, 0.84), (1.00, 0.82, 0.94), (0.96, 0.78, 0.24)),
            ((0.86, 0.54, 1.00), (1.00, 0.78, 0.96), (0.98, 0.86, 0.26)),
            ((1.00, 0.76, 0.32), (1.00, 0.92, 0.52), (0.45, 0.28, 0.10)),
        ]
        for i in range(32):
            angle = math.radians(40 + i * 8.4)
            radius = 6.15 + 1.25 * math.sin(i * 0.9) ** 2
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            outer, inner, center = bloom_colors[i % len(bloom_colors)]
            start = 0.36 + (i % 6) * 0.040
            self.add_transition_bloom(
                app,
                x,
                z,
                start,
                0.82 + 0.10 * math.sin(i),
                outer,
                inner,
                center,
                sprout,
                angle + i * 0.17,
            )

    def add_transition_bloom(
        self,
        app,
        x,
        z,
        progress_start,
        scale,
        outer_color,
        inner_color,
        center_color,
        stem_color,
        spin,
    ):
        add = self.add_object
        bloom_y = 0.22 * scale
        add(
            TransitionCube(
                app,
                pos=(x, 0.055, z),
                end_pos=(x, 0.11 * scale, z),
                rot=(10, math.degrees(spin), 14),
                scale=(0.010, 0.010, 0.008),
                end_scale=(0.016 * scale, 0.120 * scale, 0.010 * scale),
                color=stem_color,
                end_color=stem_color,
                progress_start=progress_start,
                progress_end=min(1.0, progress_start + 0.34),
            )
        )
        for petal_idx in range(5):
            petal_angle = spin + petal_idx * (math.tau / 5.0)
            petal_color = outer_color if petal_idx % 2 == 0 else inner_color
            end_x = x + math.cos(petal_angle) * 0.055 * scale
            end_z = z + math.sin(petal_angle) * 0.055 * scale
            add(
                TransitionCube(
                    app,
                    pos=(x, bloom_y, z),
                    end_pos=(end_x, bloom_y + 0.020 * scale, end_z),
                    rot=(18, math.degrees(petal_angle), 28),
                    scale=(0.006, 0.004, 0.006),
                    end_scale=(0.040 * scale, 0.010 * scale, 0.020 * scale),
                    color=inner_color,
                    end_color=petal_color,
                    progress_start=min(1.0, progress_start + 0.12),
                    progress_end=min(1.0, progress_start + 0.52),
                    pulse=0.05,
                )
            )
        add(
            TransitionCube(
                app,
                pos=(x, bloom_y, z),
                end_pos=(x, bloom_y + 0.018 * scale, z),
                rot=(0, math.degrees(spin), 0),
                scale=(0.006, 0.004, 0.006),
                end_scale=(0.022 * scale, 0.012 * scale, 0.022 * scale),
                color=center_color,
                end_color=center_color,
                progress_start=min(1.0, progress_start + 0.18),
                progress_end=min(1.0, progress_start + 0.48),
            )
        )

    def add_emotional_season_marks(self, app, pond_radius_scale):
        add = self.add_object
        effect = self.season_value("seasonal_effect", "spring")
        accent = self.season_color("transition_color", (1.0, 1.0, 1.0))
        secondary = self.season_color("transition_secondary_color", accent)

        if effect == "spring":
            # Small sprouts: the first stage of life.
            for i in range(16):
                angle = math.radians(35 + i * 8.0)
                radius = 7.05 + 0.30 * math.sin(i * 1.4)
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.075, z),
                        rot=(18, math.degrees(angle), 18),
                        scale=(0.020, 0.080, 0.010),
                        color=(0.42, 0.72, 0.28),
                    )
                )
                self.add_garden_flower(
                    app,
                    (x + 0.060 * math.cos(angle + 0.8), z + 0.060 * math.sin(angle + 0.8)),
                    accent,
                    (1.00, 0.82, 0.92),
                    (0.98, 0.82, 0.30),
                    scale=0.72,
                    spin=angle,
                )

        elif effect == "summer":
            # Firefly-like sparks: youth, movement, courage.
            for i in range(28):
                angle = math.radians(i * 19.0)
                radius = 5.7 + (i % 6) * 0.62
                add(
                    WindStreak(
                        app,
                        pos=(
                            math.cos(angle) * radius,
                            0.82 + (i % 5) * 0.22,
                            math.sin(angle) * radius,
                        ),
                        rot=(0, 42 + i * 5.0, 0),
                        scale=(0.035, 0.010, 0.020),
                        color=accent if i % 2 else secondary,
                        travel=(0.55, 0.0, -0.32),
                        speed=0.11 + (i % 3) * 0.016,
                        phase=(i * 0.097) % 1.0,
                        bob=0.18,
                    )
                )

        elif effect == "autumn":
            # Lanterns and memory leaves: maturity and letting go.
            for i, angle_deg in enumerate((196, 214, 232, 250, 268)):
                angle = math.radians(angle_deg)
                x = math.cos(angle) * 8.15
                z = math.sin(angle) * 8.15
                self.add_garden_lantern(app, (x, z), scale=0.62, yaw=angle_deg)
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.96, z),
                        rot=(0, angle_deg, 0),
                        scale=(0.11, 0.045, 0.11),
                        color=accent if i % 2 else secondary,
                    )
                )

        elif effect == "winter":
            # Quiet warm lights: solitude, memory, and acceptance.
            warm = (1.00, 0.74, 0.36)
            for i, angle_deg in enumerate((215, 238, 265, 292)):
                angle = math.radians(angle_deg)
                x = math.cos(angle) * 7.75
                z = math.sin(angle) * 7.75
                add(
                    SunDisc(
                        app,
                        pos=(x, 0.82 + 0.08 * (i % 2), z + 0.02),
                        scale=(0.16, 0.16, 1.0),
                        color=warm,
                        alpha=0.72,
                    )
                )
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.32, z),
                        scale=(0.045, 0.19, 0.045),
                        color=(0.36, 0.30, 0.24),
                    )
                )

    def add_sun(self, app):
        if not self.season_value("sun_enabled", True):
            return

        add = self.add_object
        sun_scale = self.season_value("sun_scale", 1.0)
        core_radius = 0.72 * sun_scale

        halo_layers = [
            (3.50, 0.055, 0.01),
            (2.75, 0.075, 0.04),
            (2.05, 0.110, 0.07),
            (1.45, 0.180, 0.10),
        ]
        for radius_mul, alpha, z_offset in halo_layers:
            add(
                AtmosphereSunDisc(
                    app,
                    center_offset=(0.0, 0.0, -0.18 + z_offset),
                    scale=(core_radius * radius_mul, core_radius * radius_mul, 1.0),
                    alpha=alpha,
                    color_role="ray",
                )
            )

        for ray_idx in range(18):
            angle = ray_idx * (360.0 / 18.0)
            angle_rad = math.radians(angle)
            ray_len = core_radius * (1.25 + 0.32 * math.sin(ray_idx * 1.7) ** 2)
            ray_width = core_radius * (0.10 + 0.04 * (ray_idx % 3 == 0))
            offset = core_radius * (1.44 + 0.11 * (ray_idx % 2))
            ray_alpha = 0.16 if ray_idx % 2 == 0 else 0.10
            add(
                AtmosphereSunDisc(
                    app,
                    center_offset=(math.cos(angle_rad) * offset, math.sin(angle_rad) * offset, -0.08),
                    rot=(0, 0, angle - 90.0),
                    scale=(ray_width, ray_len, 1.0),
                    alpha=ray_alpha,
                    color_role="ray",
                )
            )

        add(
            AtmosphereSunDisc(
                app,
                center_offset=(0.0, 0.0, 0.02),
                scale=(core_radius * 1.08, core_radius * 1.08, 1.0),
                alpha=0.92,
                color_role="ray",
            )
        )
        add(
            AtmosphereSunDisc(
                app,
                center_offset=(0.0, 0.0, 0.04),
                scale=(core_radius * 0.82, core_radius * 0.82, 1.0),
                alpha=1.0,
                color_role="sun",
            )
        )
        add(
            AtmosphereSunDisc(
                app,
                center_offset=(-core_radius * 0.16, core_radius * 0.18, 0.06),
                scale=(core_radius * 0.34, core_radius * 0.34, 1.0),
                alpha=0.72,
                color_role="warm",
            )
        )

    def add_wind(self, app):
        if not self.season_value("wind_enabled", True):
            return

        add = self.add_object
        strength = self.season_value("wind_strength", 0.7)
        wind_color = self.season_color("wind_color", (0.86, 0.94, 0.95))
        streak_count = int(14 + strength * 12)

        for i in range(streak_count):
            lane = i % 7
            band = i // 7
            x = -9.5 + lane * 3.0 + 0.4 * math.sin(i * 1.3)
            z = -6.5 + band * 3.2 + 0.8 * math.cos(i * 0.7)
            y = 1.15 + (i % 4) * 0.34 + 0.12 * math.sin(i)
            yaw = 65 + 7.0 * math.sin(i * 0.9)

            add(
                WindStreak(
                    app,
                    pos=(x, y, z),
                    rot=(0, yaw, 0),
                    scale=(
                        (0.28 + 0.05 * (i % 3)) * strength,
                        0.010 + 0.003 * (i % 2),
                        0.015,
                    ),
                    color=wind_color,
                    travel=(1.25 * strength, 0.0, -0.58 * strength),
                    speed=0.14 + 0.035 * strength + (i % 5) * 0.006,
                    phase=(i * 0.137) % 1.0,
                    bob=0.08 + strength * 0.06,
                )
            )

        leaf_color = self.season_color("floating_petal_color", (1.00, 0.64, 0.84))
        for i in range(int(10 + strength * 10)):
            angle = i * 0.73
            add(
                WindStreak(
                    app,
                    pos=(
                        math.cos(angle) * (4.0 + (i % 5) * 1.05),
                        0.58 + (i % 4) * 0.18,
                        math.sin(angle) * (4.2 + (i % 5) * 1.00),
                    ),
                    rot=(0, 48 + i * 11.0, 18),
                    scale=(0.045, 0.007, 0.020),
                    color=leaf_color,
                    travel=(0.82 * strength, 0.0, -0.44 * strength),
                    speed=0.16 + 0.025 * strength,
                    phase=(i * 0.211) % 1.0,
                    bob=0.18,
                )
            )

    def add_rain(self, app):
        if not self.season_value("rain_enabled", False):
            return

        add = self.add_object
        rain_count = self.season_value("rain_count", 42)
        rain_color = self.season_color("rain_color", (0.56, 0.74, 0.88))
        rain_speed = self.season_value("rain_speed", 0.30)
        puddle_color = self.season_color("rain_puddle_color", (0.18, 0.38, 0.48))
        wind_strength = self.season_value("wind_strength", 0.7)

        for i in range(rain_count):
            col = i % 11
            row = i // 11
            x = -8.6 + col * 1.7 + 0.42 * math.sin(i * 1.9)
            z = -7.4 + row * 1.9 + 0.36 * math.cos(i * 1.1)
            y = 6.4 + (i % 7) * 0.38
            add(
                RainDrop(
                    app,
                    pos=(x, y, z),
                    rot=(18, 18 + wind_strength * 18.0, -15),
                    scale=(0.010, 0.34 + 0.08 * (i % 3), 0.010),
                    color=rain_color,
                    fall_distance=6.2 + (i % 4) * 0.55,
                    speed=rain_speed + (i % 5) * 0.015,
                    phase=(i * 0.071) % 1.0,
                    drift=(0.34 * wind_strength, 0.0, -0.22 * wind_strength),
                )
            )

        for i in range(max(6, rain_count // 8)):
            angle = i * 1.21
            radius = 5.7 + (i % 5) * 0.86
            add(
                ColorPlane(
                    app,
                    pos=(math.cos(angle) * radius, 0.019, math.sin(angle) * radius),
                    rot=(0, i * 29.0, 0),
                    scale=(0.22 + 0.04 * (i % 3), 1, 0.12 + 0.03 * (i % 2)),
                    color=puddle_color,
                )
            )

    def add_autumn_leaf_scatter(self, app):
        add = self.add_object
        leaf_colors = self.season_value(
            "autumn_leaf_colors",
            [
                (0.78, 0.26, 0.08),
                (0.94, 0.50, 0.13),
                (0.62, 0.20, 0.08),
                (0.86, 0.64, 0.18),
            ],
        )
        density = self.season_value("autumn_leaf_density", 260)

        # Ground scatter: leaves fall across the road, garden, yards, and pond edge.
        for i in range(density):
            zone = i % 6
            seed = i * 1.618

            if zone == 0:
                angle = math.radians((i * 13.0 + 18.0) % 360.0)
                radius = 8.15 + 1.10 * ((i * 37) % 100) / 100.0
            elif zone == 1:
                angle = math.radians(205.0 + ((i * 7.0) % 105.0))
                radius = 6.25 + 2.05 * ((i * 29) % 100) / 100.0
            elif zone == 2:
                angle = math.radians((i * 19.0 + 9.0) % 360.0)
                radius = 5.72 + 0.82 * ((i * 43) % 100) / 100.0
            elif zone == 3:
                angle = math.radians((i * 11.0 + 31.0) % 360.0)
                radius = 10.05 + 2.35 * ((i * 23) % 100) / 100.0
            elif zone == 4:
                angle = math.radians((i * 17.0 + 145.0) % 360.0)
                radius = 7.05 + 1.55 * ((i * 31) % 100) / 100.0
            else:
                angle = math.radians((i * 23.0 + 74.0) % 360.0)
                radius = 9.20 + 3.10 * ((i * 17) % 100) / 100.0

            x = math.cos(angle) * radius + 0.16 * math.sin(seed * 2.1)
            z = math.sin(angle) * radius + 0.16 * math.cos(seed * 1.7)
            color = leaf_colors[i % len(leaf_colors)]
            scale_x = 0.038 + 0.030 * (0.5 + 0.5 * math.sin(seed))
            scale_z = 0.016 + 0.020 * (0.5 + 0.5 * math.cos(seed * 1.3))
            y = 0.030 + 0.002 * (i % 4)

            add(
                ColorCube(
                    app,
                    pos=(x, y, z),
                    rot=(0, (i * 47.0) % 360.0, 4.0 * math.sin(seed)),
                    scale=(scale_x, 0.004, scale_z),
                    color=color,
                )
            )

        # Thicker leaf piles where wind would naturally gather them.
        pile_specs = []
        for i in range(34):
            pile_specs.append(((i * 360.0 / 34.0) + 4.0, 8.88 + 0.12 * math.sin(i), 1.0))
        for i in range(18):
            pile_specs.append((210.0 + i * 5.8, 6.18 + 0.12 * math.cos(i), 0.78))
        for i in range(12):
            pile_specs.append((225.0 + i * 6.5, 7.55 + 0.22 * math.sin(i * 0.7), 0.92))

        for i, (angle_deg, radius, size) in enumerate(pile_specs):
            angle = math.radians(angle_deg)
            color = leaf_colors[(i * 2) % len(leaf_colors)]
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.050 + 0.008 * size, math.sin(angle) * radius),
                    rot=(0, angle_deg + i * 17.0, 0),
                    scale=(0.20 * size, 0.038 * size, 0.14 * size),
                    color=color,
                )
            )

        # A few leaves still falling, so the map feels alive rather than simply carpeted.
        for i in range(44):
            angle = math.radians((i * 21.0 + 35.0) % 360.0)
            radius = 4.5 + (i % 8) * 0.90
            color = leaf_colors[(i + 1) % len(leaf_colors)]
            add(
                WindStreak(
                    app,
                    pos=(
                        math.cos(angle) * radius,
                        0.78 + (i % 7) * 0.24,
                        math.sin(angle) * radius,
                    ),
                    rot=(0, 52 + i * 9.0, 16 * math.sin(i)),
                    scale=(0.050, 0.007, 0.022),
                    color=color,
                    travel=(1.10, 0.0, -0.58),
                    speed=0.18 + (i % 5) * 0.012,
                    phase=(i * 0.083) % 1.0,
                    bob=0.24,
                )
            )

    def add_summer_fireflies(self, app, pond_radius_scale):
        if self.season_value("seasonal_effect", "") != "summer":
            return

        add = self.add_object
        firefly_color = (1.00, 0.96, 0.42)

        for i in range(34):
            angle = math.radians(i * 137.5)
            radius = 0.62 + (i % 9) * 0.18
            center = (
                math.cos(angle) * radius,
                0.82 + (i % 7) * 0.17,
                math.sin(angle) * radius,
            )
            add(
                FireflyGlow(
                    app,
                    center=center,
                    orbit=(0.18 + (i % 4) * 0.035, 0.12 + (i % 5) * 0.018, 0.20 + (i % 3) * 0.040),
                    scale=(0.028, 0.028, 1.0),
                    color=firefly_color,
                    alpha=0.66,
                    speed=0.13 + (i % 6) * 0.018,
                    phase=(i * 0.079) % 1.0,
                )
            )

        for i in range(40):
            angle = math.radians(i * 31.0 + 8.0 * math.sin(i))
            radius = (3.45 + (i % 10) * 0.19 + 0.18 * math.sin(i * 1.3)) * pond_radius_scale
            center = (
                math.cos(angle) * radius,
                0.40 + (i % 6) * 0.13,
                math.sin(angle) * radius,
            )
            add(
                FireflyGlow(
                    app,
                    center=center,
                    orbit=(0.28 + (i % 5) * 0.045, 0.11 + (i % 4) * 0.025, 0.28 + (i % 6) * 0.036),
                    scale=(0.023, 0.023, 1.0),
                    color=firefly_color,
                    alpha=0.56,
                    speed=0.10 + (i % 7) * 0.016,
                    phase=(i * 0.061 + 0.21) % 1.0,
                )
            )

    def add_seasonal_effects(self, app, pond_radius_scale):
        add = self.add_object
        effect = self.season_value("seasonal_effect", "spring")

        if effect == "winter":
            snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
            snow_shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
            add(
                IceSurface(
                    app,
                    pos=(0, 0.062, 0),
                    scale=(1.0, 1.0, 1.0),
                    color=(0.70, 0.88, 0.96),
                )
            )

            for i in range(62):
                angle = math.radians(i * 17.0 + 7.0)
                radius = 5.80 + 6.60 * ((i * 37) % 100) / 100.0
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    TexturedPlane(
                        app,
                        pos=(x, 0.018 + 0.002 * (i % 3), z),
                        rot=(0, i * 31.0, 0),
                        scale=(
                            0.42 + 0.42 * math.sin(i * 1.7) ** 2,
                            1,
                            0.24 + 0.28 * math.cos(i * 1.2) ** 2,
                        ),
                        texture_name="snow",
                        tint=snow,
                        repeat=(1.0, 1.0),
                    )
                )

            # Snowbanks around the lake edge and the circular road.
            for i in range(44):
                angle = math.radians(i * 360.0 / 44.0)
                for radius, scale_mul in ((6.20 + 0.16 * math.sin(i), 1.0), (8.95 + 0.10 * math.cos(i), 1.28)):
                    add(
                        PondRock(
                            app,
                            pos=(math.cos(angle) * radius, 0.080, math.sin(angle) * radius),
                            rot=(0, i * 29.0, 0),
                            scale=(
                                (0.23 + 0.05 * math.sin(i * 0.8)) * scale_mul,
                                (0.062 + 0.018 * math.cos(i * 1.3)) * scale_mul,
                                (0.16 + 0.04 * math.cos(i)) * scale_mul,
                            ),
                            color=snow if i % 3 else snow_shadow,
                        )
                    )

            for i in range(30):
                angle = math.radians(205 + i * 4.2)
                radius = 7.10 + 0.92 * math.sin(i * 0.37) ** 2
                add(
                    PondRock(
                        app,
                        pos=(math.cos(angle) * radius, 0.115, math.sin(angle) * radius),
                        rot=(0, i * 23.0, 0),
                        scale=(0.30, 0.095, 0.22),
                        color=snow,
                    )
                )

            # Soft snow clumps on the central island and below the tree canopy.
            for i in range(18):
                angle = math.radians(i * 20.0)
                radius = 0.55 + 1.30 * ((i * 19) % 100) / 100.0
                add(
                    PondRock(
                        app,
                        pos=(math.cos(angle) * radius, 0.32, math.sin(angle) * radius),
                        rot=(0, i * 41.0, 0),
                        scale=(0.15, 0.040, 0.11),
                        color=snow,
                    )
                )

        elif effect == "autumn":
            self.add_autumn_leaf_scatter(app)

        elif effect == "summer":
            for i in range(18):
                angle = math.radians(120 + i * 7.0)
                radius = 7.40 + 0.35 * math.sin(i * 1.2)
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                self.add_garden_flower(
                    app,
                    (x, z),
                    (1.00, 0.88, 0.18),
                    (1.00, 0.62, 0.14),
                    (0.36, 0.21, 0.08),
                    scale=1.22,
                    spin=angle,
                )
            self.add_summer_fireflies(app, pond_radius_scale)

        else:
            for i in range(26):
                angle = math.radians(45 + i * 9.0)
                radius = (5.85 + 0.25 * math.sin(i * 1.6)) * pond_radius_scale
                add(
                    ColorCube(
                        app,
                        pos=(math.cos(angle) * radius, 0.030, math.sin(angle) * radius),
                        rot=(0, i * 43.0, 0),
                        scale=(0.030, 0.004, 0.018),
                        color=(1.00, 0.72, 0.88),
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

        house_specs = [
            (20, 11.4, (0.76, 0.61, 0.70), (0.71, 0.58, 0.42), (0.43, 0.12, 0.09), (0.83, 0.78, 0.65), -6, "cottage"),
            (44, 12.0, (0.88, 0.68, 0.76), (0.64, 0.54, 0.36), (0.36, 0.16, 0.12), (0.80, 0.73, 0.58), 4, "two_story"),
            (68, 11.7, (0.72, 0.60, 0.68), (0.76, 0.66, 0.48), (0.50, 0.18, 0.11), (0.88, 0.82, 0.66), -3, "l_shape"),
            (116, 11.8, (0.82, 0.65, 0.75), (0.67, 0.57, 0.43), (0.34, 0.18, 0.15), (0.80, 0.74, 0.60), 5, "split_level"),
            (142, 12.2, (0.92, 0.70, 0.80), (0.72, 0.61, 0.45), (0.45, 0.13, 0.10), (0.86, 0.79, 0.62), -4, "tower"),
            (166, 11.3, (0.74, 0.58, 0.68), (0.61, 0.52, 0.38), (0.38, 0.20, 0.13), (0.78, 0.70, 0.56), 6, "wide_veranda"),
            (206, 11.8, (0.86, 0.64, 0.74), (0.70, 0.55, 0.39), (0.46, 0.16, 0.10), (0.85, 0.77, 0.60), -5, "two_story"),
            (232, 12.3, (0.94, 0.72, 0.84), (0.66, 0.58, 0.42), (0.35, 0.15, 0.13), (0.82, 0.75, 0.59), 3, "l_shape"),
            (258, 11.6, (0.76, 0.60, 0.70), (0.73, 0.63, 0.47), (0.49, 0.17, 0.11), (0.88, 0.80, 0.64), -2, "cottage"),
            (288, 12.0, (0.88, 0.66, 0.78), (0.63, 0.53, 0.37), (0.39, 0.14, 0.10), (0.81, 0.72, 0.57), 5, "split_level"),
            (318, 11.5, (0.78, 0.62, 0.72), (0.74, 0.60, 0.43), (0.44, 0.15, 0.10), (0.86, 0.78, 0.61), -5, "tower"),
            (344, 12.2, (0.90, 0.68, 0.82), (0.68, 0.56, 0.40), (0.34, 0.17, 0.13), (0.82, 0.75, 0.58), 4, "wide_veranda"),
        ]

        for idx, (angle_deg, radius, body_scale, body_color, roof_color, trim_color, yaw_offset, variant) in enumerate(house_specs):
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

    def update(self):
        for obj in self.objects:
            obj.update()
