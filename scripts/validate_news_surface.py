#!/usr/bin/env python3
"""Validate the Current World live-news projection and its reader-first boundaries."""
from __future__ import annotations
import json
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
    'class="news-header news-header--simple"',
    'class="news-primary-bar"',
    'class="news-filter-drawer"',
    'class="news-secondary-drawer"',
    'class="news-info-drawer"',
    'class="news-about-drawer"',
    '<b>Refine coverage</b>',
    'data-news-tabs',
    'data-news-lenses',
    'data-news-horizons',
    'data-news-search',
    'data-news-readable',
    'id="news-reading-stream"',
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
    'Readable here only',
    'Read all news',
    'appearing here is not project endorsement, verification or canon',
    'Repetition is not corroboration.',
    'data-tts-longform',
    'data-tts-root="#news-reading-stream"',
    'data-tts-trigger-label="Read all news"',
    'data-tts-exclude=".news-story-kicker,.news-story-footer,.news-story-image,.news-story-expand,.news-empty"',
    'data-provider="publisher-rss"',
):
    require(html,token,"news/index.html")

latest_pos=html.find('id="news-reading-stream"')
secondary_pos=html.find('class="news-secondary-drawer"')
if latest_pos < 0 or secondary_pos < 0 or latest_pos > secondary_pos:
    errors.append("Latest news must appear before secondary News drawers")

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
    "baseProviders.filter(id=>'publisher-rss'!=id)",
):
    pass

# Use exact runtime markers, including query-honest provider filtering.
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
    "baseProviders.filter(id=>id!=='publisher-rss')",
    "function renderPulse",
    "news-story--compact",
    "view!=='latest')more.open=true",
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

for token in (
    ".news-header--simple",
    ".news-primary-bar",
    ".news-filter-drawer",
    ".news-secondary-drawer",
    ".news-info-drawer",
    ".news-about-drawer",
    ".news-story--compact",
    ".news-pulse-grid",
    ".news-briefing",
    ".news-readable-toggle",
    ".news-view-switch",
    ".news-clusters",
    ".news-source-lanes",
    ".news-source-contract",
    ".news-feed-register",
    ".news-console",
    ".news-story-summary",
    ".news-story-expand",
):
    require(css,token,"app/news.css")

for token in ('data-news-mode="preview"','publisher-rss','app/news.js?v=20260920i','app/news.css?v=20260920i'):
    require(home,token,"index.html")
require(house,'href="../news/">Current World</a>',"house/index.html")

providers={row.get("id") for row in cfg.get("providers",[]) if isinstance(row,dict)}
if providers != {"gdelt","publisher-rss","hacker-news","spaceflight-news"}:
    errors.append(f"unexpected provider contract: {sorted(providers)}")
for row in cfg.get("providers",[]):
    if isinstance(row,dict) and (not row.get("display_mode") or not row.get("reuse_mode")):
        errors.append(f"news provider missing display/reuse metadata: {row.get('id')}")

feeds=cfg.get("publisher_feeds",[])
if len(feeds) < 4:
    errors.append("publisher RSS layer must declare at least four feeds")
for row in feeds:
    if isinstance(row,dict) and (not row.get("feed_url") or not row.get("name") or not row.get("reuse_mode") or not row.get("reuse_note") or not row.get("terms_url")):
        errors.append(f"publisher feed missing URL/reuse/terms metadata: {row.get('id')}")

presentation=cfg.get("presentation",{})
if int(presentation.get("max_feed",0)) < 60:
    errors.append("Current World must expose at least 60 stories in the main river")
if int(presentation.get("publisher_rss_items_per_feed",0)) != 10:
    errors.append("public no-key RSS adapter limit must remain explicit at 10 items per feed")
if not presentation.get("rss_adapter_note"):
    errors.append("RSS adapter public-limit note is required")

horizons={row.get("id") for row in cfg.get("horizons",[]) if isinstance(row,dict)}
if not {"3h","12h","24h","3d","7d"}.issubset(horizons):
    errors.append("news horizons must include 3h, 12h, 24h, 3d and 7d")
if not any(row.get("id")=="24h" and row.get("default") for row in cfg.get("horizons",[]) if isinstance(row,dict)):
    errors.append("24h must remain the default news horizon")

lens_ids={row.get("id") for row in cfg.get("lenses",[]) if isinstance(row,dict)}
for required in ("north-arctic","europe","ukraine-russia","middle-east","americas","asia-pacific","africa","economy-energy","security","science-tech"):
    if required not in lens_ids:
        errors.append(f"missing Current World lens: {required}")

if cfg.get("source_transparency",{}).get("no_ranking") is not True:
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
        if row.get("knowledge_owner") is not False: errors.append("news must remain a non-owning public view")
        if row.get("is_view") is not True: errors.append("news must remain typed as a view")
        if row.get("canonical_route")!="/news/": errors.append("news canonical route drift")
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

print("Current World news validation passed: simple reader-first hierarchy, source contract, House projection and epistemic boundaries are aligned.")
