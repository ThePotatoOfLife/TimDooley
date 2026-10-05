(()=>{"use strict";
const input=document.getElementById("papers-find");
const status=document.getElementById("papers-find-status");
if(!input||!status)return;
const shelves=[...document.querySelectorAll(".papers-shelf")];
const entries=[...document.querySelectorAll("[data-paper-entry]")];
const initialOpen=new Map(shelves.map(s=>[s,s.open]));
const normalize=value=>String(value||"").toLocaleLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").trim();
function apply(){
  const q=normalize(input.value);
  let matches=0;
  shelves.forEach(shelf=>{
    let shelfMatches=0;
    shelf.querySelectorAll("[data-paper-entry]").forEach(entry=>{
      const hit=!q||normalize(entry.dataset.search).includes(q);
      entry.hidden=!hit;
      if(hit){matches++;shelfMatches++;}
    });
    shelf.hidden=!!q&&shelfMatches===0;
    shelf.open=q?shelfMatches>0:initialOpen.get(shelf);
  });
  status.textContent=q?(matches===1?"1 matching paper":matches+" matching papers"):entries.length+" papers available";
}
input.addEventListener("input",apply);
input.addEventListener("search",apply);
apply();
})();
