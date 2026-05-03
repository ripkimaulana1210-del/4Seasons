import math

from ..model import ColorCube, ColorPlane, NightGlow, PondRock, SunDisc, WindStreak


class SceneObjectUpgradeMixin:
    def add_object_upgrades(self, app, pond_radius_scale):
        self.add_distant_background_layers(app)
        self.add_foreground_plants(app)
        self.add_pond_life(app, pond_radius_scale)
        self.add_stream_and_waterfall(app, pond_radius_scale)
        self.add_stepping_stones_and_boat(app, pond_radius_scale)
        self.add_torii_and_shrine(app)
        self.add_shrine_path_and_offerings(app)
        self.add_bridge_detail_props(app, pond_radius_scale)
        self.add_extra_house_details(app)
        self.add_extra_vegetation(app)
        self.add_seasonal_props(app)

    def add_background_object(self, obj):
        obj.is_background = True
        self.add_object(obj)

    def add_distant_background_layers(self, app):
        hill_colors = [
            self.season_color("fuji_peak_color", (0.38, 0.46, 0.54)),
            self.season_color("garden_hedge_color", (0.18, 0.34, 0.18)),
            self.season_color("night_fog_color", (0.09, 0.12, 0.18)),
        ]
        layer_specs = [
            ((4.5, 1.0, -51.5), (13.0, 1.15, 0.030), hill_colors[0]),
            ((-10.5, 0.72, -49.0), (11.0, 0.92, 0.030), hill_colors[1]),
            ((11.8, 0.58, -47.4), (9.0, 0.62, 0.030), hill_colors[2]),
        ]
        for pos, scale, color in layer_specs:
            self.add_background_object(ColorCube(app, pos=pos, scale=scale, color=color))

        fog_color = self.season_color("winter_snow_shadow_color", (0.80, 0.88, 0.94))
        for i in range(6):
            x = -18.0 + i * 7.2
            y = 0.22 + 0.06 * math.sin(i)
            self.add_background_object(
                SunDisc(
                    app,
                    pos=(x, y, -46.0 - i * 0.30),
                    rot=(90, 0, 0),
                    scale=(2.4 + 0.4 * (i % 2), 0.34, 1.0),
                    color=fog_color,
                    alpha=0.10,
                )
            )

    def add_foreground_plants(self, app):
        add = self.add_object
        colors = [
            self.season_color("garden_lawn_color", (0.34, 0.49, 0.24)),
            self.season_color("garden_rich_lawn_color", (0.25, 0.42, 0.20)),
            self.season_color("garden_hedge_color", (0.24, 0.42, 0.18)),
        ]
        for cluster in range(9):
            base_x = -9.8 + cluster * 2.35
            base_z = 15.1 + 0.35 * math.sin(cluster * 1.4)
            for blade in range(7):
                angle = -28.0 + blade * 9.0 + cluster * 3.0
                height = 0.16 + 0.05 * ((cluster + blade) % 3)
                add(
                    ColorCube(
                        app,
                        pos=(
                            base_x + 0.18 * math.cos(blade),
                            0.05 + height,
                            base_z + 0.11 * math.sin(blade * 1.7),
                        ),
                        rot=(12.0 * math.sin(blade), angle, 10.0 * math.cos(cluster)),
                        scale=(0.018, height, 0.010),
                        color=colors[(cluster + blade) % len(colors)],
                    )
                )
            if cluster % 2 == 0:
                add(
                    PondRock(
                        app,
                        pos=(base_x + 0.32, 0.085, base_z - 0.08),
                        rot=(0, cluster * 23.0, 0),
                        scale=(0.26, 0.10, 0.20),
                        color=(0.38, 0.38, 0.34),
                    )
                )

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

    def add_torii_and_shrine(self, app):
        add = self.add_object
        red = (0.78, 0.10, 0.07)
        dark_red = (0.42, 0.07, 0.05)
        black = (0.08, 0.06, 0.05)
        x, z, yaw = (8.9, -6.9, -30.0)

        for local_x in (-0.62, 0.62):
            px = x + math.cos(math.radians(yaw)) * local_x
            pz = z - math.sin(math.radians(yaw)) * local_x
            add(ColorCube(app, pos=(px, 0.76, pz), rot=(0, yaw, 0), scale=(0.07, 0.76, 0.07), color=red))
            add(ColorCube(app, pos=(px, 1.56, pz), rot=(0, yaw, 0), scale=(0.10, 0.05, 0.10), color=black))

        add(ColorCube(app, pos=(x, 1.48, z), rot=(0, yaw, 0), scale=(0.88, 0.055, 0.075), color=dark_red))
        add(ColorCube(app, pos=(x, 1.66, z), rot=(0, yaw, 0), scale=(1.08, 0.065, 0.095), color=red))
        add(ColorCube(app, pos=(x, 1.78, z), rot=(0, yaw, 0), scale=(1.16, 0.030, 0.110), color=black))

        shrine_x, shrine_z = (10.3, -8.2)
        add(ColorCube(app, pos=(shrine_x, 0.24, shrine_z), rot=(0, -20, 0), scale=(0.46, 0.24, 0.38), color=(0.46, 0.30, 0.16)))
        add(ColorCube(app, pos=(shrine_x, 0.58, shrine_z), rot=(0, -20, 0), scale=(0.54, 0.08, 0.46), color=dark_red))
        add(ColorCube(app, pos=(shrine_x, 0.73, shrine_z), rot=(0, -20, 0), scale=(0.42, 0.08, 0.34), color=black))
        add(NightGlow(app, pos=(shrine_x, 0.48, shrine_z + 0.05), scale=(0.24, 0.24, 1.0), color=(1.0, 0.58, 0.24), alpha=0.32, pulse=0.03))

    def add_shrine_path_and_offerings(self, app):
        add = self.add_object
        torii_x, torii_z, torii_yaw = (8.9, -6.9, -30.0)
        shrine_x, shrine_z, shrine_yaw = (10.3, -8.2, -20.0)
        path_color = self.season_color("garden_path_color", (0.62, 0.54, 0.40))
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone_color = snow if self.is_winter() else path_color
        wood = (0.36, 0.22, 0.12)
        dark_wood = (0.18, 0.10, 0.06)
        straw = (0.78, 0.62, 0.34)
        paper = (0.96, 0.92, 0.78)
        red = (0.78, 0.10, 0.07)

        dx = shrine_x - torii_x
        dz = shrine_z - torii_z
        length = math.sqrt(dx * dx + dz * dz)
        lat_x = -dz / (length + 1e-6)
        lat_z = dx / (length + 1e-6)
        yaw = math.degrees(math.atan2(dx, dz))

        for i in range(9):
            t = 0.08 + i * 0.10
            wiggle = math.sin(i * 1.7) * 0.08
            x = torii_x + dx * t + lat_x * wiggle
            z = torii_z + dz * t + lat_z * wiggle
            add(
                PondRock(
                    app,
                    pos=(x, 0.075, z),
                    rot=(0, yaw + i * 11.0, 0),
                    scale=(0.22 + 0.02 * (i % 2), 0.040, 0.15),
                    color=stone_color,
                )
            )

        for idx, (t, side) in enumerate(((0.24, -1), (0.42, 1), (0.62, -1), (0.78, 1))):
            x = torii_x + dx * t + lat_x * side * 0.56
            z = torii_z + dz * t + lat_z * side * 0.56
            add(ColorCube(app, pos=(x, 0.10, z), rot=(0, yaw, 0), scale=(0.12, 0.08, 0.12), color=dark_wood))
            add(ColorCube(app, pos=(x, 0.38, z), rot=(0, yaw, 0), scale=(0.030, 0.30, 0.030), color=wood))
            add(ColorCube(app, pos=(x, 0.72, z), rot=(0, yaw, 0), scale=(0.10, 0.045, 0.10), color=red if idx % 2 else dark_wood))
            add(ColorCube(app, pos=(x, 0.58, z), rot=(0, yaw, 0), scale=(0.070, 0.080, 0.070), color=paper))
            add(NightGlow(app, pos=(x, 0.58, z), scale=(0.20, 0.20, 1.0), color=(1.0, 0.64, 0.30), alpha=0.28, pulse=0.035))

        self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, 0.0, 0.18, 0.54, (0.30, 0.13, 0.18), dark_wood)
        self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, 0.0, 0.33, 0.54, (0.32, 0.028, 0.20), wood)
        for i, local_x in enumerate((-0.20, -0.07, 0.07, 0.20)):
            self.add_local_cube(app, shrine_x, shrine_z, shrine_yaw, local_x, 0.38, 0.42, (0.018, 0.022, 0.13), straw if i % 2 else paper)

        board_x, board_z, board_yaw = (9.55, -8.55, 16.0)
        for local_x in (-0.42, 0.42):
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.34, 0.0, (0.026, 0.34, 0.026), wood)
        self.add_local_cube(app, board_x, board_z, board_yaw, 0.0, 0.60, 0.0, (0.48, 0.020, 0.018), dark_wood)
        self.add_local_cube(app, board_x, board_z, board_yaw, 0.0, 0.31, 0.0, (0.44, 0.020, 0.018), dark_wood)
        for i, local_x in enumerate((-0.30, -0.15, 0.0, 0.15, 0.30)):
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.45, -0.03, (0.055, 0.070, 0.012), paper if i % 2 else (0.86, 0.68, 0.38))
            self.add_local_cube(app, board_x, board_z, board_yaw, local_x, 0.53, -0.03, (0.010, 0.030, 0.010), straw)

        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.28, 0.0, (0.52, 0.014, 0.016), straw)
        for i, local_x in enumerate((-0.28, -0.09, 0.10, 0.30)):
            self.add_local_cube(app, torii_x, torii_z, torii_yaw, local_x, 1.14 - 0.03 * (i % 2), 0.02, (0.034, 0.10, 0.008), paper, rot=(0, 0, 5.0 * (-1 if i % 2 else 1)))
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.10, 0.03, (0.040, 0.050, 0.030), (0.88, 0.66, 0.22))

    def add_bridge_detail_props(self, app, pond_radius_scale):
        add = self.add_object
        island_radius_scale = 2.35 / 1.95
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

    def add_extra_house_details(self, app):
        detail_specs = [
            (-9.7, 8.0, 12.0),
            (-5.7, -10.1, -8.0),
            (6.6, 10.0, 6.0),
            (10.4, -4.9, 18.0),
        ]
        for idx, (x, z, yaw) in enumerate(detail_specs):
            self.add_house_side_props(app, x, z, yaw, idx)

    def add_house_side_props(self, app, x, z, yaw, idx):
        add = self.add_object
        wood = (0.38, 0.22, 0.11)
        cloth_colors = [(0.84, 0.32, 0.28), (0.92, 0.82, 0.54), (0.42, 0.62, 0.84)]
        self.add_local_cube(app, x, z, yaw, -0.42, 0.34, 0.62, (0.030, 0.34, 0.030), wood)
        self.add_local_cube(app, x, z, yaw, 0.42, 0.34, 0.62, (0.030, 0.34, 0.030), wood)
        self.add_local_cube(app, x, z, yaw, 0.0, 0.62, 0.62, (0.46, 0.018, 0.018), wood)
        for i, local_x in enumerate((-0.24, 0.00, 0.24)):
            self.add_local_cube(app, x, z, yaw, local_x, 0.49, 0.64, (0.070, 0.11, 0.012), cloth_colors[(idx + i) % len(cloth_colors)])

        for i, local_x in enumerate((-0.55, 0.55)):
            px, pz = self.local_house_pos(x, z, yaw, local_x, -0.48)
            add(ColorCube(app, pos=(px, 0.10, pz), rot=(0, yaw, 0), scale=(0.095, 0.080, 0.095), color=(0.36, 0.20, 0.11)))
            add(PondRock(app, pos=(px, 0.24, pz), rot=(0, yaw + i * 24, 0), scale=(0.14, 0.10, 0.12), color=self.season_color("garden_hedge_color", (0.24, 0.42, 0.18))))

    def add_extra_vegetation(self, app):
        bamboo_sites = [(-13.6, 2.4), (13.2, 3.6), (-12.8, -7.2)]
        for idx, (x, z) in enumerate(bamboo_sites):
            self.add_bamboo_cluster(app, x, z, idx * 17.0)

        for idx, (x, z, color) in enumerate(
            [
                (-15.0, -11.0, self.season_color("transition_color", (0.86, 0.34, 0.14))),
                (15.4, -9.4, self.season_color("sakura_canopy_deep_color", (0.72, 0.25, 0.11))),
                (14.8, 8.8, (0.20, 0.38, 0.18) if not self.is_winter() else (0.82, 0.88, 0.90)),
            ]
        ):
            self.add_flat_season_tree(app, x, z, color, idx)

    def add_bamboo_cluster(self, app, x, z, phase):
        add = self.add_object
        stem = (0.30, 0.46, 0.18) if not self.is_winter() else (0.62, 0.72, 0.68)
        leaf = (0.20, 0.40, 0.16) if not self.is_winter() else (0.84, 0.90, 0.92)
        for i in range(7):
            offset = (i - 3) * 0.12
            height = 0.95 + 0.12 * (i % 3)
            add(ColorCube(app, pos=(x + offset, height, z + 0.08 * math.sin(i)), rot=(0, phase + i * 9.0, 5.0 * math.sin(i)), scale=(0.026, height, 0.026), color=stem))
            for j in range(2):
                add(ColorCube(app, pos=(x + offset + 0.10 * (-1 if j else 1), height * 1.55, z), rot=(20, phase + 40 + j * 90, 0), scale=(0.16, 0.018, 0.045), color=leaf))

    def add_flat_season_tree(self, app, x, z, color, idx):
        add = self.add_object
        add(ColorCube(app, pos=(x, 0.62, z), scale=(0.10, 0.62, 0.10), color=(0.28, 0.17, 0.09)))
        for layer in range(4):
            add(
                PondRock(
                    app,
                    pos=(x + 0.18 * math.sin(layer + idx), 1.16 + layer * 0.14, z + 0.12 * math.cos(layer)),
                    rot=(0, idx * 31.0 + layer * 18.0, 0),
                    scale=(0.60 - layer * 0.06, 0.24, 0.46 - layer * 0.04),
                    color=color,
                )
            )

    def add_seasonal_props(self, app):
        effect = self.season_value("seasonal_effect", "spring")
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
        for i in range(3):
            add(ColorCube(app, pos=(-6.55 + i * 0.22, 0.075, 6.70 + 0.05 * (i % 2)), rot=(0, i * 20, 0), scale=(0.075, 0.035, 0.060), color=(0.92, 0.78, 0.48)))

    def add_summer_props(self, app):
        add = self.add_object
        x, z = (6.1, 6.7)
        add(ColorCube(app, pos=(x, 0.52, z), scale=(0.030, 0.52, 0.030), color=(0.34, 0.20, 0.10)))
        for i in range(8):
            angle = i * math.tau / 8.0
            add(ColorCube(app, pos=(x + math.cos(angle) * 0.18, 1.02, z + math.sin(angle) * 0.18), rot=(0, math.degrees(angle), 14), scale=(0.20, 0.020, 0.055), color=(0.94, 0.70, 0.18) if i % 2 else (0.92, 0.28, 0.16)))
        add(ColorCube(app, pos=(8.2, 0.86, 5.4), scale=(0.035, 0.70, 0.035), color=(0.42, 0.24, 0.12)))
        add(WindStreak(app, pos=(8.2, 1.62, 5.4), rot=(0, 75, 0), scale=(0.10, 0.018, 0.018), color=(0.86, 0.94, 0.95), travel=(0.12, 0.0, -0.05), speed=0.08, bob=0.05))

    def add_autumn_props(self, app):
        add = self.add_object
        colors = self.season_value("autumn_leaf_colors", [(0.86, 0.34, 0.12), (0.94, 0.58, 0.18)])
        for i in range(24):
            angle = i * 0.61
            add(ColorCube(app, pos=(-7.8 + math.cos(angle) * 0.48, 0.050 + 0.006 * (i % 3), -5.8 + math.sin(angle) * 0.32), rot=(0, i * 19, 0), scale=(0.060, 0.012, 0.035), color=colors[i % len(colors)]))
        add(ColorCube(app, pos=(-8.8, 0.16, -5.4), scale=(0.18, 0.13, 0.16), color=(0.46, 0.24, 0.08)))
        add(PondRock(app, pos=(-8.8, 0.34, -5.4), scale=(0.16, 0.10, 0.14), color=(0.90, 0.46, 0.14)))

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
