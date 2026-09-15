#!/usr/bin/env python3
"""Normalize visitor-facing navigation in the generated Pages artifact.

The repository intentionally preserves historical/internal names and research strata.
This pass only cleans the deployed visitor surface: retired homepage branch hashes,
parent-hub continuity, duplicate navigation choices, visitor-facing vocabulary, and
small public-only capability projections that should not mutate legacy source strata.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
ROOT_BRANCH_HREF = re.compile(
    r'''href=(?P<quote>["'])(?P<prefix>(?:\.\./|\./)*)#branch=(?P<branch>[^"']+)(?P=quote)''',
    re.I,
)
ABSOLUTE_ROOT_BRANCH = "https://thepotatooflife.github.io/TimDooley/#branch="
ABSOLUTE_EXPLORE_BRANCH = "https://thepotatooflife.github.io/TimDooley/explore/#branch="
PUBLIC_LABEL_REPLACEMENTS = (
    (">Timeline</a>", ">Timeline</a>"),
    (">Corporium</a>", ">Collection</a>"),
    (">Source authority</a>", ">Sources</a>"),
    (">Tim dossier</a>", ">Tim Dooley</a>"),
    ("← Potato of Life archive</a>", "← Home</a>"),
)
LEGACY_TTS_READERS = {
    "shadow-farm/index.html": {
        "id": "shadow-farm",
        "root": ".page",
        "label": "The Farm & Trees of Strife",
        "all_label": "Whole deep reader",
        "exclude": "#shadow-farm-tts,.nav",
        "asset_prefix": "../",
    },
}


def patch_text(path: Path, replacements: tuple[tuple[str, str], ...] = ()) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def normalize_public_surface(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text

    def route(match: re.Match[str]) -> str:
        quote = match.group("quote")
        prefix = match.group("prefix")
        branch = match.group("branch")
        return f"href={quote}{prefix}explore/#branch={branch}{quote}"

    text = ROOT_BRANCH_HREF.sub(route, text)
    text = text.replace(ABSOLUTE_ROOT_BRANCH, ABSOLUTE_EXPLORE_BRANCH)
    for old, new in PUBLIC_LABEL_REPLACEMENTS:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def inject_legacy_tts_reader(text: str, config: dict[str, str]) -> str:
    """Project the shared long-form TTS reader into copied legacy HTML.

    This is intentionally a generated-artifact transform. It keeps legacy source
    byte-stable while giving mature public readers the same shared speech capability.
    The transform is fail-closed and idempotent.
    """
    reader_id = str(config.get("id", "")).strip()
    root_selector = str(config.get("root", "")).strip()
    if not reader_id or not root_selector:
        return text

    host_id = f"{reader_id}-tts"
    if f'id="{host_id}"' in text or f"id='{host_id}'" in text:
        return text

    if not re.search(r"</head\s*>", text, flags=re.I) or not re.search(r"</body\s*>", text, flags=re.I):
        return text
    main_match = re.search(r"<main\b[^>]*>", text, flags=re.I)
    if not main_match:
        return text

    prefix = str(config.get("asset_prefix", ""))
    label = html.escape(str(config.get("label", "Read aloud")), quote=True)
    all_label = html.escape(str(config.get("all_label", "Whole reader")), quote=True)
    exclude = html.escape(str(config.get("exclude", f"#{host_id}")), quote=True)
    root_attr = html.escape(root_selector, quote=True)
    id_attr = html.escape(reader_id, quote=True)

    stylesheet = f'<link rel="stylesheet" href="{prefix}app/tts-drawer.css">'
    host = (
        f'<div id="{html.escape(host_id, quote=True)}" data-tts-longform '
        f'data-tts-root="{root_attr}" data-tts-id="{id_attr}" data-tts-label="{label}" '
        f'data-tts-all-label="{all_label}" data-tts-selection-label="Selection" '
        f'data-tts-exclude="{exclude}"></div>'
    )
    scripts = (
        f'<script src="{prefix}app/tts-reader.js"></script>'
        f'<script src="{prefix}app/tts-drawer.js"></script>'
        f'<script src="{prefix}app/longform-tts-adapter.js"></script>'
    )

    text = re.sub(r"</head\s*>", stylesheet + "</head>", text, count=1, flags=re.I)

    # Prefer placing the reader immediately after the page's first navigation row.
    # Legacy readers usually begin with navigation; falling back to the main opening
    # tag still keeps the player inside its configured readable root.
    nav_match = re.search(r"<nav\b[^>]*>.*?</nav\s*>", text[main_match.end():], flags=re.I | re.S)
    if nav_match:
        insert_at = main_match.end() + nav_match.end()
    else:
        insert_at = main_match.end()
    text = text[:insert_at] + host + text[insert_at:]
    text = re.sub(r"</body\s*>", scripts + "</body>", text, count=1, flags=re.I)
    return text


def patch_legacy_tts_readers(out: Path = OUT) -> set[Path]:
    changed: set[Path] = set()
    for rel, config in LEGACY_TTS_READERS.items():
        path = out / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        projected = inject_legacy_tts_reader(text, config)
        if projected == text:
            continue
        path.write_text(projected, encoding="utf-8")
        changed.add(path)
    return changed


def main() -> None:
    if not OUT.exists():
        raise SystemExit("_site does not exist; build_site.py must run first")

    changed: set[Path] = set()
    for page in OUT.rglob("*.html"):
        if page == OUT / "explore" / "index.html":
            continue
        if normalize_public_surface(page):
            changed.add(page)

    changed.update(patch_legacy_tts_readers(OUT))

    religion = OUT / "religion" / "index.html"
    if patch_text(
        religion,
        (
            (
                '<div class="deep" aria-label="Deeper religion routes"><a href="../context/source-authority/">Sources & evidence</a><a href="../explore/#branch=traditions">Deep traditions archive</a><a href="../explore/#branch=spirit">Spirit & theology archive</a><a href="../index-a-z/">A–Z</a></div>',
                '<div class="deep" aria-label="Deeper religion routes"><a href="../context/source-authority/">Sources & evidence</a><a href="../index-a-z/">A–Z</a><a href="../explore/">Explore relationships</a></div>',
            ),
        ),
    ):
        changed.add(religion)

    bible = OUT / "traditions" / "bible" / "index.html"
    if patch_text(
        bible,
        (
            (
                '<nav class="page-nav" aria-label="Page navigation"><a href="../../">← Home</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../timeline/">Timeline</a><a href="../../context/source-authority/">Sources</a><a href="../../faq/">FAQ</a></nav>',
                '<nav class="page-nav" aria-label="Page navigation"><a href="../../religion/">← Religion</a><a href="../../">Home</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../timeline/">Timeline</a><a href="../../context/source-authority/">Sources</a></nav>',
            ),
        ),
    ):
        changed.add(bible)

    vesica = OUT / "traditions" / "vesica" / "index.html"
    if patch_text(
        vesica,
        (
            (
                '<nav class="nav"><a href="../../">← Home</a><a href="../../context/">Context &amp; evidence</a><a href="../../tim-dooley/">Tim Dooley</a><a href="../../science/spudlight/">Spudlight</a></nav>',
                '<nav class="nav"><a href="../../religion/">← Religion</a><a href="../../">Home</a><a href="../bible/">Bible</a><a href="../../science/">Science</a><a href="../../context/source-authority/">Sources</a></nav>',
            ),
            (
                '"name":"Traditions","item":"https://thepotatooflife.github.io/TimDooley/explore/#branch=traditions"',
                '"name":"Religion","item":"https://thepotatooflife.github.io/TimDooley/religion/"',
            ),
        ),
    ):
        changed.add(vesica)

    print(f"Applied public navigation cleanup to {len(changed)} generated page(s).")


if __name__ == "__main__":
    main()
