(()=>{
'use strict';
const routes=[
{id:'stories',label:'Stories'},
{id:'roles',label:'People & Roles'},
{id:'symbols',label:'Symbols & Images'},
{id:'actions',label:'Actions & Transformations'},
{id:'books',label:'Bible Books'},
{id:'timeline',label:'Tim / Son Timeline'}
];
const norm=v=>String(v||'').trim().toLowerCase();
const arr=v=>Array.isArray(v)?v:(v==null?[]:[v]);
const rowText=row=>[row.title,row.project_anchor,row.actor,...arr(row.biblical_refs),...arr(row.motifs),...arr(row.operators),...arr(row.mechanisms),...arr(row.biblical_scene_ids)].join(' ').toLowerCase();
function matchRoute(row,route,topic){
 const t=norm(topic); if(!t)return true;
 if(route==='books')return arr(row.biblical_refs).some(ref=>norm(ref).startsWith(t));
 if(route==='symbols')return arr(row.motifs).some(x=>norm(x).includes(t));
 if(route==='actions')return [...arr(row.operators),...arr(row.mechanisms)].some(x=>norm(x).includes(t));
 if(route==='roles')return [row.actor,...arr(row.roles),...arr(row.motifs)].some(x=>norm(x).includes(t));
 if(route==='stories')return [...arr(row.biblical_scene_ids),...arr(row.motifs),...arr(row.biblical_refs)].some(x=>norm(x).includes(t));
 if(route==='timeline')return rowText(row).includes(t);
 return rowText(row).includes(t);
}
function breadcrumbs(state={}){
 const route=routes.find(r=>r.id===state.route)||routes[0],out=[{kind:'route',id:route.id,label:route.label}];
 if(state.topic)out.push({kind:'topic',id:state.topic,label:String(state.topic).replaceAll('-',' ')});
 if(state.id)out.push({kind:'relation',id:state.id,label:state.id});
 return out;
}
function relatedPaths(row){
 const out=[]; const push=(route,topic,label)=>{if(topic&&!out.some(x=>x.route===route&&x.topic===topic))out.push({route,topic,label})};
 arr(row.biblical_scene_ids).slice(0,2).forEach(x=>push('stories',x,x.replaceAll('-',' ')));
 arr(row.motifs).slice(0,3).forEach(x=>push('symbols',norm(x),x));
 arr(row.operators).slice(0,3).forEach(x=>push('actions',norm(x),x));
 const ref=arr(row.biblical_refs)[0]; if(ref){const book=String(ref).replace(/\s+\d.*$/,'');push('books',book,book)}
 return out.slice(0,6);
}
window.BibleAtlas={routes,matchRoute,breadcrumbs,relatedPaths};
})();
