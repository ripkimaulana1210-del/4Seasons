import math

from ..data.scene_config import HOUSE_SPECS, SCENE_LAYOUT
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


class SceneVillageSettlementMixin:
    def add_settlement(self, app, pond_radius_scale):
        add = self.add_object
        road_layout = SCENE_LAYOUT["road"]
        road_radius = road_layout["radius"]
        road_width = road_layout["width"]
        road_color = self.season_color("road_color", (0.36, 0.34, 0.30))
        lane_color = self.season_color("lane_color", (0.43, 0.38, 0.30))
        edge_color = self.season_color("road_edge_color", (0.51, 0.49, 0.43))

        ring_segments = 64
        for i in range(ring_segments):
            a0 = 2.0 * math.pi * i / ring_segments
            a1 = 2.0 * math.pi * (i + 1) / ring_segments
            start = (math.cos(a0) * road_radius, math.sin(a0) * road_radius)
            end = (math.cos(a1) * road_radius, math.sin(a1) * road_radius)
            self.add_road_segment(app, start, end, road_width, road_color)

        # Jalan utama dan beberapa cabang keluar dari pemukiman.
        self.add_road_segment(app, (0.0, road_radius + 0.20), (0.0, 18.5), 1.45, road_color)
        self.add_road_segment(app, (road_radius + 0.20, 0.0), (17.7, 1.45), 1.14, road_color)
        self.add_road_segment(app, (-road_radius - 0.20, 0.0), (-17.7, -1.20), 1.14, road_color)
        self.add_road_segment(app, (0.0, -road_radius - 0.20), (-1.65, -18.5), 1.14, road_color)

        bridge_start = (2.45 * pond_radius_scale, 4.38 * pond_radius_scale)
        bridge_angle = math.atan2(bridge_start[1], bridge_start[0])
        bridge_ring = (
            math.cos(bridge_angle) * road_radius,
            math.sin(bridge_angle) * road_radius,
        )
        self.add_road_segment(app, bridge_start, bridge_ring, 0.92, lane_color)

        for i in range(48):
            angle = 2.0 * math.pi * i / 48.0
            for side in (-1, 1):
                radius = road_radius + side * road_width * 0.62
                add(
                    PondRock(
                        app,
                        pos=(math.cos(angle) * radius, 0.040, math.sin(angle) * radius),
                        rot=(0, i * 19.0 + side * 11.0, 0),
                        scale=(0.15, 0.052, 0.19),
                        color=edge_color,
                    )
                )

        self.add_beautiful_garden(app, pond_radius_scale, road_radius, road_width)

        for idx, (angle_deg, radius, body_scale, body_color, roof_color, trim_color, yaw_offset, variant) in enumerate(HOUSE_SPECS):
            angle = math.radians(angle_deg)
            radial_x = math.cos(angle)
            radial_z = math.sin(angle)
            x = radial_x * radius
            z = radial_z * radius

            front_x = -radial_x
            front_z = -radial_z
            yaw = math.degrees(math.atan2(front_x, front_z)) + yaw_offset
            width, height, depth = body_scale

            road_start = (
                radial_x * (road_radius + road_width * 0.58),
                radial_z * (road_radius + road_width * 0.58),
            )
            road_end = (
                radial_x * (radius - depth - 0.30),
                radial_z * (radius - depth - 0.30),
            )
            self.add_road_segment(app, road_start, road_end, 0.60, lane_color, y=0.012)

            yard_x = radial_x * (radius - depth * 0.15)
            yard_z = radial_z * (radius - depth * 0.15)
            add(
                TexturedPlane(
                    app,
                    pos=(yard_x, 0.008, yard_z),
                    rot=(0, yaw, 0),
                    scale=(width * 1.65, 1, depth * 1.85),
                    texture_name=self.season_value("yard_texture", "grass"),
                    tint=self.season_color("yard_color", (0.31, 0.39, 0.22)),
                    repeat=(2.2, 2.0),
                )
            )

            self.add_house(
                app,
                (x, z),
                yaw,
                body_scale,
                body_color,
                roof_color,
                trim_color,
                has_chimney=idx % 3 != 1,
                variant=variant,
            )
            self.add_house_porch_light(app, x, z, yaw, width, height, depth, variant)
            self.add_house_yard_details(app, idx, x, z, yaw, width, height, depth)

        self.add_village_activity_details(app, road_radius, road_width)
        self.add_outer_grove(app)
