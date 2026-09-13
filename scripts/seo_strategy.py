#!/usr/bin/env python3
"""Pure route/content strategy for search intent and structured-data projection."""
from __future__ import annotations

from dataclasses import dataclass

SITE_NAME = "The Potato of Life"


@dataclass(frozen=True)
class Strategy:
    kind: str
    schema_type: str
    topic: str
    title: str | None = None
    description: str | None = None


ROUTE_STRATEGIES: dict[str, Strategy] = {
    "": Strategy(
        "home",
        "CollectionPage",
        "Tim Dooley and The Potato of Life archive",
        "Tim Dooley & The Potato of Life — Archive, Ideas, Timeline & Research",
        "Explore the Tim Dooley and Potato of Life archive: biography, timeline, religion, philosophy, science, evidence, North, world systems and source-backed research.",
    ),
    "tim-dooley": Strategy(
        "tim-profile",
        "ProfilePage",
        "Tim Dooley",
        "Tim Dooley — Biography, Timeline, Ideas & Evidence",
        "A source-aware guide to Tim Dooley: biography, public development, ideas, timeline, evidence boundaries, theology, philosophy and the Potato of Life archive.",
    ),
    "potatoism": Strategy(
        "potatoism",
        "CollectionPage",
        "Potatoism and the Potato of Life framework",
    ),
    "traditions/bible": Strategy(
        "bible",
        "Article",
        "Tim Dooley and biblical comparison research",
        "Tim Dooley and the Bible — Parallels, Sources & Countertexts",
        "Study Tim Dooley and the Bible through dated project material, biblical passages, source direction, structural parallels, countertexts, mismatches and provenance.",
    ),
    "north": Strategy(
        "north",
        "Article",
        "North, Axis and North of North",
        "North of North & the Axis — Tim Dooley’s Sacred Geography",
        "Explore North, North of North, Axis, throne, sacred geography and their development inside the Tim Dooley / Potato of Life archive, with links to chronology and evidence.",
    ),
    "science": Strategy(
        "science",
        "CollectionPage",
        "Tim Dooley science and formal models",
        "Tim Dooley Science — Theories, Equations & Research Map",
        "Explore Tim Dooley science material, equations, formal models, research papers, comparators, model testing and the boundary between project theory and established science.",
    ),
    "timeline": Strategy(
        "timeline",
        "CollectionPage",
        "Tim Dooley timeline",
        "Tim Dooley Timeline — Development of the Potato of Life",
        "Follow the dated development of Tim Dooley and the Potato of Life: major events, role changes, public statements, research unlocks and source-aware chronology.",
    ),
    "context/source-authority": Strategy(
        "source-authority",
        "Article",
        "source authority and provenance",
        "Sources & Evidence — Tim Dooley / Potato of Life Archive",
        "How the Tim Dooley archive ranks sources, preserves first-party provenance, separates later interpretation from original material, and handles corrections and uncertainty.",
    ),
    "philosophy": Strategy(
        "philosophy",
        "CollectionPage",
        "Potato of Life philosophy",
        "Potato of Life Philosophy — Tim Dooley’s Ideas & Frameworks",
        "Explore the philosophy of the Potato of Life: relation, source and manifestation, Door, Axis, meaning, transformation, ethics and Tim Dooley’s recurring formulations.",
    ),
    "religion": Strategy(
        "religion",
        "CollectionPage",
        "Potato of Life religion and comparative theology",
        "Tim Dooley Religion — Bible, Potatoism & Comparative Theology",
        "Explore Tim Dooley’s religious and comparative framework: Potatoism, Bible research, Christian imagery, mythology, source boundaries and related traditions.",
    ),
}


RELATED: dict[str, tuple[str, ...]] = {
    "": ("tim-dooley", "timeline", "context/source-authority", "religion", "science"),
    "tim-dooley": ("timeline", "tim-dooley/evidence", "tim-dooley/public-witness", "context/source-authority"),
    "potatoism": ("philosophy", "religion", "tim-dooley", "timeline"),
    "traditions/bible": ("religion", "timeline", "context/source-authority", "tim-dooley/biblical-case"),
    "north": ("world-map", "timeline", "philosophy", "context/source-authority"),
    "science": ("science/research-map", "context/source-authority", "philosophy"),
    "timeline": ("tim-dooley", "context/source-authority", "religion", "science"),
    "context/source-authority": ("tim-dooley/evidence", "timeline", "tim-dooley", "traditions/bible"),
    "philosophy": ("tim-dooley", "science", "religion", "timeline"),
    "religion": ("traditions/bible", "tim-dooley", "timeline", "context/source-authority"),
}


def _normalize(route: str) -> str:
    return route.strip().strip("/")


def classify_route(route: str) -> str:
    route = _normalize(route)
    if route in ROUTE_STRATEGIES:
        return ROUTE_STRATEGIES[route].kind
    if route.startswith("science/papers/"):
        return "science-paper"
    if route.startswith("questions/") or route == "questions":
        return "question"
    if route.startswith("records/"):
        return "record"
    if route == "tim-dooley/evidence":
        return "source-authority"
    if route.startswith("tim-dooley/"):
        return "tim-research"
    if route.startswith("potatoism/"):
        return "potatoism-topic"
    if route.startswith("science/"):
        return "science-topic"
    if route.startswith("north/"):
        return "north"
    if route.startswith("timeline/") or route == "chronology":
        return "timeline-topic"
    if route.startswith("context/"):
        return "source-authority"
    if route.startswith("traditions/bible") or route.startswith("religion/"):
        return "bible"
    return "support"


def _looks_generic_title(title: str) -> bool:
    value = " ".join(title.split()).strip().casefold()
    if not value:
        return True
    return value in {
        SITE_NAME.casefold(),
        "tim dooley",
        "religion",
        "philosophy",
        "science",
        "timeline",
        "north",
        "north axis — world map",
    } or value.endswith(" — the potato of life") and len(value) < 34


def _looks_generic_description(description: str) -> bool:
    value = " ".join(description.split()).strip().casefold()
    return len(value) < 70 or value.startswith("explore this page") or value.startswith("explore the archive")


def metadata_for(route: str, current_title: str, current_description: str) -> dict[str, str]:
    route = _normalize(route)
    strategy = ROUTE_STRATEGIES.get(route)
    title = " ".join(current_title.split()).strip()
    description = " ".join(current_description.split()).strip()
    if strategy and strategy.title and _looks_generic_title(title):
        title = strategy.title
    if strategy and strategy.description and _looks_generic_description(description):
        description = strategy.description
    return {"title": title, "description": description}


def schema_profile(route: str) -> dict[str, object]:
    route = _normalize(route)
    kind = classify_route(route)
    strategy = ROUTE_STRATEGIES.get(route)
    if strategy:
        schema_type = strategy.schema_type
        topic = strategy.topic
    elif kind == "science-paper":
        schema_type, topic = "ScholarlyArticle", "research paper"
    elif kind in {"question", "support"}:
        schema_type, topic = "WebPage", "archive topic"
    elif kind == "record":
        schema_type, topic = "Article", "canonical source record"
    elif kind in {"science-topic", "timeline-topic", "potatoism-topic", "tim-research", "north", "bible", "source-authority"}:
        schema_type, topic = "Article", kind.replace("-", " ")
    else:
        schema_type, topic = "WebPage", kind.replace("-", " ")
    profile: dict[str, object] = {"kind": kind, "schema_type": schema_type, "topic": topic}
    if schema_type == "ProfilePage":
        profile["main_entity"] = {"@type": "Person", "name": "Tim Dooley"}
    return profile


def related_routes(route: str) -> tuple[str, ...]:
    route = _normalize(route)
    if route in RELATED:
        return RELATED[route]
    kind = classify_route(route)
    if kind == "science-paper":
        return ("science", "science/research-map", "context/source-authority")
    if kind == "science-topic":
        return ("science", "science/research-map", "context/source-authority")
    if kind == "question":
        return ("tim-dooley", "timeline", "context/source-authority")
    if kind == "record":
        return ("context/source-authority", "timeline")
    if kind == "tim-research":
        return ("tim-dooley", "timeline", "context/source-authority")
    if kind == "potatoism-topic":
        return RELATED["potatoism"]
    if kind == "timeline-topic":
        return ("timeline", "tim-dooley", "context/source-authority")
    return ()
