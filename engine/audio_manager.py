from pathlib import Path
import math

import numpy as np
import pygame as pg

from .paths import PROJECT_DIR


class AudioManager:
    def __init__(self, muted=False):
        self.enabled = False
        self.muted = muted
        self.current_path = None
        self.current_ambience = None
        self.ambience_channel = None
        self.cue_channel = None
        self.ambience_sounds = {}
        self.transition_cues = {}
        self.status = "Audio OFF"

        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
            self.enabled = True
            self.ambience_channel = pg.mixer.Channel(1)
            self.cue_channel = pg.mixer.Channel(2)
            self.status = "Muted" if self.muted else "Audio siap"
        except pg.error:
            self.status = "Audio device tidak aktif"

    def resolve_path(self, path_value):
        if not path_value:
            return None

        path = Path(path_value)
        if not path.is_absolute():
            path = PROJECT_DIR / path
        return path

    def generate_ambience(self, kind):
        mixer = pg.mixer.get_init()
        if mixer is None:
            return None

        frequency, _, channels = mixer
        duration = 2.75
        count = int(frequency * duration)
        t = np.linspace(0.0, duration, count, endpoint=False)
        seed = {
            "spring": 11,
            "summer": 23,
            "autumn": 37,
            "winter": 53,
        }.get(kind, 71)
        rng = np.random.default_rng(seed)
        noise = np.cumsum(rng.normal(0.0, 0.012, count))
        noise = np.tanh(noise) * 0.10

        if kind == "summer":
            pulse = 0.55 + 0.45 * np.sin(2.0 * math.pi * 17.0 * t)
            wave = (
                np.sin(2.0 * math.pi * 3820.0 * t) * pulse * 0.06
                + np.sin(2.0 * math.pi * 193.0 * t) * 0.035
                + noise * 0.22
            )
        elif kind == "autumn":
            wave = np.sin(2.0 * math.pi * 94.0 * t) * 0.035 + noise * 0.34
            for burst in range(12):
                start = int((burst * 0.21 + 0.07 * (burst % 3)) * frequency) % count
                length = max(80, int(0.035 * frequency))
                end = min(count, start + length)
                envelope = np.linspace(1.0, 0.0, end - start)
                wave[start:end] += rng.normal(0.0, 0.08, end - start) * envelope
        elif kind == "winter":
            wave = (
                np.sin(2.0 * math.pi * 73.0 * t) * 0.045
                + np.sin(2.0 * math.pi * 147.0 * t + 0.8) * 0.020
                + noise * 0.42
            )
            bell = np.sin(2.0 * math.pi * 660.0 * t) * np.exp(-t * 2.2) * 0.030
            wave += bell
        else:
            wave = np.sin(2.0 * math.pi * 128.0 * t) * 0.030 + noise * 0.22
            for chirp in range(6):
                start = int((0.24 + chirp * 0.39) * frequency) % count
                length = max(100, int(0.055 * frequency))
                end = min(count, start + length)
                local_t = np.linspace(0.0, 1.0, end - start, endpoint=False)
                freq = 1600.0 + chirp * 130.0
                envelope = np.sin(math.pi * local_t) ** 2
                wave[start:end] += np.sin(2.0 * math.pi * freq * local_t * 0.055) * envelope * 0.055

        peak = max(0.001, float(np.max(np.abs(wave))))
        wave = np.clip(wave / peak * 0.36, -1.0, 1.0)
        samples = (wave * 32767).astype(np.int16)
        if channels == 2:
            samples = np.column_stack((samples, samples))
        return pg.sndarray.make_sound(samples)

    def generate_transition_cue(self, kind):
        mixer = pg.mixer.get_init()
        if mixer is None:
            return None

        frequency, _, channels = mixer
        duration = 1.15
        count = int(frequency * duration)
        t = np.linspace(0.0, duration, count, endpoint=False)
        rng = np.random.default_rng(
            {
                "thaw": 101,
                "heat": 113,
                "leaves": 127,
                "snow": 149,
            }.get(kind, 173)
        )
        envelope = np.sin(np.linspace(0.0, math.pi, count)) ** 2
        noise = rng.normal(0.0, 0.035, count)

        if kind == "thaw":
            crack = np.zeros(count)
            for offset in (0.08, 0.18, 0.31):
                start = int(offset * frequency)
                length = min(count - start, int(0.045 * frequency))
                burst_env = np.linspace(1.0, 0.0, length) ** 2
                crack[start:start + length] += rng.normal(0.0, 0.28, length) * burst_env
            drip = np.sin(2.0 * math.pi * 820.0 * t) * np.exp(-t * 2.8) * 0.12
            wave = crack + drip + noise * envelope * 0.25
        elif kind == "heat":
            shimmer = np.sin(2.0 * math.pi * (420.0 + 90.0 * np.sin(t * 8.0)) * t) * 0.055
            wave = shimmer * envelope + noise * 0.16
        elif kind == "leaves":
            rustle = noise * (0.30 + 0.70 * np.sin(2.0 * math.pi * 4.0 * t) ** 2)
            low = np.sin(2.0 * math.pi * 92.0 * t) * 0.035
            wave = (rustle + low) * envelope
        elif kind == "snow":
            wind = np.sin(2.0 * math.pi * 70.0 * t) * 0.040 + noise * 0.20
            bell = np.sin(2.0 * math.pi * 960.0 * t) * np.exp(-t * 3.4) * 0.055
            wave = (wind + bell) * envelope
        else:
            wave = noise * envelope * 0.20

        peak = max(0.001, float(np.max(np.abs(wave))))
        samples = np.clip(wave / peak * 0.42, -1.0, 1.0)
        samples = (samples * 32767).astype(np.int16)
        if channels == 2:
            samples = np.column_stack((samples, samples))
        return pg.sndarray.make_sound(samples)

    def play_transition_cue(self, pair, kind="blend"):
        if not self.enabled or self.muted or self.cue_channel is None:
            return False

        cue_key = f"{pair}:{kind}"
        sound = self.transition_cues.get(cue_key)
        if sound is None:
            sound = self.generate_transition_cue(kind)
            if sound is None:
                return False
            self.transition_cues[cue_key] = sound

        self.cue_channel.play(sound)
        self.cue_channel.set_volume(0.36)
        return True

    def start_ambience(self, season):
        if not self.enabled or self.ambience_channel is None:
            return False

        kind = season.get("ambience_type", season.get("id", "spring"))
        volume = float(season.get("ambience_volume", 0.16))
        if self.current_ambience == kind and self.ambience_channel.get_busy():
            self.ambience_channel.set_volume(volume)
            return True

        sound = self.ambience_sounds.get(kind)
        if sound is None:
            sound = self.generate_ambience(kind)
            if sound is None:
                return False
            self.ambience_sounds[kind] = sound

        self.ambience_channel.play(sound, loops=-1, fade_ms=900)
        self.ambience_channel.set_volume(volume)
        self.current_ambience = kind
        return True

    def apply_season(self, season):
        if not self.enabled:
            return

        if self.muted:
            self.stop(fade_ms=300)
            self.status = "Muted"
            return

        ambience_on = self.start_ambience(season)
        music_path = self.resolve_path(season.get("music_path"))
        if music_path is None:
            self.stop_music()
            self.status = f"Ambience: {season.get('name', season.get('id', 'season'))}" if ambience_on else "Tidak ada musik"
            return

        if not music_path.exists():
            self.stop_music()
            self.status = f"Ambience: {season.get('name', music_path.name)}" if ambience_on else f"File belum ada: {music_path.name}"
            return

        if self.current_path == music_path and pg.mixer.music.get_busy():
            self.status = f"Play: {music_path.name} + ambience" if ambience_on else f"Play: {music_path.name}"
            return

        try:
            pg.mixer.music.fadeout(500)
            pg.mixer.music.load(str(music_path))
            pg.mixer.music.set_volume(season.get("music_volume", 0.45))
            pg.mixer.music.play(loops=-1, fade_ms=1200)
            self.current_path = music_path
            self.status = f"Play: {music_path.name} + ambience" if ambience_on else f"Play: {music_path.name}"
        except pg.error:
            self.current_path = None
            self.status = f"Ambience: {season.get('name', music_path.name)}" if ambience_on else f"Gagal play: {music_path.name}"

    def toggle_mute(self, season):
        self.muted = not self.muted
        if self.muted:
            self.stop(fade_ms=500)
            self.status = "Muted"
        else:
            self.apply_season(season)

    def stop(self, fade_ms=800):
        self.stop_music(fade_ms)
        self.stop_ambience(fade_ms)
        if self.cue_channel is not None:
            self.cue_channel.fadeout(fade_ms)

    def stop_music(self, fade_ms=800):
        if self.enabled and pg.mixer.get_init():
            pg.mixer.music.fadeout(fade_ms)
        self.current_path = None

    def stop_ambience(self, fade_ms=800):
        if self.ambience_channel is not None:
            self.ambience_channel.fadeout(fade_ms)
        self.current_ambience = None

    def destroy(self):
        if self.enabled and pg.mixer.get_init():
            self.stop_ambience(fade_ms=100)
            pg.mixer.music.stop()
            pg.mixer.quit()
