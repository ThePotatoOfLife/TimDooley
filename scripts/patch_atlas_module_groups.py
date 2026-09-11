#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'world-map' / '3d-app.js'
text = APP.read_text(encoding='utf-8')

if 'const MODULE_GROUPS = [' not in text:
    marker = "  {id:'tim',label:'Tim / Project Canon',keys:[],plane:'project-canon'}\n];\n\nfunction mode()"
    replacement = "  {id:'tim',label:'Tim / Project Canon',keys:[],plane:'project-canon'}\n];\n\n// The on-map country orbit is intentionally capped to stable knowledge groups.\n// Individual modules remain available in Details; future modules join a group\n// instead of adding another permanent dot around the selected country.\nconst MODULE_GROUPS = [\n  {id:'society',label:'Society',members:['religion','migration']},\n  {id:'state',label:'State',members:['government','security']},\n  {id:'economy',label:'Economy',members:['economy','debt','trade','ownership']},\n  {id:'systems',label:'Systems',members:['energy','infrastructure','science']},\n  {id:'context',label:'Context',members:['history','relations']},\n  {id:'project',label:'Project',members:['north','tim']}\n];\n\nfunction groupedModules(record,code){\n  const available=HUBS.map(h=>({...h,data:getModule(h,record,code)})).filter(h=>h.data);\n  const byId=new Map(available.map(module=>[module.id,module]));\n  const assigned=new Set();\n  const groups=MODULE_GROUPS.map(group=>{\n    const modules=group.members.map(id=>byId.get(id)).filter(Boolean);\n    modules.forEach(module=>assigned.add(module.id));\n    return {...group,modules};\n  }).filter(group=>group.modules.length);\n  const extras=available.filter(module=>!assigned.has(module.id));\n  if(extras.length)groups.push({id:'more',label:'More',members:extras.map(module=>module.id),modules:extras});\n  return groups;\n}\n\nfunction mode()"
    if marker not in text:
        raise SystemExit('MODULE_GROUPS insertion marker missing')
    text = text.replace(marker, replacement, 1)

pattern = r"function hubData\(code, record\) \{.*?\n\}\nfunction compareData\(\)"
replacement = '''function hubData(code, record) {
  const r = by3[code];
  if (!r?.latlng) return {points:emptyFC(),lines:emptyFC()};
  const lat=r.latlng[0], lon=r.latlng[1], baseRadius=Math.max(.7,Math.min(4.5,Math.sqrt(Math.max(r.area||1,1))/430));
  const groups=groupedModules(record,code);
  const pts=[],lines=[];
  groups.forEach((group,i)=>{
    const a=i*GOLDEN_ANGLE;
    const radialScale=.72+.13*Math.sqrt(i+1);
    const radius=baseRadius*radialScale;
    const dx=Math.cos(a)*radius, dy=Math.sin(a)*radius*.65;
    const coord=[lon+dx,Math.max(-82,Math.min(82,lat+dy))];
    const label=`${group.label} · ${group.modules.length}`;
    pts.push({type:'Feature',properties:{id:group.id,label,plane:'group',code,count:group.modules.length},geometry:{type:'Point',coordinates:coord}});
    lines.push({type:'Feature',properties:{id:group.id,code},geometry:{type:'LineString',coordinates:[[lon,lat],coord]}});
  });
  return {points:{type:'FeatureCollection',features:pts},lines:{type:'FeatureCollection',features:lines}};
}
function compareData()'''
out, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1 and 'const groups=groupedModules(record,code);' not in text:
    raise SystemExit('hubData grouping patch failed')
text = out if count == 1 else text

old_click = "map.on('click','semantic-hubs',e=>{claimOverlayClick(e);const f=e.features?.[0];if(f)window.openModule(f.properties.id)});"
new_click = "map.on('click','semantic-hubs',e=>{claimOverlayClick(e);const f=e.features?.[0];if(f)window.openModuleGroup(f.properties.id)});"
if old_click in text:
    text = text.replace(old_click, new_click, 1)
elif new_click not in text:
    raise SystemExit('semantic-hub click patch marker missing')

if 'window.openModuleGroup=' not in text:
    marker = "window.openModule=id=>{const h=HUBS.find(x=>x.id===id);"
    group_handler = "window.openModuleGroup=id=>{if(!selected)return;const group=groupedModules(currentCanonical,selected).find(item=>item.id===id);if(!group)return;$('#panel').innerHTML=`<div class=\"eyebrow\">Country knowledge · ${esc(selected)}</div><h1>${esc(group.label)}</h1><div class=\"actions\"><button onclick=\"showOverview()\">Back to country</button></div><div class=\"card\">${group.modules.map(module=>`<div class=\"row\"><button onclick=\"openModule('${module.id}')\">${esc(module.label)}</button> <span class=\"pill\">${esc(module.plane)}</span></div>`).join('')}</div><div class=\"boundary\">The on-map orbit is grouped navigation only. Detailed modules remain in the inspector so the map does not grow a new node for every future dataset.</div>`};\nwindow.openModule=id=>{const h=HUBS.find(x=>x.id===id);"
    if marker not in text:
        raise SystemExit('openModule insertion marker missing')
    text = text.replace(marker, group_handler, 1)

APP.write_text(text, encoding='utf-8')
print('Grouped country knowledge orbit applied.')
