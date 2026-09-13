#!/usr/bin/env python3
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
reg=json.loads((R/'data/atlas-registry.json').read_text())
errors=[]; warnings=[]
active=[n for n in reg.get('nodes',[]) if n.get('status')=='active']
ids=[n['id'] for n in active]; routes=[n['route'] for n in active]; owners=[n['owner_path'] for n in active]
if len(ids)!=len(set(ids)): errors.append('duplicate_active_id')
if len(routes)!=len(set(routes)): errors.append('duplicate_active_route')
if len(owners)!=len(set(owners)): warnings.append('duplicate_owner_candidate')
for n in active:
    if not (R/n['owner_path']).exists(): errors.append('missing_owner:'+n['id'])
bridge=(R/'data/frontend-atlas-bridge.json').read_text(encoding='utf-8',errors='replace')
if 'exactly five simple public doors' in bridge or 'exactly five primary public doors' in bridge: warnings.append('legacy_navigation_contract')
site=(R/'scripts/validate_site_shell.py').read_text(encoding='utf-8',errors='replace')
if 'restore_canonical_world_route()' in site: warnings.append('validator_mutates_output')
report={'errors':sorted(set(errors)),'warnings':sorted(set(warnings))}
(R/'atlas-swamp-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(1 if errors else 0)
