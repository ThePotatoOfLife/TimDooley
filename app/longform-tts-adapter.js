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
    if(!excludeSelector||typeof node.cloneNode!=='function')return cleanText(node.textContent||'');
    const clone=node.cloneNode(true);
    if(typeof clone.querySelectorAll==='function')clone.querySelectorAll(excludeSelector).forEach(item=>item.remove());
    return cleanText(clone.textContent||'');
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

    const itemSelector=config.itemSelector||'';
    let currentItem=null;
    let drawer=null;
    const getItems=()=>itemSelector?[...container.querySelectorAll(itemSelector)]:[];
    const firstItem=()=>getItems()[0]||null;
    const chooseCurrent=item=>{
      if(item&&container.contains(item))currentItem=item;
      drawer?.updatePayload('current-entry');
    };
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

    drawer=Drawer.mount({
      mount:host,
      source,
      label:config.buttonLabel||'Read aloud',
      settingsKey:config.settingsKey||'potato-tts-drawer-settings',
      className:config.className||'tts-drawer--longform',
    });
    if(!drawer)return null;

    const onActivate=event=>{
      if(!itemSelector)return;
      const item=event.target?.closest?.(itemSelector);
      if(item&&container.contains(item))chooseCurrent(item);
    };
    container.addEventListener('click',onActivate);
    container.addEventListener('focusin',onActivate);

    const onSelection=()=>drawer.updatePayload('selection');
    doc.addEventListener('selectionchange',onSelection);

    const Observer=config.MutationObserver||root?.MutationObserver;
    const observer=Observer?new Observer(()=>{
      if(currentItem&&!container.contains(currentItem))currentItem=null;
      drawer.updatePayload('content');
    }):null;
    observer?.observe(container,{childList:true,subtree:true,characterData:true});
    drawer.updatePayload('mount');

    return {
      drawer,
      refresh:()=>drawer.updatePayload('refresh'),
      setCurrent:chooseCurrent,
      source,
      destroy(){
        observer?.disconnect();
        container.removeEventListener('click',onActivate);
        container.removeEventListener('focusin',onActivate);
        doc.removeEventListener('selectionchange',onSelection);
        drawer.destroy?.();
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

  return {cleanText,buildLongformPayload,selectionInside,readableText,configFromElement,mount,autoMount};
});