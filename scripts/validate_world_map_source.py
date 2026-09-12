#!/usr/bin/env python3
"""Run the established renderer, UI-shell, and browse-performance contracts."""
from __future__ import annotations

from pathlib import Path

import validate_world_map_3d as validator
import validate_world_map_ui_shell as ui_shell
import validate_world_map_browse_performance as browse_performance

validator.HTML = Path(__file__).resolve().parents[1] / "world-map" / "index.html"

if __name__ == "__main__":
    status = validator.main()
    if status:
        raise SystemExit(status)
    status = ui_shell.main()
    if status:
        raise SystemExit(status)
    raise SystemExit(browse_performance.main())