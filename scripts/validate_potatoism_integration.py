"""Validate the declarative Potatoism integration contract."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / 'data/potatoism-integration.json').read_text(encoding='utf-8'))
errors = []
for rel in contract['sources']:
    path = ROOT / rel
    if not path.exists():
        errors.append(f'missing source: {rel}')
    else:
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'invalid JSON: {rel}: {exc}')
if contract.get('navigation', {}).get('root') != 'potatoism':
    errors.append('navigation root must be potatoism')
if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f"Potatoism integration valid: {len(contract['sources'])} source files registered")
