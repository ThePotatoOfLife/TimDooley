import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "data/indicator-catalog.json": ["version", "dimensions", "coverage_policy", "derived_metrics"],
    "data/domain-coupling.json": ["version", "domains", "relationship_types", "priority_paths"],
    "data/religious-layer-map.json": ["version", "layers", "taxonomy", "coupling_rules"],
}

def load(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)

errors = []
for rel, keys in REQUIRED.items():
    p = ROOT / rel
    if not p.exists():
        errors.append(f"missing required expansion file: {rel}")
        continue
    try:
        data = load(p)
    except Exception as exc:
        errors.append(f"invalid JSON {rel}: {exc}")
        continue
    for key in keys:
        if key not in data or data[key] in (None, "", [], {}):
            errors.append(f"{rel}: empty/missing {key}")

ind = load(ROOT / "data/indicator-catalog.json")
dom = load(ROOT / "data/domain-coupling.json")
rel = load(ROOT / "data/religious-layer-map.json")

ids = [x.get("id") for x in ind["dimensions"]]
if len(ids) != len(set(ids)):
    errors.append("indicator-catalog: duplicate dimension IDs")
if len(ids) < 30:
    errors.append("indicator-catalog: expansion unexpectedly small")

domain_ids = [x.get("id") for x in dom["domains"]]
if len(domain_ids) != len(set(domain_ids)):
    errors.append("domain-coupling: duplicate domain IDs")
if len(dom["relationship_types"]) < 15:
    errors.append("domain-coupling: relationship grammar unexpectedly small")

layer_ids = [x.get("id") for x in rel["layers"]]
if len(layer_ids) != len(set(layer_ids)):
    errors.append("religious-layer-map: duplicate layer IDs")
for layer in rel["layers"]:
    if not (ROOT / layer["file"]).exists():
        errors.append(f"religious-layer-map: missing layer file {layer['file']}")

if errors:
    print("EXPANSION VALIDATION FAILED")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("EXPANSION VALIDATION OK")
print(f"indicator dimensions: {len(ind['dimensions'])}")
print(f"derived metrics: {len(ind['derived_metrics'])}")
print(f"domains: {len(dom['domains'])}")
print(f"relationship types: {len(dom['relationship_types'])}")
print(f"priority paths: {len(dom['priority_paths'])}")
print(f"religious layers: {len(rel['layers'])}")
