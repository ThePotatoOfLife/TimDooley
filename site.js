const canvas=document.getElementById('graphCanvas');
const title=document.getElementById('nodeTitle');
const text=document.getElementById('nodeText');
const tags=document.getElementById('nodeTags');

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

loadGraph();
