#!/usr/bin/env python3
"""Fail-fast integrity checks for the static atlas before it is deployed.

This is intentionally conservative: it checks structure and references without
trying to interpret the project's heterogeneous data schemas.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"

LOCAL_SCHEME = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|//|#)")
ATTR_RE = re.compile(r"\b(?:href|src)\s*=\s*([\"'])(.*?)\1", re.I | re.S)
CSS_URL_RE = re.compile(r"url\(\s*([\"']?)(.*?)\1\s*\)", re.I | re.S)
JS_LOCAL_RE = re.compile(r"(?:fetch|import\s*\()\s*\(\s*['\"]([^'\"]+)['\"]", re.I)


def fail(errors: list[str]) -> None:
    if errors:
        print("\nSTABILITY AUDIT FAILED")
        for item in errors[:200]:
            print(f"- {item}")
        if len(errors) > 200:
            print(f"- ... and {len(errors) - 200} more")
        raise SystemExit(1)


def local_target(raw: str, base: Path) -> Path | None:
    raw = raw.strip()
    if not raw or LOCAL_SCHEME.match(raw):
        return None
    parsed = urlsplit(raw)
    path = parsed.path
    if not path:
        return base
    # GitHub Pages serves the repository at /TimDooley/, so root-relative
    # references are repository-root references in the source site.
    if path.startswith("/"):
        return ROOT / path.lstrip("/")
    return (base / path).resolve()


def exists_for_target(target: Path, site_mode: bool) -> bool:
    if target.exists():
        return True
    if site_mode and target.suffix == "":
        return (target / "index.html").exists()
    if site_mode and target.name == "index.html":
        return target.parent.exists()
    return False


def check_json(errors: list[str]) -> tuple[int, int]:
    count = 0
    bad = 0
    for path in ROOT.glob("data/**/*.json"):
        count += 1
        try:
            with path.open(encoding="utf-8") as fh:
                json.load(fh)
        except Exception as exc:
            bad += 1
            errors.append(f"invalid JSON: {path.relative_to(ROOT)} ({exc})")
    return count, bad


def check_python(errors: list[str]) -> None:
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", *map(str, scripts)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode:
        errors.append("Python syntax check failed: " + (proc.stderr or proc.stdout).strip())


def check_js(errors: list[str]) -> None:
    node = subprocess.run(["node", "--version"], cwd=ROOT, text=True, capture_output=True)
    if node.returncode:
        print("Node.js unavailable; JavaScript syntax check skipped.")
        return
    for path in sorted(ROOT.rglob("*.js")):
        if any(part in {".git", "_site", "node_modules", "__pycache__"} for part in path.parts):
            continue
        proc = subprocess.run(["node", "--check", str(path)], cwd=ROOT, text=True, capture_output=True)
        if proc.returncode:
            errors.append(f"JavaScript syntax error: {path.relative_to(ROOT)} ({proc.stderr.strip()})")


def check_html_and_assets(errors: list[str]) -> tuple[int, int]:
    pages = sorted(SITE.rglob("*.html")) if SITE.exists() else []
    links = 0
    missing = 0
    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        for _, raw in ATTR_RE.findall(text):
            target = local_target(raw, page.parent)
            if target is None:
                continue
            links += 1
            if not exists_for_target(target, True):
                missing += 1
                errors.append(f"broken built-site reference: {page.relative_to(SITE)} -> {raw}")
    return links, missing


def check_css_and_js_refs(errors: list[str]) -> int:
    refs = 0
    files = list(ROOT.rglob("*.css")) + list(ROOT.rglob("*.js"))
    for path in files:
        if any(part in {".git", "_site", "node_modules", "__pycache__"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".css":
            raw_refs = [m[1] for m in CSS_URL_RE.findall(text)]
        else:
            raw_refs = JS_LOCAL_RE.findall(text)
        for raw in raw_refs:
            target = local_target(raw, path.parent)
            if target is None:
                continue
            refs += 1
            if not target.exists():
                errors.append(f"broken source asset/data reference: {path.relative_to(ROOT)} -> {raw}")
    return refs


def main() -> None:
    errors: list[str] = []
    json_count, json_bad = check_json(errors)
    check_python(errors)
    check_js(errors)
    html_links, html_missing = check_html_and_assets(errors)
    source_refs = check_css_and_js_refs(errors)

    index = ROOT / "data/repository-index.json"
    if not index.exists():
        errors.append("missing generated repository index: data/repository-index.json")
    else:
        try:
            payload = json.loads(index.read_text(encoding="utf-8"))
            records = payload.get("records")
            if not isinstance(records, list) or not records:
                errors.append("repository index has no records array")
        except Exception as exc:
            errors.append(f"repository index is invalid JSON: {exc}")

    print(f"JSON files checked: {json_count} (invalid: {json_bad})")
    print(f"Built HTML local references checked: {html_links} (missing: {html_missing})")
    print(f"Source CSS/JS local references checked: {source_refs}")
    fail(errors)
    print("\nSTABILITY AUDIT PASSED")


if __name__ == "__main__":
    main()
