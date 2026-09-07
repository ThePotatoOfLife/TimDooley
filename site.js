const nodes=[
 {id:'eu',name:'European Union',x:50,y:50,text:'A political and economic union whose single market links goods, services, capital and people. It is the central institutional node of the first European graph.',tags:['institution','single market','27 states']},
 {id:'denmark',name:'Denmark',x:28,y:30,text:'A northern European state and anchor in the working North Axis. Its economy, institutions, energy system and EU relationships form an important research node.',tags:['state','North Axis','EU']},
 {id:'greenland',name:'Greenland',x:12,y:72,text:'An autonomous territory within the Kingdom of Denmark. In the North Programme architecture it is a geographic, resource, Arctic and strategic node.',tags:['territory','Arctic','resources']},
 {id:'france',name:'France',x:72,y:28,text:'A major EU economy and priority case for the North Programme because of its fiscal scale, public expenditure structure, industrial base and strategic role in Europe.',tags:['state','EU','priority case']},
 {id:'belgium',name:'Belgium',x:76,y:70,text:'A highly integrated European economy and priority fiscal case. Its position also makes it important to infrastructure, institutions, trade and European finance.',tags:['state','EU','priority case']},
 {id:'energy',name:'Energy system',x:38,y:76,text:'Energy links resources, generation, grids, industry, households, trade and strategic autonomy. It is one of the graph\'s main cross-domain systems.',tags:['energy','infrastructure','dependency']},
 {id:'finance',name:'Finance & debt',x:62,y:82,text:'Government bonds, banks, funds, monetary institutions and capital markets connect public finances to the wider economy.',tags:['finance','debt','capital']}
];
const canvas=document.getElementById('graphCanvas');
const title=document.getElementById('nodeTitle'); const text=document.getElementById('nodeText'); const tags=document.getElementById('nodeTags');
function selectNode(n){title.textContent=n.name;text.textContent=n.text;tags.innerHTML=n.tags.map(t=>`<span class="tag">${t}</span>`).join('');document.querySelectorAll('.g-node').forEach(e=>e.classList.toggle('active',e.dataset.id===n.id));}
nodes.forEach(n=>{const el=document.createElement('button');el.className='g-node';el.dataset.id=n.id;el.textContent=n.name;el.style.left=n.x+'%';el.style.top=n.y+'%';el.addEventListener('click',()=>selectNode(n));canvas.appendChild(el)});
selectNode(nodes[0]);
