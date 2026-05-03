import pygame as pg
import moderngl as mgl
import numpy as np

from .paths import SHADER_DIR


class HUD:
    def __init__(self, app, size=(490, 236), margin=14):
        self.app = app
        self.ctx = app.ctx
        self.size = size
        self.margin = margin
        self.refresh_interval = 0.15
        self.last_refresh = -999.0
        self.texture = None
        self.pause_texture = None

        self.font = pg.font.Font(None, 19)
        self.small_font = pg.font.Font(None, 17)
        self.title_font = pg.font.Font(None, 42)
        self.program = self.load_program()
        self.vbo = self.ctx.buffer(self.quad_vertices().astype("f4").tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f 2f", "in_position", "in_uv")],
        )
        self.pause_vbo = self.ctx.buffer(self.pause_vertices().astype("f4").tobytes())
        self.pause_vao = self.ctx.vertex_array(
            self.program,
            [(self.pause_vbo, "2f 2f", "in_position", "in_uv")],
        )
        self.program["u_texture"].value = 0

    def load_program(self):
        vertex_path = SHADER_DIR / "hud_shader.vert"
        fragment_path = SHADER_DIR / "hud_shader.frag"
        with open(vertex_path, "r", encoding="utf-8") as file:
            vertex_shader = file.read()
        with open(fragment_path, "r", encoding="utf-8") as file:
            fragment_shader = file.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

    def quad_vertices(self):
        width, height = self.app.WIN_SIZE
        panel_w, panel_h = self.size
        left = -1.0 + (self.margin / width) * 2.0
        right = left + (panel_w / width) * 2.0
        top = 1.0 - (self.margin / height) * 2.0
        bottom = top - (panel_h / height) * 2.0
        return np.array(
            [
                (left, top, 0.0, 1.0),
                (left, bottom, 0.0, 0.0),
                (right, bottom, 1.0, 0.0),
                (left, top, 0.0, 1.0),
                (right, bottom, 1.0, 0.0),
                (right, top, 1.0, 1.0),
            ],
            dtype="f4",
        )

    def pause_vertices(self):
        width, height = self.app.WIN_SIZE
        panel_w = min(460, width - 48)
        panel_h = 218
        left = -panel_w / width
        right = panel_w / width
        top = panel_h / height
        bottom = -panel_h / height
        return np.array(
            [
                (left, top, 0.0, 1.0),
                (left, bottom, 0.0, 0.0),
                (right, bottom, 1.0, 0.0),
                (left, top, 0.0, 1.0),
                (right, bottom, 1.0, 0.0),
                (right, top, 1.0, 1.0),
            ],
            dtype="f4",
        )

    def fit_text(self, text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text

        ellipsis = "..."
        while text and font.size(text + ellipsis)[0] > max_width:
            text = text[:-1]
        return text + ellipsis

    def hud_lines(self):
        season_controller = self.app.season_controller
        day_state = season_controller.day_state()
        hour = int((season_controller.day_time * 24.0) % 24.0)
        minute = int(((season_controller.day_time * 24.0) % 1.0) * 60.0)
        period = (
            "Malam"
            if day_state["night"] > 0.55
            else "Senja/Pagi"
            if day_state["dusk"] > 0.45
            else "Siang"
        )
        weather = season_controller.current.get(
            "weather_label",
            "Hujan" if season_controller.current.get("rain_enabled", False) else "Cerah",
        )
        special_effect = season_controller.current.get("special_effect_label", "Season scene")
        if season_controller.is_transitioning:
            season_progress = f"Transisi {season_controller.transition_progress * 100:0.0f}%"
        elif season_controller.time_lapse_enabled:
            season_progress = f"Progress {season_controller.elapsed / season_controller.season_duration * 100:0.0f}%"
        else:
            season_progress = "Progress manual"
        season_mode = "Auto musim" if season_controller.time_lapse_enabled else "Musim manual"
        day_mode = "Auto hari" if season_controller.day_cycle_enabled else "Hari manual"
        camera_mode = self.app.camera.preset_name.title()
        screenshot = self.app.last_screenshot_path or "F2 screenshot"
        quality = self.app.quality.name
        fps = self.app.clock.get_fps()

        lines = [
            f"{season_controller.current['name']} | {period} {hour:02d}:{minute:02d}",
            f"Suhu {season_controller.temperature_c:0.1f} C | {weather} | FPS {fps:0.0f}",
            f"{season_progress} | {special_effect}",
            f"Camera {camera_mode} | Quality {quality} | {season_mode}",
            f"{screenshot} | {self.app.audio.status}",
        ]
        if self.app.profile_visible:
            stats = self.app.render_stats
            lines.extend(
                [
                    (
                        f"Objects {stats.get('visible', stats.get('objects', 0))}/{stats.get('objects', 0)} | "
                        f"Cull {stats.get('culled', 0)} | Draw {stats.get('draw_calls', 0)} | "
                        f"Inst {stats.get('instanced_objects', 0)}/{stats.get('instanced_batches', 0)}"
                    ),
                    (
                        f"Shadow {stats.get('shadow_casters', 0)} casters @ {stats.get('shadow_size', 0)} | "
                        f"Post {'ON' if self.app.post_processor.enabled else 'OFF'} | "
                        f"Map {'ON' if self.app.scene_renderer.shadow_renderer.enabled else 'OFF'}"
                    ),
                    f"FPS avg {self.app.fps_avg:0.1f} | min {self.app.fps_min:0.1f} | {self.app.adaptive_quality_status}",
                ]
            )
        if self.app.editor.enabled:
            selected = self.app.editor.selected()
            position = "No position"
            if selected is not None:
                position = f"pos {selected.pos.x:0.2f}, {selected.pos.y:0.2f}, {selected.pos.z:0.2f}"
            lines.extend(
                [
                    f"Editor {self.app.editor.selected_label()} | {position}",
                    "Arrows move X/Z | PgUp/PgDn Y | [ ] select | F4 dump",
                ]
            )
        return lines

    def update_texture(self):
        surface = pg.Surface(self.size, flags=pg.SRCALPHA)
        pg.draw.rect(surface, (11, 16, 21, 174), surface.get_rect(), border_radius=8)
        pg.draw.rect(surface, (232, 238, 244, 56), surface.get_rect(), width=1, border_radius=8)

        x = 14
        y = 12
        max_width = self.size[0] - x * 2
        for idx, line in enumerate(self.hud_lines()):
            font = self.font if idx == 0 else self.small_font
            color = (246, 249, 252) if idx == 0 else (210, 220, 226)
            text = self.fit_text(line, font, max_width)
            surface.blit(font.render(text, True, color), (x, y))
            y += 24 if idx == 0 else 21

        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.texture is not None:
            self.texture.release()
        self.texture = self.ctx.texture(self.size, 4, data)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def update_pause_texture(self):
        size = (460, 218)
        surface = pg.Surface(size, flags=pg.SRCALPHA)
        pg.draw.rect(surface, (10, 14, 18, 218), surface.get_rect(), border_radius=10)
        pg.draw.rect(surface, (236, 242, 246, 70), surface.get_rect(), width=1, border_radius=10)

        title = self.title_font.render("Paused", True, (250, 252, 255))
        surface.blit(title, (24, 22))
        lines = [
            "Esc resume",
            "Q exit",
            "F2 screenshot | F3 editor | F5-F8 camera | F9 quality",
            "F10 profile | F11 fullscreen | F12 post | F4 shadow/editor dump",
        ]
        y = 76
        for line in lines:
            text = self.fit_text(line, self.font, size[0] - 48)
            surface.blit(self.font.render(text, True, (214, 224, 230)), (24, y))
            y += 28

        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.pause_texture is not None:
            self.pause_texture.release()
        self.pause_texture = self.ctx.texture(size, 4, data)
        self.pause_texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def render(self):
        if self.app.time - self.last_refresh >= self.refresh_interval or self.texture is None:
            self.update_texture()
            self.last_refresh = self.app.time

        self.ctx.disable(mgl.DEPTH_TEST)
        self.texture.use(location=0)
        self.vao.render()
        if self.app.paused:
            if self.pause_texture is None:
                self.update_pause_texture()
            self.pause_texture.use(location=0)
            self.pause_vao.render()
        self.ctx.enable(mgl.DEPTH_TEST)

    def resize(self):
        self.vbo.write(self.quad_vertices().astype("f4").tobytes())
        self.pause_vbo.write(self.pause_vertices().astype("f4").tobytes())
        self.last_refresh = -999.0

    def destroy(self):
        if self.texture is not None:
            self.texture.release()
        if self.pause_texture is not None:
            self.pause_texture.release()
        self.vao.release()
        self.pause_vao.release()
        self.vbo.release()
        self.pause_vbo.release()
        self.program.release()
