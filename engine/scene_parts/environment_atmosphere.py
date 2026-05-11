import math

from ..models import (
    AtmosphereSunDisc,
    ColorCube,
    ColorPlane,
    DriftParticle,
    FireflyGlow,
    IceSurface,
    PondRock,
    RainDrop,
    TexturedPlane,
    WindStreak,
)


class SceneAtmosphereEffectsMixin:
    def add_natural_elements(self, app):
        self.add_sun(app)
        self.add_night_lights(app)
        self.add_wind(app)
        self.add_ambient_particles(app)
        self.add_rain(app)

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
