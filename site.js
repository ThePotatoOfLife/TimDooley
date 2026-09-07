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
    levelTitle.textContent=`Level ${value} · ${level.querySelector('span').textContent}`;
    planeDetail.textContent=levelDescriptions[value];
  });
});

document.querySelectorAll('.plane-card').forEach(card=>{
  card.addEventListener('click',()=>{
    document.querySelectorAll('.plane-card').forEach(item=>item.classList.remove('selected'));
    card.classList.add('selected');
    planeDetail.textContent=`${card.dataset.name}: this dimension becomes a view across the records at the selected level. The same information can be reordered by geography, scale, time, importance, relationships or evidence.`;
  });
});
