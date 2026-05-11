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
    _set_uniform_value(program, "u_shadow_pcf", _shadow_pcf_level(app))
    try:
        program["m_light_space"].write(shadow.light_space)
    except KeyError:
        return


def _shadow_pcf_level(app):
    quality = getattr(app, "quality", None)
    if quality is None:
        return 2
    return int(quality.current.get("shadow_pcf", 2))


def _frame_stamp_cache(app):
    cache = getattr(app, "_uniform_frame_stamps", None)
    if cache is None:
        cache = {}
        app._uniform_frame_stamps = cache
    return cache


def _should_write_program_frame_uniforms(app, program, channel, force=False):
    frame = getattr(app, "frame_count", 0)
    key = (id(program), channel)
    cache = _frame_stamp_cache(app)
    if force:
        cache[key] = frame
        return True
    if cache.get(key) == frame:
        return False
    cache[key] = frame
    return True


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
        self.write_per_frame_uniforms()
        self.write_per_object_uniforms()

    def write_per_frame_uniforms(self, force=False):
        if not _should_write_program_frame_uniforms(self.app, self.program, "color", force):
            return
        light = self.app.light
        self.program["m_proj"].write(self.camera.m_proj)
        self.program["light.position"].write(light.position)
        self.program["light.Ia"].write(light.Ia)
        self.program["light.Id"].write(light.Id)
        self.program["light.Is"].write(light.Is)
        self.program["m_view"].write(self.camera.m_view)
        self.program["cam_pos"].write(self.camera.position)
        _write_fog_uniforms(self.program, self.app)
        _write_shadow_uniforms(self.program, self.app)
        _set_uniform_value(self.program, "u_time", self.app.time)
        if hasattr(self.app, "season_controller"):
            atmosphere = self.app.season_controller.atmosphere_state()
            _set_uniform_value(self.program, "u_night_factor", atmosphere["night"])
            _set_uniform_value(
                self.program,
                "u_wind_strength",
                self.app.season_controller.get_blended_season().get("wind_strength", 0.7),
            )

    def write_per_object_uniforms(self):
        self.program["m_model"].write(self.m_model)
        self.program["u_color"].write(self.color)

    def render(self):
        self.update()
        self.vao.render()

    def render_fast(self):
        """Render with minimal uniform writes. Per-frame uniforms (light,
        camera, fog, shadow) must already be set by the scene renderer."""
        self.write_per_object_uniforms()
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
        self.write_per_frame_uniforms()
        self.write_per_object_uniforms()

    def write_per_frame_uniforms(self, force=False):
        if not _should_write_program_frame_uniforms(self.app, self.program, "emissive", force):
            return
        self.program["m_proj"].write(self.camera.m_proj)
        self.program["m_view"].write(self.camera.m_view)

    def write_per_object_uniforms(self):
        self.program["m_model"].write(self.m_model)
        self.program["u_color"].write(self.color)
        self.program["u_alpha"].value = self.alpha

    def render(self):
        self.update()
        self.vao.render()

    def render_fast(self):
        self.write_per_object_uniforms()
        self.vao.render()


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
        self.texture_name = texture_name

        self.pos = glm.vec3(pos)
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = glm.vec3(scale)
        self.tint = glm.vec3(tint)
        self.base_tint = glm.vec3(tint)
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
        _set_uniform_value(self.program, "u_texture_next", 2)

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self):
        self.tint = self.transition_tint()
        self.write_per_frame_uniforms()
        self.write_per_object_uniforms()

    def transition_tint(self):
        if not hasattr(self.app, "season_controller"):
            return self.base_tint
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return self.base_tint

        roles = (
            ("ground_texture", "ground_color"),
            ("road_texture", "road_color"),
            ("garden_texture", "garden_lawn_color"),
            ("yard_texture", "yard_color"),
        )
        for texture_key, color_key in roles:
            if self.texture_name == transition["from"].get(texture_key):
                target = transition["to"].get(color_key)
                if target is not None:
                    return _lerp_vec3(self.base_tint, glm.vec3(target), transition["eased"])
        return self.base_tint

    def transition_texture_blend(self):
        if not hasattr(self.app, "season_controller"):
            return self.texture, self.base_tint, 0.0
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return self.texture, self.base_tint, 0.0

        texture_roles = (
            ("ground_texture", "ground_color"),
            ("road_texture", "road_color"),
            ("garden_texture", "garden_lawn_color"),
            ("yard_texture", "yard_color"),
        )
        for texture_key, tint_key in texture_roles:
            if self.texture_name != transition["from"].get(texture_key):
                continue
            next_texture_name = transition["to"].get(texture_key)
            if not next_texture_name:
                continue
            next_texture = self.app.mesh.texture.get(next_texture_name)
            next_tint = glm.vec3(transition["to"].get(tint_key, self.base_tint))
            return next_texture, next_tint, transition["eased"]

        return self.texture, self.base_tint, 0.0

    def write_per_frame_uniforms(self, force=False):
        if not _should_write_program_frame_uniforms(self.app, self.program, "texture", force):
            return
        light = self.app.light
        self.program["m_proj"].write(self.camera.m_proj)
        self.program["light.position"].write(light.position)
        self.program["light.Ia"].write(light.Ia)
        self.program["light.Id"].write(light.Id)
        self.program["light.Is"].write(light.Is)
        self.program["m_view"].write(self.camera.m_view)
        self.program["cam_pos"].write(self.camera.position)
        self.program["u_texture"].value = 0
        _write_fog_uniforms(self.program, self.app)
        _write_shadow_uniforms(self.program, self.app)

    def write_per_object_uniforms(self):
        blend_texture, blend_tint, texture_blend = self.transition_texture_blend()
        self.texture.use(location=0)
        blend_texture.use(location=2)
        self.program["m_model"].write(self.m_model)
        self.program["u_tint"].write(self.tint)
        try:
            self.program["u_blend_tint"].write(blend_tint)
        except KeyError:
            pass
        self.program["u_repeat"].write(self.repeat)
        self.program["u_alpha"].value = self.alpha
        _set_uniform_value(self.program, "u_texture_blend", texture_blend)

    def render(self):
        self.update()
        self.vao.render()

    def render_fast(self):
        self.write_per_object_uniforms()
        self.vao.render()


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
