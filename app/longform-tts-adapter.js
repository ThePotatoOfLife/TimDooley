(function(root,factory){
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoLongformTTS=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';

  function cleanText(value){
    return String(value??'').replace(/\s+/g,' ').trim();
  }

  function buildLongformPayload(input={}){
    const id=String(input.id||'longform');
    const label=cleanText(input.label||'Read aloud');
    const sections=[];
    const whole=cleanText(input.whole);
    const current=cleanText(input.current);
    const selection=cleanText(input.selection);
    if(whole)sections.push({id:'all',label:cleanText(input.allLabel||'Whole story'),text:whole});
    if(current)sections.push({id:'current',label:cleanText(input.currentLabel||'Current entry'),text:current});
    if(selection)sections.push({id:'selection',label:cleanText(input.selectionLabel||'Selection'),text:selection});
    return {id,label,sections};
  }

  function selectionInside(doc,container){
    if(!doc||!container||typeof doc.getSelection!=='function')return '';
    const selection=doc.getSelection();
    if(!selection||selection.rangeCount===0||selection.isCollapsed)return '';
    const range=selection.getRangeAt(0);
    const node=range.commonAncestorContainer;
    const element=node.nodeType===1?node:node.parentNode;
    if(!element||!container.contains(element))return '';
    return cleanText(selection.toString());
  }

  function readableText(node,excludeSelector=''){
    if(!node)return '';
    if(typeof node.cloneNode!=='function')return cleanText(node.textContent||'');
    const clone=node.cloneNode(true);
    const exclusions=['button','summary','.ptts-inline-listen','.ptts-drawer',excludeSelector].filter(Boolean).join(',');
    if(exclusions&&typeof clone.querySelectorAll==='function')clone.querySelectorAll(exclusions).forEach(item=>item.remove());
    return cleanText(clone.textContent||'');
  }

  function mutationsAreInside(records,boundary){
    const list=Array.from(records||[]);
    if(!list.length||!boundary)return false;
    return list.every(record=>{
      const target=record?.target;
      if(!target)return false;
      return target===boundary||Boolean(boundary.contains?.(target));
    });
  }

  async function requestContentPreparation(container,sectionId,EventCtor=root?.CustomEvent,options={}){
    if(!container||typeof container.dispatchEvent!=='function'||typeof EventCtor!=='function')return false;
    const pending=[];
    const event=new EventCtor('potato:tts-prepare',{
      bubbles:false,
      detail:{
        sectionId,
        signal:options.signal,
        waitUntil(task){
          if(task&&typeof task.then==='function')pending.push(Promise.resolve(task));
        },
      },
    });
    container.dispatchEvent(event);
    if(!pending.length)return false;
    await Promise.all(pending);
    return true;
  }

  function configFromElement(host,doc){
    if(!host||!doc)return null;
    const data=host.dataset||{};
    const rootSelector=data.ttsRoot||'';
    const container=rootSelector?doc.querySelector(rootSelector):null;
    if(!container)return null;
    return {
      mount:host,
      root:container,
      id:data.ttsId||container.id||'longform',
      label:data.ttsLabel||doc.title||'Read aloud',
      allLabel:data.ttsAllLabel||'Whole content',
      currentLabel:data.ttsCurrentLabel||'Current section',
      selectionLabel:data.ttsSelectionLabel||'Selection',
      itemSelector:data.ttsItem||'',
      excludeSelector:data.ttsExclude||'',
    };
  }

  function mount(config={}){
    const doc=config.document||root?.document;
    const Drawer=config.drawer||root?.PotatoTTSDrawer;
    const host=config.mount;
    const container=config.root;
    if(!doc||!Drawer||typeof Drawer.mount!=='function'||!host||!container)return null;
    if(host.dataset)host.dataset.ttsPrimary='';

    const itemSelector=config.itemSelector||'';
    let currentItem=null;
    let drawer=null;
    let selectionAction=null;
    let preparing=false;
    const pageHighlighter=Drawer.createPageHighlighter?.({document:doc})||{highlight:()=>false,clear:()=>{},invalidate:()=>{}};
    const getItems=()=>itemSelector?[...container.querySelectorAll(itemSelector)]:[];
    const firstItem=()=>getItems()[0]||null;
    const source=()=>{
      if(itemSelector&&(!currentItem||!container.contains(currentItem)))currentItem=firstItem();
      return buildLongformPayload({
        id:config.id||container.id||'longform',
        label:config.label||doc.title||'Read aloud',
        allLabel:config.allLabel||'Whole story',
        currentLabel:config.currentLabel||'Current entry',
        selectionLabel:config.selectionLabel||'Selection',
        whole:readableText(container,config.excludeSelector||''),
        current:readableText(currentItem,config.excludeSelector||''),
        selection:selectionInside(doc,container),
      });
    };
    const refresh=()=>drawer?.setPayload?.(source());
    const clearReadingActive=()=>getItems().forEach(item=>item.classList?.remove('ptts-reading-active'));
    const setReadingActive=active=>{
      clearReadingActive();
      if(active&&currentItem?.classList)currentItem.classList.add('ptts-reading-active');
    };
    const chooseCurrent=item=>{
      setReadingActive(false);
      pageHighlighter.invalidate();
      if(item&&container.contains(item))currentItem=item;
      refresh();
    };
    const prepareForPlayback=async(sectionId,options={})=>{
      preparing=true;
      try{
        await requestContentPreparation(container,sectionId,doc.defaultView?.CustomEvent||root?.CustomEvent,options);
      }finally{
        preparing=false;
        pageHighlighter.invalidate();
        if(currentItem&&!container.contains(currentItem)){setReadingActive(false);currentItem=null}
        ensureListenButtons();
      }
      const next=source();
      drawer?.setPayload?.(next);
      return next;
    };

    drawer=Drawer.mount({
      target:host,
      getPayload:source,
      prepareSection:prepareForPlayback,
      settingsKey:config.settingsKey||'potato-tts-settings',
      onEvent:event=>{
        if(event.sectionId==='current'&&['chunkstart','boundary'].includes(event.type))setReadingActive(true);
        if(event.type==='boundary'&&event.absoluteWord){
          const target=event.sectionId==='current'?currentItem:event.sectionId==='all'?container:null;
          if(target)pageHighlighter.highlight(target,event.absoluteWord,config.excludeSelector||'',event.followReading);
          else pageHighlighter.clear();
        }
        if(['complete','stop','error'].includes(event.type)){setReadingActive(false);pageHighlighter.clear()}
      },
    });
    if(!drawer)return null;

    function ensureListenButtons(){
      if(!itemSelector||typeof doc.createElement!=='function')return;
      for(const item of getItems()){
        if(item.dataset?.ttsListenReady==='true')continue;
        const control=doc.createElement('button');
        control.type='button';
        control.className='ptts-inline-listen';
        control.dataset.ttsListen='';
        control.textContent='🔊 Listen';
        control.setAttribute('aria-label','Listen to this section');
        control.addEventListener('click',event=>{
          event.preventDefault();
          event.stopPropagation();
          chooseCurrent(item);
          drawer.playSection?.('current');
        });
        const anchor=item.querySelector?.('h2,h3,h1')||item.querySelector?.('.movement-label,.story-meta');
        if(anchor?.insertAdjacentElement)anchor.insertAdjacentElement('afterend',control);
        else if(item.prepend)item.prepend(control);
        else item.append?.(control);
        if(item.dataset)item.dataset.ttsListenReady='true';
      }
    }

    const onActivate=event=>{
      if(!itemSelector||event.target?.closest?.('[data-tts-listen]'))return;
      const item=event.target?.closest?.(itemSelector);
      if(item&&container.contains(item))chooseCurrent(item);
    };
    const onCurrent=event=>{
      const item=event.detail?.item;
      if(itemSelector&&item&&container.contains(item)&&item.matches?.(itemSelector)&&item!==currentItem)chooseCurrent(item);
    };
    container.addEventListener('click',onActivate);
    container.addEventListener('focusin',onActivate);
    container.addEventListener('potato:tts-current',onCurrent);

    const Observer=config.MutationObserver||root?.MutationObserver;
    const observer=Observer?new Observer(records=>{
      if(mutationsAreInside(records,host))return;
      pageHighlighter.invalidate();
      if(preparing)return;
      if(currentItem&&!container.contains(currentItem)){setReadingActive(false);currentItem=null}
      ensureListenButtons();
      refresh();
    }):null;
    observer?.observe(container,{childList:true,subtree:true,characterData:true});

    ensureListenButtons();
    refresh();
    selectionAction=Drawer.mountSelectionAction?.({document:doc,container,drawer,getPayload:source});

    return {
      drawer,
      refresh,
      setCurrent:chooseCurrent,
      source,
      ensureListenButtons,
      selectionAction,
      pageHighlighter,
      destroy(){
        observer?.disconnect();
        container.removeEventListener('click',onActivate);
        container.removeEventListener('focusin',onActivate);
        container.removeEventListener('potato:tts-current',onCurrent);
        selectionAction?.destroy?.();
        pageHighlighter.clear();
        clearReadingActive();
        drawer.stop?.();
      }
    };
  }

  function autoMount(doc=root?.document){
    if(!doc||typeof doc.querySelectorAll!=='function')return [];
    const mounted=[];
    for(const host of doc.querySelectorAll('[data-tts-longform]')){
      if(host.dataset?.ttsMounted==='true')continue;
      const config=configFromElement(host,doc);
      if(!config)continue;
      const instance=mount(config);
      if(instance){
        if(host.dataset)host.dataset.ttsMounted='true';
        mounted.push(instance);
      }
    }
    return mounted;
  }

  if(root?.document){
    const start=()=>autoMount(root.document);
    root.document.readyState==='loading'?root.document.addEventListener('DOMContentLoaded',start,{once:true}):start();
  }

  return {cleanText,buildLongformPayload,selectionInside,readableText,mutationsAreInside,requestContentPreparation,configFromElement,mount,autoMount};
});
