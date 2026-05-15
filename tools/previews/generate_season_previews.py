from pathlib import Path
import sys

import pygame as pg

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from engine.core.app import SxvxnEngine
from engine.core.paths import SCREENSHOT_DIR, UI_DIR
from engine.systems.season_controller import SEASONS


PREVIEW_TIMES = {
    "spring": 0.34,
    "summer": 0.04,
    "autumn": 0.72,
    "winter": 0.05,
}

MENU_CARD_TIMES = {
    "spring": 0.34,
    "summer": 0.34,
    "autumn": 0.70,
    "winter": 0.24,
}

MENU_CARD_CAMERA_PRESET = "bridge"


def save_screen(app, path):
    data = app.ctx.screen.read(components=3, alignment=1)
    surface = pg.image.frombuffer(data, app.WIN_SIZE, "RGB")
    surface = pg.transform.flip(surface, False, True)
    pg.image.save(surface, str(path))


def set_menu_card_camera(app):
    app.camera.set_preset(MENU_CARD_CAMERA_PRESET)


def write_gallery(paths):
    gallery_path = SCREENSHOT_DIR / "season_gallery.md"
    lines = [
        "# Season Preview Gallery",
        "",
        "Generated from the current OpenGL scene using `python tools\\previews\\generate_season_previews.py`.",
        "",
    ]
    for season_id, image_path in paths:
        lines.extend(
            [
                f"## {season_id.title()}",
                "",
                f"![{season_id}]({image_path.name})",
                "",
            ]
        )
    gallery_path.write_text("\n".join(lines), encoding="utf-8")
    return gallery_path


def main():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    UI_DIR.mkdir(parents=True, exist_ok=True)
    app = SxvxnEngine()
    paths = []

    try:
        app.hud_visible = False
        app.profile_visible = False
        app.audio.muted = True
        app.audio.stop(fade_ms=0)
        app.post_processor.enabled = True
        app.game_started = True

        for index, season in enumerate(SEASONS):
            season_id = season["id"]
            app.season_controller.current_index = index
            app.season_controller.transition_from = None
            app.season_controller.transition_to = None
            app.season_controller.day_time = PREVIEW_TIMES.get(season_id, 0.34)
            app.apply_season()
            app.camera.set_season_preset()

            for _ in range(3):
                app.get_time()
                app.season_controller.update(16)
                app.camera.update()
                app.render()

            path = SCREENSHOT_DIR / f"season_{season_id}.png"
            save_screen(app, path)
            paths.append((season_id, path))
            print(f"saved {path}")

            if season_id in MENU_CARD_TIMES:
                app.season_controller.day_time = MENU_CARD_TIMES[season_id]
                app.apply_season()
                set_menu_card_camera(app)
                for _ in range(3):
                    app.get_time()
                    app.season_controller.update(16)
                    set_menu_card_camera(app)
                    app.render()
                menu_path = UI_DIR / f"menu_{season_id}.png"
                save_screen(app, menu_path)
                print(f"saved {menu_path}")

        gallery = write_gallery(paths)
        print(f"gallery {gallery}")
    finally:
        app.destroy()
        pg.quit()


if __name__ == "__main__":
    main()
