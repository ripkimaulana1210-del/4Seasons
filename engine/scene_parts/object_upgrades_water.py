import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneWaterUpgradeMixin:
    def add_pond_life(self, app, pond_radius_scale):
        add = self.add_object
        pad_color = (0.16, 0.40, 0.22) if not self.is_winter() else (0.76, 0.88, 0.92)
        flower_color = self.season_color("floating_petal_color", (1.0, 0.64, 0.84))

        for i in range(12):
            angle = i * math.tau / 12.0 + 0.20 * math.sin(i)
            radius = (2.55 + 0.55 * (i % 3)) * pond_radius_scale
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            add(
                ColorPlane(
                    app,
                    pos=(x, 0.050, z),
                    rot=(0, math.degrees(angle) + i * 11.0, 0),
                    scale=(0.22 + 0.03 * (i % 2), 1, 0.13),
                    color=pad_color,
                )
            )
            if not self.is_winter() and i % 4 == 0:
                add(
                    ColorCube(
                        app,
                        pos=(x + 0.03, 0.086, z - 0.02),
                        rot=(0, i * 31.0, 0),
                        scale=(0.035, 0.018, 0.035),
                        color=flower_color,
                    )
                )

        koi_colors = [
            ((0.95, 0.36, 0.10), (0.96, 0.90, 0.76)),
            ((0.96, 0.82, 0.34), (0.34, 0.14, 0.08)),
            ((0.92, 0.92, 0.84), (0.86, 0.28, 0.08)),
        ]
        for i in range(10):
            angle = i * 0.72
            radius = (1.95 + 0.25 * (i % 4)) * pond_radius_scale
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            yaw = math.degrees(angle) + 90.0
            body_color, accent = koi_colors[i % len(koi_colors)]
            add(ColorCube(app, pos=(x, 0.072, z), rot=(0, yaw, 0), scale=(0.13, 0.014, 0.034), color=body_color))
            add(ColorCube(app, pos=(x - math.sin(angle) * 0.12, 0.074, z + math.cos(angle) * 0.12), rot=(0, yaw + 35, 0), scale=(0.045, 0.010, 0.026), color=accent))
            if i % 3 == 0:
                add(
                    SunDisc(
                        app,
                        pos=(x, 0.082, z),
                        rot=(90, 0, 0),
                        scale=(0.34, 0.10, 1.0),
                        color=(0.72, 0.90, 1.0),
                        alpha=0.10,
                    )
                )

    def add_stream_and_waterfall(self, app, pond_radius_scale):
        add = self.add_object
        winter = self.is_winter()
        water_color = (0.34, 0.64, 0.76) if not winter else (0.70, 0.86, 0.94)
        deep_water = (0.16, 0.38, 0.50) if not winter else (0.58, 0.74, 0.84)
        foam_color = (0.86, 0.96, 1.0)
        bank_color = self.season_color("garden_path_color", (0.56, 0.48, 0.34))
        moss_color = self.season_color("garden_hedge_color", (0.22, 0.38, 0.17))

        stream_points = [
            (-9.25, -5.45),
            (-8.35, -4.92),
            (-7.30, -4.30),
            (-6.45, -3.42),
            (-5.78, -2.35),
            (-5.12, -1.25),
        ]

        for i in range(len(stream_points) - 1):
            ax, az = stream_points[i]
            bx, bz = stream_points[i + 1]
            dx = bx - ax
            dz = bz - az
            length = math.sqrt(dx * dx + dz * dz)
            yaw = math.degrees(math.atan2(dx, dz))
            lat_x = -dz / (length + 1e-6)
            lat_z = dx / (length + 1e-6)
            x = (ax + bx) * 0.5
            z = (az + bz) * 0.5
            width = 0.34 + 0.03 * (i % 2)

            add(
                ColorPlane(
                    app,
                    pos=(x, 0.052, z),
                    rot=(0, yaw, 0),
                    scale=(width * 0.5, 1, length * 0.54),
                    color=water_color if i % 2 else deep_water,
                )
            )
            if i % 2 == 0:
                add(
                    SunDisc(
                        app,
                        pos=(x + lat_x * 0.04, 0.066, z + lat_z * 0.04),
                        rot=(90, yaw, 0),
                        scale=(width * 0.58, 0.10, 1.0),
                        color=foam_color,
                        alpha=0.13 if not winter else 0.18,
                    )
                )

            for side in (-1, 1):
                if (i + side) % 2 == 0:
                    side_offset = side * (width * 0.82 + 0.10)
                    add(
                        PondRock(
                            app,
                            pos=(x + lat_x * side_offset, 0.084, z + lat_z * side_offset),
                            rot=(0, yaw + i * 13.0, 0),
                            scale=(0.18 + 0.03 * (i % 3), 0.060, 0.13),
                            color=bank_color,
                        )
                    )

        ledge_x, ledge_z = stream_points[0]
        for i, offset in enumerate((-0.34, 0.0, 0.36)):
            add(
                PondRock(
                    app,
                    pos=(ledge_x + offset, 0.22 + 0.03 * (i % 2), ledge_z - 0.18 + 0.05 * i),
                    rot=(0, -35 + i * 18.0, 0),
                    scale=(0.34, 0.16, 0.24),
                    color=(0.36, 0.34, 0.31) if not winter else self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92)),
                )
            )

        add(
            ColorPlane(
                app,
                pos=(ledge_x - 0.18, 0.115, ledge_z - 0.42),
                rot=(0, -38, 0),
                scale=(0.44, 1, 0.24),
                color=deep_water,
            )
        )

        for i, offset in enumerate((-0.16, 0.02, 0.18)):
            add(
                ColorCube(
                    app,
                    pos=(ledge_x + offset, 0.37, ledge_z - 0.03 + i * 0.03),
                    rot=(10, -38, 0),
                    scale=(0.034, 0.24 + 0.02 * i, 0.050),
                    color=water_color,
                )
            )
            add(
                WindStreak(
                    app,
                    pos=(ledge_x + offset, 0.34, ledge_z + 0.12 + i * 0.04),
                    rot=(0, -38, 0),
                    scale=(0.034, 0.010, 0.12),
                    color=foam_color,
                    travel=(0.18, 0.0, 0.05),
                    speed=0.18 + i * 0.02,
                    phase=i * 0.20,
                    bob=0.020,
                )
            )

        reed_sites = [
            (-5.70, -1.55),
            (-5.35, -0.92),
            (-4.92, -1.70),
            (-6.05, -2.10),
            (-7.58, -4.00),
            (-8.02, -4.65),
        ]
        for i, (x, z) in enumerate(reed_sites):
            height = 0.30 + 0.04 * (i % 3)
            add(
                ColorCube(
                    app,
                    pos=(x, 0.05 + height, z),
                    rot=(0, i * 18.0, 7.0 * math.sin(i)),
                    scale=(0.014, height, 0.014),
                    color=moss_color,
                )
            )
            if not winter and i % 2 == 0:
                add(
                    ColorCube(
                        app,
                        pos=(x + 0.02, 0.10 + height * 2.0, z - 0.01),
                        rot=(0, i * 18.0, 0),
                        scale=(0.026, 0.055, 0.026),
                        color=(0.42, 0.25, 0.12),
                    )
                )

    def add_stepping_stones_and_boat(self, app, pond_radius_scale):
        add = self.add_object
        for i in range(8):
            t = i / 7.0
            x = -5.4 * pond_radius_scale + t * 3.8 * pond_radius_scale
            z = 3.85 * pond_radius_scale - math.sin(t * math.pi) * 0.7
            add(
                PondRock(
                    app,
                    pos=(x, 0.090, z),
                    rot=(0, i * 17.0, 0),
                    scale=(0.24 + 0.03 * (i % 2), 0.050, 0.18),
                    color=(0.48, 0.47, 0.42) if not self.is_winter() else self.season_color("winter_snow_color", (0.94, 0.97, 1.0)),
                )
            )

        boat_x, boat_z = (-2.8 * pond_radius_scale, -2.6 * pond_radius_scale)
        wood = (0.42, 0.24, 0.12)
        dark = (0.22, 0.13, 0.07)
        for side, offset in ((-1, -0.22), (1, 0.22)):
            add(ColorCube(app, pos=(boat_x + offset, 0.125, boat_z), rot=(0, 24, side * 10), scale=(0.055, 0.050, 0.58), color=dark))
        add(ColorCube(app, pos=(boat_x, 0.104, boat_z), rot=(0, 24, 0), scale=(0.24, 0.035, 0.64), color=wood))
        add(ColorCube(app, pos=(boat_x + 0.58, 0.125, boat_z - 0.26), rot=(0, 62, 0), scale=(0.030, 0.018, 0.54), color=dark))

    def add_bridge_detail_props(self, app, pond_radius_scale):
        add = self.add_object
        island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]
        bridge_width = 1.30
        y_base = 0.16
        arch_height = 0.88
        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)
        rope_color = (0.78, 0.58, 0.30)
        dark = (0.16, 0.09, 0.05)
        lantern_shell = (0.82, 0.16, 0.10)
        lantern_paper = (0.96, 0.82, 0.52)

        def bridge_point(t):
            inv_t = 1.0 - t
            x = inv_t * inv_t * start[0] + 2.0 * inv_t * t * control[0] + t * t * end[0]
            z = inv_t * inv_t * start[1] + 2.0 * inv_t * t * control[1] + t * t * end[1]
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

        rope_points = [bridge_point(i / 10.0) for i in range(11)]
        for i in range(0, len(rope_points) - 1, 2):
            p0 = rope_points[i]
            p1 = rope_points[i + 1]
            horizontal, yaw, pitch, lat_x, lat_z = bridge_frame(p0, p1)
            seg_len = horizontal * 0.52 + 0.04
            x = (p0[0] + p1[0]) * 0.5
            y = (p0[1] + p1[1]) * 0.5 + 0.28
            z = (p0[2] + p1[2]) * 0.5
            for side in (-1, 1):
                offset = side * bridge_width * 0.57
                add(
                    ColorCube(
                        app,
                        pos=(x + lat_x * offset, y, z + lat_z * offset),
                        rot=(pitch, yaw, 0),
                        scale=(0.016, 0.014, seg_len),
                        color=rope_color,
                    )
                )

        for idx, t in enumerate((0.12, 0.30, 0.50, 0.70, 0.88)):
            point = bridge_point(t)
            prev_point = bridge_point(max(0.0, t - 0.04))
            next_point = bridge_point(min(1.0, t + 0.04))
            _, yaw, _, lat_x, lat_z = bridge_frame(prev_point, next_point)
            sides = (-1, 1) if idx in (0, 2, 4) else (1,)

            for side in sides:
                offset = side * bridge_width * 0.66
                x = point[0] + lat_x * offset
                z = point[2] + lat_z * offset
                add(ColorCube(app, pos=(x, point[1] + 0.62, z), rot=(0, yaw, 0), scale=(0.012, 0.15, 0.012), color=dark))
                add(ColorCube(app, pos=(x, point[1] + 0.44, z), rot=(0, yaw, 0), scale=(0.085, 0.095, 0.070), color=lantern_shell))
                add(ColorCube(app, pos=(x, point[1] + 0.44, z), rot=(0, yaw, 0), scale=(0.058, 0.068, 0.074), color=lantern_paper))
                add(ColorCube(app, pos=(x, point[1] + 0.55, z), rot=(0, yaw, 0), scale=(0.070, 0.018, 0.072), color=dark))
                add(NightGlow(app, pos=(x, point[1] + 0.44, z), scale=(0.22, 0.22, 1.0), color=(1.0, 0.58, 0.24), alpha=0.24, pulse=0.040))

        for i, t in enumerate((0.16, 0.28, 0.42, 0.58, 0.72, 0.86)):
            point = bridge_point(t)
            prev_point = bridge_point(max(0.0, t - 0.03))
            next_point = bridge_point(min(1.0, t + 0.03))
            _, yaw, _, lat_x, lat_z = bridge_frame(prev_point, next_point)
            for side in (-1, 1):
                offset = side * bridge_width * 0.26
                add(
                    ColorCube(
                        app,
                        pos=(point[0] + lat_x * offset, point[1] + 0.055, point[2] + lat_z * offset),
                        rot=(0, yaw + i * 7.0, 0),
                        scale=(0.026, 0.010, 0.026),
                        color=dark,
                    )
                )
