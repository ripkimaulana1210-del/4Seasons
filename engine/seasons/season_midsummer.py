from copy import deepcopy

from .season_summer import SEASON as SUMMER


SEASON = deepcopy(SUMMER)
SEASON.update(
    {
        "id": "midsummer",
        "name": "Midsummer Festival",
        "micro_season": "midsummer",
        "temperature_range": (30.0, 37.0),
        "sky_day_top": (0.24, 0.60, 1.00),
        "sky_day_horizon": (0.74, 0.90, 1.00),
        "cloud_density": 0.24,
        "light_intensity": 1.42,
        "sun_scale": 1.46,
        "ground_color": (0.24, 0.40, 0.14),
        "water_reflection_color": (1.00, 0.78, 0.28),
        "rain_enabled": False,
        "ambient_particle_count": 58,
        "wind_strength": 0.34,
        "fog_density_bonus": -0.035,
        "weather_label": "Festival panas + langit jernih",
        "special_effect_label": "Yatai aktif, lantern, fireflies, fireworks",
        "water_sparkle_strength": 1.34,
        "lantern_glow_boost": 1.38,
        "post_temperature_grade": 0.135,
        "post_saturation": 1.18,
        "post_bloom_bonus": 0.052,
        "life_stage": "Pesta tengah musim",
        "emotion_title": "Riuh dan bersinar",
        "emotion_line": "Malam terasa dekat, lampu-lampu terasa hidup.",
        "transition_phrase": "Panas menjadi perayaan.",
        "transition_color": (1.00, 0.62, 0.18),
        "transition_secondary_color": (1.00, 0.92, 0.34),
    }
)
