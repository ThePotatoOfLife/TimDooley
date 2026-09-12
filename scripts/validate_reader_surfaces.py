#!/usr/bin/env python3
"""Validate the semantic contract for the public reader surfaces.

This intentionally checks durable structure and concepts, not exact paragraphs.
Questions are presentation over existing canonical owners; the validator must not
turn reader copy into a second content database.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRIMARY = (
    ("tim-dooley/", "Tim Dooley"),
    ("religion/", "Religion"),
    ("philosophy/", "Philosophy"),
    ("science/", "Science"),
    ("world-map/", "World Map"),
)


def read(rel: str, errors: list[str]) -> str:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing reader surface: {rel}")
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def require(text: str, marker: str, owner: str, errors: list[str]) -> None:
    if marker not in text:
        errors.append(f"{owner} missing reader marker: {marker}")


def require_absent(text: str, marker: str, owner: str, errors: list[str]) -> None:
    if marker in text:
        errors.append(f"{owner} must not contain deprecated/runtime marker: {marker}")


def require_any(text: str, markers: tuple[str, ...], owner: str, label: str, errors: list[str]) -> None:
    if not any(marker.lower() in text.lower() for marker in markers):
        errors.append(f"{owner} missing {label}: expected one of {markers}")


def question_count(text: str) -> int:
    return len(re.findall(r'class=["\'][^"\']*\bquestion-(?:preview|stub)\b', text, flags=re.I))


def validate_projection_surface(text: str, owner: str, errors: list[str]) -> None:
    matches = re.findall(
        r'<(?:section|nav)\b[^>]*data-projection-surface(?:=["\'][^"\']*["\'])?[^>]*>(.*?)</(?:section|nav)>',
        text,
        flags=re.I | re.S,
    )
    if len(matches) != 1:
        errors.append(f"{owner} must contain exactly one compact data-projection-surface; found {len(matches)}")
        return
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', matches[0], flags=re.I)
    if len(dict.fromkeys(hrefs)) < 2:
        errors.append(f"{owner} projection surface must expose at least two distinct deeper routes")
    forbidden = ("data/", "knowledge/", ".json", "root.js", "index.html#node=")
    if any(token in matches[0] for token in forbidden):
        errors.append(f"{owner} projection surface leaks backend filenames or retired routing")


def main() -> int:
    errors: list[str] = []

    home = read("index.html", errors)
    tim = read("tim-dooley/index.html", errors)
    religion = read("religion/index.html", errors)
    bible = read("traditions/bible/index.html", errors)
    bible_js = read("app/bible-study.js", errors)
    philosophy = read("philosophy/index.html", errors)
    science = read("science/index.html", errors)
    world = read("world-map/index.html", errors)

    # Home: exactly five primary doors, each carrying two questions.
    require(home, 'data-reader-surface="home"', "index.html", errors)
    require(home, 'class="project-purpose"', "index.html", errors)
    require(home, 'class="secondary-threads"', "index.html", errors)
    nav = re.search(r'<nav class="sections"[^>]*>(.*?)</nav>', home, flags=re.I | re.S)
    if not nav:
        errors.append("index.html missing canonical sections navigation")
    else:
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', nav.group(1))
        expected = [href for href, _ in PRIMARY]
        if hrefs != expected:
            errors.append(f"homepage primary navigation must contain exactly five doors in order; found {hrefs}")
        for href, label in PRIMARY:
            match = re.search(rf'<a\b[^>]*href=["\']{re.escape(href)}["\'][^>]*>(.*?)</a>', nav.group(1), flags=re.I | re.S)
            if not match:
                errors.append(f"homepage missing primary door {label}")
            elif question_count(match.group(1)) < 2:
                errors.append(f"homepage door {label} must preview at least two natural questions")
    footer = re.search(r'<footer\b[^>]*>(.*?)</footer>', home, flags=re.I | re.S)
    if footer and 'timeline/' in footer.group(1).lower():
        errors.append("homepage footer must not treat Timeline as utility navigation")

    # Tim: identity, development, purpose, and Timeline as a principal route.
    require(tim, 'data-reader-surface="tim"', "tim-dooley/index.html", errors)
    if question_count(tim) < 3:
        errors.append("Tim reader surface needs at least three compact question stubs")
    require_any(tim, ("Who is Tim Dooley?",), "tim-dooley/index.html", "identity question", errors)
    require_any(tim, ("What changed over time?", "How did"), "tim-dooley/index.html", "development question", errors)
    require_any(tim, ("mission", "trying to do", "purpose"), "tim-dooley/index.html", "purpose/mission question", errors)
    require(tim, 'href="../timeline/"', "tim-dooley/index.html", errors)
    require_any(tim, ("Tim/Father", "Tim / Father"), "tim-dooley/index.html", "Tim/Father distinction", errors)
    require_any(tim, ("Thomas/Son", "Thomas / Son"), "tim-dooley/index.html", "Thomas/Son distinction", errors)
    validate_projection_surface(tim, "tim-dooley/index.html", errors)

    # Religion: broad inquiry, but Bible comparison must be an obvious primary next step.
    require(religion, 'data-reader-surface="religion"', "religion/index.html", errors)
    if question_count(religion) < 6:
        errors.append("Religion reader surface needs at least six compact question stubs")
    for label, markers in (
        ("Potatoism", ("What is Potatoism?",)),
        ("Christianity", ("Christianity", "Jesus")),
        ("Judaism", ("Judaism", "Jewish")),
        ("chosenness", ("chosen", "chosenness", "covenant")),
        ("Islam/Qur'an", ("Islam", "Qur’an", "Qur'an")),
    ):
        require_any(religion, markers, "religion/index.html", label, errors)
    require(religion, 'href="../traditions/bible/"', "religion/index.html", errors)
    require(religion, 'class="bible-lab-cta"', "religion/index.html", errors)
    require_any(religion, ("Bible comparison", "comparison laboratory", "parallels"), "religion/index.html", "prominent Bible comparison introduction", errors)
    require_any(religion, ("filter", "shuffle", "explore"), "religion/index.html", "Bible lab interaction description", errors)
    require_any(religion, ("resemblance is not identity", "similarity is not identity", "structural resemblance is not identity"), "religion/index.html", "comparison boundary", errors)
    validate_projection_surface(religion, "religion/index.html", errors)

    # Bible: guided entry first, filters second, canonical runtime only.
    require(bible, 'class="comparison-intro"', "traditions/bible/index.html", errors)
    require(bible, 'class="featured-arcs"', "traditions/bible/index.html", errors)
    require(bible, 'id="shuffle-comparisons"', "traditions/bible/index.html", errors)
    require(bible, 'id="operator"', "traditions/bible/index.html", errors)
    for label in ("Jesus / Son", "Father / House", "Door / Ladder", "God / Presence", "Garden / Spirit"):
        require_any(bible, (label,), "traditions/bible/index.html", f"featured arc {label}", errors)
    require(bible_js, "biblical-syncretism-field.json", "app/bible-study.js", errors)
    require_absent(bible_js, "biblical-overlap-wave-", "app/bible-study.js", errors)

    # Philosophy: inquiry before/alongside the preserved sayings.
    require(philosophy, 'data-reader-surface="philosophy"', "philosophy/index.html", errors)
    if question_count(philosophy) < 4:
        errors.append("Philosophy needs at least four inquiry stubs")
    require_any(philosophy, ("What makes a claim true?", "truth"), "philosophy/index.html", "truth/evidence inquiry", errors)
    require_any(philosophy, ("relationship-first", "relation before isolation"), "philosophy/index.html", "relationship-first inquiry", errors)
    require(philosophy, 'class="sayings"', "philosophy/index.html", errors)
    validate_projection_surface(philosophy, "philosophy/index.html", errors)

    # Science: orientation must preserve the actual library.
    require(science, 'data-reader-surface="science"', "science/index.html", errors)
    if question_count(science) < 4:
        errors.append("Science needs at least four orientation questions")
    require_any(science, ("formal model", "formalized"), "science/index.html", "formal-model boundary", errors)
    require_any(science, ("analogy", "metaphor"), "science/index.html", "analogy/metaphor boundary", errors)
    require_any(science, ("falsifi", "tested", "testing"), "science/index.html", "testing/falsifiability", errors)
    for marker in ('id="science-search"', 'id="science-field"', 'id="science-type"', '<!-- SCIENCE_CATALOG_STATIC -->'):
        require(science, marker, "science/index.html", errors)
    validate_projection_surface(science, "science/index.html", errors)

    # World Map: questions teach the application without creating another toolbar.
    require(world, 'data-reader-surface="world-map"', "world-map/index.html", errors)
    require(world, 'class="map-inquiry"', "world-map/index.html", errors)
    if question_count(world) < 3:
        errors.append("World Map initial inspector needs at least three conceptual questions")
    require_any(world, ("How are countries connected?",), "world-map/index.html", "relationship question", errors)
    for marker in ('id="map"', 'id="compare"', 'id="relationType"', 'id="traceDepth"', 'id="timeMode"', 'src="./3d-bootstrap.js"'):
        require(world, marker, "world-map/index.html", errors)
    if 'id="questionMenu"' in world or 'id="inquiryMenu"' in world:
        errors.append("World Map question layer must not introduce a persistent top-level menu")
    validate_projection_surface(world, "world-map/index.html", errors)

    if errors:
        print("READER SURFACE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("READER SURFACE VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
