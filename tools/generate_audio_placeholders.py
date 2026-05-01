from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT_DIR / "assets" / "audio"
SEASONS_DIR = ROOT_DIR / "engine" / "seasons"


DEFAULT_AUDIO_PLAN = {
    "spring": {
        "filename": "spring_hope.ogg",
        "volume": 0.38,
        "emotion": "Harapan baru, sakura, hujan ringan, awal kehidupan.",
        "mood_keywords": ["gentle piano", "koto", "soft strings", "morning birds", "light rain"],
        "reference": "Ikimonogakari - SAKURA / Sakura Sakura mood, but use licensed or royalty-free audio.",
    },
    "summer": {
        "filename": "summer_courage.ogg",
        "volume": 0.40,
        "emotion": "Energi muda, festival malam, kunang-kunang, langit cerah penuh bintang.",
        "mood_keywords": ["matsuri drums", "shamisen", "warm synth pad", "crickets", "fireworks ambience"],
        "reference": "Uchiage Hanabi / Joe Hisaishi - Summer mood, but use licensed or royalty-free audio.",
    },
    "autumn": {
        "filename": "autumn_memory.ogg",
        "volume": 0.36,
        "emotion": "Melepaskan, daun gugur, nostalgia, angin pelan.",
        "mood_keywords": ["solo piano", "shakuhachi", "low strings", "wind", "dry leaves"],
        "reference": "Spitz - Kaede / Aka Tombo mood, but use licensed or royalty-free audio.",
    },
    "winter": {
        "filename": "winter_silence.ogg",
        "volume": 0.34,
        "emotion": "Hening, salju, menerima, pulang ke dalam diri.",
        "mood_keywords": ["music box", "soft piano", "choir pad", "snow wind", "distant bells"],
        "reference": "Yuki no Hana / Konayuki mood, but use licensed or royalty-free audio.",
    },
}


@dataclass(frozen=True)
class SeasonAudio:
    season_id: str
    season_name: str
    current_music_path: str | None
    planned_path: str
    volume: float
    emotion_title: str
    emotion_line: str
    mood_keywords: list[str]
    reference: str
    status: str


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def literal_assignment(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"{name} assignment not found in {path}")


def load_seasons(seasons_dir: Path):
    seasons = []
    for path in sorted(seasons_dir.glob("season_*.py")):
        seasons.append((path, literal_assignment(path, "SEASON")))
    return seasons


def build_audio_plan(root: Path):
    seasons = load_seasons(root / "engine" / "seasons")
    plan = []

    for _path, season in seasons:
        season_id = season["id"]
        defaults = DEFAULT_AUDIO_PLAN.get(season_id, {})
        filename = defaults.get("filename", f"{season_id}_ambience.ogg")
        planned_path = f"assets/audio/{filename}"
        current_music_path = season.get("music_path")
        audio_path = root / planned_path
        current_path = root / current_music_path if isinstance(current_music_path, str) else None

        if audio_path.exists():
            status = "planned file exists"
        elif current_path and current_path.exists():
            status = "current music exists"
        elif current_music_path:
            status = "current music missing"
        else:
            status = "needs audio file"

        plan.append(
            SeasonAudio(
                season_id=season_id,
                season_name=season.get("name", season_id),
                current_music_path=current_music_path,
                planned_path=planned_path,
                volume=float(season.get("music_volume", defaults.get("volume", 0.40))),
                emotion_title=season.get("emotion_title", ""),
                emotion_line=season.get("emotion_line", ""),
                mood_keywords=list(defaults.get("mood_keywords", [])),
                reference=defaults.get("reference", ""),
                status=status,
            )
        )

    return plan


def make_placeholder_text(item: SeasonAudio):
    keywords = ", ".join(item.mood_keywords) if item.mood_keywords else "-"
    return "\n".join(
        [
            f"Season: {item.season_name} ({item.season_id})",
            f"Planned audio file: {item.planned_path}",
            f"Suggested volume: {item.volume:0.2f}",
            "",
            "Emotion:",
            f"- {item.emotion_title}",
            f"- {item.emotion_line}",
            "",
            "Mood keywords:",
            f"- {keywords}",
            "",
            "Reference mood:",
            f"- {item.reference}",
            "",
            "Note:",
            "- This is a planning placeholder, not an audio file.",
            "- Use licensed, royalty-free, or self-created audio before enabling it in season files.",
            "",
        ]
    )


def write_markdown_manifest(plan: list[SeasonAudio], path: Path):
    lines = [
        "# Audio Plan",
        "",
        "This file tracks planned seasonal music and ambience. Do not commit copyrighted commercial songs unless you have the rights.",
        "",
        "| Season | Planned file | Volume | Status | Mood |",
        "|---|---:|---:|---|---|",
    ]

    for item in plan:
        mood = ", ".join(item.mood_keywords[:3]) if item.mood_keywords else "-"
        lines.append(
            f"| {item.season_name} | `{item.planned_path}` | {item.volume:0.2f} | {item.status} | {mood} |"
        )

    lines.append("")
    lines.append("## References")
    for item in plan:
        lines.append(f"- **{item.season_name}:** {item.reference}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def update_audio_readme(plan: list[SeasonAudio], path: Path):
    lines = [
        "Seasonal audio folder.",
        "",
        "Recommended files:",
    ]
    for item in plan:
        lines.append(f"- {item.planned_path}: {item.season_name} ({item.emotion_title})")

    lines.extend(
        [
            "",
            "Current notes:",
            "- Pygame usually supports .mp3, .ogg, and .wav, depending on SDL_mixer.",
            "- Prefer .ogg for small looping ambience files.",
            "- Only use audio you are licensed to use.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def update_season_file(path: Path, planned_path: str, volume: float, dry_run: bool):
    text = path.read_text(encoding="utf-8")
    if '"music_path"' in text:
        return False

    marker = '    "life_stage":'
    insert = f'    "music_path": "{planned_path}",\n    "music_volume": {volume:0.2f},\n'
    if marker not in text:
        raise ValueError(f"Cannot find insertion point in {path}")

    updated = text.replace(marker, insert + marker, 1)
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate seasonal audio placeholders and manifests.")
    parser.add_argument("--root", type=Path, default=ROOT_DIR, help="Project root. Defaults to this repository.")
    parser.add_argument("--write", action="store_true", help="Write placeholder .txt files and manifests.")
    parser.add_argument(
        "--update-seasons",
        action="store_true",
        help="Add music_path/music_volume to season files that do not have them yet.",
    )
    parser.add_argument("--json", action="store_true", help="Print the audio plan as JSON.")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    audio_dir = root / "assets" / "audio"
    plan = build_audio_plan(root)

    if args.json:
        print(json.dumps([asdict(item) for item in plan], indent=2))
    else:
        print("Seasonal audio placeholders")
        for item in plan:
            print(f"- {item.season_name}: {item.planned_path} ({item.status})")

    if not args.write and not args.update_seasons:
        print("\nDry-run only. Use --write to create placeholder files/manifests.")
        return 0

    audio_dir.mkdir(parents=True, exist_ok=True)

    if args.write:
        for item in plan:
            placeholder_path = audio_dir / f"{item.season_id}.placeholder.txt"
            placeholder_path.write_text(make_placeholder_text(item), encoding="utf-8")

        write_markdown_manifest(plan, audio_dir / "AUDIO_PLAN.md")
        update_audio_readme(plan, audio_dir / "README.txt")
        print(f"\nWrote placeholders and manifests in {rel(audio_dir, root)}")

    if args.update_seasons:
        changed = 0
        for path, season in load_seasons(root / "engine" / "seasons"):
            item = next(entry for entry in plan if entry.season_id == season["id"])
            if update_season_file(path, item.planned_path, item.volume, dry_run=False):
                changed += 1
                print(f"Updated {rel(path, root)}")
        print(f"Season files updated: {changed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
