#!/usr/bin/env python3
"""Run the established renderer contract and ordinary UI-shell contract."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator
import validate_world_map_ui_shell as ui_shell

validator.HTML = Path(__file__).resolve().parents[1] / "world-map" / "index.html"

if __name__ == "__main__":
    status = validator.main()
    if status:
        raise SystemExit(status)
    raise SystemExit(ui_shell.main())
