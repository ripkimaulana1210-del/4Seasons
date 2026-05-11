from copy import deepcopy

from .season_summer import SEASON as SUMMER


SEASON = deepcopy(SUMMER)
SEASON.update(
    {
        "id": "late_summer",
        "name": "Late Summer / Dry Heat",
        "micro_season": "late_summer",
        "temperature_range": (26.0, 33.0),
        "sky_day_top": (0.34, 0.58, 0.86),
        "sky_day_horizon": (0.86, 0.82, 0.64),
        "cloud_color": (0.94, 0.86, 0.66),
        "cloud_density": 0.42,
        "light_color": (1.00, 0.86, 0.62),
        "ground_texture": "dry_grass",
        "garden_texture": "summer_grass",
        "yard_texture": "dry_grass",
        "ground_color": (0.38, 0.40, 0.16),
        "garden_lawn_color": (0.36, 0.43, 0.16),
        "water_color": (0.12, 0.32, 0.46),
        "water_wave_strength": 0.72,
        "water_sparkle_strength": 0.72,
        "rain_enabled": False,
        "ambient_particle_count": 30,
        "wind_strength": 0.62,
        "weather_label": "Panas kering + debu halus",
        "special_effect_label": "Rumput mulai kering, air kolam lebih tenang",
        "post_temperature_grade": 0.110,
        "post_saturation": 0.98,
        "life_stage": "Sisa panas",
        "emotion_title": "Lelah yang hangat",
        "emotion_line": "Hari masih terang, tapi musim mulai menepi.",
        "transition_phrase": "Pesta mereda menjadi kuning kering.",
        "transition_color": (0.86, 0.66, 0.20),
        "transition_secondary_color": (0.66, 0.46, 0.16),
    }
)
