import math

import moderngl as mgl
from pyglm import glm

from .model import (
    BaseModelColor,
    BaseModelEmissive,
    BaseModelEmissiveTexture,
    BaseModelTexture,
    SkyDome,
)
from .paths import SHADER_DIR


class ShadowMapRenderer:
    def __init__(self, app, size=2048):
        self.app = app
        self.ctx = app.ctx
        self.size = size
        self.enabled = True
        self.strength = 0.34
        self.depth_texture = self.ctx.depth_texture((size, size))
        self.depth_texture.repeat_x = False
        self.depth_texture.repeat_y = False
        self.depth_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        self.fbo = self.ctx.framebuffer(depth_attachment=self.depth_texture)
        self.program_color = self.load_program("shadow_depth.vert")
        self.program_textured = self.load_program("shadow_depth_textured.vert")
        self.vaos = {}
        self.light_space = glm.mat4()
        self._shadow_frustum_planes = None
        self._cache_key = None
        self._cache_valid = False

    def load_program(self, vertex_name):
        with open(SHADER_DIR / vertex_name, "r", encoding="utf-8") as file:
            vertex_shader = file.read()
        with open(SHADER_DIR / "shadow_depth.frag", "r", encoding="utf-8") as file:
            fragment_shader = file.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def light_space_matrix(self):
        light_dir = glm.normalize(glm.vec3(self.app.light.position))
        target = glm.vec3(0.0, 1.0, 0.0)
        light_pos = target + light_dir * 38.0
        light_view = glm.lookAt(light_pos, target, glm.vec3(0.0, 1.0, 0.0))
        light_proj = glm.ortho(-26.0, 26.0, -20.0, 24.0, 3.0, 86.0)
        return light_proj * light_view

    def extract_shadow_frustum(self, light_space):
        """Extract 6 frustum planes from the light's projection*view matrix
        so we can cull objects that are outside the shadow map's view."""
        m = light_space
        rows = [
            (m[0][3] + m[0][0], m[1][3] + m[1][0], m[2][3] + m[2][0], m[3][3] + m[3][0]),
            (m[0][3] - m[0][0], m[1][3] - m[1][0], m[2][3] - m[2][0], m[3][3] - m[3][0]),
            (m[0][3] + m[0][1], m[1][3] + m[1][1], m[2][3] + m[2][1], m[3][3] + m[3][1]),
            (m[0][3] - m[0][1], m[1][3] - m[1][1], m[2][3] - m[2][1], m[3][3] - m[3][1]),
            (m[0][3] + m[0][2], m[1][3] + m[1][2], m[2][3] + m[2][2], m[3][3] + m[3][2]),
            (m[0][3] - m[0][2], m[1][3] - m[1][2], m[2][3] - m[2][2], m[3][3] - m[3][2]),
        ]
        planes = []
        for a, b, c, d in rows:
            length = math.sqrt(a * a + b * b + c * c)
            if length > 1e-8:
                inv = 1.0 / length
                planes.append((a * inv, b * inv, c * inv, d * inv))
            else:
                planes.append((0.0, 0.0, 0.0, 0.0))
        return planes

    def is_in_shadow_frustum(self, obj):
        """Test if object is within the shadow map's frustum."""
        if self._shadow_frustum_planes is None:
            return True
        pos = getattr(obj, "pos", None)
        if pos is None:
            return True
        scale = getattr(obj, "scale", None)
        if scale is None:
            radius = 1.0
        else:
            radius = max(abs(scale.x), abs(scale.y), abs(scale.z)) * 1.8
        px, py, pz = pos.x, pos.y, pos.z
        for a, b, c, d in self._shadow_frustum_planes:
            if a * px + b * py + c * pz + d < -radius:
                return False
        return True

    def casts_shadow(self, obj):
        if getattr(obj, "is_background", False):
            return False
        if isinstance(obj, (SkyDome, BaseModelEmissive, BaseModelEmissiveTexture)):
            return False
        return hasattr(obj, "m_model") and hasattr(obj, "vao_name")

    def is_static_shadow_caster(self, obj):
        if isinstance(obj, BaseModelColor):
            return type(obj).update is BaseModelColor.update
        if isinstance(obj, BaseModelTexture):
            return type(obj).update is BaseModelTexture.update
        return False

    def invalidate_cache(self):
        self._cache_key = None
        self._cache_valid = False

    def shadow_cache_key(self, objects):
        season_controller = getattr(self.app, "season_controller", None)
        if season_controller is not None and season_controller.is_transitioning:
            return None

        for obj in objects:
            if self.casts_shadow(obj) and not self.is_static_shadow_caster(obj):
                return None

        light_pos = self.app.light.position
        light_key = (
            round(float(light_pos.x), 4),
            round(float(light_pos.y), 4),
            round(float(light_pos.z), 4),
        )
        object_key = tuple(id(obj) for obj in objects if self.casts_shadow(obj))
        return (self.size, light_key, object_key)

    def vao_for(self, obj):
        vao_name = obj.vao_name
        if vao_name in self.vaos:
            return self.vaos[vao_name]

        vbo = self.app.mesh.vao.vbo.vbos[vao_name]
        if "2f" in vbo.format:
            vao = self.ctx.vertex_array(
                self.program_textured,
                [(vbo.vbo, vbo.format, "in_normal", "in_position", "in_uv")],
            )
        else:
            vao = self.ctx.vertex_array(
                self.program_color,
                [(vbo.vbo, vbo.format, "in_normal", "in_position")],
            )
        self.vaos[vao_name] = vao
        return vao

    def render(self, objects):
        if not self.enabled:
            return

        self.light_space = self.light_space_matrix()
        self._shadow_frustum_planes = self.extract_shadow_frustum(self.light_space)
        cache_key = self.shadow_cache_key(objects)
        if cache_key is not None and self._cache_valid and cache_key == self._cache_key:
            return

        previous_viewport = self.ctx.viewport
        self.fbo.use()
        self.ctx.viewport = (0, 0, self.size, self.size)
        self.ctx.clear(depth=1.0)
        self.ctx.disable(mgl.BLEND)
        self.ctx.enable(mgl.DEPTH_TEST)

        # Write light_space to both programs once
        self.program_color["m_light_space"].write(self.light_space)
        self.program_textured["m_light_space"].write(self.light_space)

        # Cache VBO format lookups
        vbo_formats = self.app.mesh.vao.vbo.vbos

        for obj in objects:
            if not self.casts_shadow(obj):
                continue

            # Shadow frustum culling
            if not self.is_in_shadow_frustum(obj):
                continue

            vao = self.vao_for(obj)
            program = self.program_textured if "2f" in vbo_formats[obj.vao_name].format else self.program_color
            program["m_model"].write(obj.m_model)
            vao.render()

        post_processor = getattr(self.app, "post_processor", None)
        if post_processor is not None:
            post_processor.fbo.use()
        else:
            self.ctx.screen.use()
        self.ctx.viewport = previous_viewport
        self.ctx.enable(mgl.BLEND)
        if cache_key is None:
            self.invalidate_cache()
        else:
            self._cache_key = cache_key
            self._cache_valid = True

    def resize(self, new_size):
        """Resize the shadow map texture and FBO."""
        if new_size == self.size:
            return
        # Release old resources
        for vao in self.vaos.values():
            vao.release()
        self.vaos = {}
        self.fbo.release()
        self.depth_texture.release()
        # Create new resources
        self.size = new_size
        self.depth_texture = self.ctx.depth_texture((new_size, new_size))
        self.depth_texture.repeat_x = False
        self.depth_texture.repeat_y = False
        self.depth_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        self.fbo = self.ctx.framebuffer(depth_attachment=self.depth_texture)
        self.invalidate_cache()

    def bind(self, location=1):
        self.depth_texture.use(location=location)

    def destroy(self):
        for vao in self.vaos.values():
            vao.release()
        self.fbo.release()
        self.depth_texture.release()
        self.program_color.release()
        self.program_textured.release()
