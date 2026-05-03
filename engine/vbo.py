import math

import numpy as np

from .geometry.environment_geometry import (
    generate_floating_petal_data,
    generate_fuji_peak_data,
    generate_fuji_snowcap_data,
    generate_gable_roof_data,
    generate_island_grass_data,
    generate_island_mound_data,
    generate_rock_data,
    generate_sun_disc_data,
    generate_water_reflection_data,
    generate_water_surface_data,
)
from .geometry.sakura_geometry import (
    generate_sakura_blossom_data,
    generate_sakura_canopy_fill_data,
    generate_sakura_wood_data,
)

POND_RADIUS = 5.55
ISLAND_RADIUS = 2.35
ISLAND_GRASS_RADIUS = 2.16
WATER_REFLECTION_INNER_RADIUS = 2.25
FLOATING_PETAL_INNER_RADIUS = 2.12


class VBO:
    def __init__(self, ctx):
        self.vbos = {
            "color_cube": ColorCubeVBO(ctx),
            "color_plane": ColorPlaneVBO(ctx),
            "textured_cube": TexturedCubeVBO(ctx),
            "textured_gable_roof": TexturedGableRoofVBO(ctx),
            "textured_plane": TexturedPlaneVBO(ctx),
            "sky_dome": SkyDomeVBO(ctx),
            "sakura_wood": SakuraWoodVBO(ctx),
            "sakura_canopy_light": SakuraCanopyLightVBO(ctx),
            "sakura_canopy_deep": SakuraCanopyDeepVBO(ctx),
            "sakura_blossom_light": SakuraBlossomLightVBO(ctx),
            "sakura_blossom_deep": SakuraBlossomDeepVBO(ctx),
            "water_surface": WaterSurfaceVBO(ctx),
            "island_mound": IslandMoundVBO(ctx),
            "island_grass": IslandGrassVBO(ctx),
            "pond_rock": PondRockVBO(ctx),
            "water_reflection": WaterReflectionVBO(ctx),
            "floating_petals": FloatingPetalsVBO(ctx),
            "fuji_peak": FujiPeakVBO(ctx),
            "fuji_snowcap": FujiSnowcapVBO(ctx),
            "gable_roof": GableRoofVBO(ctx),
            "sun_disc": SunDiscVBO(ctx),
        }

    def destroy(self):
        for vbo in self.vbos.values():
            vbo.destroy()


class BaseVBO:
    format = None
    attribs = None

    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.ctx.buffer(self.get_vertex_data().astype("f4").tobytes())

    def get_vertex_data(self):
        raise NotImplementedError

    def destroy(self):
        self.vbo.release()


class ColorPlaneVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        positions = [
            (-1, 0, -1),
            (1, 0, -1),
            (1, 0, 1),
            (-1, 0, 1),
        ]

        indices = [
            (0, 2, 1),
            (0, 3, 2),
        ]

        normals = [(0, 1, 0)] * 6

        def get_data(verts, inds):
            return np.array([verts[i] for tri in inds for i in tri], dtype="f4")

        pos_data = get_data(positions, indices)
        norm_data = np.array(normals, dtype="f4")

        return np.hstack([norm_data, pos_data])


class ColorCubeVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        vertices = np.array(
            [
                (-1, -1, 1),
                (1, -1, 1),
                (1, 1, 1),
                (-1, 1, 1),
                (-1, 1, -1),
                (-1, -1, -1),
                (1, -1, -1),
                (1, 1, -1),
            ],
            dtype="f4",
        )

        faces = [
            ((0, 2, 3), (0, 1, 2), (0, 0, 1)),
            ((1, 7, 2), (1, 6, 7), (1, 0, 0)),
            ((6, 5, 4), (4, 7, 6), (0, 0, -1)),
            ((3, 4, 5), (3, 5, 0), (-1, 0, 0)),
            ((3, 7, 4), (3, 2, 7), (0, 1, 0)),
            ((0, 6, 1), (0, 5, 6), (0, -1, 0)),
        ]

        data = []

        for tri_a, tri_b, normal in faces:
            for tri in (tri_a, tri_b):
                for idx in tri:
                    data.extend(normal)
                    data.extend(vertices[idx])

        return np.array(data, dtype="f4").reshape(-1, 6)


class TexturedPlaneVBO(BaseVBO):
    format = "3f 3f 2f"
    attribs = ["in_normal", "in_position", "in_uv"]

    def get_vertex_data(self):
        normal = (0, 1, 0)
        vertices = [
            ((-1, 0, -1), (0, 0)),
            ((1, 0, -1), (1, 0)),
            ((1, 0, 1), (1, 1)),
            ((-1, 0, 1), (0, 1)),
        ]
        indices = [(0, 2, 1), (0, 3, 2)]
        data = []

        for tri in indices:
            for idx in tri:
                position, uv = vertices[idx]
                data.extend(normal)
                data.extend(position)
                data.extend(uv)

        return np.array(data, dtype="f4").reshape(-1, 8)


class TexturedCubeVBO(BaseVBO):
    format = "3f 3f 2f"
    attribs = ["in_normal", "in_position", "in_uv"]

    def get_vertex_data(self):
        faces = [
            (
                (0, 0, 1),
                [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)],
            ),
            (
                (1, 0, 0),
                [(1, -1, 1), (1, -1, -1), (1, 1, -1), (1, 1, 1)],
            ),
            (
                (0, 0, -1),
                [(1, -1, -1), (-1, -1, -1), (-1, 1, -1), (1, 1, -1)],
            ),
            (
                (-1, 0, 0),
                [(-1, -1, -1), (-1, -1, 1), (-1, 1, 1), (-1, 1, -1)],
            ),
            (
                (0, 1, 0),
                [(-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1)],
            ),
            (
                (0, -1, 0),
                [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)],
            ),
        ]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tris = [(0, 1, 2), (0, 2, 3)]
        data = []

        for normal, corners in faces:
            for tri in tris:
                for idx in tri:
                    data.extend(normal)
                    data.extend(corners[idx])
                    data.extend(uvs[idx])

        return np.array(data, dtype="f4").reshape(-1, 8)


class TexturedGableRoofVBO(BaseVBO):
    format = "3f 3f 2f"
    attribs = ["in_normal", "in_position", "in_uv"]

    def get_vertex_data(self):
        data = []

        left_front = np.array([-1.0, 0.0, 1.0], dtype="f4")
        right_front = np.array([1.0, 0.0, 1.0], dtype="f4")
        ridge_front = np.array([0.0, 1.0, 1.0], dtype="f4")
        left_back = np.array([-1.0, 0.0, -1.0], dtype="f4")
        right_back = np.array([1.0, 0.0, -1.0], dtype="f4")
        ridge_back = np.array([0.0, 1.0, -1.0], dtype="f4")

        def normal_for(p0, p1, p2):
            normal = np.cross(p1 - p0, p2 - p0)
            length = np.linalg.norm(normal)
            if length < 1e-6:
                return np.array([0.0, 1.0, 0.0], dtype="f4")
            return (normal / length).astype("f4")

        def push_vertex(normal, point, uv):
            data.extend(normal)
            data.extend(point)
            data.extend(uv)

        def push_tri(p0, p1, p2, uv0, uv1, uv2):
            normal = normal_for(p0, p1, p2)
            push_vertex(normal, p0, uv0)
            push_vertex(normal, p1, uv1)
            push_vertex(normal, p2, uv2)
            back = -normal
            push_vertex(back, p2, uv2)
            push_vertex(back, p1, uv1)
            push_vertex(back, p0, uv0)

        def push_quad(p0, p1, p2, p3):
            push_tri(p0, p1, p2, (0, 0), (0.5, 1), (1, 1))
            push_tri(p0, p2, p3, (0, 0), (1, 1), (1, 0))

        push_quad(left_front, ridge_front, ridge_back, left_back)
        push_quad(ridge_front, right_front, right_back, ridge_back)
        push_tri(left_front, right_front, ridge_front, (0, 0), (1, 0), (0.5, 1))
        push_tri(right_back, left_back, ridge_back, (0, 0), (1, 0), (0.5, 1))
        push_quad(right_front, left_front, left_back, right_back)

        return np.array(data, dtype="f4").reshape(-1, 8)


class SkyDomeVBO(BaseVBO):
    format = "3f"
    attribs = ["in_position"]

    def get_vertex_data(self):
        rings = 18
        sectors = 72
        data = []

        for ring in range(rings):
            theta0 = (ring / rings) * (math.pi * 0.58)
            theta1 = ((ring + 1) / rings) * (math.pi * 0.58)
            y0 = math.cos(theta0)
            y1 = math.cos(theta1)
            r0 = math.sin(theta0)
            r1 = math.sin(theta1)

            for sector in range(sectors):
                phi0 = (sector / sectors) * math.tau
                phi1 = ((sector + 1) / sectors) * math.tau
                p00 = (math.cos(phi0) * r0, y0, math.sin(phi0) * r0)
                p01 = (math.cos(phi1) * r0, y0, math.sin(phi1) * r0)
                p10 = (math.cos(phi0) * r1, y1, math.sin(phi0) * r1)
                p11 = (math.cos(phi1) * r1, y1, math.sin(phi1) * r1)

                data.extend([p00, p10, p11, p00, p11, p01])

        return np.array(data, dtype="f4").reshape(-1, 3)


class SakuraWoodVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        return generate_sakura_wood_data(seed=12)


class SakuraCanopyLightVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        return generate_sakura_canopy_fill_data(seed=12, variant=0)


class SakuraCanopyDeepVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        return generate_sakura_canopy_fill_data(seed=12, variant=1)


class SakuraBlossomLightVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        return generate_sakura_blossom_data(seed=12, variant=0)


class SakuraBlossomDeepVBO(BaseVBO):
    format = "3f 3f"
    attribs = [0, 1]

    def get_vertex_data(self):
        return generate_sakura_blossom_data(seed=12, variant=1)


class WaterSurfaceVBO(BaseVBO):
    format = "3f 3f 2f"
    attribs = ["in_normal", "in_position", "in_uv"]

    def get_vertex_data(self):
        return generate_water_surface_data(radius=POND_RADIUS, rings=40, sectors=144)

class IslandMoundVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_island_mound_data(radius=ISLAND_RADIUS, rings=10, sectors=84)


class IslandGrassVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_island_grass_data(seed=21, count=1180, radius=ISLAND_GRASS_RADIUS)


class PondRockVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_rock_data(lat_steps=8, lon_steps=14)


class GableRoofVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_gable_roof_data()


class SunDiscVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_sun_disc_data(sectors=128)


class WaterReflectionVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_water_reflection_data(
            seed=52,
            count=860,
            inner_radius=WATER_REFLECTION_INNER_RADIUS,
            outer_radius=POND_RADIUS - 0.18,
        )


class FloatingPetalsVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_floating_petal_data(
            seed=44,
            count=980,
            inner_radius=FLOATING_PETAL_INNER_RADIUS,
            outer_radius=POND_RADIUS - 0.22,
        )


class FujiPeakVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_fuji_peak_data(radius=1.0, height=1.0)


class FujiSnowcapVBO(BaseVBO):
    format = "3f 3f"
    attribs = ["in_normal", "in_position"]

    def get_vertex_data(self):
        return generate_fuji_snowcap_data(radius=1.0, height=1.0)
