(async()=>{
 const esc=v=>String(v??'').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
 const houseDataRoot=new URL('../data/house/',import.meta.url);
 let ir;
 try{ir=await fetch(new URL('room-inhabitants.json',houseDataRoot),{cache:'no-cache'})}catch(_){ir=null}
 if(!ir?.ok){document.getElementById('summary').textContent='The explanatory layer is available, but the live object list could not be loaded.';document.getElementById('results').innerHTML='<p class="loading">The live object list is unavailable. The page above still explains how inhabitants, cases and Room lenses relate.</p>';return}
 const data=await ir.json();
 let sub={subrooms:[]},subroomsAvailable=false;
 try{
   const sr=await fetch(new URL('subrooms.json',houseDataRoot),{cache:'no-cache'});
   if(sr.ok){sub=await sr.json();subroomsAvailable=true}
 }catch(_){}
 const subBy=Object.fromEntries((sub.subrooms||[]).map(x=>[x.id,x]));
 const rows=data.inhabitants||[];
 const q=document.getElementById('q'),kind=document.getElementById('kind'),room=document.getElementById('room'),maturity=document.getElementById('maturity'),results=document.getElementById('results');
 document.getElementById('summary').textContent=rows.length+' objects currently appear inside one or more Rooms. They can be inspected through different lenses without becoming separate copies.'+(subroomsAvailable?'':' Room names and spatial placement are temporarily unavailable, but object browsing remains active.');
 [...new Set(rows.map(x=>x.kind).filter(Boolean))].sort().forEach(v=>kind.insertAdjacentHTML('beforeend','<option value="'+esc(v)+'">'+esc(v)+'</option>'));
 [...new Set(rows.flatMap(x=>x.room_ids||[]))].sort((a,b)=>(subBy[a]?.title||a).localeCompare(subBy[b]?.title||b)).forEach(v=>room.insertAdjacentHTML('beforeend','<option value="'+esc(v)+'">'+esc(subBy[v]?.title||v)+'</option>'));
 function render(){
   const term=q.value.trim().toLowerCase(),kv=kind.value,rv=room.value,mv=maturity.value;
   const filtered=rows.filter(x=>(!kv||x.kind===kv)&&(!rv||(x.room_ids||[]).includes(rv))&&(!mv||x.maturity===mv)&&(!term||[x.label,x.kind,x.summary,...(x.room_ids||[]).map(id=>subBy[id]?.title||id)].join(' ').toLowerCase().includes(term)));
   const groups={};filtered.forEach(x=>(groups[x.kind||'object']??=[]).push(x));
   results.innerHTML=Object.entries(groups).sort(([a],[b])=>a.localeCompare(b)).map(([k,list])=>'<section class="kind-group"><p class="eyebrow">'+esc(k)+'</p><div class="obj-grid">'+list.map(x=>{const first=(x.room_ids||[])[0],s=subBy[first],params=new URLSearchParams({room:s?.parent_room_id||'',inner:first||'',object:x.id});return '<article class="obj-card"><h3>'+esc(x.label)+'</h3><p>'+esc(x.summary||'House inhabitant or case.')+'</p><div class="lenses"><span>'+esc(x.maturity||'seed')+'</span>'+(x.room_ids||[]).map(id=>'<span>'+esc(subBy[id]?.title||id)+'</span>').join('')+'</div>'+(subroomsAvailable&&s?.parent_room_id?'<a href="../../elevator/?'+params.toString()+'">Locate in House →</a>':(x.route?'<a href="'+esc(String(x.route).startsWith('/')?'../..'+x.route:x.route)+'">Open object →</a>':'<span class="loading">Spatial placement unavailable</span>'))+'</article>'}).join('')+'</div></section>').join('')||'<p>No inhabitants match this view.</p>';
 }
 q.addEventListener('input',render);kind.addEventListener('change',render);room.addEventListener('change',render);maturity.addEventListener('change',render);render();
})();
