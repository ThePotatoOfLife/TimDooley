#!/usr/bin/env python3
"""Audit the static web layer for GitHub Pages project-root correctness and broken local references."""
from __future__ import annotations
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []
html_files = sorted(ROOT.glob('*.html'))
link_re = re.compile(r'<link\b[^>]*?href=["\']([^"\']+)["\']', re.I | re.S)
script_src_re = re.compile(r'<script\b[^>]*?src=["\']([^"\']+)["\']', re.I | re.S)
attr_re = re.compile(r'\b(?:href|src)=["\']([^"\']+)["\']', re.I)
style_block_re = re.compile(r'<style\b[^>]*>.*?</style>', re.I | re.S)
inline_style_re = re.compile(r'\sstyle\s*=\s*["\']', re.I)
external_prefixes = ('http://', 'https://', '//', 'mailto:', 'javascript:', 'data:')
canonical = ('index.html', 'repository.html', 'nations.html', 'people.html', 'belief.html', 'potatoism.html', 'hawkins.html')

def local_target(raw: str):
    raw = raw.split('#', 1)[0].split('?', 1)[0].strip()
    if not raw or raw.startswith(external_prefixes) or raw.startswith('${'):
        return None
    return raw

for page in html_files:
    text = page.read_text(encoding='utf-8', errors='replace')
    styles = link_re.findall(text)
    scripts = script_src_re.findall(text)
    if len(styles) != len(set(styles)):
        errors.append(f'{page.name}: duplicate stylesheet link')
    if len(scripts) != len(set(scripts)):
        errors.append(f'{page.name}: duplicate script source')
    if style_block_re.findall(text):
        warnings.append(f'{page.name}: contains embedded <style> block(s)')
    if inline_style_re.search(text):
        warnings.append(f'{page.name}: contains inline style attribute(s)')
    if page.name in canonical and 'consistency.css' not in styles:
        errors.append(f'{page.name}: missing consistency.css')
    if page.name in canonical and styles and styles[-1] != 'consistency.css':
        errors.append(f'{page.name}: consistency.css must be the final stylesheet')
    if page.name in canonical:
        for target in canonical:
            if f'href="{target}"' not in text and f"href='{target}'" not in text:
                warnings.append(f'{page.name}: canonical nav does not visibly contain {target}')
    for raw in attr_re.findall(text):
        if raw.startswith('/') and not raw.startswith('//'):
            errors.append(f'{page.name}: root-relative reference breaks GitHub Pages project root -> {raw}')
        target = local_target(raw)
        if not target or any(x in target for x in ('${', '`', '<', '>')):
            continue
        p = (page.parent / target).resolve()
        try:
            p.relative_to(ROOT.resolve())
        except ValueError:
            continue
        if not p.exists():
            errors.append(f'{page.name}: broken local reference -> {target}')

if not (ROOT / 'site.css').exists():
    errors.append('Missing canonical site.css')
portal = ROOT / 'portal.css'
if portal.exists() and '@import url("site.css")' not in portal.read_text(encoding='utf-8', errors='replace'):
    errors.append('portal.css is not a compatibility layer importing site.css')

print(f'Public application root: /TimDooley/')
print(f'HTML pages audited: {len(html_files)}')
print(f'Errors: {len(errors)}')
print(f'Warnings: {len(warnings)}')
for x in errors:
    print('ERROR:', x)
for x in warnings:
    print('WARNING:', x)
sys.exit(1 if errors else 0)
