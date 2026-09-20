#!/usr/bin/env python3
"""Validate the Current World live-news projection and its House boundaries."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(rel):
    p=ROOT/rel
    if not p.exists():
        errors.append(f"missing {rel}")
        return ""
    return p.read_text(encoding="utf-8",errors="replace")

def require(text,token,owner):
    if token not in text:
        errors.append(f"{owner} missing marker: {token}")

html=read("news/index.html")
js=read("app/news.js")
css=read("app/news.css")
home=read("index.html")
house=read("house/index.html")

try:
    cfg=json.loads(read("data/news/sources.json"))
except Exception as exc:
    cfg={}
    errors.append(f"invalid data/news/sources.json: {exc}")

for token in (
    'data-news-view="latest"',
    'data-news-view="briefing"',
    'data-news-view="clusters"',
    'data-news-view="sources"',
    'data-news-horizon="24h"',
    'data-news-lens="north-arctic"',
    'data-news-pulse',
    'data-news-clusters',
    'data-news-source-lanes',
    'data-news-briefing',
    'source-balanced rotation',
    'data-news-readable',
    'Readable here only',
    '../world-map/',
    'Repeated coverage',
    'not a truth, consensus, importance or endorsement score',
    'data-tts-longform',
    'data-tts-root="#news-reading-stream"',
    'data-tts-trigger-label="Read all news"',
    'data-tts-exclude=".news-story-kicker,.news-story-footer,.news-story-image,.news-story-expand,.news-empty"',
    'data-provider="publisher-rss"',
):
    require(html,token,"news/index.html")

for token in (
    "function coverageClusters",
    "function normalizePublisherRss",
    "async function loadPublisherRss",
    "publisher-excerpt",
    "Full report ↗",
    "function sourceBalancedBriefing",
    "function renderBriefing",
    "readable=params.get('readable')==='1'",
    "allRows.filter(r=>clean(r.summary).length>0)",
    "baseProviders.filter(id=>id!==\'publisher-rss\')",
    "function renderPulse",
    "data-news-expand",
    "Show full excerpt",
    "querySelectorAll('[data-news-category]')",
    "querySelectorAll('[data-news-lens]')",
    "querySelectorAll('[data-news-horizon]')",
    "function renderClusters",
    "function providerContract",
    "function publisherFeedRegister",
    "function renderSourceLanes",
    "function mergeQueries",
    "horizonMs(config,horizon)",
    "sourceState(host,id,'error')",
    "CACHE_TTL=10*60*1000",
):
    require(js,token,"app/news.js")


if re.search(r"(?<!\$)\$\('\[data-news-category\]',tabs\)\.forEach", js):
    errors.append("News category controls must use $() node-list selection, not $() single-element selection")
if re.search(r"(?<!\$)\$\('\[data-news-lens\]',lenses\)\.forEach", js):
    errors.append("News lens controls must use $() node-list selection, not $() single-element selection")
if re.search(r"(?<!\$)\$\('\[data-news-horizon\]',horizons\)\.forEach", js):
    errors.append("News horizon controls must use $() node-list selection, not $() single-element selection")

for token in (
    ".news-pulse-grid",
    ".news-briefing",
    ".news-briefing-item",
    ".news-readable-toggle",
    ".news-view-switch",
    ".news-clusters",
    ".news-source-lanes",
    ".news-source-contract",
    ".news-feed-register",
    ".news-feed-contract",
    ".news-console",
    ".news-audio-reader",
    ".news-story-summary",
    ".news-story-image",
    ".news-story-expand",
    ".news-story.is-expanded .news-story-summary",
):
    require(css,token,"app/news.css")

for token in ('data-news-mode="preview"','publisher-rss','app/news.js?v=20260920g','app/news.css?v=20260920g'):
    require(home,token,"index.html")
require(house,'href="../news/">Current World</a>',"house/index.html")

providers={row.get("id") for row in cfg.get("providers",[]) if isinstance(row,dict)}
if providers != {"gdelt","publisher-rss","hacker-news","spaceflight-news"}:
    errors.append(f"unexpected provider contract: {sorted(providers)}")
for row in cfg.get("providers",[]):
    if not isinstance(row,dict):
        continue
    if not row.get("display_mode") or not row.get("reuse_mode"):
        errors.append(f"news provider missing display/reuse metadata: {row.get('id')}")
feeds=cfg.get("publisher_feeds",[])
for row in feeds:
    if not isinstance(row,dict):
        continue
    if not row.get("reuse_mode") or not row.get("reuse_note") or not row.get("terms_url"):
        errors.append(f"publisher feed missing reuse/terms metadata: {row.get('id')}")
if len(feeds) < 4:
    errors.append("publisher RSS layer must declare at least four feeds")
if not all(row.get("feed_url") and row.get("name") for row in feeds if isinstance(row,dict)):
    errors.append("publisher RSS feeds require name and feed_url")
if "full article bodies" not in str(next((row.get("boundary","") for row in cfg.get("providers",[]) if row.get("id")=="publisher-rss"),"")).lower():
    errors.append("publisher RSS boundary must forbid full-article mirroring")

horizons={row.get("id") for row in cfg.get("horizons",[]) if isinstance(row,dict)}
if not {"3h","12h","24h","3d","7d"}.issubset(horizons):
    errors.append("news horizons must include 3h, 12h, 24h, 3d and 7d")
if not any(row.get("id")=="24h" and row.get("default") for row in cfg.get("horizons",[]) if isinstance(row,dict)):
    errors.append("24h must remain the default news horizon")
lens_ids={row.get("id") for row in cfg.get("lenses",[]) if isinstance(row,dict)}
for required in ("north-arctic","europe","ukraine-russia","middle-east","americas","asia-pacific","africa","economy-energy","security","science-tech"):
    if required not in lens_ids:
        errors.append(f"missing Current World lens: {required}")
transparency=cfg.get("source_transparency",{})
if transparency.get("no_ranking") is not True:
    errors.append("news source transparency must remain non-ranking")
boundary=str(cfg.get("epistemic_boundary","")).lower()
for phrase in ("similar headlines","geographic mentions","not corroboration"):
    if phrase not in boundary:
        errors.append(f"news epistemic boundary missing: {phrase}")

try:
    surfaces=json.loads(read("data/house/public-surfaces.json"))
    row=next((x for x in surfaces.get("surfaces",[]) if x.get("id")=="news"),None)
    if not row:
        errors.append("news surface missing from House public surfaces")
    else:
        if row.get("knowledge_owner") is not False:
            errors.append("news must remain a non-owning public view")
        if row.get("is_view") is not True:
            errors.append("news must remain typed as a view")
        if row.get("canonical_route")!="/news/":
            errors.append("news canonical route drift")
except Exception as exc:
    errors.append(f"could not validate public surface registry: {exc}")

try:
    bridge=json.loads(read("data/frontend-atlas-bridge.json"))
    if bridge.get("global_secondary_surfaces",{}).get("news")!="news/":
        errors.append("frontend bridge news projection drift")
except Exception as exc:
    errors.append(f"could not validate frontend bridge: {exc}")

if errors:
    print("CURRENT WORLD NEWS VALIDATION FAILED")
    for error in errors:
        print(" -",error)
    raise SystemExit(1)
print("Current World news validation passed: multi-view reader, source contract, House projection and epistemic boundaries are aligned.")
