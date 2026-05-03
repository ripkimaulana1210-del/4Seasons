import moderngl as mgl
from pyglm import glm

from .model import BaseModelEmissive, BaseModelEmissiveTexture, SkyDome
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

    def casts_shadow(self, obj):
        if getattr(obj, "is_background", False):
            return False
        if isinstance(obj, (SkyDome, BaseModelEmissive, BaseModelEmissiveTexture)):
            return False
        return hasattr(obj, "m_model") and hasattr(obj, "vao_name")

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
        previous_viewport = self.ctx.viewport
        self.fbo.use()
        self.ctx.viewport = (0, 0, self.size, self.size)
        self.ctx.clear(depth=1.0)
        self.ctx.disable(mgl.BLEND)
        self.ctx.enable(mgl.DEPTH_TEST)

        for obj in objects:
            if not self.casts_shadow(obj):
                continue

            vao = self.vao_for(obj)
            program = self.program_textured if "2f" in self.app.mesh.vao.vbo.vbos[obj.vao_name].format else self.program_color
            program["m_light_space"].write(self.light_space)
            program["m_model"].write(obj.m_model)
            vao.render()

        post_processor = getattr(self.app, "post_processor", None)
        if post_processor is not None:
            post_processor.fbo.use()
        else:
            self.ctx.screen.use()
        self.ctx.viewport = previous_viewport
        self.ctx.enable(mgl.BLEND)

    def bind(self, location=1):
        self.depth_texture.use(location=location)

    def destroy(self):
        for vao in self.vaos.values():
            vao.release()
        self.fbo.release()
        self.depth_texture.release()
        self.program_color.release()
        self.program_textured.release()
