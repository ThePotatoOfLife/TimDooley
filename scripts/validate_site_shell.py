#!/usr/bin/env python3
"""Verify that the Pages artifact exposes the unified root and the existing site material."""
from __future__ import annotations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'

def main():
    errors=[]
    if not SITE.exists():
        errors.append('_site does not exist; build_site.py must run first')
    else:
        pages=sorted(SITE.rglob('*.html'))
        required_files=('index.html','root.js','data/root-navigation.json','data/root-record-index.json')
        for rel in required_files:
            if not (SITE/rel).exists(): errors.append(f'missing required reader file: {rel}')
        if not (SITE/'index.html').exists():
            errors.append('index.html is missing')
        else:
            text=(SITE/'index.html').read_text(encoding='utf-8',errors='replace')
            for required in ('id="root-tree"','id="center-frame"','id="frame-content"','WORLD','AXIS','./root.js'):
                if required not in text: errors.append(f'index.html missing root reader feature: {required}')
            if '<iframe' in text: errors.append('index.html contains retired iframe dependency')
        js=(SITE/'root.js').read_text(encoding='utf-8',errors='replace') if (SITE/'root.js').exists() else ''
        for required in ('root-record-index.json','root-navigation.json','navigation_path','function collection','function row'):
            if required not in js: errors.append(f'root.js missing navigation feature: {required}')
        if SITE.exists() and not pages: errors.append('Pages artifact contains no HTML documents')
    count=len(list(SITE.rglob('*.html'))) if SITE.exists() else 0
    print(f'Built HTML pages checked: {count}')
    if errors:
        print('SITE SHELL VALIDATION FAILED');[print('-',e) for e in errors];return 1
    print('SITE SHELL VALIDATION PASSED');return 0

if __name__=='__main__':raise SystemExit(main())
