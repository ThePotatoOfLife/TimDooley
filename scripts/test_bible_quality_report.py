#!/usr/bin/env python3
from __future__ import annotations

from build_bible_comparator_quality import research_reasons


def main() -> int:
    assert research_reasons({'strength':2}, ['why_it_matters']) == ['low-strength','interpretation-gap']
    assert research_reasons({}, ['project_side','source_direction']) == ['project-evidence-gap','unscored-provisional']
    assert research_reasons({'dossier_level':'A'}, ['biblical_sequence']) == ['biblical-context-gap']
    assert research_reasons({'dossier_level':'B'}, ['counterpressure','supported_conclusion']) == ['boundary-gap','unscored-provisional']
    assert research_reasons({'strength':4}, ['why_it_matters']) == ['interpretation-gap']
    print('BIBLE QUALITY REASON TESTS PASSED (5 cases)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
