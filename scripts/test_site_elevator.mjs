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
const lowerCss=fs.readFileSync(path.join(ROOT,'app/lower-layer.css'),'utf8');
const journeyCss=fs.readFileSync(path.join(ROOT,'app/house-journey.css'),'utf8');

// VISUAL CONTRACT
for(const marker of [
  'site-elevator-controls',
  'site-elevator-up',
  'site-elevator-down',
  'site-elevator-reel',
  'site-elevator-stage',
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
assert.ok(source.includes('document.documentElement.dataset.siteFloor=spatial.levelId'),'page atmosphere must remain locked to the canonical spatial floor');
assert.equal(source.includes('document.documentElement.dataset.siteFloor=selectedLevel'),false,'elevator browsing must not repaint the page floor');
assert.equal(/location\.(?:assign|replace)|location\.href\s*=/.test(source),false,'floor switching must not navigate the page');
assert.ok(source.includes("ArrowUp"),'header keyboard contract needs ArrowUp');
assert.ok(source.includes("ArrowDown"),'header keyboard contract needs ArrowDown');
assert.ok(source.includes("Home"),'header keyboard contract needs Home → Plane');
assert.ok(source.includes("disabled"),'boundary arrows must expose disabled state');

assert.ok(css.includes('--elevator-slot-count:5'),'desktop header must preserve one five-slot Room geometry across all floors');
assert.ok(css.includes('flex:0 0 calc((100% - (var(--elevator-room-gap) * (var(--elevator-slot-count) - 1))) / var(--elevator-slot-count))'),'desktop Room buttons must keep identical widths across Heaven, Plane and Below');
assert.ok(css.includes('grid-template-columns:repeat(auto-fit,minmax(72px,1fr))'),'narrow Room rail must retain a responsive wrapped fallback');
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
assert.ok(css.includes('[data-elevator-level="heaven"] .site-elevator-stage::before'),'Heaven needs a distinct scenic-window layer');
assert.ok(css.includes('html[data-site-floor="heaven"]{'),'resolved Heaven routes should own the root page canvas');
assert.ok(css.includes('html[data-site-floor="plane"]{'),'resolved Plane routes should own the root page canvas');
assert.match(css,/body:not\(\.home-body\)\{[\s\S]*?background:transparent;/,'governed page bodies must remain transparent above the realm canvas');
assert.ok(css.includes('html[data-site-floor="below"]{'),'resolved Below routes should own the root page canvas');
for(const [floor,asset] of [['heaven','home-heaven.avif'],['plane','home-plane.avif'],['below','home-below.avif']]){
  assert.ok(css.includes('url("./'+asset+'")'),'shared floor renderer must reference '+asset);
  const headerStart=css.indexOf('.site-elevator[data-elevator-level="'+floor+'"] .site-elevator-stage::before{');
  assert.ok(headerStart>=0,'elevator header scenic window must define '+floor+' scene');
  assert.ok(css.slice(headerStart,headerStart+260).includes(asset),'elevator header scenic window must use '+asset);
}

assert.ok(css.includes('#090909'),'elevator scenes need one neutral fallback behind the final realm art');
assert.ok(css.includes('linear-gradient(180deg,rgba(3,6,8,.22),transparent 26%,transparent 70%,rgba(2,4,5,.46))'),'scenic window needs a neutral vertical readability shade instead of synthetic realm recoloring');
assert.ok(css.includes('--site-realm-fallback:#090909'),'all realms should share one neutral fallback base behind the final art');
assert.ok(css.includes('[data-elevator-level="plane"] .site-elevator-stage::before'),'Plane needs a distinct scenic-window layer');
assert.equal(/\.site-elevator\[data-elevator-level="plane"\] \.site-elevator-stage::before\{[\s\S]*?repeat-x/.test(css),false,'Plane elevator header should not rebuild mountains with repeated gradient strips');
assert.ok(css.includes('[data-elevator-level="below"] .site-elevator-stage::before'),'Below needs a distinct scenic-window layer');
assert.ok(css.includes('border-radius:0'),'terminal Room tiles should not drift back into pill styling');
assert.ok(css.includes('background:var(--site-elevator-accent)'),'active Room tile needs a compact location beacon');
for(const floor of ['heaven','plane','below']){
  assert.ok(css.includes('.site-elevator[data-elevator-level="'+floor+'"]{'),'elevator must expose a '+floor+' accent token');
  assert.equal(css.includes('.site-elevator[data-elevator-level="'+floor+'"] .site-elevator-room{'),false,'Room tiles must use one neutral material skin across floors');
}
assert.equal(css.includes('backdrop-filter:blur(8px)'),false,'elevator must not spend GPU work on floor-specific blur skins');
assert.equal(css.includes('backdrop-filter:blur(9px)'),false,'elevator reel must not use a separate Heaven blur skin');
assert.equal(css.includes('.site-elevator-room.is-secondary'),false,'header CSS must not preserve cross-floor Room affordances');
assert.equal(source.includes('is-secondary'),false,'runtime must not emit cross-floor Room doors');


assert.ok(css.includes('background:rgba(6,9,11,.74)'),'Room tiles need one neutral readability surface over every realm');
assert.ok(css.includes('background:var(--site-elevator-panel)'),'floor board must use the shared terminal panel token');
assert.ok(css.includes('@media (prefers-contrast: more)'),'terminal UI needs one generic high-contrast mode');
assert.equal(css.includes('backdrop-filter:'),false,'terminal UI must not reintroduce blur-based floor materials');
assert.ok(css.includes('background:#090d11'),'arrow column needs a stable dark readability plate');
assert.ok(css.includes('[data-elevator-ready="false"]'),'loading state must have a neutral terminal treatment');
assert.ok(css.includes('--elevator-room-height:40px'),'desktop Room buttons must share one fixed height across all floors');
assert.ok(css.includes('--elevator-floor-size:14px'),'floor label must remain immediately readable');
assert.ok(css.includes('text-shadow:0 1px 0 rgba(0,0,0,.95)'),'floor text needs dark contrast shadow');

assert.ok(css.includes('background:transparent'),'arrow controls must float without metallic button blocks');
assert.match(css,/\.site-elevator\{[\s\S]*?display:block;/,'elevator shell must define its own display mode without specificity escalation');
assert.ok((css.match(/!important/g)||[]).length<=8,'elevator CSS should keep specificity escalation tightly bounded');
assert.ok(css.includes('.site-elevator-room-rail{\n  margin:0;'),'Room rail must reset page-level nav spacing without specificity escalation');
assert.ok(css.includes('margin:0;'),'elevator shell must reset page-level header/nav margins');
assert.ok(css.includes('--elevator-shell-height:60px'),'desktop elevator console and scenic window must share one shell height');
assert.ok(css.includes('grid-template-rows:1fr 1fr'),'up/down controls must split the same console height evenly');
assert.ok(!/--([\\w-]+):var\\(--\\1\\)/.test(css),'elevator CSS custom properties must not self-reference');

for(const match of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)){
  const selector=match[1].trim();
  if(selector.startsWith('@')||/^\d+%$/.test(selector))continue;
  const props=[...match[2].matchAll(/([\w-]+)\s*:/g)].map(row=>row[1]);
  const duplicates=props.filter((prop,index)=>props.indexOf(prop)!==index);
  assert.equal(duplicates.length,0,selector+' must not repeat CSS properties: '+[...new Set(duplicates)].join(', '));
}
assert.ok(css.includes('.site-elevator-stage{\n  position:relative;'),'scenic Room stage must remain a distinct visual owner');
assert.ok(css.includes('min-height:var(--elevator-shell-height)'),'console, stage and Room rail must inherit one height token');
assert.ok(css.includes('.site-elevator-up::before{content:"△"}'),'up arrow needs triangle framing');
assert.ok(css.includes('.site-elevator-down::before{content:"▽"}'),'down arrow needs inverted triangle framing');
assert.ok(css.includes('--elevator-arrow-size:20px'),'triangle framing should retain its desktop size token');
assert.ok(!css.includes('pointer-events:none;\n  z-index:-1;\n}\n.site-elevator-up::before'),'triangle framing must not disappear behind the control column');
assert.ok(css.includes('text-wrap:balance'),'Room labels should wrap into balanced readable lines');
assert.ok(source.includes('site-elevator-floor-code'),'runtime must render terminal floor code');
assert.ok(source.includes('site-elevator-stage'),'runtime must separate the stable console from the scenic Room window');
assert.equal(source.includes("--elevator-room-count"),false,'Room geometry should stay CSS-owned rather than being recalculated in runtime');
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
assert.ok(source.includes("document.body.classList.contains('home-body')"),'Home must own its multi-realm canvas instead of inheriting one elevator floor');
assert.ok(source.includes('if(homeOwnsRealmCanvas||!projection||!roomContract)return'),'Home must keep cross-floor navigation visible instead of being filtered as Plane');
assert.ok(source.includes('delete document.documentElement.dataset.siteFloor'),'Home runtime must clear stale single-floor state');
assert.ok(source.includes('if(!projection||!LEVELS.includes(spatial.levelId))return'),'pre-hydration render must preserve the build-stamped first-paint floor');
assert.ok(css.includes('body.home-body::before'),'elevator CSS must defensively suppress stale floor scenery on Home');
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

assert.ok(css.includes('background-color:var(--site-realm-fallback)'),'realm canvas must use the shared neutral fallback token');
assert.ok(css.includes('body:not(.home-body)::before'),'single-floor pages need one universal realm canvas');
assert.ok(css.includes('--site-realm-art:url("./home-heaven.avif")'),'Heaven pages must use final Heaven art');
assert.ok(css.includes('--site-realm-art:url("./home-plane.avif")'),'Plane pages must use final Plane art');
assert.ok(css.includes('--site-realm-art:url("./home-below.avif")'),'Below pages must use final Below art');
assert.equal(/html\[data-site-floor="(?:heaven|plane|below)"\]\{[\s\S]*?--site-panel:/.test(css),false,'floor identity must come from realm art, not global panel recoloring');
assert.ok(css.includes('--site-realm-art-size:max(1086px,100vw)'),'ordinary realm art should stay at or above native source width without the retired viewport-height overzoom');
assert.ok(css.includes('inset:-8vh 0'),'realm canvas must retain overscan for the shared page pan');
assert.ok(css.includes('background-color:var(--site-realm-fallback)'),'realm overscan must retain a nonblank fallback behind the image');
assert.ok(css.includes('@keyframes site-realm-page-pan'),'ordinary floor pages must share one lightweight scroll-pan animation');
assert.ok(css.includes('animation-timeline:scroll(root block)'),'modern browsers should pan realm art with native scroll timelines');
assert.equal(source.includes('requestAnimationFrame(update)'),false,'realm scrolling must not restore the retired JavaScript animation loop');
assert.equal(source.includes('installSceneParallax'),false,'fixed realm pages must not keep old parallax runtime');
assert.equal(lowerCss.includes('body.lower-layer-page::before'),false,'Below must not own a second compositor');
assert.equal(lowerCss.includes('site-below-root-field.svg'),false,'Below must not use retired SVG scene');
for(const asset of ['home-heaven.avif','home-plane.avif','home-below.avif'])assert.ok(journeyCss.includes(asset),'Room preview missing '+asset);

assert.ok(css.includes('isolation:isolate'),'ordinary floor pages must isolate the realm canvas behind their content');
assert.ok(css.includes('z-index:-1'),'realm canvas must sit behind document content inside the isolated body');
assert.equal(css.includes('body:not(.home-body) > :not(script):not(style)'),false,'realm layering must not rewrite direct-body child positioning');
assert.equal(css.includes('body:not(.lower-layer-page)::after'),false,'shared floor renderer must not add a second atmosphere compositor');
assert.equal(lowerCss.includes('body.lower-layer-page::after'),false,'Below must not add a second full-screen depth compositor');
assert.equal(lowerCss.includes('.lower-layer-surface::before'),false,'Below content must not rebuild duplicate terrain textures');
assert.equal(lowerCss.includes('.lower-layer-surface::after'),false,'Below content must not rebuild duplicate terrain textures');
assert.equal(css.includes('--site-scene-zoom'),false,'retired scene zoom state must stay removed');
assert.equal(source.includes("'--site-depth-progress'"),false,'runtime must not restore retired depth-progress state');
assert.equal(css.includes('background-attachment:fixed'),false,'realm canvases should use the fixed pseudo layer rather than fixed-background repaints');
assert.ok(lowerCss.length<13000,'lower floor CSS should remain consolidated rather than regrowing duplicate terrain systems');
assert.equal(lowerCss.includes('long tap roots'),false,'legacy stripe-built tap-root wallpaper must stay removed');
assert.equal(lowerCss.includes('thick roots: dark bark edge'),false,'legacy root stripe stack must stay removed');
assert.equal(lowerCss.includes('--site-depth-start'),false,'Below should not maintain a second animated depth-wash channel');
assert.equal(css.includes('@keyframes site-depth-wash'),false,'shared pixel realms must remain the only floor atmosphere system');
assert.match(css,/prefers-reduced-motion\s*:\s*reduce/,'elevator UI must still respect reduced-motion preferences');

console.log('Site elevator resolver + visual contract passed.');
