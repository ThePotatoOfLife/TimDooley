#!/usr/bin/env python3
"""Verify the generated Pages artifact uses the self-contained reader shell."""
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
        if pages != [SITE/'index.html']:
            errors.append('public site must contain exactly one HTML document: index.html')
        if pages:
            text=(SITE/'index.html').read_text(encoding='utf-8',errors='replace')
            for required in ('id="app"','id="rail"','id="reader"','id="content"','WORLD','AXIS','data/root-navigation.json','data/root-record-index.json'):
                if required not in text:
                    errors.append(f'index.html missing required self-contained reader feature: {required}')
            for forbidden in ('<iframe','center.html','<link rel="stylesheet"','<script src=','repository.html','axis.html','node.html','people.html','nations.html','timeline.html'):
                if forbidden in text:
                    errors.append(f'index.html contains forbidden fragile dependency or retired page: {forbidden}')
    count=len(list(SITE.rglob('*.html'))) if SITE.exists() else 0
    print(f'Built HTML pages checked: {count}')
    if errors:
        print('SITE SHELL VALIDATION FAILED');[print('-',e) for e in errors];return 1
    print('SITE SHELL VALIDATION PASSED');return 0

if __name__=='__main__':raise SystemExit(main())
