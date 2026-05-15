import math

import pygame as pg
import moderngl as mgl
import numpy as np

from ..core.paths import SHADER_DIR
from ..systems.season_transition_manager import transition_effect_family
from .main_menu import MainMenu


SEASON_HUD = {
    "spring": {"accent": (255, 132, 184), "icon": "sakura"},
    "early_spring": {"accent": (176, 220, 196), "icon": "sprout"},
    "hanami": {"accent": (255, 152, 202), "icon": "sakura"},
    "tsuyu": {"accent": (116, 178, 220), "icon": "rain"},
    "summer": {"accent": (255, 196, 58), "icon": "sun"},
    "midsummer": {"accent": (255, 174, 54), "icon": "sun"},
    "late_summer": {"accent": (232, 178, 90), "icon": "leaf"},
    "autumn": {"accent": (220, 112, 48), "icon": "leaf"},
    "momiji": {"accent": (236, 84, 52), "icon": "leaf"},
    "first_frost": {"accent": (162, 206, 226), "icon": "snow"},
    "winter": {"accent": (120, 204, 255), "icon": "snow"},
    "deep_winter": {"accent": (166, 212, 255), "icon": "snow"},
}


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


class HUD:
    def __init__(self, app, size=(560, 286), margin=14):
        self.app = app
        self.ctx = app.ctx
        self.size = size
        self.margin = margin
        self.refresh_interval = 0.15
        self.last_refresh = -999.0
        self.texture = None
        self.pause_texture = None
        self.startup_texture = None
        self.startup_hover_token = None
        self.startup_last_refresh = -999.0
        self.main_menu = MainMenu(app)

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

    def season_style(self, season):
        return SEASON_HUD.get(season.get("id"), {"accent": (232, 238, 244), "icon": "sakura"})

    def draw_icon(self, surface, icon, center, color, size):
        x, y = center
        if icon == "sakura":
            for angle in range(0, 360, 72):
                vx = x + math.cos(math.radians(angle)) * size * 0.32
                vy = y + math.sin(math.radians(angle)) * size * 0.32
                pg.draw.circle(surface, (*color, 230), (int(vx), int(vy)), max(3, int(size * 0.16)))
            pg.draw.circle(surface, (255, 235, 246, 240), (x, y), max(2, int(size * 0.10)))
        elif icon == "sun":
            for angle in range(0, 360, 45):
                sx = x + math.cos(math.radians(angle)) * size * 0.34
                sy = y + math.sin(math.radians(angle)) * size * 0.34
                ex = x + math.cos(math.radians(angle)) * size * 0.56
                ey = y + math.sin(math.radians(angle)) * size * 0.56
                pg.draw.aaline(surface, (*color, 220), (sx, sy), (ex, ey))
            pg.draw.circle(surface, (*color, 235), (x, y), max(5, int(size * 0.25)))
        elif icon == "leaf":
            points = [(x, y - size // 2), (x + size // 2, y), (x, y + size // 2), (x - size // 3, y)]
            pg.draw.polygon(surface, (*color, 230), points)
            pg.draw.aaline(surface, (255, 226, 185, 220), (x - size // 4, y), (x + size // 3, y))
        elif icon == "rain":
            cloud = pg.Rect(x - size // 2, y - size // 4, size, size // 2)
            pg.draw.ellipse(surface, (*color, 210), cloud)
            for offset in (-size // 4, 0, size // 4):
                pg.draw.aaline(surface, (*color, 230), (x + offset, y + size * 0.20), (x + offset - 4, y + size * 0.48))
        elif icon == "sprout":
            pg.draw.aaline(surface, (*color, 230), (x, y + size * 0.42), (x, y - size * 0.18))
            left = [(x, y - size * 0.05), (x - size * 0.38, y - size * 0.25), (x - size * 0.14, y + size * 0.12)]
            right = [(x, y - size * 0.12), (x + size * 0.38, y - size * 0.32), (x + size * 0.14, y + size * 0.07)]
            pg.draw.polygon(surface, (*color, 220), left)
            pg.draw.polygon(surface, (*color, 220), right)
        elif icon == "snow":
            for angle in range(0, 180, 60):
                dx = math.cos(math.radians(angle)) * size * 0.45
                dy = math.sin(math.radians(angle)) * size * 0.45
                pg.draw.aaline(surface, (*color, 230), (x - dx, y - dy), (x + dx, y + dy))
            pg.draw.circle(surface, (236, 250, 255, 230), (x, y), max(2, int(size * 0.10)))
        else:
            pg.draw.circle(surface, (*color, 230), (x, y), max(5, int(size * 0.25)))

    def draw_progress_bar(self, surface, rect, amount, color):
        amount = clamp(amount, 0.0, 1.0)
        pg.draw.rect(surface, (28, 34, 42, 220), rect, border_radius=rect.height // 2)
        fill = pg.Rect(rect.x, rect.y, max(rect.height, int(rect.width * amount)), rect.height)
        pg.draw.rect(surface, (*color, 210), fill, border_radius=rect.height // 2)

    def draw_chip(self, surface, rect, text, color):
        pg.draw.rect(surface, (13, 18, 25, 216), rect, border_radius=rect.height // 2)
        pg.draw.rect(surface, (*color, 86), rect, width=1, border_radius=rect.height // 2)
        label = self.fit_text(text, self.small_font, rect.width - 14)
        rendered = self.small_font.render(label, True, (232, 238, 244))
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    def draw_day_clock(self, surface, center, radius, phase, accent, night_amount):
        pg.draw.circle(surface, (42, 48, 56, 220), center, radius)
        pg.draw.circle(surface, (8, 13, 20, 170), center, radius - 2)
        start = -90
        end = start + int(360 * phase)
        if end != start:
            pg.draw.arc(surface, (*accent, 230), (center[0] - radius, center[1] - radius, radius * 2, radius * 2), math.radians(start), math.radians(end), 3)
        sun_y = center[1] + int(math.sin(phase * math.tau - math.pi * 0.5) * radius * 0.42)
        sun_x = center[0] + int(math.cos(phase * math.tau - math.pi * 0.5) * radius * 0.42)
        body = (178, 205, 236) if night_amount > 0.45 else (255, 210, 92)
        pg.draw.circle(surface, (*body, 240), (sun_x, sun_y), max(4, radius // 5))

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
            if transition_effect_family(transition["pair"]) == "winter->spring":
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

    def hud_state(self):
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
        if season_controller.is_transitioning:
            snapshot = season_controller.transition_snapshot()
            season_progress = season_controller.transition_progress
            progress_label = f"Transisi {season_progress * 100:0.0f}%"
            detail = snapshot["story"]
        elif season_controller.time_lapse_enabled:
            season_progress = season_controller.elapsed / max(0.001, season_controller.season_duration)
            progress_label = f"Musim {season_progress * 100:0.0f}%"
            detail = season.get("special_effect_label", season.get("emotion_title", "Season scene"))
        else:
            season_progress = 1.0
            progress_label = "Manual"
            detail = season.get("special_effect_label", season.get("emotion_title", "Season scene"))

        return {
            "season": season,
            "style": self.season_style(season),
            "day_state": day_state,
            "time": f"{hour:02d}:{minute:02d}",
            "period": period,
            "weather": weather,
            "season_progress": season_progress,
            "progress_label": progress_label,
            "detail": detail,
            "temperature": season_controller.temperature_c,
            "season_mode": "AUTO" if season_controller.time_lapse_enabled else "MANUAL",
            "day_mode": "AUTO" if season_controller.day_cycle_enabled else "MANUAL",
            "camera": self.app.camera.preset_name.title(),
            "quality": self.app.quality.name,
            "fps": self.app.clock.get_fps(),
            "audio": self.app.audio.status,
        }

    def draw_hud_surface(self):
        surface = pg.Surface(self.size, flags=pg.SRCALPHA)
        state = self.hud_state()
        accent = state["style"]["accent"]
        rect = surface.get_rect()

        pg.draw.rect(surface, (8, 12, 18, 184), rect, border_radius=8)
        pg.draw.rect(surface, (232, 238, 244, 58), rect, width=1, border_radius=8)
        pg.draw.rect(surface, (*accent, 150), (0, 0, 5, rect.height), border_radius=4)

        name = state["season"].get("name", "Season")
        title = self.fit_text(name.upper(), self.title_font, 270)
        surface.blit(self.title_font.render(title, True, (248, 251, 253)), (58, 16))
        self.draw_icon(surface, state["style"]["icon"], (31, 35), accent, 34)
        surface.blit(self.small_font.render(state["progress_label"], True, (214, 224, 230)), (60, 58))
        self.draw_progress_bar(surface, pg.Rect(60, 80, 252, 9), state["season_progress"], accent)

        detail = self.fit_text(state["detail"], self.small_font, 300)
        surface.blit(self.small_font.render(detail, True, (196, 210, 218)), (16, 104))

        time_panel = pg.Rect(332, 14, 210, 96)
        pg.draw.rect(surface, (13, 18, 25, 212), time_panel, border_radius=8)
        pg.draw.rect(surface, (255, 255, 255, 38), time_panel, width=1, border_radius=8)
        self.draw_day_clock(surface, (374, 62), 28, state["day_state"]["phase"], accent, state["day_state"]["night"])
        surface.blit(self.title_font.render(state["time"], True, (248, 251, 253)), (414, 27))
        sub = f"{state['period']} | {state['weather']}"
        surface.blit(self.small_font.render(self.fit_text(sub, self.small_font, 114), True, (202, 214, 222)), (416, 70))

        temp = f"{state['temperature']:0.1f} C"
        self.draw_chip(surface, pg.Rect(16, 136, 96, 28), temp, accent)
        self.draw_chip(surface, pg.Rect(120, 136, 102, 28), f"FPS {state['fps']:0.0f}", (132, 214, 160))
        self.draw_chip(surface, pg.Rect(230, 136, 128, 28), f"Quality {state['quality']}", (186, 198, 232))
        self.draw_chip(surface, pg.Rect(366, 136, 84, 28), state["season_mode"], accent)
        self.draw_chip(surface, pg.Rect(458, 136, 84, 28), f"Day {state['day_mode']}", (152, 204, 232))

        status_text = f"Camera {state['camera']} | Audio {state['audio']}"
        surface.blit(self.small_font.render(self.fit_text(status_text, self.small_font, 510), True, (210, 220, 226)), (16, 180))

        controls = "H HUD  |  Esc Pause  |  1-4 Season  |  F1 Camera  |  F9 Quality  |  F10 Stats"
        surface.blit(self.small_font.render(self.fit_text(controls, self.small_font, 510), True, (172, 188, 198)), (16, 204))

        y = 232
        if self.app.profile_visible:
            stats = self.app.render_stats
            profile = (
                f"Draw {stats.get('draw_calls', 0)} | Obj {stats.get('visible', stats.get('objects', 0))}/"
                f"{stats.get('objects', 0)} | Avg {self.app.fps_avg:0.1f} | {self.app.adaptive_quality_status}"
            )
            surface.blit(self.small_font.render(self.fit_text(profile, self.small_font, 510), True, (190, 202, 210)), (16, y))
            y += 20
        if self.app.editor.enabled:
            selected = self.app.editor.selected_label()
            editor = f"Editor {selected} | Arrows X/Z | PgUp/PgDn Y | [ ] select"
            surface.blit(self.small_font.render(self.fit_text(editor, self.small_font, 510), True, (238, 218, 168)), (16, y))

        return surface

    def update_texture(self):
        surface = self.draw_hud_surface()

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
            "Esc pause/resume | Q exit saat pause",
            "W/A/S/D gerak | Q/E turun-naik | Mouse lihat | Shift cepat | Ctrl pelan",
            "Tab free/orbit | Mouse wheel zoom | ` mouse grab | C cinematic",
            "1-4 utama | 5-0 micro | Shift+1-0/[ ] pilih | N/P next-prev",
            "T auto musim | X stop auto musim | +/- speed",
            "Y auto hari | J/K geser jam | L malam | O pagi",
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

    def invalidate_startup_texture(self):
        if self.startup_texture is not None:
            self.startup_texture.release()
            self.startup_texture = None
        self.startup_last_refresh = -999.0

    def play_button_rect(self):
        return self.main_menu.play_button_rect()

    def upload_startup_texture(self, surface):
        width, height = self.app.WIN_SIZE
        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.startup_texture is not None:
            self.startup_texture.release()
        self.startup_texture = self.ctx.texture((width, height), 4, data)
        self.startup_texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def handle_menu_input(self, event):
        return self.main_menu.handle_menu_input(event)

    def update_startup_texture(self):
        delta_s = self.app.delta_time * 0.001 if self.app.delta_time > 0 else 1.0 / 60.0
        surface = self.main_menu.render_surface(delta_s)
        self.startup_hover_token = self.main_menu.hover_token()
        self.startup_last_refresh = self.app.time
        self.upload_startup_texture(surface)

    def render(self, show_panel=True):
        if show_panel and (self.app.time - self.last_refresh >= self.refresh_interval or self.texture is None):
            self.update_texture()
            self.last_refresh = self.app.time

        self.ctx.disable(mgl.DEPTH_TEST)
        self.program["u_alpha"].value = 1.0
        if show_panel and self.texture is not None:
            self.texture.use(location=0)
            self.vao.render()
        if self.app.paused:
            if self.pause_texture is None:
                self.update_pause_texture()
            self.pause_texture.use(location=0)
            self.pause_vao.render()
        startup_alpha = self.app.startup_overlay_alpha()
        if startup_alpha > 0.0:
            hover_token = self.main_menu.hover_token()
            needs_refresh = self.app.time - self.startup_last_refresh >= 1.0 / 30.0
            if self.startup_texture is None or hover_token != self.startup_hover_token or needs_refresh:
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
        self.startup_last_refresh = -999.0
        self.main_menu.resize()

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
