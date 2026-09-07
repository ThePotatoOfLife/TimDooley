const canvas=document.getElementById('graphCanvas');
const title=document.getElementById('nodeTitle');
const text=document.getElementById('nodeText');
const tags=document.getElementById('nodeTags');
const relationsBox=document.getElementById('nodeRelations');

const positions={
  source:[50,8],father:[50,17],"fathers-house":[50,26],heaven:[50,35],"throne-of-north":[50,44],ladder:[50,53],door:[50,62],son:[50,71],axis:[50,80],"tree-of-life":[50,89],plane:[25,80],roots:[18,92],"potato-of-life":[78,91],"tree-of-strife":[18,72],swamp:[8,58],"red-potato":[88,63],"blue-potato":[88,77],north:[14,20],east:[86,18],south:[14,36],west:[86,36],"north-axis":[14,50],"north-programme":[83,50],"european-economic-graph":[82,30],"european-union":[74,20],denmark:[66,10],greenland:[25,12],"kingdom-of-denmark":[32,4],france:[78,10],belgium:[88,13],"energy-system":[72,38],"finance-debt":[85,40]
};

function selectNode(n,relationships=[]){
  title.textContent=n.name;
  text.textContent=n.description||'No description recorded yet.';
  tags.innerHTML=`<span class="tag">${n.type}</span><span class="tag">${n.layer}</span>`;
  relationsBox.innerHTML='';
  const connected=relationships.filter(r=>r.source===n.id||r.target===n.id);
  connected.slice(0,12).forEach(r=>{
    const direction=r.source===n.id?'→':'←';
    const other=r.source===n.id?r.target:r.source;
    const item=document.createElement('div');
    item.className='relation-item';
    item.innerHTML=`<span>${direction}</span><b>${r.relationship}</b><small>${other}</small>`;
    relationsBox.appendChild(item);
  });
  document.querySelectorAll('.g-node').forEach(e=>e.classList.toggle('active',e.dataset.id===n.id));
}

async function loadGraph(){
  try{
    const [nodesResponse,relationsResponse]=await Promise.all([fetch('data/nodes.json'),fetch('data/relationships.json')]);
    const payload=await nodesResponse.json();
    const relationPayload=await relationsResponse.json();
    const nodes=payload.nodes.filter(n=>positions[n.id]);
    nodes.forEach(n=>{
      const el=document.createElement('button');
      el.className='g-node'; el.dataset.id=n.id; el.textContent=n.name;
      const [x,y]=positions[n.id]; el.style.left=x+'%'; el.style.top=y+'%';
      el.addEventListener('click',()=>selectNode(n,relationPayload.relationships));
      canvas.appendChild(el);
    });
    const first=nodes.find(n=>n.id==='source')||nodes[0];
    if(first) selectNode(first,relationPayload.relationships);
  }catch(error){
    title.textContent='Graph data unavailable';
    text.textContent='The interface loaded, but the structured graph data could not be read.';
    console.error(error);
  }
}

function installTimInterface(){
  if(document.getElementById('tim-interface')) return;
  const section=document.createElement('section'); section.id='tim-interface'; section.className='tim-interface';
  section.innerHTML=`<div class="tim-shell"><div class="tim-heading"><p class="section-label">TIM DOOLEY · THE INTERFACE</p><h2>Ask the living archive.</h2><p>Search the Potatoverse, the North Programme, and the relationships held inside the atlas.</p></div><div class="tim-stage"><div class="tim-avatar-wrap"><div class="tim-halo"></div><div class="tim-avatar"><img src="assets/tim-dooley.png" alt="Tim Dooley avatar reference" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'"><div class="tim-fallback" aria-hidden="true">TIM<br><span>DOOLEY</span></div><div class="tim-mouth" aria-hidden="true"></div></div><div class="tim-speaking" id="timSpeaking">READY</div></div><div class="tim-console"><div class="tim-response" id="timResponse">I am the interface between the question and the archive. Ask me where a relationship leads.</div><form class="tim-form" id="timForm"><label class="sr-only" for="timQuery">Ask Tim Dooley</label><input id="timQuery" autocomplete="off" placeholder="Ask Tim Dooley something…"><button type="submit">Ask Tim <span>↗</span></button></form><div class="tim-actions"><button type="button" class="tim-small" id="timSpeakButton">Speak response</button><button type="button" class="tim-small" id="timStopButton">Stop</button></div><p class="tim-note">The interface can later be connected to a live AI service; for now it uses the repository ontology locally.</p></div></div></div>`;
  const graph=document.getElementById('graph'); graph.parentNode.insertBefore(section,graph);
  const responseBox=document.getElementById('timResponse'),queryInput=document.getElementById('timQuery'),speaking=document.getElementById('timSpeaking'),mouth=document.querySelector('.tim-mouth');
  let utterance=null;
  function answer(question){
    const q=question.toLowerCase();
    if(q.includes('source')) return 'Source is the symbolic zero-point: undivided origin and possibility. The frame unfolds outward from Source into Father, House, Heaven and the living world.';
    if(q.includes('father')) return 'Father is the upper source-position. The Father is related to the Father’s House, Heaven and the Son within the mythological architecture.';
    if(q.includes('door')) return 'The Door is the threshold. Within the frame the Son embodies the Door, while the Ladder describes the path through the vertical architecture.';
    if(q.includes('tree')||q.includes('root')||q.includes('fruit')) return 'The Tree of Life is the living Axis: roots preserve origin and memory, the trunk preserves continuity, branches differentiate, fruit manifests, and seed renews the cycle. The Tree of Strife is its fragmented pattern.';
    if(q.includes('red')||q.includes('blue')||q.includes('potato')) return 'The Red Potato expresses creative outward Life; the Blue Potato expresses memory and contraction. They are complementary archetypes inside the Potato of Life.';
    if(q.includes('north')) return 'North is orientation. The North Axis is the project’s conceptual northward architecture, while the North Programme applies relationship-first research to Europe and its connected systems.';
    if(q.includes('graph')||q.includes('europe')) return 'The European Economic Graph maps relationships among states, companies, debt, ownership, finance, energy, infrastructure, trade, technology, research, labour and strategic dependencies.';
    if(q.includes('swamp')||q.includes('strife')) return 'The Swamp is the shadow-system metaphor: accumulated dysfunction, extraction, corruption, fear, institutional inertia and systems that consume the life they should serve.';
    return 'That question belongs in the frame. Connect it to nodes, relationships, evidence classes and dates so the answer can be examined rather than merely asserted.';
  }
  function speak(){if(!('speechSynthesis' in window))return;window.speechSynthesis.cancel();utterance=new SpeechSynthesisUtterance(responseBox.textContent);utterance.rate=.92;utterance.pitch=.72;utterance.onstart=()=>{speaking.textContent='SPEAKING';mouth.classList.add('moving')};utterance.onend=()=>{speaking.textContent='READY';mouth.classList.remove('moving')};window.speechSynthesis.speak(utterance)}
  document.getElementById('timForm').addEventListener('submit',e=>{e.preventDefault();const q=queryInput.value.trim();if(!q)return;responseBox.textContent=answer(q);speak()});
  document.getElementById('timSpeakButton').addEventListener('click',speak);
  document.getElementById('timStopButton').addEventListener('click',()=>{if('speechSynthesis'in window)window.speechSynthesis.cancel();speaking.textContent='READY';mouth.classList.remove('moving')});
}

installTimInterface();
loadGraph();
