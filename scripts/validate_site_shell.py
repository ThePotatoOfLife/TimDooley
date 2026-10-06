#!/usr/bin/env python3
"""Pure validation entrypoint for the built site-shell contract."""
from __future__ import annotations

import site_shell_contract as contract
from site_shell_contract import *  # re-export contract helpers for regression tests

# Build/finalization owns artifact normalization. Validation must not mutate it.
contract.restore_canonical_world_route = lambda: None


if __name__ == "__main__":
    raise SystemExit(contract.main())
