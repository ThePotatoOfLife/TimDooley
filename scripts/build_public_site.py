#!/usr/bin/env python3
"""Compose the current public-site builder with the additive Atlas builder.

During migration, legacy readers remain intact. Atlas is added after the legacy
copy/generation stage. Final discovery/SEO passes continue to operate on the
combined _site artifact.
"""
from __future__ import annotations

from build_site import build as build_legacy_site
from build_atlas_pages import build_pages as build_atlas_pages


def build() -> list[str]:
    build_legacy_site()
    atlas_urls = build_atlas_pages()
    print(f"PUBLIC SITE COMPOSED: legacy surface + {len(atlas_urls)} Atlas routes")
    return atlas_urls


if __name__ == "__main__":
    build()
