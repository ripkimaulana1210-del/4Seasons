import moderngl as mgl
import numpy as np

from .paths import SHADER_DIR


class PostProcessor:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.enabled = True
        self.program = self.load_program()
        self.vbo = self.ctx.buffer(self.quad_vertices().astype("f4").tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f 2f", "in_position", "in_uv")],
        )
        self.program["u_scene"].value = 0
        self.color_texture = None
        self.depth_buffer = None
        self.fbo = None
        self.resize()

    def load_program(self):
        with open(SHADER_DIR / "postprocess.vert", "r", encoding="utf-8") as file:
            vertex_shader = file.read()
        with open(SHADER_DIR / "postprocess.frag", "r", encoding="utf-8") as file:
            fragment_shader = file.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def quad_vertices(self):
        return np.array(
            [
                (-1.0, 1.0, 0.0, 1.0),
                (-1.0, -1.0, 0.0, 0.0),
                (1.0, -1.0, 1.0, 0.0),
                (-1.0, 1.0, 0.0, 1.0),
                (1.0, -1.0, 1.0, 0.0),
                (1.0, 1.0, 1.0, 1.0),
            ],
            dtype="f4",
        )

    def resize(self):
        if self.fbo is not None:
            self.fbo.release()
            self.color_texture.release()
            self.depth_buffer.release()

        self.color_texture = self.ctx.texture(self.app.WIN_SIZE, 4)
        self.color_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        self.depth_buffer = self.ctx.depth_renderbuffer(self.app.WIN_SIZE)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.color_texture],
            depth_attachment=self.depth_buffer,
        )

    def begin(self):
        self.fbo.use()
        self.ctx.viewport = (0, 0, self.app.WIN_SIZE[0], self.app.WIN_SIZE[1])

    def render(self):
        self.ctx.screen.use()
        self.ctx.viewport = (0, 0, self.app.WIN_SIZE[0], self.app.WIN_SIZE[1])
        self.ctx.disable(mgl.DEPTH_TEST)
        self.color_texture.use(location=0)
        atmosphere = self.app.season_controller.atmosphere_state()
        self.program["u_time"].value = self.app.time
        self.program["u_night"].value = atmosphere["night"]
        self.program["u_dusk"].value = atmosphere["dusk"]
        self.program["u_enabled"].value = 1.0 if self.enabled else 0.0
        self.program["u_texel_size"].value = (
            1.0 / max(1, self.app.WIN_SIZE[0]),
            1.0 / max(1, self.app.WIN_SIZE[1]),
        )
        effect = self.app.season_controller.current.get("seasonal_effect", "spring")
        season = self.app.season_controller.current
        temperature_grade = season.get(
            "post_temperature_grade",
            {
                "spring": 0.02,
                "summer": 0.07,
                "autumn": 0.05,
                "winter": -0.08,
            }.get(effect, 0.0),
        )
        saturation = season.get(
            "post_saturation",
            {
                "spring": 1.05,
                "summer": 1.07,
                "autumn": 1.03,
                "winter": 0.94,
            }.get(effect, 1.0),
        )
        bloom_bonus = season.get("post_bloom_bonus", 0.0)
        self.program["u_temperature_grade"].value = temperature_grade
        self.program["u_saturation"].value = saturation
        self.program["u_bloom_strength"].value = 0.028 + bloom_bonus + atmosphere["night"] * 0.080 + atmosphere["dusk"] * 0.040
        self.vao.render()
        self.ctx.enable(mgl.DEPTH_TEST)

    def destroy(self):
        self.fbo.release()
        self.color_texture.release()
        self.depth_buffer.release()
        self.vao.release()
        self.vbo.release()
        self.program.release()
