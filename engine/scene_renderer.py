from .model import (
    BaseModelEmissive,
    BaseModelEmissiveTexture,
    FloatingPetals,
    IceSurface,
    SkyDome,
    WaterReflection,
    WaterSurface,
)
from .instancing import InstancedColorRenderer
from .shadow import ShadowMapRenderer


WATER_PASS_TYPES = (WaterSurface, IceSurface, WaterReflection, FloatingPetals)
TRANSPARENT_PASS_TYPES = (BaseModelEmissive, BaseModelEmissiveTexture)


class SceneRenderer:
    def __init__(self, app):
        self.app = app
        self.scene = app.scene
        self.shadow_renderer = ShadowMapRenderer(app)
        self.app.shadow_renderer = self.shadow_renderer
        self.instanced_color = InstancedColorRenderer(app)

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

    def is_visible_at_distance(self, obj, max_distance):
        if max_distance <= 0.0 or self.is_cull_exempt(obj):
            return True

        pos = getattr(obj, "pos", None)
        if pos is None:
            return True

        camera_pos = self.app.camera.position
        dx = pos.x - camera_pos.x
        dy = pos.y - camera_pos.y
        dz = pos.z - camera_pos.z
        radius = self.object_radius(obj)
        limit = max_distance + radius
        return (dx * dx + dy * dy + dz * dz) <= (limit * limit)

    def cull_objects(self, objects, pass_name):
        max_distance = self.culling_distance(pass_name)
        if max_distance <= 0.0:
            return objects, 0

        visible = []
        culled = 0
        for obj in objects:
            if self.is_visible_at_distance(obj, max_distance):
                visible.append(obj)
            else:
                culled += 1
        return visible, culled

    def render_objects(self, objects):
        for obj in objects:
            obj.render()
        return len(objects)

    def render(self):
        self.scene = self.app.scene
        sky = []
        background = []
        opaque = []
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
            else:
                opaque.append(obj)

        opaque, culled_opaque = self.cull_objects(opaque, "opaque")
        transparent, culled_transparent = self.cull_objects(transparent, "transparent")

        shadow_opaque, shadow_distance_culled = self.cull_objects(opaque, "shadow")
        self.shadow_renderer.render(shadow_opaque)
        transparent.sort(key=self.transparent_distance, reverse=True)
        batched, opaque = self.instanced_color.split(opaque)
        sky_draws = self.render_objects(sky)
        background_draws = self.render_objects(background)
        opaque_draws = self.render_objects(opaque)
        instanced_draws = self.instanced_color.render(self.scene, batched) or 0
        water_draws = self.render_objects(water)
        transparent_draws = self.render_objects(transparent)
        visible_objects = len(sky) + len(background) + len(opaque) + len(water) + len(transparent) + len(batched)
        shadow_casters = sum(1 for obj in shadow_opaque if self.shadow_renderer.casts_shadow(obj))

        self.app.render_stats = {
            "objects": len(self.scene.objects),
            "visible": visible_objects,
            "culled": culled_opaque + culled_transparent,
            "shadow_culled": shadow_distance_culled,
            "sky": len(sky),
            "background": len(background),
            "opaque": len(opaque),
            "water": len(water),
            "transparent": len(transparent),
            "instanced_objects": len(batched),
            "instanced_batches": instanced_draws,
            "draw_calls": sky_draws + background_draws + opaque_draws + instanced_draws + water_draws + transparent_draws,
            "shadow_casters": shadow_casters,
            "shadow_size": self.shadow_renderer.size,
        }

    def destroy(self):
        self.instanced_color.destroy()
        self.shadow_renderer.destroy()
