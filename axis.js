import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x030605);
const camera=new THREE.PerspectiveCamera(42,innerWidth/innerHeight,.01,100);
camera.position.set(2.9,1.25,3.8);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight); renderer.outputColorSpace=THREE.SRGBColorSpace;
$('viewport').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; controls.dampingFactor=.06; controls.target.set(0,0,0); controls.minDistance=1.8; controls.maxDistance=8;
scene.add(new THREE.AmbientLight(0xffffff,.7));
const key=new THREE.PointLight(0xffffff,2.2,8); key.position.set(2,3,3); scene.add(key);

const root=new THREE.Group(); scene.add(root);
const COLORS={spirit:0xa58cff,matter:0xd9a14b,overlap:0x55e0b5,axis:0x35ff68,plane:0x8ad8ff,node:0xd9ffdc,edge:0x3a7548};

function ellipse(center,radii,color,opacity=.10){
 const g=new THREE.SphereGeometry(1,64,32); const m=new THREE.MeshBasicMaterial({color,transparent:true,opacity,depthWrite:false,side:THREE.DoubleSide});
 const mesh=new THREE.Mesh(g,m); mesh.position.set(...center); mesh.scale.set(...radii); root.add(mesh);
 const wire=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.SphereGeometry(1,32,16)),new THREE.LineBasicMaterial({color,transparent:true,opacity:.28})); wire.position.copy(mesh.position); wire.scale.copy(mesh.scale); root.add(wire); return mesh;
}
ellipse([0,.43,0],[.68,.78,.68],COLORS.spirit,.075);
ellipse([0,-.43,0],[.82,.78,.82],COLORS.matter,.075);

// Organic hourglass envelope: x²+z²=r(y)², sampled as a smooth surface.
function envelope(){const verts=[],inds=[];const ny=56,nr=72;const radius=y=>.34+.72*(1-Math.pow(Math.abs(y),1.7));for(let j=0;j<=ny;j++){const y=-1+2*j/ny,r=radius(y);for(let i=0;i<nr;i++){const a=2*Math.PI*i/nr;verts.push(r*Math.cos(a),y,r*Math.sin(a));}}for(let j=0;j<ny;j++)for(let i=0;i<nr;i++){const a=j*nr+i,b=j*nr+(i+1)%nr,c=(j+1)*nr+(i+1)%nr,d=(j+1)*nr+i;inds.push(a,b,d,b,c,d)}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geo.setIndex(inds);geo.computeVertexNormals();const mesh=new THREE.Mesh(geo,new THREE.MeshPhysicalMaterial({color:0x17351f,transparent:true,opacity:.13,roughness:.8,metalness:.05,side:THREE.DoubleSide,depthWrite:false}));root.add(mesh);const wire=new THREE.LineSegments(new THREE.WireframeGeometry(geo),new THREE.LineBasicMaterial({color:COLORS.axis,transparent:true,opacity:.07}));root.add(wire)}
envelope();

// The continuous Axis / Spine: x=z=0, y∈[-1,1].
const spineGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-1.18,0),new THREE.Vector3(0,1.18,0)]);
root.add(new THREE.Line(spineGeo,new THREE.LineBasicMaterial({color:COLORS.axis,transparent:true,opacity:.9})));

// Cardinal crosshair through the overlap.
for(const pts of [[[-1.25,0,0],[1.25,0,0]],[[0,0,-1.25],[0,0,1.25]]]){const g=new THREE.BufferGeometry().setFromPoints(pts.map(p=>new THREE.Vector3(...p)));root.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:COLORS.axis,transparent:true,opacity:.16})))}

const nodes=new Map(), nodeObjects=[]; let relationships=[];
function positionFor(levelIndex,childIndex,count){const t=(levelIndex+.5)/10;const y=1-2*t;const phase=levelIndex*Math.PI*.37;const theta=2*Math.PI*(childIndex/Math.max(1,count))+phase;const rho=Math.min(.76,.18+.48*Math.sqrt((childIndex+1)/Math.max(1,count)));return new THREE.Vector3(rho*Math.cos(theta),y,rho*Math.sin(theta))}
function addNode(id,name,levelIndex,childIndex,count){const p=positionFor(levelIndex,childIndex,count);const inOverlap=Math.abs(p.y)<.22;const color=inOverlap?COLORS.overlap:(p.y>0?COLORS.spirit:COLORS.matter);const g=new THREE.SphereGeometry(inOverlap?.042:.032,16,10);const m=new THREE.MeshBasicMaterial({color,transparent:true,opacity:.95});const o=new THREE.Mesh(g,m);o.position.copy(p);o.userData={id,name,levelIndex};root.add(o);nodes.set(id,o);nodeObjects.push(o);}

async function json(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw Error(path+' '+r.status);return r.json()}
const tree=await json('data/tree.json');
const data=await json('data/nodes.json');
const byId=new Map((data.nodes||[]).map(n=>[n.id,n]));
(tree.levels||[]).forEach((level,li)=>(level.children||[]).forEach((id,ci,arr)=>addNode(id,byId.get(id)?.name||id,li,ci,arr.length)));

// Repository relationships become 3D graph edges when both records have positions.
try{const rel=await json('data/relationships.json');relationships=rel.relationships||[];}catch{}
for(const e of relationships){const a=nodes.get(e.from),b=nodes.get(e.to);if(!a||!b)continue;const g=new THREE.BufferGeometry().setFromPoints([a.position,b.position]);root.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:COLORS.edge,transparent:true,opacity:.20})))}

// A movable analytical plane. Default is y=0, the overlap slice.
const plane=new THREE.Mesh(new THREE.PlaneGeometry(2.25,2.25),new THREE.MeshBasicMaterial({color:COLORS.plane,transparent:true,opacity:.035,side:THREE.DoubleSide,depthWrite:false}));plane.rotation.x=-Math.PI/2;root.add(plane);
const planeEdge=new THREE.LineSegments(new THREE.EdgesGeometry(plane.geometry),new THREE.LineBasicMaterial({color:COLORS.plane,transparent:true,opacity:.28}));planeEdge.rotation.copy(plane.rotation);root.add(planeEdge);

const raycaster=new THREE.Raycaster(), pointer=new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown',ev=>{pointer.x=ev.clientX/innerWidth*2-1;pointer.y=-(ev.clientY/innerHeight)*2+1;raycaster.setFromCamera(pointer,camera);const hits=raycaster.intersectObjects(nodeObjects,false);if(!hits.length)return;const n=hits[0].object.userData;$('selected').innerHTML=`<span style="color:#35ff68">${esc(n.name)}</span><br>${esc(n.id)}`;setTimeout(()=>{location.href='node.html?id='+encodeURIComponent(n.id)},180)},{passive:true});

$('load-status').textContent=`${nodeObjects.length} NODES`;
function resize(){camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)}addEventListener('resize',resize);
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera)}animate();
