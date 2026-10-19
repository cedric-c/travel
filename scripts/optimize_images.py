#!/usr/bin/env python3
"""Generate deterministic, responsive WebP variants and a Jekyll data manifest."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

WIDTHS = (320, 800, 1600)
QUALITY = 80
VERSION = 1
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 60 * 1024 * 1024
MAX_PIXELS = 75_000_000


def process(root: Path, force: bool, dry_run: bool):
    source_dir = root / "images"
    output_dir = source_dir / "optimized"
    manifest_path = root / "_data" / "responsive_images.json"
    try:
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        previous = {}
    manifest = {}
    stats = {"sources": 0, "generated": 0, "unchanged": 0, "skipped": 0, "failed": 0, "original_bytes": 0, "variant_bytes": 0}
    failures = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or output_dir in path.parents or path.suffix.lower() not in EXTENSIONS:
            continue
        stats["sources"] += 1
        relative = path.relative_to(source_dir)
        key = "/images/" + relative.as_posix()
        try:
            if path.stat().st_size > MAX_BYTES:
                raise ValueError("file exceeds 60 MiB")
            with Image.open(path) as probe:
                if getattr(probe, "is_animated", False):
                    stats["skipped"] += 1
                    continue
                if probe.width * probe.height > MAX_PIXELS:
                    raise ValueError("image exceeds 75 megapixels")
                oriented = ImageOps.exif_transpose(probe)
                width, height = oriented.size
                if oriented.mode not in ("RGB", "RGBA"):
                    oriented = oriented.convert("RGBA" if "A" in oriented.getbands() or "transparency" in oriented.info else "RGB")
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                config = hashlib.sha256(f"{digest}:{VERSION}:{WIDTHS}:{QUALITY}".encode()).hexdigest()
                existing = previous.get(key, {})
                variants = []
                for target in WIDTHS:
                    if target > width:
                        continue
                    # Include source extension to avoid collisions between foo.jpg and foo.png.
                    dest = output_dir / relative.parent / f"{relative.name}-{target}.webp"
                    url = "/images/optimized/" + (relative.parent / dest.name).as_posix()
                    variant_width = target
                    variant_height = max(1, round(height * target / width))
                    unchanged = (not force and existing.get("config") == config and dest.exists())
                    if unchanged:
                        stats["unchanged"] += 1
                        byte_size = dest.stat().st_size
                    elif dry_run:
                        stats["generated"] += 1
                        byte_size = 0
                    else:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        resized = oriented.resize((variant_width, variant_height), Image.Resampling.LANCZOS)
                        if resized.mode == "RGBA" and resized.getchannel("A").getextrema() == (255, 255):
                            resized = resized.convert("RGB")
                        tmp = dest.with_suffix(".tmp")
                        resized.save(tmp, format="WEBP", quality=QUALITY, method=6)
                        os.replace(tmp, dest)
                        stats["generated"] += 1
                        byte_size = dest.stat().st_size
                    stats["variant_bytes"] += byte_size
                    variants.append({"width": variant_width, "height": variant_height, "url": url})
                if variants:
                    manifest[key] = {"width": width, "height": height, "config": config, "variants": variants}
                    stats["original_bytes"] += path.stat().st_size
                else:
                    stats["skipped"] += 1
        except (OSError, ValueError, UnidentifiedImageError) as exc:
            stats["failed"] += 1
            failures.append(f"{key}: {exc}")
    if not dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"dry_run": dry_run, "stats": stats, "failures": failures}, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process(args.root, args.force, args.dry_run)
