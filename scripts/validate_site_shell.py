#!/usr/bin/env python3
"""Verify the built Pages artifact for the current manifest-driven archive.

The validator writes ``site-shell-report.txt`` as a CI diagnostic artifact so a
failed deployment can be inspected without weakening the deployment gate.
"""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'_site'
REPORT=ROOT/'site-shell-report.txt'


def load_json(path,errors):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        errors.append(f'invalid JSON: {path.relative_to(SITE)} — {exc}');return {}


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
            'world-map/index.html','world-map/3d.html','world-map/3d-app.js','world-map/3d-hover.js','world-map/3d-pathfinder.js',
            'data/world-map-3d-runtime.json','data/world-relational-map.json','sitemap.xml','llms.txt'
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

        # The map is a first-class public surface and must survive every build.
        map3d=(SITE/'world-map/3d.html').read_text(encoding='utf-8',errors='replace') if (SITE/'world-map/3d.html').exists() else ''
        mapapp=(SITE/'world-map/3d-app.js').read_text(encoding='utf-8',errors='replace') if (SITE/'world-map/3d-app.js').exists() else ''
        hover=(SITE/'world-map/3d-hover.js').read_text(encoding='utf-8',errors='replace') if (SITE/'world-map/3d-hover.js').exists() else ''
        for required in ('World Relational Atlas','id="map"','id="compare"','id="relationType"','id="traceDepth"','src="./3d-hover.js"','Trace · 3 hops'):
            if required not in map3d:errors.append(f'world-map/3d.html missing current atlas shell feature: {required}')
        for required in ('semantic-hubs','trace-hubs','compare-hubs','window.goCountry','window.fitTrace','function fitCodes','function traceGraph','Trace outward','fitBounds',"searchParams.set('depth'"):
            if required not in mapapp:errors.append(f'world-map/3d-app.js missing current atlas application feature: {required}')
        for required in ('GEO_LOCAL','REST_LOCAL','fallbackRestCountries','capital-cities','capital-city-labels','countryHtml','capitalHtml',"await import('./3d-app.js')"):
            if required not in hover:errors.append(f'world-map/3d-hover.js missing resilient/hover feature: {required}')
        if map3d and 'navigation handles rather than fake geographic locations' not in map3d:
            errors.append('world-map/3d.html missing semantic-coordinate boundary')
        if mapapp and 'visited.has(other)' not in mapapp:
            errors.append('world-map/3d-app.js missing recursive Trace cycle guard')
        if hover and 'return bestGeometryResponse()' not in hover:
            errors.append('world-map/3d-hover.js missing local-first geometry fallback')
        if hover and 'fetchJsonResponse(REST_LOCAL' not in hover:
            errors.append('world-map/3d-hover.js missing local-first country runtime fallback')
        runtime=load_json(SITE/'data/world-map-3d-runtime.json',errors) if (SITE/'data/world-map-3d-runtime.json').exists() else {}
        if runtime and runtime.get('status')!='active experimental renderer contract':
            errors.append('built world-map-3d-runtime has unexpected status')
        if runtime and runtime.get('compare_mode',{}).get('status') not in {'implemented','implemented-basic'}:
            errors.append('built world-map runtime does not preserve implemented Compare status')
        if runtime and runtime.get('trace_mode',{}).get('status') not in {'implemented','implemented-recursive-country','implemented-basic'}:
            errors.append('built world-map runtime does not preserve recursive Trace status')
        if runtime and runtime.get('trace_mode',{}).get('maximum_depth')!=3:
            errors.append('built world-map runtime does not preserve Trace depth contract')

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
        for h in pages:
            for raw in ref.findall(h.read_text(encoding='utf-8',errors='replace')):
                if raw.startswith(('http:','https:','mailto:','javascript:','data:')):continue
                target=(h.parent/raw).resolve()
                try:target.relative_to(SITE.resolve())
                except ValueError:continue
                if not target.exists():bad.append(f'{h.relative_to(SITE)} -> {raw}')
        if bad:errors.append(f'broken local references in built site: {len(bad)}; examples: {bad[:8]}')
        if not pages:errors.append('Pages artifact contains no HTML documents')

    lines=[f'Built HTML pages checked: {len(pages)}',f'Errors: {len(errors)} · Warnings: {len(warnings)}']
    lines.extend(f'WARNING: {w}' for w in warnings[:50])
    if errors:
        lines.append('SITE SHELL VALIDATION FAILED');lines.extend(f'- {e}' for e in errors)
    else:lines.append('SITE SHELL VALIDATION PASSED')
    report='\n'.join(lines)+'\n';REPORT.write_text(report,encoding='utf-8');print(report,end='')
    return 1 if errors else 0

if __name__=='__main__':raise SystemExit(main())
