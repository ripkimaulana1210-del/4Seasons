import sys
from datetime import datetime
import ctypes
import os

import pygame as pg
import moderngl as mgl

from ..systems.audio_manager import AudioManager
from .camera import Camera
from ..ui.editor import SceneEditor
from ..ui.hud import HUD
from ..rendering.mesh import Mesh
from .paths import SCREENSHOT_DIR
from .point_light import PointLight
from ..rendering.postprocess import PostProcessor
from .quality import QualityManager
from ..scenes.scene import Scene
from ..rendering.scene_renderer import SceneRenderer
from ..systems.season_controller import SeasonController
from .settings import SettingsManager


def enable_dpi_awareness():
    if os.name != "nt":
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


class SxvxnEngine:
    def __init__(self, win_size=None):
        enable_dpi_awareness()
        pg.init()
        pg.display.set_caption("Modern GL Basics")
        self.settings = SettingsManager()
        win_size = self.settings.window_size(win_size or self.desktop_size())
        self.WIN_SIZE = win_size
        self.windowed_size = win_size
        self.fullscreen = True
        self.screenshot_requested = False
        self.last_screenshot_path = ""
        self.paused = False
        self.pause_screen = "main"
        self.pause_parent = "pause"
        self.profile_visible = bool(self.settings.get("profile_visible", True))
        self.hud_visible = bool(self.settings.get("hud_visible", True))
        self.quality_mode = self.settings.get("quality_mode", "manual")
        if self.quality_mode not in ("manual", "adaptive"):
            self.quality_mode = "manual"
        self.adaptive_quality_enabled = self.quality_mode == "adaptive" and bool(self.settings.get("adaptive_quality", False))
        self.adaptive_quality_status = "Adaptive siap" if self.adaptive_quality_enabled else "Manual quality"
        self.adaptive_quality_timer = 0.0
        self.adaptive_quality_cooldown = 0.0
        self.render_stats = {}
        self.frame_count = 0
        self.fps_avg = 0.0
        self.fps_min = 0.0
        self.game_started = False

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        self.display_flags = pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
        self.fullscreen_flags = pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN
        self.WIN_SIZE = self.desktop_size()
        pg.display.set_mode(self.WIN_SIZE, flags=self.fullscreen_flags)
        self.WIN_SIZE = self.display_size()
        self.settings.set("fullscreen", True)

        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        self.ctx = mgl.create_context(require=330)
        self.ctx.viewport = (0, 0, self.WIN_SIZE[0], self.WIN_SIZE[1])
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA
        self.ctx.gc_mode = "auto"

        self.clock = pg.time.Clock()
        self.time = 0.0
        self.delta_time = 0.0
        self.background_color = (0.60, 0.74, 0.90)
        self.audio = AudioManager(
            muted=bool(self.settings.get("audio_muted", False)),
            master_volume=self.settings.get("master_volume", 1.0),
            music_volume=self.settings.get("music_volume", 1.0),
            sfx_volume=self.settings.get("sfx_volume", 1.0),
            ambience_volume=self.settings.get("ambience_volume", 1.0),
            ui_volume=self.settings.get("ui_volume", 1.0),
        )
        self.quality = QualityManager(self.settings.get("quality", "medium"))
        self.adaptive_quality_status = f"Adaptive {self.quality.name}" if self.adaptive_quality_enabled else f"Quality {self.quality.name}"

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
        self.season_controller.update_caption(force=True)

    def desktop_size(self):
        try:
            sizes = pg.display.get_desktop_sizes()
            if sizes:
                width, height = sizes[0]
                return (max(640, int(width)), max(360, int(height)))
        except (AttributeError, pg.error, TypeError, ValueError):
            pass

        info = pg.display.Info()
        return (max(640, int(info.current_w)), max(360, int(info.current_h)))

    def display_size(self):
        surface = pg.display.get_surface()
        if surface is not None:
            width, height = surface.get_size()
            if width > 0 and height > 0:
                return (int(width), int(height))
        return self.WIN_SIZE

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
        if not self.game_started:
            return
        if self.paused:
            if self.pause_screen in ("controls", "audio", "graphics"):
                self.back_from_submenu()
            else:
                self.resume_game()
        else:
            self.open_pause_menu()
        pg.mouse.get_rel()

    def open_pause_menu(self):
        self.paused = True
        self.pause_screen = "main"
        self.pause_parent = "pause"
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        self.hud.reset_pause_texture()

    def show_pause_menu(self):
        self.pause_screen = "main"
        self.pause_parent = "pause"
        self.hud.reset_pause_texture()

    def open_settings_menu(self):
        self.paused = True
        self.pause_screen = "settings"
        self.pause_parent = "settings"
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        self.hud.reset_pause_texture()

    def close_settings_menu(self):
        self.paused = False
        self.pause_screen = "main"
        self.pause_parent = "pause"
        self.hud.reset_pause_texture()
        self.hud.invalidate_startup_texture()

    def show_control_menu(self, parent=None):
        self.pause_screen = "controls"
        if parent is not None:
            self.pause_parent = parent
        self.hud.pause_scroll = 0
        self.hud.reset_pause_texture()

    def show_menu_page(self, page, parent=None):
        self.pause_screen = page
        if parent is not None:
            self.pause_parent = parent
        self.hud.reset_pause_texture()

    def show_graphic_menu(self, parent=None):
        self.show_menu_page("graphics", parent)

    def show_audio_menu(self, parent=None):
        self.show_menu_page("audio", parent)

    def back_from_submenu(self):
        if self.pause_parent == "settings":
            self.pause_screen = "settings"
        else:
            self.pause_screen = "main"
        self.hud.reset_pause_texture()

    def resume_game(self):
        self.paused = False
        self.pause_screen = "main"
        self.pause_parent = "pause"
        self.hud.reset_pause_texture()
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        pg.mouse.get_rel()

    def return_to_main_menu(self):
        self.game_started = False
        self.paused = False
        self.pause_screen = "main"
        self.pause_parent = "pause"
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)
        self.hud.reset_pause_texture()
        self.hud.invalidate_startup_texture()
        self.audio.stop(fade_ms=400)
        self.season_controller.update_caption(force=True)

    def set_graphics_quality(self, profile_id):
        if str(profile_id).lower() in ("adaptive", "auto"):
            self.quality_mode = "adaptive"
            self.adaptive_quality_enabled = True
            self.adaptive_quality_timer = 0.0
            self.adaptive_quality_cooldown = 0.0
            self.adaptive_quality_status = f"Adaptive {self.quality.name}"
            self.settings.update(
                quality=self.quality.current["id"],
                quality_mode="adaptive",
                adaptive_quality=True,
            )
            self.hud.reset_pause_texture()
            return

        previous_id = self.quality.current["id"]
        self.quality.set_profile(profile_id)
        current_id = self.quality.current["id"]
        self.quality_mode = "manual"
        self.adaptive_quality_enabled = False
        self.adaptive_quality_timer = 0.0
        self.adaptive_quality_cooldown = 6.0
        self.adaptive_quality_status = f"Quality {self.quality.name}"
        self.settings.update(
            quality=current_id,
            quality_mode="manual",
            adaptive_quality=False,
        )
        if self.game_started and current_id != previous_id:
            self.apply_season()
            self.season_controller.update_caption(force=True)
        self.hud.reset_pause_texture()

    def quality_label(self):
        prefix = "Adaptive" if self.adaptive_quality_enabled else "Quality"
        return f"{prefix} {self.quality.name}"

    def set_audio_volume(self, channel, value):
        self.audio.set_volume(channel, value)
        self.settings.set(f"{channel}_volume", self.audio.volume_state()[channel])
        self.hud.invalidate_pause_texture()

    def start_game(self, season_id=None):
        self.game_started = True
        if season_id:
            self.season_controller.current_index = self.season_controller.index_for_id(season_id)
            self.season_controller.transition_manager.reset()
            self.season_controller.elapsed = 0.0
            self.season_controller.temperature_c = self.season_controller.calculate_temperature()
            self.apply_season()
        else:
            self.audio.apply_season(self.season_controller.current)
        self.season_controller.update_caption(force=True)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)
        pg.mouse.get_rel()

    def cycle_quality(self):
        self.quality.next()
        self.quality_mode = "manual"
        self.adaptive_quality_enabled = False
        self.adaptive_quality_timer = 0.0
        self.adaptive_quality_cooldown = 6.0
        self.adaptive_quality_status = f"Quality {self.quality.name}"
        self.settings.update(
            quality=self.quality.current["id"],
            quality_mode="manual",
            adaptive_quality=False,
        )
        self.apply_season()
        self.season_controller.update_caption(force=True)

    def resize(self, size=None):
        if size is None:
            size = self.display_size()
        width = max(640, int(size[0]))
        height = max(360, int(size[1]))
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
            self.WIN_SIZE = self.desktop_size()
            flags = self.fullscreen_flags
        else:
            self.WIN_SIZE = self.windowed_size
            flags = self.display_flags

        pg.display.set_mode(self.WIN_SIZE, flags=flags)
        self.resize()
        self.settings.update(
            fullscreen=self.fullscreen,
            windowed_size=[self.windowed_size[0], self.windowed_size[1]],
        )

    def request_screenshot(self):
        self.screenshot_requested = True

    def toggle_profile(self):
        self.profile_visible = not self.profile_visible
        self.settings.set("profile_visible", self.profile_visible)

    def toggle_hud(self):
        self.hud_visible = not self.hud_visible
        self.settings.set("hud_visible", self.hud_visible)

    def toggle_postprocess(self):
        self.post_processor.enabled = not self.post_processor.enabled
        self.settings.set("postprocess", self.post_processor.enabled)

    def toggle_shadow(self):
        self.scene_renderer.shadow_renderer.enabled = not self.scene_renderer.shadow_renderer.enabled
        self.settings.set("shadow", self.scene_renderer.shadow_renderer.enabled)

    def startup_overlay_alpha(self):
        return 0.0 if self.game_started else 1.0

    def update_adaptive_quality(self):
        if self.quality_mode != "adaptive" or not self.adaptive_quality_enabled or self.delta_time <= 0:
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
                self.settings.set("quality", self.quality.current["id"])
                self.apply_season()
                self.adaptive_quality_status = f"Adaptive {self.quality.name}"
                self.adaptive_quality_cooldown = 7.0
                self.adaptive_quality_timer = 0.0
                return
        elif self.fps_avg > 58.0 and self.quality.index < len(self.quality.profiles) - 1:
            self.adaptive_quality_timer += delta_s
            if self.adaptive_quality_timer >= 6.0:
                self.quality.raise_one()
                self.settings.set("quality", self.quality.current["id"])
                self.apply_season()
                self.adaptive_quality_status = f"Adaptive {self.quality.name}"
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

            if event.type == pg.VIDEORESIZE:
                self.windowed_size = event.size
                self.resize(event.size if not self.fullscreen else None)
                continue

            if not self.game_started:
                if self.paused:
                    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                        if self.pause_screen in ("controls", "audio", "graphics"):
                            self.back_from_submenu()
                        else:
                            self.close_settings_menu()
                        continue
                    if event.type == pg.MOUSEWHEEL:
                        if self.pause_screen == "controls":
                            self.hud.scroll_pause_help(event.y)
                        continue
                    if event.type == pg.MOUSEMOTION:
                        if self.pause_screen == "audio" and event.buttons[0]:
                            result = self.hud.handle_audio_drag(event.pos)
                            if result is not None:
                                self.set_audio_volume(*result)
                        else:
                            self.hud.invalidate_pause_texture()
                        continue
                    if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        result = self.hud.handle_pause_input(event)
                        if result == "controls":
                            self.show_control_menu(parent="settings")
                        elif result == "audio":
                            self.show_audio_menu(parent="settings")
                        elif result == "graphics":
                            self.show_graphic_menu(parent="settings")
                        elif result == "back":
                            if self.pause_screen in ("controls", "audio", "graphics"):
                                self.back_from_submenu()
                            else:
                                self.close_settings_menu()
                        elif result.startswith("quality:"):
                            self.set_graphics_quality(result.split(":", 1)[1])
                        elif result.startswith("volume:"):
                            _prefix, channel, value = result.split(":", 2)
                            self.set_audio_volume(channel, float(value))
                        continue
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.quit()
                if event.type == pg.KEYDOWN and event.key == pg.K_F11:
                    self.toggle_fullscreen()
                    pg.event.set_grab(False)
                    pg.mouse.set_visible(True)
                    continue
                if event.type == pg.MOUSEMOTION:
                    self.hud.invalidate_startup_texture()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    result = self.hud.handle_menu_input(event)
                    if result["action"] == "play":
                        self.start_game(result.get("season_id"))
                    elif result["action"] == "settings":
                        self.open_settings_menu()
                    elif result["action"] == "exit":
                        self.quit()
                    elif result["action"] == "none":
                        self.hud.invalidate_startup_texture()
                continue

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.toggle_pause()
                continue

            if self.paused and event.type == pg.MOUSEMOTION:
                if self.pause_screen == "audio" and event.buttons[0]:
                    result = self.hud.handle_audio_drag(event.pos)
                    if result is not None:
                        self.set_audio_volume(*result)
                else:
                    self.hud.invalidate_pause_texture()
                continue

            if self.paused and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                result = self.hud.handle_pause_input(event)
                if result == "resume":
                    self.resume_game()
                elif result == "controls":
                    self.show_control_menu(parent="pause")
                elif result == "audio":
                    self.show_audio_menu(parent="pause")
                elif result == "graphics":
                    self.show_graphic_menu(parent="pause")
                elif result == "back":
                    self.back_from_submenu()
                elif result == "main_menu":
                    self.return_to_main_menu()
                elif result.startswith("quality:"):
                    self.set_graphics_quality(result.split(":", 1)[1])
                elif result.startswith("volume:"):
                    _prefix, channel, value = result.split(":", 2)
                    self.set_audio_volume(channel, float(value))
                continue

            if self.paused and event.type == pg.KEYDOWN and event.key == pg.K_q:
                self.quit()

            if self.paused and event.type == pg.MOUSEWHEEL:
                if self.pause_screen == "controls":
                    self.hud.scroll_pause_help(event.y)
                continue

            if self.paused:
                continue

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
                elif event.key == pg.K_h:
                    self.toggle_hud()
                elif event.key == pg.K_F12:
                    self.toggle_postprocess()
                elif event.key == pg.K_F4:
                    self.toggle_shadow()

            if event.type == pg.KEYDOWN and event.key == pg.K_BACKQUOTE:
                visible = not pg.mouse.get_visible()
                pg.mouse.set_visible(visible)
                pg.event.set_grab(not visible)

            if event.type == pg.MOUSEBUTTONDOWN and self.camera.use_orbit:
                if event.button == 4:
                    self.camera.orbit_radius = max(2.0, self.camera.orbit_radius - 0.5)
                elif event.button == 5:
                    self.camera.orbit_radius = min(40.0, self.camera.orbit_radius + 0.5)

    def render(self):
        if not self.game_started:
            self.ctx.screen.use()
            self.ctx.viewport = (0, 0, self.WIN_SIZE[0], self.WIN_SIZE[1])
            self.ctx.clear(color=(0.02, 0.03, 0.05))
            self.hud.render(show_panel=False)
            pg.display.flip()
            return

        self.post_processor.begin()
        self.ctx.clear(color=self.background_color)
        self.scene_renderer.render()
        self.season_controller.render_transition_effects()
        self.post_processor.render()
        if self.hud_visible or self.paused or self.startup_overlay_alpha() > 0.0:
            self.hud.render(show_panel=self.hud_visible)
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
            if self.game_started and not self.paused:
                self.season_controller.update(self.delta_time)
                self.camera.update()
            self.render()
            self.delta_time = self.clock.tick(60)
            if self.game_started:
                self.update_frame_stats()
                self.update_adaptive_quality()
