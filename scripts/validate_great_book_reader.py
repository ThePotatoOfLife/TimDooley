#!/usr/bin/env python3
"""Validate the Great Book four-shard chapter-file reader contract."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

EXPECTED_SHARDS = [f"manifest/chapters-{i}.json" for i in range(1, 5)]
EXPECTED_CHAPTERS = 168
EXPECTED_BODY = 167
EXPECTED_INDEX_ONLY = 1
EXPECTED_INDEX_ONLY_NUMBERS = ["20"]
EXPECTED_SHARD_SIZE = 42
MAX_CHAPTER_BYTES = 500_000
REQUIRED_NUMBERS = ["1", "20", "24", "26.32", "47", "78", "125"]
CHAPTER_FILENAME_RE = re.compile(r"^(?P<order>\d{3})--(?P<anchor>chapter-[0-9-]+)--(?P<slug>[a-z0-9-]+)\.html$")
READER_MARKERS = [
    'href="great-book.css"',
    'id="gb-search"',
    'id="gb-toc"',
    'id="gb-document"',
    'id="gb-status"',
    'src="../app/great-book-reader.js"',
    'Read the original book',
    'Continue the Potato',
]


def load_json(path: Path, errors: list[str]) -> Any | None:
    if not path.is_file():
        errors.append(f"missing {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def safe_rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def expected_anchor(number: str) -> str:
    return "chapter-" + number.replace(".", "-")


def validate(root: Path, allow_missing_chapters: bool = False) -> list[str]:
    errors: list[str] = []
    gb = root / "great-book"
    index_path = gb / "book-index.json"
    index = load_json(index_path, errors)
    if not isinstance(index, dict):
        return errors or ["great-book/book-index.json must contain an object"]

    if index.get("architecture") != "one-chapter-one-file":
        errors.append("book-index architecture must be 'one-chapter-one-file'")

    shards = index.get("shards")
    if shards != EXPECTED_SHARDS:
        errors.append(
            "four-shard contract mismatch: expected "
            + ", ".join(EXPECTED_SHARDS)
            + f"; got {shards!r}"
        )

    records: list[dict[str, Any]] = []
    for shard_rel in EXPECTED_SHARDS:
        shard_path = gb / shard_rel
        if not shard_path.is_file():
            errors.append(f"four-shard contract mismatch: missing {shard_rel}")
            continue
        shard = load_json(shard_path, errors)
        if not isinstance(shard, list):
            if shard is not None:
                errors.append(f"{shard_rel} must contain a JSON array")
            continue
        if len(shard) != EXPECTED_SHARD_SIZE:
            errors.append(
                f"four-shard contract mismatch: {shard_rel} must contain "
                f"{EXPECTED_SHARD_SIZE} records, got {len(shard)}"
            )
        for record in shard:
            if isinstance(record, dict):
                records.append(record)
            else:
                errors.append(f"{shard_rel} contains a non-object chapter record")

    if index.get("chapter_count") != EXPECTED_CHAPTERS:
        errors.append(
            f"book-index chapter_count must be {EXPECTED_CHAPTERS}, got {index.get('chapter_count')!r}"
        )
    if index.get("body_chapter_count") != EXPECTED_BODY:
        errors.append(
            f"book-index body_chapter_count must be {EXPECTED_BODY}, got {index.get('body_chapter_count')!r}"
        )
    if index.get("index_only_count") != EXPECTED_INDEX_ONLY:
        errors.append(
            f"book-index index_only_count must be {EXPECTED_INDEX_ONLY}, got {index.get('index_only_count')!r}"
        )
    if len(records) != EXPECTED_CHAPTERS:
        errors.append(f"expected {EXPECTED_CHAPTERS} chapter records, got {len(records)}")

    numbers: list[str] = []
    anchors: list[str] = []
    paths: list[str] = []
    orders: list[int] = []
    referenced_files: set[Path] = set()

    for position, record in enumerate(records, start=1):
        number = record.get("number")
        anchor = record.get("anchor")
        rel_path = record.get("path")
        order = record.get("order")
        status = record.get("status")

        if not isinstance(number, str) or not number:
            errors.append(f"record {position}: missing string chapter number")
            continue
        numbers.append(number)

        if not isinstance(order, int):
            errors.append(f"chapter {number}: order must be an integer")
        else:
            orders.append(order)
            if order != position:
                errors.append(f"chapter {number}: order {order} does not match position {position}")

        exp_anchor = expected_anchor(number)
        if anchor != exp_anchor:
            errors.append(
                f"chapter {number}: anchor must be {exp_anchor!r}; decimal chapter numbers use hyphens, never dots"
            )
        if isinstance(anchor, str):
            anchors.append(anchor)
            if "." in anchor:
                errors.append(f"chapter {number}: anchor contains a dot; expected {exp_anchor!r}")

        if not isinstance(rel_path, str) or not rel_path:
            errors.append(f"chapter {number}: missing chapter path")
            continue
        paths.append(rel_path)
        rel = Path(rel_path)
        referenced_files.add(rel)

        if rel.is_absolute() or ".." in rel.parts:
            errors.append(f"chapter {number}: unsafe chapter path {rel_path!r}")
        if not rel_path.startswith("chapters/"):
            errors.append(f"chapter {number}: path must live under chapters/: {rel_path!r}")

        filename = rel.name
        if filename.count(".") != 1 or not filename.endswith(".html"):
            errors.append(
                f"chapter {number}: .html must be the only filename dot: {filename!r}"
            )
        if "." in rel.stem:
            errors.append(
                f"chapter {number}: filename stem contains a dot; use hyphens for decimal numbers: {filename!r}"
            )

        match = CHAPTER_FILENAME_RE.fullmatch(filename)
        if not match:
            errors.append(f"chapter {number}: filename does not match canonical chapter-file pattern: {filename!r}")
        else:
            if match.group("anchor") != exp_anchor:
                errors.append(
                    f"chapter {number}: filename anchor must be {exp_anchor!r}, got {match.group('anchor')!r}"
                )
            expected_prefix = f"{position:03d}--"
            if not filename.startswith(expected_prefix):
                errors.append(
                    f"chapter {number}: filename ordinal must start {expected_prefix!r}, got {filename!r}"
                )

        if status not in {"body", "index-only"}:
            errors.append(f"chapter {number}: unexpected status {status!r}")

        chapter_path = gb / rel
        if not chapter_path.is_file():
            if not allow_missing_chapters:
                errors.append(f"missing chapter file {rel_path}")
            continue
        try:
            size = chapter_path.stat().st_size
            if size > MAX_CHAPTER_BYTES:
                errors.append(f"oversized chapter file {rel_path}: {size} bytes")
            text = chapter_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"unreadable chapter file {rel_path}: {exc}")
            continue
        chapter_number_attr = re.compile(
            rf"""data-chapter-number\s*=\s*["']{re.escape(number)}["']"""
        )
        if chapter_number_attr.search(text) is None:
            errors.append(f"chapter {number}: fragment does not declare matching data-chapter-number")
        status_attr = re.compile(
            rf"""data-status\s*=\s*["']{re.escape(str(status))}["']"""
        )
        if status in {"body", "index-only"} and status_attr.search(text) is None:
            errors.append(f"chapter {number}: fragment does not declare matching data-status={status!r}")

    for label, values in [
        ("chapter numbers", numbers),
        ("anchors", anchors),
        ("paths", paths),
        ("orders", orders),
    ]:
        if len(values) != len(set(values)):
            errors.append(f"duplicate {label}")

    for required in REQUIRED_NUMBERS:
        if required not in numbers:
            errors.append(f"missing required chapter identity {required}")

    index_only = [
        str(record.get("number"))
        for record in records
        if record.get("status") == "index-only"
    ]
    if index_only != EXPECTED_INDEX_ONLY_NUMBERS:
        errors.append(f"unexpected index-only chapter set: {index_only!r}")
    body_count = sum(1 for record in records if record.get("status") == "body")
    if body_count != EXPECTED_BODY:
        errors.append(f"expected {EXPECTED_BODY} body chapters, got {body_count}")

    front = index.get("front_matter")
    if not isinstance(front, dict):
        errors.append("book-index front_matter must be an object")
    else:
        if front.get("anchor") != "front-matter":
            errors.append("front_matter anchor must be 'front-matter'")
        front_path = front.get("path")
        if not isinstance(front_path, str) or not (gb / front_path).is_file():
            errors.append(f"missing front matter file {front_path!r}")

    required_runtime = [
        gb / "index.html",
        gb / "great-book.css",
        root / "app" / "great-book-reader.js",
    ]
    for path in required_runtime:
        if not path.is_file():
            errors.append(f"missing runtime file {safe_rel(root, path)}")

    public_index = gb / "index.html"
    if public_index.is_file():
        try:
            public_html = public_index.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"unreadable public reader shell: {exc}")
        else:
            if "Reader restoration in progress" in public_html:
                errors.append("public Great Book route is still a restoration placeholder")
            for marker in READER_MARKERS:
                if marker not in public_html:
                    errors.append(f"public Great Book reader shell missing marker: {marker}")

    chapter_dir = gb / "chapters"
    if chapter_dir.is_dir():
        actual_files = {p.relative_to(gb) for p in chapter_dir.glob("*.html")}
        extras = sorted(actual_files - referenced_files)
        if extras:
            errors.append(
                "unreferenced chapter files: " + ", ".join(str(p) for p in extras[:20])
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to the parent of scripts/)",
    )
    parser.add_argument(
        "--allow-missing-chapters",
        action="store_true",
        help="Validate manifests/naming/runtime while allowing an incomplete incremental chapter directory",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = validate(root, allow_missing_chapters=args.allow_missing_chapters)
    if errors:
        print("Great Book validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    mode = "incremental" if args.allow_missing_chapters else "complete"
    print(
        f"Great Book validation passed ({mode}): "
        f"{EXPECTED_CHAPTERS} identities across four shards; decimal anchors and filenames are hyphen-safe."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
