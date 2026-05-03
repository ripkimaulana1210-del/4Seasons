from pathlib import Path


ENGINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ENGINE_DIR.parent
ASSETS_DIR = PROJECT_DIR / "assets"
SHADER_DIR = ASSETS_DIR / "shaders"
TEXTURE_DIR = ASSETS_DIR / "textures"
AUDIO_DIR = ASSETS_DIR / "audio"
SCREENSHOT_DIR = PROJECT_DIR / "docs" / "previews"
CONFIG_DIR = PROJECT_DIR / "config"
SETTINGS_PATH = CONFIG_DIR / "settings.json"
