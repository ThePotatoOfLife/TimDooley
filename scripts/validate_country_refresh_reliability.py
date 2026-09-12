#!/usr/bin/env python3
"""Validate bounded retry/backoff for canonical country-data acquisition.

External APIs are acquisition inputs, not runtime dependencies. A transient
network failure should be retried a small number of times, while permanent
errors and incomplete data must still fail closed without overwriting records.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "refresh_country_atlas.py"


def main() -> int:
    errors: list[str] = []
    if not TARGET.exists():
        errors.append("missing scripts/refresh_country_atlas.py")
        text = ""
    else:
        text = TARGET.read_text(encoding="utf-8", errors="replace")
        try:
            ast.parse(text)
        except SyntaxError as exc:
            errors.append(f"refresh_country_atlas.py syntax error: {exc}")

    required = (
        "REQUEST_TIMEOUT_SECONDS",
        "MAX_ATTEMPTS",
        "RETRY_BASE_SECONDS",
        "TRANSIENT_HTTP_CODES",
        "urllib.error.HTTPError",
        "urllib.error.URLError",
        "socket.timeout",
        "Retry-After",
        "time.sleep(delay)",
        "Transient HTTP",
        "Transient network error",
        "after {MAX_ATTEMPTS} attempts",
    )
    for marker in required:
        if marker not in text:
            errors.append(f"country refresh missing reliability marker: {marker}")

    # Keep retries bounded and timeout materially below the previous single
    # 180-second attempt. Values are parsed rather than merely string-matched.
    values: dict[str, object] = {}
    try:
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                if name in {"REQUEST_TIMEOUT_SECONDS", "MAX_ATTEMPTS", "RETRY_BASE_SECONDS"}:
                    try:
                        values[name] = ast.literal_eval(node.value)
                    except Exception:
                        pass
    except SyntaxError:
        tree = None

    attempts = values.get("MAX_ATTEMPTS")
    timeout = values.get("REQUEST_TIMEOUT_SECONDS")
    base = values.get("RETRY_BASE_SECONDS")
    if not isinstance(attempts, int) or not 2 <= attempts <= 6:
        errors.append(f"MAX_ATTEMPTS must be bounded between 2 and 6; found {attempts!r}")
    if not isinstance(timeout, (int, float)) or not 5 <= timeout <= 90:
        errors.append(f"REQUEST_TIMEOUT_SECONDS must be between 5 and 90; found {timeout!r}")
    if not isinstance(base, (int, float)) or not 0 < base <= 10:
        errors.append(f"RETRY_BASE_SECONDS must be >0 and <=10; found {base!r}")

    # Existing fail-closed data-quality guard must remain intact.
    if "Refusing incomplete refresh" not in text:
        errors.append("country refresh lost incomplete-refresh safeguard")
    if "population" not in text or "gdp" not in text:
        errors.append("country refresh lost population/GDP coverage gate")

    if errors:
        print("COUNTRY REFRESH RELIABILITY VALIDATION FAILED")
        for error in errors:
            print("-", error)
        return 1

    print("COUNTRY REFRESH RELIABILITY VALIDATION PASSED")
    print("Country acquisition: bounded retries · transient HTTP/network handling · fail-closed coverage guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
