from copy import deepcopy

from .season_spring import SEASON as SPRING


SEASON = deepcopy(SPRING)
SEASON.update(
    {
        "id": "tsuyu",
        "name": "Tsuyu / Rainy Season",
        "micro_season": "tsuyu",
        "temperature_range": (20.0, 27.0),
        "background_color": (0.55, 0.66, 0.76),
        "sky_day_top": (0.38, 0.52, 0.68),
        "sky_day_horizon": (0.68, 0.78, 0.84),
        "cloud_color": (0.70, 0.76, 0.82),
        "cloud_density": 0.96,
        "light_color": (0.76, 0.84, 0.88),
        "light_intensity": 0.86,
        "ground_texture": "spring_grass",
        "garden_texture": "flower_meadow",
        "yard_texture": "petal_ground",
        "road_texture": "road",
        "ground_color": (0.24, 0.38, 0.24),
        "water_color": (0.14, 0.34, 0.46),
        "water_reflection_color": (0.56, 0.70, 0.82),
        "floating_petals_enabled": False,
        "rain_enabled": True,
        "rain_count": 92,
        "rain_speed": 0.42,
        "rain_puddle_color": (0.12, 0.30, 0.42),
        "ambient_particle_count": 52,
        "wind_strength": 0.74,
        "fog_density_bonus": 0.135,
        "weather_label": "Tsuyu rain + puddle reflektif",
        "special_effect_label": "Hydrangea biru, jalan basah, kabut rendah",
        "water_wave_strength": 1.05,
        "water_sparkle_strength": 0.20,
        "post_temperature_grade": -0.010,
        "post_saturation": 0.96,
        "life_stage": "Menyuburkan",
        "emotion_title": "Tenang dalam hujan",
        "emotion_line": "Tidak semua redup berarti berhenti tumbuh.",
        "transition_phrase": "Mekar berubah menjadi hujan.",
        "transition_color": (0.46, 0.68, 0.88),
        "transition_secondary_color": (0.56, 0.48, 0.86),
    }
)
