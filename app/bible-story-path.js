(()=>{
'use strict';

const stages=[
  {id:'beginnings',label:'Beginnings',subtitle:'Creation and the early world',summary:'Genesis opens with creation, human vocation, fracture, flood and the scattering of nations. This is the Bible’s first great field of origins, boundaries, exile and renewed beginnings.',books:['Genesis'],reference:'Genesis 1:1-2:3',query:'garden creation'},
  {id:'ancestors',label:'Ancestors',subtitle:'Abraham, Isaac, Jacob and Joseph',summary:'The story narrows from the nations to one family. Promise, inheritance, sibling conflict, exile, reconciliation and blessing become recurring structures.',books:['Genesis'],reference:'Genesis 12:1-9',query:'jacob joseph'},
  {id:'exodus',label:'Exodus and Covenant',subtitle:'Liberation, wilderness and Torah',summary:'Israel is brought out of slavery, formed through covenant, taught how to live, and carried through the wilderness toward a land it has not yet entered.',books:['Exodus','Leviticus','Numbers','Deuteronomy'],reference:'Exodus 3:1-15',query:'exodus covenant'},
  {id:'land',label:'Land and Judges',subtitle:'Settlement, cycles and fragile leadership',summary:'Joshua through Ruth moves through conquest traditions, settlement, repeated breakdown and local deliverance. Ruth offers a quieter story of loyalty, provision and belonging.',books:['Joshua','Judges','Ruth'],reference:'Judges 2:10-23',query:'judges ruth'},
  {id:'kingdom',label:'Kings and Kingdom',subtitle:'Saul, David, Solomon and the divided kingdoms',summary:'The monarchy rises, centralizes worship and power, fractures, and repeatedly tests what kingship is for. Psalms and royal traditions grow beside this world.',books:['1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles'],reference:'2 Samuel 7:8-17',query:'david kingdom'},
  {id:'prophets',label:'Prophets and Crisis',subtitle:'Warning, judgment, hope and exile',summary:'Prophets confront rulers, worship, injustice and covenant failure while also speaking of remnant, return, renewal, new covenant and restored creation.',books:['Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah'],reference:'Isaiah 40:1-11',query:'exile restoration'},
  {id:'return',label:'Return and Rebuilding',subtitle:'Homecoming after exile',summary:'Ezra, Nehemiah and the later prophets focus on return, rebuilding, identity, temple, city and the difficult question of what restoration actually means.',books:['Ezra','Nehemiah','Esther','Haggai','Zechariah','Malachi'],reference:'Ezra 1:1-5',query:'return temple'},
  {id:'wisdom',label:'Wisdom and Prayer',subtitle:'A thread running across the story',summary:'Job, Psalms, Proverbs, Ecclesiastes and Song of Solomon do not fit into one simple historical slot. They are better read as an ongoing stream of prayer, wisdom, suffering, love and reflection.',books:['Job','Psalms','Proverbs','Ecclesiastes','Song of Solomon'],reference:'Psalm 1',query:'wisdom psalm'},
  {id:'jesus',label:'Jesus',subtitle:'The four Gospel witnesses',summary:'Matthew, Mark, Luke and John tell the story of Jesus through overlapping but distinct portraits: teaching, healing, conflict, death, resurrection and recognition.',books:['Matthew','Mark','Luke','John'],reference:'Mark 1:1-15',query:'jesus resurrection'},
  {id:'mission',label:'Church and Mission',subtitle:'Acts and the expanding movement',summary:'Acts follows the movement from Jerusalem outward through witness, conflict, travel, community formation and mission across the eastern Mediterranean.',books:['Acts'],reference:'Acts 1:1-11',query:'spirit witness'},
  {id:'letters',label:'Letters and Communities',subtitle:'Teaching life inside the movement',summary:'The New Testament letters argue about faith, practice, community, suffering, leadership, freedom, unity and hope. They are conversations with real communities, not one continuous narrative.',books:['Romans','1 Corinthians','2 Corinthians','Galatians','Ephesians','Philippians','Colossians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','Titus','Philemon','Hebrews','James','1 Peter','2 Peter','1 John','2 John','3 John','Jude'],reference:'Romans 12:1-8',query:'body community'},
  {id:'new-creation',label:'New Creation',subtitle:'Revelation and the renewed city',summary:'Revelation gathers throne, Lamb, witness, judgment, Babylon, river, tree and city imagery into a final vision of conflict, renewal and divine presence.',books:['Revelation'],reference:'Revelation 21:1-7',query:'new jerusalem'}
];

const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let active=0;

function renderRail(){
  const rail=$('bible-story-rail');
  if(!rail)return;
  rail.innerHTML=stages.map((stage,index)=>
    '<button type="button" class="story-stage'+(index===active?' is-active':'')+'" data-story-stage="'+esc(stage.id)+'">'+
    '<span>'+String(index+1).padStart(2,'0')+'</span><strong>'+esc(stage.label)+'</strong></button>'
  ).join('');
  rail.querySelectorAll('[data-story-stage]').forEach(button=>button.addEventListener('click',()=>select(button.dataset.storyStage)));
}

function renderDetail(){
  const stage=stages[active],host=$('bible-story-detail');
  if(!stage||!host)return;
  host.innerHTML=
    '<div class="story-detail-copy"><div class="eyebrow">'+esc(stage.subtitle)+'</div><h3>'+esc(stage.label)+'</h3><p>'+esc(stage.summary)+'</p>'+
    '<div class="story-books"><strong>Books</strong><span>'+esc(stage.books.join(' · '))+'</span></div></div>'+
    '<div class="story-detail-actions"><button type="button" id="story-read-passage">Read '+esc(stage.reference)+'</button>'+
    '<button type="button" class="secondary" id="story-open-book">Open '+esc(stage.books[0])+'</button>'+
    '<button type="button" class="secondary" id="story-find-comparisons">Related comparisons</button></div>';
  $('story-read-passage')?.addEventListener('click',()=>window.BibleScriptureReader?.openReference(stage.reference));
  $('story-open-book')?.addEventListener('click',()=>{
    const library=window.BibleLibrary;
    if(library?.selectByName){
      library.selectByName(stage.books[0],1);
      document.getElementById('bible-library')?.scrollIntoView({behavior:'smooth',block:'start'});
    }
  });
  $('story-find-comparisons')?.addEventListener('click',()=>{
    const search=$('search');
    if(search){
      search.value=stage.query;
      search.dispatchEvent(new Event('input',{bubbles:true}));
      document.getElementById('comparison-atlas')?.scrollIntoView({behavior:'smooth',block:'start'});
    }
  });
}

function select(id){
  const index=stages.findIndex(stage=>stage.id===id);
  if(index<0)return;
  active=index;
  renderRail();
  renderDetail();
  const url=new URL(location.href);
  url.searchParams.set('story',stages[active].id);
  history.replaceState(null,'',url);
}

function init(){
  if(!$('bible-story-path'))return;
  const requested=new URL(location.href).searchParams.get('story');
  const index=stages.findIndex(stage=>stage.id===requested);
  if(index>=0)active=index;
  renderRail();
  renderDetail();
}

window.BibleStoryPath={stages,select};
document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init):init();
})();