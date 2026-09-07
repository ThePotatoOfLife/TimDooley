from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

# Repair the two legacy religious datasets before the broader import job commits.
for name in ['data/religious-foundations/enriched-records.json','data/religious-foundations/minor-traditions.json']:
    path = ROOT / name
    raw = path.read_text(encoding='utf-8')
    slash_n = chr(92) + 'n'
    count = raw.count(slash_n)
    print(f'{name}: literal backslash-n separators={count}')
    fixed = raw.replace(slash_n, chr(10))
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
        print(f'repaired {name}')

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
