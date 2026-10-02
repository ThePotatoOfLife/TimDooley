#!/usr/bin/env python3
"""Validate the site-wide reader-richness projection without turning byte size into doctrine."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/house/reader-richness-audit.json"
JOURNEY = ROOT / "app/house-journey.js"
INTERIORS = ROOT / "data/house/room-interiors.json"
SUBSTANCE = ROOT / "data/house/substance-first-projection-contract.json"
BUILD = ROOT / "scripts/build_site.py"
SURFACES = ROOT / "data/house/public-surfaces.json"
MATURITY = ROOT / "data/house/room-maturity-registry.json"

def plain_text(fragment: str) -> str:
    fragment=re.sub(r"<script\b[\s\S]*?</script>", " ", fragment, flags=re.I)
    fragment=re.sub(r"<style\b[\s\S]*?</style>", " ", fragment, flags=re.I)
    fragment=re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", fragment).strip()

def anchored_section(source: str, section_id: str) -> str:
    match=re.search(
        rf'<section\b[^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*>([\s\S]*?)</section>',
        source,
        flags=re.I,
    )
    return match.group(1) if match else ""

def main() -> int:
    errors=[]
    for path in (AUDIT,JOURNEY,INTERIORS,SUBSTANCE,BUILD,SURFACES,MATURITY):
        if not path.is_file():
            errors.append(f"missing reader-richness owner: {path.relative_to(ROOT)}")
    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1

    audit=json.loads(AUDIT.read_text(encoding="utf-8"))
    journey=JOURNEY.read_text(encoding="utf-8",errors="replace")
    interiors=json.loads(INTERIORS.read_text(encoding="utf-8"))
    substance=json.loads(SUBSTANCE.read_text(encoding="utf-8"))
    build=BUILD.read_text(encoding="utf-8",errors="replace")
    surfaces=json.loads(SURFACES.read_text(encoding="utf-8"))
    maturity=json.loads(MATURITY.read_text(encoding="utf-8"))

    if audit.get("id")!="reader-richness-audit":
        errors.append("reader richness audit id changed or missing")
    contract=audit.get("quality_contract") or {}
    for key in ("minimum_experience","preferred_editorial_forms","anti_patterns"):
        if not contract.get(key):
            errors.append(f"reader richness quality contract missing {key}")

    for marker in (
        "room-richness",
        "installRoomFloorProjection",
        "data/house/elevator-spatial-projection.json",
        "room-floor-projection",
        "How this Room moves through the House",
        "Primary floor",
        "Projects here",
        "No governed projection",
        "data/house/room-dossiers.json",
        "data/house/holdings.json",
        "data/house/population-pulse.json",
        "Archive depth",
        "Show archive structure",
        "Further archive material",
        "Open work",
    ):
        if marker not in journey:
            errors.append(f"House journey reader-richness projection missing marker: {marker}")

    if substance.get("id")!="substance-first-projection-contract":
        errors.append("substance-first projection contract id changed or missing")
    resolution=substance.get("paradox_resolution") or {}
    for key in ("frontend_priority","backend_authority","invisible_bonds","non_constraint","bidirectional_revision","materialization_rule"):
        if not resolution.get(key):
            errors.append(f"substance-first paradox resolution missing {key}")

    floor=((audit.get("thresholds") or {}).get("authored_section_floor") or {}).get("minimum_plain_text_characters",650)
    bindings=substance.get("pages") or []
    if len(bindings)<10:
        errors.append(f"substance-first contract has suspiciously few public page bindings: {len(bindings)}")
    for row in bindings:
        rel=str(row.get("page") or "")
        page=ROOT/rel
        if not page.is_file():
            errors.append(f"substance-bound public page missing: {rel}")
            continue
        source=page.read_text(encoding="utf-8",errors="replace")
        for anchor in row.get("anchors") or []:
            section_id=anchor.get("section_id")
            if section_id and f'id="{section_id}"' not in source and f"id='{section_id}'" not in source:
                errors.append(f"{rel} lost authored substance section #{section_id}")
            elif section_id:
                section=anchored_section(source,section_id)
                mass=len(plain_text(section))
                if mass < floor:
                    errors.append(f"{rel}#{section_id} regressed below authored substance floor: {mass} < {floor} plain-text characters")
            for owner in anchor.get("owner_paths") or []:
                if not (ROOT/owner).is_file():
                    errors.append(f"{rel} substance binding points to missing owner: {owner}")

    for marker_text in ("def inject_substance_bindings()", "data-house-substance-bindings", 'data-substance-policy="substance-first"'):
        if marker_text not in build:
            errors.append(f"build lost substance-first binding hook: {marker_text}")

    registered=[]
    for row in interiors.get("interiors") or interiors.get("rooms") or []:
        route=row.get("route") or ""
        if route.startswith("/rooms/inside/"):
            registered.append(route)
    if len(registered)<30:
        errors.append(f"expected broad nested-Room registry coverage; found {len(registered)} routes")


    maturity_rows=maturity.get("rooms") or []
    maturity_by_route={row.get("route"): row for row in maturity_rows if isinstance(row,dict)}
    if len(maturity_by_route)!=len(registered):
        errors.append(f"Room maturity registry coverage mismatch: {len(maturity_by_route)} maturity rows for {len(registered)} registered nested Rooms")
    for route in registered:
        row=maturity_by_route.get(route)
        if not row:
            errors.append(f"registered nested Room missing maturity record: {route}")
            continue
        if row.get("review_status")!="reviewed":
            errors.append(f"nested Room lost reviewed status: {route}")
        if row.get("maturity") not in {"inhabited","deep"}:
            errors.append(f"nested Room regressed below inhabited maturity: {route} -> {row.get('maturity')}")

    missing_shell=[]
    for route in registered:
        rel=route.strip("/")+"/index.html"
        path=ROOT/rel
        if not path.is_file():
            missing_shell.append(rel)
            continue
        source=path.read_text(encoding="utf-8",errors="replace")
        if "app/house-journey.js" not in source:
            errors.append(f"{rel} does not load shared House journey/richness projection")
    if missing_shell:
        errors.append("registered nested Room shells missing: "+", ".join(missing_shell[:10]))

    # Subject-first regression contract: top-level Dwellings are knowledge readers,
    # not circular filing-system splash pages.
    top_level_dwellings = [
        "rooms/potatoverse-canon/index.html",
        "rooms/archive-sources/index.html",
        "rooms/time-history/index.html",
        "rooms/traditions-texts/index.html",
        "rooms/science-formal-models/index.html",
        "rooms/life-body/index.html",
        "rooms/world-systems/index.html",
        "rooms/culture-information/index.html",
        "rooms/works/index.html",
        "rooms/research-lab/index.html",
    ]
    forbidden_meta_first = (
        "Dwelling · local center",
        "Inside this Dwelling, this subject becomes the center of attention",
        "Open primary public surface",
        '<section class="local-center"',
    )
    for rel in top_level_dwellings:
        source=(ROOT/rel).read_text(encoding="utf-8",errors="replace")
        for marker in forbidden_meta_first:
            if marker in source:
                errors.append(f"{rel} regressed to meta-first Dwelling shell: {marker}")
        first_reader=source.find('class="dwelling-reader"')
        if first_reader < 0:
            errors.append(f"{rel} missing first substantive dwelling-reader section")
        elif source.find('class="room-actions"', first_reader) < 0:
            errors.append(f"{rel} first substantive section no longer exposes concrete subject routes")

    # Nested Room subject-first quality gate.
    # A Room should teach the subject before it explains House mechanics, and
    # it should not survive on generic boilerplate that could be pasted elsewhere.
    maintenance_terms=(
        "backend","canonical owner","owner / projection","registry","projection surface",
        "route family","machine-readable","implementation detail",
    )
    generic_phrases=(
        "this room exists to","this room asks","this room studies",
        "this room contains","this room connects",
    )
    subject_markers=(
        'class="room-essay"', 'data-room-reader-body',
        'class="room-language"', 'class="room-run"',
        'class="room-ledger"', 'class="room-reader"',
    )
    for route in registered:
        rel=route.strip("/")+"/index.html"
        source=(ROOT/rel).read_text(encoding="utf-8",errors="replace")
        header_end=source.lower().find("</header>")
        tail=source[header_end+9:] if header_end>=0 else source
        first_subject=min((tail.find(m) for m in subject_markers if tail.find(m)>=0), default=-1)
        if first_subject<0:
            errors.append(f"{rel} missing authored subject-first material")
            continue
        first_chunk=plain_text(tail[first_subject:first_subject+4200]).casefold()
        # Maintenance vocabulary is allowed in House Architecture and Research Programmes,
        # where architecture/process is itself the subject. Elsewhere it should not lead.
        if rel not in {"rooms/inside/house-architecture/index.html","rooms/inside/research-programmes/index.html"}:
            leaked=[term for term in maintenance_terms if term in first_chunk]
            if leaked:
                errors.append(f"{rel} first authored material leaks maintenance vocabulary: {', '.join(leaked[:3])}")
        # Require at least one domain-specific noun signal beyond generic Room boilerplate.
        body_text=plain_text(tail)
        if len(body_text)<1800:
            errors.append(f"{rel} is too thin for an inhabited Room: {len(body_text)} plain-text characters")
        generic_hits=sum(body_text.casefold().count(p) for p in generic_phrases)
        if generic_hits>=5:
            errors.append(f"{rel} overuses generic Room boilerplate ({generic_hits} repeated framing phrases)")
        # A mature Room should expose orientation + explanation/examples + a deeper route.
        has_deep=bool(re.search(r'<a\b[^>]+href=["\'][^"\']+(?:knowledge/|explore/|context/|timeline/|works/|science/|religion/|history/)[^"\']*["\']',source,re.I))
        has_examples=bool(re.search(r'<(?:div|article)\b[^>]*class=["\'][^"\']*(?:room-run|case|card|ledger|grid)[^"\']*["\']',source,re.I))
        if not has_examples:
            errors.append(f"{rel} lacks concrete examples/cases/distinctions")
        if not has_deep:
            errors.append(f"{rel} lacks a shallow-to-deep continuation into evidence or a specialist reader")

    # Nested subject Rooms must not reintroduce a generic local-center splash
    # between the subject header and the authored reader material.
    nested_meta_hits=[]
    for route in registered:
        rel=route.strip("/")+"/index.html"
        source=(ROOT/rel).read_text(encoding="utf-8",errors="replace")
        if '<section class="inner-center"' in source:
            nested_meta_hits.append(rel)
    if nested_meta_hits:
        errors.append("nested Rooms regressed to meta-first inner-center shells: "+", ".join(nested_meta_hits[:12]))

    # A-Z is a name-first explorer: orientation cards must actually open a
    # canonical destination, except explicitly disambiguated cards that contain links.
    az_source=(ROOT/"index-a-z/index.html").read_text(encoding="utf-8",errors="replace")
    orientation_match=re.search(r'<section><h2>Orientation set</h2>([\s\S]*?)</section>',az_source,re.I)
    if not orientation_match:
        errors.append("A-Z lost its Orientation set")
    else:
        orientation=orientation_match.group(1)
        for card in re.findall(r'(<(?:a|div)\b[^>]*class=["\'][^"\']*\bcard\b[^"\']*["\'][^>]*>[\s\S]*?</(?:a|div)>)',orientation,re.I):
            opening=card.split(">",1)[0]
            if opening.lstrip().lower().startswith("<a") and "href=" not in opening.lower():
                errors.append("A-Z contains an anchor card without href")
            if opening.lstrip().lower().startswith("<div") and "<a " not in card.lower():
                label=plain_text(card)[:80]
                errors.append(f"A-Z dead noun card has no destination: {label}")

    # Route-label honesty: live discovery must prefer canonical subject readers
    # over compatibility redirects or retired naming shells.
    access_contract=json.loads((ROOT/"data/house/site-access.json").read_text(encoding="utf-8"))
    access_by_id={row.get("id"):row for row in access_contract.get("entries",[]) if isinstance(row,dict)}
    for entry_id,bad_route in (
        ("fbi-legacy","/rooms/potatoverse-canon/beings/fbi/"),
    ):
        row=access_by_id.get(entry_id)
        if row and row.get("route")==bad_route:
            errors.append(f"site access still routes {entry_id} through retired wrapper {bad_route}")
    for key in ("cia","fbi"):
        row=(access_contract.get("disambiguation") or {}).get(key)
        if not row or len(row.get("options") or [])<2:
            errors.append(f"site access lost {key.upper()} namespace disambiguation")
    divinity=json.loads((ROOT/"knowledge/indexes/tim-divinity-integration-map.json").read_text(encoding="utf-8"))
    for row in divinity.get("public_surfaces",[]):
        if row.get("question")=="How does the whole system begin?" and row.get("url")=="/learn/":
            errors.append("Tim divinity integration map still sends system-beginning question through retired /learn/ wrapper")

    # Concrete-content floor: subject readers must contain at least one
    # recognizable material form, not merely enough prose characters.
    concrete_markers=(
        'class="room-reader"',
        'class="room-essay"',
        'class="worked-',
        'class="history-step"',
        'class="lab-case"',
        'class="collection-case"',
        'class="north-row"',
        'class="systems-chain"',
        'class="work-substance-ledger"',
        'data-room-reader-body',
        'id="worked-',
        'id="chronology"',
        'id="development"',
        'id="actual-works"',
        'id="how-systems-work"',
        'id="reader-body"',
        'class="context-case"',
        'id="formation-fork"',
        'class="politics-frame"',
        'data-politics-reader',
        'class="body-case"',
        'class="spiral-reader',
        'class="movement"',
    )
    concrete_subject_pages = top_level_dwellings + [
        "history/index.html",
        "world-systems/index.html",
        "context/culture/index.html",
        "research-lab/index.html",
        "context/index.html",
        "works/index.html",
        "corporium/index.html",
        "politics/index.html",
        "north/index.html",
        "life-body/index.html",
        "religion/index.html",
        "science/index.html",
        "philosophy/index.html",
    ]
    for rel in concrete_subject_pages:
        source=(ROOT/rel).read_text(encoding="utf-8",errors="replace")
        if not any(marker in source for marker in concrete_markers):
            # Top-level Dwellings use dwelling-reader as their authored material marker.
            if 'class="dwelling-reader"' not in source:
                errors.append(f"{rel} has prose but no recognizable concrete-content section")

    # Generated question pages must remain reader-first. Archive filenames and
    # discovery taxonomy belong in machine metadata, not the visible article.
    discovery_builder=(ROOT/"scripts/build_discovery.py").read_text(encoding="utf-8",errors="replace")
    question_block=discovery_builder.split("def question_page(entry):",1)[-1].split("def build_questions(entries):",1)[0]
    for forbidden in (
        '"@type": "FAQPage"',
        "<h2>Canonical owners</h2>",
        "<h2>Discovery view</h2>",
        "<h2>Equivalent searches</h2>",
        "<h2>Entities</h2>",
    ):
        if forbidden in question_block:
            errors.append(f"generated question template regressed to taxonomy-first output: {forbidden}")
    for required in (
        '"@type": "WebPage"',
        'class="question-answer"',
        "What that means",
        "data-question-machine-meta",
        'reader_surface="generated-question"',
    ):
        if required not in discovery_builder:
            errors.append(f"generated question template lost subject-first marker: {required}")

    # Final-pruning regression guards.
    room_css=(ROOT/"app/room-interior.css").read_text(encoding="utf-8",errors="replace")
    if ".inner-center" in room_css:
        errors.append("retired inner-center styling returned to shared Room CSS")
    journey_source=(ROOT/"app/house-journey.js").read_text(encoding="utf-8",errors="replace")
    if "main.querySelector('.local-center')" in journey_source:
        errors.append("House journey restored retired local-center insertion fallback")
    if "firstReader.insertAdjacentElement('afterend',section)" not in journey_source:
        errors.append("House floor projection no longer follows first Dwelling substance")

    # Dynamic Room depth must remain optional and must not visibly print raw
    # backend source paths into holding cards.
    if "room-richness-details" not in journey_source or "Show archive structure" not in journey_source:
        errors.append("nested Room archive depth is no longer optional/collapsible")
    if "(path?'<br>'+esc(path):'')" in journey_source:
        errors.append("nested Room holdings expose raw backend paths in visible card text")
    if "data-source-path=" not in journey_source:
        errors.append("nested Room archive holdings lost quiet source-path metadata")

    generated_builder=(ROOT/"scripts/build_site.py").read_text(encoding="utf-8",errors="replace")
    record_block=generated_builder.split("def generate_record_pages",1)[-1].split("def generate_sitemap",1)[0]
    for forbidden in (
        "<h2>Canonical source record</h2>",
        "<br><code>{esc(path)}</code>",
    ):
        if forbidden in generated_builder:
            errors.append(f"generated knowledge pages expose backend path taxonomy again: {forbidden}")
    for required in (
        "data-generated-knowledge-meta",
        "machine_meta = {",
        'body = "".join(text_blocks(data))',
    ):
        if required not in generated_builder:
            errors.append(f"generated record projection lost subject-first marker: {required}")

    authored_groups = [
        audit.get("authored_history") or [],
        audit.get("second_authored_wave") or [],
        audit.get("third_authored_wave") or [],
        audit.get("fourth_authored_wave") or [],
        audit.get("fifth_authored_wave") or [],
        audit.get("sixth_authored_wave") or [],
        audit.get("seventh_authored_wave") or [],
    ]
    history=[row for group in authored_groups for row in group]
    seen_authored=set()
    for row in history:
        rel=str(row.get("path") or "")
        if not rel or rel in seen_authored:
            continue
        seen_authored.add(rel)
        path=ROOT/rel
        if not path.is_file():
            errors.append(f"authored richness page missing: {rel}")
            continue
        source=path.read_text(encoding="utf-8",errors="replace")
        mass=len(plain_text(source))
        if mass < 1800:
            errors.append(f"authored richness page regressed to a thin shell: {rel} has {mass} plain-text characters")
        if rel.startswith("rooms/inside/") and 'class="room-essay"' not in source and "data-room-reader-body" not in source:
            errors.append(f"authored nested Room lost its substantive reader marker: {rel}")
        if re.match(r"^rooms/[^/]+/index\.html$", rel) and rel != "rooms/objects/index.html" and 'class="dwelling-reader"' not in source:
            errors.append(f"authored Dwelling lost its narrative reader marker: {rel}")

    bound_pages={str(row.get("page") or "") for row in bindings}
    surface_rows=[row for row in surfaces.get("surfaces",[]) if isinstance(row,dict)]
    visible=[row for row in surface_rows if row.get("status")=="active" and row.get("visibility") in {"primary","secondary"}]
    for row in visible:
        route=row.get("canonical_route") or row.get("route") or "/"
        rel="index.html" if route=="/" else route.strip("/")+"/index.html"
        page=ROOT/rel
        if not page.is_file():
            errors.append(f"visible public surface missing reader file: {row.get('id')} -> {rel}")
            continue
        # Visible surfaces need substance either through an explicit binding or enough
        # authored page body to be more than a routing shell. This is deliberately
        # qualitative/lightweight and does not impose one layout.
        source=page.read_text(encoding="utf-8",errors="replace")
        mass=len(plain_text(source))
        if rel not in bound_pages and mass < 1800:
            errors.append(f"visible substance coverage too weak: {row.get('id')} has {mass} plain-text characters and no substance binding")

    if errors:
        print("READER RICHNESS VALIDATION FAILED")
        for error in errors: print("-",error)
        return 1
    print(f"Reader richness: PASS · {len(registered)} nested Rooms · {len(seen_authored)} authored pages protected · {len(bindings)} substance-bound public pages · {len(visible)} visible surfaces checked live")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
