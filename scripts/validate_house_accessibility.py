#!/usr/bin/env python3
"""Validate shared House accessibility and narrow-screen interaction contracts."""
from __future__ import annotations

import re
from pathlib import Path

from house_shell import render_house_bar

ROOT = Path(__file__).resolve().parents[1]
SITE_CSS = ROOT / "app" / "site-system.css"
SPECIALIST_CSS = ROOT / "app" / "specialist-house.css"
UTILITY_CSS = ROOT / "app" / "utility-house.css"
BUILD_SITE = ROOT / "scripts" / "build_site.py"


def css_block(css: str, selector: str) -> str:
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", css, re.I | re.S)
    return match.group(1) if match else ""


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    site_css = SITE_CSS.read_text(encoding="utf-8")
    specialist_css = SPECIALIST_CSS.read_text(encoding="utf-8")
    utility_css = UTILITY_CSS.read_text(encoding="utf-8")
    build_site = BUILD_SITE.read_text(encoding="utf-8")

    descendant_bar = render_house_bar(ROOT, "tim-ontology")
    exact_bar = render_house_bar(ROOT, "tim")

    require(
        errors,
        bool(re.search(r'aria-current="location"[^>]*>Tim Dooley</a>', descendant_bar)),
        "descendant pages must mark their active primary Door with aria-current=location, not page",
    )
    require(
        errors,
        bool(re.search(r'aria-current="page"[^>]*>Tim Dooley</a>', exact_bar)),
        "a primary Door on its own canonical page must retain aria-current=page",
    )
    require(
        errors,
        'class="site-skip-link"' in descendant_bar and 'href="#main-content"' in descendant_bar,
        "editorial House chrome must expose a keyboard skip-to-content link",
    )
    require(
        errors,
        descendant_bar.count('role="group"') >= 2,
        "mobile House navigation groups need explicit group semantics",
    )
    require(
        errors,
        "ensure_main_content_target" in build_site,
        "public House projection must guarantee a #main-content skip target",
    )

    require(errors, ".site-skip-link" in site_css, "site-system.css must style the skip link")
    require(
        errors,
        "min-height: 44px" in css_block(site_css, ".site-nav__link"),
        "global House navigation links need a 44px minimum touch height",
    )
    require(
        errors,
        "min-height: 44px" in css_block(site_css, ".site-local-nav__link"),
        "local House navigation links need a 44px minimum touch height",
    )
    require(
        errors,
        "min-height: 44px" in css_block(site_css, ".site-mobile-nav > summary"),
        "mobile House menu control needs a 44px minimum touch height",
    )
    mobile_panel = css_block(site_css, ".site-mobile-nav__panel")
    require(
        errors,
        "max-height:" in mobile_panel and "100dvh" in mobile_panel and "overflow-y: auto" in mobile_panel,
        "mobile House menu panel must stay inside the dynamic viewport and scroll internally",
    )
    require(
        errors,
        "@media (prefers-reduced-motion: reduce)" in site_css,
        "shared House CSS must honor prefers-reduced-motion",
    )
    require(
        errors,
        ":focus-visible" in site_css,
        "shared House CSS must expose visible keyboard focus",
    )
    require(
        errors,
        "overflow-wrap: anywhere" in css_block(site_css, ".site-related a"),
        "continuation links must not force horizontal overflow on narrow screens",
    )
    require(
        errors,
        "min-height: 28px" in css_block(specialist_css, ".site-specialist-house__link"),
        "specialist House escape links need a compact but accessible touch target",
    )
    utility_link = css_block(utility_css, ".site-utility-house__link")
    require(
        errors,
        ("height: 30px" in utility_link or "min-height: 30px" in utility_link) and ":focus-visible" in utility_css,
        "utility House escape must preserve its compact >=30px target and visible focus state",
    )

    if errors:
        print("House accessibility validation FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print("House accessibility validation passed: keyboard orientation, current semantics, touch targets, reduced motion and narrow-screen overflow are covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
