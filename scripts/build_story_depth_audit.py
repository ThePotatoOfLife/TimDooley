from __future__ import annotations

import json
import sys
from pathlib import Path

from validate_story_archive import scan_public_story_entries

DEPTHS = ["FRAGMENT", "ANECDOTE", "SCENE", "TRANSCRIPT_DEPTH", "LITERARY_COMPLETE"]
MODES = ["documentary", "literary", "mixed"]


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def build_story_depth_audit(root: Path) -> dict:
    story_dir = root / "knowledge" / "story"
    registry_data = load(story_dir / "story-registry.json", {"enforcement": "migration", "stories": []})
    source_data = load(story_dir / "source-records.json", {"sources": []})
    registry = registry_data.get("stories", [])
    sources = {x.get("id"): x for x in source_data.get("sources", []) if x.get("id")}
    public = scan_public_story_entries(root)
    public_ids = {x.get("id") for x in public}
    reg_map = {x.get("id"): x for x in registry if x.get("id")}

    published = {
        "total": len(public),
        "main": sum(1 for x in public if x.get("story_type") == "main"),
        "side": sum(1 for x in public if x.get("story_type") == "side"),
    }
    depths = {depth: sum(1 for x in registry if x.get("depth") == depth) for depth in DEPTHS}
    modes = {mode: sum(1 for x in registry if x.get("mode") == mode) for mode in MODES}
    full_html = [x for x in public if x.get("has_full_story")]
    qualified = [x for x in full_html if x.get("id") in reg_map and reg_map[x.get("id")].get("full_story_allowed") is True]
    incorrect = sorted(x.get("id") for x in full_html if x.get("id") in reg_map and reg_map[x.get("id")].get("full_story_allowed") is not True)
    unregistered_full = sorted(x.get("id") for x in full_html if x.get("id") not in reg_map)

    unresolved = []
    for item in registry:
        for source_id in item.get("source_ids", []):
            src = sources.get(source_id)
            if not src or not isinstance(src.get("locator"), dict) or not src.get("locator"):
                unresolved.append({"story_id": item.get("id"), "source_id": source_id})

    recovery = []
    for item in registry:
        targets = item.get("recovery_targets", [])
        if targets:
            recovery.append({"story_id": item.get("id"), "depth": item.get("depth"), "targets": targets})
    recovery.sort(key=lambda x: x["story_id"] or "")

    return {
        "schema_version": 1,
        "enforcement": registry_data.get("enforcement", "migration"),
        "published": published,
        "registry": {"registered": len(registry), "unregistered": len(public_ids - set(reg_map))},
        "modes": modes,
        "depths": depths,
        "full_story": {
            "html_total": len(full_html),
            "qualified_registered": len(qualified),
            "incorrectly_promoted_registered": incorrect,
            "unregistered_full_story": unregistered_full,
        },
        "unresolved_source_locators": sorted(unresolved, key=lambda x: ((x.get("story_id") or ""), (x.get("source_id") or ""))),
        "recovery_priorities": recovery,
    }


def audit_is_current(root: Path) -> bool:
    expected = build_story_depth_audit(root)
    path = root / "knowledge" / "story" / "story-depth-audit.json"
    return load(path, None) == expected


def write_story_depth_audit(root: Path) -> Path:
    data = build_story_depth_audit(root)
    out = root / "knowledge" / "story" / "story-depth-audit.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parents[1]
    if "--check" in argv:
        if not audit_is_current(root):
            print("Story depth audit is stale; expected report follows:")
            print(json.dumps(build_story_depth_audit(root), indent=2, ensure_ascii=False))
            return 1
        print("Story depth audit is current")
        return 0
    path = write_story_depth_audit(root)
    print(path.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
