#!/usr/bin/env python3
"""Regression checks for Timeline findability and chronology-first presentation."""
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(rel):
    p=ROOT/rel
    if not p.is_file():
        errors.append(f"missing {rel}")
        return ""
    return p.read_text(encoding="utf-8")

home=read("index.html")
timeline=read("timeline/index.html")

if 'href="timeline/">Timeline</a>' not in home:
    errors.append('Home main navigation must expose literal "Timeline" label')

if re.search(r'href="timeline/">Time</a>',home):
    errors.append('Home must not hide Timeline behind the sole label "Time"')

if not re.search(r'<h1>\s*TIMELINE\s*</h1>',timeline,re.I):
    errors.append('/timeline/ must use TIMELINE as the visible H1')

for marker in ('id="tim-project-timeline"','id="timeline-explorer"','Tim &amp; project timeline'):
    if marker not in timeline:
        errors.append(f"/timeline/ missing discoverability marker: {marker}")

static_i=timeline.find('id="tim-project-timeline"')
fig_i=timeline.find('<figure class="editorial-visual')
explore_i=timeline.find('id="timeline-explorer"')
if min(static_i,fig_i,explore_i) < 0:
    errors.append("Timeline ordering markers unavailable")
elif not (static_i < fig_i < explore_i):
    errors.append("Timeline must show dated Tim/project chronology before methodology graphic and full explorer")

event_count=len(re.findall(r'class="static-event(?:\s+hinge)?"',timeline))
if event_count < 25:
    errors.append(f"Timeline static chronology unexpectedly thin: {event_count} events")

if 'class="static-events"' not in timeline or '.static-events:before' not in timeline:
    errors.append("Timeline static chronology must retain visible vertical-rail styling")

if errors:
    print("Timeline discoverability validation failed:")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print(f"Timeline discoverability OK: {event_count} static dated events; noun-visible Home route; chronology-first layout.")
