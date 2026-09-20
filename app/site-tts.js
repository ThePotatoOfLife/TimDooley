(function(root){
  'use strict';
  if(!root||root.__potatoSiteTTSBooted)return;
  root.__potatoSiteTTSBooted=true;
  const doc=root.document;if(!doc)return;

  const current=[...doc.scripts].find(s=>/\/app\/site-tts\.js(?:\?|$)/.test(s.src||''))||doc.currentScript;
  let appBase='';
  try{appBase=new URL('./',current?.src||doc.baseURI).href}catch{appBase=''}
  const asset=name=>new URL(name,appBase||doc.baseURI).href;
  const loadCss=href=>new Promise(resolve=>{
    const existing=[...doc.querySelectorAll('link[rel="stylesheet"]')].find(x=>(x.href||'')===href||/\/app\/tts-drawer\.css(?:\?|$)/.test(x.href||''));
    if(existing){resolve();return}
    const link=doc.createElement('link');link.rel='stylesheet';link.href=href;link.onload=()=>resolve();link.onerror=()=>resolve();doc.head.appendChild(link);
  });
  const loadScript=(href,test)=>new Promise(resolve=>{
    if(test?.()){resolve();return}
    const existing=[...doc.scripts].find(x=>(x.src||'')===href);
    if(existing){existing.addEventListener('load',()=>resolve(),{once:true});existing.addEventListener('error',()=>resolve(),{once:true});return}
    const script=doc.createElement('script');script.src=href;script.defer=true;script.onload=()=>resolve();script.onerror=()=>resolve();doc.head.appendChild(script);
  });

  const INTERACTIVE_EXCLUDE=[
    'nav','.page-nav','.nav','.topnav','.world-family','.deep','.links','.routes','.path-grid',
    'footer','.footer','form','button','select','input','textarea','canvas','svg','iframe',
    '.science-controls','.science-library','.science-results','.timeline-explorer-standalone',
    '#archive-explorer','.archive-nav','.search','.gb-toolbar','.longform-toc',
    '.basin-modebar','.explorer-toolbar','.explorer-nav','.body-finder-box','.body-finder-results',
    '.house-journey-ribbon','.map-action','[role="map"]','[data-no-tts]','.ptts-drawer',
    '.ptts-selection-listen','.ptts-inline-listen'
  ].join(',');

  const INTERACTIVE_SECTION_MATCH=[
    '.science-library','.timeline-explorer-standalone','#archive-explorer','.longform-layout',
    '#body-finder','#vertebral-rooms','#brain-rooms','.basin-shell','[data-no-tts]'
  ].join(',');

  function clean(v){return String(v||'').replace(/\s+/g,' ').trim()}
  function pageLabel(main){
    return clean(main?.querySelector('h1')?.textContent)||clean(doc.title.replace(/\s+[—|-].*$/,''))||'Read aloud';
  }
  function chooseRoot(){
    return doc.querySelector('main[data-reader-surface],main.page--reading,main.page,main.longform-shell,main.shell,main.wrap,main');
  }
  function ensureId(el){
    if(el.id)return el.id;
    const base='tts-page-root';let id=base,n=2;
    while(doc.getElementById(id))id=base+'-'+n++;
    el.id=id;return id;
  }
  function meaningful(el){
    if(!el||el.matches?.(INTERACTIVE_SECTION_MATCH))return false;
    const clone=el.cloneNode(true);
    try{clone.querySelectorAll(INTERACTIVE_EXCLUDE).forEach(n=>n.remove())}catch{}
    return clean(clone.textContent).length>=90;
  }
  function markSections(main){
    const direct=[...main.children].filter(el=>/^(SECTION|ARTICLE)$/i.test(el.tagName||'')&&meaningful(el));
    const pool=direct.length?direct:[...main.querySelectorAll(':scope > div > section,:scope > div > article')].filter(meaningful);
    pool.forEach(el=>el.setAttribute('data-site-tts-section',''));
    return pool.length;
  }
  function placeHost(main){
    let host=doc.getElementById('site-tts');
    if(host)return host;
    host=doc.createElement('div');host.id='site-tts';host.className='site-tts-host';
    const header=main.querySelector(':scope > header,.page-header,.hero,.longform-hero');
    if(header?.insertAdjacentElement)header.insertAdjacentElement('afterend',host);
    else{
      const nav=main.querySelector(':scope > nav');
      if(nav?.insertAdjacentElement)nav.insertAdjacentElement('afterend',host);
      else main.prepend(host);
    }
    return host;
  }

  function configureAutomaticHost(){
    if(doc.querySelector('[data-tts-longform]'))return false;
    const main=chooseRoot();if(!main||main.matches('[data-tts-skip]'))return false;
    const id=ensureId(main);
    const host=placeHost(main);
    markSections(main);
    host.setAttribute('data-tts-longform','');
    host.dataset.ttsRoot='#'+id;
    host.dataset.ttsId='site-'+(main.dataset?.readerSurface||location.pathname.replace(/[^a-z0-9]+/gi,'-')||'page');
    host.dataset.ttsLabel=pageLabel(main);
    host.dataset.ttsAllLabel='Whole page';
    host.dataset.ttsCurrentLabel='Current section';
    host.dataset.ttsSelectionLabel='Selection';
    host.dataset.ttsItem='[data-site-tts-section]';
    host.dataset.ttsExclude=INTERACTIVE_EXCLUDE;
    return true;
  }

  async function boot(){
    configureAutomaticHost();
    if(!doc.querySelector('[data-tts-longform]'))return;
    await loadCss(asset('tts-drawer.css'));
    await loadScript(asset('tts-reader.js'),()=>Boolean(root.PotatoTTS?.TTSEngine));
    await loadScript(asset('tts-drawer.js'),()=>Boolean(root.PotatoTTSDrawer?.mount));
    await loadScript(asset('longform-tts-adapter.js'),()=>Boolean(root.PotatoLongformTTS?.autoMount));
    root.PotatoLongformTTS?.autoMount?.(doc);
  }

  const start=()=>{void boot()};
  doc.readyState==='loading'?doc.addEventListener('DOMContentLoaded',start,{once:true}):start();
})(typeof globalThis!=='undefined'?globalThis:window);
