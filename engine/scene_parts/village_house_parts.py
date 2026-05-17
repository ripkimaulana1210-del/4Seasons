import math

from ..data.scene_config import HOUSE_SPECS
from ..models import (
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


class SceneVillageHousePartsMixin:
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
        
        overhang_x = 1.14
        overhang_z = 1.18
        
    def add_snow_roof_cap(self, app, base_x, base_z, yaw, width, height, depth, roof_base_y, roof_height, transition_mode=None):
        if not self.is_winter() and not transition_mode:
            return

        if not transition_mode:
            transition = app.season_controller.transition_snapshot()
            if transition is not None and transition["pair"] in ("autumn->winter", "winter->spring"):
                # Do not add the static snow roof if we are in the middle of animating it
                return

        add = self.add_object
        snow = self.season_color("winter_snow_color", (0.94, 0.97, 1.00))
        from ..models import TexturedGableRoof, PondRock, TransitionGableRoof, TransitionPondRock
        
        overhang_x = 1.14
        overhang_z = 1.18
        
        # 1. Selimut Salju Utama (Smooth Blanket)
        # Menggunakan bentuk atap yang Anda sukai, namun dipakaikan tekstur "cloud_soft"
        # agar permukaannya terlihat seperti salju empuk (tidak ber-noise/kasar seperti tekstur salju biasa)
        roof_pos = (base_x, roof_base_y + 0.04, base_z)
        roof_scale = (width * overhang_x + 0.04, roof_height + 0.04, depth * overhang_z + 0.04)
        
        if transition_mode == "fade_in":
            add(
                TransitionGableRoof(
                    app,
                    pos=roof_pos,
                    rot=(0, yaw, 0),
                    scale=(roof_scale[0], 0.001, roof_scale[2]),
                    end_scale=roof_scale,
                    texture_name="cloud_soft",
                    tint=(0.86, 0.98, 1.00),
                    end_tint=snow,
                    progress_start=0.3,
                    progress_end=0.8,
                    repeat=(1.5, 1.5)
                )
            )
        elif transition_mode == "fade_out":
            add(
                TransitionGableRoof(
                    app,
                    pos=roof_pos,
                    rot=(0, yaw, 0),
                    scale=roof_scale,
                    end_scale=(roof_scale[0], 0.001, roof_scale[2]),
                    texture_name="cloud_soft",
                    tint=snow,
                    end_tint=(0.36, 0.66, 0.76),
                    progress_start=0.3,
                    progress_end=0.8,
                    repeat=(1.5, 1.5)
                )
            )
        else:
            add(
                TexturedGableRoof(
                    app,
                    pos=roof_pos,
                    rot=(0, yaw, 0),
                    scale=roof_scale,
                    texture_name="cloud_soft",
                    tint=snow,
                    repeat=(1.5, 1.5)
                )
            )
        
        # 2. Ketebalan Salju di Ujung Atap (Eaves / Overhang)
        # Menambahkan juntaian tebal di ujung atap agar tidak terlihat seperti dicat putih
        hw = width * overhang_x * 0.5
        hd = depth * overhang_z * 0.5
        
        # Sepanjang sisi kiri dan kanan (Eaves)
        for side in (-1, 1):
            eaves_z_steps = max(2, int(depth * 5))
            for zi in range(eaves_z_steps):
                t_z = (zi / (eaves_z_steps - 1)) * 2.0 - 1.0 if eaves_z_steps > 1 else 0.0
                local_z = t_z * hd
                
                local_x = side * hw
                size_var = 0.8 + 0.4 * math.sin(zi * 45.6)
                
                sx = width * 0.15 * size_var
                sy = height * 0.12 * size_var
                sz = depth * 0.35 * size_var
                
                pos_x, pos_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
                rock_pos = (pos_x, roof_base_y + 0.02 - sy * 0.2, pos_z)
                rock_scale = (sx, sy, sz)
                
                if transition_mode == "fade_in":
                    add(
                        TransitionPondRock(
                            app,
                            pos=rock_pos,
                            rot=(0, yaw, 0),
                            scale=(0.001, 0.001, 0.001),
                            end_scale=rock_scale,
                            color=(0.86, 0.98, 1.00),
                            end_color=snow,
                            progress_start=0.4 + (zi % 3) * 0.1,
                            progress_end=0.9
                        )
                    )
                elif transition_mode == "fade_out":
                    add(
                        TransitionPondRock(
                            app,
                            pos=rock_pos,
                            rot=(0, yaw, 0),
                            scale=rock_scale,
                            end_scale=(0.001, 0.001, 0.001),
                            color=snow,
                            end_color=(0.36, 0.66, 0.76),
                            progress_start=0.3 + (zi % 3) * 0.1,
                            progress_end=0.7
                        )
                    )
                else:
                    add(
                        PondRock(
                            app,
                            pos=rock_pos,
                            rot=(0, yaw, 0),
                            scale=rock_scale,
                            color=snow
                        )
                    )

        # Sepanjang sisi depan dan belakang (Gable Ends)
        x_steps = max(4, int(width * 8))
        slope_angle = math.degrees(math.atan2(roof_height, hw))
        for end_z in (-1, 1):
            for xi in range(x_steps):
                t_x = (xi / (x_steps - 1)) * 2.0 - 1.0 if x_steps > 1 else 0.0
                local_x = t_x * hw
                local_z = end_z * hd
                
                surface_y = roof_base_y + roof_height * (1.0 - abs(t_x))
                size_var = 0.8 + 0.4 * math.sin(xi * 33.3)
                
                sx = width * 0.35 * size_var
                sy = height * 0.10 * size_var
                sz = depth * 0.15 * size_var
                
                pos_x, pos_z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
                side_rot = -1 if local_x < 0 else 1
                rock_pos = (pos_x, surface_y + 0.04, pos_z)
                rock_rot = (0, yaw, -side_rot * slope_angle)
                rock_scale = (sx, sy, sz)
                
                if transition_mode == "fade_in":
                    add(
                        TransitionPondRock(
                            app,
                            pos=rock_pos,
                            rot=rock_rot,
                            scale=(0.001, 0.001, 0.001),
                            end_scale=rock_scale,
                            color=(0.86, 0.98, 1.00),
                            end_color=snow,
                            progress_start=0.4 + (xi % 3) * 0.1,
                            progress_end=0.9
                        )
                    )
                elif transition_mode == "fade_out":
                    add(
                        TransitionPondRock(
                            app,
                            pos=rock_pos,
                            rot=rock_rot,
                            scale=rock_scale,
                            end_scale=(0.001, 0.001, 0.001),
                            color=snow,
                            end_color=(0.36, 0.66, 0.76),
                            progress_start=0.3 + (xi % 3) * 0.1,
                            progress_end=0.7
                        )
                    )
                else:
                    add(
                        PondRock(
                            app,
                            pos=rock_pos,
                            rot=rock_rot,
                            scale=rock_scale,
                            color=snow
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
        if not hasattr(self, "_cached_snow_roofs"):
            self._cached_snow_roofs = []
        self._cached_snow_roofs.append({
            "base_x": x,
            "base_z": z,
            "yaw": roof_yaw,
            "width": width,
            "height": body_half_height,
            "depth": depth,
            "roof_base_y": roof_base_y,
            "roof_height": roof_height,
        })
        
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

    def add_local_cube(self, app, base_x, base_z, yaw, local_x, y, local_z, scale, color, rot=(0, 0, 0)):
        x, z = self.local_house_pos(base_x, base_z, yaw, local_x, local_z)
        self.add_object(
            ColorCube(
                app,
                pos=(x, y, z),
                rot=(rot[0], yaw + rot[1], rot[2]),
                scale=scale,
                color=color,
            )
        )
        return x, z
