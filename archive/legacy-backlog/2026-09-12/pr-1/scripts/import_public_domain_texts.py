from pathlib import Path
from urllib.request import urlopen
import json
import re

ROOT = Path(__file__).resolve().parents[1]

# Legacy foundation files may contain literal escaped line separators. Normalize
# those first, then require strict JSON before importing any texts.
for name in [
    'data/religious-foundations/enriched-records.json',
    'data/religious-foundations/minor-traditions.json',
]:
    path = ROOT / name
    raw = path.read_text(encoding='utf-8-sig')
    fixed = raw.replace('\\\\n', '\n').replace('\\n', '\n')
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
    with path.open(encoding='utf-8') as f:
        json.load(f)
    print(f'VALID JSON {name}')

TARGETS = {
    'data/texts/christianity/bible-kjv-1611-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/30/pg30.txt',
    'data/texts/islam/quran-rodwell-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/2800/pg2800.txt',
    'data/texts/hinduism/bhagavad-gita-arnold-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/2388/pg2388.txt',
    'data/texts/judaism/torah-tyndale-pentateuch-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/10553/pg10553.txt',
    'data/texts/taoism/tao-teh-king-legge-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/216/pg216.txt',
    'data/texts/taoism/dao-de-jing-chinese-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/7337/pg7337.txt',
    'data/texts/confucianism/analects-legge-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/4094/pg4094.txt',
    'data/texts/buddhism/dhammapada-muller-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/2017/pg2017.txt',
    'data/texts/hinduism/upanishads-paramananda-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/3283/pg3283.txt',
    'data/texts/taoism/zhuangzi-giles-gutenberg.txt': 'https://www.gutenberg.org/cache/epub/59709/pg59709.txt',
}

for relative, url in TARGETS.items():
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=90) as response:
        data = response.read().decode('utf-8')
    if len(data.strip()) < 1000:
        raise RuntimeError(f'{relative} downloaded suspiciously small: {len(data)} characters')
    path.write_text(data, encoding='utf-8')
    print(f'imported {relative}: {len(data):,} characters')
