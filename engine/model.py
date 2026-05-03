import math

from pyglm import glm


def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def _smoothstep(value):
    value = _clamp(value)
    return value * value * (3.0 - 2.0 * value)


def _transition_local_progress(app, progress_start, progress_end, use_eased=True):
    transition = app.season_controller.transition_snapshot()
    if transition is None:
        return 1.0

    raw_progress = transition["eased"] if use_eased else transition["progress"]
    if progress_end <= progress_start:
        return 1.0
    return _smoothstep((raw_progress - progress_start) / (progress_end - progress_start))


def _lerp_vec3(start, end, amount):
    return glm.vec3(
        start.x + (end.x - start.x) * amount,
        start.y + (end.y - start.y) * amount,
        start.z + (end.z - start.z) * amount,
    )


def _set_uniform_value(program, name, value):
    try:
        program[name].value = value
    except KeyError:
        return


def _write_fog_uniforms(program, app):
    if not hasattr(app, "season_controller"):
        return

    atmosphere = app.season_controller.atmosphere_state()
    _set_uniform_value(program, "u_fog_density", atmosphere["fog_density"])
    _set_uniform_value(program, "u_fog_start", atmosphere["fog_start"])
    _set_uniform_value(program, "u_fog_end", atmosphere["fog_end"])
    try:
        program["u_fog_color"].write(glm.vec3(atmosphere["fog_color"]))
    except KeyError:
        return


def _write_shadow_uniforms(program, app):
    shadow = getattr(app, "shadow_renderer", None)
    if shadow is None:
        return

    shadow.bind(location=1)
    _set_uniform_value(program, "u_shadow_map", 1)
    _set_uniform_value(program, "u_shadow_strength", shadow.strength if shadow.enabled else 0.0)
    try:
        program["m_light_space"].write(shadow.light_space)
    except KeyError:
        return


class BaseModelColor:
    def __init__(
        self,
        app,
        vao_name,
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
    ):
        self.app = app
        self.camera = app.camera
        self.light = app.light

        self.vao_name = vao_name
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.color = glm.vec3(color)

        self.m_model = self.get_model_matrix()

        self.on_init()

    def on_init(self):
        self.program["m_proj"].write(self.camera.m_proj)
        self.program["light.position"].write(self.light.position)
        self.program["light.Ia"].write(self.light.Ia)
        self.program["light.Id"].write(self.light.Id)
        self.program["light.Is"].write(self.light.Is)

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self):
        light = self.app.light
        self.program["light.position"].write(light.position)
        self.program["light.Ia"].write(light.Ia)
        self.program["light.Id"].write(light.Id)
        self.program["light.Is"].write(light.Is)
        self.program["m_view"].write(self.camera.m_view)
        self.program["m_model"].write(self.m_model)
        self.program["cam_pos"].write(self.camera.position)
        self.program["u_color"].write(self.color)
        _write_fog_uniforms(self.program, self.app)
        _write_shadow_uniforms(self.program, self.app)
        _set_uniform_value(self.program, "u_time", self.app.time)
        if hasattr(self.app, "season_controller"):
            atmosphere = self.app.season_controller.atmosphere_state()
            _set_uniform_value(self.program, "u_night_factor", atmosphere["night"])
            _set_uniform_value(
                self.program,
                "u_wind_strength",
                self.app.season_controller.current.get("wind_strength", 0.7),
            )

    def render(self):
        self.update()
        self.vao.render()


class BaseModelEmissive:
    def __init__(
        self,
        app,
        vao_name,
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
        alpha=1.0,
    ):
        self.app = app
        self.camera = app.camera
        self.vao_name = vao_name
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.color = glm.vec3(color)
        self.alpha = alpha

        self.m_model = self.get_model_matrix()
        self.on_init()

    def on_init(self):
        self.program["m_proj"].write(self.camera.m_proj)

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self):
        self.program["m_view"].write(self.camera.m_view)
        self.program["m_model"].write(self.m_model)
        self.program["u_color"].write(self.color)
        self.program["u_alpha"].value = self.alpha

    def render(self):
        self.update()
        self.vao.render()


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
        glow *= self.app.season_controller.current.get("lantern_glow_boost", 1.0)
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


class BaseModelTexture:
    def __init__(
        self,
        app,
        vao_name,
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="white",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        self.app = app
        self.camera = app.camera
        self.light = app.light
        self.vao_name = vao_name
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.texture = app.mesh.texture.get(texture_name)

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.tint = glm.vec3(tint)
        self.repeat = glm.vec2(repeat)
        self.alpha = alpha

        self.m_model = self.get_model_matrix()
        self.on_init()

    def on_init(self):
        self.program["m_proj"].write(self.camera.m_proj)
        self.program["light.position"].write(self.light.position)
        self.program["light.Ia"].write(self.light.Ia)
        self.program["light.Id"].write(self.light.Id)
        self.program["light.Is"].write(self.light.Is)
        self.program["u_texture"].value = 0

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self):
        light = self.app.light
        self.texture.use(location=0)
        self.program["light.position"].write(light.position)
        self.program["light.Ia"].write(light.Ia)
        self.program["light.Id"].write(light.Id)
        self.program["light.Is"].write(light.Is)
        self.program["m_view"].write(self.camera.m_view)
        self.program["m_model"].write(self.m_model)
        self.program["cam_pos"].write(self.camera.position)
        self.program["u_tint"].write(self.tint)
        self.program["u_repeat"].write(self.repeat)
        self.program["u_alpha"].value = self.alpha
        _write_fog_uniforms(self.program, self.app)
        _write_shadow_uniforms(self.program, self.app)

    def render(self):
        self.update()
        self.vao.render()


class TexturedPlane(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="grass",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class TexturedCube(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_cube",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="wall",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class TexturedGableRoof(BaseModelTexture):
    def __init__(
        self,
        app,
        vao_name="textured_gable_roof",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="roof",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


class BaseModelEmissiveTexture:
    def __init__(
        self,
        app,
        vao_name,
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="white",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        self.app = app
        self.camera = app.camera
        self.vao = app.mesh.vao.vaos[vao_name]
        self.program = self.vao.program
        self.texture = app.mesh.texture.get(texture_name)

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.tint = glm.vec3(tint)
        self.repeat = glm.vec2(repeat)
        self.alpha = alpha
        self.m_model = self.get_model_matrix()

        self.program["m_proj"].write(self.camera.m_proj)
        self.program["u_texture"].value = 0

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self):
        self.texture.use(location=0)
        self.program["m_view"].write(self.camera.m_view)
        self.program["m_model"].write(self.m_model)
        self.program["u_tint"].write(self.tint)
        self.program["u_repeat"].write(self.repeat)
        self.program["u_alpha"].value = self.alpha

    def render(self):
        self.update()
        self.vao.render()


class EmissiveTexturedPlane(BaseModelEmissiveTexture):
    def __init__(
        self,
        app,
        vao_name="emissive_textured_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        texture_name="white",
        tint=(1.0, 1.0, 1.0),
        repeat=(1.0, 1.0),
        alpha=1.0,
    ):
        super().__init__(app, vao_name, pos, rot, scale, texture_name, tint, repeat, alpha)


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
        season = self.app.season_controller.current
        effect = season.get("seasonal_effect", "spring")
        effect_index = {"spring": 0.0, "summer": 1.0, "autumn": 2.0, "winter": 3.0}.get(effect, 0.0)
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


class ColorCube(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class TransitionCube(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 0, 0),
        end_pos=None,
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        end_scale=None,
        color=(1.0, 1.0, 1.0),
        end_color=None,
        progress_start=0.0,
        progress_end=1.0,
        pulse=0.0,
        use_eased=True,
    ):
        self.start_pos = glm.vec3(pos)
        self.end_pos = glm.vec3(end_pos if end_pos is not None else pos)
        self.start_scale = glm.vec3(scale)
        self.end_scale = glm.vec3(end_scale if end_scale is not None else scale)
        self.start_color = glm.vec3(color)
        self.end_color = glm.vec3(end_color if end_color is not None else color)
        self.progress_start = progress_start
        self.progress_end = progress_end
        self.pulse = pulse
        self.use_eased = use_eased
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        progress = _transition_local_progress(
            self.app,
            self.progress_start,
            self.progress_end,
            self.use_eased,
        )
        pulse = 1.0
        if self.pulse:
            pulse += math.sin(self.app.time * math.tau * 1.7 + self.phase_offset()) * self.pulse

        self.pos = _lerp_vec3(self.start_pos, self.end_pos, progress)
        self.scale = _lerp_vec3(self.start_scale, self.end_scale, progress) * pulse
        self.color = _lerp_vec3(self.start_color, self.end_color, progress)
        self.m_model = self.get_model_matrix()
        super().update()

    def phase_offset(self):
        return self.start_pos.x * 0.37 + self.start_pos.z * 0.23 + self.progress_start * 5.0


class RainDrop(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 6, 0),
        rot=(18, 0, -12),
        scale=(0.010, 0.42, 0.010),
        color=(0.58, 0.76, 0.88),
        fall_distance=7.0,
        speed=0.34,
        phase=0.0,
        drift=(0.45, 0.0, -0.28),
    ):
        self.base_pos = glm.vec3(pos)
        self.fall_distance = fall_distance
        self.speed = speed
        self.phase = phase
        self.drift = glm.vec3(drift)
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        progress = (self.app.time * self.speed + self.phase) % 1.0
        self.pos = glm.vec3(
            self.base_pos.x + self.drift.x * progress,
            self.base_pos.y - self.fall_distance * progress,
            self.base_pos.z + self.drift.z * progress,
        )
        self.m_model = self.get_model_matrix()
        super().update()


class DriftParticle(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 4, 0),
        rot=(0, 0, 0),
        scale=(0.035, 0.006, 0.020),
        color=(1.0, 0.72, 0.88),
        fall_distance=4.0,
        drift=(1.0, 0.0, -0.45),
        speed=0.09,
        phase=0.0,
        spin_speed=90.0,
        sway=0.22,
    ):
        self.base_pos = glm.vec3(pos)
        self.base_rot = glm.vec3([glm.radians(a) for a in rot])
        self.fall_distance = fall_distance
        self.drift = glm.vec3(drift)
        self.speed = speed
        self.phase = phase
        self.spin_speed = glm.radians(spin_speed)
        self.sway = sway
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        speed_boost = self.app.season_controller.current.get("particle_speed_boost", 1.0)
        progress = (self.app.time * self.speed * speed_boost + self.phase) % 1.0
        wave = math.sin((progress + self.phase) * math.tau)
        cross = math.cos((progress * 1.7 + self.phase) * math.tau)
        self.pos = glm.vec3(
            self.base_pos.x + self.drift.x * (progress - 0.5) + self.sway * 0.18 * cross,
            self.base_pos.y - self.fall_distance * progress + self.sway * 0.08 * wave,
            self.base_pos.z + self.drift.z * (progress - 0.5) + self.sway * 0.12 * wave,
        )
        self.rot = glm.vec3(
            self.base_rot.x + wave * 0.20,
            self.base_rot.y + self.spin_speed * progress,
            self.base_rot.z + cross * 0.30,
        )
        self.m_model = self.get_model_matrix()
        super().update()


class WindStreak(ColorCube):
    def __init__(
        self,
        app,
        vao_name="color_cube",
        pos=(0, 2, 0),
        rot=(0, 64, 0),
        scale=(0.34, 0.012, 0.018),
        color=(0.86, 0.94, 0.95),
        travel=(1.4, 0.0, -0.55),
        speed=0.18,
        phase=0.0,
        bob=0.16,
    ):
        self.base_pos = glm.vec3(pos)
        self.travel = glm.vec3(travel)
        self.speed = speed
        self.phase = phase
        self.bob = bob
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        boost = self.app.season_controller.current.get("wind_motion_boost", 1.0)
        progress = (self.app.time * self.speed * boost + self.phase) % 1.0
        wave = math.sin((progress + self.phase) * math.tau)
        self.pos = glm.vec3(
            self.base_pos.x + self.travel.x * boost * (progress - 0.5),
            self.base_pos.y + self.bob * boost * wave,
            self.base_pos.z + self.travel.z * boost * (progress - 0.5),
        )
        self.m_model = self.get_model_matrix()
        super().update()


class ColorPlane(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="color_plane",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.0, 1.0, 1.0),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraWood(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_wood",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.26, 0.16, 0.09),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraCanopyLight(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_canopy_light",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.70, 0.90),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraCanopyDeep(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_canopy_deep",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.92, 0.36, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraBlossomLight(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_blossom_light",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.78, 0.90),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraBlossomDeep(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_blossom_deep",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.98, 0.50, 0.68),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class WaterSurface(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="water_surface",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.26, 0.48, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        super().update()
        season = self.app.season_controller.current
        effect = season.get("seasonal_effect", "spring")
        effect_index = {"spring": 0.0, "summer": 1.0, "autumn": 2.0, "winter": 3.0}.get(effect, 0.0)
        self.program["u_time"].value = self.app.time
        self.program["u_water_mode"].value = effect_index
        self.program["u_wave_strength"].value = season.get("water_wave_strength", 1.0)
        self.program["u_sparkle_strength"].value = season.get("water_sparkle_strength", 0.5)
        self.program["u_season_mix"].value = season.get("water_season_mix", 0.5)
        self.program["u_accent_color"].write(glm.vec3(season.get("water_accent_color", (0.72, 0.90, 1.0))))


class IceSurface(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="ice_surface",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.70, 0.88, 0.96),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class IslandMound(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="island_mound",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.24, 0.34, 0.16),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class IslandGrass(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="island_grass",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.42, 0.55, 0.20),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class PondRock(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="pond_rock",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.43, 0.42, 0.38),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class WaterReflection(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="water_reflection",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.92, 0.35, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class FloatingPetals(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="floating_petals",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.62, 0.82),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class FujiPeak(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="fuji_peak",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.44, 0.50, 0.60),
    ):
        self.is_background = True
        super().__init__(app, vao_name, pos, rot, scale, color)


class FujiSnowcap(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="fuji_snowcap",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.96, 0.97, 1.00),
    ):
        self.is_background = True
        super().__init__(app, vao_name, pos, rot, scale, color)


class GableRoof(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="gable_roof",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.46, 0.16, 0.11),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)
