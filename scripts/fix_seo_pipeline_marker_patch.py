#!/usr/bin/env python3
"""Temporary branch-only correction for source-form crawler markers in SEO validator."""
from pathlib import Path

p = Path("scripts/validate_seo_pipeline.py")
text = p.read_text(encoding="utf-8")
old = '''            "User-agent: Googlebot",
            "User-agent: Google-Extended",
            "User-agent: bingbot",
            "User-agent: OAI-SearchBot",
            "def robots_text()",
            "OFFICIAL_REPOSITORY",
            "SOURCE_AUTHORITY",
            "AUTHORITY_MANIFEST",
            "Sitemap: {BASE_URL}/sitemap-index.xml",
'''
new = '''            '"Googlebot"',
            '"Google-Extended"',
            '"bingbot"',
            '"OAI-SearchBot"',
            "def robots_text()",
            "OFFICIAL_REPOSITORY",
            "SOURCE_AUTHORITY",
            "AUTHORITY_MANIFEST",
            "Sitemap: {BASE_URL}/sitemap-index.xml",
'''
if old in text:
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
elif new not in text:
    raise SystemExit("expected crawler marker block not found")
