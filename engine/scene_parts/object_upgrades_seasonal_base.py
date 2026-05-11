import math

from ..data.scene_config import HOUSE_SPECS
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneSeasonalObjectBaseMixin:
    def add_seasonal_props(self, app):
        effect = self.season_value("seasonal_effect", "spring")
        self.add_house_seasonal_accents(app, effect)

        if effect == "spring":
            self.add_picnic_set(app)
        elif effect == "summer":
            self.add_summer_props(app)
        elif effect == "autumn":
            self.add_autumn_props(app)
        elif effect == "winter":
            self.add_winter_props(app)

    def add_picnic_set(self, app):
        add = self.add_object
        add(ColorPlane(app, pos=(-6.3, 0.034, 6.8), rot=(0, 22, 0), scale=(0.72, 1, 0.44), color=(0.88, 0.24, 0.28)))
        add(ColorPlane(app, pos=(-6.3, 0.036, 6.8), rot=(0, 22, 0), scale=(0.68, 1, 0.40), color=(0.96, 0.74, 0.78)))
        for i in range(3):
            add(ColorCube(app, pos=(-6.55 + i * 0.22, 0.075, 6.70 + 0.05 * (i % 2)), rot=(0, i * 20, 0), scale=(0.075, 0.035, 0.060), color=(0.92, 0.78, 0.48)))
        add(ColorCube(app, pos=(-6.15, 0.105, 6.63), rot=(0, 32, 0), scale=(0.070, 0.045, 0.055), color=(0.32, 0.18, 0.09)))
        add(ColorCube(app, pos=(-6.12, 0.155, 6.62), rot=(0, 32, 0), scale=(0.040, 0.020, 0.038), color=(0.72, 0.18, 0.22)))
        for i in range(4):
            add(ColorCube(app, pos=(-6.04 + i * 0.11, 0.073, 6.92), rot=(0, i * 36, 0), scale=(0.032, 0.020, 0.032), color=(0.96, 0.86, 0.58)))

        self.add_spring_flower_arch(app)
        self.add_spring_petal_road(app)
        self.add_spring_butterflies(app)
        self.add_spring_rain_puddles(app)
        self.add_spring_tea_corner(app)
        self.add_spring_wishing_tags(app)

    def add_summer_props(self, app):
        add = self.add_object
        x, z = (6.1, 6.7)
        add(ColorCube(app, pos=(x, 0.52, z), scale=(0.030, 0.52, 0.030), color=(0.34, 0.20, 0.10)))
        for i in range(8):
            angle = i * math.tau / 8.0
            add(ColorCube(app, pos=(x + math.cos(angle) * 0.18, 1.02, z + math.sin(angle) * 0.18), rot=(0, math.degrees(angle), 14), scale=(0.20, 0.020, 0.055), color=(0.94, 0.70, 0.18) if i % 2 else (0.92, 0.28, 0.16)))
        add(ColorCube(app, pos=(8.2, 0.86, 5.4), scale=(0.035, 0.70, 0.035), color=(0.42, 0.24, 0.12)))
        add(WindStreak(app, pos=(8.2, 1.62, 5.4), rot=(0, 75, 0), scale=(0.10, 0.018, 0.018), color=(0.86, 0.94, 0.95), travel=(0.12, 0.0, -0.05), speed=0.08, bob=0.05))
        self.add_summer_yatai(app)
        self.add_summer_firefly_clusters(app)
        self.add_summer_heat_shimmer(app)
        self.add_summer_festival_banners(app)
        self.add_summer_fireworks(app)
        self.add_summer_kakigori_counter(app)

    def add_autumn_props(self, app):
        add = self.add_object
        colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
        for i in range(24):
            angle = i * 0.61
            add(ColorCube(app, pos=(-7.8 + math.cos(angle) * 0.48, 0.050 + 0.006 * (i % 3), -5.8 + math.sin(angle) * 0.32), rot=(0, i * 19, 0), scale=(0.060, 0.012, 0.035), color=colors[i % len(colors)]))
        add(ColorCube(app, pos=(-8.8, 0.16, -5.4), scale=(0.18, 0.13, 0.16), color=(0.46, 0.24, 0.08)))
        add(PondRock(app, pos=(-8.8, 0.34, -5.4), scale=(0.16, 0.10, 0.14), color=(0.90, 0.46, 0.14)))
        self.add_autumn_work_corner(app)
        self.add_autumn_mushrooms(app)
        self.add_autumn_bare_branches(app)
        self.add_autumn_wet_path(app)
        self.add_autumn_harvest_display(app)
        self.add_autumn_maple_tunnel(app)

    def add_winter_props(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        x, z = (-6.6, -6.8)
        add(PondRock(app, pos=(x, 0.18, z), scale=(0.28, 0.24, 0.28), color=snow))
        add(PondRock(app, pos=(x, 0.52, z), scale=(0.20, 0.18, 0.20), color=snow))
        add(PondRock(app, pos=(x, 0.76, z), scale=(0.14, 0.13, 0.14), color=snow))
        add(ColorCube(app, pos=(x - 0.05, 0.80, z + 0.13), scale=(0.016, 0.016, 0.016), color=(0.04, 0.04, 0.04)))
        add(ColorCube(app, pos=(x + 0.05, 0.80, z + 0.13), scale=(0.016, 0.016, 0.016), color=(0.04, 0.04, 0.04)))
        for i in range(10):
            add(ColorPlane(app, pos=(-4.8 + i * 0.24, 0.041, -7.4 + 0.10 * math.sin(i)), rot=(0, i * 8.0, 0), scale=(0.055, 1, 0.095), color=(0.78, 0.86, 0.92)))
        self.add_winter_snow_lantern(app)
        self.add_winter_torii_and_bridge_snow(app)
        self.add_winter_frozen_koi(app)
        self.add_winter_footprints_and_drifts(app)
        self.add_winter_onsen_corner(app)
        self.add_winter_frozen_waterfall_detail(app)

    def add_house_seasonal_accents(self, app, effect):
        add = self.add_object
        for idx, (angle_deg, radius, body_scale, _body_color, _roof_color, _trim_color, yaw_offset, _variant) in enumerate(HOUSE_SPECS):
            angle = math.radians(angle_deg)
            radial_x = math.cos(angle)
            radial_z = math.sin(angle)
            x = radial_x * radius
            z = radial_z * radius
            yaw = math.degrees(math.atan2(-radial_x, -radial_z)) + yaw_offset
            width, height, depth = body_scale
            front_z = depth + 0.08

            if effect == "spring" and idx % 3 == 0:
                for local_x in (-width * 0.34, 0.0, width * 0.34):
                    self.add_local_cube(app, x, z, yaw, local_x, 0.52, front_z, (0.14, 0.032, 0.035), (0.38, 0.20, 0.10))
                    for bloom in (-0.050, 0.050):
                        self.add_local_cube(
                            app,
                            x,
                            z,
                            yaw,
                            local_x + bloom,
                            0.575,
                            front_z + 0.020,
                            (0.026, 0.020, 0.020),
                            (1.00, 0.62, 0.84) if bloom < 0 else (0.96, 0.82, 0.46),
                        )

            elif effect == "summer" and idx % 3 == 1:
                cloth_colors = [(0.88, 0.18, 0.12), (0.96, 0.82, 0.38), (0.18, 0.42, 0.72)]
                for panel in range(3):
                    local_x = (panel - 1) * width * 0.18
                    self.add_local_cube(
                        app,
                        x,
                        z,
                        yaw,
                        local_x,
                        0.86,
                        front_z + 0.030,
                        (width * 0.070, 0.155, 0.012),
                        cloth_colors[(idx + panel) % len(cloth_colors)],
                    )
                chime_x, chime_z = self.local_house_pos(x, z, yaw, width * 0.62, front_z)
                add(ColorCube(app, pos=(chime_x, 1.18, chime_z), rot=(0, yaw, 0), scale=(0.010, 0.14, 0.010), color=(0.84, 0.88, 0.84)))
                add(ColorCube(app, pos=(chime_x, 1.02, chime_z), rot=(0, yaw, 0), scale=(0.038, 0.045, 0.038), color=(0.80, 0.92, 0.94)))
                add(WindStreak(app, pos=(chime_x, 0.94, chime_z), rot=(0, yaw + 78, 0), scale=(0.070, 0.007, 0.010), color=(0.98, 0.96, 0.78), travel=(0.16, 0.0, -0.06), speed=0.11, phase=idx * 0.13, bob=0.04))

            elif effect == "autumn" and idx % 3 == 2:
                px, pz = self.local_house_pos(x, z, yaw, -width * 0.12, front_z + 0.22)
                add(ColorPlane(app, pos=(px, 0.040, pz), rot=(0, yaw, 0), scale=(width * 0.24, 1, depth * 0.16), color=(0.62, 0.30, 0.12)))
                self.add_local_cube(app, x, z, yaw, width * 0.48, 0.28, front_z + 0.14, (0.014, 0.28, 0.014), (0.36, 0.20, 0.08), rot=(0, 0, 24))
                for tooth in range(4):
                    self.add_local_cube(
                        app,
                        x,
                        z,
                        yaw,
                        width * 0.48 + (tooth - 1.5) * 0.035,
                        0.53,
                        front_z + 0.09,
                        (0.008, 0.050, 0.008),
                        (0.56, 0.34, 0.12),
                        rot=(0, 0, 24),
                    )

            elif effect == "winter" and idx % 2 == 0:
                snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
                shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
                for local_x in (-width * 0.40, -width * 0.12, width * 0.16, width * 0.42):
                    self.add_local_cube(app, x, z, yaw, local_x, 1.05 - 0.03 * (idx % 2), front_z, (0.018, 0.12 + 0.02 * ((idx + int(local_x * 10)) % 2), 0.012), shadow)
                drift_x, drift_z = self.local_house_pos(x, z, yaw, 0.0, front_z + 0.28)
                add(PondRock(app, pos=(drift_x, 0.075, drift_z), rot=(0, yaw + idx * 13.0, 0), scale=(width * 0.42, 0.070, depth * 0.16), color=snow))
                glow_x, glow_z = self.local_house_pos(x, z, yaw, width * 0.28, front_z + 0.040)
                add(NightGlow(app, pos=(glow_x, 0.82, glow_z), rot=(0, yaw, 0), scale=(0.30, 0.24, 1.0), color=(1.00, 0.68, 0.34), alpha=0.26, pulse=0.025))
