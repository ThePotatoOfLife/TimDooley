from __future__ import annotations

OPTIONAL_METADATA = (
    "status",
    "entity",
    "implementation_notes",
    "validation_rules",
    "acquisition_plan",
)


def collect_missing_optional_metadata(rows):
    grouped = {key: [] for key in OPTIONAL_METADATA}
    for rel, data in rows:
        for key in OPTIONAL_METADATA:
            if key not in data:
                grouped[key].append(rel)
    return {key: paths for key, paths in grouped.items() if paths}


def format_advisory_summary(grouped, sample_limit=4):
    lines = []
    for key, paths in grouped.items():
        count = len(paths)
        shown = paths[:sample_limit]
        suffix = ""
        if count > sample_limit:
            suffix = f", +{count - sample_limit} more"
        noun = "blueprint" if count == 1 else "blueprints"
        lines.append(f"{key}: missing from {count} {noun} ({', '.join(shown)}{suffix})")
    return lines
