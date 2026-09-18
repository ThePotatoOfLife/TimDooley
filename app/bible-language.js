(()=>{
'use strict';

const TITLE_OVERRIDES={
  'atlas-jacobs-ladder-son-of-man':"Jacob's Ladder and the Son of Man",
  'atlas-lion-root-lamb-scroll':'Lion, Root, Lamb and Scroll',
  'atlas-open-scroll-to-nations':'The Open Scroll and the Nations',
  'atlas-two-witnesses-death-return':'Two Witnesses: Death, Breath and Return',
  'atlas-key-of-david-door-authority':'The Key of David: Door and Authority',
  'atlas-red-heifer-ash-death-purification':'The Red Heifer: Ash and Purification',
  'atlas-three-day-grammar':'The Three-Day Pattern',
  'atlas-needle-eye-threshold':"The Needle's Eye",
  'atlas-seed-death-multiplication':'Seed, Death and Multiplication',
  'atlas-cornerstone-rejected-foundation':'The Rejected Stone and the Foundation',
  'atlas-new-heaven-new-earth-restoration':'A New Heaven and a New Earth',
  'atlas-alpha-omega-center':'Alpha and Omega',
  'atlas-fruit-test':'The Fruit Test',
  'son-tree-ordeal-2011':'Before the Cross: The 2011 Ego Death',
  'son-custody-prison-passion-2016':'Custody, Judgment and the Passion Parallel',
  'son-prison-lamb-recognition-2016':'Recognition in Prison',
  'son-reciprocity-enemy-love-2016':'Where the Parallel Breaks: Enemy Love',
  'son-jesus-crucifixion-declaration-2017-2018':'Before the Meme Death: The Crucifixion Declaration',
  'son-meme-crucifixion-burial-2019-2020':'The Meme as Tomb',
  'thomas-twin-way-wounds-recognition':'Thomas: Twin, Way and Wounds',
  'son-joseph-prison-listening-2016':'Joseph in Prison: Listening and Service',
  'son-joseph-release-suit-2016':'Joseph: Release and Changed Clothes',
  'father-internet-orphans-2026-01-21':'Fatherhood Before the Throne',
  'father-carries-orphans-sewer-2026-01-21':'Carrying the Orphans',
  'gardener-sorts-by-fruit-2026-06-27':'The Gardener and the Fruit Test',
  'hold-release-resurrected-son-2026-06-27':'Holding On and Letting Go',
  'thomas-tammuz-weeping-investigation-2026-07':'Thomas, Tammuz and the Weeping Women',
  'tammuz-north-gate-2026-07-31':'Thomas, Tammuz and the North Gate',
  'new-jerusalem-house-ladder-cluster-2026-05-01':'New Jerusalem, House and Ladder',
  'ladder-door-specialization-2026-05-19':'Ladder and Door: A Role Tension',
  'self-resurrection-witnesses-2025-09-30':'Resurrection and Witnesses Become Explicit',
  'father-root-seat-north-ladder-2026-04-30':'Father, Root, North and Ladder',
  'bread-door-tomb-resurrection-2026-04-23':'Bread, Lion and the Door',
  'new-jerusalem-north-ladder-2026-05-11':'Lower Cube and New Jerusalem',
  'breath-nostrils-2026-07-23':'The Breath of Life',
  'son-cornerstone-2026-08-17':'The Son and the Cornerstone',
  'micah-6-8-virtue-test-2026':'Micah 6:8: Justice, Mercy and Humility',
  'psalm-84-door-doorkeeper-role-contrast-2026':'Door and Doorkeeper',
  'deuteronomy-romans-nearness-countertext-2026':'The Word Is Near',
  'quiet-presence-1-kings-19-2026':'The Quiet Voice After the Spectacle',
  'ploughshares-seat-peace-function-2026':'Swords into Ploughshares',
  'exodus25-two-cherubim-central-presence':'Cherubim and the Meeting Place',
  'psalm80-compressed-potatoverse-neighbor':'Psalm 80: Shepherd, Vine and Restoration',
  'luke15-restorative-return-versus-vomit-return':'Return and Restoration',
  'isaiah55-return-rain-seed-bread':'Rain, Seed, Bread and Return',
  'isaiah58-repairer-breach-watered-garden':'Repairing the Breach',
  'ezekiel34-shepherd-versus-extractive-ruler':'The Shepherd and the Flock',
  'psalm23-shepherd-valley-table-house':'Valley, Table and House',
  'john21-love-becomes-feeding':'Love Becomes Feeding',
  'romans8-creation-groaning-liberation':'Creation Groans for Freedom',
  'revelation3-door-knock-meal':'The Door, the Knock and the Meal',
  'revelation22-open-water-invitation':'The Open Invitation to Life',
  'daniel7-ancient-of-days-son-of-man-role-distribution':'The Ancient of Days and the Son of Man',
  'philippians2-descent-service-death-exaltation':'Descent, Service and Exaltation',
  'noah-ark-versus-covenant-ark-distinction':'Two Arks, Two Functions'
};

const SMALL_WORDS=new Set(['and','as','at','by','for','from','in','of','on','or','the','to','vs']);
const ACRONYMS=new Map([['kjv','KJV'],['web','WEB'],['csf','CSF']]);

function titleCase(value){
  return String(value||'').split(/\s+/).filter(Boolean).map((word,index)=>{
    const lower=word.toLowerCase();
    if(ACRONYMS.has(lower))return ACRONYMS.get(lower);
    if(index>0&&SMALL_WORDS.has(lower))return lower==='vs'?'vs.':lower;
    return lower.charAt(0).toUpperCase()+lower.slice(1);
  }).join(' ');
}

function humanizeId(id){
  let value=String(id||'')
    .replace(/^atlas-/,'')
    .replace(/^arc-/,'')
    .replace(/-(?:19|20)\d{2}(?:-\d{2})?(?:-\d{2})?$/,'')
    .replace(/\bversus\b/g,'vs')
    .replace(/-/g,' ')
    .replace(/\s+/g,' ')
    .trim();
  value=value.replace(/^jacobs\b/i,"Jacob's");
  return titleCase(value);
}

function machineLike(title,id){
  const clean=String(title||'').trim();
  if(!clean)return true;
  const fromId=String(id||'').replace(/^atlas-|^arc-/,'').replace(/-/g,' ').trim().toLowerCase();
  return clean.toLowerCase()===fromId || (/^[a-z0-9 ]+$/.test(clean)&&clean.split(/\s+/).length>2);
}

function title(row){
  const id=String(row?.id||'');
  if(TITLE_OVERRIDES[id])return TITLE_OVERRIDES[id];
  const raw=String(row?.title||'').trim();
  if(raw&&!machineLike(raw,id))return raw.replace(/\s+/g,' ');
  return humanizeId(id||row?.project_anchor||'Bible comparison');
}

function label(value){
  return titleCase(String(value||'').replace(/[-_]+/g,' ').replace(/\s+/g,' ').trim());
}

window.BibleLanguage={title,label,humanizeId,TITLE_OVERRIDES};
})();