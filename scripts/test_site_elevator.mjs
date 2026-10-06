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
  ['/north/', 'plane', null],
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
  const explicit=projection.route_contexts.find(row=>row.subroom_id===subroom.id);
  const route=explicit?.match||('/rooms/inside/'+(subroom.route_id||subroom.id)+'/');
  const ctx=elevator.resolveSpatialContext(route,projection,roomContract,subroomContract);
  assert.equal(ctx.roomId,subroom.parent_room_id, subroom.id+' must light its parent Room');
  assert.equal(ctx.levelId,primaryByRoom[subroom.parent_room_id], subroom.id+' must inherit the parent Room primary floor');
  assert.ok(['subroom-route','subroom-context'].includes(ctx.source), subroom.id+' must resolve through nested Room ownership');
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
const scienceHeader=elevator.roomsForLevel('plane',projection,roomContract).find(room=>room.id==='science-formal-models');
assert.equal(scienceHeader.title,'Science & Formal Models','header rail should preserve the finished illustrated Room title');
assert.equal(scienceHeader.fullTitle,'Science & Formal Models','illustrated header labels must preserve the canonical Room title');
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

assert.ok(css.includes('--elevator-slot-count:5'),'header must preserve the five-slot floor geometry contract');
assert.ok(css.includes('@media (max-width:760px)'),'true mobile must retain a compact fallback');
assert.equal((css.match(/@media \(min-width:761px\)/g)||[]).length,1,'tablet/desktop must have one responsive panorama owner');
assert.ok(css.includes('/* 2026-10-06 approved-reference responsive composition.'),'approved panorama architecture marker missing');
assert.equal(css.includes('/* Desktop illustrated header skin.'),false,'retired desktop HUD skin must not coexist with panorama strip');
assert.equal(css.includes('target-reference refinement'),false,'retired target-reference override must not coexist with panorama strip');
assert.equal(css.includes('exact target-reference desktop skin'),false,'retired exact desktop override must not coexist with panorama strip');
assert.ok(css.includes('background-image:var(--site-header-art)'),'responsive strip must use the dedicated panorama asset directly');
assert.ok(css.includes('background-size:100% 100%'),'responsive strip must fill the full shared composition box');
assert.match(css,/--elevator-shell-height:clamp\(106px,13\.96vw,286px\)/,'header height must scale continuously with viewport width');
assert.match(css,/\.site-elevator-main\{[\s\S]*?width:100%;[\s\S]*?max-width:none;/,'live geometry must share the full panorama width');
assert.ok(css.includes('grid-template-columns:repeat(var(--elevator-visible-count),minmax(0,1fr))'),'room hit geometry must follow the painted plaque count');
assert.equal(css.includes('overflow-x:auto'),false,'Room rail must not horizontally scroll');
assert.equal(css.includes('scrollbar-width'),false,'Room rail must not render a scrollbar');
assert.ok((css.match(/!important/g)||[]).length<=8,'elevator CSS should keep specificity escalation tightly bounded');
assert.ok(css.includes('--site-header-art:url("./header-heaven.svg")'),'Heaven panorama token missing');
assert.ok(css.includes('--site-header-art:url("./header-plane.svg")'),'Plane panorama token missing');
assert.ok(css.includes('--site-header-art:url("./header-below.svg")'),'Below panorama token missing');
for(const asset of ['header-heaven.svg','header-plane.svg','header-below.svg']){
  const art=fs.readFileSync(path.join(ROOT,'app',asset),'utf8');
  assert.ok(art.includes('viewBox="0 0 1655 231"'),asset+' must share the canonical 1655×231 composition');
  assert.ok(art.includes('preserveAspectRatio="xMidYMid slice"'),asset+' must preserve panorama proportions');
}
assert.equal(css.includes('backdrop-filter:'),false,'elevator must not use blur-heavy legacy HUD materials');
assert.equal(css.includes('.site-elevator-room.is-secondary'),false,'header CSS must not preserve cross-floor Room affordances');
assert.equal(source.includes('is-secondary'),false,'runtime must not emit cross-floor Room doors');
assert.ok(css.includes('@media (prefers-contrast: more)'),'header needs a generic high-contrast mode');
assert.ok(css.includes('[data-elevator-ready="false"]'),'loading state must retain a neutral treatment');
assert.ok(css.includes('.site-elevator-up::before{content:"△"}'),'mobile/base fallback must retain up-arrow semantics');
assert.ok(css.includes('.site-elevator-down::before{content:"▽"}'),'mobile/base fallback must retain down-arrow semantics');

assert.ok(source.includes("roomRail.dataset.roomCount=String(visibleCount)"),'runtime must expose actual floor door count for illustrated layout');
assert.ok(css.includes('grid-template-columns:repeat(var(--elevator-visible-count),minmax(0,1fr))'),'desktop illustrated rail must size Heaven, Plane and Below by their actual door count');
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
assert.ok(css.includes('--site-realm-art-size:max(1086px,100vw)'),'ordinary realm art should stay at or above native source width without viewport-height overzoom');
assert.ok(css.includes('background-color:var(--site-realm-fallback)'),'realm canvas must retain a nonblank fallback behind the image');
assert.equal(css.includes('@keyframes site-realm-page-pan'),false,'ordinary floor pages must not spend continuous compositor work on decorative realm panning');
assert.equal(css.includes('animation-timeline:scroll(root block)'),false,'ordinary floor pages must keep the realm canvas static while scrolling');
assert.equal(css.includes('filter:saturate(1.06) contrast(1.045)'),false,'full-screen realm canvas must not use an always-on image filter');
assert.equal(css.includes('filter:saturate(.95) contrast(1.05)'),false,'header scenery must not use an always-on image filter');
assert.equal(css.includes('transform:translateZ(0)'),false,'header/realm scenery must not force permanent compositor layers');
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
