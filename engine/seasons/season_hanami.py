from copy import deepcopy

from .season_spring import SEASON as SPRING


SEASON = deepcopy(SPRING)
SEASON.update(
    {
        "id": "hanami",
        "name": "Hanami / Sakura Peak",
        "micro_season": "hanami",
        "temperature_range": (18.0, 24.0),
        "cloud_density": 0.52,
        "sky_day_top": (0.48, 0.70, 0.98),
        "sky_day_horizon": (0.88, 0.94, 1.00),
        "light_color": (1.00, 0.92, 0.94),
        "light_intensity": 1.24,
        "ground_texture": "flower_meadow",
        "garden_texture": "flower_meadow",
        "yard_texture": "petal_ground",
        "ground_color": (0.34, 0.48, 0.24),
        "water_reflection_color": (1.00, 0.50, 0.76),
        "sakura_canopy_deep_color": (0.98, 0.32, 0.62),
        "sakura_canopy_light_color": (1.00, 0.76, 0.94),
        "sakura_blossom_deep_color": (1.00, 0.40, 0.68),
        "sakura_blossom_light_color": (1.00, 0.84, 0.96),
        "floating_petal_color": (1.00, 0.60, 0.86),
        "rain_enabled": False,
        "ambient_particle_count": 86,
        "wind_strength": 0.52,
        "fog_density_bonus": 0.010,
        "weather_label": "Cerah lembut + petal rain",
        "special_effect_label": "Sakura full bloom, piknik, kelopak padat",
        "water_sparkle_strength": 0.58,
        "post_saturation": 1.14,
        "post_bloom_bonus": 0.038,
        "life_stage": "Puncak mekar",
        "emotion_title": "Merayakan yang sementara",
        "emotion_line": "Semua indah justru karena tidak lama.",
        "transition_phrase": "Tunas menjadi perayaan.",
        "transition_color": (1.00, 0.58, 0.86),
        "transition_secondary_color": (1.00, 0.86, 0.94),
    }
)
