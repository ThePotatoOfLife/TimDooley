#!/usr/bin/env python3
"""Compatibility scoping for self-themed authored House readers.

Some older dossier/FAQ pages carry their component CSS inline and historically owned
`:root`, `body` and generic anchor styling. The public House should own those global
layers, but rewriting large archival documents by hand is unnecessarily risky.

This transformer keeps the authored component CSS intact while making its effective
scope local to the page's <main> content:
- legacy :root variables move to .house-content-scope;
- legacy body blocks are removed so site-system.css owns the document canvas;
- standalone generic anchor rules become .house-content-scope a rules;
- the first <main> receives the house-content-scope class.

The transformation is deliberately narrow. It does not rename cards, grids, FAQ
families, evidence modules, IDs or application hooks.
"""
from __future__ import annotations

import re

MAIN_TAG_RE = re.compile(r"<main\b[^>]*>", re.I)
CLASS_ATTR_RE = re.compile(r"\bclass=(['\"])(.*?)\1", re.I | re.S)
INLINE_STYLE_RE = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.I | re.S)
ROOT_SELECTOR_RE = re.compile(r"(^|})(\s*):root\s*\{", re.I)
BODY_BLOCK_RE = re.compile(r"(^|})(\s*)body\s*\{[^{}]*\}", re.I)
ANCHOR_SELECTOR_RE = re.compile(r"(^|})(\s*)a\s*\{", re.I)


def has_legacy_global_theme(text: str) -> bool:
    """Return True when inline CSS still owns one of the legacy global layers."""
    for _open, css, _close in INLINE_STYLE_RE.findall(text):
        if ROOT_SELECTOR_RE.search(css) or BODY_BLOCK_RE.search(css) or ANCHOR_SELECTOR_RE.search(css):
            return True
    return False


def _scope_main_tag(tag: str) -> str:
    if "house-content-scope" in tag:
        return tag
    match = CLASS_ATTR_RE.search(tag)
    if match:
        classes = match.group(2).split()
        classes.append("house-content-scope")
        replacement = f'class="{" ".join(classes)}"'
        return tag[: match.start()] + replacement + tag[match.end() :]
    return tag[:-1] + ' class="house-content-scope">'


def _scope_css(css: str) -> str:
    css = ROOT_SELECTOR_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}.house-content-scope{{", css)
    css = BODY_BLOCK_RE.sub(lambda m: m.group(1), css)
    css = ANCHOR_SELECTOR_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}.house-content-scope a{{", css)
    return css


def scope_legacy_inline_theme(text: str) -> str:
    """Return HTML with legacy global inline theme ownership scoped to page content."""
    if not has_legacy_global_theme(text):
        return text

    if not MAIN_TAG_RE.search(text):
        raise ValueError("self-themed House reader has no <main> element to scope")
    text = MAIN_TAG_RE.sub(lambda m: _scope_main_tag(m.group(0)), text, count=1)
    text = INLINE_STYLE_RE.sub(lambda m: m.group(1) + _scope_css(m.group(2)) + m.group(3), text)
    return text
