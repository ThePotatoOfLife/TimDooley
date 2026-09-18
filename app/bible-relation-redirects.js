(()=>{
'use strict';
function redirectLegacyRelation(){
  const ready=window.BibleCorpus?.ready;
  if(!ready)return;
  ready.then(corpus=>{
    const redirects=corpus?.redirects||{};
    const url=new URL(location.href);
    const current=url.searchParams.get('id');
    const target=window.BibleCorpus?.resolveRelationId?.(current,redirects)||current;
    if(!current||!target||target===current)return;
    url.searchParams.set('id',target);
    location.replace(url.toString());
  }).catch(error=>console.warn('Bible legacy relation redirect unavailable',error));
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',redirectLegacyRelation,{once:true});else redirectLegacyRelation();
})();
