// Lightweight homepage lazy loader. Artwork is static; no scroll-linked rendering.
(()=>{
  if(!document.body?.classList.contains('home-body'))return;
  const loadStyleNear=(target,href,margin='1200px')=>{
    if(!target)return;
    let loaded=false;
    const load=()=>{
      if(loaded)return;
      loaded=true;
      const link=document.createElement('link');
      link.rel='stylesheet';
      link.href=href;
      document.head.appendChild(link);
    };
    if(!('IntersectionObserver' in window)){setTimeout(load,500);return}
    const observer=new IntersectionObserver(entries=>{
      if(entries.some(entry=>entry.isIntersecting)){
        observer.disconnect();
        load();
      }
    },{rootMargin:`${margin} 0px`});
    observer.observe(target);
  };

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
  const loadDeferredTTS=()=>{
    if(document.querySelector('script[data-home-tts-loader]'))return;
    const script=document.createElement('script');
    script.src='app/site-tts.js?v=20261003a';
    script.defer=true;
    script.dataset.homeTtsLoader='';
    document.body.appendChild(script);
  };
  const armTTS=()=>{
    ['pointerdown','keydown','touchstart'].forEach(type=>window.removeEventListener(type,armTTS));
    loadDeferredTTS();
  };
  ['pointerdown','keydown','touchstart'].forEach(type=>window.addEventListener(type,armTTS,{once:true,passive:true}));
  if('requestIdleCallback' in window)requestIdleCallback(loadDeferredTTS,{timeout:2600});
  else setTimeout(loadDeferredTTS,1800);

  const newsTarget=document.querySelector('[data-news-feed]');
  loadStyleNear(newsTarget,'app/news.css?v=20260920j','1400px');
  loadScriptNear(newsTarget,'app/news.js?v=20260920j','850px');
  loadScriptNear(
    document.getElementById('reality-cases')||document.getElementById('route-comparison'),
    'app/home-page-projection.js?v=20261003j',
    '1100px'
  );
})();
