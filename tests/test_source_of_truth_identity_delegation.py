from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from audit_source_of_truth import effective_owner_families


def test_cross_family_identity_delegation_leaves_one_effective_owner():
    families = {
        "religion": {
            "identity_delegations": {"shared-node": "extremism_movements"},
        },
        "extremism_movements": {},
    }

    effective, applied = effective_owner_families(
        "shared-node",
        {"religion", "extremism_movements"},
        families,
    )

    assert effective == {"extremism_movements"}
    assert applied == {"religion": "extremism_movements"}


def test_invalid_delegation_does_not_hide_real_owner_collision():
    families = {
        "religion": {
            "identity_delegations": {"shared-node": "missing-family"},
        },
        "extremism_movements": {},
    }

    effective, applied = effective_owner_families(
        "shared-node",
        {"religion", "extremism_movements"},
        families,
    )

    assert effective == {"religion", "extremism_movements"}
    assert applied == {}
