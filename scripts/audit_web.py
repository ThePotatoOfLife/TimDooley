#!/usr/bin/env python3
"""Audit the single public web surface for broken local references."""
from __future__ import annotations
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]; warnings=[]
html_files=sorted(ROOT.rglob('*.html')); css_files=sorted(ROOT.rglob('*.css')); js_files=sorted(ROOT.rglob('*.js'))
attr_re=re.compile(r'\b(?:href|src)=["\']([^"\']+)["\']',re.I); css_url_re=re.compile(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)',re.I); js_static_asset_re=re.compile(r'(?:fetch|import|src|href)\s*\(\s*["\']([^"\']+)["\']\s*\)',re.I)
external=('http://','https://','//','mailto:','javascript:','data:','blob:')
def local(raw):
    raw=raw.split('#',1)[0].split('?',1)[0].strip()
    return None if not raw or raw.startswith(external) or raw.startswith(('${','<','`')) else raw
def check(source,raw,label):
    target=local(raw)
    if not target:return
    if target.startswith('/'):
        errors.append(f'{source.relative_to(ROOT)}: root-relative reference -> {raw}');return
    p=(source.parent/target).resolve()
    try:p.relative_to(ROOT.resolve())
    except ValueError:return
    if not p.exists():errors.append(f'{source.relative_to(ROOT)}: broken {label} -> {target}')
for page in html_files:
    text=page.read_text(encoding='utf-8',errors='replace')
    for raw in attr_re.findall(text):check(page,raw,'HTML reference')
for css in css_files:
    for _,raw in css_url_re.findall(css.read_text(encoding='utf-8',errors='replace')):check(css,raw,'CSS asset')
for js in js_files:
    for raw in js_static_asset_re.findall(js.read_text(encoding='utf-8',errors='replace')):
        if raw.startswith(('/','./','../')) or '.' in Path(raw).name:check(js,raw,'JavaScript asset')
if not (ROOT/'index.html').exists():errors.append('Missing index.html public Door')
if (ROOT/'index.html').exists() and not (ROOT/'root.js').exists():warnings.append('index.html exists without root.js; unified reader may be static-only')
if len(html_files)!=1:warnings.append(f'Expected one public HTML entry point; found {len(html_files)} HTML files')
print('Public application root: /TimDooley/')
print(f'HTML pages audited: {len(html_files)}'); print(f'CSS files audited: {len(css_files)}'); print(f'JS files audited: {len(js_files)}')
print(f'Errors: {len(errors)}'); print(f'Warnings: {len(warnings)}')
for x in errors:print('ERROR:',x)
for x in warnings:print('WARNING:',x)
sys.exit(1 if errors else 0)
