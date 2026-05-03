import math

from ..model import ColorCube, ColorPlane, NightGlow, PondRock, SunDisc, TransitionCube, WindStreak


class SceneSeasonUpgradeMixin:
    def add_season_upgrades(self, app, pond_radius_scale):
        effect = self.season_value("seasonal_effect", "spring")
        self.add_season_pond_treatment(app, pond_radius_scale, effect)

        if effect == "spring":
            self.add_spring_identity_objects(app, pond_radius_scale)
        elif effect == "summer":
            self.add_summer_identity_objects(app, pond_radius_scale)
        elif effect == "autumn":
            self.add_autumn_identity_objects(app, pond_radius_scale)
        elif effect == "winter":
            self.add_winter_identity_objects(app, pond_radius_scale)

        self.add_transition_season_accents(app, pond_radius_scale)

    def add_season_pond_treatment(self, app, pond_radius_scale, effect):
        add = self.add_object
        if effect == "spring":
            petal = self.season_color("floating_petal_color", (1.0, 0.64, 0.84))
            pale = (1.0, 0.82, 0.94)
            for i in range(34):
                angle = math.radians(12 + i * 10.4)
                radius = (2.45 + (i % 5) * 0.33) * pond_radius_scale
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.070 + 0.002 * (i % 3), z),
                        rot=(0, math.degrees(angle) + i * 13.0, 0),
                        scale=(0.050, 0.004, 0.025),
                        color=petal if i % 3 else pale,
                    )
                )

            for i in range(5):
                add(
                    SunDisc(
                        app,
                        pos=(-4.0 + i * 1.8, 0.082, -3.4 + 0.28 * math.sin(i)),
                        rot=(90, i * 17.0, 0),
                        scale=(1.25 + 0.18 * (i % 2), 0.28, 1.0),
                        color=(0.92, 0.96, 1.0),
                        alpha=0.075,
                    )
                )

        elif effect == "summer":
            for i in range(22):
                angle = math.radians(i * 17.0 + 4.0)
                radius = (1.9 + (i % 7) * 0.42) * pond_radius_scale
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    SunDisc(
                        app,
                        pos=(x, 0.086, z),
                        rot=(90, math.degrees(angle), 0),
                        scale=(0.12 + 0.03 * (i % 3), 0.030, 1.0),
                        color=(1.0, 0.88, 0.34),
                        alpha=0.18,
                    )
                )
            for i in range(12):
                add(
                    WindStreak(
                        app,
                        pos=(-6.8 + i * 1.15, 0.36 + 0.03 * (i % 4), -0.9 + 0.34 * math.sin(i)),
                        rot=(0, 78 + i * 3.0, 0),
                        scale=(0.17, 0.007, 0.013),
                        color=(1.0, 0.84, 0.38),
                        travel=(0.24, 0.0, -0.10),
                        speed=0.09 + (i % 4) * 0.006,
                        phase=(i * 0.113) % 1.0,
                        bob=0.050,
                    )
                )

        elif effect == "autumn":
            leaves = self.season_value(
                "autumn_leaf_colors",
                [(0.82, 0.32, 0.08), (0.94, 0.52, 0.12), (0.62, 0.22, 0.08)],
            )
            for i in range(48):
                angle = math.radians(i * 13.0 + 20.0)
                radius = (2.15 + (i % 8) * 0.35) * pond_radius_scale
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.074 + 0.002 * (i % 4), z),
                        rot=(0, math.degrees(angle) + i * 29.0, 0),
                        scale=(0.060, 0.005, 0.026),
                        color=leaves[i % len(leaves)],
                    )
                )
            for i in range(8):
                angle = math.radians(190 + i * 13.0)
                radius = 5.45 * pond_radius_scale
                add(
                    PondRock(
                        app,
                        pos=(math.cos(angle) * radius, 0.100, math.sin(angle) * radius),
                        rot=(0, i * 24.0, 0),
                        scale=(0.28, 0.060, 0.18),
                        color=leaves[(i + 1) % len(leaves)],
                    )
                )

        elif effect == "winter":
            crack = (0.40, 0.58, 0.68)
            frost = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
            for i in range(18):
                angle = math.radians(i * 21.0 + 8.0)
                radius = (1.10 + (i % 6) * 0.45) * pond_radius_scale
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    ColorCube(
                        app,
                        pos=(x, 0.092, z),
                        rot=(0, math.degrees(angle) + 18.0 * math.sin(i), 0),
                        scale=(0.018, 0.004, 0.34 + 0.06 * (i % 3)),
                        color=crack,
                    )
                )
            for i in range(12):
                angle = math.radians(i * 30.0)
                radius = (4.75 + 0.16 * math.sin(i)) * pond_radius_scale
                add(
                    SunDisc(
                        app,
                        pos=(math.cos(angle) * radius, 0.102, math.sin(angle) * radius),
                        rot=(90, i * 12.0, 0),
                        scale=(0.42, 0.10, 1.0),
                        color=frost,
                        alpha=0.14,
                    )
                )

    def add_spring_identity_objects(self, app, pond_radius_scale):
        add = self.add_object
        umbrella_colors = [(1.0, 0.50, 0.74), (0.86, 0.62, 1.0), (1.0, 0.82, 0.44)]
        for idx, (x, z, yaw) in enumerate(((-8.1, 5.9, -18.0), (-5.9, 7.1, 24.0), (5.2, -7.1, 12.0))):
            add(ColorCube(app, pos=(x, 0.34, z), rot=(0, yaw, 0), scale=(0.018, 0.34, 0.018), color=(0.28, 0.17, 0.08)))
            for rib in range(6):
                angle = yaw + rib * 60.0
                add(
                    ColorCube(
                        app,
                        pos=(x + 0.12 * math.cos(math.radians(angle)), 0.72, z + 0.12 * math.sin(math.radians(angle))),
                        rot=(8, angle, 0),
                        scale=(0.20, 0.014, 0.050),
                        color=umbrella_colors[(idx + rib) % len(umbrella_colors)],
                    )
                )
            add(NightGlow(app, pos=(x, 0.74, z), scale=(0.20, 0.20, 1.0), color=(1.0, 0.62, 0.82), alpha=0.18, pulse=0.02))

        for i in range(24):
            angle = math.radians(35 + i * 7.8)
            radius = (6.7 + 0.28 * math.sin(i)) * pond_radius_scale
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            add(ColorCube(app, pos=(x, 0.14, z), rot=(18, math.degrees(angle), 8), scale=(0.016, 0.11, 0.010), color=(0.36, 0.66, 0.26)))
            add(ColorCube(app, pos=(x, 0.29, z), rot=(0, i * 31.0, 0), scale=(0.055, 0.018, 0.055), color=(1.0, 0.72, 0.90)))

    def add_summer_identity_objects(self, app, pond_radius_scale):
        add = self.add_object
        lantern_colors = [(0.92, 0.18, 0.10), (1.0, 0.78, 0.30), (0.18, 0.42, 0.72)]
        start_x, start_z = (-5.8, 9.2)
        for i in range(10):
            x = start_x + i * 0.74
            z = start_z + 0.18 * math.sin(i * 0.7)
            add(ColorCube(app, pos=(x, 1.26, z), rot=(0, 8, 0), scale=(0.030, 0.030, 0.36), color=(0.24, 0.14, 0.07)))
            add(ColorCube(app, pos=(x, 1.02, z), rot=(0, i * 7.0, 0), scale=(0.090, 0.12, 0.070), color=lantern_colors[i % len(lantern_colors)]))
            add(NightGlow(app, pos=(x, 1.02, z), scale=(0.24, 0.24, 1.0), color=(1.0, 0.66, 0.28), alpha=0.22, pulse=0.05))

        fan_x, fan_z = (7.0, 5.8)
        add(ColorCube(app, pos=(fan_x, 0.42, fan_z), scale=(0.020, 0.42, 0.020), color=(0.30, 0.18, 0.08)))
        for i in range(7):
            angle = -42 + i * 14.0
            add(ColorCube(app, pos=(fan_x + 0.09 * math.sin(i), 0.88, fan_z), rot=(0, angle, 18), scale=(0.15, 0.012, 0.040), color=(0.96, 0.76, 0.24) if i % 2 else (0.92, 0.22, 0.12)))

    def add_autumn_identity_objects(self, app, pond_radius_scale):
        add = self.add_object
        leaves = self.season_value("autumn_leaf_colors", [(0.82, 0.32, 0.08), (0.94, 0.52, 0.12)])
        pile_sites = [(-7.8, -5.8), (-3.2, 7.8), (6.6, 6.2), (8.2, -4.4)]
        for idx, (x, z) in enumerate(pile_sites):
            for i in range(10):
                angle = i * math.tau / 10.0
                add(
                    ColorCube(
                        app,
                        pos=(x + math.cos(angle) * 0.12, 0.055 + 0.006 * (i % 3), z + math.sin(angle) * 0.09),
                        rot=(0, i * 23.0, 0),
                        scale=(0.070, 0.008, 0.035),
                        color=leaves[(idx + i) % len(leaves)],
                    )
                )
            add(ColorCube(app, pos=(x - 0.34, 0.20, z + 0.12), rot=(0, idx * 18.0, 20), scale=(0.018, 0.20, 0.018), color=(0.36, 0.20, 0.08)))
            add(ColorCube(app, pos=(x - 0.24, 0.45, z + 0.05), rot=(0, idx * 18.0, 70), scale=(0.15, 0.012, 0.018), color=(0.72, 0.50, 0.20)))

        for i in range(18):
            angle = math.radians(225 + i * 5.5)
            radius = (7.0 + 0.42 * math.sin(i * 0.9)) * pond_radius_scale
            add(
                WindStreak(
                    app,
                    pos=(math.cos(angle) * radius, 0.70 + (i % 4) * 0.10, math.sin(angle) * radius),
                    rot=(0, 52 + i * 7.0, 18),
                    scale=(0.060, 0.007, 0.024),
                    color=leaves[i % len(leaves)],
                    travel=(1.10, 0.0, -0.52),
                    speed=0.17 + (i % 4) * 0.010,
                    phase=(i * 0.091) % 1.0,
                    bob=0.25,
                )
            )

    def add_winter_identity_objects(self, app, pond_radius_scale):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        for x, z, yaw in ((-4.0, -3.1, 16.0), (2.9, 4.9, -18.0), (8.9, -6.9, -30.0)):
            for i, local_x in enumerate((-0.20, 0.0, 0.20)):
                add(ColorCube(app, pos=(x + local_x, 0.86 - i * 0.04, z), rot=(0, yaw, 0), scale=(0.026, 0.20, 0.018), color=shadow))
            add(PondRock(app, pos=(x, 0.070, z), rot=(0, yaw, 0), scale=(0.34, 0.055, 0.24), color=snow))

        for i in range(26):
            angle = math.radians(175 + i * 7.4)
            radius = (6.3 + 0.32 * math.sin(i * 1.3)) * pond_radius_scale
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.105, math.sin(angle) * radius),
                    rot=(0, i * 29.0, 0),
                    scale=(0.23 + 0.03 * (i % 3), 0.070, 0.16),
                    color=snow if i % 2 else shadow,
                )
            )

    def add_transition_season_accents(self, app, pond_radius_scale):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return

        add = self.add_object
        pair = transition["pair"]
        if pair == "spring->summer":
            for i in range(14):
                x = -8.0 + i * 1.25
                add(
                    TransitionCube(
                        app,
                        pos=(x, 0.08, 6.8 + 0.16 * math.sin(i)),
                        end_pos=(x, 0.62 + 0.04 * (i % 3), 6.8),
                        rot=(0, i * 17.0, 0),
                        scale=(0.020, 0.020, 0.020),
                        end_scale=(0.040, 0.34, 0.014),
                        color=(1.0, 0.70, 0.88),
                        end_color=(1.0, 0.68, 0.12),
                        progress_start=0.10 + (i % 4) * 0.04,
                        progress_end=0.84,
                        pulse=0.12,
                    )
                )
        elif pair == "summer->autumn":
            colors = [(0.82, 0.32, 0.08), (0.94, 0.52, 0.12), (0.62, 0.22, 0.08)]
            for i in range(18):
                angle = math.radians(40 + i * 12.0)
                radius = (4.0 + (i % 6) * 0.55) * pond_radius_scale
                add(
                    TransitionCube(
                        app,
                        pos=(math.cos(angle) * radius, 2.1 + (i % 5) * 0.20, math.sin(angle) * radius),
                        end_pos=(math.cos(angle + 0.4) * radius, 0.065, math.sin(angle - 0.2) * radius),
                        rot=(0, i * 31.0, 18),
                        scale=(0.050, 0.006, 0.024),
                        end_scale=(0.065, 0.005, 0.028),
                        color=(0.42, 0.64, 0.22),
                        end_color=colors[i % len(colors)],
                        progress_start=(i % 6) * 0.05,
                        progress_end=0.92,
                        pulse=0.06,
                    )
                )
        elif pair == "autumn->winter":
            snow = (0.94, 0.97, 1.0)
            for i in range(16):
                angle = math.radians(190 + i * 7.0)
                radius = (5.9 + 0.4 * math.sin(i)) * pond_radius_scale
                add(
                    TransitionCube(
                        app,
                        pos=(math.cos(angle) * radius, 0.050, math.sin(angle) * radius),
                        rot=(0, i * 19.0, 0),
                        scale=(0.035, 0.006, 0.022),
                        end_scale=(0.32, 0.020, 0.18),
                        color=(0.86, 0.42, 0.14),
                        end_color=snow,
                        progress_start=0.24 + (i % 5) * 0.045,
                        progress_end=1.0,
                    )
                )
        elif pair == "winter->spring":
            for i in range(20):
                angle = math.radians(25 + i * 8.0)
                radius = (6.2 + 0.30 * math.sin(i * 0.8)) * pond_radius_scale
                x = math.cos(angle) * radius
                z = math.sin(angle) * radius
                add(
                    TransitionCube(
                        app,
                        pos=(x, 0.040, z),
                        end_pos=(x, 0.23, z),
                        rot=(14, math.degrees(angle), 18),
                        scale=(0.080, 0.006, 0.050),
                        end_scale=(0.018, 0.14, 0.012),
                        color=(0.86, 0.94, 1.0),
                        end_color=(0.36, 0.72, 0.28),
                        progress_start=0.12 + (i % 6) * 0.04,
                        progress_end=0.78,
                    )
                )
