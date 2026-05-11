import math

from ..models import (
    BaseModelColor,
    BaseModelEmissive,
    BaseModelEmissiveTexture,
    BaseModelTexture,
    FloatingPetals,
    IceSurface,
    SkyDome,
    WaterReflection,
    WaterSurface,
)
from .instancing import InstancedColorRenderer
from .instanced_emissive import InstancedEmissiveRenderer
from .instanced_texture import InstancedTextureRenderer
from .shadow import ShadowMapRenderer


WATER_PASS_TYPES = (WaterSurface, IceSurface, WaterReflection, FloatingPetals)
TRANSPARENT_PASS_TYPES = (BaseModelEmissive, BaseModelEmissiveTexture)


class SceneRenderer:
    def __init__(self, app):
        self.app = app
        self.scene = app.scene
        shadow_size = int(app.quality.current.get("shadow_map_size", 2048))
        self.shadow_renderer = ShadowMapRenderer(app, size=max(256, shadow_size))
        self.app.shadow_renderer = self.shadow_renderer
        self.instanced_color = InstancedColorRenderer(app)
        self.instanced_emissive = InstancedEmissiveRenderer(app)
        self.instanced_texture = InstancedTextureRenderer(app)
        self._frustum_planes = None
        # Per-frame uniform cache: tracks which programs already got per-frame writes
        self._per_frame_stamp = -1

    def transparent_distance(self, obj):
        pos = getattr(obj, "pos", None)
        if pos is None:
            return 0.0

        camera_pos = self.app.camera.position
        dx = pos.x - camera_pos.x
        dy = pos.y - camera_pos.y
        dz = pos.z - camera_pos.z
        return dx * dx + dy * dy + dz * dz

    def object_radius(self, obj):
        scale = getattr(obj, "scale", None)
        if scale is None:
            return 0.0
        return max(abs(scale.x), abs(scale.y), abs(scale.z)) * 1.8

    def is_cull_exempt(self, obj):
        if isinstance(obj, SkyDome):
            return True
        if getattr(obj, "is_background", False):
            return True
        if isinstance(obj, WATER_PASS_TYPES):
            return True
        return self.object_radius(obj) > 12.0

    def culling_distance(self, pass_name):
        config = self.app.quality.current.get("culling", {})
        key = f"{pass_name}_distance"
        return float(config.get(key, 0.0))

    # ── Frustum culling ──────────────────────────────────────────────

    def extract_frustum_planes(self):
        """Extract 6 frustum planes from the combined projection*view matrix.
        Each plane is (a, b, c, d) such that ax+by+cz+d >= 0 means inside."""
        m = self.app.camera.m_proj * self.app.camera.m_view
        # Left, Right, Bottom, Top, Near, Far
        rows = [
            (m[0][3] + m[0][0], m[1][3] + m[1][0], m[2][3] + m[2][0], m[3][3] + m[3][0]),
            (m[0][3] - m[0][0], m[1][3] - m[1][0], m[2][3] - m[2][0], m[3][3] - m[3][0]),
            (m[0][3] + m[0][1], m[1][3] + m[1][1], m[2][3] + m[2][1], m[3][3] + m[3][1]),
            (m[0][3] - m[0][1], m[1][3] - m[1][1], m[2][3] - m[2][1], m[3][3] - m[3][1]),
            (m[0][3] + m[0][2], m[1][3] + m[1][2], m[2][3] + m[2][2], m[3][3] + m[3][2]),
            (m[0][3] - m[0][2], m[1][3] - m[1][2], m[2][3] - m[2][2], m[3][3] - m[3][2]),
        ]

        # Normalize planes
        planes = []
        for a, b, c, d in rows:
            length = math.sqrt(a * a + b * b + c * c)
            if length > 1e-8:
                inv = 1.0 / length
                planes.append((a * inv, b * inv, c * inv, d * inv))
            else:
                planes.append((0.0, 0.0, 0.0, 0.0))
        return planes

    def is_in_frustum(self, obj, planes):
        """Test if object's bounding sphere intersects the view frustum."""
        pos = getattr(obj, "pos", None)
        if pos is None:
            return True
        radius = self.object_radius(obj)
        px, py, pz = pos.x, pos.y, pos.z
        for a, b, c, d in planes:
            if a * px + b * py + c * pz + d < -radius:
                return False
        return True

    def is_visible(self, obj, max_distance, planes):
        """Combined distance + frustum culling check."""
        if self.is_cull_exempt(obj):
            return True

        pos = getattr(obj, "pos", None)
        if pos is None:
            return True

        # Distance culling (cheaper, do first)
        if max_distance > 0.0:
            camera_pos = self.app.camera.position
            dx = pos.x - camera_pos.x
            dy = pos.y - camera_pos.y
            dz = pos.z - camera_pos.z
            radius = self.object_radius(obj)
            limit = max_distance + radius
            if (dx * dx + dy * dy + dz * dz) > (limit * limit):
                return False

        # Frustum culling
        if planes is not None:
            if not self.is_in_frustum(obj, planes):
                return False

        return True

    def cull_objects(self, objects, pass_name, use_frustum=True):
        max_distance = self.culling_distance(pass_name)
        planes = self._frustum_planes if use_frustum else None
        if max_distance <= 0.0 and planes is None:
            return objects, 0

        visible = []
        culled = 0
        for obj in objects:
            if self.is_visible(obj, max_distance, planes):
                visible.append(obj)
            else:
                culled += 1
        return visible, culled

    # ── Shadow helpers ────────────────────────────────────────────────

    def shadow_min_scale(self):
        """Minimum bounding radius for an object to be a shadow caster."""
        return float(self.app.quality.current.get("shadow_min_scale", 0.0))

    def filter_shadow_casters(self, objects):
        """Filter objects for shadow pass: skip tiny objects that contribute
        nothing visible to the shadow map."""
        min_scale = self.shadow_min_scale()
        if min_scale <= 0.0:
            return objects
        result = []
        for obj in objects:
            if self.object_radius(obj) >= min_scale:
                result.append(obj)
            elif self.is_cull_exempt(obj):
                result.append(obj)
        return result

    # ── Per-frame uniform optimization ────────────────────────────────

    def write_per_frame_uniforms(self):
        """Prime per-frame uniforms on shared programs once per frame."""
        frame = self.app.frame_count
        if self._per_frame_stamp == frame:
            return
        self._per_frame_stamp = frame

        primed_programs = set()
        for obj in self.scene.objects:
            prog = getattr(obj, "program", None)
            if prog is None:
                continue
            pid = id(prog)
            if pid in primed_programs:
                continue
            write_method = getattr(obj, "write_per_frame_uniforms", None)
            if callable(write_method):
                write_method(force=True)
                primed_programs.add(pid)

    # ── Main render ───────────────────────────────────────────────────

    def render_objects(self, objects):
        for obj in objects:
            obj.render()
        return len(objects)

    def render_objects_fast(self, objects):
        """Render objects with minimal per-object uniform writes since
        per-frame uniforms are already set."""
        for obj in objects:
            obj.render_fast()
        return len(objects)

    def can_render_fast(self, obj):
        if isinstance(obj, BaseModelColor):
            return type(obj).update is BaseModelColor.update
        if isinstance(obj, BaseModelTexture):
            return type(obj).update is BaseModelTexture.update
        if isinstance(obj, BaseModelEmissive):
            return type(obj).update is BaseModelEmissive.update
        return False

    def split_fast_render(self, objects):
        fast = []
        normal = []
        for obj in objects:
            if self.can_render_fast(obj):
                fast.append(obj)
            else:
                normal.append(obj)
        return fast, normal

    def state_sort_key(self, obj):
        program_id = id(getattr(obj, "program", None))
        vao_name = getattr(obj, "vao_name", "")
        texture_id = id(getattr(obj, "texture", None))
        return (program_id, vao_name, texture_id)

    def render(self):
        self.scene = self.app.scene
        target_shadow_size = int(self.app.quality.current.get("shadow_map_size", self.shadow_renderer.size))
        target_shadow_size = max(256, target_shadow_size)
        if target_shadow_size != self.shadow_renderer.size:
            self.shadow_renderer.resize(target_shadow_size)

        # Extract frustum planes once per frame
        self._frustum_planes = self.extract_frustum_planes()

        sky = []
        background = []
        opaque = []
        opaque_textured = []
        water = []
        transparent = []

        for obj in self.scene.objects:
            if isinstance(obj, SkyDome):
                sky.append(obj)
            elif getattr(obj, "is_background", False):
                background.append(obj)
            elif isinstance(obj, WATER_PASS_TYPES):
                water.append(obj)
            elif isinstance(obj, TRANSPARENT_PASS_TYPES):
                transparent.append(obj)
            elif isinstance(obj, BaseModelTexture):
                opaque_textured.append(obj)
            else:
                opaque.append(obj)

        opaque, culled_opaque = self.cull_objects(opaque, "opaque")
        opaque_textured, culled_textured = self.cull_objects(opaque_textured, "opaque")
        transparent, culled_transparent = self.cull_objects(transparent, "transparent")

        # Shadow pass — filter out tiny objects
        all_shadow_eligible = opaque + opaque_textured
        shadow_opaque, shadow_distance_culled = self.cull_objects(all_shadow_eligible, "shadow", use_frustum=False)
        shadow_opaque = self.filter_shadow_casters(shadow_opaque)
        self.shadow_renderer.render(shadow_opaque)

        # Write per-frame uniforms once for all shared programs
        self.write_per_frame_uniforms()

        transparent.sort(key=self.transparent_distance, reverse=True)

        # Split color objects into instanced vs individual
        batched_color, opaque = self.instanced_color.split(opaque)
        # Split textured objects into instanced vs individual
        batched_texture, opaque_textured = self.instanced_texture.split(opaque_textured)
        # Split emissive/transparent objects into instanced vs individual
        batched_emissive, transparent = self.instanced_emissive.split(transparent)
        opaque_fast, opaque_dynamic = self.split_fast_render(opaque)
        opaque_fast.sort(key=self.state_sort_key)
        opaque_dynamic.sort(key=self.state_sort_key)
        opaque_textured.sort(key=self.state_sort_key)

        sky_draws = self.render_objects(sky)
        background_draws = self.render_objects(background)

        # Use fast render for objects that benefit from per-frame caching
        opaque_fast_draws = self.render_objects_fast(opaque_fast)
        opaque_dynamic_draws = self.render_objects(opaque_dynamic)
        opaque_textured_draws = self.render_objects(opaque_textured)

        instanced_color_draws = self.instanced_color.render(self.scene, batched_color) or 0
        instanced_texture_draws = self.instanced_texture.render(self.scene, batched_texture) or 0

        water_draws = self.render_objects(water)

        instanced_emissive_draws = self.instanced_emissive.render(self.scene, batched_emissive) or 0
        transparent_draws = self.render_objects(transparent)

        visible_objects = (
            len(sky) + len(background) + len(opaque_fast) + len(opaque_dynamic) + len(opaque_textured)
            + len(water) + len(transparent)
            + len(batched_color) + len(batched_texture) + len(batched_emissive)
        )
        total_instanced = len(batched_color) + len(batched_texture) + len(batched_emissive)
        total_instanced_batches = instanced_color_draws + instanced_texture_draws + instanced_emissive_draws
        shadow_casters = sum(1 for obj in shadow_opaque if self.shadow_renderer.casts_shadow(obj))

        self.app.render_stats = {
            "objects": len(self.scene.objects),
            "visible": visible_objects,
            "culled": culled_opaque + culled_textured + culled_transparent,
            "shadow_culled": shadow_distance_culled,
            "sky": len(sky),
            "background": len(background),
            "opaque": len(opaque_fast) + len(opaque_dynamic) + len(opaque_textured),
            "water": len(water),
            "transparent": len(transparent),
            "instanced_objects": total_instanced,
            "instanced_batches": total_instanced_batches,
            "draw_calls": (
                sky_draws + background_draws + opaque_fast_draws + opaque_dynamic_draws + opaque_textured_draws
                + total_instanced_batches + water_draws + transparent_draws
            ),
            "shadow_casters": shadow_casters,
            "shadow_size": self.shadow_renderer.size,
        }

    def destroy(self):
        self.instanced_color.destroy()
        self.instanced_texture.destroy()
        self.instanced_emissive.destroy()
        self.shadow_renderer.destroy()
