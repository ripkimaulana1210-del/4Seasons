import math

from ..data.scene_config import HOUSE_SPECS
from ..models import (
    AtmosphereSunDisc,
    AuroraBand,
    CloudLayer,
    ColorCube,
    ColorPlane,
    FireflyGlow,
    FloatingPetals,
    FujiPeak,
    FujiSnowcap,
    IceSurface,
    IslandGrass,
    IslandMound,
    NightGlow,
    PondRock,
    RainDrop,
    SakuraBlossomDeep,
    SakuraBlossomLight,
    SakuraCanopyDeep,
    SakuraCanopyLight,
    SakuraWood,
    MoonDisc,
    SkyDome,
    SunDisc,
    TexturedCube,
    TexturedGableRoof,
    TexturedPlane,
    TransitionCube,
    WaterReflection,
    WaterSurface,
    WindStreak,
)


class SceneVillageRoadMixin:
    def add_road_segment(self, app, start, end, width, color, y=0.010):
        dx = end[0] - start[0]
        dz = end[1] - start[1]
        length = math.sqrt(dx * dx + dz * dz)
        if length < 0.001:
            return

        yaw = math.degrees(math.atan2(dx, dz))
        self.add_object(
            TexturedPlane(
                app,
                pos=((start[0] + end[0]) * 0.5, y, (start[1] + end[1]) * 0.5),
                rot=(0, yaw, 0),
                scale=(width * 0.5, 1, length * 0.5),
                texture_name=self.season_value("road_texture", "road"),
                tint=color,
                repeat=(max(1.0, width * 1.6), max(1.0, length * 1.3)),
            )
        )
