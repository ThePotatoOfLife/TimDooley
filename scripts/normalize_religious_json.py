from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / 'data/religious-foundations/enriched-records.json',
    ROOT / 'data/religious-foundations/minor-traditions.json',
]

for path in TARGETS:
    raw = path.read_text(encoding='utf-8')
    # These legacy files contain literal escaped newlines between JSON tokens.
    # Convert only those formatting escapes; escaped newlines inside JSON strings
    # are not present in these records and must remain untouched.
    fixed = raw.replace('\\\\n', '\n')
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
        print(f'normalized {path.relative_to(ROOT)}')
    else:
        print(f'no normalization needed: {path.relative_to(ROOT)}')
