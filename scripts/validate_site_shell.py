#!/usr/bin/env python3
"""Verify the generated Pages artifact has one canonical, consistent site shell."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'_site'
EXPECTED=[('home','index.html','Home'),('repository','repository.html','Repository'),('timeline','timeline.html','Timeline'),('world','nations.html','World'),('people','people.html','People'),('ideas','belief.html','Ideas'),('culture','culture.html','Culture'),('books','books.html','Books'),('potatoism','potatoism.html','Potatoism'),('movements','extremism.html','Movements'),('hawkins','hawkins.html','Hawkins')]
class HeaderParser(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.headers=0; self.canonical=0; self.links=[]; self.in_canonical=False; self.current=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag.lower()=='header':
            self.headers+=1
            self.in_canonical=attrs.get('data-site-header')=='canonical'
            if self.in_canonical:self.canonical+=1
        elif tag.lower()=='a' and self.in_canonical and 'data-nav' in attrs:
            self.current={'key':attrs['data-nav'],'href':attrs.get('href'),'label':''}; self.links.append(self.current)
    def handle_data(self,data):
        if self.current and self.in_canonical:self.current['label']+=data
    def handle_endtag(self,tag):
        if tag.lower()=='a': self.current=None
        elif tag.lower()=='header': self.in_canonical=False

def check(page):
    p=HeaderParser(); p.feed(page.read_text(encoding='utf-8',errors='replace')); errors=[]
    if p.canonical!=1: errors.append(f'{page.relative_to(SITE)}: expected exactly one canonical header, found {p.canonical}'); return errors
    if p.headers!=p.canonical: errors.append(f'{page.relative_to(SITE)}: {p.headers-p.canonical} legacy/non-canonical header(s) remain')
    actual=[x['key'] for x in p.links]; expected=[x[0] for x in EXPECTED]
    if actual!=expected: errors.append(f'{page.relative_to(SITE)}: navigation keys differ from canonical order: {actual}')
    emap={k:(href,label) for k,href,label in EXPECTED}
    for x in p.links:
        href,label=emap[x['key']]
        got=x['href'] or ''
        if not got: errors.append(f'{page.relative_to(SITE)}: {x["key"]} has no href')
        elif not got.endswith(href): errors.append(f'{page.relative_to(SITE)}: {x["key"]} href is {got!r}, expected suffix {href!r}')
        if ''.join(x['label'].split())!=''.join(label.split()): errors.append(f'{page.relative_to(SITE)}: {x["key"]} label is {x["label"]!r}, expected {label!r}')
    return errors

def main():
    errors=[]
    if not SITE.exists(): errors.append('_site does not exist; build_site.py must run first')
    else:
        pages=sorted(SITE.rglob('*.html'))
        if not pages: errors.append('_site contains no HTML pages')
        for page in pages: errors.extend(check(page))
    count=len(list(SITE.rglob('*.html'))) if SITE.exists() else 0; print(f'Built HTML pages checked: {count}')
    if errors:
        print('SITE SHELL VALIDATION FAILED'); [print('-',e) for e in errors]; return 1
    print('SITE SHELL VALIDATION PASSED'); return 0
if __name__=='__main__': raise SystemExit(main())
