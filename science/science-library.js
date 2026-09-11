(()=>{
  'use strict';

  const search=document.getElementById('science-search');
  const field=document.getElementById('science-field');
  const type=document.getElementById('science-type');
  const count=document.getElementById('science-count');
  const empty=document.getElementById('science-empty');
  const rows=[...document.querySelectorAll('.science-record')];

  const splitValues=value=>String(value||'').split('|').map(item=>item.trim()).filter(Boolean);
  const natural=(a,b)=>a.localeCompare(b,undefined,{sensitivity:'base'});

  function populateSelect(select,values,allLabel){
    if(!select) return;
    const selected=select.value||'all';
    select.innerHTML='';
    const all=document.createElement('option');
    all.value='all';
    all.textContent=allLabel;
    select.appendChild(all);
    [...new Set(values)].sort(natural).forEach(value=>{
      const option=document.createElement('option');
      option.value=value;
      option.textContent=value;
      select.appendChild(option);
    });
    select.value=[...select.options].some(option=>option.value===selected)?selected:'all';
  }

  function prepareFilters(){
    populateSelect(field,rows.flatMap(row=>splitValues(row.dataset.fields)),'All fields');
    populateSelect(type,rows.map(row=>row.dataset.type).filter(Boolean),'All document types');
  }

  function matchesSearch(row,tokens){
    if(!tokens.length) return true;
    const haystack=(row.dataset.search||row.textContent||'').toLowerCase();
    return tokens.every(token=>haystack.includes(token));
  }

  function draw(){
    const tokens=String(search?.value||'').trim().toLowerCase().split(/\s+/).filter(Boolean);
    const selectedField=field?.value||'all';
    const selectedType=type?.value||'all';
    let shown=0;

    rows.forEach(row=>{
      const rowFields=splitValues(row.dataset.fields);
      const matchesField=selectedField==='all'||rowFields.includes(selectedField);
      const matchesType=selectedType==='all'||row.dataset.type===selectedType;
      const visible=matchesField&&matchesType&&matchesSearch(row,tokens);
      row.hidden=!visible;
      if(visible) shown++;
    });

    if(count){
      const noun=shown===1?'document':'documents';
      count.textContent=`${shown} ${noun} shown`;
    }
    if(empty) empty.hidden=shown!==0;
  }

  prepareFilters();
  [search,field,type].filter(Boolean).forEach(control=>{
    control.addEventListener(control===search?'input':'change',draw);
  });
  draw();
})();
