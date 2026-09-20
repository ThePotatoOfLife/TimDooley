import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPANSION_REGISTRY = ROOT / "data/expansion-registry.json"
EXPANSION_DIR = ROOT / "data/expansions"
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
registry = load(EXPANSION_REGISTRY)

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

registry_rows=[x for x in registry.get("waves",[]) if isinstance(x,dict)]
registry_files=[x.get("file") for x in registry_rows if x.get("file","").startswith("data/expansions/") and x.get("file","").endswith(".json")]
disk_files=sorted(p.relative_to(ROOT).as_posix() for p in EXPANSION_DIR.glob("*.json"))
if len(registry_files)!=len(set(registry_files)):
    errors.append("expansion-registry: duplicate data/expansions file registrations")
if set(registry_files)!=set(disk_files):
    missing=sorted(set(disk_files)-set(registry_files))
    stale=sorted(set(registry_files)-set(disk_files))
    if missing: errors.append(f"expansion-registry: unclassified expansion files: {missing}")
    if stale: errors.append(f"expansion-registry: registered files missing on disk: {stale}")
allowed_status={
    "verified-present","active-referenced-research","research-reservoir",
    "migration-candidate","promotion-backlog","superseded-seed-retained","promoted","archived"
}
for row in registry_rows:
    path=row.get("file","")
    if path.startswith("data/expansions/") and row.get("status") not in allowed_status:
        errors.append(f"expansion-registry: {path} has unclassified status {row.get('status')!r}")
inv=registry.get("directory_inventory",{})
if inv.get("json_file_count")!=len(disk_files) or inv.get("registered_json_file_count")!=len(registry_files):
    errors.append("expansion-registry: directory inventory counts drifted")

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
print(f"classified expansion JSON files: {len(registry_files)}")
