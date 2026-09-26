(()=> {
  const script=document.currentScript;
  if(script&&!document.querySelector('link[data-body-lens-style]')){
    try{
      const link=document.createElement('link');
      link.rel='stylesheet';
      link.href=new URL('body-relational-lens.css?v=20260926a',script.src).href;
      link.dataset.bodyLensStyle='';
      document.head.appendChild(link);
    }catch(_){}
  }
  const src=script?.dataset?.bodyOverlay||'';
  if(!src)return;
  const esc=v=>String(v??'').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
  const wanted=(script.dataset.bodyObjects||'').split(',').map(x=>x.trim()).filter(Boolean);
  const mountSel=script.dataset.bodyMount||'[data-body-lens]';
  const projectUrl=(route)=>{
    const value=String(route||'/life-body/');
    if(/^https?:\/\//i.test(value))return value;
    return new URL('../'+value.replace(/^\/+/,''),script.src).href;
  };
  fetch(src).then(r=>r.ok?r.json():Promise.reject()).then(data=>{
    const mount=document.querySelector(mountSel);if(!mount)return;
    const rows=(data.objects||[]).filter(x=>!wanted.length||wanted.includes(x.id));
    if(!rows.length)return;
    mount.classList.add('body-lens');
    mount.innerHTML='<p class="eyebrow">Body lens</p><h2>Same object, different layer</h2><p class="boundary">These cards do not create duplicate truth. They project the same governed object through anatomy, project symbolism, history/tradition and systems views.</p><div class="body-lens-grid">'+rows.map(x=>{
      const p=x.projections||{};const summary=p.anatomy||p.tradition||p.project||p.systems||'Cross-layer project object.';const fc=x.formal_correspondence||{};const status=(fc.correspondence_maturity&&fc.epistemic_status)?'<div class="body-lens-formal"><b>'+esc(fc.correspondence_maturity)+' · '+esc(fc.epistemic_status)+'</b><span>'+esc(fc.map||'typed comparator')+'</span></div>':'';
      return '<article class="body-lens-card"><strong>'+esc(x.label)+'</strong><div class="body-lens-tags">'+(x.lens_tags||[]).map(t=>'<span>'+esc(t)+'</span>').join('')+'</div><p>'+esc(summary)+'</p>'+status+'<a href="'+esc(projectUrl(x.body_route||'/life-body/'))+'">Open exact Body view →</a></article>';
    }).join('')+'</div>';
  }).catch(()=>{});
})();