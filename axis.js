import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const $=id=>document.getElementById(id);
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x020403);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.01,100);
camera.position.set(3.4,1.5,4.2);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight);
renderer.outputColorSpace=THREE.SRGBColorSpace;
$('viewport').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true; controls.target.set(0,0,0); controls.minDistance=1.5; controls.maxDistance=8;
scene.add(new THREE.AmbientLight(0xffffff,.9));
const root=new THREE.Group(); scene.add(root);
const C={life:0x64ff86,serpent:0xd6a94d,spirit:0x9f8cff,matter:0x8d6b42,overlap:0x58e0b0,plane:0x80d8ff,node:0xe8ffe9,edge:0x315f3d,door:0xffffff};

function line(points,color,opacity=1){const g=new THREE.BufferGeometry().setFromPoints(points);root.add(new THREE.Line(g,new THREE.LineBasicMaterial({color,transparent:opacity<1,opacity})));}
function ellipsoid(center,radii,color,opacity){const g=new THREE.SphereGeometry(1,48,24);const m=new THREE.MeshBasicMaterial({color,transparent:true,opacity,depthWrite:false,side:THREE.DoubleSide});const o=new THREE.Mesh(g,m);o.position.set(...center);o.scale.set(...radii);root.add(o);const w=new THREE.LineSegments(new THREE.WireframeGeometry(g),new THREE.LineBasicMaterial({color,transparent:true,opacity:.13}));w.position.copy(o.position);w.scale.copy(o.scale);root.add(w);}

ellipsoid([0,.48,0],[.74,.82,.74],C.spirit,.055);
ellipsoid([0,-.48,0],[.86,.82,.86],C.matter,.055);

const verts=[],inds=[],ny=64,nr=80;
const R=y=>.30+.76*(1-Math.pow(Math.abs(y),1.65));
for(let j=0;j<=ny;j++){const y=-1+2*j/ny,r=R(y);for(let i=0;i<nr;i++){const a=2*Math.PI*i/nr;verts.push(r*Math.cos(a),y,r*Math.sin(a));}}
for(let j=0;j<ny;j++)for(let i=0;i<nr;i++){const a=j*nr+i,b=j*nr+(i+1)%nr,c=(j+1)*nr+(i+1)%nr,d=(j+1)*nr+i;inds.push(a,b,d,b,c,d);}
const envGeo=new THREE.BufferGeometry();envGeo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));envGeo.setIndex(inds);envGeo.computeVertexNormals();
root.add(new THREE.Mesh(envGeo,new THREE.MeshBasicMaterial({color:0x17351f,transparent:true,opacity:.075,side:THREE.DoubleSide,depthWrite:false})));

// Door = origin / bifurcation. Tree of Life rises; Hermes/Serpent descends.
const door=new THREE.Mesh(new THREE.TorusGeometry(.075,.018,16,48),new THREE.MeshBasicMaterial({color:C.door}));door.rotation.x=Math.PI/2;root.add(door);
const spine=[];for(let i=0;i<=120;i++){const y=-1.18+2.36*i/120;spine.push(new THREE.Vector3(.025*Math.sin(y*8),y,.025*Math.cos(y*8)));}line(spine,C.serpent,.9);
const trunk=[];for(let i=0;i<=55;i++)trunk.push(new THREE.Vector3(0,.02+.96*i/55,0));line(trunk,C.life,.95);
for(let b=0;b<9;b++){const y=.20+b*.09,s=b%2?1:-1;line([new THREE.Vector3(0,y,0),new THREE.Vector3(s*(.12+b*.045),y+.14,s*.025),new THREE.Vector3(s*(.30+b*.045),y+.27,s*(.07+b*.02))],C.life,.7);}
for(let k=0;k<5;k++){const pts=[];for(let i=0;i<=60;i++){const a=i/60*Math.PI*2;const y=-.10-k*.18-.13*i/60;pts.push(new THREE.Vector3(.095*Math.sin(a),y,.095*Math.cos(a)));}line(pts,C.serpent,.55);}
line([new THREE.Vector3(-1.18,0,0),new THREE.Vector3(1.18,0,0)],C.overlap,.16);
line([new THREE.Vector3(0,0,-1.18),new THREE.Vector3(0,0,1.18)],C.overlap,.16);

const tree=await loadJson('data/tree.json');
const nodeData=await loadJson('data/nodes.json');
const relData=await loadJson('data/relationships.json');
const records=Array.isArray(nodeData.nodes)?nodeData.nodes:[];
const byId=new Map(records.map(n=>[n.id,n]));
const canonical=new Map();
for(const level of tree.levels||[])for(const id of level.children||[])canonical.set(id,level.id);

const anchors={
 source:[0,.92,0],father:[-.30,.80,.05],'fathers-house':[.30,.72,.05],heaven:[0,.64,-.28],'throne-of-north':[0,.55,.25],
 ladder:[-.18,.42,0],axis:[0,.18,0],door:[0,0,0],'narrow-gate':[.08,.06,.03],vessel:[-.10,.04,.03],
 'pineal-gland':[.14,.03,.02],son:[0,.10,.10],thomas:[-.20,.16,.08],twin:[.20,.16,.08],lion:[-.28,.28,.08],
 'lion-of-judah':[.28,.28,.08],'jesus-christ':[0,.22,.22],'son-of-man':[0,.32,-.20],
 'tree-of-life':[0,.52,0],roots:[0,-.18,.02],trunk:[0,.30,0],branches:[.20,.55,0],leaves:[.40,.76,0],fruit:[.48,.62,.05],seed:[-.42,.48,.04],
 'tree-of-strife':[0,-.48,0],strife:[.38,-.40,.12],swamp:[-.40,-.72,.12],mud:[.20,-.88,.18],drain:[-.22,-.78,-.16],fear:[.48,-.55,-.05],anger:[-.50,-.50,-.05],
 'potato-of-life':[0,-.12,.38],potatoism:[.34,-.18,.34],'red-potato':[-.34,.18,.28],'blue-potato':[.34,-.30,.28],spudlight:[-.18,.28,.30],
 north:[0,.72,-.58],south:[0,-.72,-.58],east:[.65,0,0],west:[-.65,0,0],plane:[0,0,0],
 matter:[0,-.30,-.42],biology:[.35,-.25,-.25],people:[-.35,-.25,-.25],families:[-.45,-.05,-.20],animals:[.45,-.05,-.20],places:[.55,-.45,-.15],
 nations:[-.55,-.45,-.15],societies:[-.30,-.58,-.35],institutions:[.30,-.58,-.35],laws:[0,-.65,-.42],economies:[-.15,-.48,-.55],technology:[.38,-.42,-.48],infrastructure:[-.38,-.42,-.48],
 history:[-.55,-.15,-.42],war:[.55,-.22,-.40],trade:[-.62,-.30,-.32],money:[.62,-.30,-.32],ownership:[-.20,-.70,-.50],obligations:[.20,-.70,-.50],alliances:[0,-.52,-.62],
 'european-economic-graph':[.12,-.52,-.60],'north-programme':[0,-.28,-.68],
 denmark:[-.10,-.34,-.70],greenland:[.10,-.12,-.72],canada:[-.28,-.12,-.68],'european-union':[.30,-.38,-.66],iceland:[-.10,.02,-.72],britain:[.40,-.05,-.65],ukraine:[.40,-.45,-.55],turkey:[.20,-.62,-.48]
};

const nodes=new Map(),nodeObjects=[];
function fallback(id,index,total){
  const h=hash(id), angle=(h%100000)/100000*Math.PI*2, band=(Math.floor(h/100000)%1000)/1000;
  const canonicalLevel=canonical.get(id);
  const levelIndex=(tree.levels||[]).findIndex(l=>l.id===canonicalLevel);
  const y=levelIndex>=0 ? 1-2*(levelIndex+.5)/10 : (h%2000)/1000-1;
  const radius=.20+.55*Math.sqrt(Math.max(.02,band));
  return new THREE.Vector3(Math.cos(angle)*radius,y,Math.sin(angle)*radius);
}
function hash(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}
function position(id,index,total){if(anchors[id])return new THREE.Vector3(...anchors[id]);return fallback(id,index,total);}
function addNode(n,index,total){const p=position(n.id,index,total);let color=p.y>=.03?C.life:C.serpent;if(Math.abs(p.y)<.12)color=C.overlap;if(n.id==='door')color=C.door;if(n.id==='tree-of-life')color=C.life;if(['tree-of-strife','swamp','mud','fear','anger','drain'].includes(n.id))color=C.serpent;const size=n.id==='door'?.075:(['tree-of-life','tree-of-strife','son'].includes(n.id)?.055:.028);const o=new THREE.Mesh(new THREE.SphereGeometry(size,14,10),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.95}));o.position.copy(p);o.userData={id:n.id,name:n.name||n.id};root.add(o);nodes.set(n.id,o);nodeObjects.push(o);}
records.forEach((n,i)=>addNode(n,i,records.length));

for(const e of (Array.isArray(relData.relationships)?relData.relationships:[])){
  const a=nodes.get(e.source),b=nodes.get(e.target);if(!a||!b)continue;
  line([a.position,b.position],C.edge,.20);
}

// A movable horizontal analytical plane. Wheel changes its signed y position.
const planeMesh=new THREE.Mesh(new THREE.PlaneGeometry(2.15,2.15),new THREE.MeshBasicMaterial({color:C.plane,transparent:true,opacity:.025,side:THREE.DoubleSide,depthWrite:false}));
planeMesh.rotation.x=-Math.PI/2;root.add(planeMesh);
const planeEdge=new THREE.LineSegments(new THREE.EdgesGeometry(planeMesh.geometry),new THREE.LineBasicMaterial({color:C.plane,transparent:true,opacity:.25}));planeEdge.rotation.copy(planeMesh.rotation);root.add(planeEdge);
let planeY=0;
function updatePlane(){planeMesh.position.y=planeY;planeEdge.position.y=planeY;const el=$('plane-status');if(el)el.textContent='PLANE y='+planeY.toFixed(2);}
updatePlane();
addEventListener('wheel',e=>{planeY=Math.max(-1,Math.min(1,planeY-e.deltaY*.001));updatePlane();},{passive:true});

const ray=new THREE.Raycaster(),ptr=new THREE.Vector2();
renderer.domElement.addEventListener('pointermove',e=>{ptr.x=e.clientX/innerWidth*2-1;ptr.y=-(e.clientY/innerHeight)*2+1;ray.setFromCamera(ptr,camera);const hit=ray.intersectObjects(nodeObjects,false)[0];renderer.domElement.style.cursor=hit?'pointer':'grab';});
renderer.domElement.addEventListener('click',e=>{ptr.x=e.clientX/innerWidth*2-1;ptr.y=-(e.clientY/innerHeight)*2+1;ray.setFromCamera(ptr,camera);const hit=ray.intersectObjects(nodeObjects,false)[0];if(!hit)return;const n=hit.object.userData;const el=$('selected');if(el)el.textContent=n.name+' ['+n.id+']';location.href='node.html?id='+encodeURIComponent(n.id);});

$('load-status').textContent=records.length+' NODES';
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);}
addEventListener('resize',resize);
(function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera);})();

async function loadJson(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(path+' HTTP '+r.status);return r.json();}
