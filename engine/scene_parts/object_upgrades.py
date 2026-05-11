from .object_upgrades_background import SceneBackgroundUpgradeMixin
from .object_upgrades_water import SceneWaterUpgradeMixin
from .object_upgrades_shrine import SceneShrineUpgradeMixin
from .object_upgrades_village import SceneVillageUpgradeMixin
from .object_upgrades_seasonal import SceneSeasonalObjectUpgradeMixin


class SceneObjectUpgradeMixin(SceneBackgroundUpgradeMixin, SceneWaterUpgradeMixin, SceneShrineUpgradeMixin, SceneVillageUpgradeMixin, SceneSeasonalObjectUpgradeMixin):
    def add_object_upgrades(self, app, pond_radius_scale):
        self.add_distant_background_layers(app)
        self.add_foreground_plants(app)
        self.add_pond_life(app, pond_radius_scale)
        self.add_stream_and_waterfall(app, pond_radius_scale)
        self.add_stepping_stones_and_boat(app, pond_radius_scale)
        self.add_torii_and_shrine(app)
        self.add_shrine_path_and_offerings(app)
        self.add_bridge_detail_props(app, pond_radius_scale)
        self.add_extra_house_details(app)
        self.add_extra_vegetation(app)
        self.add_seasonal_props(app)
