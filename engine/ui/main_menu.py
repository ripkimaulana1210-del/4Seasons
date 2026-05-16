import math
import random

import pygame as pg

from ..core.paths import PROJECT_DIR, UI_DIR


def clamp(value, lower, upper):
    return max(lower, min(upper, value))


def rgba(color, alpha):
    return (*color[:3], alpha)


def font_from(names, size, bold=False):
    for name in names:
        path = pg.font.match_font(name, bold=bold)
        if path:
            return pg.font.Font(path, size)
    return pg.font.Font(None, size)


MENU = {
    "max_width": 1160,
    "bg_paths": (
        UI_DIR / "menu_background.png",
        UI_DIR / "game_cover.png",
        PROJECT_DIR / "docs" / "cover_project_16x9.png",
    ),
    "season_cards": (
        {
            "id": "spring",
            "label": "SEMI",
            "images": (
                UI_DIR / "menu_spring.png",
                PROJECT_DIR / "docs" / "previews" / "season_spring.png",
            ),
            "color": (255, 128, 184),
            "icon": "sakura",
        },
        {
            "id": "summer",
            "label": "PANAS",
            "images": (
                UI_DIR / "menu_summer.png",
                PROJECT_DIR / "docs" / "previews" / "season_summer.png",
            ),
            "color": (255, 196, 58),
            "icon": "sun",
        },
        {
            "id": "autumn",
            "label": "GUGUR",
            "images": (
                UI_DIR / "menu_autumn.png",
                PROJECT_DIR / "docs" / "previews" / "season_autumn.png",
            ),
            "color": (220, 112, 48),
            "icon": "leaf",
        },
        {
            "id": "winter",
            "label": "DINGIN",
            "images": (
                UI_DIR / "menu_winter.png",
                PROJECT_DIR / "docs" / "previews" / "season_winter.png",
            ),
            "color": (120, 204, 255),
            "icon": "snow",
        },
    ),
}


class MainMenu:
    def __init__(self, app):
        self.app = app
        self.background = None
        self.background_path = None
        self.background_loaded = False
        self.season_images = {}
        self.selected_season_id = "spring"
        self.hovered_id = None
        self.hovered_play = False
        self.hovered_settings = False
        self.notice = ""
        self.notice_timer = 0.0
        self.particles = []
        self.rng = random.Random(114)
        self.build_particles()

    def build_particles(self):
        self.particles = []
        colors = (
            (255, 169, 205, 118),
            (255, 224, 142, 96),
            (241, 128, 70, 104),
            (176, 226, 255, 112),
        )
        for _ in range(34):
            self.particles.append(
                {
                    "x": self.rng.random(),
                    "y": self.rng.random(),
                    "speed": self.rng.uniform(0.010, 0.026),
                    "drift": self.rng.uniform(-0.012, 0.018),
                    "size": self.rng.uniform(1.3, 3.4),
                    "phase": self.rng.uniform(0.0, math.tau),
                    "color": self.rng.choice(colors),
                }
            )

    def resize(self):
        self.build_particles()

    def update_particles(self, delta_s):
        delta_s = min(max(delta_s, 1.0 / 120.0), 1.0 / 20.0)
        self.notice_timer = max(0.0, self.notice_timer - delta_s)
        for particle in self.particles:
            wave = math.sin(self.app.time * 0.75 + particle["phase"]) * 0.006
            particle["x"] += (particle["drift"] + wave) * delta_s
            particle["y"] += particle["speed"] * delta_s
            if particle["y"] > 1.05:
                particle["y"] = -0.05
                particle["x"] = self.rng.random()
            if particle["x"] < -0.05:
                particle["x"] = 1.05
            elif particle["x"] > 1.05:
                particle["x"] = -0.05

    def load_background(self):
        if self.background_loaded:
            return self.background

        self.background_loaded = True
        for path in MENU["bg_paths"]:
            if not path.exists():
                continue
            try:
                self.background = pg.image.load(str(path)).convert_alpha()
                self.background_path = path
                return self.background
            except pg.error:
                continue
        return None

    def cinematic_season_crop(self, index):
        background = self.load_background()
        if background is None or self.background_path is None or self.background_path.name != "menu_background.png":
            return None

        width, height = background.get_size()
        left = int(index * width / 4.0)
        right = int((index + 1) * width / 4.0)
        crop = pg.Rect(left, int(height * 0.08), max(1, right - left), int(height * 0.84))
        crop.clamp_ip(background.get_rect())
        return background.subsurface(crop).copy()

    def load_season_image(self, spec):
        key = spec["id"]
        if key in self.season_images:
            return self.season_images[key]

        paths = spec.get("images", (spec.get("image"),))
        for path in paths:
            if path is None or not path.exists():
                continue
            try:
                self.season_images[key] = pg.image.load(str(path)).convert_alpha()
                return self.season_images[key]
            except pg.error:
                continue
        self.season_images[key] = None
        return None

    def scale_fill(self, source, size):
        width, height = size
        source_w, source_h = source.get_size()
        scale = max(width / source_w, height / source_h)
        scaled = pg.transform.smoothscale(
            source,
            (max(1, math.ceil(source_w * scale)), max(1, math.ceil(source_h * scale))),
        )
        crop = pg.Rect(0, 0, width, height)
        crop.center = scaled.get_rect().center
        return scaled.subsurface(crop).copy()

    def layout(self):
        width, height = self.app.WIN_SIZE
        content_w = min(MENU["max_width"], int(width * 0.86))
        top = int(height * 0.070)
        card_gap = int(clamp(width * 0.017, 14, 24))
        card_w = int((content_w - card_gap * 3) / 4)
        card_h = int(clamp(min(height * 0.205, card_w * 0.52), 108, 164))
        card_y = int(clamp(height * 0.445, 220, height - card_h - 174))
        card_x = (width - (card_w * 4 + card_gap * 3)) // 2
        action_w = int(clamp(width * 0.18, 190, 270))
        action_h = int(clamp(height * 0.052, 42, 54))
        action_gap = int(clamp(height * 0.014, 10, 16))
        action_total_h = action_h * 3 + action_gap * 2
        action_y = int(card_y + card_h + clamp(height * 0.048, 30, 48))
        action_y = int(clamp(action_y, card_y + card_h + 22, height - action_total_h - 58))
        return {
            "width": width,
            "height": height,
            "content_w": content_w,
            "top": top,
            "card_w": card_w,
            "card_h": card_h,
            "card_gap": card_gap,
            "card_x": card_x,
            "card_y": card_y,
            "action_w": action_w,
            "action_h": action_h,
            "action_gap": action_gap,
            "action_y": action_y,
        }

    def main_action_rects(self):
        layout = self.layout()
        x = (layout["width"] - layout["action_w"]) // 2
        y = layout["action_y"]
        gap = layout["action_gap"]
        h = layout["action_h"]
        return {
            "play": pg.Rect(x, y, layout["action_w"], h),
            "settings": pg.Rect(x, y + h + gap, layout["action_w"], h),
            "exit": pg.Rect(x, y + (h + gap) * 2, layout["action_w"], h),
        }

    def play_button_rect(self):
        return self.main_action_rects()["play"]

    def season_card_rects(self):
        layout = self.layout()
        rects = {}
        for index, spec in enumerate(MENU["season_cards"]):
            x = layout["card_x"] + index * (layout["card_w"] + layout["card_gap"])
            rects[spec["id"]] = pg.Rect(x, layout["card_y"], layout["card_w"], layout["card_h"])
        return rects

    def settings_button_rect(self):
        return self.main_action_rects()["settings"]

    def exit_button_rect(self):
        return self.main_action_rects()["exit"]

    def hover_token(self):
        mouse = pg.mouse.get_pos()
        card = None
        for season_id, rect in self.season_card_rects().items():
            if rect.collidepoint(mouse):
                card = season_id
                break
        return (
            self.play_button_rect().collidepoint(mouse),
            self.settings_button_rect().collidepoint(mouse),
            self.exit_button_rect().collidepoint(mouse),
            card,
            self.selected_season_id,
            bool(self.notice_timer > 0.0),
        )

    def handle_menu_input(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            position = event.pos
            if self.play_button_rect().collidepoint(position):
                return {"action": "play", "season_id": self.selected_season_id}
            if self.settings_button_rect().collidepoint(position):
                return {"action": "settings"}
            if self.exit_button_rect().collidepoint(position):
                return {"action": "exit"}
            for season_id, rect in self.season_card_rects().items():
                if rect.collidepoint(position):
                    self.selected_season_id = season_id
                    return {"action": "select_season", "season_id": season_id}
        return {"action": "none"}

    def draw_background(self, surface):
        width, height = surface.get_size()
        background = self.load_background()
        if background is not None:
            surface.blit(self.scale_fill(background, (width, height)), (0, 0))
        else:
            surface.fill((12, 18, 28))

        veil = pg.Surface((width, height), pg.SRCALPHA)
        for y in range(height):
            t = y / max(1, height - 1)
            top = int(46 * max(0.0, 1.0 - t * 2.0))
            bottom = int(94 * max(0.0, (t - 0.50) / 0.50))
            center = int(14 * (1.0 - abs(t - 0.50) * 2.0))
            alpha = clamp(top + bottom + center, 8, 112)
            pg.draw.line(veil, (4, 8, 15, int(alpha)), (0, y), (width, y))
        surface.blit(veil, (0, 0))

        vignette = pg.Surface((width, height), pg.SRCALPHA)
        edge = int(width * 0.18)
        for x in range(edge):
            alpha = int(36 * (1.0 - x / max(1, edge)) ** 1.7)
            pg.draw.line(vignette, (0, 0, 0, alpha), (x, 0), (x, height))
            pg.draw.line(vignette, (0, 0, 0, alpha), (width - x - 1, 0), (width - x - 1, height))
        surface.blit(vignette, (0, 0))

    def draw_particles(self, surface):
        width, height = surface.get_size()
        for particle in self.particles:
            x = int(particle["x"] * width)
            y = int(particle["y"] * height)
            size = max(1, int(particle["size"]))
            color = particle["color"]
            if size <= 2:
                pg.draw.circle(surface, color, (x, y), size)
            else:
                rect = pg.Rect(x - size, y - size // 2, size * 2, max(2, size))
                pg.draw.ellipse(surface, color, rect)

    def draw_text(self, surface, text, font, center, color, shadow=(0, 0, 0, 150), glow=None):
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect(center=center)
        if glow is not None:
            glow_surface = font.render(text, True, glow)
            for offset in ((0, 0), (2, 0), (-2, 0), (0, 2), (0, -2), (3, 3), (-3, 3)):
                surface.blit(glow_surface, rect.move(offset))
        if shadow is not None:
            shadow_surface = font.render(text, True, shadow)
            surface.blit(shadow_surface, rect.move(2, 3))
        surface.blit(text_surface, rect)
        return rect

    def draw_title(self, surface):
        layout = self.layout()
        width, height = layout["width"], layout["height"]
        top = layout["top"]
        seasonal_size = int(clamp(height * 0.056, 34, 56))
        sakura_size = int(clamp(height * 0.082, 50, 84))
        subtitle_size = int(clamp(height * 0.029, 18, 27))
        body_size = int(clamp(height * 0.019, 13, 18))
        title_top = font_from(("segoeuisemibold", "arial", "calibri"), seasonal_size, bold=True)
        title = font_from(("segoeuisemibold", "arial", "calibri"), sakura_size, bold=True)
        subtitle = font_from(("segoeui", "arial", "calibri"), subtitle_size, bold=False)
        body = font_from(("segoeui", "arial", "calibri"), body_size, bold=False)

        self.draw_text(surface, "SEASONAL", title_top, (width // 2, top + seasonal_size // 2), (250, 249, 245), shadow=(0, 0, 0, 165))
        self.draw_text(surface, "SAKURA", title, (width // 2, top + seasonal_size + sakura_size // 2 - 6), (255, 255, 255), shadow=(0, 0, 0, 170))
        self.draw_text(surface, "FOUR SEASONS GARDEN", subtitle, (width // 2, top + seasonal_size + sakura_size + subtitle_size // 2 + 8), (229, 238, 243))
        self.draw_text(
            surface,
            "Explore a peaceful Japanese garden in four beautiful seasons.",
            body,
            (width // 2, top + seasonal_size + sakura_size + subtitle_size + body_size // 2 + 22),
            (213, 224, 232),
            shadow=(0, 0, 0, 130),
        )

    def draw_icon(self, surface, icon, center, color, size):
        x, y = center
        if icon == "sakura":
            for angle in range(0, 360, 72):
                px = x + math.cos(math.radians(angle)) * size * 0.36
                py = y + math.sin(math.radians(angle)) * size * 0.36
                pg.draw.circle(surface, rgba(color, 230), (int(px), int(py)), max(3, int(size * 0.18)))
            pg.draw.circle(surface, (255, 235, 246, 245), (x, y), max(2, int(size * 0.12)))
        elif icon == "sun":
            for angle in range(0, 360, 45):
                start = (x + math.cos(math.radians(angle)) * size * 0.34, y + math.sin(math.radians(angle)) * size * 0.34)
                end = (x + math.cos(math.radians(angle)) * size * 0.55, y + math.sin(math.radians(angle)) * size * 0.55)
                pg.draw.aaline(surface, rgba(color, 230), start, end)
            pg.draw.circle(surface, rgba(color, 240), (x, y), max(5, int(size * 0.26)))
        elif icon == "leaf":
            points = [(x, y - size // 2), (x + size // 2, y), (x, y + size // 2), (x - size // 3, y)]
            pg.draw.polygon(surface, rgba(color, 230), points)
            pg.draw.aaline(surface, (255, 220, 178, 230), (x - size // 3, y), (x + size // 3, y))
        elif icon == "snow":
            for angle in range(0, 180, 60):
                dx = math.cos(math.radians(angle)) * size * 0.50
                dy = math.sin(math.radians(angle)) * size * 0.50
                pg.draw.aaline(surface, rgba(color, 230), (x - dx, y - dy), (x + dx, y + dy))
            pg.draw.circle(surface, (236, 250, 255, 230), (x, y), max(2, int(size * 0.10)))

    def draw_season_cards(self, surface):
        mouse = pg.mouse.get_pos()
        rects = self.season_card_rects()
        self.hovered_id = None
        for index, spec in enumerate(MENU["season_cards"]):
            base_rect = rects[spec["id"]]
            hovered = base_rect.collidepoint(mouse)
            selected = self.selected_season_id == spec["id"]
            if hovered:
                self.hovered_id = spec["id"]
            scale = 1.018 if hovered else 1.0
            rect = base_rect.inflate(int(base_rect.width * (scale - 1.0)), int(base_rect.height * (scale - 1.0)))
            color = spec["color"]

            for spread, alpha in ((7, 12), (3, 28)):
                glow = pg.Surface((rect.width + spread * 2, rect.height + spread * 2), pg.SRCALPHA)
                pg.draw.rect(glow, rgba(color, alpha + (12 if selected or hovered else 0)), glow.get_rect(), border_radius=9)
                surface.blit(glow, (rect.x - spread, rect.y - spread))

            image = self.load_season_image(spec)
            if image is not None:
                card = self.scale_fill(image, rect.size)
            else:
                card = pg.Surface(rect.size, pg.SRCALPHA)
                card.fill(rgba(color, 90))
            lift = pg.Surface(rect.size, pg.SRCALPHA)
            lift.fill((255, 255, 255, 14))
            card.blit(lift, (0, 0))
            card_overlay = pg.Surface(rect.size, pg.SRCALPHA)
            card_overlay.fill((0, 0, 0, 18))
            card.blit(card_overlay, (0, 0))
            surface.blit(card, rect)

            bottom_h = max(42, int(rect.height * 0.30))
            bottom = pg.Surface((rect.width, bottom_h), pg.SRCALPHA)
            for y in range(bottom_h):
                alpha = int(50 + 108 * y / max(1, bottom_h - 1))
                pg.draw.line(bottom, (3, 6, 11, alpha), (0, y), (rect.width, y))
            surface.blit(bottom, (rect.x, rect.bottom - bottom_h))

            pg.draw.rect(surface, rgba(color, 220 if selected or hovered else 145), rect, width=2 if selected or hovered else 1, border_radius=8)
            if selected:
                pg.draw.rect(surface, (255, 255, 255, 74), rect.inflate(-6, -6), width=1, border_radius=6)

            font = font_from(("segoeuisemibold", "arial", "calibri"), int(clamp(rect.height * 0.145, 18, 26)), bold=True)
            label = font.render(spec["label"], True, (250, 252, 255))
            icon_center = (rect.x + 26, rect.bottom - bottom_h // 2 + 1)
            self.draw_icon(surface, spec["icon"], icon_center, color, int(clamp(rect.height * 0.16, 20, 30)))
            surface.blit(label, label.get_rect(midleft=(rect.x + 52, icon_center[1])))

    def draw_main_action_button(self, surface, rect, label, accent, hovered=False):
        radius = min(12, rect.height // 3)
        shadow = pg.Surface((rect.width + 14, rect.height + 14), pg.SRCALPHA)
        shadow_alpha = 96 if hovered else 68
        pg.draw.rect(shadow, (0, 0, 0, shadow_alpha), shadow.get_rect().inflate(-8, -8), border_radius=radius + 4)
        surface.blit(shadow, (rect.x - 7, rect.y - 4))

        fill = (32, 45, 60, 255) if hovered else (15, 25, 36, 248)
        border = rgba(accent, 255 if hovered else 210)
        inner = (255, 255, 255, 28 if hovered else 16)
        pg.draw.rect(surface, fill, rect, border_radius=radius)
        pg.draw.rect(surface, border, rect, width=2 if hovered else 1, border_radius=radius)
        pg.draw.rect(surface, inner, rect.inflate(-6, -6), width=1, border_radius=max(4, radius - 3))

        icon_x = rect.x + int(rect.height * 0.72)
        icon_y = rect.centery
        if label == "PLAY":
            tri = max(10, int(rect.height * 0.34))
            points = [
                (icon_x - tri // 3, icon_y - tri // 2),
                (icon_x - tri // 3, icon_y + tri // 2),
                (icon_x + tri // 2, icon_y),
            ]
            pg.draw.polygon(surface, rgba(accent, 245), points)
        elif label == "SETTINGS":
            pg.draw.circle(surface, rgba(accent, 235), (icon_x, icon_y), 8, width=2)
            for angle in range(0, 360, 60):
                dx = math.cos(math.radians(angle)) * 12
                dy = math.sin(math.radians(angle)) * 12
                pg.draw.aaline(surface, rgba(accent, 210), (icon_x, icon_y), (icon_x + dx, icon_y + dy))
        elif label == "EXIT":
            arrow = max(12, int(rect.height * 0.32))
            pg.draw.line(surface, rgba(accent, 235), (icon_x - arrow // 2, icon_y), (icon_x + arrow // 2, icon_y), width=3)
            pg.draw.polygon(
                surface,
                rgba(accent, 235),
                [(icon_x + arrow // 2, icon_y), (icon_x + 1, icon_y - 6), (icon_x + 1, icon_y + 6)],
            )

        font = font_from(("segoeuisemibold", "arial", "calibri"), int(clamp(rect.height * 0.40, 17, 22)), bold=True)
        text = font.render(label, True, (248, 252, 255))
        text_rect = text.get_rect(center=rect.center)
        shadow_text = font.render(label, True, (0, 0, 0))
        surface.blit(shadow_text, text_rect.move(1, 2))
        surface.blit(text, text_rect)

    def draw_main_actions(self, surface):
        rects = self.main_action_rects()
        mouse = pg.mouse.get_pos()
        self.hovered_play = rects["play"].collidepoint(mouse)
        self.hovered_settings = rects["settings"].collidepoint(mouse)
        actions = (
            ("play", "PLAY", (255, 150, 204), self.hovered_play),
            ("settings", "SETTINGS", (126, 205, 255), self.hovered_settings),
            ("exit", "EXIT", (255, 124, 138), rects["exit"].collidepoint(mouse)),
        )
        for key, label, accent, hovered in actions:
            self.draw_main_action_button(surface, rects[key], label, accent, hovered)

    def draw_settings_button(self, surface):
        rect = self.settings_button_rect()
        self.hovered_settings = rect.collidepoint(pg.mouse.get_pos())
        fill_alpha = 150 if self.hovered_settings else 108
        pg.draw.rect(surface, (8, 14, 22, fill_alpha), rect, border_radius=rect.height // 2)
        pg.draw.rect(surface, (255, 255, 255, 80 if self.hovered_settings else 42), rect, width=1, border_radius=rect.height // 2)

        icon_x = rect.x + rect.height // 2 + 2
        icon_y = rect.centery
        pg.draw.circle(surface, (230, 238, 244, 210), (icon_x, icon_y), 8, width=2)
        for angle in range(0, 360, 60):
            dx = math.cos(math.radians(angle)) * 12
            dy = math.sin(math.radians(angle)) * 12
            pg.draw.aaline(surface, (230, 238, 244, 180), (icon_x, icon_y), (icon_x + dx, icon_y + dy))
        font = font_from(("segoeui", "arial", "calibri"), int(clamp(rect.height * 0.40, 14, 18)), bold=True)
        label = font.render("SETTINGS", True, (230, 238, 244))
        surface.blit(label, label.get_rect(midleft=(rect.x + rect.height + 8, rect.centery)))

    def draw_footer(self, surface):
        layout = self.layout()
        font = font_from(("segoeui", "arial", "calibri"), int(clamp(layout["height"] * 0.022, 14, 18)))
        text = "Python - Pygame - ModernGL - GLSL"
        self.draw_text(surface, text, font, (layout["width"] // 2, layout["height"] - 24), (218, 226, 233), shadow=(0, 0, 0, 130))
        if self.notice_timer > 0.0 and self.notice:
            notice_font = font_from(("segoeui", "arial", "calibri"), int(clamp(layout["height"] * 0.024, 15, 20)))
            self.draw_text(surface, self.notice, notice_font, (layout["width"] // 2, layout["height"] - 52), (255, 244, 250), glow=(255, 128, 184, 46))

    def render_surface(self, delta_s):
        self.update_particles(delta_s)
        surface = pg.Surface(self.app.WIN_SIZE, pg.SRCALPHA)
        self.draw_background(surface)
        self.draw_title(surface)
        self.draw_season_cards(surface)
        self.draw_main_actions(surface)
        self.draw_footer(surface)
        return surface
