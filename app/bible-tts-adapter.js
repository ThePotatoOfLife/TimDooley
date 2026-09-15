(function(root,factory){
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoBibleTTS=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const clean=value=>String(value??'').replace(/\s+/g,' ').trim();
  function join(parts){return parts.map(clean).filter(Boolean).join(' ')}
  function buildBiblePayload(parts={}){
    const project=clean(parts.project),scripture=clean(parts.scripture),why=clean(parts.why),mismatch=clean(parts.mismatch);
    const both=join([
      project&&`Project. ${project}`,
      scripture&&`Scripture. ${scripture}`,
      why&&`Why these connect. ${why}`,
      mismatch,
    ]);
    const whyText=join([why,mismatch]);
    return {
      id:clean(parts.id),
      label:clean(parts.title)||'Bible comparison',
      sections:[
        {id:'both',label:'Both',text:both},
        {id:'project',label:'Project',text:project},
        {id:'scripture',label:'Scripture',text:scripture},
        {id:'why',label:'Why',text:whyText},
      ].filter(section=>section.text),
    };
  }
  function textOf(node,selector){return clean(node?.querySelector(selector)?.textContent)}
  function extractRelation(node){
    if(!node)return buildBiblePayload({});
    const article=node.matches?.('.relation')?node:node.querySelector?.('.relation');
    if(!article)return buildBiblePayload({});
    const sides=article.querySelectorAll('.parallel .side');
    return buildBiblePayload({
      id:article.dataset?.relationId||'',
      title:textOf(article,'.relation-title'),
      project:clean(sides[0]?.textContent),
      scripture:clean(sides[1]?.textContent),
      why:textOf(article,'.why p'),
      mismatch:textOf(article,'.boundary-callout'),
    });
  }
  function mount(){
    if(typeof document==='undefined'||!root?.PotatoTTSDrawer)return null;
    const active=document.getElementById('active-relation');
    const nav=document.querySelector('.comparison-nav');
    if(!active||!nav)return null;
    let host=document.getElementById('bible-tts-drawer');
    if(!host){host=document.createElement('div');host.id='bible-tts-drawer';host.className='bible-tts-drawer';nav.before(host)}
    const read=()=>extractRelation(active);
    const drawer=root.PotatoTTSDrawer.mount({target:host,getPayload:read,settingsKey:'potato-tts-settings'});
    let lastId=read().id;
    const observer=new MutationObserver(()=>{
      const next=read();
      if(next.id!==lastId){lastId=next.id;drawer?.setPayload(next)}
      else drawer?.setPayload(next);
    });
    observer.observe(active,{childList:true,subtree:true,characterData:true});
    return {drawer,observer,refresh:()=>drawer?.setPayload(read())};
  }
  if(typeof document!=='undefined'){
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else setTimeout(mount,0);
  }
  return {buildBiblePayload,extractRelation,mount};
});