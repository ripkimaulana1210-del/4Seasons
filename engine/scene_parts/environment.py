import math

from ..models import (
    AuroraBand,
    CloudLayer,
    ColorCube,
    MoonDisc,
    NightGlow,
    SkyDome,
    SunDisc,
    WindStreak,
)
from .environment_atmosphere import SceneAtmosphereEffectsMixin
from .environment_transitions import SceneTransitionEffectsMixin


class SceneEnvironmentMixin(SceneTransitionEffectsMixin, SceneAtmosphereEffectsMixin):
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

        transition = app.season_controller.transition_snapshot()
        transition_aurora = 0.0
        if transition is not None:
            transition_aurora = max(
                transition["from"].get("aurora_intensity", 0.0),
                transition["to"].get("aurora_intensity", 0.0),
            )
        if max(self.season_value("aurora_intensity", 0.0), transition_aurora) > 0.0:
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
