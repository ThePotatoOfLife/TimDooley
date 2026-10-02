#!/usr/bin/env node
import assert from 'node:assert/strict';

let elevator;
try{
  elevator=await import('../app/site-elevator.js');
}catch(error){
  console.error('Expected RED: app/site-elevator.js does not exist yet');
  throw error;
}

const projection=(await import('../data/house/elevator-spatial-projection.json',{with:{type:'json'}})).default;
const roomContract=(await import('../data/house/rooms.json',{with:{type:'json'}})).default;
const subroomContract=(await import('../data/house/subrooms.json',{with:{type:'json'}})).default;

const cases=[
  ['/', 'plane', null],
  ['/tim-dooley/', 'plane', null],
  ['/potato-of-life/', 'heaven', 'potatoverse-canon'],
  ['/religion/', 'heaven', 'traditions-texts'],
  ['/science/', 'plane', 'science-formal-models'],
  ['/politics/', 'plane', 'world-systems'],
  ['/context/culture/', 'plane', 'culture-information'],
  ['/shadow-farm/', 'below', null],
  ['/context/source-authority/', 'below', 'archive-sources'],
  ['/research-lab/', 'below', 'research-lab'],
  ['/works/', 'heaven', 'works'],
  ['/timeline/', 'plane', 'time-history'],
  ['/below/', 'below', null],
  ['/philosophy/', 'heaven', 'potatoverse-canon'],
  ['/philosophy/interpretive-justice.html', 'heaven', 'potatoverse-canon'],
  ['/world/', 'plane', 'world-systems'],
  ['/news/', 'plane', 'world-systems'],
  ['/world-map/', 'plane', 'world-systems'],
  ['/world-systems/', 'plane', 'world-systems'],
  ['/context/', 'below', 'archive-sources'],
  ['/corporium/', 'plane', null],
  ['/axis/', 'heaven', 'potatoverse-canon'],
  ['/north/', 'heaven', null],
  ['/traditions/bible/', 'heaven', 'traditions-texts'],
  ['/history/', 'plane', 'time-history'],
  ['/law/', 'plane', 'world-systems'],
  ['/life-body/', 'plane', 'life-body'],
  ['/explore/', 'plane', null],
  ['/questions/', 'plane', null],
  ['/index-a-z/', 'plane', null],
  ['/house/', 'plane', null],
  ['/rooms/', 'plane', null],
  ['/rooms/objects/', 'plane', null],
  ['/paths/', 'plane', null],
  ['/elevator/', 'plane', null],
];

for(const [route,levelId,roomId] of cases){
  const ctx=elevator.resolveSpatialContext(route,projection,roomContract);
  assert.equal(ctx.levelId,levelId,route+' level');
  assert.equal(ctx.roomId,roomId,route+' room');
}

const direct=elevator.resolveSpatialContext('/rooms/culture-information/deeper/topic/',projection,roomContract);
assert.equal(direct.levelId,'plane');
assert.equal(direct.roomId,'culture-information');
assert.equal(direct.source,'room-route');

// all direct Room routes must resolve to each Room's primary floor
for(const dwelling of projection.dwellings){
  const ctx=elevator.resolveSpatialContext('/rooms/'+dwelling.id+'/',projection,roomContract);
  assert.equal(ctx.roomId,dwelling.id, dwelling.id+' direct Room route');
  assert.equal(ctx.levelId,dwelling.primary_level, dwelling.id+' must open on its primary floor');
  assert.equal(ctx.source,'room-route', dwelling.id+' must resolve through direct Room ownership');
}

// nested Room inheritance contract
const primaryByRoom=Object.fromEntries(projection.dwellings.map(row=>[row.id,row.primary_level]));
for(const subroom of subroomContract.subrooms.filter(row=>row.status==='active')){
  const ctx=elevator.resolveSpatialContext('/rooms/inside/'+subroom.id+'/',projection,roomContract,subroomContract);
  assert.equal(ctx.roomId,subroom.parent_room_id, subroom.id+' must light its parent Room');
  assert.equal(ctx.levelId,primaryByRoom[subroom.parent_room_id], subroom.id+' must inherit the parent Room primary floor');
  assert.equal(ctx.source,'subroom-route', subroom.id+' must resolve through nested Room ownership');
  assert.equal(ctx.subroomId,subroom.id, subroom.id+' must preserve nested Room identity');
}

const chronologyAlias=elevator.resolveSpatialContext('/rooms/inside/timeline-events/',projection,roomContract,subroomContract);
assert.equal(chronologyAlias.roomId,'time-history','timeline-events route alias must light Time & History');
assert.equal(chronologyAlias.levelId,'plane','timeline-events route alias must stand on Plane');
assert.equal(chronologyAlias.subroomId,'chronology-events','timeline-events route alias must preserve chronology-events identity');
assert.equal(chronologyAlias.source,'subroom-route','timeline-events route alias must resolve through nested Room ownership');

const taoismFile=elevator.resolveSpatialContext('/taoism.html',projection,roomContract,subroomContract);
assert.equal(taoismFile.levelId,'heaven','taoism.html must stand on Heaven');
assert.equal(taoismFile.roomId,'traditions-texts','taoism.html must light Traditions & Texts');

const unknown=elevator.resolveSpatialContext('/totally-unknown/',projection,roomContract,subroomContract);
assert.equal(unknown.levelId,'plane');
assert.equal(unknown.roomId,null);

const archiveRecord=elevator.resolveSpatialContext('/records/archive-epistemics/',projection,roomContract,subroomContract);
const archiveInherited=elevator.inheritParentContext(
  archiveRecord,
  '/context/source-authority/',
  projection,
  roomContract,
  subroomContract
);
assert.equal(archiveInherited.levelId,'below');
assert.equal(archiveInherited.roomId,'archive-sources');
assert.equal(archiveInherited.source,'parent-route');
assert.equal(archiveInherited.parentRoute,'/context/source-authority/');

const scienceKnown=elevator.resolveSpatialContext('/science/',projection,roomContract,subroomContract);
assert.equal(
  elevator.inheritParentContext(scienceKnown,'/religion/',projection,roomContract,subroomContract),
  scienceKnown,
  'known route context must not be overridden by a Parent link'
);

assert.equal(elevator.stepLevel('heaven','up'),'heaven');
assert.equal(elevator.stepLevel('heaven','down'),'plane');
assert.equal(elevator.stepLevel('plane','up'),'heaven');
assert.equal(elevator.stepLevel('plane','down'),'below');
assert.equal(elevator.stepLevel('below','down'),'below');

const lowerLandmarks=elevator.landmarksForLevel('below',projection);
assert.deepEqual(
  lowerLandmarks.map(row=>row.title),
  ['Below Basin','Farm / Sektur'],
  'Below must expose exactly the two non-Room field stations before governed Rooms'
);
const lowerRoomLabels=elevator.roomsForLevel('below',projection,roomContract).map(room=>room.title);
assert.deepEqual(
  lowerRoomLabels,
  ['Roots / Evidence','Forge / Repair'],
  'Below governed Rooms should use concise reader-facing labels'
);
const cultureBelow=elevator.roomsForLevel('below',projection,roomContract).map(room=>room.id);
assert.equal(cultureBelow.includes('culture-information'),false,'Below rail must not expose Plane-owned Culture as a door');
const culturePlane=elevator.roomsForLevel('plane',projection,roomContract).map(room=>room.id);
assert.ok(culturePlane.includes('culture-information'),'Culture must remain reachable from its Plane floor');
const cultureHeaven=elevator.roomsForLevel('heaven',projection,roomContract).map(room=>room.id);
assert.equal(cultureHeaven.includes('culture-information'),false);

// hard floor-boundary contract: the header rail is a floor-local door list, not a cross-floor projection browser
for(const levelId of elevator.LEVELS){
  const visible=elevator.roomsForLevel(levelId,projection,roomContract);
  assert.ok(visible.length>0,levelId+' must expose at least one floor-local Room');
  assert.ok(visible.every(room=>room.primaryLevel===levelId),levelId+' rail must contain only Rooms whose canonical entrance stays on '+levelId);
  assert.ok(visible.every(room=>room.isPrimaryProjection===true),levelId+' rail rows must all be primary floor entrances');
}

// every governed Room must be visible on exactly its resolved primary floor so a Room click never changes floors
for(const dwelling of projection.dwellings){
  const appearances=elevator.LEVELS.filter(levelId=>
    elevator.roomsForLevel(levelId,projection,roomContract).some(room=>room.id===dwelling.id)
  );
  assert.deepEqual(appearances,[dwelling.primary_level],dwelling.id+' must appear only on its primary floor rail');
}

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=fs.readFileSync(path.join(ROOT,'app/site-elevator.js'),'utf8');
const css=fs.readFileSync(path.join(ROOT,'app/site-elevator.css'),'utf8');

// VISUAL CONTRACT
for(const marker of [
  'site-elevator-controls',
  'site-elevator-up',
  'site-elevator-down',
  'site-elevator-reel',
  'site-elevator-room-rail',
  'site-elevator-landmark',
  'aria-live',
  'aria-current',
  'data-elevator-level',
  'is-primary',
  "if(event.target!==header)return",
]){
  assert.ok(source.includes(marker),'site elevator visual contract missing '+marker);
}
assert.equal(/history\.(?:pushState|replaceState)/.test(source),false,'floor switching must not mutate history');
assert.ok(source.includes('document.documentElement.dataset.siteFloor=selectedLevel'),'floor switching must synchronize the page atmosphere with the selected floor');
assert.equal(/location\.(?:assign|replace)|location\.href\s*=/.test(source),false,'floor switching must not navigate the page');
assert.ok(source.includes("ArrowUp"),'header keyboard contract needs ArrowUp');
assert.ok(source.includes("ArrowDown"),'header keyboard contract needs ArrowDown');
assert.ok(source.includes("Home"),'header keyboard contract needs Home → Plane');
assert.ok(source.includes("disabled"),'boundary arrows must expose disabled state');

assert.ok(css.includes('grid-template-columns:repeat(auto-fit,minmax('),'Room rail must pack into a responsive wrapped terminal grid');
assert.ok(css.includes('overflow:visible'),'Room rail must expose wrapped lines');
assert.equal(css.includes('overflow-x:auto'),false,'Room rail must not horizontally scroll');
assert.equal(css.includes('scrollbar-width'),false,'Room rail must not render a scrollbar');
assert.ok(css.includes('.site-elevator-arrow::before'),'arrow controls should use metallic line detailing without button blocks');
const backgroundImageValues=[...css.matchAll(/background-image\\s*:\\s*([^;]+);/g)].map(match=>match[1]);
const malformedBackgroundImages=backgroundImageValues.filter(value=>
  value.includes('repeat-x') || value.includes('repeat-y') || value.includes('no-repeat')
);
assert.deepEqual(malformedBackgroundImages,[],'background-image declarations must not contain background shorthand repeat syntax');
assert.ok(css.includes('.site-elevator-floor-code'),'terminal board needs a numbered floor code');
assert.ok(css.includes('[data-elevator-level="heaven"]::before'),'Heaven needs a distinct pixel-biome layer');
assert.ok(css.includes('html[data-site-floor="heaven"]{'),'resolved Heaven routes should own the root page canvas');
assert.ok(css.includes('html[data-site-floor="plane"]{'),'resolved Plane routes should own the root page canvas');
assert.ok(css.includes('linear-gradient(180deg,#1f4b63'),'Plane page atmosphere must visibly rise above the black foundation');
assert.ok(css.includes('linear-gradient(180deg,#0b1028'),'Heaven page atmosphere must visibly rise above the black foundation');
assert.ok(css.includes('background:transparent!important'),'governed page bodies must not paint opaque black over the floor canvas');
assert.ok(css.includes('--site-panel:rgba(14,16,38,.80)'),'Heaven must tint shared panels, not only the wallpaper');
assert.ok(css.includes('--site-panel:rgba(13,29,25,.80)'),'Plane must tint shared panels, not only the wallpaper');
assert.ok(css.includes('--site-panel:rgba(24,11,8,.84)'),'Below must tint shared panels, not only the wallpaper');
assert.ok(css.includes('html[data-site-floor="below"]{'),'resolved Below routes should own the root page canvas');
assert.ok(css.includes('radial-gradient(ellipse at 8% 108%,rgba(94,133,88,.34)'),'Heaven needs a soft garden horizon beneath the cosmos');
assert.ok(css.includes('radial-gradient(ellipse at 68% 24%,rgba(103,72,170,.40)'),'Heaven needs purple nebula depth');
assert.ok(css.includes('linear-gradient(88deg,transparent 0 47.9%,'),'Heaven needs a restrained luminous spiritual-tree trunk');
assert.match(css,/\.site-elevator\[data-elevator-level="heaven"\]::before\{[\s\S]*?radial-gradient\(circle/,'Heaven needs sparse celestial points');
assert.ok(css.includes('linear-gradient(180deg,#090d24'),'Heaven needs dark-blue/purple cosmic depth rather than a flat sky plate');
assert.ok(css.includes('[data-elevator-level="plane"]::before'),'Plane needs a distinct CSS landscape biome layer');
assert.match(css,/\.site-elevator\[data-elevator-level="plane"\]::before\{[\s\S]*?background:/,'Plane header scenery must use the background shorthand when positioning repeated mountain layers');
assert.match(css,/\.site-elevator\[data-elevator-level="plane"\]::before\{[\s\S]*?repeat-x/,'Plane needs distant CSS mountain ridges');
assert.ok(css.includes('linear-gradient(180deg,#244f66'),'Plane needs blue air transitioning into green land');
assert.ok(css.includes('[data-elevator-level="below"]::before'),'Below needs a distinct CSS root-and-soil biome layer');
assert.match(css,/\.site-elevator\[data-elevator-level="below"\]::before\{[\s\S]*?radial-gradient\(ellipse/,'Below needs an irregular compacted-soil ceiling');
assert.match(css,/\.site-elevator\[data-elevator-level="below"\]::before\{[\s\S]*?no-repeat/,'Below needs thick hanging roots');
assert.ok(css.includes('border-radius:0'),'terminal Room tiles should not drift back into pill styling');
assert.ok(css.includes('background:var(--site-elevator-accent)'),'active Room tile needs a compact location beacon');
assert.equal(css.includes('.site-elevator-room.is-secondary'),false,'header CSS must not preserve cross-floor Room affordances');
assert.equal(source.includes('is-secondary'),false,'runtime must not emit cross-floor Room doors');
assert.ok(css.includes('[data-elevator-level="plane"] .site-elevator-room'),'Plane Room tiles need block-earth material styling');
assert.ok(css.includes('[data-elevator-level="heaven"] .site-elevator-room'),'Heaven Room tiles need sky material styling');
assert.ok(css.includes('rgba(18,49,75,.66)'),'Heaven Room panes must remain readable while revealing more sky');
assert.ok(!css.includes('backdrop-filter:blur(6px) saturate(116%)'),'Heaven should blur shared panes rather than every Room tile');
assert.ok(css.includes('@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px)))'),'Heaven glass needs an opaque fallback when blur is unavailable');
assert.ok(css.includes('@media (prefers-contrast: more)'),'Heaven glass needs an explicit high-contrast mode');
assert.ok(css.includes('[data-elevator-level="heaven"] .site-elevator-room.is-active'),'Heaven current Room needs a dedicated glass-active state');
assert.ok(css.includes('rgba(15,38,60,.72)'),'Heaven floor board needs readable translucent glass');
assert.ok(css.includes('backdrop-filter:blur(9px) saturate(122%)'),'Heaven floor board needs a restrained frosted-glass treatment');
assert.ok(css.includes('rgba(11,33,52,.64)'),'Heaven Room rail needs translucent glass over the sky');
assert.ok(css.includes('backdrop-filter:blur(8px) saturate(118%)'),'Heaven rail needs restrained glass refraction');
assert.ok(css.includes('background:linear-gradient(180deg,rgba(72,120,132,.28),rgba(24,55,47,.90))'),'Plane floor board needs a blue-green landscape readability plate');
assert.ok(css.includes('background:rgba(24,14,11,.96)'),'Below floor board needs a dark readability plate');
assert.ok(css.includes('background:rgba(5,8,8,.72)'),'arrow column needs a stable dark readability plate');
assert.ok(css.includes('[data-elevator-ready="false"]'),'loading state must have a neutral terminal treatment');
assert.ok(css.includes('--elevator-room-min:49px'),'narrow mobile Plane grid must fit enough columns to avoid four Room rows');
assert.ok(css.includes('--elevator-floor-size:12px'),'floor label must remain immediately readable');
assert.ok(css.includes('text-shadow:0 1px 0 rgba(0,0,0,.95)'),'floor text needs dark contrast shadow');
assert.ok(css.includes('[data-elevator-level="below"] .site-elevator-room'),'Below Room tiles need underground material styling');
assert.ok(css.includes('background:transparent'),'arrow controls must float without metallic button blocks');
assert.ok(css.includes('display:block!important'),'elevator shell must survive page-level header display overrides');
assert.ok((css.match(/!important/g)||[]).length<=8,'elevator CSS should keep specificity escalation tightly bounded');
assert.ok(css.includes('.site-elevator-room-rail{\n  margin:0;'),'Room rail must reset page-level nav spacing without specificity escalation');
assert.ok(css.includes('margin:0;'),'elevator shell must reset page-level header/nav margins');
assert.ok(css.includes('align-self:start'),'elevator controls must stay pinned when Room grid wraps');
assert.ok(css.includes('--elevator-row-height:42px'),'desktop elevator controls need a fixed one-row height token');
assert.ok(!/--([\\w-]+):var\\(--\\1\\)/.test(css),'elevator CSS custom properties must not self-reference');

for(const match of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)){
  const selector=match[1].trim();
  if(selector.startsWith('@')||/^\d+%$/.test(selector))continue;
  const props=[...match[2].matchAll(/([\w-]+)\s*:/g)].map(row=>row[1]);
  const duplicates=props.filter((prop,index)=>props.indexOf(prop)!==index);
  assert.equal(duplicates.length,0,selector+' must not repeat CSS properties: '+[...new Set(duplicates)].join(', '));
}
assert.ok(css.includes('.site-elevator-reel{\n  align-self:start;'),'floor board must stay pinned when Room grid wraps');
assert.ok(css.includes('--elevator-room-row-min:26px'),'wrapped Room rows must stay compact and predictable');
assert.ok(css.includes('.site-elevator-up::before{content:"△"}'),'up arrow needs triangle framing');
assert.ok(css.includes('.site-elevator-down::before{content:"▽"}'),'down arrow needs inverted triangle framing');
assert.ok(css.includes('--elevator-arrow-size:21px'),'triangle framing should retain its desktop size token');
assert.ok(!css.includes('pointer-events:none;\n  z-index:-1;\n}\n.site-elevator-up::before'),'triangle framing must not disappear behind the control column');
assert.ok(css.includes('text-wrap:balance'),'Room labels should wrap into balanced readable lines');
assert.ok(source.includes('site-elevator-floor-code'),'runtime must render terminal floor code');
assert.ok(source.includes('header.dataset.elevatorRoom=spatial.roomId'),'runtime must publish the current Room on the header');
assert.ok(source.includes("selectedLevel===spatial.levelId"),'active Room highlight must only appear on the actual floor');
assert.equal(source.includes('ROOM PROJECTION · ENTER VIA'),false,'single-floor Room ownership must not advertise legacy cross-floor projections');
assert.ok(source.includes("'BROWSING FLOOR'"),'non-actual floor must be clearly marked as browsing');
assert.ok(source.includes("data-elevator-level','pending"),'pre-hydration header must not falsely present Plane');
assert.ok(source.includes('Finding your Room…'),'pre-hydration header needs a neutral orientation label');
assert.equal(source.includes("sessionStorage.getItem(key)"),false,'elevator governance data must not be pinned to stale session data');
assert.ok(source.includes("cache:'no-store'"),'governance fetch should always read the currently deployed floor data');
assert.ok(source.includes('House topology changes independently of this JavaScript asset'),'runtime should document why governance data bypasses the old asset-version session cache');
assert.ok(source.includes("requestAnimationFrame(publishClearance)"),'every render must republish top clearance after Room wrapping');
assert.ok(source.includes("setAttribute('aria-busy','true')"),'loading header should expose busy state');
assert.ok(source.includes('const runtimeScript='),'elevator must capture its script URL before deferred context can disappear');
assert.ok(source.includes("'aria-keyshortcuts','ArrowUp ArrowDown Home'"),'header keyboard navigation should be discoverable to assistive tech');
assert.ok(source.includes('role="group" aria-label="Change House floor"'),'floor controls need an announced control group');
assert.ok(source.includes("'Move to '+levelLabel(upTarget"),'up control should announce its destination floor');
assert.ok(source.includes("'Move to '+levelLabel(downTarget"),'down control should announce its destination floor');
assert.ok(source.includes("'ORIENTATION OFFLINE'"),'failed governance hydration needs a visible fallback state');
assert.ok(source.includes('const FLOOR_LOCAL_LINK_SELECTOR='),'runtime must own one floor-local link selector for page and secondary navigation');
assert.ok(source.includes('const enforceFloorLocalNavigation='),'runtime must enforce floor boundaries through one shared pass');
assert.ok(source.includes("'main > nav.page-nav a[href]'"),'page navigation must participate in floor-boundary enforcement');
assert.ok(source.includes("'main > header nav a[href]'"),'header-local navigation must participate in floor-boundary enforcement');
assert.ok(source.includes("'.door-grid a[href]'"),'secondary Room doors must participate in the shared floor-boundary selector');
assert.ok(source.includes("'.side-routes a[href]'"),'secondary side routes must participate in the shared floor-boundary selector');
assert.ok(source.includes('enforceFloorLocalLinks(FLOOR_LOCAL_LINK_SELECTOR)'),'all local navigation must use the same floor filter');
assert.ok(source.includes('enforceFloorLocalNavigation();'),'shared floor filtering must run after spatial hydration');
assert.ok(source.includes("link.hidden=true"),'cross-floor page/header links must be hidden rather than offered as ordinary doors');
assert.ok(source.includes("link.dataset.elevatorFloorHidden='true'"),'runtime must only unhide links that it hid for floor enforcement');
assert.ok(source.includes('const crossFloor=target.levelId!==spatial.levelId'),'floor enforcement must compare every local door against the page floor');

assert.ok(css.includes('background-color:#244f66'),'Plane needs a non-black fallback canvas even if layered gradients fail');
assert.ok(css.includes('body:not(.lower-layer-page)::before'),'tree atmosphere must mount inside the transparent body stacking context');
assert.ok(css.includes('isolation:isolate'),'ordinary floor pages must isolate the atmosphere behind their content');
assert.ok(css.includes('site-tree-perspective.svg'),'shared floor canvas must include the tall perspective tree asset');
assert.ok(css.includes('@keyframes site-tree-descent'),'tree atmosphere needs a crown-to-roots scroll sequence');
assert.ok(css.includes('animation-timeline:scroll(root block)'),'tree descent must follow root-page scroll rather than an independent timer');
assert.ok(css.includes('visual travel is'),'tree CSS should document the slower-than-page parallax contract');
assert.ok(css.includes('background-position:50% 62%'),'tree parallax must travel only part of the asset while the page scrolls farther');
assert.ok(css.includes('scale(1.16)'),'tree should grow subtly without moving one-to-one with the page');
assert.ok(css.includes('site-ground-approach'),'floor colour needs a restrained terrestrial shift during descent');
assert.ok(css.includes('body:not(.lower-layer-page)'),'lower-floor cut-earth pages must keep their dedicated root environment');
assert.ok(css.includes('prefers-reduced-motion:reduce'),'scroll-depth atmosphere must respect reduced-motion preferences');

console.log('Site elevator resolver + visual contract passed.');
