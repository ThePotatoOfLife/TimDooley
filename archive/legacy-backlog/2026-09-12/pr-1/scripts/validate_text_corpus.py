import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
corpus = json.loads((ROOT / 'data/religious-text-corpus.json').read_text(encoding='utf-8'))
errors = []
seen = set()
for item in corpus.get('local_full_texts', []):
    ident = item.get('id')
    path = item.get('path')
    if not ident or not path:
        errors.append(f'missing id/path: {item}')
        continue
    if ident in seen:
        errors.append(f'duplicate local text id: {ident}')
    seen.add(ident)
    target = ROOT / path
    if not target.is_file():
        errors.append(f'missing local text: {path}')
        continue
    size = target.stat().st_size
    if size < 1000:
        errors.append(f'local text suspiciously small: {path} ({size} bytes)')
    print(f'LOCAL TEXT OK: {ident} · {size:,} bytes · {path}')

if errors:
    print('TEXT CORPUS: FAIL')
    for error in errors:
        print('-', error)
    raise SystemExit(1)
print(f'TEXT CORPUS: PASS · {len(seen)} local editions validated')
