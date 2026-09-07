from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
 p=ROOT/name; lines=p.read_text(encoding='utf-8-sig').splitlines(); print(name)
 for i in range(min(17,len(lines))): print(i+1,repr(lines[i]))
 try: json.loads('\n'.join(lines))
 except Exception as e: print('ERR',e); raise
