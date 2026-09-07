from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / 'data/religious-foundations/enriched-records.json',
    ROOT / 'data/religious-foundations/minor-traditions.json',
]

for path in TARGETS:
    raw = path.read_text(encoding='utf-8')
    # These legacy files contain literal backslash+n separators between JSON
    # tokens. Convert those separators to real newlines so the documents become
    # ordinary JSON again. These records do not use escaped newlines inside
    # string values.
    fixed = raw.replace('\\n', '\n')
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
        print(f'normalized {path.relative_to(ROOT)}')
    else:
        print(f'no normalization needed: {path.relative_to(ROOT)}')
