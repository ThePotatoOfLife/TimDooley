(()=>{
  const GOLD=(1+Math.sqrt(5))/2;
  const NS='http://www.w3.org/2000/svg';
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function el(name,attrs={},text=''){
    const n=document.createElementNS(NS,name);
    for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,String(v));
    if(text)n.textContent=text;
    return n;
  }
  function pathFor(sign,chirality,turns,scale,cx,cy){
    const pts=[]; const steps=Math.max(80,turns*70);
    const b=2*Math.log(GOLD)/Math.PI;
    for(let i=0;i<=steps;i++){
      const t=(turns*2*Math.PI)*i/steps;
      const R=scale*(Math.exp(b*t)-1);
      const th=(sign>0?1:chirality)*t + (sign<0?Math.PI:0);
      const x=cx+R*Math.cos(th);
      const y=cy-sign*(12*t+R*.20);
      pts.push((i?'L':'M')+x.toFixed(2)+' '+y.toFixed(2));
    }
    return pts.join(' ');
  }
  function mount(root){
    const levels=Number(root.dataset.levels||4);
    const turns=Number(root.dataset.turns||1.25);
    let chirality=-1;
    const wrap=document.createElement('div');wrap.className='spiral-field-shell';
    wrap.innerHTML=`
      <div class="spiral-field-controls" role="group" aria-label="Bidirectional spiral field controls">
        <button type="button" data-toggle="terrain" aria-pressed="true">Terrain</button>
        <button type="button" data-toggle="tree" aria-pressed="true">Tree / roots</button>
        <button type="button" data-toggle="rings" aria-pressed="true">Layer rings</button>
        <button type="button" data-chirality aria-pressed="true">Mirrored chirality</button>
      </div>
      <div class="spiral-field-stage"></div>
      <p class="spiral-field-note">Axis = vertical orientation · Plane = waist section · radius = modeled scope/amplitude · angle = recurrence/phase. Mountain, Garden, Swamp and Drain are overlays, not the spiral itself. Direction, radius and handedness do not set moral value.</p>`;
    root.replaceChildren(wrap);
    const stage=wrap.querySelector('.spiral-field-stage');
    const svg=el('svg',{viewBox:'0 0 760 680',role:'img','aria-labelledby':'spiralFieldTitle spiralFieldDesc'});
    svg.append(el('title',{id:'spiralFieldTitle'},'Bidirectional O-centered spiral field'));
    svg.append(el('desc',{id:'spiralFieldDesc'},'A central Plane and Axis with mirrored widening spiral trajectories above and below, sampled layer rings, Mountain and Garden overlays above, Roots, Swamp and Drain overlays below.'));
    stage.append(svg);

    const terrain=el('g',{'data-layer':'terrain'});
    terrain.append(el('path',{d:'M380 332 L292 128 Q380 70 468 128 Z',class:'sf-mountain'}));
    terrain.append(el('path',{d:'M220 138 Q380 72 540 138 Q500 190 380 214 Q260 190 220 138 Z',class:'sf-garden'}));
    terrain.append(el('path',{d:'M182 470 Q380 402 578 470 Q554 610 380 632 Q206 610 182 470 Z',class:'sf-swamp'}));
    terrain.append(el('path',{d:'M330 500 Q380 470 430 500 L398 620 Q380 646 362 620 Z',class:'sf-drain'}));
    terrain.append(el('text',{x:380,y:112,'text-anchor':'middle',class:'sf-label'},'MOUNTAIN · integration'));
    terrain.append(el('text',{x:380,y:166,'text-anchor':'middle',class:'sf-label'},'GARDEN · generativity'));
    terrain.append(el('text',{x:380,y:548,'text-anchor':'middle',class:'sf-label'},'SWAMP · entanglement regime'));
    terrain.append(el('text',{x:380,y:612,'text-anchor':'middle',class:'sf-label'},'DRAIN'));
    svg.append(terrain);

    const rings=el('g',{'data-layer':'rings'});
    const maxR=170, stepY=52;
    for(let n=1;n<=levels;n++){
      const frac=(Math.pow(GOLD,n)-1)/(Math.pow(GOLD,levels)-1);
      const rx=42+maxR*frac;
      const ry=12+18*frac;
      const dy=n*stepY;
      for(const sign of [1,-1]){
        rings.append(el('ellipse',{cx:380,cy:340-sign*dy,rx,ry,class:'sf-ring'}));
        rings.append(el('text',{x:380+rx+8,y:344-sign*dy,class:'sf-ring-label'},`Σ${sign>0?'+':'-'}${n}`));
      }
    }
    svg.append(rings);

    const organic=el('g',{'data-layer':'tree'});
    organic.append(el('path',{d:'M380 340 L380 208 M380 250 L322 180 M380 248 L438 180 M380 220 L350 150 M380 220 L410 150',class:'sf-tree'}));
    organic.append(el('path',{d:'M380 340 C360 392 322 432 278 468 M380 340 C400 392 438 432 482 468 M380 356 C350 414 350 470 334 524 M380 356 C410 414 410 470 426 524',class:'sf-root'}));
    svg.append(organic);

    const geom=el('g',{'data-layer':'geometry'});
    geom.append(el('line',{x1:380,y1:38,x2:380,y2:642,class:'sf-axis'}));
    geom.append(el('line',{x1:82,y1:340,x2:678,y2:340,class:'sf-plane'}));
    geom.append(el('circle',{cx:380,cy:340,r:7,class:'sf-origin'}));
    geom.append(el('text',{x:394,y:328,class:'sf-origin-label'},'O · Here / Door'));
    geom.append(el('text',{x:392,y:58,class:'sf-axis-label'},'+Axis'));
    geom.append(el('text',{x:392,y:638,class:'sf-axis-label'},'−Axis'));
    geom.append(el('text',{x:92,y:330,class:'sf-plane-label'},'Σ₀ · Plane'));
    svg.append(geom);

    const spirals=el('g',{'data-layer':'spirals'});
    const redraw=()=>{
      spirals.replaceChildren();
      spirals.append(el('path',{d:pathFor(1,chirality,turns,8,380,340),class:'sf-spiral sf-upper'}));
      spirals.append(el('path',{d:pathFor(-1,chirality,turns,8,380,340),class:'sf-spiral sf-lower'}));
    };
    redraw(); svg.append(spirals);

    wrap.querySelectorAll('[data-toggle]').forEach(btn=>btn.addEventListener('click',()=>{
      const key=btn.dataset.toggle, group=svg.querySelector('[data-layer="'+key+'"]');
      const on=btn.getAttribute('aria-pressed')!=='false';
      btn.setAttribute('aria-pressed',String(!on));
      if(group)group.hidden=on;
    }));
    wrap.querySelector('[data-chirality]').addEventListener('click',e=>{
      const btn=e.currentTarget; const mirrored=btn.getAttribute('aria-pressed')==='true';
      chirality=mirrored?1:-1; btn.setAttribute('aria-pressed',String(!mirrored));
      btn.textContent=mirrored?'Same chirality':'Mirrored chirality'; redraw();
    });
  }
  document.querySelectorAll('[data-bidirectional-spiral-field]').forEach(mount);
})();
