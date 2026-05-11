from pyglm import glm

from .core import BaseModelColor, _lerp_vec3, _set_uniform_value


class SakuraWood(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_wood",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.26, 0.16, 0.09),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraCanopyLight(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_canopy_light",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.70, 0.90),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraCanopyDeep(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_canopy_deep",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.92, 0.36, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraBlossomLight(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_blossom_light",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.78, 0.90),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class SakuraBlossomDeep(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="sakura_blossom_deep",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.98, 0.50, 0.68),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class WaterSurface(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="water_surface",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.26, 0.48, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)

    def update(self):
        super().update()
        season = self.app.season_controller.get_blended_season()
        effect_index = self.app.season_controller.season_effect_index()
        self.program["u_time"].value = self.app.time
        self.program["u_water_mode"].value = effect_index
        self.program["u_wave_strength"].value = season.get("water_wave_strength", 1.0)
        self.program["u_sparkle_strength"].value = season.get("water_sparkle_strength", 0.5)
        self.program["u_season_mix"].value = season.get("water_season_mix", 0.5)
        self.program["u_accent_color"].write(glm.vec3(season.get("water_accent_color", (0.72, 0.90, 1.0))))


class IceSurface(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="ice_surface",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.70, 0.88, 0.96),
    ):
        self.base_pos = glm.vec3(pos)
        self.base_scale = glm.vec3(scale)
        self.base_color = glm.vec3(color)
        super().__init__(app, vao_name, pos, rot, scale, color)

    def melt_progress(self):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None or transition["pair"] != "winter->spring":
            return 0.0
        return transition.get("melt_intensity", transition["eased"])

    def update(self):
        melt = self.melt_progress()
        cool_water = glm.vec3(0.42, 0.70, 0.82)
        self.pos = glm.vec3(
            self.base_pos.x,
            self.base_pos.y - 0.018 * melt,
            self.base_pos.z,
        )
        self.scale = glm.vec3(
            self.base_scale.x * (1.0 - 0.18 * melt),
            self.base_scale.y,
            self.base_scale.z * (1.0 - 0.18 * melt),
        )
        self.color = _lerp_vec3(self.base_color, cool_water, min(1.0, melt * 1.15))
        self.m_model = self.get_model_matrix()
        super().update()
        _set_uniform_value(self.program, "u_melt", melt)


class IslandMound(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="island_mound",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.24, 0.34, 0.16),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class IslandGrass(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="island_grass",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.42, 0.55, 0.20),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class PondRock(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="pond_rock",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.43, 0.42, 0.38),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class WaterReflection(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="water_reflection",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.92, 0.35, 0.62),
    ):
        super().__init__(app, vao_name, pos, rot, scale, color)


class FloatingPetals(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="floating_petals",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(1.00, 0.62, 0.82),
    ):
        self.base_scale = glm.vec3(scale)
        self.base_color = glm.vec3(color)
        super().__init__(app, vao_name, pos, rot, scale, color)

    def visibility(self):
        transition = self.app.season_controller.transition_snapshot()
        if transition is None:
            return 1.0

        pair = transition["pair"]
        if pair == "spring->summer":
            return transition.get("petal_fade", 1.0)
        if pair == "autumn->winter":
            return 1.0 - transition.get("snow_intensity", transition["eased"])
        if pair == "winter->spring":
            return transition.get("petal_intensity", transition["eased"])
        return 1.0

    def update(self):
        visibility = max(0.015, self.visibility())
        self.scale = self.base_scale * visibility
        self.color = self.base_color
        self.m_model = self.get_model_matrix()
        super().update()


class FujiPeak(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="fuji_peak",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.44, 0.50, 0.60),
    ):
        self.is_background = True
        super().__init__(app, vao_name, pos, rot, scale, color)


class FujiSnowcap(BaseModelColor):
    def __init__(
        self,
        app,
        vao_name="fuji_snowcap",
        pos=(0, 0, 0),
        rot=(0, 0, 0),
        scale=(1, 1, 1),
        color=(0.96, 0.97, 1.00),
    ):
        self.is_background = True
        super().__init__(app, vao_name, pos, rot, scale, color)
