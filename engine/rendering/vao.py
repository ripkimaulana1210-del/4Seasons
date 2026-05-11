from .shader_program import ShaderProgram
from .vbo import VBO


class VAO:
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = VBO(ctx)
        self.program = ShaderProgram(ctx)

        self.vaos = {
            "color_cube": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["color_cube"],
            ),
            "color_plane": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["color_plane"],
            ),
            "textured_cube": self.get_vao(
                self.program.programs["texture_color"],
                self.vbo.vbos["textured_cube"],
            ),
            "textured_gable_roof": self.get_vao(
                self.program.programs["texture_color"],
                self.vbo.vbos["textured_gable_roof"],
            ),
            "textured_plane": self.get_vao(
                self.program.programs["texture_color"],
                self.vbo.vbos["textured_plane"],
            ),
            "emissive_textured_plane": self.get_vao(
                self.program.programs["emissive_texture"],
                self.vbo.vbos["textured_plane"],
            ),
            "sky_dome": self.get_vao(
                self.program.programs["sky_shader"],
                self.vbo.vbos["sky_dome"],
            ),
            "sakura_wood": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["sakura_wood"],
            ),
            "sakura_canopy_light": self.get_vao(
                self.program.programs["foliage_shader"],
                self.vbo.vbos["sakura_canopy_light"],
            ),
            "sakura_canopy_deep": self.get_vao(
                self.program.programs["foliage_shader"],
                self.vbo.vbos["sakura_canopy_deep"],
            ),
            "sakura_blossom_light": self.get_vao(
                self.program.programs["foliage_shader"],
                self.vbo.vbos["sakura_blossom_light"],
            ),
            "sakura_blossom_deep": self.get_vao(
                self.program.programs["foliage_shader"],
                self.vbo.vbos["sakura_blossom_deep"],
            ),
            "water_surface": self.get_vao(
                self.program.programs["water_shader"],
                self.vbo.vbos["water_surface"],
            ),
            "ice_surface": self.get_vao(
                self.program.programs["ice_shader"],
                self.vbo.vbos["water_surface"],
            ),
            "island_mound": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["island_mound"],
            ),
            "island_grass": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["island_grass"],
            ),
            "pond_rock": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["pond_rock"],
            ),
            "water_reflection": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["water_reflection"],
            ),
            "floating_petals": self.get_vao(
                self.program.programs["foliage_shader"],
                self.vbo.vbos["floating_petals"],
            ),
            "fuji_peak": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["fuji_peak"],
            ),
            "fuji_snowcap": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["fuji_snowcap"],
            ),
            "gable_roof": self.get_vao(
                self.program.programs["default_color"],
                self.vbo.vbos["gable_roof"],
            ),
            "sun_disc": self.get_vao(
                self.program.programs["emissive_color"],
                self.vbo.vbos["sun_disc"],
            ),
        }

    def get_vao(self, program, vbo):
        return self.ctx.vertex_array(
            program,
            [(vbo.vbo, vbo.format, *vbo.attribs)],
        )

    def destroy(self):
        for vao in self.vaos.values():
            vao.release()

        self.vbo.destroy()
        self.program.destroy()
