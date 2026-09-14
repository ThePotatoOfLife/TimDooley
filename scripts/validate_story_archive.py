from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED_CLASSES = {"person", "collective", "great_book_character", "created_being", "platform_or_system"}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _duplicates(values):
    seen = set()
    dupes = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    return sorted(dupes)


def validate_story_archive(root: Path) -> list[str]:
    story = root / "knowledge" / "story"
    errors: list[str] = []

    cast_path = story / "cast-book.json"
    arc_path = story / "arc-season-map.json"
    for path in (cast_path, arc_path):
        if not path.exists():
            errors.append(f"missing {path.relative_to(root)}")
            return errors

    try:
        cast_data = _load(cast_path)
        arc_data = _load(arc_path)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"story archive parse error: {exc}"]

    cast = cast_data.get("cast", [])
    cast_ids = [entry.get("id") for entry in cast]
    for duplicate in _duplicates(cast_ids):
        errors.append(f"duplicate cast id {duplicate}")
    for entry in cast:
        if not entry.get("id"):
            errors.append("cast entry missing id")
        if entry.get("class") not in ALLOWED_CLASSES:
            errors.append(f"invalid cast class for {entry.get('id', '<unknown>')}")

    arcs = arc_data.get("arcs", [])
    arc_ids = [entry.get("id") for entry in arcs]
    for duplicate in _duplicates(arc_ids):
        errors.append(f"duplicate arc id {duplicate}")
    for entry in arcs:
        if not entry.get("id"):
            errors.append("arc entry missing id")
        for cast_id in entry.get("cast", []):
            if cast_id not in cast_ids:
                errors.append(f"arc {entry.get('id')} references unknown cast id {cast_id}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_story_archive(root)
    if errors:
        print("Story archive validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Story archive validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
