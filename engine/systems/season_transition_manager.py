import math
from copy import deepcopy

from ..data.scene_config import TRANSITION_PRESETS


COLOR_KEYS = {
    "background_color",
    "sky_day_top",
    "sky_day_horizon",
    "sky_dusk_top",
    "sky_dusk_horizon",
    "sky_night_top",
    "sky_night_horizon",
    "cloud_color",
    "moon_light_color",
    "star_color",
    "night_fog_color",
    "light_color",
    "ground_color",
    "water_color",
    "water_reflection_color",
    "island_mound_color",
    "island_grass_color",
    "sakura_wood_color",
    "sakura_canopy_deep_color",
    "sakura_canopy_light_color",
    "sakura_blossom_deep_color",
    "sakura_blossom_light_color",
    "floating_petal_color",
    "fuji_peak_color",
    "fuji_snow_color",
    "road_color",
    "lane_color",
    "road_edge_color",
    "garden_path_color",
    "garden_lawn_color",
    "garden_rich_lawn_color",
    "garden_hedge_color",
    "garden_bed_color",
    "yard_color",
    "bush_color",
    "winter_snow_color",
    "winter_snow_shadow_color",
    "temperature_bar_color",
    "sun_color",
    "sun_ray_color",
    "wind_color",
    "rain_color",
    "rain_puddle_color",
    "water_accent_color",
    "transition_color",
    "transition_secondary_color",
}

NUMERIC_BLEND_KEYS = {
    "cloud_density",
    "fog_density_bonus",
    "aurora_intensity",
    "light_intensity",
    "sun_scale",
    "wind_strength",
    "rain_count",
    "rain_speed",
    "ambient_particle_count",
    "ambience_volume",
    "post_temperature_grade",
    "post_saturation",
    "post_bloom_bonus",
    "sky_detail_strength",
    "water_wave_strength",
    "water_sparkle_strength",
    "water_season_mix",
    "lantern_glow_boost",
    "particle_speed_boost",
    "wind_motion_boost",
}

TEXTURE_KEYS = {
    "ground_texture",
    "garden_texture",
    "yard_texture",
    "road_texture",
}

BOOLEAN_THRESHOLDS = {
    "winter->early_spring": {
        "garden_flowers_enabled": 0.70,
        "pond_flowers_enabled": 0.82,
        "floating_petals_enabled": 0.90,
        "rain_enabled": 0.58,
    },
    "early_spring->spring": {
        "garden_flowers_enabled": 0.28,
        "pond_flowers_enabled": 0.38,
        "floating_petals_enabled": 0.62,
        "rain_enabled": 0.48,
    },
    "winter->spring": {
        "garden_flowers_enabled": 0.35,
        "pond_flowers_enabled": 0.42,
        "floating_petals_enabled": 0.55,
        "rain_enabled": 0.50,
    },
    "spring->hanami": {
        "garden_flowers_enabled": 0.12,
        "pond_flowers_enabled": 0.18,
        "floating_petals_enabled": 0.42,
        "rain_enabled": 0.74,
    },
    "hanami->tsuyu": {
        "garden_flowers_enabled": 0.62,
        "pond_flowers_enabled": 0.62,
        "floating_petals_enabled": 0.52,
        "rain_enabled": 0.44,
    },
    "tsuyu->summer": {
        "rain_enabled": 0.42,
        "floating_petals_enabled": 0.34,
    },
    "spring->summer": {
        "rain_enabled": 0.40,
        "floating_petals_enabled": 0.62,
    },
    "late_summer->autumn": {
        "rain_enabled": 0.62,
        "floating_petals_enabled": 0.36,
    },
    "summer->autumn": {
        "rain_enabled": 0.60,
        "floating_petals_enabled": 0.35,
    },
    "momiji->first_frost": {
        "garden_flowers_enabled": 0.58,
        "pond_flowers_enabled": 0.52,
        "floating_petals_enabled": 0.44,
        "rain_enabled": 0.46,
    },
    "first_frost->winter": {
        "garden_flowers_enabled": 0.54,
        "pond_flowers_enabled": 0.48,
        "floating_petals_enabled": 0.40,
        "rain_enabled": 0.50,
    },
    "winter->deep_winter": {
        "garden_flowers_enabled": 0.35,
        "pond_flowers_enabled": 0.35,
        "floating_petals_enabled": 0.35,
        "rain_enabled": 0.60,
    },
    "first_frost->deep_winter": {
        "garden_flowers_enabled": 0.42,
        "pond_flowers_enabled": 0.38,
        "floating_petals_enabled": 0.34,
        "rain_enabled": 0.54,
    },
    "autumn->winter": {
        "garden_flowers_enabled": 0.66,
        "pond_flowers_enabled": 0.58,
        "floating_petals_enabled": 0.52,
        "rain_enabled": 0.45,
    },
}

TRANSITION_STORIES = {
    "winter->early_spring": "Salju basah menipis, puddle muncul, dan tunas pertama keluar.",
    "early_spring->spring": "Tanah dingin berubah hijau dan taman mulai kembali hidup.",
    "spring->hanami": "Sakura mencapai full bloom, petal rain semakin padat.",
    "hanami->tsuyu": "Kelopak turun ke tanah, awan hujan menutup langit.",
    "tsuyu->summer": "Hujan mereda, udara menghangat, dan kolam mulai berkilau.",
    "spring->summer": "Petal rain mereda, udara memanas, dan kolam mulai berkilau.",
    "summer->midsummer": "Panas memuncak, festival lantern dan fireflies menyala.",
    "midsummer->late_summer": "Festival mereda, rumput mulai kering dan udara berdebu.",
    "late_summer->autumn": "Warna hijau memudar menuju kuning-oranye awal gugur.",
    "summer->autumn": "Daun menguning, angin berputar, lalu taman tertutup leaf litter.",
    "autumn->momiji": "Daun merah-oranye mencapai puncak dan menutup jalur taman.",
    "momiji->first_frost": "Warna hangat memucat saat frost pertama menyentuh jalan.",
    "first_frost->winter": "Frost pertama menebal menjadi snow cover yang lebih stabil.",
    "winter->deep_winter": "Winter menjadi lebih sunyi, tebal, dan bercahaya aurora.",
    "first_frost->deep_winter": "Frost berubah menjadi salju tebal dan malam aurora.",
    "autumn->winter": "First snow turun pelan, daun membeku, dan kolam mulai diam.",
    "deep_winter->early_spring": "Es terdalam mulai retak dan air pertama kembali bergerak.",
    "winter->spring": "Es retak dan mencair, tunas tumbuh, lalu sakura kembali bermekaran.",
}

DEFAULT_TRANSITION_PRESET = {
    "duration": 8.0,
    "camera_route": ("sakura", "bridge", "village"),
    "timeline": (("Blend", 0.0, 1.0),),
    "audio_cue": "blend",
}

EFFECT_INDEX = {
    "spring": 0.0,
    "summer": 1.0,
    "autumn": 2.0,
    "winter": 3.0,
}

TRANSITION_EFFECT_FAMILIES = {
    "winter->early_spring": "winter->spring",
    "early_spring->spring": "winter->spring",
    "deep_winter->early_spring": "winter->spring",
    "tsuyu->summer": "spring->summer",
    "late_summer->autumn": "summer->autumn",
    "momiji->first_frost": "autumn->winter",
    "first_frost->winter": "autumn->winter",
    "winter->deep_winter": "autumn->winter",
    "first_frost->deep_winter": "autumn->winter",
}


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def smoothstep(t):
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)


def transition_effect_family(pair):
    return TRANSITION_EFFECT_FAMILIES.get(pair, pair)


def ease_in_out(t):
    return 0.5 - 0.5 * math.cos(clamp(t) * math.pi)


def window_smooth(progress, start, end):
    if end <= start:
        return 1.0 if progress >= end else 0.0
    return smoothstep((progress - start) / (end - start))


def window_peak(progress, start, peak, end):
    if progress <= peak:
        return window_smooth(progress, start, peak)
    return 1.0 - window_smooth(progress, peak, end)


def lerp_float(a, b, t):
    return float(a) * (1.0 - t) + float(b) * t


def lerp_color(a, b, t):
    return tuple(lerp_float(a[i], b[i], t) for i in range(3))


def season_mid_temperature(season):
    low, high = season["temperature_range"]
    return (low + high) * 0.5


def is_color(value):
    return (
        isinstance(value, tuple)
        and len(value) == 3
        and all(isinstance(channel, (int, float)) for channel in value)
    )


def boolean_transition_value(key, from_value, to_value, progress, pair):
    if from_value == to_value:
        return bool(from_value)

    threshold = BOOLEAN_THRESHOLDS.get(pair, {}).get(key, 0.50)
    if bool(to_value):
        return progress >= threshold
    return progress < threshold


def blend_season_config(from_config, to_config, t, progress=None):
    progress = t if progress is None else progress
    pair = f"{from_config.get('id')}->{to_config.get('id')}"
    blended = deepcopy(from_config)

    for key in set(from_config) | set(to_config):
        if key not in from_config:
            blended[key] = to_config[key]
            continue
        if key not in to_config:
            blended[key] = from_config[key]
            continue

        from_value = from_config[key]
        to_value = to_config[key]

        if isinstance(from_value, bool) and isinstance(to_value, bool):
            blended[key] = boolean_transition_value(key, from_value, to_value, progress, pair)
        elif key in TEXTURE_KEYS:
            blended[key] = to_value if progress >= 0.62 else from_value
        elif key in COLOR_KEYS and is_color(from_value) and is_color(to_value):
            blended[key] = lerp_color(from_value, to_value, t)
        elif key in NUMERIC_BLEND_KEYS and isinstance(from_value, (int, float)) and isinstance(to_value, (int, float)):
            blended[key] = lerp_float(from_value, to_value, t)
        elif key == "temperature_range":
            blended[key] = (
                lerp_float(from_value[0], to_value[0], t),
                lerp_float(from_value[1], to_value[1], t),
            )
        else:
            blended[key] = to_value if progress >= 0.72 else from_value

    blended["transition_pair"] = pair
    blended["transition_progress"] = progress
    blended["transition_eased"] = t
    return blended


class SeasonTransitionManager:
    """Keeps one cinematic season handoff active and exposes reusable blend data.

    Scene objects still own their actual OpenGL draw calls. This manager owns
    timing, easing, blended season config, and named effect intensities so the
    renderer/controller do not need pair-specific progress math scattered around.
    """

    def __init__(self, default_duration=8.0):
        self.default_duration = default_duration
        self.duration = default_duration
        self.elapsed = 0.0
        self.from_season = None
        self.to_season = None

    @property
    def is_active(self):
        return self.from_season is not None and self.to_season is not None

    @property
    def progress(self):
        if not self.is_active:
            return 1.0
        return clamp(self.elapsed / max(0.001, self.duration))

    @property
    def eased(self):
        return ease_in_out(self.progress)

    @property
    def pair(self):
        if not self.is_active:
            return ""
        return f"{self.from_season['id']}->{self.to_season['id']}"

    def preset_for_pair(self, pair=None):
        return TRANSITION_PRESETS.get(pair or self.pair, DEFAULT_TRANSITION_PRESET)

    def reset(self):
        self.elapsed = 0.0
        self.from_season = None
        self.to_season = None

    def start_transition(self, from_season, to_season, duration=None):
        self.from_season = from_season
        self.to_season = to_season
        preset_duration = self.preset_for_pair(f"{from_season['id']}->{to_season['id']}").get("duration", self.default_duration)
        self.duration = max(0.25, float(duration or preset_duration))
        self.elapsed = 0.0

    def update(self, delta_time):
        if not self.is_active:
            return False

        self.elapsed += max(0.0, float(delta_time))
        if self.elapsed < self.duration:
            return False

        self.reset()
        return True

    def get_blended_season(self, fallback_season):
        if not self.is_active:
            return fallback_season
        return blend_season_config(self.from_season, self.to_season, self.eased, self.progress)

    def effect_index(self, fallback_season):
        if not self.is_active:
            return EFFECT_INDEX.get(fallback_season.get("seasonal_effect", "spring"), 0.0)

        start = EFFECT_INDEX.get(self.from_season.get("seasonal_effect", "spring"), 0.0)
        end = EFFECT_INDEX.get(self.to_season.get("seasonal_effect", "spring"), start)
        return lerp_float(start, end, self.eased)

    def visibility(self, effect_name, fallback_season):
        if not self.is_active:
            return 1.0 if fallback_season.get("seasonal_effect") == effect_name else 0.0

        from_match = self.from_season.get("seasonal_effect") == effect_name
        to_match = self.to_season.get("seasonal_effect") == effect_name
        if from_match and to_match:
            return 1.0
        if from_match:
            return 1.0 - self.eased
        if to_match:
            return self.eased
        return 0.0

    def snapshot(self):
        if not self.is_active:
            return None

        progress = self.progress
        eased = self.eased
        pair = self.pair
        family = transition_effect_family(pair)
        return {
            "from": self.from_season,
            "to": self.to_season,
            "pair": pair,
            "progress": progress,
            "eased": eased,
            "blended": self.get_blended_season(self.to_season),
            "preset": self.preset_for_pair(pair),
            "timeline": self.timeline_items(progress, pair),
            "heat_intensity": window_smooth(progress, 0.16, 0.86) if family == "spring->summer" else 0.0,
            "sparkle_intensity": window_smooth(progress, 0.36, 0.95) if family == "spring->summer" else 0.0,
            "firefly_intensity": window_smooth(progress, 0.55, 1.0) if family == "spring->summer" else 0.0,
            "petal_fade": 1.0 - window_smooth(progress, 0.10, 0.70) if family == "spring->summer" else 0.0,
            "wilt_intensity": window_smooth(progress, 0.14, 0.78) if family == "summer->autumn" else 0.0,
            "leaf_color_intensity": window_smooth(progress, 0.16, 0.72) if family == "summer->autumn" else 0.0,
            "leaf_fall_intensity": window_smooth(progress, 0.22, 0.92) if family == "summer->autumn" else 0.0,
            "wind_intensity": window_smooth(progress, 0.20, 0.88) if family == "summer->autumn" else 0.0,
            "cold_rain_intensity": window_smooth(progress, 0.60, 1.0) if family == "summer->autumn" else 0.0,
            "frost_intensity": window_smooth(progress, 0.24, 0.88) if family == "autumn->winter" else 0.0,
            "freeze_intensity": window_smooth(progress, 0.38, 0.96) if family == "autumn->winter" else 0.0,
            "snow_intensity": window_smooth(progress, 0.45, 1.0) if family == "autumn->winter" else 0.0,
            "first_snow_intensity": window_peak(progress, 0.42, 0.68, 1.0) if family == "autumn->winter" else 0.0,
            "melt_intensity": window_smooth(progress, 0.02, 0.64) if family == "winter->spring" else 0.0,
            "ice_crack_intensity": window_peak(progress, 0.12, 0.28, 0.52) if family == "winter->spring" else 0.0,
            "puddle_intensity": window_smooth(progress, 0.12, 0.72) if family == "winter->spring" else 0.0,
            "sprout_intensity": window_smooth(progress, 0.30, 0.80) if family == "winter->spring" else 0.0,
            "bloom_intensity": window_smooth(progress, 0.46, 0.94) if family == "winter->spring" else 0.0,
            "petal_intensity": window_smooth(progress, 0.55, 1.0) if family == "winter->spring" else 0.0,
            "story": TRANSITION_STORIES.get(pair, self.to_season.get("transition_phrase", "")),
        }

    def timeline_items(self, progress=None, pair=None):
        progress = self.progress if progress is None else progress
        preset = self.preset_for_pair(pair)
        items = []
        for label, start, end in preset.get("timeline", DEFAULT_TRANSITION_PRESET["timeline"]):
            items.append(
                {
                    "label": label,
                    "start": start,
                    "end": end,
                    "progress": window_smooth(progress, start, end),
                    "active": start <= progress <= end,
                    "done": progress > end,
                }
            )
        return items

    def render_transition_effects(self, app):
        # Hook for the main loop. The current renderer materializes transition
        # visuals as scene objects, so this intentionally stays lightweight.
        return self.snapshot()
