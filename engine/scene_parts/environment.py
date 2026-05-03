import math

from ..model import (
    AtmosphereSunDisc,
    AuroraBand,
    CloudLayer,
    ColorCube,
    ColorPlane,
    DriftParticle,
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


class SceneEnvironmentMixin:
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
        self.add_ambient_particles(app)
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

    def add_ambient_particles(self, app):
        add = self.add_object
        effect = self.season_value("seasonal_effect", "spring")
        count = int(self.season_value("ambient_particle_count", 44))
        if count <= 0:
            return

        wind_strength = self.season_value("wind_strength", 0.7)
        base_color = self.season_color("floating_petal_color", (1.00, 0.64, 0.84))
        leaf_colors = self.season_value("autumn_leaf_colors", [base_color])
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))

        for i in range(count):
            lane = i % 13
            row = i // 13
            x = -9.8 + lane * 1.65 + 0.35 * math.sin(i * 1.27)
            z = -7.9 + row * 1.42 + 0.48 * math.cos(i * 0.83)
            phase = (i * 0.067) % 1.0

            if effect == "winter":
                y = 4.4 + (i % 9) * 0.28
                add(
                    DriftParticle(
                        app,
                        pos=(x, y, z),
                        rot=(0, i * 19.0, 0),
                        scale=(0.018 + 0.004 * (i % 3), 0.018, 0.018),
                        color=snow if i % 3 else self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92)),
                        fall_distance=4.9 + (i % 5) * 0.34,
                        drift=(0.34 * wind_strength, 0.0, -0.24 * wind_strength),
                        speed=0.050 + (i % 5) * 0.004,
                        phase=phase,
                        spin_speed=34.0,
                        sway=0.34,
                    )
                )
            elif effect == "autumn":
                color = leaf_colors[i % len(leaf_colors)]
                y = 3.0 + (i % 8) * 0.34
                add(
                    DriftParticle(
                        app,
                        pos=(x, y, z),
                        rot=(10, i * 31.0, 24),
                        scale=(0.050, 0.006, 0.026),
                        color=color,
                        fall_distance=3.8 + (i % 6) * 0.32,
                        drift=(1.05 * wind_strength, 0.0, -0.62 * wind_strength),
                        speed=0.072 + (i % 6) * 0.006,
                        phase=phase,
                        spin_speed=160.0,
                        sway=0.48,
                    )
                )
            elif effect == "summer":
                y = 1.00 + (i % 7) * 0.24
                warm = (1.00, 0.82, 0.34) if i % 2 else (0.86, 0.95, 0.72)
                add(
                    DriftParticle(
                        app,
                        pos=(x * 0.82, y, z * 0.82),
                        rot=(0, i * 17.0, 0),
                        scale=(0.018, 0.010, 0.018),
                        color=warm,
                        fall_distance=0.95 + (i % 4) * 0.12,
                        drift=(0.28 * wind_strength, 0.0, -0.18 * wind_strength),
                        speed=0.036 + (i % 4) * 0.004,
                        phase=phase,
                        spin_speed=42.0,
                        sway=0.40,
                    )
                )
            else:
                y = 3.3 + (i % 8) * 0.30
                petal_color = base_color if i % 4 else (1.00, 0.82, 0.94)
                add(
                    DriftParticle(
                        app,
                        pos=(x, y, z),
                        rot=(12, i * 27.0, 22),
                        scale=(0.042, 0.005, 0.024),
                        color=petal_color,
                        fall_distance=3.6 + (i % 5) * 0.28,
                        drift=(0.72 * wind_strength, 0.0, -0.42 * wind_strength),
                        speed=0.060 + (i % 6) * 0.005,
                        phase=phase,
                        spin_speed=120.0,
                        sway=0.52,
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
