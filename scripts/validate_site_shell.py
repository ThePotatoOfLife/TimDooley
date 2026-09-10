#!/usr/bin/env python3
"""Verify the built Pages artifact for the current manifest-driven archive."""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
SITE_BASE='/TimDooley'
REPORT=ROOT/'site-shell-report.txt'


def load_json(path,errors):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'invalid JSON: {path.relative_to(SITE)} — {exc}');return {}


def resolve_local_reference(page:Path,raw:str)->Path|None:
    """Resolve a built-page reference using the actual GitHub Pages base path."""
    if raw==SITE_BASE or raw==f'{SITE_BASE}/':return SITE
    if raw.startswith(f'{SITE_BASE}/'):
        return (SITE/raw[len(SITE_BASE)+1:]).resolve()
    if raw.startswith('/'):
        return None
    return (page.parent/raw).resolve()


def annotation(kind:str,message:str)->str:
    clean=message.replace('%','%25').replace('\r','%0D').replace('\n','%0A')
    return f'::{kind} title=Built site shell::{clean}'


def write_report(pages,errors,warnings):
    lines=[
        f'Built HTML pages checked: {len(pages)}',
        f'Errors: {len(errors)} · Warnings: {len(warnings)}',
        '',
    ]
    if warnings:
        lines.append('WARNINGS')
        lines.extend(f'- {w}' for w in warnings)
        lines.append('')
    if errors:
        lines.append('ERRORS')
        lines.extend(f'- {e}' for e in errors)
        lines.append('')
    REPORT.write_text('\n'.join(lines),encoding='utf-8')


def main():
    errors=[];warnings=[]
    if not SITE.exists():
        errors.append('_site does not exist; build_site.py must run first')
        pages=[]
    else:
        pages=sorted(SITE.rglob('*.html'))
        required_files=(
            'index.html','manifest.json','app/app.js','app/style.css',
            'knowledge/indexes/context-graph.json','knowledge/indexes/core-index.json',
            'sitemap.xml','llms.txt'
        )
        for rel in required_files:
            if not (SITE/rel).exists():errors.append(f'missing required site file: {rel}')

        manifest=load_json(SITE/'manifest.json',errors) if (SITE/'manifest.json').exists() else {}
        branches={b.get('id') for b in manifest.get('branches',[]) if b.get('id')}
        expected={'tim','son','spirit','transformation','cosmology','body','traditions','north','world','chronology','works','sources'}
        missing=sorted(expected-branches)
        if missing:errors.append(f'built manifest missing branches: {missing}')

        index=SITE/'index.html'
        if index.exists():
            text=index.read_text(encoding='utf-8',errors='replace')
            for required in ('id="reader"','id="branches"','app/app.js','app/style.css','application/ld+json','llms.txt','sitemap.xml','POTATO'):
                if required not in text:errors.append(f'index.html missing current archive feature: {required}')
            for retired in ('id="root-tree"','id="center-frame"','id="frame-content"','./root.js'):
                if retired in text:warnings.append(f'index.html still contains retired reader marker: {retired}')
            if '<iframe' in text:errors.append('index.html contains retired iframe dependency')

        app=(SITE/'app/app.js').read_text(encoding='utf-8',errors='replace') if (SITE/'app/app.js').exists() else ''
        for required in ('manifest.json','context-graph.json','showContext','showRecord','renderMarkdown'):
            if required not in app:errors.append(f'app/app.js missing current navigation feature: {required}')

        # Generated SEO surfaces must actually exist and contain real pages.
        topic_pages=list((SITE/'topics').glob('*/index.html')) if (SITE/'topics').exists() else []
        context_pages=list((SITE/'context').glob('*/index.html')) if (SITE/'context').exists() else []
        record_pages=list((SITE/'records').glob('*/index.html')) if (SITE/'records').exists() else []
        if len(topic_pages)<len(expected):errors.append(f'expected at least {len(expected)} topic pages; found {len(topic_pages)}')
        if not context_pages:errors.append('no generated context pages found')
        if not record_pages:errors.append('no generated record pages found')

        sitemap=(SITE/'sitemap.xml').read_text(encoding='utf-8',errors='replace') if (SITE/'sitemap.xml').exists() else ''
        for fragment in ('/topics/tim/','/topics/son/','/records/tim-dooley/','/context/'):
            if fragment not in sitemap:errors.append(f'sitemap.xml missing expected route fragment: {fragment}')
        llms=(SITE/'llms.txt').read_text(encoding='utf-8',errors='replace') if (SITE/'llms.txt').exists() else ''
        llms_lower=llms.lower()
        for term in ('tim dooley','potato of life','generated canonical topics','generated contextual constellations'):
            if term not in llms_lower:errors.append(f'llms.txt missing discovery term/section: {term}')

        # Validate local references inside generated HTML, resolving relative to each page.
        ref=re.compile(r'''(?:href|src)=["']([^"'#?]+)["']''',re.I)
        bad=[]
        site_root=SITE.resolve()
        for h in pages:
            for raw in ref.findall(h.read_text(encoding='utf-8',errors='replace')):
                if raw.startswith(('http:','https:','mailto:','javascript:','data:')):continue
                target=resolve_local_reference(h,raw)
                if target is None:
                    bad.append(f'{h.relative_to(SITE)} -> unsupported root-relative reference {raw}')
                    continue
                try:target.relative_to(site_root)
                except ValueError:
                    warnings.append(f'{h.relative_to(SITE)} -> reference escapes site artifact: {raw}')
                    continue
                if not target.exists():bad.append(f'{h.relative_to(SITE)} -> {raw}')
        if bad:
            errors.append(f'broken local references in built site: {len(bad)}')
            errors.extend(f'broken reference: {item}' for item in bad[:100])
            if len(bad)>100:errors.append(f'{len(bad)-100} additional broken references omitted from annotations')
        if not pages:errors.append('Pages artifact contains no HTML documents')

    write_report(pages,errors,warnings)
    print(f'Built HTML pages checked: {len(pages)}')
    print(f'Errors: {len(errors)} · Warnings: {len(warnings)}')
    for w in warnings[:50]:
        print('WARNING:',w)
        print(annotation('warning',w))
    if errors:
        print('SITE SHELL VALIDATION FAILED')
        for e in errors:
            print('-',e)
            print(annotation('error',e))
        return 1
    print('SITE SHELL VALIDATION PASSED');return 0

if __name__=='__main__':raise SystemExit(main())
