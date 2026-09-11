#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if new in text:
        return False
    if old not in text:
        raise SystemExit(f'Expected marker missing in {path}: {old[:100]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')
    return True

# Keep the selection dock useful but quiet: two primary actions stay visible;
# lower-frequency Compare/Focus actions live behind a compact More menu.
replace_once('world-map/3d-selection-ui.js',
"""  #atlasSelectionDock .selection-clear{font-size:16px;line-height:1;padding:4px 7px;color:#aeb9b2}
  .atlas-layer-registry""",
"""  #atlasSelectionDock .selection-clear{font-size:16px;line-height:1;padding:4px 7px;color:#aeb9b2}
  #atlasSelectionDock .selection-more{position:relative}
  #atlasSelectionDock .selection-more>summary{list-style:none;cursor:pointer;padding:5px 8px;border:1px solid var(--line);border-radius:999px;background:#14201f;color:var(--muted);line-height:1.1}
  #atlasSelectionDock .selection-more>summary::-webkit-details-marker{display:none}
  #atlasSelectionDock .selection-more-pop{position:absolute;left:50%;bottom:calc(100% + 7px);transform:translateX(-50%);min-width:120px;padding:5px;border:1px solid var(--line);border-radius:9px;background:#0d1514;box-shadow:0 8px 22px #0008}
  #atlasSelectionDock .selection-more-pop button{display:block;width:100%;margin:2px 0;text-align:left}
  .atlas-layer-registry""")

replace_once('world-map/3d-selection-ui.js',
"""  <button data-action="details" title="Open country details">Details</button>
  <button data-action="connections" title="Show or hide country connections">Connections</button>
  <button data-action="compare" title="Add this country to comparison">Compare</button>
  <button data-action="focus" title="Fit the selected country">Focus</button>
  <button class="selection-clear" data-action="clear" title="Deselect country" aria-label="Deselect country">×</button>""",
"""  <button data-action="details" title="Open country details">Details</button>
  <button data-action="connections" title="Show or hide country connections">Connections</button>
  <details class="selection-more">
    <summary title="More country actions" aria-label="More country actions">•••</summary>
    <div class="selection-more-pop">
      <button data-action="focus" title="Fit the selected country">Focus</button>
      <button data-action="compare" title="Add this country to comparison">Compare</button>
    </div>
  </details>
  <button class="selection-clear" data-action="clear" title="Deselect country" aria-label="Deselect country">×</button>""")

replace_once('world-map/3d-selection-ui.js',
"""  } else if (action === 'clear') {
    window.clearCountrySelection?.();
  }
  queueMicrotask(syncDock);""",
"""  } else if (action === 'clear') {
    window.clearCountrySelection?.();
  }
  const more = button.closest('.selection-more');
  if (more) more.open = false;
  queueMicrotask(syncDock);""")

# Give future layers a stable metadata contract without exposing extra controls.
replace_once('world-map/3d-selection-ui.js',
"function registerLayer({ id, label, group = 'Overlays', getVisible, setVisible, element }) {",
"function registerLayer({ id, label, group = 'Overlays', kind = 'overlay', scope = 'global', minZoom = 0, maxZoom = 24, description = '', getVisible, setVisible, element }) {")
replace_once('world-map/3d-selection-ui.js',
"  const record = { id, label: label || id, group, getVisible, setVisible, element: control };",
"  const record = { id, label: label || id, group, kind, scope, minZoom, maxZoom, description, getVisible, setVisible, element: control };")

# Capital source contains a few alternate/admin seats. Keep those records for
# future use but show primary national capitals by default.
replace_once('world-map/3d-hover.js',
"""      id: 'capital-cities', type: 'circle', source: 'capital-cities', minzoom: 0,
      paint: {""",
"""      id: 'capital-cities', type: 'circle', source: 'capital-cities', minzoom: 0,
      filter: ['==', ['get', 'primary'], true],
      paint: {""")
replace_once('world-map/3d-hover.js',
"""      filter: ['<=', ['get', 'scalerank'], 2],""",
"""      filter: ['all', ['==', ['get', 'primary'], true], ['<=', ['get', 'scalerank'], 3]],""")
replace_once('world-map/3d-hover.js',
"""      id: 'capital-city-labels', type: 'symbol', source: 'capital-cities', minzoom: 3.1,
      layout: {""",
"""      id: 'capital-city-labels', type: 'symbol', source: 'capital-cities', minzoom: 3.1,
      filter: ['==', ['get', 'primary'], true],
      layout: {""")

print('Final atlas interaction polish applied.')
