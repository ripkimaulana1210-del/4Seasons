import sys
import pygame as pg
import moderngl as mgl

from .audio_manager import AudioManager
from .camera import Camera
from .mesh import Mesh
from .point_light import PointLight
from .scene import Scene
from .scene_renderer import SceneRenderer
from .season_controller import SeasonController


class SxvxnEngine:
    def __init__(self, win_size=(1280, 720)):
        pg.init()
        pg.display.set_caption("Modern GL Basics")
        self.WIN_SIZE = win_size

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)

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
        self.audio = AudioManager()

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
        self.mesh = Mesh(self)
        self.scene = Scene(self)
        self.scene_renderer = SceneRenderer(self)
        self.audio.apply_season(season)
        self.season_controller.update_caption(force=True)

    def apply_season(self):
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

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                self.destroy()
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                self.camera.use_orbit = not self.camera.use_orbit
                self.camera.set_default()

            if event.type == pg.KEYDOWN:
                self.season_controller.handle_key(event.key)

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
        self.ctx.clear(color=self.background_color)
        self.scene_renderer.render()
        pg.display.flip()

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def destroy(self):
        self.mesh.destroy()
        self.scene_renderer.destroy()
        self.audio.destroy()

    def run(self):
        while True:
            self.get_time()
            self.check_events()
            self.season_controller.update(self.delta_time)
            self.camera.update()
            self.render()
            self.delta_time = self.clock.tick(60)
