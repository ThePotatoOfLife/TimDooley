(()=> {
  const script=document.currentScript;
  const src=script?.dataset?.bodyOverlay||'';
  if(!src)return;
  const esc=v=>String(v??'').replace(/[&<>"]/g,s=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
  const wanted=(script.dataset.bodyObjects||'').split(',').map(x=>x.trim()).filter(Boolean);
  const mountSel=script.dataset.bodyMount||'[data-body-lens]';
  fetch(src).then(r=>r.ok?r.json():Promise.reject()).then(data=>{
    const mount=document.querySelector(mountSel);if(!mount)return;
    const rows=(data.objects||[]).filter(x=>!wanted.length||wanted.includes(x.id));
    if(!rows.length)return;
    if(!document.getElementById('body-lens-style')){
      const st=document.createElement('style');st.id='body-lens-style';st.textContent=`
      .body-lens{margin:28px 0;border-top:1px solid var(--site-line);padding-top:18px}.body-lens-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}.body-lens-card{border:1px solid var(--site-line);border-radius:11px;padding:13px;background:var(--site-panel)}.body-lens-card strong{display:block;font:400 18px var(--site-font-serif);color:var(--site-gold)}.body-lens-card p{font-size:10px;line-height:1.45;color:var(--site-muted)}.body-lens-card a{font-size:9px;color:var(--site-green);text-decoration:none}.body-lens-tags{display:flex;flex-wrap:wrap;gap:4px;margin:7px 0}.body-lens-tags span{font-size:7px;text-transform:uppercase;letter-spacing:.05em;border:1px solid var(--site-line);border-radius:999px;padding:3px 5px;color:var(--site-muted)}
      `;document.head.appendChild(st);
    }
    mount.classList.add('body-lens');
    mount.innerHTML='<p class="eyebrow">Body lens</p><h2>Same object, different layer</h2><p class="boundary">These cards do not create duplicate truth. They project the same governed object through anatomy, project symbolism, history/tradition and systems views.</p><div class="body-lens-grid">'+rows.map(x=>{
      const p=x.projections||{};const summary=p.anatomy||p.tradition||p.project||p.systems||'Cross-layer project object.';
      return '<article class="body-lens-card"><strong>'+esc(x.label)+'</strong><div class="body-lens-tags">'+(x.lens_tags||[]).map(t=>'<span>'+esc(t)+'</span>').join('')+'</div><p>'+esc(summary)+'</p><a href="'+esc(x.body_route||'/life-body/')+'">Open exact Body view →</a></article>';
    }).join('')+'</div>';
  }).catch(()=>{});
})();