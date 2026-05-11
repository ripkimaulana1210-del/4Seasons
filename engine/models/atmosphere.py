import math

from pyglm import glm

from .core import BaseModelEmissive
from .primitives import EmissiveTexturedPlane


class SunDisc(BaseModelEmissive):
    def __init__(
        self,
        app,
        vao_name="sun_disc",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 0.8, 0.2),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, color, alpha)


class ContactShadow(SunDisc):
    def __init__(
        self,
        app,
        pos=(0, 0.024, 0),
        rot=(90, 0, 0),
        scale=(1.0, 0.38, 1.0),
        color=(0.015, 0.018, 0.018),
        alpha=0.22,
    ):
        super().__init__(app, pos=pos, rot=rot, scale=scale, color=color, alpha=alpha)


class AtmosphereSunDisc(SunDisc):
    def __init__(
        self,
        app,
        center_offset=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        alpha=1.0,
        color_role="sun",
    ):
        self.center_offset = glm.vec3(center_offset)
        self.base_alpha = alpha
        self.color_role = color_role
        super().__init__(app, pos=center_offset, rot=rot, scale=scale, alpha=alpha)

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        self.pos = glm.vec3(atmosphere["sun_position"]) + self.center_offset
        if self.color_role == "ray":
            self.color = glm.vec3(atmosphere["sun_ray_color"])
        elif self.color_role == "warm":
            sun = atmosphere["sun_color"]
            self.color = glm.vec3(
                min(1.0, sun[0] + 0.14),
                min(1.0, sun[1] + 0.12),
                min(1.0, sun[2] + 0.08),
            )
        else:
            self.color = glm.vec3(atmosphere["sun_color"])
        self.alpha = self.base_alpha * atmosphere["sun_alpha"]
        self.m_model = self.get_model_matrix()
        super().update()


class NightGlow(SunDisc):
    def __init__(
        self,
        app,
        pos=(0, 0, 0),
        rot=(90, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 0.72, 0.34),
        alpha=0.55,
        pulse=0.08,
    ):
        self.base_alpha = alpha
        self.base_color = glm.vec3(color)
        self.pulse = pulse
        super().__init__(app, pos=pos, rot=rot, scale=scale, color=color, alpha=0.0)

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        glow = max(atmosphere["night"], atmosphere["dusk"] * 0.62)
        glow *= self.app.season_controller.get_blended_season().get("lantern_glow_boost", 1.0)
        flicker = 1.0 + self.pulse * math.sin(self.app.time * 4.2 + self.pos.x * 0.7 + self.pos.z * 0.3)
        self.alpha = self.base_alpha * glow * flicker
        self.color = self.base_color
        self.m_model = self.get_model_matrix()
        super().update()


class FireflyGlow(SunDisc):
    def __init__(
        self,
        app,
        center=(0, 1, 0),
        orbit=(0.32, 0.18, 0.32),
        scale=(0.026, 0.026, 1.0),
        color=(1.0, 0.96, 0.42),
        alpha=0.62,
        speed=0.18,
        phase=0.0,
    ):
        self.center = glm.vec3(center)
        self.orbit = glm.vec3(orbit)
        self.base_scale = glm.vec3(scale)
        self.base_alpha = alpha
        self.base_color = glm.vec3(color)
        self.speed = speed
        self.phase = phase
        super().__init__(app, pos=center, rot=(0, 0, 0), scale=scale, color=color, alpha=0.0)

    def summer_visibility(self):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return 1.0 if self.app.season_controller.current.get("seasonal_effect") == "summer" else 0.0

        from_summer = transition["from"].get("seasonal_effect") == "summer"
        to_summer = transition["to"].get("seasonal_effect") == "summer"
        if from_summer and not to_summer:
            return 1.0 - transition["eased"]
        if to_summer and not from_summer:
            return transition["eased"]
        return 1.0 if from_summer or to_summer else 0.0

    def update(self):
        t = self.app.time * self.speed + self.phase
        drift_x = math.cos(t * math.tau * 1.23) + 0.42 * math.sin(t * math.tau * 0.63 + self.phase)
        drift_z = math.sin(t * math.tau * 1.04) + 0.38 * math.cos(t * math.tau * 0.78 + self.phase * 1.7)
        drift_y = math.sin(t * math.tau * 1.71 + self.phase * 2.0) + 0.32 * math.cos(t * math.tau * 0.91)

        self.pos = glm.vec3(
            self.center.x + drift_x * self.orbit.x,
            self.center.y + drift_y * self.orbit.y,
            self.center.z + drift_z * self.orbit.z,
        )

        atmosphere = self.app.season_controller.atmosphere_state()
        night_visibility = max(atmosphere["night"], atmosphere["dusk"] * 0.72)
        summer_visibility = self.summer_visibility()
        pulse = 0.50 + 0.50 * math.sin(self.app.time * 7.4 + self.phase * 17.0)
        scale_mul = 0.74 + pulse * 0.34

        self.alpha = self.base_alpha * night_visibility * summer_visibility * (0.36 + pulse * 0.64)
        self.color = self.base_color
        self.scale = self.base_scale * scale_mul
        self.m_model = self.get_model_matrix()
        super().update()


class CloudLayer(EmissiveTexturedPlane):
    def __init__(
        self,
        app,
        pos=(0, 10, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="cloud_soft",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=0.5,
        travel=(1.0, 0.0, -0.4),
        speed=0.015,
        phase=0.0,
    ):
        self.base_pos = glm.vec3(pos)
        self.travel = glm.vec3(travel)
        self.speed = speed
        self.phase = phase
        self.base_alpha = alpha
        super().__init__(app, pos=pos, rot=rot, scale=scale, texture_name=texture_name, tint=tint, repeat=repeat, alpha=alpha)

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        progress = (self.app.time * self.speed + self.phase) % 1.0
        drift = progress - 0.5
        self.pos = glm.vec3(
            self.base_pos.x + self.travel.x * drift,
            self.base_pos.y + 0.10 * math.sin(progress * math.tau + self.phase),
            self.base_pos.z + self.travel.z * drift,
        )
        self.tint = glm.vec3(atmosphere["cloud_color"])
        self.alpha = self.base_alpha * atmosphere["cloud_alpha"]
        self.m_model = self.get_model_matrix()
        super().update()


class MoonDisc(EmissiveTexturedPlane):
    def __init__(self, app):
        super().__init__(
            app,
            pos=(0, 12, -28),
            rot=(90, 0, 0),
            scale=(1.25, 1.0, 1.25),
            texture_name="moon_disc",
            tint=(0.82, 0.88, 1.0),
            alpha=0.0,
        )

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        self.pos = glm.vec3(atmosphere["moon_position"])
        self.tint = glm.vec3(atmosphere["moon_color"])
        self.alpha = 0.92 * atmosphere["moon_alpha"]
        self.m_model = self.get_model_matrix()
        super().update()


class AuroraBand(EmissiveTexturedPlane):
    def __init__(self, app):
        super().__init__(
            app,
            pos=(-9.0, 12.8, -36.0),
            rot=(76, -8, 0),
            scale=(13.5, 1.0, 3.2),
            texture_name="aurora_band",
            tint=(0.55, 1.0, 0.84),
            alpha=0.0,
        )

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        shimmer = 0.75 + 0.25 * math.sin(self.app.time * 0.9)
        self.alpha = atmosphere["aurora_alpha"] * shimmer
        self.m_model = self.get_model_matrix()
        super().update()


class SkyDome:
    def __init__(self, app, vao_name="sky_dome", scale=86.0):
        self.app = app
        self.camera = app.camera
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.scale = scale
        self.m_model = glm.mat4()
        self.program["m_proj"].write(self.camera.m_proj)

    def update(self):
        atmosphere = self.app.season_controller.atmosphere_state()
        season = self.app.season_controller.get_blended_season()
        effect_index = self.app.season_controller.season_effect_index()
        self.m_model = glm.translate(glm.mat4(), self.camera.position)
        self.m_model = glm.scale(self.m_model, glm.vec3(self.scale, self.scale, self.scale))
        self.program["m_view"].write(self.camera.m_view)
        self.program["m_model"].write(self.m_model)
        self.program["u_top_color"].write(glm.vec3(atmosphere["top_color"]))
        self.program["u_mid_color"].write(glm.vec3(atmosphere["mid_color"]))
        self.program["u_horizon_color"].write(glm.vec3(atmosphere["horizon_color"]))
        self.program["u_star_color"].write(glm.vec3(atmosphere["star_color"]))
        self.program["u_star_intensity"].value = atmosphere["star_intensity"]
        self.program["u_summer_sky_clarity"].value = atmosphere["summer_sky_clarity"]
        self.program["u_season_index"].value = effect_index
        self.program["u_sky_detail_strength"].value = season.get("sky_detail_strength", 1.0)
        self.program["u_dusk"].value = atmosphere["dusk"]
        self.program["u_night"].value = atmosphere["night"]
        self.program["u_time"].value = self.app.time

    def render(self):
        self.update()
        self.vao.render()
