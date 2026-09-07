from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
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
