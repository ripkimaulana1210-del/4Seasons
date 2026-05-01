from pathlib import Path

import pygame as pg

from .paths import PROJECT_DIR


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.current_path = None
        self.status = "Audio OFF"

        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
            self.enabled = True
            self.status = "Audio siap"
        except pg.error:
            self.status = "Audio device tidak aktif"

    def resolve_path(self, path_value):
        if not path_value:
            return None

        path = Path(path_value)
        if not path.is_absolute():
            path = PROJECT_DIR / path
        return path

    def apply_season(self, season):
        if not self.enabled:
            return

        if self.muted:
            self.stop(fade_ms=300)
            self.status = "Muted"
            return

        music_path = self.resolve_path(season.get("music_path"))
        if music_path is None:
            self.stop()
            self.status = "Tidak ada musik"
            return

        if not music_path.exists():
            self.stop()
            self.status = f"File belum ada: {music_path.name}"
            return

        if self.current_path == music_path and pg.mixer.music.get_busy():
            self.status = f"Play: {music_path.name}"
            return

        try:
            pg.mixer.music.fadeout(500)
            pg.mixer.music.load(str(music_path))
            pg.mixer.music.set_volume(season.get("music_volume", 0.45))
            pg.mixer.music.play(loops=-1, fade_ms=1200)
            self.current_path = music_path
            self.status = f"Play: {music_path.name}"
        except pg.error:
            self.current_path = None
            self.status = f"Gagal play: {music_path.name}"

    def toggle_mute(self, season):
        self.muted = not self.muted
        if self.muted:
            self.stop(fade_ms=500)
            self.status = "Muted"
        else:
            self.apply_season(season)

    def stop(self, fade_ms=800):
        if self.enabled and pg.mixer.get_init():
            pg.mixer.music.fadeout(fade_ms)
        self.current_path = None

    def destroy(self):
        if self.enabled and pg.mixer.get_init():
            pg.mixer.music.stop()
            pg.mixer.quit()
