from .data.scene_config import QUALITY_PROFILES
from .model import ContactShadow, DriftParticle, FireflyGlow, NightGlow, PondRock, RainDrop, WindStreak


class QualityManager:
    def __init__(self, initial_id=None):
        self.profiles = QUALITY_PROFILES
        self.index = len(self.profiles) - 1
        self.counters = {}
        if initial_id is not None:
            self.set_profile(initial_id)

    @property
    def current(self):
        return self.profiles[self.index]

    @property
    def name(self):
        return self.current["name"]

    def reset_scene_counters(self):
        self.counters = {}

    def set_profile(self, profile_id):
        profile_id = str(profile_id).lower()
        for index, profile in enumerate(self.profiles):
            if profile["id"] == profile_id or profile["name"].lower() == profile_id:
                self.index = index
                self.reset_scene_counters()
                return self.current
        return self.current

    def next(self):
        self.index = (self.index + 1) % len(self.profiles)
        self.reset_scene_counters()
        return self.current

    def lower(self):
        if self.index <= 0:
            return self.current
        self.index -= 1
        self.reset_scene_counters()
        return self.current

    def raise_one(self):
        if self.index >= len(self.profiles) - 1:
            return self.current
        self.index += 1
        self.reset_scene_counters()
        return self.current

    def category_for(self, obj):
        if isinstance(obj, RainDrop):
            return "rain"
        if isinstance(obj, WindStreak):
            return "wind"
        if isinstance(obj, DriftParticle):
            return "particle"
        if isinstance(obj, FireflyGlow):
            return "firefly"
        if isinstance(obj, NightGlow):
            return "glow"
        if isinstance(obj, ContactShadow):
            return "shadow"
        if isinstance(obj, PondRock):
            return "pond_rock"
        return None

    def should_include(self, obj):
        category = self.category_for(obj)
        if category is None:
            return True

        fraction = self.current["fractions"].get(category, 1.0)
        if fraction >= 1.0:
            return True

        count = self.counters.get(category, 0)
        self.counters[category] = count + 1
        return ((count * 37) % 100) < int(fraction * 100)
