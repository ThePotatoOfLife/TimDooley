(()=>{
  const REGISTRY='data/canonical-record-registry.json';
  const safeSource=source=>typeof source==='string'&&/^data\/[A-Za-z0-9._/-]+\.json$/i.test(source)&&!source.includes('..')&&!source.startsWith('/');
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let pending=null;
  let resolving=false;
  let registryPromise=null;

  function requestedId(){
    if(!location.hash.startsWith('#lookup='))return null;
    try{return decodeURIComponent(location.hash.slice(8))}catch{return null}
  }
  function remember(){
    const id=requestedId();
    if(id)pending=id;
  }
  function registry(){
    if(!registryPromise)registryPromise=fetch(REGISTRY).then(response=>{
      if(!response.ok)throw new Error(`registry ${response.status}`);
      return response.json();
    });
    return registryPromise;
  }
  function showChoices(id,sources){
    const reader=document.querySelector('#reader');
    if(!reader)return;
    const buttons=sources.map(source=>`<button class="record-link" data-record="${esc(source)}"><span class="recordtype">OPEN MATCH</span><strong>${esc(source.split('/').pop().replace(/\.json$/i,''))}</strong><code>${esc(source)}</code></button>`).join('');
    reader.innerHTML=`<div class="eyebrow">Archive ID lookup</div><h2>${esc(id)}</h2><p class="summary">${sources.length===1?'One source carries this ID.':'This ID appears in more than one source, so the archive will not guess which occurrence you meant.'}</p><div class="section"><h3>${sources.length===1?'Source':'Choose a source'}</h3>${buttons}</div><div id="record-detail"></div>`;
    history.replaceState(null,'',`#lookup=${encodeURIComponent(id)}`);
  }
  function showMissing(id,message){
    const reader=document.querySelector('#reader');
    if(!reader)return;
    reader.innerHTML=`<div class="eyebrow">Archive ID lookup</div><h2>${esc(id)}</h2><p class="summary">${esc(message)}</p>`;
    history.replaceState(null,'',`#lookup=${encodeURIComponent(id)}`);
  }
  async function resolvePending(){
    if(resolving||!pending)return;
    resolving=true;
    const id=pending;
    pending=null;
    try{
      const data=await registry();
      const row=(data.records||[]).find(item=>String(item.id)===id);
      const sources=[...new Set((row?.occurrences||[]).map(item=>item.source).filter(safeSource))];
      if(sources.length===1){
        location.hash=`#record=${encodeURIComponent(sources[0])}`;
      }else if(sources.length>1){
        showChoices(id,sources);
      }else{
        showMissing(id,'No safe source record is registered for this ID. Use Explore search or a nearby branch instead.');
      }
    }catch(error){
      showMissing(id,`ID lookup is unavailable: ${error.message}`);
    }finally{
      resolving=false;
      if(pending)resolvePending();
    }
  }

  remember();
  window.addEventListener('hashchange',()=>{remember();resolvePending()});
  window.addEventListener('potato:navigation',()=>resolvePending());
})();
