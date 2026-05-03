import math
import pygame as pg

from .seasons.season_autumn import SEASON as AUTUMN
from .seasons.season_spring import SEASON as SPRING
from .seasons.season_summer import SEASON as SUMMER
from .seasons.season_winter import SEASON as WINTER


SEASONS = [SPRING, SUMMER, AUTUMN, WINTER]


TRANSITION_STORIES = {
    "spring->summer": "Gelombang panas: udara naik cepat, cahaya makin terik.",
    "summer->autumn": "Daun mulai layu, menguning, lalu berguguran.",
    "autumn->winter": "Udara membeku, salju pertama turun sedikit demi sedikit.",
    "winter->spring": "Es dan salju mencair, lalu taman kembali bermekaran.",
}

SKY_DEFAULTS = {
    "sky_day_top": (0.38, 0.66, 0.96),
    "sky_day_horizon": (0.74, 0.88, 1.00),
    "sky_dusk_top": (0.36, 0.28, 0.58),
    "sky_dusk_horizon": (1.00, 0.52, 0.24),
    "sky_night_top": (0.015, 0.026, 0.075),
    "sky_night_horizon": (0.070, 0.095, 0.160),
    "moon_light_color": (0.58, 0.68, 0.92),
    "cloud_color": (0.94, 0.96, 0.98),
    "cloud_density": 0.56,
    "star_color": (0.96, 0.94, 0.86),
    "night_fog_color": (0.08, 0.11, 0.17),
    "fog_density_bonus": 0.0,
}


def clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def lerp(a, b, amount):
    return a * (1.0 - amount) + b * amount


def inverse_lerp(a, b, value):
    if abs(b - a) < 1e-6:
        return 0.0
    return clamp((value - a) / (b - a))


def blend_color(a, b, amount):
    return tuple(lerp(a[i], b[i], amount) for i in range(3))


def season_mid_temperature(season):
    low, high = season["temperature_range"]
    return (low + high) * 0.5


class SeasonController:
    def __init__(self, app):
        self.app = app
        self.current_index = 0
        self.elapsed = 0.0
        self.season_duration = 8.0
        self.time_lapse_enabled = False
        self.day_time = 0.34
        self.day_duration = 72.0
        self.day_cycle_enabled = True
        self.transition_duration = 4.5
        self.transition_elapsed = 0.0
        self.transition_from = None
        self.transition_to = None
        self.temperature_c = self.calculate_temperature()
        self.caption_timer = 0.0
        self._atmosphere_cache_key = None
        self._atmosphere_cache = None

    @property
    def current(self):
        return SEASONS[self.current_index]

    @property
    def is_transitioning(self):
        return self.transition_from is not None and self.transition_to is not None

    @property
    def transition_progress(self):
        if not self.is_transitioning:
            return 1.0
        return max(0.0, min(1.0, self.transition_elapsed / self.transition_duration))

    def transition_snapshot(self):
        if not self.is_transitioning:
            return None
        progress = self.transition_progress
        eased = 0.5 - 0.5 * math.cos(progress * math.pi)
        pair = f"{self.transition_from['id']}->{self.transition_to['id']}"
        return {
            "from": self.transition_from,
            "to": self.transition_to,
            "pair": pair,
            "progress": progress,
            "eased": eased,
            "heat_intensity": smoothstep(progress) if pair == "spring->summer" else 0.0,
            "wilt_intensity": smoothstep(progress) if pair == "summer->autumn" else 0.0,
            "leaf_fall_intensity": smoothstep(progress) if pair == "summer->autumn" else 0.0,
            "snow_intensity": smoothstep(progress) if pair == "autumn->winter" else 0.0,
            "melt_intensity": smoothstep(progress) if pair == "winter->spring" else 0.0,
            "bloom_intensity": smoothstep(progress) if pair == "winter->spring" else 0.0,
            "story": TRANSITION_STORIES.get(pair, self.transition_to.get("transition_phrase", "")),
        }

    def calculate_temperature(self):
        if self.is_transitioning:
            progress = self.transition_progress
            eased = 0.5 - 0.5 * math.cos(progress * math.pi)
            from_temp = season_mid_temperature(self.transition_from)
            to_temp = season_mid_temperature(self.transition_to)
            pair = f"{self.transition_from['id']}->{self.transition_to['id']}"

            if pair == "spring->summer":
                heat_peak = 38.0
                if progress < 0.72:
                    return lerp(from_temp, heat_peak, smoothstep(progress / 0.72))
                return lerp(heat_peak, to_temp, smoothstep((progress - 0.72) / 0.28))

            if pair == "summer->autumn":
                return lerp(from_temp, to_temp, eased)

            if pair == "autumn->winter":
                cold_snap = -3.0
                return lerp(from_temp, cold_snap, smoothstep(progress))

            if pair == "winter->spring":
                thaw = lerp(from_temp, 8.0, smoothstep(min(progress / 0.45, 1.0)))
                return lerp(thaw, to_temp, smoothstep(max((progress - 0.35) / 0.65, 0.0)))

        low, high = self.current["temperature_range"]
        if self.time_lapse_enabled:
            progress = (self.elapsed / self.season_duration) % 1.0
            wave = 0.5 + 0.5 * math.sin(progress * math.tau - math.pi * 0.5)
            return low + (high - low) * wave
        return (low + high) * 0.5

    def season_setting(self, season, key):
        return season.get(key, SKY_DEFAULTS[key])

    def blended_season_setting(self, key):
        transition = self.transition_snapshot()
        if transition is None:
            return self.season_setting(self.current, key)

        start = self.season_setting(transition["from"], key)
        end = self.season_setting(transition["to"], key)
        amount = transition["eased"]
        if isinstance(start, tuple):
            return blend_color(start, end, amount)
        return lerp(start, end, amount)

    def seasonal_effect_visibility(self, effect_name):
        transition = self.transition_snapshot()
        if transition is None:
            return 1.0 if self.current.get("seasonal_effect") == effect_name else 0.0

        from_match = transition["from"].get("seasonal_effect") == effect_name
        to_match = transition["to"].get("seasonal_effect") == effect_name
        if from_match and to_match:
            return 1.0
        if from_match:
            return 1.0 - transition["eased"]
        if to_match:
            return transition["eased"]
        return 0.0

    def day_state(self):
        phase = self.day_time % 1.0
        sun_angle = phase * math.tau
        sun_height = math.sin(sun_angle - math.pi * 0.5)
        daylight = smoothstep(inverse_lerp(-0.18, 0.34, sun_height))
        night = 1.0 - smoothstep(inverse_lerp(-0.12, 0.20, sun_height))
        horizon_glow = smoothstep(1.0 - min(1.0, abs(sun_height) / 0.42))
        horizon_glow *= 0.25 + 0.75 * (1.0 - night * 0.35)
        return {
            "phase": phase,
            "sun_angle": sun_angle,
            "sun_height": sun_height,
            "daylight": daylight,
            "night": night,
            "dusk": horizon_glow,
        }

    def atmosphere_state(self):
        transition_key = None
        if self.is_transitioning:
            transition_key = (
                self.transition_from["id"],
                self.transition_to["id"],
                self.transition_elapsed,
            )

        cache_key = (
            self.current_index,
            self.day_time,
            transition_key,
        )
        if cache_key == self._atmosphere_cache_key:
            return self._atmosphere_cache

        self._atmosphere_cache = self._calculate_atmosphere_state()
        self._atmosphere_cache_key = cache_key
        return self._atmosphere_cache

    def _calculate_atmosphere_state(self):
        day = self.day_state()
        night = day["night"]
        dusk = day["dusk"]
        daylight = day["daylight"]

        day_top = self.blended_season_setting("sky_day_top")
        day_horizon = self.blended_season_setting("sky_day_horizon")
        dusk_top = self.blended_season_setting("sky_dusk_top")
        dusk_horizon = self.blended_season_setting("sky_dusk_horizon")
        night_top = self.blended_season_setting("sky_night_top")
        night_horizon = self.blended_season_setting("sky_night_horizon")
        cloud_color = self.blended_season_setting("cloud_color")
        cloud_density = self.blended_season_setting("cloud_density")
        fog_bonus = self.blended_season_setting("fog_density_bonus")
        summer_clarity = self.seasonal_effect_visibility("summer") * (1.0 - cloud_density * 0.20)
        winter = self.seasonal_effect_visibility("winter")
        autumn = self.seasonal_effect_visibility("autumn")

        top = blend_color(day_top, dusk_top, dusk)
        horizon = blend_color(day_horizon, dusk_horizon, dusk)
        top = blend_color(top, night_top, night)
        horizon = blend_color(horizon, night_horizon, night)
        mid = blend_color(horizon, top, 0.56)

        phase = day["phase"]
        sun_theta = phase * math.tau - math.pi * 0.5
        moon_theta = sun_theta + math.pi
        sun_radius = 34.0
        moon_radius = 36.0
        sun_position = (
            math.cos(sun_theta) * sun_radius,
            6.0 + max(-0.35, math.sin(sun_theta)) * 20.0,
            -20.0,
        )
        moon_position = (
            math.cos(moon_theta) * moon_radius,
            7.5 + max(-0.25, math.sin(moon_theta)) * 18.0,
            -24.0,
        )

        base_light_color = self.current["light_color"]
        if self.is_transitioning:
            base_light_color = blend_color(
                self.transition_from["light_color"],
                self.transition_to["light_color"],
                self.transition_snapshot()["eased"],
            )
        moon_light = self.blended_season_setting("moon_light_color")
        light_color = blend_color(base_light_color, moon_light, night * 0.72)

        base_intensity = self.current["light_intensity"]
        if self.is_transitioning:
            base_intensity = lerp(
                self.transition_from["light_intensity"],
                self.transition_to["light_intensity"],
                self.transition_snapshot()["eased"],
            )
        light_intensity = max(0.30, base_intensity * (0.36 + daylight * 0.82) + dusk * 0.12)
        fog_density = max(
            0.015,
            0.08 + cloud_density * 0.10 + night * 0.08 + winter * 0.17 + autumn * 0.08 + fog_bonus,
        )
        fog_start = lerp(22.0, 12.0, min(1.0, winter + night * 0.45))
        fog_end = lerp(64.0, 42.0, min(1.0, winter + cloud_density * 0.35))
        fog_color = blend_color(
            blend_color(horizon, self.blended_season_setting("night_fog_color"), night * 0.55),
            self.current.get("winter_snow_shadow_color", (0.78, 0.86, 0.92)),
            winter * 0.35,
        )

        return {
            **day,
            "top_color": top,
            "mid_color": mid,
            "horizon_color": horizon,
            "background_color": blend_color(horizon, top, 0.42),
            "light_position": sun_position if daylight > 0.12 else moon_position,
            "light_color": light_color,
            "light_intensity": light_intensity,
            "sun_position": sun_position,
            "sun_alpha": smoothstep(inverse_lerp(-0.08, 0.24, day["sun_height"])),
            "sun_color": blend_color(self.current.get("sun_color", (1.0, 0.78, 0.22)), dusk_horizon, dusk * 0.45),
            "sun_ray_color": blend_color(self.current.get("sun_ray_color", (1.0, 0.70, 0.18)), dusk_horizon, dusk * 0.52),
            "moon_position": moon_position,
            "moon_alpha": smoothstep(night),
            "moon_color": self.blended_season_setting("moon_light_color"),
            "star_color": self.blended_season_setting("star_color"),
            "star_intensity": max(0.0, (night - cloud_density * (0.12 - summer_clarity * 0.04)) * (1.55 + summer_clarity * 0.80)),
            "summer_sky_clarity": summer_clarity,
            "cloud_color": blend_color(cloud_color, self.blended_season_setting("night_fog_color"), night * 0.48),
            "cloud_density": cloud_density,
            "cloud_alpha": cloud_density * (0.28 + daylight * 0.48 + night * 0.22),
            "night_fog_color": self.blended_season_setting("night_fog_color"),
            "aurora_alpha": night * self.current.get("aurora_intensity", 0.0),
            "fog_color": fog_color,
            "fog_density": fog_density,
            "fog_start": fog_start,
            "fog_end": fog_end,
        }

    def apply_atmosphere(self):
        if not hasattr(self.app, "light"):
            return
        from .point_light import PointLight

        atmosphere = self.atmosphere_state()
        self.app.background_color = atmosphere["background_color"]
        self.app.light = PointLight(
            position=atmosphere["light_position"],
            color=atmosphere["light_color"],
            intensity=atmosphere["light_intensity"],
        )

    def update_day_cycle(self, delta_s):
        if self.day_cycle_enabled:
            self.day_time = (self.day_time + delta_s / self.day_duration) % 1.0

    def set_season(self, index):
        index %= len(SEASONS)
        if index == self.current_index:
            self.elapsed = 0.0
            self.temperature_c = self.calculate_temperature()
            self.app.audio.apply_season(self.current)
            self.update_caption(force=True)
            return

        previous = self.current
        self.current_index = index
        self.transition_from = previous
        self.transition_to = self.current
        self.transition_elapsed = 0.0
        self.elapsed = 0.0
        self.temperature_c = self.calculate_temperature()
        self.app.apply_season()
        self.update_caption(force=True)

    def next_season(self):
        self.set_season(self.current_index + 1)

    def previous_season(self):
        self.set_season(self.current_index - 1)

    def toggle_time_lapse(self):
        self.time_lapse_enabled = not self.time_lapse_enabled
        self.temperature_c = self.calculate_temperature()
        self.update_caption(force=True)

    def toggle_day_cycle(self):
        self.day_cycle_enabled = not self.day_cycle_enabled
        self.apply_atmosphere()
        self.update_caption(force=True)

    def set_day_time(self, day_time):
        self.day_time = day_time % 1.0
        self.apply_atmosphere()
        self.update_caption(force=True)

    def change_speed(self, multiplier):
        self.season_duration = max(2.0, min(40.0, self.season_duration * multiplier))
        self.temperature_c = self.calculate_temperature()
        self.update_caption(force=True)

    def handle_key(self, key):
        if key == pg.K_1:
            self.set_season(0)
        elif key == pg.K_2:
            self.set_season(1)
        elif key == pg.K_3:
            self.set_season(2)
        elif key == pg.K_4:
            self.set_season(3)
        elif key == pg.K_t:
            self.toggle_time_lapse()
        elif key == pg.K_y:
            self.toggle_day_cycle()
        elif key == pg.K_l:
            self.set_day_time(0.04)
        elif key == pg.K_o:
            self.set_day_time(0.34)
        elif key == pg.K_n:
            self.next_season()
        elif key == pg.K_p:
            self.previous_season()
        elif key == pg.K_m:
            self.app.audio.toggle_mute(self.current)
            if hasattr(self.app, "settings"):
                self.app.settings.set("audio_muted", self.app.audio.muted)
            self.update_caption(force=True)
        elif key in (pg.K_EQUALS, pg.K_PLUS, pg.K_KP_PLUS):
            self.change_speed(0.75)
        elif key in (pg.K_MINUS, pg.K_KP_MINUS):
            self.change_speed(1.25)

    def update(self, delta_ms):
        delta_s = delta_ms * 0.001
        self.update_day_cycle(delta_s)

        if self.is_transitioning:
            self.transition_elapsed += delta_s
            if self.transition_elapsed >= self.transition_duration:
                self.transition_from = None
                self.transition_to = None
                self.transition_elapsed = 0.0
                self.app.apply_season()

            self.temperature_c = self.calculate_temperature()
            self.caption_timer += delta_s
            if self.caption_timer >= 0.25:
                self.update_caption(force=True)
                self.caption_timer = 0.0
            self.apply_atmosphere()
            return

        if self.time_lapse_enabled:
            self.elapsed += delta_s
            while self.elapsed >= self.season_duration:
                self.elapsed -= self.season_duration
                self.set_season(self.current_index + 1)
                return

        self.temperature_c = self.calculate_temperature()

        self.caption_timer += delta_s
        if self.caption_timer >= 0.25:
            self.update_caption()
            self.caption_timer = 0.0
        self.apply_atmosphere()

    def update_caption(self, force=False):
        mode = "ON" if self.time_lapse_enabled else "OFF"
        day_mode = "ON" if self.day_cycle_enabled else "OFF"
        day_state = self.day_state()
        clock_hour = int((self.day_time * 24.0) % 24.0)
        clock_minute = int(((self.day_time * 24.0) % 1.0) * 60.0)
        period = "Malam" if day_state["night"] > 0.55 else "Senja/Pagi" if day_state["dusk"] > 0.45 else "Siang"
        weather = self.current.get(
            "weather_label",
            "Hujan" if self.current.get("rain_enabled", False) else "Cerah",
        )
        wind = self.current.get("wind_strength", 0.0)
        audio_status = self.app.audio.status
        emotion = (
            f"{self.current.get('life_stage', '')}: "
            f"{self.current.get('emotion_title', '')} - "
            f"{self.current.get('emotion_line', '')}"
        )
        transition = ""
        if self.is_transitioning:
            story = self.transition_snapshot()["story"]
            transition = (
                f" | Transisi {self.transition_from['name']} ke {self.transition_to['name']} "
                f"{self.transition_progress * 100:0.0f}% | {story}"
            )
        caption = (
            "Modern GL Basics | "
            f"{self.current['name']} | "
            f"{emotion} | "
            f"Suhu {self.temperature_c:0.1f} C | "
            f"{weather} | Angin {wind:0.1f} | "
            f"Audio {audio_status} | "
            f"Time-lapse {mode} ({self.season_duration:0.1f}s/musim)"
            f" | {period} {clock_hour:02d}:{clock_minute:02d} Day-cycle {day_mode}"
            f"{transition} | "
            "1-4 musim, T auto musim, Y auto hari, L malam, O pagi, N/P geser, "
            "M mute, +/- speed, F1 kamera musim, F2 screenshot, F5-F8 kamera, F9 quality, "
            "C cinematic, F11 fullscreen, Esc pause"
        )
        pg.display.set_caption(caption)
