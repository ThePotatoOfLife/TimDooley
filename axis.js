import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const scene=new THREE.Scene(); scene.background=new THREE.Color(0x020403);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.01,100); camera.position.set(3.4,1.5,4.2);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(innerWidth,innerHeight); renderer.outputColorSpace=THREE.SRGBColorSpace; $('viewport').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.target.set(0,0,0); controls.minDistance=1.5; controls.maxDistance=8;
scene.add(new THREE.AmbientLight(0xffffff,.8));
const root=new THREE.Group(); scene.add(root);
const C={life:0x64ff86,serpent:0xd6a94d,spirit:0x9f8cff,matter:0x8d6b42,overlap:0x58e0b0,plane:0x80d8ff,node:0xe8ffe9,edge:0x315f3d,door:0xffffff};

function ellipsoid(center,radii,color,opacity){const g=new THREE.SphereGeometry(1,64,32);const m=new THREE.MeshBasicMaterial({color,transparent:true,opacity,depthWrite:false,side:THREE.DoubleSide});const o=new THREE.Mesh(g,m);o.position.set(...center);o.scale.set(...radii);root.add(o);const w=new THREE.LineSegments(new THREE.WireframeGeometry(g),new THREE.LineBasicMaterial({color,transparent:true,opacity:.16}));w.position.copy(o.position);w.scale.copy(o.scale);root.add(w)}
ellipsoid([0,.48,0],[.74,.82,.74],C.spirit,.055); ellipsoid([0,-.48,0],[.86,.82,.86],C.matter,.055);

// Hourglass-like potato envelope: x²+z²=r(y)².
const verts=[],inds=[],ny=64,nr=80; const R=y=>.30+.76*(1-Math.pow(Math.abs(y),1.65));
for(let j=0;j<=ny;j++){const y=-1+2*j/ny,r=R(y);for(let i=0;i<nr;i++){const a=2*Math.PI*i/nr;verts.push(r*Math.cos(a),y,r*Math.sin(a))}}
for(let j=0;j<ny;j++)for(let i=0;i<nr;i++){const a=j*nr+i,b=j*nr+(i+1)%nr,c=(j+1)*nr+(i+1)%nr,d=(j+1)*nr+i;inds.push(a,b,d,b,c,d)}
const envGeo=new THREE.BufferGeometry();envGeo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));envGeo.setIndex(inds);envGeo.computeVertexNormals();root.add(new THREE.Mesh(envGeo,new THREE.MeshPhysicalMaterial({color:0x17351f,transparent:true,opacity:.09,roughness:.9,side:THREE.DoubleSide,depthWrite:false})));root.add(new THREE.LineSegments(new THREE.WireframeGeometry(envGeo),new THREE.LineBasicMaterial({color:C.life,transparent:true,opacity:.045})));

// Door is the origin. The Tree of Life grows upward; Hermes/serpent descends.
const door=new THREE.Mesh(new THREE.TorusGeometry(.075,.018,16,48),new THREE.MeshBasicMaterial({color:C.door}));door.rotation.x=Math.PI/2;root.add(door);
const spinePts=[];for(let i=0;i<=100;i++){const y=-1.15+2.3*i/100;spinePts.push(new THREE.Vector3(.035*Math.sin(y*7),y,.035*Math.cos(y*7)))}
root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(spinePts),new THREE.LineBasicMaterial({color:C.serpent,transparent:true,opacity:.9})));

// Tree of Life: trunk starts at Door and branches upward.
const lifeTrunk=[];for(let i=0;i<=45;i++){const y=.03+.92*i/45;lifeTrunk.push(new THREE.Vector3(0,y,0))}root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(lifeTrunk),new THREE.LineBasicMaterial({color:C.life,transparent:true,opacity:.95})));
for(let b=0;b<7;b++){const y=.25+b*.095,side=b%2?1:-1;const p=[new THREE.Vector3(0,y,0),new THREE.Vector3(side*(.16+b*.055),y+.18,side*(.05+b*.025)),new THREE.Vector3(side*(.34+b*.07),y+.29,side*(.10+b*.03))];root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(p),new THREE.LineBasicMaterial({color:C.life,transparent:true,opacity:.75})))}

// Serpent coils around the downward Axis.
for(let k=0;k<5;k++){const pts=[];for(let i=0;i<=50;i++){const y=-.04-(k+.15)*.18-.14*i/50;const a=i/50*Math.PI*2;pts.push(new THREE.Vector3(.10*Math.sin(a),y,.10*Math.cos(a)))}root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),new THREE.LineBasicMaterial({color:C.serpent,transparent:true,opacity:.6})))}

// Cardinal directions through the Door/overlap.
for(const p of [[[ -1.18,0,0],[1.18,0,0]],[[0,0,-1.18],[0,0,1.18]]]){root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(p.map(v=>new THREE.Vector3(...v))),new THREE.LineBasicMaterial({color:C.overlap,transparent:true,opacity:.13})))}

const nodes=new Map(),nodeObjects=[];
function place(level,idx,count){const t=(level+.5)/10;const y=1-2*t;const n=Math.max(1,count);const theta=2*Math.PI*idx/n+level*.61;const radius=Math.min(R(y)*.72,.16+.52*Math.sqrt((idx+1)/n));return new THREE.Vector3(radius*Math.cos(theta),y,radius*Math.sin(theta))}
function addNode(id,name,level,idx,count){const p=place(level,idx,count);const isDoor=id==='door',isLife=id==='tree-of-life',isSerpent=['hermes','serpent'].includes(id);let color=p.y>.05?C.life:C.serpent;if(Math.abs(p.y)<.10)color=C.overlap;if(isDoor)color=C.door;if(isLife)color=C.life;if(isSerpent)color=C.serpent;const size=isDoor?.075:(isLife||isSerpent?.05:.032);const o=new THREE.Mesh(new THREE.SphereGeometry(size,16,10),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.95}));o.position.copy(p);o.userData={id,name};root.add(o);nodes.set(id,o);nodeObjects.push(o)}
async function json(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error(path);return r.json()}
const tree=await json('data/tree.json'),data=await json('data/nodes.json');const byId=new Map((data.nodes||[]).map(n=>[n.id,n]));
(tree.levels||[]).forEach((l,li)=>(l.children||[]).forEach((id,i,a)=>addNode(id,byId.get(id)?.name||id,li,i,a.length)));
// Add structural records even if they are not direct canonical children.
for(const id of ['father','fathers-house','heaven','axis','door','son','tree-of-life','tree-of-strife','roots','plane','hermes','serpent','eyes','eye','children','father','source'])if(!nodes.has(id)&&byId.has(id)){const n=byId.get(id);const y=id==='door'?0:id==='tree-of-life'?.52:id==='roots'?-0.72:id==='plane'?.0:(n.type==='concept'?.25:-.25);const p=new THREE.Vector3(.24*Math.cos(id.length),y,.24*Math.sin(id.length));const o=new THREE.Mesh(new THREE.SphereGeometry(id==='door'?.07:.035,16,10),new THREE.MeshBasicMaterial({color:y>=0?C.life:C.serpent}));o.position.copy(p);o.userData={id,name:n.name};root.add(o);nodes.set(id,o);nodeObjects.push(o)}

try{const rel=await json('data/relationships.json');for(const e of rel.relationships||[]){const a=nodes.get(e.source||e.from),b=nodes.get(e.target||e.to);if(!a||!b)continue;const g=new THREE.BufferGeometry().setFromPoints([a.position,b.position]);root.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:C.edge,transparent:true,opacity:.22})))} }catch(e){}

// Arbitrary analytical plane, initially at Door. Drag with wheel to move through y.
const plane=new THREE.Mesh(new THREE.PlaneGeometry(2.15,2.15),new THREE.MeshBasicMaterial({color:C.plane,transparent:true,opacity:.025,side:THREE.DoubleSide,depthWrite:false}));plane.rotation.x=-Math.PI/2;root.add(plane);const pe=new THREE.LineSegments(new THREE.EdgesGeometry(plane.geometry),new THREE.LineBasicMaterial({color:C.plane,transparent:true,opacity:.22}));pe.rotation.copy(plane.rotation);root.add(pe);
let planeY=0;addEventListener('wheel',e=>{planeY=Math.max(-1,Math.min(1,planeY-e.deltaY*.001));plane.position.y=planeY;pe.position.y=planeY;$('plane-status').textContent='PLANE y='+planeY.toFixed(2)},{passive:true});

const ray=new THREE.Raycaster(),ptr=new THREE.Vector2();renderer.domElement.addEventListener('click',e=>{ptr.x=e.clientX/innerWidth*2-1;ptr.y=-(e.clientY/innerHeight)*2+1;ray.setFromCamera(ptr,camera);const hit=ray.intersectObjects(nodeObjects,false)[0];if(!hit)return;const n=hit.object.userData;$('selected').textContent=n.name+'  ['+n.id+']';location.href='node.html?id='+encodeURIComponent(n.id)});
$('load-status').textContent=nodeObjects.length+' NODES';
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}addEventListener('resize',resize);
(function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera)})();
