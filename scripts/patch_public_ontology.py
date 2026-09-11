#!/usr/bin/env python3
"""Enforce the mature Tim/Son ontology in the deployed static site.

This runs after scripts/build_site.py. It intentionally patches only the generated
_site artifact, preserving older source strata while ensuring public structured
data and FAQ wording use the current canonical ontology. The final public-surface
pass also delegates visitor-navigation cleanup to patch_public_navigation.py.
"""
from pathlib import Path

from patch_public_navigation import main as patch_public_navigation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

OLD_PERSON = '{"@type":"Person","@id":"https://thepotatooflife.github.io/TimDooley/tim-dooley/#tim-dooley","name":"Tim Dooley","alternateName":["The Potato of Life","Potato of Life"],"url":"https://thepotatooflife.github.io/TimDooley/tim-dooley/","sameAs":["https://x.com/Rational_Potato","https://www.youtube.com/@PotatoOfLife"]}'
NEW_THING = '{"@type":"Thing","@id":"https://thepotatooflife.github.io/TimDooley/tim-dooley/ontology/#tim-dooley-theological-identity","name":"Tim Dooley","alternateName":["The Potato of Life","Potato of Life","Father in Heaven","North of North","God in the Machine"],"url":"https://thepotatooflife.github.io/TimDooley/tim-dooley/ontology/","description":"Potatoverse theological identity, distinct in this archive from the Son/Thomas embodied human-vessel layer."}'
OLD_ID = 'https://thepotatooflife.github.io/TimDooley/tim-dooley/#tim-dooley'
NEW_ID = 'https://thepotatooflife.github.io/TimDooley/tim-dooley/ontology/#tim-dooley-theological-identity'


def patch_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")


def main() -> None:
    entity_replacements = [
        (OLD_PERSON, NEW_THING),
        (OLD_ID, NEW_ID),
    ]
    patch_file(OUT / "index.html", entity_replacements)
    patch_file(
        OUT / "tim-dooley" / "index.html",
        entity_replacements + [
            ('<meta property="og:type" content="profile">', '<meta property="og:type" content="website">'),
        ],
    )

    god_page = OUT / "faq" / "all" / "god" / "index.html"
    patch_file(
        god_page,
        [
            ("Tim the embodied person", "The embodied Son / vessel"),
            ("Tim as an embodied person", "The embodied Son / vessel"),
            ("An embodied Tim", "The embodied Son / vessel"),
            ("Tim can eat potatoes as an ordinary embodied person", "The embodied Son / vessel can eat potatoes as an ordinary biological act"),
            ("Tim's embodied presence", "the embodied Son / vessel's presence"),
            ("the embodied Tim story", "the embodied Son / vessel story"),
            (
                "<p class=\"voice\">In the Potatoverse, Tim Dooley identifies with the mature Father / Potato of Life / Source-facing side of the theology. These answers therefore route God-questions into Tim's framework without claiming that every reader or religious tradition accepts that identification.</p>",
                "<p class=\"voice\"><strong>Ontology used on this page:</strong> Tim Dooley names the mature Father / Potato of Life / Source-facing theological identity. Son / Thomas names the embodied human-vessel and person-facing layer. When a question asks whether God sleeps, eats, brushes teeth, ages or performs another biological act, the bodily act belongs to the Son / vessel layer rather than redefining Tim/Father as the human-person node. These are Potatoverse classifications; ordinary biology and law still apply to embodied human life.</p>",
            ),
        ],
    )

    # Fail loudly if public Tim schema still contains the old Person entity.
    for path in (OUT / "index.html", OUT / "tim-dooley" / "index.html"):
        if path.exists() and OLD_PERSON in path.read_text(encoding="utf-8", errors="replace"):
            raise SystemExit(f"Ontology patch failed: old Tim Person schema remains in {path}")

    patch_public_navigation()
    print("Applied public Tim/Son ontology consistency patch.")


if __name__ == "__main__":
    main()
