from copy import deepcopy

from .season_autumn import SEASON as AUTUMN


SEASON = deepcopy(AUTUMN)
SEASON.update(
    {
        "id": "first_frost",
        "name": "Late Autumn / First Frost",
        "micro_season": "first_frost",
        "temperature_range": (1.0, 9.0),
        "background_color": (0.62, 0.66, 0.70),
        "sky_day_top": (0.48, 0.58, 0.70),
        "sky_day_horizon": (0.76, 0.78, 0.74),
        "cloud_color": (0.80, 0.84, 0.86),
        "cloud_density": 0.84,
        "light_color": (0.84, 0.88, 0.90),
        "light_intensity": 0.88,
        "ground_texture": "autumn_grass",
        "garden_texture": "leaf_litter",
        "yard_texture": "autumn_grass",
        "road_texture": "icy_road",
        "ground_color": (0.46, 0.42, 0.30),
        "water_color": (0.34, 0.48, 0.54),
        "water_reflection_color": (0.74, 0.82, 0.84),
        "floating_petal_color": (0.80, 0.76, 0.68),
        "winter_snow_color": (0.88, 0.94, 0.98),
        "winter_snow_shadow_color": (0.70, 0.78, 0.82),
        "rain_enabled": True,
        "rain_count": 42,
        "rain_speed": 0.28,
        "ambient_particle_count": 44,
        "autumn_leaf_density": 150,
        "wind_strength": 1.08,
        "fog_density_bonus": 0.125,
        "weather_label": "First frost + hujan dingin",
        "special_effect_label": "Daun sisa, frost tipis di batu dan jalan",
        "water_wave_strength": 0.42,
        "water_sparkle_strength": 0.32,
        "post_temperature_grade": -0.060,
        "post_saturation": 0.84,
        "life_stage": "Embun beku pertama",
        "emotion_title": "Menahan dingin pertama",
        "emotion_line": "Yang tersisa mulai memucat di pagi yang tajam.",
        "transition_phrase": "Gugur berubah menjadi beku.",
        "transition_color": (0.72, 0.82, 0.84),
        "transition_secondary_color": (0.50, 0.36, 0.18),
    }
)
