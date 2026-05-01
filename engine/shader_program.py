from .paths import SHADER_DIR


class ShaderProgram:
    def __init__(self, ctx):
        self.ctx = ctx
        self.programs = {
            "default_color": self.get_program("default_color"),
            "emissive_color": self.get_program("emissive_color"),
            "emissive_texture": self.get_program("emissive_texture"),
            "foliage_shader": self.get_program("foliage_shader"),
            "ice_shader": self.get_program("ice_shader"),
            "sky_shader": self.get_program("sky_shader"),
            "texture_color": self.get_program("texture_color"),
            "water_shader": self.get_program("water_shader"),
        }

    def get_program(self, shader_program_name):
        vertex_path = SHADER_DIR / f"{shader_program_name}.vert"
        fragment_path = SHADER_DIR / f"{shader_program_name}.frag"

        with open(vertex_path, "r", encoding="utf-8") as file:
            vertex_shader = file.read()

        with open(fragment_path, "r", encoding="utf-8") as file:
            fragment_shader = file.read()

        return self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

    def destroy(self):
        for program in self.programs.values():
            program.release()
