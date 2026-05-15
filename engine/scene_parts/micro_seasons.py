import math

from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneMicroSeasonMixin:
    """Procedural detail layer for short seasonal sub-stages.

    These accents are intentionally asset-free. They keep every micro-season
    visually readable even when no new texture files are available.
    """

    def add_micro_season_accents(self, app, pond_radius_scale):
        micro = self.season_value("micro_season", "")
        method = getattr(self, f"add_{micro}_accents", None)
        if method is not None:
            method(app, pond_radius_scale)

    def _ring_position(self, angle_deg, radius, pond_radius_scale=1.0):
        angle = math.radians(angle_deg)
        return math.cos(angle) * radius * pond_radius_scale, math.sin(angle) * radius * pond_radius_scale

    def _add_puddle(self, app, x, z, yaw, scale_x, scale_z, alpha=0.14, color=(0.36, 0.62, 0.72)):
        self.add_object(
            SunDisc(
                app,
                pos=(x, 0.041, z),
                rot=(90, yaw, 0),
                scale=(scale_x, scale_z, 1.0),
                color=color,
                alpha=alpha,
            ),
            tag="micro_puddle",
            layer="water",
        )

    def _add_leaf_chip(self, app, x, z, yaw, color, scale=(0.065, 0.006, 0.028), y=0.058):
        self.add_object(
            ColorCube(app, pos=(x, y, z), rot=(0, yaw, 0), scale=scale, color=color),
            tag="micro_leaf",
            layer="vegetation",
        )

    def _add_sprout(self, app, x, z, yaw, height=0.13, color=(0.38, 0.72, 0.28)):
        self.add_object(
            ColorCube(
                app,
                pos=(x, 0.065 + height * 0.50, z),
                rot=(10, yaw, 14),
                scale=(0.014, height, 0.010),
                color=color,
            ),
            tag="micro_sprout",
            layer="vegetation",
        )
        self.add_object(
            ColorCube(
                app,
                pos=(x + 0.030 * math.cos(math.radians(yaw)), 0.108 + height, z + 0.030 * math.sin(math.radians(yaw))),
                rot=(18, yaw + 28, 24),
                scale=(0.052, 0.010, 0.020),
                color=(0.54, 0.84, 0.34),
            ),
            tag="micro_sprout_leaf",
            layer="vegetation",
        )

    def _add_flower(self, app, x, z, yaw, petal_color, center_color=(0.96, 0.80, 0.22), scale=1.0):
        stem_color = (0.34, 0.62, 0.24)
        self.add_object(
            ColorCube(
                app,
                pos=(x, 0.135 * scale, z),
                rot=(8, yaw, 10),
                scale=(0.012 * scale, 0.110 * scale, 0.010 * scale),
                color=stem_color,
            ),
            tag="micro_flower_stem",
            layer="vegetation",
        )
        for petal in range(5):
            petal_yaw = yaw + petal * 72.0
            px = x + math.cos(math.radians(petal_yaw)) * 0.050 * scale
            pz = z + math.sin(math.radians(petal_yaw)) * 0.050 * scale
            self.add_object(
                ColorCube(
                    app,
                    pos=(px, 0.245 * scale, pz),
                    rot=(18, petal_yaw, 26),
                    scale=(0.034 * scale, 0.010 * scale, 0.018 * scale),
                    color=petal_color,
                ),
                tag="micro_flower_petal",
                layer="vegetation",
            )
        self.add_object(
            ColorCube(
                app,
                pos=(x, 0.247 * scale, z),
                rot=(0, yaw, 0),
                scale=(0.018 * scale, 0.012 * scale, 0.018 * scale),
                color=center_color,
            ),
            tag="micro_flower_center",
            layer="vegetation",
        )

    def add_early_spring_accents(self, app, pond_radius_scale):
        # Thaw marks: blue puddles, thin remaining snow, and the first small sprouts.
        for i in range(18):
            angle = 18 + i * 17.0
            radius = 5.85 + (i % 5) * 0.62
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self._add_puddle(
                app,
                x,
                z,
                angle + i * 11.0,
                0.24 + 0.035 * (i % 3),
                0.090 + 0.025 * (i % 2),
                alpha=0.13,
            )
            if i % 2 == 0:
                self.add_object(
                    ColorPlane(
                        app,
                        pos=(x + 0.10 * math.sin(i), 0.045, z - 0.08 * math.cos(i)),
                        rot=(0, angle + 24, 0),
                        scale=(0.18, 1.0, 0.075),
                        color=(0.88, 0.94, 0.98),
                    ),
                    tag="micro_wet_snow_patch",
                    layer="terrain",
                )

        for i in range(30):
            angle = 38 + i * 7.8
            radius = 6.45 + 0.50 * math.sin(i * 1.25)
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self._add_sprout(app, x, z, angle + i * 13.0, height=0.075 + 0.018 * (i % 3))

    def add_hanami_accents(self, app, pond_radius_scale):
        # Peak bloom: dense petal carpet around the sakura and picnic side.
        petal_colors = [(1.00, 0.70, 0.88), (1.00, 0.82, 0.94), (0.96, 0.52, 0.78)]
        for i in range(78):
            angle = i * 137.5
            radius = 0.85 + (i % 12) * 0.42
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self._add_leaf_chip(
                app,
                x,
                z,
                angle + i * 19.0,
                petal_colors[i % len(petal_colors)],
                scale=(0.050, 0.004, 0.022),
                y=0.066 + 0.002 * (i % 4),
            )

        for i in range(18):
            x = -7.1 + i * 0.34
            z = 6.6 + 0.16 * math.sin(i * 0.7)
            self.add_object(
                ColorPlane(
                    app,
                    pos=(x, 0.050, z),
                    rot=(0, 18 + i * 5.0, 0),
                    scale=(0.085, 1.0, 0.035),
                    color=petal_colors[(i + 1) % len(petal_colors)],
                ),
                tag="micro_hanami_petal_mat",
                layer="vegetation",
            )

    def add_tsuyu_accents(self, app, pond_radius_scale):
        # Rainy season: puddles, hydrangea clusters, and soft blue-violet accents.
        for i in range(24):
            col = i % 6
            row = i // 6
            x = -7.5 + col * 2.85 + 0.25 * math.sin(i)
            z = -5.8 + row * 3.45 + 0.30 * math.cos(i * 0.9)
            self._add_puddle(
                app,
                x,
                z,
                28 + i * 17.0,
                0.32 + 0.04 * (i % 3),
                0.12 + 0.03 * (i % 2),
                alpha=0.16,
                color=(0.42, 0.62, 0.76),
            )

        cluster_colors = [(0.48, 0.50, 0.92), (0.58, 0.42, 0.82), (0.82, 0.72, 0.96)]
        for i in range(16):
            angle = 116 + i * 6.8
            radius = 7.0 + 0.24 * math.sin(i)
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            for bloom in range(5):
                yaw = angle + bloom * 72.0
                self.add_object(
                    PondRock(
                        app,
                        pos=(x + 0.09 * math.cos(math.radians(yaw)), 0.145 + 0.018 * (bloom % 2), z + 0.07 * math.sin(math.radians(yaw))),
                        rot=(0, yaw, 0),
                        scale=(0.075, 0.050, 0.060),
                        color=cluster_colors[(i + bloom) % len(cluster_colors)],
                    ),
                    tag="micro_hydrangea",
                    layer="vegetation",
                )

    def add_midsummer_accents(self, app, pond_radius_scale):
        # Festival peak: extra lantern glow, fireflies, and small firework sparks.
        lantern_colors = [(1.0, 0.30, 0.16), (1.0, 0.78, 0.28), (0.28, 0.50, 0.86)]
        for i in range(12):
            x = 2.6 + i * 0.55
            z = 8.6 + 0.16 * math.sin(i * 0.8)
            self.add_object(ColorCube(app, pos=(x, 1.12, z), scale=(0.022, 0.26, 0.022), color=(0.24, 0.14, 0.07)), tag="micro_lantern_string", layer="village")
            self.add_object(
                ColorCube(
                    app,
                    pos=(x, 0.84, z),
                    rot=(0, i * 9.0, 0),
                    scale=(0.085, 0.105, 0.065),
                    color=lantern_colors[i % len(lantern_colors)],
                ),
                tag="micro_festival_lantern",
                layer="village",
            )
            self.add_object(
                NightGlow(app, pos=(x, 0.84, z), scale=(0.22, 0.22, 1.0), color=(1.0, 0.65, 0.28), alpha=0.24, pulse=0.06),
                tag="micro_festival_glow",
                layer="atmosphere",
            )

        for i in range(30):
            angle = math.radians(i * 37.0)
            center = (
                math.cos(angle) * (3.0 + (i % 5) * 0.45),
                0.70 + (i % 6) * 0.15,
                math.sin(angle) * (2.8 + (i % 4) * 0.42),
            )
            self.add_object(
                FireflyGlow(
                    app,
                    center=center,
                    orbit=(0.26, 0.14, 0.24),
                    scale=(0.023, 0.023, 1.0),
                    color=(1.0, 0.95, 0.35),
                    alpha=0.55,
                    speed=0.12 + (i % 5) * 0.012,
                    phase=(i * 0.071) % 1.0,
                ),
                tag="micro_firefly",
                layer="atmosphere",
            )

        for i in range(18):
            angle = i * 20.0
            x = -4.0 + math.cos(math.radians(angle)) * (0.45 + 0.035 * (i % 3))
            z = -10.8
            y = 5.4 + math.sin(math.radians(angle)) * (0.45 + 0.035 * (i % 3))
            self.add_object(
                SunDisc(
                    app,
                    pos=(x, y, z),
                    rot=(0, angle, 0),
                    scale=(0.050, 0.050, 1.0),
                    color=lantern_colors[i % len(lantern_colors)],
                    alpha=0.20,
                ),
                tag="micro_firework_spark",
                layer="atmosphere",
            )

    def add_late_summer_accents(self, app, pond_radius_scale):
        # Dry late heat: dusty wind and muted yellow grass patches.
        dry_colors = [(0.64, 0.56, 0.22), (0.70, 0.62, 0.28), (0.54, 0.48, 0.18)]
        for i in range(34):
            angle = 24 + i * 9.6
            radius = 6.6 + (i % 7) * 0.55
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self.add_object(
                ColorPlane(
                    app,
                    pos=(x, 0.037 + 0.001 * (i % 3), z),
                    rot=(0, angle + i * 11.0, 0),
                    scale=(0.20 + 0.035 * (i % 3), 1.0, 0.080 + 0.020 * (i % 2)),
                    color=dry_colors[i % len(dry_colors)],
                ),
                tag="micro_dry_grass_patch",
                layer="terrain",
            )

        for i in range(18):
            self.add_object(
                WindStreak(
                    app,
                    pos=(-8.0 + i * 0.95, 0.34 + 0.035 * (i % 4), -2.8 + 0.38 * math.sin(i)),
                    rot=(0, 70 + i * 3.0, 0),
                    scale=(0.24, 0.008, 0.016),
                    color=(0.84, 0.72, 0.34),
                    travel=(0.70, 0.0, -0.22),
                    speed=0.12 + (i % 4) * 0.008,
                    phase=(i * 0.083) % 1.0,
                    bob=0.070,
                ),
                tag="micro_dust_heat",
                layer="atmosphere",
            )

    def add_momiji_accents(self, app, pond_radius_scale):
        # Maple peak: red-orange carpet and larger leaf piles near the path.
        leaves = self.season_value(
            "autumn_leaf_colors",
            [(0.82, 0.32, 0.08), (0.94, 0.52, 0.12), (0.62, 0.22, 0.08)],
        )
        red_boost = [(0.90, 0.16, 0.06), (0.78, 0.24, 0.08), (0.96, 0.42, 0.10)]
        palette = list(red_boost) + list(leaves)
        for i in range(96):
            angle = i * 137.5 + 7.0
            radius = 3.8 + (i % 14) * 0.46
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self._add_leaf_chip(app, x, z, angle + i * 17.0, palette[i % len(palette)], y=0.060 + 0.002 * (i % 5))

        for pile, (x, z) in enumerate(((-7.2, -5.3), (-3.8, 7.4), (6.9, 5.6), (7.8, -4.8), (1.8, 9.4))):
            for i in range(14):
                angle = i * math.tau / 14.0
                self._add_leaf_chip(
                    app,
                    x + math.cos(angle) * (0.18 + 0.025 * (i % 3)),
                    z + math.sin(angle) * (0.12 + 0.020 * (i % 2)),
                    pile * 23.0 + i * 17.0,
                    palette[(pile + i) % len(palette)],
                    scale=(0.080, 0.010, 0.040),
                    y=0.072 + 0.006 * (i % 4),
                )

    def add_first_frost_accents(self, app, pond_radius_scale):
        # Late autumn cold: thin frost lines on path, rocks, and bridge approach.
        frost = (0.82, 0.94, 1.00)
        for i in range(36):
            angle = 168 + i * 4.8
            radius = 7.3 + 0.35 * math.sin(i * 0.7)
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self.add_object(
                ColorPlane(
                    app,
                    pos=(x, 0.046, z),
                    rot=(0, angle + 80 + i * 5.0, 0),
                    scale=(0.14, 1.0, 0.018),
                    color=frost,
                ),
                tag="micro_frost_line",
                layer="terrain",
            )

        for i in range(14):
            x = -1.9 + i * 0.30
            z = 4.80 * pond_radius_scale + 0.05 * math.sin(i)
            self.add_object(
                SunDisc(app, pos=(x, 0.074, z), rot=(90, i * 12.0, 0), scale=(0.18, 0.052, 1.0), color=frost, alpha=0.13),
                tag="micro_bridge_frost",
                layer="terrain",
            )

    def add_deep_winter_accents(self, app, pond_radius_scale):
        # Strong winter identity: deeper drifts, extra aurora hint, and quiet snowbanks.
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        for i in range(42):
            angle = 180 + i * 5.2
            radius = 6.1 + 0.46 * math.sin(i * 0.62) ** 2
            x, z = self._ring_position(angle, radius, pond_radius_scale)
            self.add_object(
                PondRock(
                    app,
                    pos=(x, 0.080 + 0.006 * (i % 3), z),
                    rot=(0, angle + i * 11.0, 0),
                    scale=(0.26 + 0.04 * (i % 4), 0.060 + 0.010 * (i % 2), 0.18 + 0.03 * (i % 3)),
                    color=snow if i % 3 else shadow,
                ),
                tag="micro_deep_snow_drift",
                layer="terrain",
            )

        for i in range(9):
            self.add_object(
                SunDisc(
                    app,
                    pos=(-8.0 + i * 1.55, 8.8 + 0.18 * math.sin(i), -24.0),
                    rot=(75, -12 + i * 3.0, 0),
                    scale=(1.15, 0.16, 1.0),
                    color=(0.48, 1.00, 0.82) if i % 2 else (0.44, 0.72, 1.00),
                    alpha=0.060,
                ),
                tag="micro_aurora_thread",
                layer="atmosphere",
            )
