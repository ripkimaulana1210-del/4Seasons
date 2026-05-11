from copy import deepcopy

from .season_winter import SEASON as WINTER


SEASON = deepcopy(WINTER)
SEASON.update(
    {
        "id": "deep_winter",
        "name": "Deep Winter",
        "micro_season": "deep_winter",
        "temperature_range": (-10.0, -1.0),
        "background_color": (0.62, 0.70, 0.78),
        "sky_day_top": (0.50, 0.64, 0.80),
        "sky_day_horizon": (0.78, 0.88, 0.96),
        "sky_night_top": (0.006, 0.014, 0.050),
        "sky_night_horizon": (0.04, 0.08, 0.13),
        "cloud_density": 0.92,
        "aurora_intensity": 0.72,
        "light_color": (0.74, 0.84, 1.00),
        "light_intensity": 0.76,
        "ground_color": (0.96, 0.99, 1.00),
        "water_color": (0.72, 0.86, 0.94),
        "water_reflection_color": (0.88, 0.96, 1.00),
        "rain_enabled": False,
        "ambient_particle_count": 116,
        "wind_strength": 1.52,
        "fog_density_bonus": 0.165,
        "weather_label": "Deep snow + aurora night",
        "special_effect_label": "Snow accumulation tebal, frozen pond, onsen steam",
        "water_wave_strength": 0.05,
        "water_sparkle_strength": 0.80,
        "lantern_glow_boost": 1.62,
        "particle_speed_boost": 0.62,
        "post_temperature_grade": -0.160,
        "post_saturation": 0.86,
        "post_bloom_bonus": 0.055,
        "life_stage": "Hening terdalam",
        "emotion_title": "Diam yang bercahaya",
        "emotion_line": "Dunia membeku, tapi lampu kecil terasa lebih hangat.",
        "transition_phrase": "Frost menjadi salju penuh.",
        "transition_color": (0.72, 0.90, 1.00),
        "transition_secondary_color": (0.42, 0.86, 0.76),
    }
)
