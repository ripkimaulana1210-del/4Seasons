import math

import pygame as pg
import moderngl as mgl
import numpy as np

from .paths import SHADER_DIR


class HUD:
    def __init__(self, app, size=(520, 260), margin=14):
        self.app = app
        self.ctx = app.ctx
        self.size = size
        self.margin = margin
        self.refresh_interval = 0.15
        self.last_refresh = -999.0
        self.texture = None
        self.pause_texture = None
        self.startup_texture = None

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
        self.startup_vbo = self.ctx.buffer(self.fullscreen_vertices().astype("f4").tobytes())
        self.startup_vao = self.ctx.vertex_array(
            self.program,
            [(self.startup_vbo, "2f 2f", "in_position", "in_uv")],
        )
        self.program["u_texture"].value = 0
        self.program["u_alpha"].value = 1.0

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
        panel_w, panel_h = self.pause_panel_size()
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

    def pause_panel_size(self):
        width, height = self.app.WIN_SIZE
        panel_w = min(760, max(420, width - 48))
        panel_h = min(420, max(260, height - 48))
        return int(panel_w), int(panel_h)

    def fullscreen_vertices(self):
        return np.array(
            [
                (-1.0, 1.0, 0.0, 1.0),
                (-1.0, -1.0, 0.0, 0.0),
                (1.0, -1.0, 1.0, 0.0),
                (-1.0, 1.0, 0.0, 1.0),
                (1.0, -1.0, 1.0, 0.0),
                (1.0, 1.0, 1.0, 1.0),
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
        season = season_controller.get_blended_season()
        period = (
            "Malam"
            if day_state["night"] > 0.55
            else "Senja/Pagi"
            if day_state["dusk"] > 0.45
            else "Siang"
        )
        weather = season.get(
            "weather_label",
            "Hujan" if season.get("rain_enabled", False) else "Cerah",
        )
        special_effect = season.get("special_effect_label", "Season scene")
        if season_controller.is_transitioning:
            transition = season_controller.transition_snapshot()
            season_progress = f"Transisi {season_controller.transition_progress * 100:0.0f}%"
            if transition["pair"] == "winter->spring":
                special_effect = (
                    f"Cair {transition['melt_intensity'] * 100:0.0f}% | "
                    f"Tunas {transition['sprout_intensity'] * 100:0.0f}% | "
                    f"Mekar {transition['bloom_intensity'] * 100:0.0f}%"
                )
            else:
                special_effect = transition["story"]
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
        if season_controller.is_transitioning:
            timeline = season_controller.transition_snapshot().get("timeline", [])
            if timeline:
                stages = []
                for item in timeline[:5]:
                    mark = ">" if item["active"] else "*" if item["done"] else "-"
                    stages.append(f"{mark}{item['label']} {item['progress'] * 100:0.0f}%")
                lines.insert(3, "Timeline " + " | ".join(stages))
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
        size = self.pause_panel_size()
        surface = pg.Surface(size, flags=pg.SRCALPHA)
        pg.draw.rect(surface, (10, 14, 18, 218), surface.get_rect(), border_radius=10)
        pg.draw.rect(surface, (236, 242, 246, 70), surface.get_rect(), width=1, border_radius=10)

        title = self.title_font.render("Paused", True, (250, 252, 255))
        surface.blit(title, (24, 16))
        lines = [
            "Esc pause/resume | Q exit saat pause | Enter/Space skip intro",
            "W/A/S/D gerak | Q/E turun-naik | Mouse lihat | Shift cepat | Ctrl pelan",
            "Tab free/orbit | Mouse wheel zoom | ` mouse grab | C cinematic",
            "1-4 pilih musim | N/P next-prev | T auto musim | X stop auto musim",
            "Y auto hari | J/K geser jam | L malam | O pagi | +/- speed",
            "M mute | H HUD | F1 preset musim | F2 screenshot",
            "F3 editor | F4 shadow (normal) / dump transform (editor)",
            "F5 sakura | F6 bridge | F7 village | F8 fuji",
            "F9 quality | F10 profile | F11 fullscreen | F12 post",
            "Editor ON: [/] pilih objek | Arrows X/Z | PgUp/PgDn Y",
        ]
        y = 66
        line_step = 22 if size[1] >= 360 else 20
        for line in lines:
            text = self.fit_text(line, self.small_font, size[0] - 48)
            surface.blit(self.small_font.render(text, True, (214, 224, 230)), (24, y))
            y += line_step

        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.pause_texture is not None:
            self.pause_texture.release()
        self.pause_texture = self.ctx.texture(size, 4, data)
        self.pause_texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def update_startup_texture(self):
        width, height = self.app.WIN_SIZE
        surface = pg.Surface((width, height), flags=pg.SRCALPHA)
        surface.fill((5, 8, 13, 226))

        season_specs = [
            ("SPRING", (255, 128, 184)),
            ("SUMMER", (255, 196, 58)),
            ("AUTUMN", (224, 92, 34)),
            ("WINTER", (150, 210, 255)),
        ]
        band_w = width / 4.0
        for idx, (_name, color) in enumerate(season_specs):
            left = int(idx * band_w)
            rect = pg.Rect(left, 0, int(band_w) + 2, height)
            pg.draw.rect(surface, (*color, 30), rect)
            pg.draw.rect(surface, (*color, 72), (left, height - 8, int(band_w) + 2, 8))

        center = (width // 2, height // 2)
        min_dim = min(width, height)
        ring_size = max(190, int(min_dim * 0.42))
        ring_rect = pg.Rect(0, 0, ring_size, ring_size)
        ring_rect.center = (center[0], center[1] - int(min_dim * 0.035))
        arc_width = max(6, int(min_dim * 0.014))
        for idx, (_name, color) in enumerate(season_specs):
            start = -math.pi / 2.0 + idx * math.pi / 2.0
            pg.draw.arc(surface, (*color, 220), ring_rect, start, start + math.pi / 2.0, arc_width)

        glow_rect = ring_rect.inflate(int(min_dim * 0.10), int(min_dim * 0.10))
        pg.draw.ellipse(surface, (255, 255, 255, 18), glow_rect, width=max(2, arc_width // 2))
        pg.draw.ellipse(surface, (12, 18, 26, 132), ring_rect.inflate(-arc_width * 3, -arc_width * 3))

        def fitted_font(text, start_size, max_width, min_size=22):
            size = start_size
            font = pg.font.Font(None, size)
            while size > min_size and font.size(text)[0] > max_width:
                size -= 3
                font = pg.font.Font(None, size)
            return font

        def blit_centered(text, font, y, color, shadow=(0, 0, 0, 130)):
            text_surface = font.render(text, True, color)
            shadow_surface = font.render(text, True, shadow)
            rect = text_surface.get_rect(center=(center[0], y))
            for offset in ((2, 2), (-1, 2), (2, -1)):
                surface.blit(shadow_surface, rect.move(offset))
            surface.blit(text_surface, rect)
            return rect

        title_font = fitted_font("4 SEASONS", int(min_dim * 0.155), int(width * 0.78), min_size=44)
        subtitle_font = fitted_font("SAKURA SEASONAL SCENE", int(min_dim * 0.038), int(width * 0.72), min_size=18)
        title_y = center[1] - int(min_dim * 0.065)
        blit_centered("4 SEASONS", title_font, title_y, (250, 253, 255))
        blit_centered("SAKURA SEASONAL SCENE", subtitle_font, title_y + int(min_dim * 0.082), (208, 224, 232), shadow=(0, 0, 0, 100))

        chip_font = fitted_font("SPRING", int(min_dim * 0.030), max(92, int(width * 0.13)), min_size=15)
        chip_y = min(height - 54, center[1] + int(min_dim * 0.205))
        chip_gap = max(8, int(width * 0.012))
        chip_w = min(138, max(86, int((width - chip_gap * 5) / 4.8)))
        chip_h = max(28, int(min_dim * 0.044))
        total_w = chip_w * 4 + chip_gap * 3
        start_x = center[0] - total_w // 2
        for idx, (name, color) in enumerate(season_specs):
            rect = pg.Rect(start_x + idx * (chip_w + chip_gap), chip_y, chip_w, chip_h)
            pg.draw.rect(surface, (*color, 72), rect, border_radius=6)
            pg.draw.rect(surface, (*color, 185), rect, width=1, border_radius=6)
            text = chip_font.render(name, True, (246, 250, 252))
            surface.blit(text, text.get_rect(center=rect.center))

        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.startup_texture is not None:
            self.startup_texture.release()
        self.startup_texture = self.ctx.texture((width, height), 4, data)
        self.startup_texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def render(self):
        if self.app.time - self.last_refresh >= self.refresh_interval or self.texture is None:
            self.update_texture()
            self.last_refresh = self.app.time

        self.ctx.disable(mgl.DEPTH_TEST)
        self.program["u_alpha"].value = 1.0
        self.texture.use(location=0)
        self.vao.render()
        if self.app.paused:
            if self.pause_texture is None:
                self.update_pause_texture()
            self.pause_texture.use(location=0)
            self.pause_vao.render()
        startup_alpha = self.app.startup_overlay_alpha()
        if startup_alpha > 0.0:
            if self.startup_texture is None:
                self.update_startup_texture()
            self.program["u_alpha"].value = max(0.0, min(1.0, startup_alpha))
            self.startup_texture.use(location=0)
            self.startup_vao.render()
            self.program["u_alpha"].value = 1.0
        self.ctx.enable(mgl.DEPTH_TEST)

    def resize(self):
        self.vbo.write(self.quad_vertices().astype("f4").tobytes())
        self.pause_vbo.write(self.pause_vertices().astype("f4").tobytes())
        self.startup_vbo.write(self.fullscreen_vertices().astype("f4").tobytes())
        self.last_refresh = -999.0
        if self.pause_texture is not None:
            self.pause_texture.release()
            self.pause_texture = None
        if self.startup_texture is not None:
            self.startup_texture.release()
            self.startup_texture = None

    def destroy(self):
        if self.texture is not None:
            self.texture.release()
        if self.pause_texture is not None:
            self.pause_texture.release()
        if self.startup_texture is not None:
            self.startup_texture.release()
        self.vao.release()
        self.pause_vao.release()
        self.startup_vao.release()
        self.vbo.release()
        self.pause_vbo.release()
        self.startup_vbo.release()
        self.program.release()
