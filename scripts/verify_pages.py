#!/usr/bin/env python3
"""Fail-fast-with-context verification for the generated GitHub Pages artifact.

The old workflow used one long shell chain: when any grep failed GitHub only showed
"exit code 1", which made a healthy build look like an unexplained deployment
problem. This verifier keeps the same purpose but prints every broken invariant
and also protects the Science Atlas files that previously reached main without
being deployed.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
errors: list[str] = []


def require_file(rel: str) -> Path:
    path = SITE / rel
    if not path.is_file():
        errors.append(f"missing generated file: {rel}")
    return path


def require_contains(rel: str, needle: str) -> None:
    path = require_file(rel)
    if path.is_file():
        text = path.read_text(encoding="utf-8", errors="replace")
        if needle not in text:
            errors.append(f"{rel}: expected marker not found: {needle!r}")


def require_json(rel: str) -> None:
    path = require_file(rel)
    if path.is_file():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")


for rel in [
    "index.html", "manifest.json", "app/app.js", "app/style.css",
    "knowledge/core/potato-of-life.json", "knowledge/core/tim-dooley.json",
    "knowledge/core/tim-identity-ontology.json",
    "knowledge/indexes/faq-tim-ontology-questions.json",
    "tim-dooley/ontology/index.html", "faq/index.html", "faq/all/god/index.html",
    "questions/index.html", "questions/who-is-tim-dooley/index.html",
    "index-a-z/index.html", "discovery.json", "llms.txt", "llms-full.txt",
    "robots.txt", "sitemap.xml", "sitemap-index.xml", "sitemap-questions.xml",
    "science/index.html", "science/science.css", "science/science.js",
    "knowledge/science/science-master-index.json",
    "knowledge/science/unified-potato-theory-2025-recovery.json",
    "knowledge/science/april-21-2025-potato-axis-spiral-primary-recovery.json",
    "knowledge/science/theory-of-everything-archaeology.json",
]:
    require_file(rel)

for rel in ["manifest.json", "discovery.json", "knowledge/science/science-master-index.json"]:
    require_json(rel)

checks = [
    ("index.html", 'id="branches"'),
    ("index.html", 'id="reader"'),
    ("index.html", 'app/app.js'),
    ("app/app.js", 'manifest.json'),
    ("sitemap.xml", 'tim-dooley/ontology/'),
    ("llms.txt", 'Critical entity resolution'),
    ("tim-dooley/ontology/index.html", 'Potatoverse theological identity'),
    ("questions/who-is-tim-dooley/index.html", 'Who is Tim Dooley'),
    ("index.html", 'questions/'),
    ("index.html", 'index-a-z/'),
    ("robots.txt", 'sitemap-index.xml'),
    ("sitemap-index.xml", 'sitemap-questions.xml'),
    ("index.html", '"@type":"Thing"'),
    ("science/index.html", 'SCIENCE'),
    ("science/index.html", 'Complete theories, abstracts & conclusions'),
    ("science/index.html", 'Evidence & status system'),
    ("science/index.html", 'Visual science graph'),
    ("science/index.html", 'science.js'),
    ("science/science.js", 'async function loadCorpus()'),
    ("science/science.js", 'renderEquationCorpus'),
]
for rel, needle in checks:
    require_contains(rel, needle)

if errors:
    print("Pages verification FAILED:\n")
    for i, error in enumerate(dict.fromkeys(errors), 1):
        print(f"{i:02d}. {error}")
    raise SystemExit(1)

print("Pages verification passed: core archive, discovery surfaces, ontology and Science Atlas are deployable.")
