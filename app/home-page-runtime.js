// Lightweight homepage lazy loader. Artwork is static; no scroll-linked rendering.
(()=>{
  if(!document.body?.classList.contains('home-body'))return;
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
  loadScriptNear(document.querySelector('[data-news-feed]'),'app/news.js?v=20260920j','850px');
  loadScriptNear(
    document.getElementById('reality-cases')||document.getElementById('route-comparison'),
    'app/home-page-projection.js?v=20261003j',
    '1100px'
  );
})();
