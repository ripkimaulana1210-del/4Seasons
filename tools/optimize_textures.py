from __future__ import annotations

import argparse
import io
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
TEXTURE_DIR = ROOT_DIR / "assets" / "textures"


@dataclass(frozen=True)
class Result:
    path: Path
    original_bytes: int
    optimized_bytes: int
    original_size: tuple[int, int]
    optimized_size: tuple[int, int]
    resized: bool
    written: bool
    skipped_reason: str = ""

    @property
    def saved_bytes(self) -> int:
        return self.original_bytes - self.optimized_bytes

    @property
    def saved_percent(self) -> float:
        if self.original_bytes <= 0:
            return 0.0
        return (self.saved_bytes / self.original_bytes) * 100.0


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def require_pillow():
    try:
        from PIL import Image, ImageOps, UnidentifiedImageError
    except ImportError as exc:
        raise SystemExit(
            "Pillow is required for texture optimization. Install it with: python -m pip install pillow"
        ) from exc
    return Image, ImageOps, UnidentifiedImageError


def resampling_filter(Image):
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


def planned_size(size: tuple[int, int], max_size: int) -> tuple[int, int]:
    width, height = size
    if max_size <= 0 or max(width, height) <= max_size:
        return size

    scale = max_size / max(width, height)
    return max(1, int(round(width * scale))), max(1, int(round(height * scale)))


def encode_png(path: Path, max_size: int):
    Image, ImageOps, UnidentifiedImageError = require_pillow()

    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            original_size = image.size
            target_size = planned_size(original_size, max_size)
            resized = target_size != original_size

            if resized:
                image = image.resize(target_size, resampling_filter(Image))

            if image.mode not in ("RGBA", "RGB", "LA", "L", "P"):
                image = image.convert("RGBA")

            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            return buffer.getvalue(), original_size, image.size, resized
    except UnidentifiedImageError as exc:
        raise ValueError(f"Not a readable image: {path}") from exc


def iter_textures(texture_dir: Path, patterns: list[str]):
    seen = set()
    for pattern in patterns:
        for path in sorted(texture_dir.glob(pattern)):
            if path.is_file() and path.suffix.lower() == ".png" and path not in seen:
                seen.add(path)
                yield path


def target_path_for(path: Path, texture_dir: Path, out_dir: Path | None):
    if out_dir is None:
        return path
    return out_dir / path.relative_to(texture_dir)


def optimize_texture(path: Path, texture_dir: Path, out_dir: Path | None, args) -> Result:
    original_bytes = path.stat().st_size
    optimized_data, original_size, optimized_size, resized = encode_png(path, args.max_size)
    optimized_bytes = len(optimized_data)
    saved = original_bytes - optimized_bytes

    should_write = args.write or out_dir is not None
    worth_writing = args.force or resized or saved >= args.min_savings
    skipped_reason = ""

    if not worth_writing:
        skipped_reason = f"savings below {args.min_savings} bytes"
        should_write = False

    written = False
    if should_write:
        target_path = target_path_for(path, texture_dir, out_dir)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if out_dir is None and args.backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            if not backup_path.exists():
                shutil.copy2(path, backup_path)

        target_path.write_bytes(optimized_data)
        written = True

    return Result(
        path=path,
        original_bytes=original_bytes,
        optimized_bytes=optimized_bytes,
        original_size=original_size,
        optimized_size=optimized_size,
        resized=resized,
        written=written,
        skipped_reason=skipped_reason,
    )


def print_result(result: Result, root: Path):
    size_text = f"{result.original_size[0]}x{result.original_size[1]}"
    if result.resized:
        size_text += f" -> {result.optimized_size[0]}x{result.optimized_size[1]}"

    action = "written" if result.written else "dry-run"
    if result.skipped_reason:
        action = f"skipped: {result.skipped_reason}"

    print(
        f"{rel(result.path, root)} | {size_text} | "
        f"{result.original_bytes} -> {result.optimized_bytes} bytes "
        f"({result.saved_percent:0.1f}%) | {action}"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Optimize PNG textures. Default mode is a safe dry-run."
    )
    parser.add_argument("--root", type=Path, default=ROOT_DIR, help="Project root. Defaults to this repository.")
    parser.add_argument("--texture-dir", type=Path, default=None, help="Texture directory. Defaults to assets/textures.")
    parser.add_argument("--pattern", action="append", default=["*.png"], help="Glob pattern relative to texture dir.")
    parser.add_argument("--max-size", type=int, default=0, help="Resize longest side to this many pixels. 0 disables resizing.")
    parser.add_argument("--min-savings", type=int, default=512, help="Minimum byte savings before writing.")
    parser.add_argument("--write", action="store_true", help="Overwrite source textures when optimization is worthwhile.")
    parser.add_argument("--out-dir", type=Path, default=None, help="Write optimized copies here instead of overwriting.")
    parser.add_argument("--force", action="store_true", help="Write even when file size does not improve.")
    parser.add_argument("--no-backup", dest="backup", action="store_false", help="Do not create .bak files when overwriting.")
    parser.set_defaults(backup=True)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    texture_dir = (args.texture_dir or (root / "assets" / "textures")).resolve()
    out_dir = args.out_dir.resolve() if args.out_dir else None

    if not texture_dir.exists():
        print(f"Texture directory does not exist: {texture_dir}", file=sys.stderr)
        return 1

    paths = list(iter_textures(texture_dir, args.pattern))
    if not paths:
        print(f"No PNG textures found in {texture_dir}")
        return 0

    print("Texture optimization")
    print(f"- texture dir: {rel(texture_dir, root)}")
    print(f"- mode: {'write' if args.write else 'copy to out-dir' if out_dir else 'dry-run'}")
    if args.max_size > 0:
        print(f"- max size: {args.max_size}px")
    print()

    results = []
    errors = 0
    for path in paths:
        try:
            result = optimize_texture(path, texture_dir, out_dir, args)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"ERROR {rel(path, root)}: {exc}")
            continue
        results.append(result)
        print_result(result, root)

    total_original = sum(result.original_bytes for result in results)
    total_optimized = sum(result.optimized_bytes for result in results)
    total_saved = total_original - total_optimized
    written = sum(1 for result in results if result.written)

    print()
    print(f"Processed: {len(results)} textures")
    print(f"Written: {written}")
    print(f"Potential savings: {total_saved} bytes")
    if not args.write and out_dir is None:
        print("Dry-run only. Re-run with --write to overwrite, or --out-dir <dir> to create optimized copies.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
