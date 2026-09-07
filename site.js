const canvas=document.getElementById('graphCanvas');
const title=document.getElementById('nodeTitle');
const text=document.getElementById('nodeText');
const tags=document.getElementById('nodeTags');

function installTimInterface(){
  if(document.getElementById('tim-interface')) return;
  const section=document.createElement('section');
  section.id='tim-interface';
  section.className='tim-interface';
  section.innerHTML=`
    <div class="tim-shell">
      <div class="tim-heading">
        <p class="section-label">TIM DOOLEY · THE INTERFACE</p>
        <h2>Ask the living archive.</h2>
        <p>Search the Potatoverse, the North Programme, and the relationships held inside the atlas.</p>
      </div>
      <div class="tim-stage">
        <div class="tim-avatar-wrap">
          <div class="tim-halo"></div>
          <div class="tim-avatar">
            <img src="assets/tim-dooley.png" alt="Tim Dooley avatar reference" onerror="this.style.display='none';this.nextElementSibling.style.display='grid'">
            <div class="tim-fallback" aria-hidden="true">TIM<br><span>DOOLEY</span></div>
            <div class="tim-mouth" aria-hidden="true"></div>
          </div>
          <div class="tim-speaking" id="timSpeaking">READY</div>
        </div>
        <div class="tim-console">
          <div class="tim-response" id="timResponse">I am the interface between the question and the archive. Ask me where a relationship leads.</div>
          <form class="tim-form" id="timForm">
            <label class="sr-only" for="timQuery">Ask Tim Dooley</label>
            <input id="timQuery" autocomplete="off" placeholder="Ask Tim Dooley something…">
            <button type="submit">Ask Tim <span>↗</span></button>
          </form>
          <div class="tim-actions">
            <button type="button" class="tim-small" id="timSpeakButton">Speak response</button>
            <button type="button" class="tim-small" id="timStopButton">Stop</button>
          </div>
          <p class="tim-note">The avatar is a visual interface. Answers can later be connected to a live AI service and the repository’s structured data.</p>
        </div>
      </div>
    </div>`;
  const graph=document.getElementById('graph');
  graph.parentNode.insertBefore(section,graph);

  const responseBox=document.getElementById('timResponse');
  const queryInput=document.getElementById('timQuery');
  const speaking=document.getElementById('timSpeaking');
  const mouth=document.querySelector('.tim-mouth');
  let utterance=null;

  function answer(question){
    const q=question.toLowerCase();
    if(q.includes('greenland')) return 'Greenland is an anchor in the North Axis architecture and a geographic bridge between the North Atlantic, Denmark, energy, infrastructure, and the wider European system.';
    if(q.includes('debt')||q.includes('france')||q.includes('belgium')) return 'The research layer tracks public debt as a relationship: obligations connect governments to budgets, interest costs, taxation, investment, and the productive economy.';
    if(q.includes('door')||q.includes('son')||q.includes('ladder')) return 'In the mythic layer, the Son becomes the Door and the Ladder: the centre through which the buried story becomes a path upward. This is symbolic architecture, not scientific evidence.';
    if(q.includes('north')) return 'The North Programme is the practical layer: map Europe through energy, finance, infrastructure, technology, labour, ownership, and strategic dependencies.';
    return 'That question belongs in the atlas. The next step is to connect it to nodes, relationships, sources, and dates so the answer can be examined rather than merely asserted.';
  }
  function speak(){
    if(!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    utterance=new SpeechSynthesisUtterance(responseBox.textContent);
    utterance.rate=.92; utterance.pitch=.72;
    utterance.onstart=()=>{speaking.textContent='SPEAKING';mouth.classList.add('moving')};
    utterance.onend=()=>{speaking.textContent='READY';mouth.classList.remove('moving')};
    window.speechSynthesis.speak(utterance);
  }
  document.getElementById('timForm').addEventListener('submit',event=>{
    event.preventDefault();
    const question=queryInput.value.trim();
    if(!question) return;
    responseBox.textContent=answer(question);
    speak();
  });
  document.getElementById('timSpeakButton').addEventListener('click',speak);
  document.getElementById('timStopButton').addEventListener('click',()=>{
    if('speechSynthesis' in window) window.speechSynthesis.cancel();
    speaking.textContent='READY'; mouth.classList.remove('moving');
  });
}

const positions={
  'european-union':[50,50], 'denmark':[28,30], 'greenland':[12,72],
  'france':[72,28], 'belgium':[76,70], 'energy-system':[38,76], 'finance-debt':[62,82],
  'potato-of-life':[50,50], 'father':[50,18], 'son':[50,82], 'door':[28,50], 'ladder':[72,50]
};

function selectNode(n){
  title.textContent=n.name;
  text.textContent=n.description || 'No description recorded yet.';
  tags.innerHTML=`<span class="tag">${n.type}</span><span class="tag">${n.layer}</span>`;
  document.querySelectorAll('.g-node').forEach(e=>e.classList.toggle('active',e.dataset.id===n.id));
}

async function loadGraph(){
  try{
    const response=await fetch('data/nodes.json');
    const payload=await response.json();
    const nodes=payload.nodes.filter(n=>positions[n.id]);
    nodes.forEach(n=>{
      const el=document.createElement('button');
      el.className='g-node'; el.dataset.id=n.id; el.textContent=n.name;
      const [x,y]=positions[n.id]; el.style.left=x+'%'; el.style.top=y+'%';
      el.addEventListener('click',()=>selectNode(n));
      canvas.appendChild(el);
    });
    const first=nodes.find(n=>n.id==='european-union')||nodes[0];
    if(first) selectNode(first);
  }catch(error){
    title.textContent='Graph data unavailable';
    text.textContent='The interface loaded, but the structured graph data could not be read. The repository remains the source of record.';
    console.error(error);
  }
}

installTimInterface();
loadGraph();
