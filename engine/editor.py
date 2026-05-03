import pygame as pg

from .model import (
    BaseModelEmissive,
    BaseModelEmissiveTexture,
    FireflyGlow,
    RainDrop,
    SkyDome,
    WindStreak,
)


class SceneEditor:
    def __init__(self, app):
        self.app = app
        self.enabled = False
        self.selected_index = 0
        self.step = 0.12
        self.vertical_step = 0.08
        self.last_dump = ""

    def editable_objects(self):
        objects = []
        for obj in self.app.scene.objects:
            if getattr(obj, "is_background", False):
                continue
            if isinstance(obj, (SkyDome, BaseModelEmissive, BaseModelEmissiveTexture, RainDrop, WindStreak, FireflyGlow)):
                continue
            if hasattr(obj, "pos") and hasattr(obj, "get_model_matrix"):
                objects.append(obj)
        return objects

    def selected(self):
        objects = self.editable_objects()
        if not objects:
            return None
        self.selected_index %= len(objects)
        return objects[self.selected_index]

    def selected_label(self):
        obj = self.selected()
        if obj is None:
            return "No editable object"
        return f"{self.selected_index + 1}/{len(self.editable_objects())} {obj.__class__.__name__}"

    def toggle(self):
        self.enabled = not self.enabled
        pg.mouse.get_rel()

    def select_next(self, direction):
        objects = self.editable_objects()
        if not objects:
            return
        self.selected_index = (self.selected_index + direction) % len(objects)

    def move_selected(self, dx=0.0, dy=0.0, dz=0.0):
        obj = self.selected()
        if obj is None:
            return
        obj.pos.x += dx
        obj.pos.y += dy
        obj.pos.z += dz
        obj.m_model = obj.get_model_matrix()
        self.app.scene_renderer.instanced_color.scene_id = None

    def dump_selected(self):
        obj = self.selected()
        if obj is None:
            self.last_dump = "No editable object"
            return
        self.last_dump = (
            f"{obj.__class__.__name__} pos=({obj.pos.x:.2f}, {obj.pos.y:.2f}, {obj.pos.z:.2f}) "
            f"scale=({obj.scale.x:.2f}, {obj.scale.y:.2f}, {obj.scale.z:.2f})"
        )
        print(self.last_dump)

    def handle_key(self, key):
        if key == pg.K_F3:
            self.toggle()
            return True
        if not self.enabled:
            return False
        if key == pg.K_LEFTBRACKET:
            self.select_next(-1)
            return True
        if key == pg.K_RIGHTBRACKET:
            self.select_next(1)
            return True
        if key == pg.K_LEFT:
            self.move_selected(dx=-self.step)
            return True
        if key == pg.K_RIGHT:
            self.move_selected(dx=self.step)
            return True
        if key == pg.K_UP:
            self.move_selected(dz=-self.step)
            return True
        if key == pg.K_DOWN:
            self.move_selected(dz=self.step)
            return True
        if key == pg.K_PAGEUP:
            self.move_selected(dy=self.vertical_step)
            return True
        if key == pg.K_PAGEDOWN:
            self.move_selected(dy=-self.vertical_step)
            return True
        if key == pg.K_F4:
            self.dump_selected()
            return True
        return False
