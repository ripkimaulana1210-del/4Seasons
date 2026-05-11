from copy import deepcopy

from .season_spring import SEASON as SPRING


SEASON = deepcopy(SPRING)
SEASON.update(
    {
        "id": "early_spring",
        "name": "Early Spring / Thaw",
        "micro_season": "early_spring",
        "temperature_range": (6.0, 15.0),
        "background_color": (0.66, 0.76, 0.84),
        "sky_day_top": (0.48, 0.66, 0.88),
        "sky_day_horizon": (0.78, 0.88, 0.94),
        "cloud_color": (0.88, 0.93, 0.96),
        "cloud_density": 0.78,
        "light_color": (0.92, 0.96, 0.92),
        "light_intensity": 1.02,
        "ground_texture": "spring_grass",
        "garden_texture": "snow",
        "yard_texture": "spring_grass",
        "road_texture": "icy_road",
        "ground_color": (0.52, 0.64, 0.52),
        "water_color": (0.36, 0.58, 0.68),
        "water_reflection_color": (0.70, 0.86, 0.92),
        "island_mound_color": (0.54, 0.62, 0.48),
        "island_grass_color": (0.60, 0.72, 0.48),
        "sakura_canopy_deep_color": (0.72, 0.62, 0.66),
        "sakura_canopy_light_color": (0.92, 0.86, 0.88),
        "sakura_blossom_deep_color": (0.76, 0.60, 0.66),
        "sakura_blossom_light_color": (0.96, 0.90, 0.92),
        "floating_petals_enabled": False,
        "garden_flowers_enabled": False,
        "pond_flowers_enabled": False,
        "rain_enabled": True,
        "rain_count": 30,
        "ambient_particle_count": 40,
        "wind_strength": 0.82,
        "fog_density_bonus": 0.080,
        "weather_label": "Thaw mist + gerimis dingin",
        "special_effect_label": "Salju basah, puddle mencair, tunas awal",
        "water_wave_strength": 0.44,
        "water_sparkle_strength": 0.28,
        "post_temperature_grade": -0.035,
        "post_saturation": 0.98,
        "life_stage": "Awal tumbuh",
        "emotion_title": "Mencair pelan",
        "emotion_line": "Dingin masih tertinggal, tapi tanah mulai bernapas.",
        "transition_phrase": "Keheningan mulai retak.",
        "transition_color": (0.72, 0.88, 0.92),
        "transition_secondary_color": (0.54, 0.84, 0.48),
    }
)
