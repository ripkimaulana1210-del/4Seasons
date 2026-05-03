import sys
from datetime import datetime

import pygame as pg
import moderngl as mgl

from .audio_manager import AudioManager
from .camera import Camera
from .editor import SceneEditor
from .hud import HUD
from .mesh import Mesh
from .paths import SCREENSHOT_DIR
from .point_light import PointLight
from .postprocess import PostProcessor
from .quality import QualityManager
from .scene import Scene
from .scene_renderer import SceneRenderer
from .season_controller import SeasonController
from .settings import SettingsManager


class SxvxnEngine:
    def __init__(self, win_size=(1280, 720)):
        pg.init()
        pg.display.set_caption("Modern GL Basics")
        self.settings = SettingsManager()
        win_size = self.settings.window_size(win_size)
        self.WIN_SIZE = win_size
        self.windowed_size = win_size
        self.fullscreen = bool(self.settings.get("fullscreen", False))
        self.screenshot_requested = False
        self.last_screenshot_path = ""
        self.paused = False
        self.profile_visible = bool(self.settings.get("profile_visible", True))
        self.hud_visible = True
        self.adaptive_quality_enabled = bool(self.settings.get("adaptive_quality", True))
        self.adaptive_quality_status = "Adaptive siap"
        self.adaptive_quality_timer = 0.0
        self.adaptive_quality_cooldown = 0.0
        self.render_stats = {}
        self.frame_count = 0
        self.fps_avg = 0.0
        self.fps_min = 0.0

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        self.display_flags = pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
        display_flags = self.display_flags
        if self.fullscreen:
            info = pg.display.Info()
            self.WIN_SIZE = (max(640, info.current_w), max(360, info.current_h))
            display_flags = pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN
        pg.display.set_mode(self.WIN_SIZE, flags=display_flags)

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.ctx = mgl.create_context(require=330)
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA
        self.ctx.gc_mode = "auto"

        self.clock = pg.time.Clock()
        self.time = 0.0
        self.delta_time = 0.0
        self.background_color = (0.60, 0.74, 0.90)
        self.audio = AudioManager(muted=bool(self.settings.get("audio_muted", False)))
        self.quality = QualityManager(self.settings.get("quality", "high"))

        self.season_controller = SeasonController(self)
        season = self.season_controller.current
        self.background_color = season["background_color"]
        self.light = PointLight(
            position=season["light_position"],
            color=season["light_color"],
            intensity=season["light_intensity"],
        )
        self.season_controller.apply_atmosphere()
        self.camera = Camera(self)
        saved_preset = self.settings.get("camera_preset", "free")
        if saved_preset not in ("free", "orbit", "cinematic"):
            self.camera.set_preset(saved_preset)
        elif saved_preset == "orbit":
            self.camera.use_orbit = True
            self.camera.set_default()
        elif saved_preset == "cinematic":
            self.camera.toggle_cinematic()
        self.mesh = Mesh(self)
        self.scene = Scene(self)
        self.post_processor = PostProcessor(self)
        self.post_processor.enabled = bool(self.settings.get("postprocess", True))
        self.scene_renderer = SceneRenderer(self)
        self.scene_renderer.shadow_renderer.enabled = bool(self.settings.get("shadow", True))
        self.editor = SceneEditor(self)
        self.hud = HUD(self)
        self.audio.apply_season(season)
        self.season_controller.update_caption(force=True)

    def apply_season(self):
        self.quality.reset_scene_counters()
        season = self.season_controller.current
        self.background_color = season["background_color"]
        self.light = PointLight(
            position=season["light_position"],
            color=season["light_color"],
            intensity=season["light_intensity"],
        )
        self.season_controller.apply_atmosphere()
        self.audio.apply_season(season)
        self.scene = Scene(self)
        self.scene_renderer.scene = self.scene
        if hasattr(self, "editor"):
            self.editor.selected_index = 0

    def quit(self):
        self.destroy()
        pg.quit()
        sys.exit()

    def toggle_pause(self):
        self.paused = not self.paused
        pg.mouse.get_rel()

    def cycle_quality(self):
        self.quality.next()
        self.adaptive_quality_timer = 0.0
        self.adaptive_quality_cooldown = 6.0
        self.adaptive_quality_status = f"Manual: {self.quality.name}"
        self.settings.set("quality", self.quality.current["id"])
        self.apply_season()
        self.season_controller.update_caption(force=True)

    def resize(self, size):
        width = max(640, size[0])
        height = max(360, size[1])
        self.WIN_SIZE = (width, height)
        self.ctx.viewport = (0, 0, width, height)
        self.camera.resize(self.WIN_SIZE)
        self.post_processor.resize()
        self.hud.resize()
        if not self.fullscreen:
            self.settings.set("windowed_size", [width, height])

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.windowed_size = self.WIN_SIZE
            info = pg.display.Info()
            self.WIN_SIZE = (info.current_w, info.current_h)
            flags = pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN
        else:
            self.WIN_SIZE = self.windowed_size
            flags = self.display_flags

        pg.display.set_mode(self.WIN_SIZE, flags=flags)
        self.resize(self.WIN_SIZE)
        self.settings.update(
            fullscreen=self.fullscreen,
            windowed_size=[self.windowed_size[0], self.windowed_size[1]],
        )

    def request_screenshot(self):
        self.screenshot_requested = True

    def toggle_profile(self):
        self.profile_visible = not self.profile_visible
        self.settings.set("profile_visible", self.profile_visible)

    def toggle_postprocess(self):
        self.post_processor.enabled = not self.post_processor.enabled
        self.settings.set("postprocess", self.post_processor.enabled)

    def toggle_shadow(self):
        self.scene_renderer.shadow_renderer.enabled = not self.scene_renderer.shadow_renderer.enabled
        self.settings.set("shadow", self.scene_renderer.shadow_renderer.enabled)

    def update_adaptive_quality(self):
        if not self.adaptive_quality_enabled or self.delta_time <= 0:
            return
        if self.frame_count < 120:
            return

        delta_s = self.delta_time * 0.001
        self.adaptive_quality_cooldown = max(0.0, self.adaptive_quality_cooldown - delta_s)
        if self.adaptive_quality_cooldown > 0.0:
            return

        target_status = self.adaptive_quality_status
        if self.fps_avg < 42.0 and self.quality.index > 0:
            self.adaptive_quality_timer += delta_s
            if self.adaptive_quality_timer >= 1.2:
                self.quality.lower()
                self.apply_season()
                self.adaptive_quality_status = f"Adaptive turun ke {self.quality.name}"
                self.adaptive_quality_cooldown = 7.0
                self.adaptive_quality_timer = 0.0
                return
        elif self.fps_avg > 58.0 and self.quality.index < len(self.quality.profiles) - 1:
            self.adaptive_quality_timer += delta_s
            if self.adaptive_quality_timer >= 6.0:
                self.quality.raise_one()
                self.apply_season()
                self.adaptive_quality_status = f"Adaptive naik ke {self.quality.name}"
                self.adaptive_quality_cooldown = 9.0
                self.adaptive_quality_timer = 0.0
                return
        else:
            self.adaptive_quality_timer = 0.0

        if self.frame_count % 120 == 0:
            self.adaptive_quality_status = target_status

    def save_screenshot(self):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"sxvxn_{timestamp}.png"

        data = self.ctx.screen.read(components=3, alignment=1)
        surface = pg.image.frombuffer(data, self.WIN_SIZE, "RGB")
        surface = pg.transform.flip(surface, False, True)
        pg.image.save(surface, str(path))
        self.last_screenshot_path = path.name
        self.screenshot_requested = False

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.toggle_pause()
                continue

            if self.paused and event.type == pg.KEYDOWN and event.key == pg.K_q:
                self.quit()

            if event.type == pg.KEYDOWN and self.editor.handle_key(event.key):
                continue

            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.camera.use_orbit = not self.camera.use_orbit
                self.camera.set_default()
                self.settings.set("camera_preset", self.camera.preset_name)

            if event.type == pg.KEYDOWN:
                self.season_controller.handle_key(event.key)
                if event.key == pg.K_F1:
                    self.camera.set_season_preset()
                    self.settings.set("camera_preset", self.camera.preset_name)
                elif event.key == pg.K_F2:
                    self.request_screenshot()
                elif event.key == pg.K_F5:
                    self.camera.set_preset("sakura")
                    self.settings.set("camera_preset", "sakura")
                elif event.key == pg.K_F6:
                    self.camera.set_preset("bridge")
                    self.settings.set("camera_preset", "bridge")
                elif event.key == pg.K_F7:
                    self.camera.set_preset("village")
                    self.settings.set("camera_preset", "village")
                elif event.key == pg.K_F8:
                    self.camera.set_preset("fuji")
                    self.settings.set("camera_preset", "fuji")
                elif event.key == pg.K_c:
                    self.camera.toggle_cinematic()
                    self.settings.set("camera_preset", self.camera.preset_name)
                elif event.key == pg.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pg.K_F9:
                    self.cycle_quality()
                elif event.key == pg.K_F10:
                    self.toggle_profile()
                elif event.key == pg.K_F12:
                    self.toggle_postprocess()
                elif event.key == pg.K_F4:
                    self.toggle_shadow()

            if event.type == pg.KEYDOWN and event.key == pg.K_BACKQUOTE:
                visible = not pg.mouse.get_visible()
                pg.mouse.set_visible(visible)
                pg.event.set_grab(not visible)

            if event.type == pg.VIDEORESIZE and not self.fullscreen:
                self.windowed_size = event.size
                self.resize(event.size)

            if event.type == pg.MOUSEBUTTONDOWN and self.camera.use_orbit:
                if event.button == 4:
                    self.camera.orbit_radius = max(2.0, self.camera.orbit_radius - 0.5)
                elif event.button == 5:
                    self.camera.orbit_radius = min(40.0, self.camera.orbit_radius + 0.5)

    def render(self):
        self.post_processor.begin()
        self.ctx.clear(color=self.background_color)
        self.scene_renderer.render()
        self.post_processor.render()
        if self.hud_visible:
            self.hud.render()
        if self.screenshot_requested:
            self.save_screenshot()
        pg.display.flip()

    def update_frame_stats(self):
        if self.delta_time <= 0:
            return

        fps = 1000.0 / self.delta_time
        self.frame_count += 1
        if self.frame_count == 1:
            self.fps_avg = fps
            self.fps_min = fps
        else:
            self.fps_avg = self.fps_avg * 0.96 + fps * 0.04
            self.fps_min = min(self.fps_min, fps)

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def destroy(self):
        self.scene_renderer.destroy()
        self.hud.destroy()
        self.post_processor.destroy()
        self.mesh.destroy()
        self.audio.destroy()

    def run(self):
        while True:
            self.get_time()
            self.check_events()
            if not self.paused:
                self.season_controller.update(self.delta_time)
                self.camera.update()
            self.render()
            self.delta_time = self.clock.tick(60)
            self.update_frame_stats()
            self.update_adaptive_quality()
