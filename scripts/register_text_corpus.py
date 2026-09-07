import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
    path=ROOT/name; raw=path.read_text(encoding='utf-8-sig')
    try: json.loads(raw)
    except json.JSONDecodeError as exc:
        lines=raw.splitlines(); print('FAILED',name,'at',exc.lineno,exc.colno)
        for i in range(max(0,exc.lineno-6),min(len(lines),exc.lineno+1)): print(f'LINE {i+1}:',repr(lines[i]))
        raise
    print('validated',name)
