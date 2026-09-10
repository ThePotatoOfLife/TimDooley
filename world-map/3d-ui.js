const app = document.getElementById('atlasApp');
const panel = document.getElementById('panel');
const panelToggle = document.getElementById('panelToggle');
const mapInspectorToggle = document.getElementById('mapInspectorToggle');
const focusMode = document.getElementById('focusMode');
const menus = [...document.querySelectorAll('details.menu')];

function setPanel(open, {persist = true} = {}) {
  if (!app) return;
  app.classList.toggle('panel-collapsed', !open);
  panelToggle?.classList.toggle('active', open);
  mapInspectorToggle?.classList.toggle('active', open);
  panelToggle?.setAttribute('aria-pressed', String(open));
  mapInspectorToggle?.setAttribute('aria-pressed', String(open));
  if (persist) localStorage.setItem('atlas:panel-open', open ? '1' : '0');
  requestAnimationFrame(() => window.__potatoAtlasMap?.resize?.());
}

function setFocus(on, {persist = true} = {}) {
  if (!app) return;
  app.classList.toggle('ui-focus', on);
  focusMode?.classList.toggle('active', on);
  focusMode && (focusMode.textContent = on ? 'Focus mode · on' : 'Focus mode · hide overlays');
  if (persist) localStorage.setItem('atlas:focus-mode', on ? '1' : '0');
}

function closeOtherMenus(current) {
  for (const menu of menus) if (menu !== current) menu.open = false;
}
for (const menu of menus) menu.addEventListener('toggle', () => menu.open && closeOtherMenus(menu));

document.addEventListener('click', event => {
  if (!event.target.closest('details.menu')) for (const menu of menus) menu.open = false;
});

panelToggle?.addEventListener('click', () => setPanel(app?.classList.contains('panel-collapsed')));
mapInspectorToggle?.addEventListener('click', () => setPanel(app?.classList.contains('panel-collapsed')));
focusMode?.addEventListener('click', () => setFocus(!app?.classList.contains('ui-focus')));

// Restore explicit user preference. First visit remains map-first / inspector closed.
setPanel(localStorage.getItem('atlas:panel-open') === '1', {persist:false});
setFocus(localStorage.getItem('atlas:focus-mode') === '1', {persist:false});

// Contextual disclosure: opening a country, relation, evidence card or Axis level
// should reveal the inspector once, unless the user has deliberately enabled focus mode.
let lastSignature = panel?.textContent || '';
const observer = panel && new MutationObserver(() => {
  const signature = panel.textContent || '';
  if (signature === lastSignature) return;
  lastSignature = signature;
  if (app?.classList.contains('ui-focus')) return;
  const isLanding = /Explore the world/.test(signature);
  if (!isLanding) setPanel(true, {persist:false});
});
observer?.observe(panel, {childList:true, subtree:true, characterData:true});

// Feature modules insert controls relative to relationType. Since relationType now
// lives in Layers, their injected selectors inherit progressive disclosure automatically.
const layersPop = document.querySelector('#layersMenu .menu-pop');
const relocateInjectedLayerControls = () => {
  for (const id of ['axisFieldView','empiricalNetworkView']) {
    const node = document.getElementById(id);
    if (node && layersPop && node.parentElement !== layersPop) layersPop.appendChild(node);
  }
};
new MutationObserver(relocateInjectedLayerControls).observe(document.body, {childList:true, subtree:true});
relocateInjectedLayerControls();

// Keep the persistent surface sparse. Axis remains fully available, but its large
// navigator is opt-in through the compact Axis handle added here.
function installAxisToggle() {
  const nav = document.getElementById('axisDepthNavigator');
  if (!nav || document.getElementById('axisCompactToggle')) return;
  nav.hidden = localStorage.getItem('atlas:axis-open') !== '1';
  const button = document.createElement('button');
  button.id = 'axisCompactToggle';
  button.textContent = nav.hidden ? 'Axis' : 'Axis · open';
  button.title = 'Show or hide the D1–D11 Axis navigator';
  button.style.cssText = 'position:absolute;right:12px;top:44px;z-index:4;border-radius:999px;background:#0b1010df;backdrop-filter:blur(8px)';
  button.classList.toggle('active', !nav.hidden);
  button.addEventListener('click', () => {
    nav.hidden = !nav.hidden;
    localStorage.setItem('atlas:axis-open', nav.hidden ? '0' : '1');
    button.textContent = nav.hidden ? 'Axis' : 'Axis · open';
    button.classList.toggle('active', !nav.hidden);
  });
  document.querySelector('.mapwrap')?.appendChild(button);
}
new MutationObserver(installAxisToggle).observe(document.body, {childList:true,subtree:true});
installAxisToggle();

window.__potatoAtlasUI = {setPanel,setFocus};
