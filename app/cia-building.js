(()=>{'use strict';
const BASE='/TimDooley/';
const esc=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const boxes=[...document.querySelectorAll('[data-cia-building-shell]')];
if(!boxes.length)return;
const currentCharacter=new URLSearchParams(location.search).get('character')||'';
const hrefFor=item=>{
 let href=BASE+String(item.path||'').replace(/^\/+/, '');
 if(currentCharacter&&item.preserve_character){
   const u=new URL(href,location.origin);
   u.searchParams.set('character',currentCharacter);
   href=u.pathname+u.search+u.hash;
 }
 return href;
};
fetch(BASE+'knowledge/cia/institution-building.json').then(r=>{if(!r.ok)throw new Error('building');return r.json()}).then(data=>{
 for(const box of boxes){
  const zone=box.dataset.zone||'archive';
  const nav=(data.navigation||[]).map(item=>'<a'+(item.zone===zone?' class="active" aria-current="page"':'')+' href="'+esc(hrefFor(item))+'">'+esc(item.label)+'</a>').join('');
  const room=(data.navigation||[]).find(x=>x.zone===zone);
  const flow=(data.flows||[]).find(x=>x.sequence.includes(zone));
  const selected=currentCharacter?'<span class="cia-building__subject">Carrying file: <b>'+esc(currentCharacter)+'</b></span>':'';
  box.innerHTML='<div class="cia-building__roof"><div><span class="cia-building__kicker">Inside one institution</span><strong>'+esc(data.title)+'</strong><small>Two entrances · one provenance spine · archive + accounts + repair</small></div>'+selected+'</div>'+
   '<nav class="cia-building__corridor" aria-label="Institution rooms">'+nav+'</nav>'+
   '<div class="cia-building__location"><span>You are here · '+esc(room?.label||zone)+'</span><small>'+esc(data.reader_position_note||'')+'</small></div>'+
   '<div class="cia-building__spine" aria-label="Shared system spine"><span>Evidence</span><i>→</i><span>Dossier</span><i>→</i><span>Account</span><i>→</i><span>System ledger</span><i>→</i><span>Repair</span></div>'+
   (flow?'<p class="cia-building__flow">'+esc(flow.meaning)+'</p>':'');
 }
}).catch(()=>{
 for(const box of boxes)box.innerHTML='<div class="cia-building__location"><span>CIA / World Spiritual Bank</span><small>Shared institution shell unavailable; this room still works independently.</small></div>';
});
})();
