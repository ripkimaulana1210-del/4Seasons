from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT_DIR / "engine"
ASSETS_DIR = ROOT_DIR / "assets"
TEXTURE_DIR = ASSETS_DIR / "textures"
SHADER_DIR = ASSETS_DIR / "shaders"
AUDIO_DIR = ASSETS_DIR / "audio"


@dataclass(frozen=True)
class Issue:
    severity: str
    category: str
    message: str
    path: str = ""

    def as_dict(self):
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "path": self.path,
        }


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def parse_python(path: Path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def literal_assignment(path: Path, name: str):
    tree = parse_python(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"{name} assignment not found in {path}")


def parse_texture_defaults(root: Path):
    texture_file = root / "engine" / "texture.py"
    tree = parse_python(texture_file)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "defaults":
                    raw_defaults = ast.literal_eval(node.value)
                    return {
                        name: filename
                        for name, (filename, _fallback) in raw_defaults.items()
                    }
    return {}


def parse_shader_programs(root: Path):
    shader_file = root / "engine" / "shader_program.py"
    tree = parse_python(shader_file)
    programs = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get_program"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            programs.add(node.args[0].value)
    return programs


def parse_shader_program_refs(root: Path):
    vao_file = root / "engine" / "vao.py"
    tree = parse_python(vao_file)
    refs = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        value = node.value
        if not (
            isinstance(value, ast.Attribute)
            and value.attr == "programs"
        ):
            continue
        slice_node = node.slice
        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
            refs.add(slice_node.value)
    return refs


def load_seasons(root: Path):
    seasons = {}
    for path in sorted((root / "engine" / "seasons").glob("season_*.py")):
        seasons[path] = literal_assignment(path, "SEASON")
    return seasons


def collect_texture_refs(root: Path, seasons):
    refs = []

    for path, season in seasons.items():
        season_id = season.get("id", path.stem)
        for key, value in season.items():
            if key.endswith("_texture") and isinstance(value, str):
                refs.append((value, path, f"{season_id}.{key}"))

    for path in sorted((root / "engine").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = parse_python(path)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "texture_name":
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    refs.append((node.value.value, path, "texture_name"))
                continue

            if not isinstance(node, ast.Call):
                continue
            if not (isinstance(node.func, ast.Attribute) and node.func.attr == "season_value"):
                continue
            if len(node.args) < 2:
                continue
            key_node, default_node = node.args[0], node.args[1]
            if (
                isinstance(key_node, ast.Constant)
                and isinstance(key_node.value, str)
                and key_node.value.endswith("_texture")
                and isinstance(default_node, ast.Constant)
                and isinstance(default_node.value, str)
            ):
                refs.append((default_node.value, path, f"default {key_node.value}"))

    return refs


def collect_audio_refs(root: Path, seasons):
    refs = []
    for path, season in seasons.items():
        music_path = season.get("music_path")
        if isinstance(music_path, str):
            refs.append((music_path, path, f"{season.get('id', path.stem)}.music_path"))
    return refs


def existing_pngs(path: Path):
    if not path.exists():
        return set()
    return {item.name for item in path.glob("*.png")}


def validate(root: Path, strict: bool):
    issues: list[Issue] = []
    assets_dir = root / "assets"
    texture_dir = assets_dir / "textures"
    shader_dir = assets_dir / "shaders"
    audio_dir = assets_dir / "audio"

    for directory, category in (
        (assets_dir, "assets"),
        (texture_dir, "textures"),
        (shader_dir, "shaders"),
        (audio_dir, "audio"),
    ):
        if not directory.exists():
            issues.append(Issue("error", category, "Missing directory", rel(directory, root)))

    try:
        texture_defaults = parse_texture_defaults(root)
    except Exception as exc:  # noqa: BLE001
        texture_defaults = {}
        issues.append(Issue("error", "textures", f"Cannot parse texture defaults: {exc}"))

    try:
        shader_programs = parse_shader_programs(root)
    except Exception as exc:  # noqa: BLE001
        shader_programs = set()
        issues.append(Issue("error", "shaders", f"Cannot parse shader programs: {exc}"))

    try:
        shader_refs = parse_shader_program_refs(root)
    except Exception as exc:  # noqa: BLE001
        shader_refs = set()
        issues.append(Issue("warning", "shaders", f"Cannot parse shader program references: {exc}"))

    try:
        seasons = load_seasons(root)
    except Exception as exc:  # noqa: BLE001
        seasons = {}
        issues.append(Issue("error", "seasons", f"Cannot parse seasons: {exc}"))

    for texture_name, filename in texture_defaults.items():
        path = texture_dir / filename
        if not path.exists():
            issues.append(
                Issue(
                    "error",
                    "textures",
                    f"Texture '{texture_name}' points to missing file '{filename}'",
                    rel(path, root),
                )
            )

    registered_textures = set(texture_defaults)
    for texture_name, path, source in collect_texture_refs(root, seasons):
        if texture_name not in registered_textures:
            issues.append(
                Issue(
                    "error",
                    "textures",
                    f"Texture reference '{texture_name}' is not registered ({source})",
                    rel(path, root),
                )
            )

    texture_files = existing_pngs(texture_dir)
    registered_files = set(texture_defaults.values())
    for filename in sorted(texture_files - registered_files):
        issues.append(
            Issue(
                "warning",
                "textures",
                f"PNG exists but is not registered by TextureManager: {filename}",
                rel(texture_dir / filename, root),
            )
        )

    for program in sorted(shader_programs):
        for suffix in (".vert", ".frag"):
            path = shader_dir / f"{program}{suffix}"
            if not path.exists():
                issues.append(
                    Issue(
                        "error",
                        "shaders",
                        f"Shader program '{program}' is missing {suffix}",
                        rel(path, root),
                    )
                )

    for ref in sorted(shader_refs - shader_programs):
        issues.append(
            Issue(
                "error",
                "shaders",
                f"VAO references shader program '{ref}' but ShaderProgram does not load it",
                "engine/vao.py",
            )
        )

    for program in sorted(shader_programs - shader_refs):
        issues.append(
            Issue(
                "warning",
                "shaders",
                f"Shader program '{program}' is loaded but not referenced by VAO",
                "engine/shader_program.py",
            )
        )

    for music_path, path, source in collect_audio_refs(root, seasons):
        resolved = root / music_path
        if not resolved.exists():
            issues.append(
                Issue(
                    "error",
                    "audio",
                    f"Audio reference does not exist ({source}): {music_path}",
                    rel(path, root),
                )
            )

    if strict:
        issues = [
            Issue("error" if issue.severity == "warning" else issue.severity, issue.category, issue.message, issue.path)
            for issue in issues
        ]

    summary = {
        "texture_count": len(texture_defaults),
        "shader_program_count": len(shader_programs),
        "season_count": len(seasons),
        "audio_reference_count": len(collect_audio_refs(root, seasons)),
        "errors": sum(1 for issue in issues if issue.severity == "error"),
        "warnings": sum(1 for issue in issues if issue.severity == "warning"),
    }
    return summary, issues


def print_report(summary, issues):
    print("Asset validation")
    print(f"- textures registered: {summary['texture_count']}")
    print(f"- shader programs: {summary['shader_program_count']}")
    print(f"- seasons: {summary['season_count']}")
    print(f"- audio references: {summary['audio_reference_count']}")
    print(f"- errors: {summary['errors']}")
    print(f"- warnings: {summary['warnings']}")

    if not issues:
        print("\nOK: no asset issues found.")
        return

    print()
    for issue in issues:
        location = f" [{issue.path}]" if issue.path else ""
        print(f"{issue.severity.upper()} {issue.category}: {issue.message}{location}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate textures, shaders, season references, and audio assets.")
    parser.add_argument("--root", type=Path, default=ROOT_DIR, help="Project root. Defaults to this repository.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    summary, issues = validate(root, args.strict)

    if args.json:
        print(json.dumps({"summary": summary, "issues": [issue.as_dict() for issue in issues]}, indent=2))
    else:
        print_report(summary, issues)

    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
