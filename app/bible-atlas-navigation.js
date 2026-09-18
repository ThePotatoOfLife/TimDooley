(()=>{
'use strict';
const routes=[
{id:'stories',label:'Stories'},
{id:'roles',label:'People & Roles'},
{id:'symbols',label:'Symbols & Images'},
{id:'actions',label:'Movements & Changes'},
{id:'books',label:'Bible Books'},
{id:'timeline',label:'Project Journey'}
];
const curatedTopics={
 roles:[
  {id:'father-source',label:'Father / Source',query:'father source house'},
  {id:'son-man',label:'Son / Son of Man',query:'son son of man'},
  {id:'king',label:'King',query:'king kingship throne'},
  {id:'servant',label:'Servant',query:'servant service'},
  {id:'shepherd',label:'Shepherd',query:'shepherd'},
  {id:'gardener',label:'Gardener / Farmer',query:'gardener farmer vinedresser'},
  {id:'judge',label:'Judge',query:'judge judgment'},
  {id:'witness',label:'Witness',query:'witness'},
  {id:'prophet',label:'Prophet',query:'prophet prophecy'},
  {id:'priest',label:'Priest',query:'priest'},
  {id:'door-role',label:'Door / Gate',query:'door gate'},
  {id:'stone-role',label:'Stone / Foundation',query:'stone cornerstone foundation'},
  {id:'lamb',label:'Lamb',query:'lamb'},
  {id:'lion',label:'Lion',query:'lion'}
 ],
 symbols:[
  {id:'house',label:'House / Rooms / Dwelling',query:'house rooms dwelling'},
  {id:'door',label:'Door / Gate',query:'door gate'},
  {id:'ladder',label:'Ladder / Stairway',query:'ladder stairway'},
  {id:'tree-root',label:'Tree / Root / Branch',query:'tree root branch'},
  {id:'seed-grain',label:'Seed / Grain',query:'seed grain wheat'},
  {id:'bread-body',label:'Bread / Body / Table',query:'bread body table'},
  {id:'stone',label:'Stone / Cornerstone',query:'stone cornerstone'},
  {id:'lion-lamb',label:'Lion / Lamb',query:'lion lamb'},
  {id:'throne',label:'Throne / Seat / Footstool',query:'throne seat footstool'},
  {id:'river',label:'River / Water',query:'river water'},
  {id:'garden',label:'Garden / Fruit',query:'garden fruit'},
  {id:'eye-light',label:'Eye / Lamp / Light',query:'eye lamp light'},
  {id:'wheel',label:'Wheel / Chariot',query:'wheel chariot'},
  {id:'cloud',label:'Cloud / Coming',query:'cloud coming son of man'},
  {id:'north-zion',label:'North / Zion',query:'north zion'},
  {id:'city',label:'City / New Jerusalem',query:'new jerusalem city'},
  {id:'temple',label:'Temple',query:'temple'},
  {id:'measure',label:'Measure / Boundary / Cube',query:'measure boundary cube'},
  {id:'dog-boundary',label:'Dog / Outside / Boundary',query:'dog outside boundary'}
 ],
 actions:[
  {id:'open',label:'Open / Shut',query:'open shut'},
  {id:'pass',label:'Enter / Pass',query:'enter pass threshold'},
  {id:'carry',label:'Carry / Burden',query:'carry burden'},
  {id:'release',label:'Release',query:'release'},
  {id:'root',label:'Root / Plant',query:'root plant'},
  {id:'prune',label:'Prune / Fruit',query:'prune fruit'},
  {id:'flow',label:'Flow',query:'flow river'},
  {id:'feed',label:'Feed / Nourish',query:'feed bread nourish'},
  {id:'repair',label:'Repair / Restore',query:'repair restore'},
  {id:'judge',label:'Judge / Measure',query:'judge measure'},
  {id:'die',label:'Die / Rise / Return',query:'die rise return resurrection'},
  {id:'inherit',label:'Inherit / Adopt',query:'inherit adoption'},
  {id:'name',label:'Name / Recognize',query:'name recognize'},
  {id:'rejection-foundation',label:'Rejection → Foundation',query:'rejection cornerstone foundation'},
  {id:'descent-ascent',label:'Descent → Ascent',query:'descent ascent'},
  {id:'death-return',label:'Death → Waiting → Return',query:'death waiting return'},
  {id:'seed-multiplication',label:'Seed → Burial → Multiplication',query:'seed burial multiplication'},
  {id:'prison-elevation',label:'Pit / Prison → Elevation',query:'pit prison elevation'},
  {id:'exile-return',label:'Exile → Return → Dwelling',query:'exile return dwelling'},
  {id:'house-authority',label:'House → Key → Door → Authority',query:'house key door authority'},
  {id:'book-nations',label:'Book → Burden → Nations',query:'book burden nations'}
 ]
};
const bookOrder=['Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra','Nehemiah','Esther','Job','Psalms','Proverbs','Ecclesiastes','Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark','Luke','John','Acts','Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter','1 John','2 John','3 John','Jude','Revelation'];
const norm=v=>String(v||'').trim().toLowerCase();
const arr=v=>Array.isArray(v)?v:(v==null?[]:[v]);
const rowText=row=>[row.title,row.project_anchor,row.actor,...arr(row.biblical_refs),...arr(row.motifs),...arr(row.operators),...arr(row.mechanisms),...arr(row.biblical_scene_ids)].join(' ').toLowerCase();
function matchRoute(row,route,topic){
 const t=norm(topic); if(!t)return true;
 if(route==='books')return arr(row.biblical_refs).some(ref=>norm(ref).startsWith(t));
 if(route==='symbols')return arr(row.motifs).some(x=>norm(x).includes(t))||rowText(row).includes(t);
 if(route==='actions')return [...arr(row.operators),...arr(row.mechanisms)].some(x=>norm(x).includes(t))||rowText(row).includes(t);
 if(route==='roles')return [row.actor,...arr(row.roles),...arr(row.motifs)].some(x=>norm(x).includes(t))||rowText(row).includes(t);
 if(route==='stories')return [...arr(row.biblical_scene_ids),...arr(row.motifs),...arr(row.biblical_refs)].some(x=>norm(x).includes(t));
 if(route==='timeline')return rowText(row).includes(t);
 return rowText(row).includes(t);
}
function breadcrumbs(state={}){
 const route=routes.find(r=>r.id===state.route)||routes[0],out=[{kind:'route',id:route.id,label:route.label}];
 if(state.topic){const topic=(curatedTopics[state.route]||[]).find(item=>item.id===state.topic);out.push({kind:'topic',id:state.topic,label:topic?.label||window.BibleLanguage?.label(state.topic)||String(state.topic)})}
 if(state.id)out.push({kind:'relation',id:state.id,label:window.BibleLanguage?.humanizeId(state.id)||state.id});
 return out;
}
function relatedPaths(row){
 const out=[]; const push=(route,topic,label)=>{if(topic&&!out.some(x=>x.route===route&&x.topic===topic))out.push({route,topic,label})};
 arr(row.biblical_scene_ids).slice(0,2).forEach(x=>push('stories',x,window.BibleLanguage?.label(x)||x));
 arr(row.motifs).slice(0,3).forEach(x=>push('symbols',norm(x),x));
 arr(row.operators).slice(0,3).forEach(x=>push('actions',norm(x),x));
 const ref=arr(row.biblical_refs)[0]; if(ref){const book=String(ref).replace(/\s+\d.*$/,'');push('books',book,book)}
 return out.slice(0,6);
}
window.BibleAtlas={routes,curatedTopics,bookOrder,matchRoute,breadcrumbs,relatedPaths};
})();
