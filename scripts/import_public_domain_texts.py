from pathlib import Path
from urllib.request import urlopen
import json
import re

ROOT = Path(__file__).resolve().parents[1]

for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
    path = ROOT / name
    raw = path.read_text(encoding='utf-8-sig')
    slash_n = chr(92) + 'n'
    print(f'{name}: literal backslash-n separators={raw.count(slash_n)}')
    # Normalize legacy token separators and trailing commas while preserving
    # commas that occur inside quoted strings.
    fixed = raw.replace(slash_n, chr(10))
    fixed = re.sub(r',([\s]*[}\]])', r'\1', fixed)
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
        print(f'normalized {name}')
    try:
        with path.open(encoding='utf-8') as f: json.load(f)
    except json.JSONDecodeError as exc:
        data = path.read_text(encoding='utf-8')
        start=max(0,exc.pos-180); end=min(len(data),exc.pos+220)
        print('JSON ERROR CONTEXT:', repr(data[start:end]))
        raise
    print(f'VALID JSON {name}')

TARGETS = {
    'data/texts/christianity/bible-kjv-1611-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/30/pg30.txt',
    'data/texts/islam/quran-rodwell-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/2800/pg2800.txt',
    'data/texts/hinduism/bhagavad-gita-arnold-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/2388/pg2388.txt',
}

for relative, url in TARGETS.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=60) as response:
        data = response.read().decode('utf-8')
    path.write_text(data, encoding='utf-8')
    print(f'imported {relative}: {len(data):,} characters')
