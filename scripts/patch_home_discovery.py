#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "_site" / "index.html"

if not PAGE.exists():
    raise SystemExit("_site/index.html missing")

text = PAGE.read_text(encoding="utf-8")

needle = '''      <a href="context/"><strong>Context &amp; Evidence</strong><span>Sources · boundaries · comparisons</span></a>\n    </nav>'''
replacement = '''      <a href="context/"><strong>Context &amp; Evidence</strong><span>Sources · boundaries · comparisons</span></a>\n      <a href="questions/"><strong>Questions</strong><span>Who · What · Why · How</span></a>\n      <a href="index-a-z/"><strong>A–Z Index</strong><span>Entities · aliases · concepts</span></a>\n      <a href="faq/"><strong>FAQ</strong><span>Main answers · long tail</span></a>\n    </nav>'''
if needle in text:
    text = text.replace(needle, replacement, 1)

footer_old = '''<a href="sitemap.xml">Sitemap</a> · <a href="llms.txt">AI/LLM guide</a>.'''
footer_new = '''<a href="questions/">Questions</a> · <a href="index-a-z/">A–Z</a> · <a href="sitemap-index.xml">Sitemap index</a> · <a href="llms.txt">AI/LLM guide</a> · <a href="llms-full.txt">Full machine index</a>.'''
text = text.replace(footer_old, footer_new)

head_old = '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap.xml">'
head_new = '<link rel="sitemap" type="application/xml" href="https://thepotatooflife.github.io/TimDooley/sitemap-index.xml">\n  <link rel="alternate" type="application/json" href="https://thepotatooflife.github.io/TimDooley/discovery.json" title="Archive discovery index">\n  <link rel="alternate" type="text/plain" href="https://thepotatooflife.github.io/TimDooley/llms-full.txt" title="Full machine retrieval index">'
text = text.replace(head_old, head_new)

PAGE.write_text(text, encoding="utf-8")
print("Patched deployed homepage with crawlable discovery entry points")
