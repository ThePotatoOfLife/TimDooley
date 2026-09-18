(function(root,factory){
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoBibleTTS=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const clean=value=>String(value??'').replace(/\s+/g,' ').trim();
  function join(parts){return parts.map(clean).filter(Boolean).join(' ')}
  function buildBiblePayload(parts={}){
    const project=clean(parts.project),scripture=clean(parts.scripture),why=clean(parts.why),mismatch=clean(parts.mismatch),selection=clean(parts.selection);
    const both=join([
      project&&`Project. ${project}`,
      scripture&&`Scripture. ${scripture}`,
      why&&`Why these connect. ${why}`,
      mismatch,
    ]);
    const whyText=join([why,mismatch]);
    return {
      id:clean(parts.id),
      label:clean(parts.title)||'Bible comparison',
      sections:[
        {id:'both',label:'Both',text:both},
        {id:'project',label:'Project',text:project},
        {id:'scripture',label:'Scripture',text:scripture},
        {id:'why',label:'Why',text:whyText},
        {id:'selection',label:'Selection',text:selection},
      ].filter(section=>section.text),
    };
  }
  function textOf(node,selector){return clean(node?.querySelector(selector)?.textContent)}
  function selectionInsideActive(node,doc=root?.document){
    const selection=doc?.getSelection?.();
    if(!node||!selection||selection.rangeCount===0||selection.isCollapsed)return '';
    const range=selection.getRangeAt(0);
    const common=range.commonAncestorContainer;
    const element=common?.nodeType===1?common:common?.parentElement||common?.parentNode;
    if(!element||!node.contains(element))return '';
    return clean(selection.toString());
  }
  function extractRelation(node,selection=''){
    if(!node)return buildBiblePayload({});
    const article=node.matches?.('.relation')?node:node.querySelector?.('.relation');
    if(!article)return buildBiblePayload({});
    const sides=article.querySelectorAll('.parallel .side');
    return buildBiblePayload({
      id:article.dataset?.relationId||'',
      title:textOf(article,'.relation-title'),
      project:clean(sides[0]?.textContent),
      scripture:clean(sides[1]?.textContent),
      why:textOf(article,'.why p'),
      mismatch:textOf(article,'.boundary-callout'),
      selection,
    });
  }
  function mount(){
    if(typeof document==='undefined'||!root?.PotatoTTSDrawer)return null;
    const active=document.getElementById('active-relation');
    const nav=document.querySelector('.comparison-nav');
    if(!active||!nav)return null;
    let host=document.getElementById('bible-tts-drawer');
    if(!host){host=document.createElement('div');host.id='bible-tts-drawer';host.className='bible-tts-drawer';nav.before(host)}
    host.dataset.ttsPrimary='';
    const settingsKey='potato-tts-settings';
    const readSettings=()=>{try{return JSON.parse(localStorage.getItem(settingsKey)||'{}')}catch{return{}}};
    const writeSettings=patch=>{try{localStorage.setItem(settingsKey,JSON.stringify({...readSettings(),...patch}))}catch{/* optional */}};
    const read=()=>extractRelation(active,selectionInsideActive(active,document));
    const setRelationActive=value=>active.querySelector?.('.relation')?.classList?.toggle('ptts-reading-active',Boolean(value));
    const pageHighlighter=root.PotatoTTSDrawer.createPageHighlighter?.({document})||{highlight:()=>false,clear:()=>{},invalidate:()=>{}};
    let continuing=Boolean(readSettings().bibleContinue);
    let continuationBusy=false;

    const continueLabel=document.createElement('label');
    continueLabel.className='bible-tts-continue';
    const continueToggle=document.createElement('input');
    continueToggle.type='checkbox';
    continueToggle.checked=continuing;
    continueToggle.setAttribute('aria-label','Continue through results');
    continueLabel.append(continueToggle,document.createTextNode(' Continue through results'));
    host.append(continueLabel);
    function setContinuing(value,{persist=true}={}){
      continuing=Boolean(value);
      continueToggle.checked=continuing;
      if(persist)writeSettings({bibleContinue:continuing});
    }
    continueToggle.addEventListener('change',()=>setContinuing(continueToggle.checked));

    function relationPieces(){
      const article=active.querySelector?.('.relation');
      if(!article)return null;
      const sides=[...article.querySelectorAll('.parallel .side')];
      const whyNode=article.querySelector('.why p');
      const mismatchNode=article.querySelector('.boundary-callout');
      return {
        article,
        project:{node:sides[0],text:clean(sides[0]?.textContent)},
        scripture:{node:sides[1],text:clean(sides[1]?.textContent)},
        why:{node:whyNode,text:clean(whyNode?.textContent)},
        mismatch:{node:mismatchNode,text:clean(mismatchNode?.textContent)},
      };
    }

    function compositeSegments(parts){
      const usable=parts.filter(part=>part?.node&&part?.text);
      let cursor=0;
      return usable.map((part,index)=>{
        const prefix=part.prefix||'';
        const contentStart=cursor+prefix.length;
        const contentEnd=contentStart+part.text.length;
        const spokenLength=prefix.length+part.text.length;
        const result={...part,contentStart,contentEnd};
        cursor+=spokenLength+(index<usable.length-1?1:0);
        return result;
      });
    }

    function highlightMapped(word,segments,followReading){
      const segment=segments.find(part=>word.start>=part.contentStart&&word.end<=part.contentEnd);
      if(!segment){pageHighlighter.clear();return}
      pageHighlighter.highlight(segment.node,{start:word.start-segment.contentStart,end:word.end-segment.contentStart},'',followReading);
    }

    function highlightBibleBoundary(event){
      if(!['boundary','followchange'].includes(event.type)||!event.absoluteWord)return;
      const pieces=relationPieces();
      if(!pieces){pageHighlighter.clear();return}
      if(event.sectionId==='project'){pageHighlighter.highlight(pieces.project.node,event.absoluteWord,'',event.followReading);return}
      if(event.sectionId==='scripture'){pageHighlighter.highlight(pieces.scripture.node,event.absoluteWord,'',event.followReading);return}
      if(event.sectionId==='why'){
        highlightMapped(event.absoluteWord,compositeSegments([
          {...pieces.why,prefix:''},
          {...pieces.mismatch,prefix:''},
        ]),event.followReading);
        return;
      }
      if(event.sectionId==='both'){
        highlightMapped(event.absoluteWord,compositeSegments([
          {...pieces.project,prefix:'Project. '},
          {...pieces.scripture,prefix:'Scripture. '},
          {...pieces.why,prefix:'Why these connect. '},
          {...pieces.mismatch,prefix:''},
        ]),event.followReading);
        return;
      }
      pageHighlighter.clear();
    }

    function waitForRelationChange(previousId,timeout=2500){
      return new Promise(resolve=>{
        const current=read();
        if(current.id&&current.id!==previousId){resolve(current);return}
        let settled=false;
        const finish=value=>{if(settled)return;settled=true;observer.disconnect();clearTimeout(timer);resolve(value)};
        const observer=new MutationObserver(()=>{
          const next=read();
          if(next.id&&next.id!==previousId)finish(next);
        });
        observer.observe(active,{childList:true,subtree:true,characterData:true});
        const timer=setTimeout(()=>finish(null),timeout);
      });
    }

    async function continueToNext(sectionId,drawer){
      if(!continuing||continuationBusy)return;
      const nextButton=document.getElementById('next-relation');
      if(!nextButton||nextButton.disabled){continuing=false;continueToggle.checked=false;return}
      continuationBusy=true;
      const previousId=read().id;
      nextButton.click();
      const next=await waitForRelationChange(previousId);
      continuationBusy=false;
      if(!continuing||!next){continuing=false;continueToggle.checked=false;return}
      drawer.setPayload(next);
      drawer.playSection(sectionId);
    }

    let drawer=null;
    drawer=root.PotatoTTSDrawer.mount({
      target:host,
      getPayload:read,
      settingsKey,
      onEvent:event=>{
        if(['chunkstart','boundary'].includes(event.type))setRelationActive(true);
        if((event.type==='boundary'||event.type==='followchange')&&event.absoluteWord)highlightBibleBoundary(event);
        if(['complete','stop','error'].includes(event.type)){setRelationActive(false);pageHighlighter.clear()}
        if(event.type==='complete'&&continuing)void continueToNext(event.sectionId,drawer);
        if(event.type==='stop'){continuing=false;continueToggle.checked=false}
        if(event.type==='error'){continuing=false;continueToggle.checked=false}
      },
    });

    let lastId=read().id;
    const observer=new MutationObserver(()=>{
      const next=read();
      if(next.id!==lastId){lastId=next.id;setRelationActive(false);pageHighlighter.invalidate();drawer?.setPayload(next)}
      else drawer?.setPayload(next);
    });
    observer.observe(active,{childList:true,subtree:true,characterData:true});
    const selectionAction=root.PotatoTTSDrawer.mountSelectionAction?.({container:active,drawer,getPayload:read});
    return {drawer,observer,selectionAction,pageHighlighter,refresh:()=>{pageHighlighter.invalidate();drawer?.setPayload(read())},destroy(){observer.disconnect();selectionAction?.destroy?.();pageHighlighter.clear();setRelationActive(false);drawer?.stop?.()}};
  }
  if(typeof document!=='undefined'){
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount,{once:true});else setTimeout(mount,0);
  }
  return {buildBiblePayload,selectionInsideActive,extractRelation,mount};
});
