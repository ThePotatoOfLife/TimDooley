#!/usr/bin/env python3
"""Verify the generated Pages artifact has a valid shell, with the center homepage exempted."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'_site'; CENTER={'index.html','root.html'}
EXPECTED=[('home','index.html','Home'),('read','scroll.html','Read'),('atlas','repository.html','Atlas'),('timeline','timeline.html','Timeline'),('potatoism','potatoism.html','Potatoism'),('explore','explore.html','Explore')]
class HeaderParser(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.headers=0; self.canonical=0; self.links=[]; self.in_canonical=False; self.current=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag.lower()=='header':
            self.headers+=1; self.in_canonical=attrs.get('data-site-header')=='canonical'; self.canonical+=int(self.in_canonical)
        elif tag.lower()=='a' and self.in_canonical and 'data-nav' in attrs:
            self.current={'key':attrs['data-nav'],'href':attrs.get('href'),'label':''}; self.links.append(self.current)
    def handle_data(self,data):
        if self.current and self.in_canonical:self.current['label']+=data
    def handle_endtag(self,tag):
        if tag.lower()=='a':self.current=None
        elif tag.lower()=='header':self.in_canonical=False

def check(page):
    if page.name in CENTER and page.parent==SITE:
        text=page.read_text(encoding='utf-8',errors='replace'); errors=[]
        if page.name=='index.html' and 'root-tree' not in text: errors.append('center homepage missing root-tree mount')
        if page.name=='index.html' and 'root.js' not in text: errors.append('center homepage missing root.js')
        return errors
    p=HeaderParser();p.feed(page.read_text(encoding='utf-8',errors='replace'));errors=[]
    if p.canonical!=1:errors.append(f'{page.relative_to(SITE)}: expected exactly one canonical header, found {p.canonical}');return errors
    if p.headers!=p.canonical:errors.append(f'{page.relative_to(SITE)}: {p.headers-p.canonical} non-canonical header(s) remain')
    actual=[x['key'] for x in p.links];expected=[x[0] for x in EXPECTED]
    if actual!=expected:errors.append(f'{page.relative_to(SITE)}: navigation keys differ: {actual}')
    emap={k:(href,label) for k,href,label in EXPECTED}
    for x in p.links:
        href,label=emap[x['key']];got=x['href'] or ''
        if not got:errors.append(f'{page.relative_to(SITE)}: {x["key"]} has no href')
        elif not got.endswith(href):errors.append(f'{page.relative_to(SITE)}: {x["key"]} href {got!r}, expected suffix {href!r}')
        if ''.join(x['label'].split())!=''.join(label.split()):errors.append(f'{page.relative_to(SITE)}: {x["key"]} label {x["label"]!r}, expected {label!r}')
    return errors

def main():
    errors=[]
    if not SITE.exists():errors.append('_site does not exist; build_site.py must run first')
    else:
        pages=sorted(SITE.rglob('*.html'))
        if not pages:errors.append('_site contains no HTML pages')
        for page in pages:errors.extend(check(page))
    count=len(list(SITE.rglob('*.html'))) if SITE.exists() else 0;print(f'Built HTML pages checked: {count}')
    if errors:
        print('SITE SHELL VALIDATION FAILED');[print('-',e) for e in errors];return 1
    print('SITE SHELL VALIDATION PASSED');return 0
if __name__=='__main__':raise SystemExit(main())
