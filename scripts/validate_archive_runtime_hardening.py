#!/usr/bin/env python3
"""Validate defensive behavior in the manifest-driven archive reader.

The archive can render large heterogeneous records and route directly from URL
hashes. This contract keeps that deep-reader surface useful without allowing an
oversized record, malformed hash or stale async response to take over the UI.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app" / "app.js"


def main() -> int:
    errors: list[str] = []
    if not APP.exists():
        errors.append("missing app/app.js archive runtime")
        js = ""
    else:
        js = APP.read_text(encoding="utf-8", errors="replace")

    required = (
        "let recordPaths=new Set()",
        "let recordRequestToken=0",
        "RENDER_LIMITS",
        "maxDepth",
        "maxNodes",
        "maxItems",
        "maxStringChars",
        "function renderLimitNotice",
        "function safeDecodeHashValue",
        "function cancelRecordLoad",
        "function isCurrentRecordLoad",
        "function isKnownRecord",
        "recordPaths.add(manifest.root.record)",
        "recordPaths.add(path)",
        "if(!isKnownRecord(path))",
        "const token=++recordRequestToken",
        "if(!isCurrentRecordLoad(token,target))",
        "[record display budget reached]",
        "[maximum display depth reached]",
        "array items not rendered",
        "object fields not rendered",
        "additional characters not rendered",
    )
    for marker in required:
        if marker not in js:
            errors.append(f"app/app.js missing archive hardening marker: {marker}")

    # Route decoding must be fail-closed rather than letting malformed percent
    # encoding throw out of hashchange/initialization.
    route_start = js.find("async function routeHash")
    route_body = js[route_start:] if route_start >= 0 else ""
    if "safeDecodeHashValue" not in route_body:
        errors.append("routeHash must use safeDecodeHashValue for hash payloads")
    if "decodeURIComponent(hash.slice" in route_body:
        errors.append("routeHash still decodes hash payloads directly")

    # A deep-reader navigation change must invalidate any in-flight record load.
    for fn in ("function selectBranch", "function showContext", "function showPathway"):
        start = js.find(fn)
        if start < 0:
            errors.append(f"app/app.js missing navigation function: {fn}")
            continue
        body = js[start : start + 700]
        if "cancelRecordLoad()" not in body:
            errors.append(f"{fn} must cancel stale record loads")

    node = shutil.which("node")
    if node and APP.exists():
        result = subprocess.run([node, "--check", str(APP)], capture_output=True, text=True)
        if result.returncode:
            errors.append("app/app.js syntax failed: " + (result.stderr.strip() or result.stdout.strip()))

    if errors:
        print("ARCHIVE RUNTIME HARDENING VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("ARCHIVE RUNTIME HARDENING VALIDATION PASSED")
    print("Archive reader: bounded rendering · known-record routing · stale-load cancellation · safe hash decoding")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
