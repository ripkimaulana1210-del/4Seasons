from copy import deepcopy

from .season_autumn import SEASON as AUTUMN


SEASON = deepcopy(AUTUMN)
SEASON.update(
    {
        "id": "momiji",
        "name": "Momiji / Maple Peak",
        "micro_season": "momiji",
        "temperature_range": (10.0, 18.0),
        "cloud_density": 0.62,
        "light_color": (1.00, 0.74, 0.42),
        "light_intensity": 1.18,
        "ground_texture": "leaf_litter",
        "garden_texture": "leaf_litter",
        "yard_texture": "leaf_litter",
        "ground_color": (0.48, 0.28, 0.10),
        "water_reflection_color": (1.00, 0.42, 0.16),
        "sakura_canopy_deep_color": (0.90, 0.20, 0.08),
        "sakura_canopy_light_color": (1.00, 0.52, 0.16),
        "floating_petal_color": (0.98, 0.28, 0.08),
        "rain_enabled": False,
        "ambient_particle_count": 94,
        "autumn_leaf_density": 430,
        "wind_strength": 1.02,
        "weather_label": "Momiji peak + golden sunlight",
        "special_effect_label": "Maple tunnel, leaf carpet merah-oranye",
        "post_saturation": 1.16,
        "post_bloom_bonus": 0.020,
        "life_stage": "Puncak gugur",
        "emotion_title": "Terang sebelum dingin",
        "emotion_line": "Warna paling kuat muncul sebelum semuanya turun.",
        "transition_phrase": "Kuning menjadi merah menyala.",
        "transition_color": (1.00, 0.32, 0.08),
        "transition_secondary_color": (0.92, 0.62, 0.12),
    }
)
