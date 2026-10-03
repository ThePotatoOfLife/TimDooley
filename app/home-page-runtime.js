// Lightweight homepage runtime: realm stepping + lazy secondary systems.
(()=>{
  const body=document.body;
  if(!body?.classList.contains('home-body'))return;

  const markers=[...document.querySelectorAll('[data-home-realm-marker]')];
  const focusY=()=>Math.max(80,innerHeight*.42);
  let moveTimer=0;

  const setRealm=(realm)=>{
    if(!realm||body.dataset.homeRealm===realm)return;
    body.dataset.homeRealm=realm;
    body.classList.add('home-world-moving');
    clearTimeout(moveTimer);
    moveTimer=setTimeout(()=>body.classList.remove('home-world-moving'),760);
  };

  const pickRealm=()=>{
    let realm=markers[0]?.dataset.homeRealmMarker||'heaven';
    const y=focusY();
    for(const marker of markers){
      if(marker.getBoundingClientRect().top<=y)realm=marker.dataset.homeRealmMarker||realm;
      else break;
    }
    setRealm(realm);
  };

  body.dataset.homeRealm='heaven';
  pickRealm();

  if('IntersectionObserver' in window&&markers.length){
    const realmObserver=new IntersectionObserver(()=>pickRealm(),{
      rootMargin:'-34% 0px -56% 0px',
      threshold:0
    });
    markers.forEach(marker=>realmObserver.observe(marker));
  }

  const loadScriptNear=(target,src,margin='900px')=>{
    if(!target)return;
    let loaded=false;
    const load=()=>{
      if(loaded)return;
      loaded=true;
      const script=document.createElement('script');
      script.src=src;
      script.defer=true;
      document.body.appendChild(script);
    };
    if(!('IntersectionObserver' in window)){setTimeout(load,700);return}
    const observer=new IntersectionObserver(entries=>{
      if(entries.some(entry=>entry.isIntersecting)){
        observer.disconnect();
        load();
      }
    },{rootMargin:`${margin} 0px`});
    observer.observe(target);
  };

  loadScriptNear(
    document.querySelector('[data-news-feed]'),
    'app/news.js?v=20260920j',
    '850px'
  );

  loadScriptNear(
    document.getElementById('reality-cases')||document.getElementById('route-comparison'),
    'app/home-page-projection.js?v=20261003j',
    '1100px'
  );
})();
