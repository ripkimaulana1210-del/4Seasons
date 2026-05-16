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


def font_from(names, size, bold=False):
    for name in names:
        try:
            path = pg.font.match_font(name, bold=bold)
            if path:
                return pg.font.Font(path, size)
        except pg.error:
            continue
    return pg.font.Font(None, size)


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
        self.pause_scroll = 0
        self.pause_scroll_max = 0
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

    def pause_panel_rect(self):
        panel_w, panel_h = self.pause_panel_size()
        width, height = self.app.WIN_SIZE
        return pg.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)

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

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            current = word
            while font.size(current)[0] > max_width and len(current) > 1:
                cut = len(current)
                while cut > 1 and font.size(current[:cut] + "...")[0] > max_width:
                    cut -= 1
                lines.append(current[:cut] + "...")
                current = current[cut:]
        if current:
            lines.append(current)
        return lines or [""]

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
        quality = self.app.quality_label()
        fps = self.app.clock.get_fps()

        lines = [
            f"{season_controller.current['name']} | {period} {hour:02d}:{minute:02d}",
            f"Suhu {season_controller.temperature_c:0.1f} C | {weather} | FPS {fps:0.0f}",
            f"{season_progress} | {special_effect}",
            f"Camera {camera_mode} | {quality} | {season_mode}",
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
            "quality": self.app.quality_label(),
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
        self.draw_chip(surface, pg.Rect(230, 136, 128, 28), state["quality"], (186, 198, 232))
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
        panel_rect = surface.get_rect()
        pg.draw.rect(surface, (7, 10, 15, 255), panel_rect, border_radius=10)
        pg.draw.rect(surface, (15, 23, 32, 255), panel_rect.inflate(-10, -10), border_radius=8)
        pg.draw.rect(surface, (236, 242, 246, 150), panel_rect, width=1, border_radius=10)

        screen = getattr(self.app, "pause_screen", "main")
        if screen in ("main", "settings"):
            self.draw_pause_menu(surface)
            self.upload_pause_texture(surface)
            return
        if screen == "audio":
            self.draw_audio_menu(surface)
            self.upload_pause_texture(surface)
            return
        if screen == "graphics":
            self.draw_graphic_menu(surface)
            self.upload_pause_texture(surface)
            return

        title_font = pg.font.Font(None, 46)
        section_font = pg.font.Font(None, 25)
        item_font = pg.font.Font(None, 22)
        hint_font = pg.font.Font(None, 18)
        title = title_font.render("Controls", True, (250, 252, 255))
        surface.blit(title, (24, 16))
        back_rect = self.pause_back_button_rect(size)
        self.draw_pause_button(surface, back_rect, "Back", (232, 238, 244), small=True)
        hint = hint_font.render("Scroll untuk melihat semua kontrol", True, (166, 183, 194))
        surface.blit(hint, hint.get_rect(midtop=(size[0] // 2, 50)))

        sections = [
            (
                "Navigasi Kamera",
                (120, 204, 255),
                [
                    (("W", "A", "S", "D"), "Gerak kamera maju, kiri, mundur, kanan"),
                    (("Q", "E"), "Turun dan naik kamera"),
                    (("Mouse",), "Arah pandang"),
                    (("Shift",), "Gerak lebih cepat"),
                    (("Ctrl",), "Gerak lebih pelan"),
                    (("Tab",), "Toggle free camera / orbit camera"),
                    (("Mouse wheel",), "Zoom saat orbit camera aktif"),
                    (("`",), "Toggle mouse grab"),
                ],
            ),
            (
                "Kontrol Musim",
                (255, 196, 58),
                [
                    (("1", "2", "3", "4"), "Debug transisi visual antar musim utama"),
                    (("5", "6", "7", "8", "9", "0"), "Debug transisi micro-season"),
                    (("Shift", "+", "1-0", "[", "]"), "Pilih musim langsung"),
                    (("N", "P"), "Musim berikutnya / sebelumnya"),
                    (("T",), "Toggle time-lapse musim"),
                    (("X",), "Stop auto musim"),
                    (("+", "-"), "Ubah kecepatan time-lapse"),
                ],
            ),
            (
                "Interaksi Scene",
                (255, 132, 184),
                [
                    (("Y",), "Toggle siklus hari"),
                    (("J", "K"), "Geser jam"),
                    (("L", "O"), "Set malam / pagi"),
                    (("M",), "Mute / unmute audio"),
                    (("C",), "Toggle cinematic tour"),
                    (("F1",), "Camera preset terbaik untuk musim aktif"),
                    (("F2",), "Simpan screenshot"),
                    (("F5", "F6", "F7", "F8"), "Preset kamera sakura, jembatan, desa, Fuji"),
                ],
            ),
            (
                "Menu / Bantuan",
                (232, 238, 244),
                [
                    (("Esc",), "Pause / resume"),
                    (("Q",), "Keluar saat pause menu terbuka"),
                    (("H",), "Toggle HUD"),
                    (("F9",), "Ganti quality Low / Medium / High"),
                    (("F10",), "Toggle profiling overlay"),
                    (("F11",), "Toggle fullscreen"),
                    (("F12",), "Toggle post-processing"),
                ],
            ),
            (
                "Kontrol Tambahan",
                (160, 220, 178),
                [
                    (("F3",), "Toggle scene editor mini"),
                    (("F4",), "Toggle shadow mapping"),
                    (("[", "]"), "Editor: pilih object sebelumnya / berikutnya"),
                    (("Arrow keys",), "Editor: geser object di sumbu X/Z"),
                    (("PgUp", "PgDn"), "Editor: geser object naik / turun"),
                    (("F4",), "Editor aktif: print transform object terpilih"),
                ],
            ),
        ]

        content_rect = pg.Rect(22, 70, size[0] - 44, size[1] - 92)
        content = pg.Surface((content_rect.width, 1), flags=pg.SRCALPHA)

        def draw_keycap(target, rect, label, accent):
            pg.draw.rect(target, (22, 29, 38, 238), rect, border_radius=6)
            pg.draw.rect(target, (*accent, 128), rect, width=1, border_radius=6)
            pg.draw.line(target, (255, 255, 255, 42), (rect.x + 5, rect.y + 3), (rect.right - 5, rect.y + 3))
            rendered = item_font.render(self.fit_text(label, item_font, rect.width - 10), True, (248, 252, 255))
            target.blit(rendered, rendered.get_rect(center=rect.center))

        def append_height(extra_height):
            nonlocal content
            old = content
            content = pg.Surface((content_rect.width, old.get_height() + extra_height), flags=pg.SRCALPHA)
            content.blit(old, (0, 0))

        y = 0
        card_gap = 10
        column_gap = 12
        card_pad_x = 10
        card_pad_y = 10
        key_gap = 6
        key_row_gap = 6
        key_h = 27
        desc_gap = 14
        desc_line_h = 22
        column_count = 1 if content_rect.width < 620 else 2
        column_w = (content_rect.width - column_gap * (column_count - 1) - 10) // column_count

        def keycap_width(label, area_width):
            return max(34, min(area_width, item_font.size(label)[0] + 18))

        def layout_keycaps(keys, area_width):
            rows = []
            row = []
            row_w = 0
            for key in keys:
                key_w = keycap_width(key, area_width)
                next_w = key_w if not row else row_w + key_gap + key_w
                if row and next_w > area_width:
                    rows.append(row)
                    row = [(key, key_w)]
                    row_w = key_w
                else:
                    row.append((key, key_w))
                    row_w = next_w
            if row:
                rows.append(row)
            return rows or [[("", 34)]]

        for title_text, accent, items in sections:
            append_height(40)
            header = section_font.render(title_text, True, (248, 252, 255))
            content.blit(header, (2, y + 6))
            pg.draw.line(content, (*accent, 165), (2, y + 34), (content_rect.width - 12, y + 34), 1)
            y += 44

            column_heights = [y for _ in range(column_count)]
            for index, (keys, description) in enumerate(items):
                column = index % column_count
                x = column * (column_w + column_gap)

                inner_w = column_w - card_pad_x * 2
                key_area_w = int(clamp(inner_w * 0.36, 76, 138))
                if column_count == 1:
                    key_area_w = int(clamp(inner_w * 0.28, 92, 168))
                desc_width = max(96, inner_w - key_area_w - desc_gap)
                key_rows = layout_keycaps(keys, key_area_w)
                desc_lines = self.wrap_text(description, item_font, desc_width)
                key_block_h = len(key_rows) * key_h + max(0, len(key_rows) - 1) * key_row_gap
                desc_block_h = max(1, len(desc_lines)) * desc_line_h
                card_h = max(50, card_pad_y * 2 + max(key_block_h, desc_block_h))
                if column_heights[column] + card_h + card_gap + 16 > content.get_height():
                    append_height(card_h + card_gap + 72)

                card = pg.Rect(x, column_heights[column], column_w, card_h)
                pg.draw.rect(content, (15, 22, 31, 216), card, border_radius=8)
                pg.draw.rect(content, (*accent, 70), card, width=1, border_radius=8)

                key_origin_x = card.x + card_pad_x
                key_y = card.y + card_pad_y
                for row in key_rows:
                    key_x = key_origin_x
                    for key, key_w in row:
                        key_rect = pg.Rect(key_x, key_y, key_w, key_h)
                        draw_keycap(content, key_rect, key, accent)
                        key_x += key_w + key_gap
                    key_y += key_h + key_row_gap

                desc_x = card.x + card_pad_x + key_area_w + desc_gap
                desc_y = card.y + card_pad_y
                if desc_block_h < card_h - card_pad_y * 2:
                    desc_y = card.y + (card_h - desc_block_h) // 2
                for line in desc_lines:
                    content.blit(item_font.render(line, True, (218, 228, 235)), (desc_x, desc_y))
                    desc_y += desc_line_h
                column_heights[column] += card_h + card_gap
            y = max(column_heights) + 12

        content_h = max(1, y)
        self.pause_scroll_max = max(0, content_h - content_rect.height)
        self.pause_scroll = int(clamp(self.pause_scroll, 0, self.pause_scroll_max))

        surface.set_clip(content_rect)
        surface.blit(content, content_rect.topleft, pg.Rect(0, self.pause_scroll, content_rect.width, content_rect.height))
        surface.set_clip(None)

        if self.pause_scroll_max > 0:
            track = pg.Rect(size[0] - 18, content_rect.y, 4, content_rect.height)
            pg.draw.rect(surface, (255, 255, 255, 30), track, border_radius=2)
            thumb_h = max(36, int(content_rect.height * content_rect.height / content_h))
            thumb_y = content_rect.y + int((content_rect.height - thumb_h) * (self.pause_scroll / self.pause_scroll_max))
            thumb = pg.Rect(track.x, thumb_y, track.width, thumb_h)
            pg.draw.rect(surface, (232, 238, 244, 142), thumb, border_radius=2)

        self.upload_pause_texture(surface)

    def upload_pause_texture(self, surface):
        flipped = pg.transform.flip(surface, False, True)
        data = pg.image.tostring(flipped, "RGBA")
        if self.pause_texture is not None:
            self.pause_texture.release()
        self.pause_texture = self.ctx.texture(surface.get_size(), 4, data)
        self.pause_texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def pause_menu_button_rects(self, size=None):
        size = size or self.pause_panel_size()
        width, height = size
        button_w = min(330, width - 96)
        actions = self.pause_menu_actions()
        button_h = 44 if len(actions) >= 5 else 50
        gap = 9 if len(actions) >= 5 else 12
        total_h = button_h * len(actions) + gap * max(0, len(actions) - 1)
        start_y = max(116, int(height * 0.51 - total_h * 0.5))
        x = (width - button_w) // 2
        return {
            action: pg.Rect(x, start_y + index * (button_h + gap), button_w, button_h)
            for index, action in enumerate(actions)
        }

    def pause_menu_actions(self):
        if getattr(self.app, "pause_screen", "main") == "settings":
            return ("controls", "audio", "graphics", "back")
        return ("resume", "controls", "audio", "graphics", "main_menu")

    def pause_back_button_rect(self, size=None):
        size = size or self.pause_panel_size()
        return pg.Rect(size[0] - 118, 18, 92, 34)

    def draw_pause_button(self, surface, rect, label, accent, small=False):
        hovered = rect.collidepoint(self.local_pause_mouse())
        pressed = hovered and pg.mouse.get_pressed(num_buttons=3)[0]
        if pressed:
            fill = (50, 64, 82, 255)
            border_alpha = 245
        elif hovered:
            fill = (43, 57, 74, 255)
            border_alpha = 235
        else:
            fill = (25, 34, 47, 255)
            border_alpha = 172
        shadow = pg.Surface((rect.width + 10, rect.height + 10), pg.SRCALPHA)
        pg.draw.rect(shadow, (0, 0, 0, 150), shadow.get_rect(), border_radius=10)
        surface.blit(shadow, (rect.x - 5, rect.y + 4))
        if hovered:
            glow = pg.Surface((rect.width + 12, rect.height + 12), pg.SRCALPHA)
            pg.draw.rect(glow, (*accent, 44), glow.get_rect(), border_radius=11)
            surface.blit(glow, (rect.x - 6, rect.y - 6))
        pg.draw.rect(surface, fill, rect, border_radius=8)
        inner = pg.Surface(rect.size, pg.SRCALPHA)
        for y in range(rect.height):
            alpha = int(20 * (1.0 - y / max(1, rect.height - 1)))
            pg.draw.line(inner, (255, 255, 255, alpha), (0, y), (rect.width, y))
        surface.blit(inner, rect.topleft)
        pg.draw.rect(surface, (*accent, border_alpha), rect, width=2 if hovered or pressed else 1, border_radius=8)
        pg.draw.rect(surface, (255, 255, 255, 28), rect.inflate(-4, -4), width=1, border_radius=6)
        if hovered:
            pg.draw.rect(surface, (*accent, 190), (rect.x, rect.y, 6, rect.height), border_radius=4)
        font_size = 22 if small else 28
        font = font_from(("segoeuisemibold", "arial", "calibri"), font_size, bold=True)
        shadow_text = font.render(label, True, (0, 0, 0))
        rendered = font.render(label, True, (248, 252, 255))
        surface.blit(shadow_text, shadow_text.get_rect(center=(rect.centerx + 1, rect.centery + 2)))
        surface.blit(rendered, rendered.get_rect(center=rect.center))

    def local_pause_mouse(self):
        panel = self.pause_panel_rect()
        mouse_x, mouse_y = pg.mouse.get_pos()
        return mouse_x - panel.x, mouse_y - panel.y

    def draw_pause_menu(self, surface):
        width, height = surface.get_size()
        title_font = pg.font.Font(None, 58)
        subtitle_font = pg.font.Font(None, 20)
        is_settings = getattr(self.app, "pause_screen", "main") == "settings"
        title_text = "Settings" if is_settings else "Paused"
        title = title_font.render(title_text, True, (250, 252, 255))
        surface.blit(title, title.get_rect(center=(width // 2, 64)))
        subtitle_text = "Control and graphic options" if is_settings else "Four Seasons Garden"
        subtitle = subtitle_font.render(subtitle_text, True, (190, 205, 216))
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, 102)))

        buttons = self.pause_menu_button_rects((width, height))
        labels = {
            "resume": "Resume",
            "controls": "Control",
            "audio": "Audio",
            "graphics": "Graphic",
            "main_menu": "Main Menu",
            "back": "Back",
        }
        accents = {
            "resume": (120, 204, 255),
            "controls": (255, 196, 58),
            "audio": (116, 178, 220),
            "graphics": (160, 220, 178),
            "main_menu": (255, 132, 184),
            "back": (232, 238, 244),
        }
        for action, rect in buttons.items():
            self.draw_pause_button(surface, rect, labels[action], accents[action])

        hint_font = pg.font.Font(None, 18)
        hint_text = "ESC untuk lanjut bermain" if not is_settings else "Back untuk kembali ke menu awal"
        hint = hint_font.render(hint_text, True, (164, 181, 194))
        surface.blit(hint, hint.get_rect(center=(width // 2, height - 34)))

    def audio_slider_rects(self, size=None):
        size = size or self.pause_panel_size()
        width, height = size
        slider_w = min(360, width - 220)
        start_y = int(height * 0.31)
        gap = 48
        x = (width - slider_w) // 2 + 42
        labels = ("master", "music", "sfx", "ambience", "ui")
        return {
            channel: pg.Rect(x, start_y + index * gap, slider_w, 12)
            for index, channel in enumerate(labels)
        }

    def draw_audio_menu(self, surface):
        width, height = surface.get_size()
        title_font = pg.font.Font(None, 50)
        body_font = pg.font.Font(None, 20)
        title = title_font.render("Audio", True, (250, 252, 255))
        surface.blit(title, title.get_rect(center=(width // 2, 58)))
        subtitle = body_font.render("Atur volume tanpa restart aplikasi", True, (190, 205, 216))
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, 94)))

        back_rect = self.pause_back_button_rect((width, height))
        self.draw_pause_button(surface, back_rect, "Back", (232, 238, 244), small=True)

        labels = {
            "master": "Master Volume",
            "music": "Music Volume",
            "sfx": "SFX Volume",
            "ambience": "Ambience Volume",
            "ui": "UI Volume",
        }
        accents = {
            "master": (232, 238, 244),
            "music": (255, 196, 58),
            "sfx": (120, 204, 255),
            "ambience": (160, 220, 178),
            "ui": (255, 132, 184),
        }
        values = self.app.audio.volume_state()
        mouse = self.local_pause_mouse()
        label_font = pg.font.Font(None, 22)
        value_font = pg.font.Font(None, 20)
        for channel, rect in self.audio_slider_rects((width, height)).items():
            value = values[channel]
            accent = accents[channel]
            row_y = rect.y - 18
            label = label_font.render(labels[channel], True, (238, 244, 248))
            surface.blit(label, (rect.x - 42, row_y))
            percent = value_font.render(f"{round(value * 100):d}%", True, (220, 232, 240))
            surface.blit(percent, percent.get_rect(midright=(rect.right + 54, row_y + 10)))

            track_rect = rect.inflate(0, 8)
            hovered = track_rect.collidepoint(mouse)
            pg.draw.rect(surface, (18, 27, 38, 255), track_rect, border_radius=8)
            pg.draw.rect(surface, (255, 255, 255, 62), track_rect, width=1, border_radius=8)
            fill_rect = pg.Rect(track_rect.x, track_rect.y, max(10, int(track_rect.width * value)), track_rect.height)
            pg.draw.rect(surface, (*accent, 240), fill_rect, border_radius=8)
            knob_x = track_rect.x + int(track_rect.width * value)
            knob = pg.Rect(0, 0, 18, 28)
            knob.center = (knob_x, track_rect.centery)
            pg.draw.rect(surface, (246, 250, 252, 255), knob, border_radius=7)
            pg.draw.rect(surface, (*accent, 255 if hovered else 190), knob, width=2, border_radius=7)

        hint = body_font.render("Klik atau drag slider untuk mengubah volume", True, (164, 181, 194))
        surface.blit(hint, hint.get_rect(center=(width // 2, height - 34)))

    def audio_value_from_pos(self, channel, local_pos):
        rect = self.audio_slider_rects().get(channel)
        if rect is None:
            return None
        track_rect = rect.inflate(0, 8)
        return clamp((local_pos[0] - track_rect.x) / max(1, track_rect.width), 0.0, 1.0)

    def handle_audio_drag(self, pos):
        panel = self.pause_panel_rect()
        if not panel.collidepoint(pos):
            return None
        local_pos = (pos[0] - panel.x, pos[1] - panel.y)
        for channel, rect in self.audio_slider_rects().items():
            if rect.inflate(0, 26).collidepoint(local_pos):
                return channel, self.audio_value_from_pos(channel, local_pos)
        return None

    def graphic_option_rects(self, size=None):
        size = size or self.pause_panel_size()
        width, height = size
        card_w = min(142, (width - 118) // 4)
        card_h = 132
        gap = 14
        total_w = card_w * 4 + gap * 3
        x = (width - total_w) // 2
        y = int(height * 0.42)
        return {
            "low": pg.Rect(x, y, card_w, card_h),
            "medium": pg.Rect(x + card_w + gap, y, card_w, card_h),
            "high": pg.Rect(x + (card_w + gap) * 2, y, card_w, card_h),
            "adaptive": pg.Rect(x + (card_w + gap) * 3, y, card_w, card_h),
        }

    def draw_graphic_menu(self, surface):
        width, height = surface.get_size()
        title_font = pg.font.Font(None, 50)
        body_font = pg.font.Font(None, 20)
        title = title_font.render("Graphic", True, (250, 252, 255))
        surface.blit(title, title.get_rect(center=(width // 2, 58)))
        subtitle = body_font.render("Pilih kualitas visual yang nyaman untuk perangkatmu", True, (190, 205, 216))
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, 94)))

        back_rect = self.pause_back_button_rect((width, height))
        self.draw_pause_button(surface, back_rect, "Back", (232, 238, 244), small=True)

        descriptions = {
            "low": ("Low", "Ringan", "Particle dan detail efek lebih hemat."),
            "medium": ("Medium", "Seimbang", "Detail normal untuk gameplay stabil."),
            "high": ("High", "Penuh", "Efek musim dan detail lebih ramai."),
            "adaptive": ("Adaptive", "Auto", "Kualitas berubah otomatis mengikuti FPS."),
        }
        current = self.app.quality.current["id"]
        adaptive_active = getattr(self.app, "adaptive_quality_enabled", False)
        mouse = self.local_pause_mouse()
        for profile_id, rect in self.graphic_option_rects((width, height)).items():
            selected = adaptive_active if profile_id == "adaptive" else (current == profile_id and not adaptive_active)
            hovered = rect.collidepoint(mouse)
            accent = {
                "low": (120, 204, 255),
                "medium": (255, 196, 58),
                "high": (160, 220, 178),
                "adaptive": (255, 132, 184),
            }[profile_id]
            fill = (38, 51, 66, 255) if hovered or selected else (23, 32, 44, 255)
            if selected:
                glow = pg.Surface((rect.width + 12, rect.height + 12), pg.SRCALPHA)
                pg.draw.rect(glow, (*accent, 54), glow.get_rect(), border_radius=11)
                surface.blit(glow, (rect.x - 6, rect.y - 6))
            pg.draw.rect(surface, fill, rect, border_radius=8)
            pg.draw.rect(surface, (*accent, 235 if selected else 150), rect, width=2 if selected else 1, border_radius=8)
            pg.draw.rect(surface, (255, 255, 255, 28), rect.inflate(-4, -4), width=1, border_radius=6)
            name, tag, desc = descriptions[profile_id]
            name_font = pg.font.Font(None, 30)
            tag_font = pg.font.Font(None, 18)
            desc_font = pg.font.Font(None, 18)
            surface.blit(name_font.render(name, True, (250, 252, 255)), (rect.x + 16, rect.y + 18))
            surface.blit(tag_font.render(tag, True, accent), (rect.x + 16, rect.y + 50))
            for index, line in enumerate(self.wrap_text(desc, desc_font, rect.width - 32)[:3]):
                surface.blit(desc_font.render(line, True, (205, 218, 228)), (rect.x + 16, rect.y + 78 + index * 18))

        hint = body_font.render(f"Aktif: {self.app.quality_label()}", True, (218, 230, 238))
        surface.blit(hint, hint.get_rect(center=(width // 2, height - 38)))

    def handle_pause_input(self, event):
        panel = self.pause_panel_rect()
        if not panel.collidepoint(event.pos):
            return "none"

        local_pos = (event.pos[0] - panel.x, event.pos[1] - panel.y)
        screen = getattr(self.app, "pause_screen", "main")
        if screen in ("controls", "audio", "graphics"):
            if self.pause_back_button_rect().collidepoint(local_pos):
                return "back"
            if screen == "audio":
                result = self.handle_audio_drag(event.pos)
                if result is not None:
                    channel, value = result
                    return f"volume:{channel}:{value}"
            if screen == "graphics":
                for profile_id, rect in self.graphic_option_rects().items():
                    if rect.collidepoint(local_pos):
                        return f"quality:{profile_id}"
            return "none"

        for action, rect in self.pause_menu_button_rects().items():
            if rect.collidepoint(local_pos):
                return action
        return "none"

    def reset_pause_texture(self):
        self.invalidate_pause_texture()
        self.pause_scroll = 0
        self.pause_scroll_max = 0

    def invalidate_pause_texture(self):
        if self.pause_texture is not None:
            self.pause_texture.release()
            self.pause_texture = None

    def scroll_pause_help(self, amount):
        if not self.app.paused:
            return
        previous = self.pause_scroll
        self.pause_scroll = int(clamp(self.pause_scroll - amount * 42, 0, self.pause_scroll_max))
        if self.pause_scroll != previous:
            if self.pause_texture is not None:
                self.pause_texture.release()
                self.pause_texture = None

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
        if self.app.paused:
            if self.pause_texture is None:
                self.update_pause_texture()
            self.pause_texture.use(location=0)
            self.pause_vao.render()
        self.ctx.enable(mgl.DEPTH_TEST)

    def resize(self):
        self.vbo.write(self.quad_vertices().astype("f4").tobytes())
        self.pause_vbo.write(self.pause_vertices().astype("f4").tobytes())
        self.startup_vbo.write(self.fullscreen_vertices().astype("f4").tobytes())
        self.last_refresh = -999.0
        if self.pause_texture is not None:
            self.pause_texture.release()
            self.pause_texture = None
        self.pause_scroll = 0
        self.pause_scroll_max = 0
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
