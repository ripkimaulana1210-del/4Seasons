from collections import defaultdict

import numpy as np

from .model import BaseModelColor, _write_fog_uniforms, _write_shadow_uniforms
from .paths import SHADER_DIR


class InstancedColorRenderer:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = self.load_program()
        self.batches = {}
        self.scene_id = None
        self.objects_signature = None
        self.default_program = app.mesh.vao.program.programs["default_color"]

    def load_program(self):
        with open(SHADER_DIR / "instanced_color.vert", "r", encoding="utf-8") as file:
            vertex_shader = file.read()
        with open(SHADER_DIR / "instanced_color.frag", "r", encoding="utf-8") as file:
            fragment_shader = file.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def is_eligible(self, obj):
        if getattr(obj, "is_background", False):
            return False
        if not isinstance(obj, BaseModelColor):
            return False
        if obj.program is not self.default_program:
            return False
        return type(obj).update is BaseModelColor.update

    def split(self, objects):
        batched = []
        normal = []
        for obj in objects:
            if self.is_eligible(obj):
                batched.append(obj)
            else:
                normal.append(obj)
        return batched, normal

    def rebuild(self, scene, objects):
        self.clear_batches()
        grouped = defaultdict(list)
        for obj in objects:
            grouped[obj.vao_name].append(obj)

        for vao_name, group in grouped.items():
            self.batches[vao_name] = self.create_batch(vao_name, group)
        self.scene_id = id(scene)
        self.objects_signature = tuple(id(obj) for obj in objects)

    def create_batch(self, vao_name, objects):
        rows = []
        for obj in objects:
            row = []
            for column in obj.m_model.to_list():
                row.extend(column)
            row.extend([obj.color.x, obj.color.y, obj.color.z])
            rows.append(row)

        data = np.array(rows, dtype="f4")
        instance_buffer = self.ctx.buffer(data.tobytes())
        vbo = self.app.mesh.vao.vbo.vbos[vao_name]
        vao = self.ctx.vertex_array(
            self.program,
            [
                (vbo.vbo, vbo.format, *vbo.attribs),
                (
                    instance_buffer,
                    "4f 4f 4f 4f 3f /i",
                    "in_model_col0",
                    "in_model_col1",
                    "in_model_col2",
                    "in_model_col3",
                    "in_instance_color",
                ),
            ],
        )
        return {"vao": vao, "buffer": instance_buffer, "count": len(objects)}

    def write_common_uniforms(self):
        light = self.app.light
        self.program["m_proj"].write(self.app.camera.m_proj)
        self.program["m_view"].write(self.app.camera.m_view)
        self.program["cam_pos"].write(self.app.camera.position)
        self.program["light.position"].write(light.position)
        self.program["light.Ia"].write(light.Ia)
        self.program["light.Id"].write(light.Id)
        self.program["light.Is"].write(light.Is)
        _write_fog_uniforms(self.program, self.app)
        _write_shadow_uniforms(self.program, self.app)

    def render(self, scene, objects):
        if not objects:
            return
        signature = tuple(id(obj) for obj in objects)
        if id(scene) != self.scene_id or signature != self.objects_signature:
            self.rebuild(scene, objects)

        self.write_common_uniforms()
        for batch in self.batches.values():
            batch["vao"].render(instances=batch["count"])
        return len(self.batches)

    def clear_batches(self):
        for batch in self.batches.values():
            batch["vao"].release()
            batch["buffer"].release()
        self.batches = {}
        self.objects_signature = None

    def destroy(self):
        self.clear_batches()
        self.program.release()
