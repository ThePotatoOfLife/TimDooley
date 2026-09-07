/* The Frame — link layer and interactive views.
   This file deliberately does not redraw or reorder the tree. It works FROM the
   existing architecture and gives each child a stable route into the record layer. */

const levelTitle=document.getElementById('levelTitle');
const planeDetail=document.getElementById('planeDetail');
const levelDescriptions={
  33:'Orientation: the current coordinate system and the questions used to organize the repository.',
  32:'Systems: connected structures such as economies, ecosystems, energy networks and institutions.',
  31:'Institutions: organizations, governments, companies, laws and formal arrangements.',
  30:'Entities: identifiable people, places, organizations, objects and concepts.',
  29:'Objects: specific records, assets, documents, measurements and material things.',
  28:'Events: dated occurrences, changes, transactions, decisions and historical moments.',
  27:'Evidence: sources, observations, calculations, uncertainty and provenance.'
};

document.querySelectorAll('.level').forEach(level=>{
  level.addEventListener('click',()=>{
    document.querySelectorAll('.level').forEach(item=>item.classList.remove('selected'));
    level.classList.add('selected');
    const value=level.dataset.level;
    if(levelTitle) levelTitle.textContent=`Level ${value} · ${level.querySelector('span').textContent}`;
    if(planeDetail) planeDetail.textContent=levelDescriptions[value]||'A level in the current repository coordinate system.';
  });
});

document.querySelectorAll('.plane-card').forEach(card=>{
  card.addEventListener('click',()=>{
    document.querySelectorAll('.plane-card').forEach(item=>item.classList.remove('selected'));
    card.classList.add('selected');
    if(planeDetail) planeDetail.textContent=`${card.dataset.name}: this dimension becomes a view across the records at the selected level. The same information can be reordered by geography, scale, time, importance, relationships or evidence.`;
  });
});

// Existing tree first; links are added without changing its order or hierarchy.
const knownIds={
  'Source':'source','Father':'father',"Father's House":'fathers-house','Heaven':'heaven','Throne':'throne-of-north','North of North':'north-axis','Origin':'source','Creator / Creation':'creation',
  'Father / Son':'father-son-relationship','Heaven / Earth':'heaven-earth','Spirit / Matter':'spirit-matter','Life / Death':'life-death','Above / Below':'above-below','Light / Darkness':'light-darkness','Identity / Non-identity':'identity-nonidentity','Distance':'distance',
  'Axis':'axis','Ladder':'ladder','Levels':'levels','Spine':'spine','33 Levels':'33-levels','North':'north','South':'south','East':'east','West':'west','Ascent':'ascent','Descent':'descent','Mountain':'mountain','North Gate':'north-gate',
  'Door':'door','Narrow Gate':'narrow-gate','Vessel':'vessel','Interface':'interface','Pineal Gland':'pineal-gland','Experience':'experience','Perception':'perception','Passage':'passage',
  'Son':'son','Son of Man':'son-of-man','Thomas':'thomas','Twin':'twin','Lion':'lion','Lion of Judah':'lion-of-judah','Jesus Christ':'jesus-christ','Death':'death','Crucifixion':'crucifixion','Christmas':'christmas','North Pole':'north-pole','Transformation':'transformation','Son → Door':'door','Son → Ladder':'ladder',
  'Roots':'roots','Trunk':'trunk','Branches':'branches','Leaves':'leaves','Fruit':'fruit','Life':'life','Growth':'growth','Memory':'memory','Renewal':'renewal','Love':'love','Light':'light','Creation':'creation',
  'Strife':'strife','Swamp':'swamp','Mud':'mud','Drain':'drain','Fear':'fear','Anger':'anger','Exploitation':'exploitation','Stagnation':'stagnation','Fragmentation':'fragmentation','False Structures':'false-structures','Loss of Connection':'loss-of-connection','Return':'return',
  'Potato of Life':'potato-of-life','Potatoism':'potatoism','Red Potato':'red-potato','Blue Potato':'blue-potato','Spudlight':'spudlight','Potato Bank':'potato-bank','Cube':'cube','Moon Cube':'moon-cube','Body':'body','World':'world','Absurdity':'absurdity',
  'Matter':'matter','Biology':'biology','People':'people','Families':'families','Animals':'animals','Places':'places','Nations':'nations','Kingdoms':'kingdoms','Societies':'societies','Institutions':'institutions','Laws':'laws','Economies':'economies','Technology':'technology','Infrastructure':'infrastructure','History':'history','War':'war','Trade':'trade','Money':'money','Ownership':'ownership','Obligations':'obligations','Alliances':'alliances',
  'North Axis':'north-axis','Denmark':'denmark','Greenland':'greenland','Canada':'canada','Europe':'european-union','Iceland':'iceland','Britain':'britain','Ukraine':'ukraine','Turkey':'turkey','European Economic Graph':'european-economic-graph','One Economic Field':'one-economic-field','Many Nations':'many-nations','Constitutions':'constitutions','Public Finance':'public-finance','Debt':'finance-debt','Energy':'energy-system','Industry':'industry','Research':'research','Labour':'labour','Strategic Dependencies':'strategic-dependencies','Repair':'repair',
  'Geography':'geography','Dependency':'dependency','Bottleneck':'bottleneck','Missing Coupling':'missing-coupling','Law':'laws','Procurement':'procurement','Funding':'funding','Skills':'skills','Strategic Security':'strategic-security'
};

function slug(text){return text.toLowerCase().trim().replace(/→/g,'-to-').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');}
function linkChildren(){
  document.querySelectorAll('.children a').forEach(anchor=>{
    const label=anchor.textContent.trim();
    const id=knownIds[label]||slug(label);
    anchor.href=`node.html?id=${encodeURIComponent(id)}&name=${encodeURIComponent(label)}`;
    anchor.setAttribute('aria-label',`Open record: ${label}`);
    anchor.classList.add('record-link');
  });
}
if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',linkChildren); else linkChildren();
