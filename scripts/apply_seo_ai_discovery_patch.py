#!/usr/bin/env python3
"""Temporary branch-only helper for applying the approved SEO discovery edits safely."""
from pathlib import Path


def replace_once(path: str, old: str, new: str, marker: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if marker in text:
        return
    if old not in text:
        raise SystemExit(f"expected source block missing in {path}: {old[:100]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    replace_once(
        "scripts/build_discovery.py",
        'TIM_Q = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"\n',
        'TIM_Q = ROOT / "knowledge" / "reader" / "tim-dooley-question-index.json"\n'
        'OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"\n'
        'SOURCE_AUTHORITY = BASE_URL + "/context/source-authority/"\n'
        'AUTHORITY_MANIFEST = BASE_URL + "/site-authority.json"\n'
        'TIM_CANONICAL = BASE_URL + "/tim-dooley/"\n',
        'OFFICIAL_REPOSITORY = "https://github.com/ThePotatoOfLife/TimDooley"',
    )
    replace_once(
        "scripts/build_discovery.py",
        'def write(rel, text):\n    path = OUT / rel\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(text, encoding="utf-8")\n\n',
        'def write(rel, text):\n    path = OUT / rel\n    path.parent.mkdir(parents=True, exist_ok=True)\n    path.write_text(text, encoding="utf-8")\n\n\n'
        'def robots_text():\n'
        '    """Return one permissive crawler policy for documented search/retrieval bots plus unknown standards-compliant crawlers."""\n'
        '    agents = ("Googlebot", "Google-Extended", "bingbot", "OAI-SearchBot", "*")\n'
        '    lines = []\n'
        '    for agent in agents:\n'
        '        lines.extend((f"User-agent: {agent}", "Allow: /", ""))\n'
        '    lines.extend((f"Sitemap: {BASE_URL}/sitemap-index.xml", ""))\n'
        '    return "\\n".join(lines)\n\n',
        'def robots_text():',
    )
    replace_once(
        "scripts/build_discovery.py",
        '        "schema_version": "3.0.0", "updated": generated, "name": "The Potato of Life — Tim Dooley Archive", "canonical_url": BASE_URL + "/",\n',
        '        "schema_version": "3.1.0", "updated": generated, "name": "The Potato of Life — Tim Dooley Archive", "canonical_url": BASE_URL + "/",\n'
        '        "official_repository": OFFICIAL_REPOSITORY,\n'
        '        "source_authority": SOURCE_AUTHORITY,\n'
        '        "authority_manifest": AUTHORITY_MANIFEST,\n'
        '        "tim_canonical": TIM_CANONICAL,\n',
        '"official_repository": OFFICIAL_REPOSITORY',
    )
    replace_once(
        "scripts/build_discovery.py",
        '            "tim": BASE_URL + "/tim-dooley/", "religion": BASE_URL + "/religion/",',
        '            "tim": TIM_CANONICAL, "religion": BASE_URL + "/religion/",',
        '"tim": TIM_CANONICAL',
    )
    replace_once(
        "scripts/build_discovery.py",
        '    concise = ["# The Potato of Life / Tim Dooley", "", f"> Canonical site: {BASE_URL}/", "> Public knowledge archive with provenance-aware records, reader pages, questions, chronology and machine-readable indexes.", "", "## Primary reader doors"]\n',
        '    concise = ["# The Potato of Life / Tim Dooley", "", f"> Canonical site: {BASE_URL}/", "> Official project-owned public knowledge archive with provenance-aware records, reader pages, questions, chronology and machine-readable indexes.", "", "## Official project authority", f"- Official repository: {OFFICIAL_REPOSITORY}", f"- Tim Dooley canonical route: {TIM_CANONICAL}", f"- Sources and evidence policy: {SOURCE_AUTHORITY}", f"- Authority manifest: {AUTHORITY_MANIFEST}", "", "## Primary reader doors"]\n',
        '## Official project authority',
    )
    replace_once(
        "scripts/build_discovery.py",
        '    full = ["# The Potato of Life / Tim Dooley — Full Machine Retrieval Index", "", f"> Canonical public archive: {BASE_URL}/", f"> Final canonical page index: {BASE_URL}/site-index.json", f"> Discovery architecture: {BASE_URL}/discovery.json", "", "## Primary reader doors"]\n',
        '    full = ["# The Potato of Life / Tim Dooley — Full Machine Retrieval Index", "", f"> Canonical public archive: {BASE_URL}/", f"> Official repository: {OFFICIAL_REPOSITORY}", f"> Tim Dooley canonical route: {TIM_CANONICAL}", f"> Sources and evidence policy: {SOURCE_AUTHORITY}", f"> Authority manifest: {AUTHORITY_MANIFEST}", f"> Final canonical page index: {BASE_URL}/site-index.json", f"> Discovery architecture: {BASE_URL}/discovery.json", "", "## Primary reader doors"]\n',
        'f"> Official repository: {OFFICIAL_REPOSITORY}"',
    )
    replace_once(
        "scripts/build_discovery.py",
        '    robots = "User-agent: OAI-SearchBot\\nAllow: /\\n\\nUser-agent: *\\nAllow: /\\n\\n" + f"Sitemap: {BASE_URL}/sitemap-index.xml\\n"\n    write("robots.txt", robots)\n',
        '    write("robots.txt", robots_text())\n',
        'write("robots.txt", robots_text())',
    )

    robots = (
        "User-agent: Googlebot\nAllow: /\n\n"
        "User-agent: Google-Extended\nAllow: /\n\n"
        "User-agent: bingbot\nAllow: /\n\n"
        "User-agent: OAI-SearchBot\nAllow: /\n\n"
        "User-agent: *\nAllow: /\n\n"
        "Sitemap: https://thepotatooflife.github.io/TimDooley/sitemap-index.xml\n"
    )
    Path("robots.txt").write_text(robots, encoding="utf-8")

    replace_once("index.html", '<title>Tim Dooley & The Potato of Life</title>', '<title>Tim Dooley & The Potato of Life — Official Archive</title>', 'Official Archive</title>')
    replace_once(
        "index.html",
        '<meta name="description" content="Tim Dooley and the Potato of Life: questions about identity, religion, philosophy, science and the world.">',
        '<meta name="description" content="Official project-owned archive for Tim Dooley, The Potato of Life, Potatoism and the Potatoverse, with sources, questions, research and structured knowledge.">',
        'Official project-owned archive for Tim Dooley',
    )
    replace_once(
        "index.html",
        '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap.xml">',
        '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap-index.xml">',
        'rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap-index.xml"',
    )
    replace_once(
        "index.html",
        '<p class="project-purpose">A living archive about Tim Dooley and the Potato of Life, organized around questions of identity, religion, philosophy, science and the relationships connecting people, ideas and the world.</p>',
        '<p class="project-purpose">The official project-owned public archive for Tim Dooley and The Potato of Life, including Potatoism and the wider Potatoverse, organized around questions of identity, religion, philosophy, science and the relationships connecting people, ideas and the world.</p>',
        'official project-owned public archive',
    )
    replace_once(
        "index.html",
        '<p class="evidence-note">Project self-description, autobiographical interpretation, comparative research and externally documented evidence remain distinct layers even when they are studied together.</p>',
        '<p class="evidence-note">Project self-description, autobiographical interpretation, comparative research and externally documented evidence remain distinct layers even when they are studied together. <a href="https://thepotatooflife.github.io/TimDooley/context/source-authority/">Sources &amp; evidence policy</a> · <a href="https://github.com/ThePotatoOfLife/TimDooley">Official repository</a>.</p>',
        'Sources &amp; evidence policy',
    )

    replace_once(
        "scripts/validate_seo_pipeline.py",
        '            "User-agent: OAI-SearchBot",\n            "Sitemap: {BASE_URL}/sitemap-index.xml",\n',
        '            "User-agent: Googlebot",\n            "User-agent: Google-Extended",\n            "User-agent: bingbot",\n            "User-agent: OAI-SearchBot",\n            "def robots_text()",\n            "OFFICIAL_REPOSITORY",\n            "SOURCE_AUTHORITY",\n            "AUTHORITY_MANIFEST",\n            "Sitemap: {BASE_URL}/sitemap-index.xml",\n',
        '"User-agent: Google-Extended"',
    )


if __name__ == "__main__":
    main()
