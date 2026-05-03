import json

from .paths import SETTINGS_PATH


DEFAULT_SETTINGS = {
    "quality": "high",
    "postprocess": True,
    "shadow": True,
    "profile_visible": True,
    "audio_muted": False,
    "fullscreen": False,
    "windowed_size": [1280, 720],
    "camera_preset": "free",
    "adaptive_quality": True,
}


class SettingsManager:
    def __init__(self, path=SETTINGS_PATH):
        self.path = path
        self.data = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if not self.path.exists():
            return

        try:
            with self.path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(loaded, dict):
            self.data.update(
                {
                    key: value
                    for key, value in loaded.items()
                    if key in DEFAULT_SETTINGS
                }
            )

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)
            file.write("\n")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def update(self, **values):
        self.data.update(values)
        self.save()

    def window_size(self, fallback):
        size = self.get("windowed_size", fallback)
        if not isinstance(size, list) or len(size) != 2:
            return fallback

        try:
            width = int(size[0])
            height = int(size[1])
        except (TypeError, ValueError):
            return fallback

        return (max(640, width), max(360, height))
