import math

from ..data.scene_config import SCENE_LAYOUT
from ..models import (
    AtmosphereSunDisc,
    AuroraBand,
    CloudLayer,
    ColorCube,
    ColorPlane,
    ContactShadow,
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
from ..scene_parts.buildings import SceneBuildingAdditionsMixin
from ..scene_parts.environment import SceneEnvironmentMixin
from ..scene_parts.garden import SceneGardenMixin
from ..scene_parts.micro_seasons import SceneMicroSeasonMixin
from ..scene_parts.object_upgrades import SceneObjectUpgradeMixin
from ..scene_parts.season_upgrades import SceneSeasonUpgradeMixin
from ..scene_parts.village import SceneVillageMixin


class Scene(
    SceneGardenMixin,
    SceneEnvironmentMixin,
    SceneVillageMixin,
    SceneObjectUpgradeMixin,
    SceneBuildingAdditionsMixin,
    SceneMicroSeasonMixin,
    SceneSeasonUpgradeMixin,
):
    def __init__(self, app):
        self.app = app
        transition = app.season_controller.transition_snapshot()
        self.season = transition["from"] if transition is not None else app.season_controller.current
        self.layout = SCENE_LAYOUT
        self.objects = []
        self.object_layer_counts = {}
        self.object_tag_counts = {}
        self.load()

    def add_object(self, obj, tag=None, layer=None):
        if hasattr(self.app, "quality") and not self.app.quality.should_include(obj):
            return
        obj.scene_tag = tag or self.infer_object_tag(obj)
        obj.scene_layer = layer or self.infer_object_layer(obj)
        self.object_tag_counts[obj.scene_tag] = self.object_tag_counts.get(obj.scene_tag, 0) + 1
        self.object_layer_counts[obj.scene_layer] = self.object_layer_counts.get(obj.scene_layer, 0) + 1
        self.objects.append(obj)

    def infer_object_tag(self, obj):
        return obj.__class__.__name__

    def infer_object_layer(self, obj):
        name = obj.__class__.__name__.lower()
        if "transition" in name:
            return "transition_effect"
        if any(key in name for key in ("water", "ice", "pond")):
            return "water"
        if any(key in name for key in ("rain", "drift", "wind", "firefly", "cloud", "aurora", "sun", "moon", "glow")):
            return "atmosphere"
        if any(key in name for key in ("sakura", "grass", "blossom", "petal")):
            return "vegetation"
        if any(key in name for key in ("roof", "house", "bridge", "gable")):
            return "village"
        return "scene"

    def layer_summary(self):
        return dict(sorted(self.object_layer_counts.items()))

    def tag_summary(self):
        return dict(sorted(self.object_tag_counts.items()))

    def objects_by_layer(self, layer):
        return [obj for obj in self.objects if getattr(obj, "scene_layer", None) == layer]

    def season_color(self, key, default):
        return self.season.get(key, default)

    def season_value(self, key, default):
        return self.season.get(key, default)

    def is_winter(self):
        return self.season_value("seasonal_effect", "") == "winter"

    def load(self):
        add = self.add_object
        app = self.app
        layout = self.layout
        ground_layout = layout["ground"]
        pond_radius_scale = layout["pond"]["radius_scale"]
        island_radius_scale = layout["island"]["radius_scale"]

        self.add_sky(app)

        # Tanah besar. Ini jadi area utama map.
        add(
            TexturedPlane(
                app,
                pos=ground_layout["pos"],
                scale=ground_layout["scale"],
                texture_name=self.season_value("ground_texture", "grass"),
                tint=self.season_color("ground_color", (0.23, 0.33, 0.17)),
                repeat=ground_layout["repeat"],
            ),
            tag="ground",
            layer="terrain",
        )

        # Kolam lingkaran di tengah. Sisanya tetap tanah dari ColorPlane di atas.
        add(
            WaterSurface(
                app,
                pos=layout["pond"]["center"],
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("water_color", (0.16, 0.38, 0.54)),
            ),
            tag="pond_water",
            layer="water",
        )

        self.add_fuji_background(app)

        add(
            WaterReflection(
                app,
                pos=layout["pond"]["center"],
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("water_reflection_color", (0.96, 0.42, 0.70)),
            ),
            tag="pond_reflection",
            layer="water",
        )

        # Pulau kecil lingkaran di tengah kolam untuk pohon sakura.
        add(
            IslandMound(
                app,
                pos=layout["island"]["center"],
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("island_mound_color", (0.25, 0.34, 0.16)),
            ),
            tag="island_mound",
            layer="terrain",
        )

        add(
            IslandGrass(
                app,
                pos=layout["island"]["center"],
                scale=(1.0, 1.0, 1.0),
                color=self.season_color("island_grass_color", (0.42, 0.56, 0.20)),
            ),
            tag="island_grass",
            layer="vegetation",
        )

        tree_layout = layout["sakura_tree"]
        tree_pos = tree_layout["pos"]
        tree_rot = tree_layout["rot"]
        tree_scale = tree_layout["scale"]

        add(
            SakuraWood(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_wood_color", (0.26, 0.16, 0.09)),
            )
        )

        add(
            SakuraCanopyDeep(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_canopy_deep_color", (0.92, 0.34, 0.60)),
            )
        )

        add(
            SakuraCanopyLight(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_canopy_light_color", (1.00, 0.70, 0.90)),
            )
        )

        add(
            SakuraBlossomDeep(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_blossom_deep_color", (0.98, 0.42, 0.66)),
            )
        )

        add(
            SakuraBlossomLight(
                app,
                pos=tree_pos,
                rot=tree_rot,
                scale=tree_scale,
                color=self.season_color("sakura_blossom_light_color", (1.00, 0.78, 0.92)),
            )
        )

        self.add_swing(app)
        self.add_bridge(app)
        self.add_settlement(app, pond_radius_scale)
        self.add_pond_edge_details(app, pond_radius_scale)
        
        # Batu di tepian pulau.
        island_rocks = [
            (1.55, 0.25, 0.10, (0.32, 0.18, 0.24)),
            (1.62, 1.05, 0.06, (0.25, 0.15, 0.20)),
            (1.58, 2.15, 0.08, (0.34, 0.18, 0.25)),
            (1.50, 3.08, 0.04, (0.24, 0.14, 0.18)),
            (1.65, 4.10, 0.07, (0.30, 0.16, 0.22)),
            (1.54, 5.10, 0.03, (0.25, 0.14, 0.18)),
            (1.82, 0.68, 0.07, (0.22, 0.12, 0.16)),
            (1.74, 1.62, 0.06, (0.28, 0.12, 0.18)),
            (1.88, 2.68, 0.05, (0.24, 0.11, 0.16)),
            (1.76, 3.62, 0.06, (0.27, 0.12, 0.18)),
            (1.86, 4.62, 0.07, (0.23, 0.11, 0.17)),
            (1.72, 5.72, 0.05, (0.29, 0.13, 0.18)),
        ]

        for radius, angle, y, scale in island_rocks:
            add(
                PondRock(
                    app,
                    pos=(
                        math.cos(angle) * radius * island_radius_scale,
                        y,
                        math.sin(angle) * radius * island_radius_scale,
                    ),
                    rot=(0, angle * 57.2958, 0),
                    scale=scale,
                    color=(0.44, 0.43, 0.39),
                )
            )

        # Batu kecil di tepi luar kolam lingkaran, di atas tanah.
        pond_edge_rocks = [
            (4.85, 0.15, 0.03, (0.35, 0.14, 0.23)),
            (4.95, 1.35, 0.03, (0.28, 0.12, 0.20)),
            (4.75, 2.75, 0.03, (0.34, 0.13, 0.22)),
            (5.00, 4.05, 0.03, (0.28, 0.12, 0.19)),
            (4.80, 5.25, 0.03, (0.33, 0.13, 0.21)),
            (5.12, 0.82, 0.02, (0.22, 0.10, 0.17)),
            (5.18, 2.05, 0.02, (0.24, 0.10, 0.18)),
            (5.08, 3.40, 0.02, (0.21, 0.10, 0.16)),
            (5.22, 4.72, 0.02, (0.25, 0.10, 0.18)),
        ]

        for radius, angle, y, scale in pond_edge_rocks:
            add(
                PondRock(
                    app,
                    pos=(
                        math.cos(angle) * radius * pond_radius_scale,
                        y,
                        math.sin(angle) * radius * pond_radius_scale,
                    ),
                    rot=(0, angle * 57.2958, 0),
                    scale=scale,
                    color=(0.42, 0.42, 0.38),
                )
            )

        # Semak rendah di sisi belakang kolam agar frame tidak kosong.
        bush_color = self.season_color("bush_color", (0.25, 0.40, 0.20))
        for i in range(12):
            angle = math.radians(188 + i * 10.0)
            radius = (5.85 + 0.35 * math.sin(i * 1.7)) * pond_radius_scale
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.18, math.sin(angle) * radius),
                    rot=(0, i * 23.0, 0),
                    scale=(
                        0.75 + 0.18 * math.sin(i * 0.9),
                        0.30 + 0.07 * math.cos(i * 1.3),
                        0.55 + 0.16 * math.cos(i * 0.8),
                    ),
                    color=(
                        min(1.0, bush_color[0] + 0.03 * math.sin(i)),
                        min(1.0, bush_color[1] + 0.03 * math.cos(i)),
                        min(1.0, bush_color[2] + 0.03 * math.sin(i * 0.7)),
                    ),
                )
            )

        for i in range(5):
            angle = math.radians(208 + i * 22.0)
            radius = (5.35 + 0.20 * math.cos(i)) * pond_radius_scale
            add(
                PondRock(
                    app,
                    pos=(math.cos(angle) * radius, 0.24, math.sin(angle) * radius),
                    rot=(0, i * 31.0, 0),
                    scale=(0.28, 0.10, 0.24) if self.is_winter() else (0.26, 0.12, 0.22),
                    color=self.season_color("winter_snow_color", (0.68, 0.42, 0.72))
                    if self.is_winter()
                    else (0.68, 0.42, 0.72),
                )
            )

        if self.season_value("pond_flowers_enabled", True):
            self.add_pond_flowers(app, pond_radius_scale)

        self.add_object_upgrades(app, pond_radius_scale)
        self.add_building_additions(app, pond_radius_scale)
        self.add_micro_season_accents(app, pond_radius_scale)
        self.add_season_upgrades(app, pond_radius_scale)

        # Lentera batu kecil seperti taman Jepang di sisi kiri belakang.
        lantern_x = -4.45 * pond_radius_scale
        lantern_z = -2.55 * pond_radius_scale
        lantern_color = (0.62, 0.61, 0.55)
        lantern_parts = [
            ((0.38, 0.06, 0.38), (0.00, 0.01, 0.00), (0, 0, 0)),
            ((0.18, 0.36, 0.18), (0.00, 0.43, 0.00), (0, 0, 0)),
            ((0.34, 0.07, 0.34), (0.00, 0.84, 0.00), (0, 0, 0)),
            ((0.22, 0.20, 0.22), (0.00, 1.02, 0.00), (0, 0, 0)),
            ((0.46, 0.06, 0.46), (0.00, 1.24, 0.00), (0, 45, 0)),
            ((0.24, 0.08, 0.24), (0.00, 1.38, 0.00), (0, 45, 0)),
        ]
        for scale, offset, rot in lantern_parts:
            add(
                ColorCube(
                    app,
                    pos=(lantern_x + offset[0], offset[1], lantern_z + offset[2]),
                    rot=rot,
                    scale=scale,
                    color=lantern_color,
                )
            )

        self.add_contact_shadows(app, pond_radius_scale)
        self.add_temperature_indicator(app)
        self.add_seasonal_effects(app, pond_radius_scale)
        self.add_natural_elements(app)
        self.add_emotional_season_marks(app, pond_radius_scale)
        self.add_emotional_transition(app)

        # Petal hanya di area kolam lingkaran.
        if self.season_value("floating_petals_enabled", True):
            add(
                FloatingPetals(
                    app,
                    pos=(0, 0.0, 0),
                    scale=(1.0, 1.0, 1.0),
                    color=self.season_color("floating_petal_color", (1.00, 0.64, 0.84)),
                )
            )

    def add_swing(self, app):
        rope_color = (0.23, 0.16, 0.09)
        seat_color = (0.36, 0.20, 0.10)

        anchor_y = 2.55
        seat_y = 1.35
        x = -0.95
        z = 0.20
        rope_gap = 0.32

        # Tali kiri
        self.add_object(
            ColorCube(
                app,
                pos=(x - rope_gap, (anchor_y + seat_y) * 0.5, z),
                scale=(0.018, (anchor_y - seat_y) * 0.5, 0.018),
                color=rope_color,
            )
        )

        # Tali kanan
        self.add_object(
            ColorCube(
                app,
                pos=(x + rope_gap, (anchor_y + seat_y) * 0.5, z),
                scale=(0.018, (anchor_y - seat_y) * 0.5, 0.018),
                color=rope_color,
            )
        )

        # Papan ayunan
        self.add_object(
            ColorCube(
                app,
                pos=(x, seat_y, z),
                scale=(0.46, 0.055, 0.18),
                color=seat_color,
            )
        )

    def add_fuji_background(self, app):
        add = self.add_object

        # Gunung Fuji hanya menjadi latar: jauh, besar, dan tidak ikut shadow/editor.
        fuji_pos = (-17.5, -0.42, -57.0)

        add(
            FujiPeak(
                app,
                pos=fuji_pos,
                scale=(17.8, 19.8, 1.0),
                color=self.season_color("fuji_peak_color", (0.42, 0.49, 0.60)),
            )
        )

        add(
            FujiSnowcap(
                app,
                pos=fuji_pos,
                scale=(17.8, 19.8, 1.0),
                color=self.season_color("fuji_snow_color", (0.96, 0.98, 1.00)),
            )
        )

    def add_contact_shadows(self, app, pond_radius_scale):
        add = self.add_object
        shadow_color = (0.018, 0.020, 0.018)
        specs = [
            ((0.0, 0.026, 0.0), (2.80, 0.92, 1.0), 0.24),
            ((2.7 * pond_radius_scale, 0.030, 3.9 * pond_radius_scale), (1.55, 0.36, 1.0), 0.18),
            ((-4.45 * pond_radius_scale, 0.030, -2.55 * pond_radius_scale), (0.72, 0.30, 1.0), 0.15),
        ]

        for angle_deg in range(20, 360, 40):
            angle = math.radians(angle_deg)
            specs.append(
                (
                    (math.cos(angle) * 11.8, 0.028, math.sin(angle) * 11.8),
                    (1.05, 0.42, 1.0),
                    0.13,
                )
            )

        for idx, (pos, scale, alpha) in enumerate(specs):
            add(
                ContactShadow(
                    app,
                    pos=pos,
                    rot=(90, idx * 17.0, 0),
                    scale=scale,
                    color=shadow_color,
                    alpha=alpha,
                )
            )

    def update(self):
        for obj in self.objects:
            obj.update()
