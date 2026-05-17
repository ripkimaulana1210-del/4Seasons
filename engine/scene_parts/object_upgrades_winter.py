import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
from ..models import ColorCube, ColorPlane, FireflyGlow, NightGlow, PondRock, SunDisc, WindStreak


class SceneWinterObjectUpgradeMixin:
    def add_winter_snow_lantern(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        x, z = (7.45, -6.00)
        add(ColorCube(app, pos=(x, 0.12, z), scale=(0.16, 0.08, 0.16), color=stone))
        add(ColorCube(app, pos=(x, 0.40, z), scale=(0.038, 0.26, 0.038), color=stone))
        add(ColorCube(app, pos=(x, 0.68, z), scale=(0.18, 0.055, 0.18), color=stone))
        add(ColorCube(app, pos=(x, 0.82, z), scale=(0.13, 0.095, 0.13), color=(0.95, 0.90, 0.72)))
        add(ColorCube(app, pos=(x, 0.95, z), scale=(0.24, 0.055, 0.24), color=snow))
        add(NightGlow(app, pos=(x, 0.82, z), scale=(0.32, 0.32, 1.0), color=(1.00, 0.66, 0.34), alpha=0.36, pulse=0.025))

    def add_winter_torii_and_bridge_snow(self, app):
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        ice_shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        torii_x, torii_z, torii_yaw = (8.9, -6.9, -30.0)
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.84, 0.0, (1.22, 0.035, 0.13), snow)
        self.add_local_cube(app, torii_x, torii_z, torii_yaw, 0.0, 1.54, 0.0, (0.94, 0.030, 0.10), snow)
        for i, local_x in enumerate((-0.52, -0.30, -0.08, 0.14, 0.38, 0.58)):
            self.add_local_cube(app, torii_x, torii_z, torii_yaw, local_x, 1.38 - 0.02 * (i % 3), 0.055, (0.016, 0.10 + 0.02 * (i % 2), 0.012), ice_shadow)

        pond_radius_scale = SCENE_LAYOUT["pond"]["radius_scale"]
        island_radius_scale = SCENE_LAYOUT["island"]["radius_scale"]
        start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        control = (2.02 * pond_radius_scale, 3.56 * pond_radius_scale)
        end = (1.02 * island_radius_scale, 1.78 * island_radius_scale)

        def bridge_point(t):
            inv_t = 1.0 - t
            x = inv_t * inv_t * start[0] + 2.0 * inv_t * t * control[0] + t * t * end[0]
            z = inv_t * inv_t * start[1] + 2.0 * inv_t * t * control[1] + t * t * end[1]
            y = 0.16 + math.sin(math.pi * t) * 0.88
            return (x, y, z)

        for i, t in enumerate((0.12, 0.25, 0.38, 0.52, 0.66, 0.80)):
            point = bridge_point(t)
            next_point = bridge_point(min(1.0, t + 0.03))
            dx = next_point[0] - point[0]
            dz = next_point[2] - point[2]
            yaw = math.degrees(math.atan2(dx, dz))
            self.add_object(ColorCube(app, pos=(point[0], point[1] + 0.15, point[2]), rot=(0, yaw, 0), scale=(0.48, 0.018, 0.12), color=snow))
            if i % 2 == 0:
                self.add_object(ColorCube(app, pos=(point[0] + 0.28, point[1] - 0.18, point[2]), rot=(0, yaw, 0), scale=(0.014, 0.12, 0.014), color=ice_shadow))

    def add_winter_frozen_koi(self, app):
        add = self.add_object
        koi_colors = [(0.86, 0.34, 0.12), (0.96, 0.82, 0.34), (0.90, 0.88, 0.78)]
        for i in range(8):
            angle = i * 0.78 + 0.25
            radius = 1.62 + 0.28 * (i % 3)
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            yaw = math.degrees(angle) + 90.0
            add(ColorCube(app, pos=(x, 0.071, z), rot=(0, yaw, 0), scale=(0.115, 0.006, 0.028), color=koi_colors[i % len(koi_colors)]))
            add(ColorCube(app, pos=(x - math.sin(angle) * 0.09, 0.072, z + math.cos(angle) * 0.09), rot=(0, yaw + 28, 0), scale=(0.035, 0.005, 0.020), color=(0.48, 0.58, 0.62)))

    def add_winter_footprints_and_drifts(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        for i in range(18):
            t = i / 17.0
            x = -5.0 + t * 4.2
            z = -7.35 + 0.18 * math.sin(i * 0.8)
            side = -1 if i % 2 else 1
            add(ColorPlane(app, pos=(x + side * 0.08, 0.043, z), rot=(0, 14 + i * 3.0, 0), scale=(0.050, 1, 0.090), color=shadow))
        for i, (x, z) in enumerate(((-8.8, -7.2), (-7.6, 4.8), (-2.8, 8.3), (4.8, 8.0), (8.8, 3.2), (7.0, -7.0))):
            add(PondRock(app, pos=(x, 0.080, z), rot=(0, i * 23.0, 0), scale=(0.42 + 0.04 * (i % 2), 0.075, 0.22), color=snow if i % 2 else shadow))

    def add_winter_onsen_corner(self, app):
        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        stone = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        water = (0.54, 0.78, 0.86)
        center_x, center_z = (-11.1, -7.1)
        add(SunDisc(app, pos=(center_x, 0.062, center_z), rot=(90, -18, 0), scale=(0.62, 0.28, 1.0), color=water, alpha=0.30))
        for i in range(14):
            angle = i * math.tau / 14.0
            add(
                PondRock(
                    app,
                    pos=(center_x + math.cos(angle) * 0.72, 0.105, center_z + math.sin(angle) * 0.42),
                    rot=(0, i * 21.0, 0),
                    scale=(0.16 + 0.02 * (i % 3), 0.070, 0.12),
                    color=stone if i % 2 else snow,
                )
            )
        for i in range(12):
            angle = -0.70 + i * 0.12
            add(
                WindStreak(
                    app,
                    pos=(center_x + math.cos(angle) * 0.28, 0.34 + 0.05 * (i % 4), center_z + math.sin(angle) * 0.18),
                    rot=(0, -34 + i * 7.0, 0),
                    scale=(0.055, 0.010, 0.070),
                    color=(0.90, 0.96, 0.98),
                    travel=(0.10, 0.18, -0.04),
                    speed=0.055 + i * 0.004,
                    phase=i * 0.09,
                    bob=0.10,
                )
            )
        add(NightGlow(app, pos=(center_x, 0.18, center_z), scale=(0.70, 0.38, 1.0), color=(0.74, 0.92, 1.00), alpha=0.18, pulse=0.020))

    def add_winter_frozen_waterfall_detail(self, app):
        add = self.add_object
        ice = (0.74, 0.90, 0.98)
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        ledge_x, ledge_z, yaw = (-11.5, -6.8, -38.0)
        add(SunDisc(app, pos=(ledge_x - 0.24, 0.070, ledge_z - 0.40), rot=(90, yaw, 0), scale=(0.52, 0.20, 1.0), color=ice, alpha=0.24))
        for i, offset in enumerate((-0.30, -0.16, -0.02, 0.14, 0.30)):
            add(
                ColorCube(
                    app,
                    pos=(ledge_x + offset, 0.34 + 0.03 * (i % 2), ledge_z - 0.08 + 0.05 * i),
                    rot=(8, yaw, 0),
                    scale=(0.026, 0.22 + 0.04 * (i % 3), 0.044),
                    color=ice if i % 2 else shadow,
                )
            )
            add(
                ColorCube(
                    app,
                    pos=(ledge_x + offset * 0.92, 0.18, ledge_z + 0.02 + 0.04 * i),
                    rot=(0, yaw + i * 6.0, 0),
                    scale=(0.018, 0.13 + 0.02 * (i % 2), 0.018),
                    color=ice,
                )
            )
        for i in range(9):
            add(
                PondRock(
                    app,
                    pos=(ledge_x - 0.54 + i * 0.12, 0.082, ledge_z + 0.28 + 0.05 * math.sin(i)),
                    rot=(0, yaw + i * 15.0, 0),
                    scale=(0.11, 0.040, 0.075),
                    color=ice if i % 2 else shadow,
                )
            )

    def add_winter_snowman(self, app, pos_x, pos_z, yaw=0.0, transition_mode=None):
        if not transition_mode:
            transition = app.season_controller.transition_snapshot()
            if transition is not None and transition["pair"] in ("autumn->winter", "winter->spring"):
                # Supress static object if we are animating it in or out
                return

        if not self.is_winter() and transition_mode is None:
            return
            
        add = self.add_object
        from ..models import PondRock, ColorCube, TransitionCube, TransitionPondRock
        import math
        
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        wood = (0.36, 0.22, 0.12)
        carrot = (0.9, 0.4, 0.1)
        coal = (0.1, 0.1, 0.1)
        
        # Base position
        base_x, base_z = (pos_x, pos_z)
        yaw_rad = math.radians(yaw)
        cos_y = math.cos(yaw_rad)
        sin_y = math.sin(yaw_rad)
        
        def spawn_part(is_rock, local_pos, local_rot, w_scale, c_col, t_layer):
            dx, w_y, dz = local_pos
            
            # Rotate position around base yaw
            w_x = base_x + (dx * cos_y + dz * sin_y)
            w_z = base_z + (-dx * sin_y + dz * cos_y)
            
            # Apply yaw to rotation
            r_x, r_y, r_z = local_rot
            r_y += yaw
            
            if transition_mode == "fade_in":
                # Manusia salju dibangun dari bawah ke atas
                p_start = 0.50 + t_layer * 0.10
                p_end = min(1.0, p_start + 0.20)
                if is_rock:
                    add(
                        TransitionPondRock(
                            app,
                            pos=(w_x, 0.0, w_z),
                            end_pos=(w_x, w_y, w_z),
                            rot=(r_x, r_y, r_z),
                            scale=(w_scale[0], 0.001, w_scale[2]),
                            end_scale=w_scale,
                            color=c_col,
                            end_color=c_col,
                            progress_start=p_start,
                            progress_end=p_end
                        )
                    )
                else:
                    add(
                        TransitionCube(
                            app,
                            pos=(w_x, 0.0, w_z),
                            end_pos=(w_x, w_y, w_z),
                            rot=(r_x, r_y, r_z),
                            scale=(w_scale[0], 0.001, w_scale[2]),
                            end_scale=w_scale,
                            color=c_col,
                            end_color=c_col,
                            progress_start=p_start,
                            progress_end=p_end
                        )
                    )
            elif transition_mode == "fade_out":
                # Manusia salju mencair dari atas ke bawah
                p_start = 0.05 + (4 - t_layer) * 0.10
                p_end = min(1.0, p_start + 0.20)
                if is_rock:
                    add(
                        TransitionPondRock(
                            app,
                            pos=(w_x, w_y, w_z),
                            end_pos=(w_x, 0.0, w_z),
                            rot=(r_x, r_y, r_z),
                            scale=w_scale,
                            end_scale=(w_scale[0], 0.001, w_scale[2]),
                            color=c_col,
                            end_color=c_col,
                            progress_start=p_start,
                            progress_end=p_end
                        )
                    )
                else:
                    add(
                        TransitionCube(
                            app,
                            pos=(w_x, w_y, w_z),
                            end_pos=(w_x, 0.0, w_z),
                            rot=(r_x, r_y, r_z),
                            scale=w_scale,
                            end_scale=(w_scale[0], 0.001, w_scale[2]),
                            color=c_col,
                            end_color=c_col,
                            progress_start=p_start,
                            progress_end=p_end
                        )
                    )
            else:
                if is_rock:
                    add(PondRock(app, pos=(w_x, w_y, w_z), rot=(r_x, r_y, r_z), scale=w_scale, color=c_col))
                else:
                    add(ColorCube(app, pos=(w_x, w_y, w_z), rot=(r_x, r_y, r_z), scale=w_scale, color=c_col))
                    
        # The coordinates below are LOCAL to the snowman center (0, 0)
        
        # Bottom body (giant)
        spawn_part(True, (0.0, 0.25, 0.0), (0, 0, 0), (0.70, 0.70, 0.70), snow, 0)
        
        # Middle body (large)
        spawn_part(True, (0.0, 0.80, 0.0), (0, 25, 0), (0.50, 0.50, 0.50), snow, 1)
        
        # Head (medium)
        spawn_part(True, (0.0, 1.25, 0.0), (0, -15, 0), (0.35, 0.35, 0.35), snow, 2)
        
        # Hat (using ColorCube)
        spawn_part(False, (0.0, 1.40, 0.0), (0, -10, 0), (0.32, 0.03, 0.32), coal, 3) # Brim
        spawn_part(False, (0.0, 1.55, 0.0), (0, -10, 0), (0.20, 0.20, 0.20), coal, 4) # Top hat part
        
        # Eyes
        spawn_part(False, (-0.10, 1.30, 0.25), (0, 0, 0), (0.04, 0.04, 0.04), coal, 2)
        spawn_part(False, (0.10, 1.30, 0.25), (0, 0, 0), (0.04, 0.04, 0.04), coal, 2)
        
        # Carrot Nose
        spawn_part(False, (0.0, 1.22, 0.35), (0, 0, 0), (0.04, 0.04, 0.20), carrot, 2)
        
        # Buttons
        spawn_part(False, (0.0, 0.95, 0.42), (15, 0, 0), (0.04, 0.04, 0.04), coal, 1)
        spawn_part(False, (0.0, 0.80, 0.45), (5, 0, 0), (0.04, 0.04, 0.04), coal, 1)
        spawn_part(False, (0.0, 0.65, 0.42), (-5, 0, 0), (0.04, 0.04, 0.04), coal, 1)

        # Arms (branches)
        spawn_part(False, (-0.50, 0.85, 0.0), (0, 0, 35), (0.40, 0.03, 0.03), wood, 1)
        spawn_part(False, (0.50, 0.85, 0.0), (0, 0, -35), (0.40, 0.03, 0.03), wood, 1)

    def add_winter_igloo(self, app, pos_x, pos_z, yaw, transition_mode=None):
        if not transition_mode:
            transition = app.season_controller.transition_snapshot()
            if transition is not None and transition["pair"] in ("autumn->winter", "winter->spring"):
                # Supress static object if we are animating it in or out
                return

        if not self.is_winter() and transition_mode is None:
            return
            
        add = self.add_object
        from ..models import ColorCube, TransitionCube
        import math
        
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.0))
        shadow = self.season_color("winter_snow_shadow_color", (0.78, 0.86, 0.92))
        
        # Mengembalikan ke ukuran dan gaya awal yang terbukti bagus (sedikit lebih besar dari versi pertama)
        igloo_radius = 1.2
        layers = 7
        block_height = 0.22
        
        # Helper function to spawn blocks (ColorCube or TransitionCube depending on mode)
        def spawn_block(w_x, w_y, w_z, r_x, r_y, r_z, s_x, s_y, s_z, c_col, layer_idx):
            if transition_mode == "fade_in":
                # Igloo dibangun lapis demi lapis dari bawah ke atas
                p_start = 0.50 + (layer_idx / layers) * 0.30
                p_end = min(1.0, p_start + 0.20)
                add(
                    TransitionCube(
                        app,
                        pos=(w_x, 0.0, w_z),
                        end_pos=(w_x, w_y, w_z),
                        rot=(r_x, r_y, r_z),
                        scale=(s_x, 0.001, s_z),
                        end_scale=(s_x, s_y, s_z),
                        color=c_col,
                        end_color=c_col,
                        progress_start=p_start,
                        progress_end=p_end
                    )
                )
            elif transition_mode == "fade_out":
                # Igloo mencair dari atas ke bawah
                p_start = 0.05 + ((layers - layer_idx) / layers) * 0.25
                p_end = min(1.0, p_start + 0.20)
                add(
                    TransitionCube(
                        app,
                        pos=(w_x, w_y, w_z),
                        end_pos=(w_x, 0.0, w_z),
                        rot=(r_x, r_y, r_z),
                        scale=(s_x, s_y, s_z),
                        end_scale=(s_x, 0.001, s_z),
                        color=c_col,
                        end_color=c_col,
                        progress_start=p_start,
                        progress_end=p_end
                    )
                )
            else:
                add(
                    ColorCube(
                        app,
                        pos=(w_x, w_y, w_z),
                        rot=(r_x, r_y, r_z),
                        scale=(s_x, s_y, s_z),
                        color=c_col
                    )
                )
        
        # Membangun kubah igloo dari balok-balok salju yang dipadatkan
        for layer in range(layers):
            # Hitung elevasi dan radius untuk lapisan ini agar membentuk kubah
            angle_elevation = (layer / layers) * (math.pi / 2)
            y = math.sin(angle_elevation) * igloo_radius + block_height / 2
            r = math.cos(angle_elevation) * igloo_radius
            
            circ = 2 * math.pi * r
            num_blocks = max(3, int(circ / 0.35))
            
            for b in range(num_blocks):
                angle_azimuth = (b / num_blocks) * math.pi * 2 + (layer % 2) * (math.pi / num_blocks)
                
                # Buat lubang untuk pintu masuk di dua lapisan terbawah
                if layer < 2 and (math.pi/2 - 0.7) < angle_azimuth < (math.pi/2 + 0.7):
                    continue
                    
                local_bx = math.cos(angle_azimuth) * r
                local_bz = math.sin(angle_azimuth) * r
                
                # Konversi ke koordinat dunia
                yaw_rad = math.radians(yaw)
                world_x = pos_x + local_bx * math.cos(yaw_rad) + local_bz * math.sin(yaw_rad)
                world_z = pos_z - local_bx * math.sin(yaw_rad) + local_bz * math.cos(yaw_rad)
                
                # Rotasi balok agar melengkung membentuk lingkaran
                block_yaw = yaw - math.degrees(angle_azimuth)
                
                block_w = (circ / num_blocks) * 0.95
                block_d = 0.20
                
                b_color = snow if (b + layer) % 2 == 0 else shadow
                
                spawn_block(world_x, y, world_z, 0, block_yaw, 0, block_w, block_height * 0.92, block_d, b_color, layer)
                
        # Membangun lorong masuk igloo
        for layer in range(2):
            y = layer * block_height + block_height / 2
            for side in (-1, 1):
                local_bx = side * 0.40
                local_bz = igloo_radius + 0.20
                
                yaw_rad = math.radians(yaw)
                world_x = pos_x + local_bx * math.cos(yaw_rad) + local_bz * math.sin(yaw_rad)
                world_z = pos_z - local_bx * math.sin(yaw_rad) + local_bz * math.cos(yaw_rad)
                
                spawn_block(world_x, y, world_z, 0, yaw, 0, 0.20, block_height * 0.92, 0.45, snow, layer)
                
        # Atap lorong masuk igloo (layer ke-2)
        roof_y = 2 * block_height + block_height / 2
        local_bx = 0
        local_bz = igloo_radius + 0.20
        yaw_rad = math.radians(yaw)
        roof_x = pos_x + local_bx * math.cos(yaw_rad) + local_bz * math.sin(yaw_rad)
        roof_z = pos_z - local_bx * math.sin(yaw_rad) + local_bz * math.cos(yaw_rad)
        
        spawn_block(roof_x, roof_y, roof_z, 0, yaw, 0, 1.00, block_height * 0.92, 0.45, shadow, 2)
