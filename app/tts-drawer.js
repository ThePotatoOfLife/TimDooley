(function(root,factory){
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoTTSDrawer=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const clean=value=>String(value??'').replace(/\s+/g,' ').trim();
  const clamp=(v,min,max)=>Math.min(max,Math.max(min,v));

  function normalizePayload(input={}){
    const sections=(Array.isArray(input.sections)?input.sections:[])
      .map((section,index)=>({
        id:clean(section?.id)||`section-${index+1}`,
        label:clean(section?.label)||clean(section?.id)||`Section ${index+1}`,
        text:clean(section?.text),
      }))
      .filter(section=>section.text);
    return {id:clean(input.id),label:clean(input.label),sections};
  }

  function resolveSection(payload,id){
    const normalized=normalizePayload(payload);
    if(!normalized.sections.length)return null;
    return normalized.sections.find(section=>section.id===id)
      ||normalized.sections.find(section=>section.id==='both')
      ||normalized.sections[0];
  }

  function buildReadingText(payload,id){return resolveSection(payload,id)?.text||'';}

  function renderFocusedText(text,range){
    const value=String(text??'');
    const start=clamp(Number(range?.start)||0,0,value.length);
    const end=clamp(Number(range?.end)||start,start,value.length);
    return {before:value.slice(0,start),active:value.slice(start,end),after:value.slice(end)};
  }

  function el(tag,className,text){
    const node=document.createElement(tag);
    if(className)node.className=className;
    if(text!==undefined)node.textContent=text;
    return node;
  }

  function button(label,icon){
    const node=el('button','ptts-button',icon);
    node.type='button';node.setAttribute('aria-label',label);node.title=label;
    return node;
  }

  function selectionElement(selection){
    if(!selection||selection.rangeCount===0||selection.isCollapsed)return null;
    const node=selection.getRangeAt(0).commonAncestorContainer;
    return node?.nodeType===1?node:node?.parentElement||node?.parentNode||null;
  }

  function buildNormalizedTextMap(container,excludeSelector=''){
    const doc=container?.ownerDocument||root?.document;
    if(!container||!doc||typeof doc.createTreeWalker!=='function')return {text:'',segments:[]};
    const exclusions=['script','style','noscript','button','summary','.ptts-inline-listen','.ptts-selection-listen','.ptts-drawer',excludeSelector].filter(Boolean).join(',');
    const walker=doc.createTreeWalker(container,4);
    const segments=[];
    let text='';
    let pendingSpace=null;
    let node=null;
    const isSpace=char=>/\s/u.test(char);
    while((node=walker.nextNode())){
      const parent=node.parentElement||node.parentNode;
      if(exclusions&&parent?.closest?.(exclusions))continue;
      const raw=String(node.nodeValue||'');
      let i=0;
      while(i<raw.length){
        if(isSpace(raw[i])){
          let j=i+1;while(j<raw.length&&isSpace(raw[j]))j+=1;
          if(text&&!text.endsWith(' '))pendingSpace={node,start:i,end:j};
          i=j;
          continue;
        }
        let j=i+1;while(j<raw.length&&!isSpace(raw[j]))j+=1;
        if(pendingSpace&&text){
          const outStart=text.length;
          text+=' ';
          segments.push({outStart,outEnd:outStart+1,node:pendingSpace.node,nodeStart:pendingSpace.start,nodeEnd:pendingSpace.end,collapsed:true});
          pendingSpace=null;
        }
        const chunk=raw.slice(i,j);
        const outStart=text.length;
        text+=chunk;
        segments.push({outStart,outEnd:outStart+chunk.length,node,nodeStart:i,nodeEnd:j,collapsed:false});
        i=j;
      }
    }
    return {text,segments};
  }

  function mapPoint(map,index,endBias=false){
    const segments=map?.segments||[];
    if(!segments.length)return null;
    const limit=map.text.length;
    const safe=clamp(Number(index)||0,0,limit);
    if(safe===limit){const last=segments[segments.length-1];return {node:last.node,offset:last.nodeEnd}}
    const probe=endBias&&safe>0?safe-1:safe;
    const segment=segments.find(part=>probe>=part.outStart&&probe<part.outEnd);
    if(!segment)return null;
    if(segment.collapsed)return {node:segment.node,offset:endBias?segment.nodeEnd:segment.nodeStart};
    const relative=endBias?safe-segment.outStart:probe-segment.outStart;
    return {node:segment.node,offset:clamp(segment.nodeStart+relative,segment.nodeStart,segment.nodeEnd)};
  }

  function rangeFromTextMap(map,range,doc){
    if(!map?.text||!range||!doc?.createRange)return null;
    const start=clamp(Number(range.start)||0,0,map.text.length);
    const end=clamp(Number(range.end)||start,start,map.text.length);
    if(end<=start)return null;
    const a=mapPoint(map,start,false),b=mapPoint(map,end,true);
    if(!a||!b)return null;
    const domRange=doc.createRange();
    try{domRange.setStart(a.node,a.offset);domRange.setEnd(b.node,b.offset)}catch{return null}
    return domRange;
  }

  function centerDomRange(win,doc,domRange){
    const rect=domRange?.getBoundingClientRect?.();
    if(!rect)return false;
    const viewportHeight=Number(win?.innerHeight||doc?.documentElement?.clientHeight)||0;
    if(!viewportHeight||typeof win?.scrollTo!=='function')return false;
    const wordCenter=(Number(rect.top)||0)+((Number(rect.height)||0)/2);
    const comfortTop=viewportHeight*.3;
    const comfortBottom=viewportHeight*.7;
    if(wordCenter>=comfortTop&&wordCenter<=comfortBottom)return false;
    const currentScroll=Number(win?.scrollY??win?.pageYOffset)||0;
    const delta=wordCenter-(viewportHeight/2);
    const top=Math.max(0,currentScroll+delta);
    const reduced=Boolean(win?.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches);
    win.scrollTo({top,behavior:reduced?'auto':'smooth'});
    return true;
  }

  function createPageHighlighter(options={}){
    const doc=options.document||root?.document;
    const win=doc?.defaultView||root;
    const highlights=win?.CSS?.highlights;
    const HighlightCtor=win?.Highlight||root?.Highlight;
    const name=options.name||'potato-tts-word';
    const settingsKey=options.settingsKey||'potato-tts-settings';
    let cachedContainer=null,cachedExclude='',cachedMap=null;
    function clear(){highlights?.delete?.(name)}
    function invalidate(){cachedContainer=null;cachedExclude='';cachedMap=null;clear()}
    function persistedFollow(){
      try{return JSON.parse(win?.localStorage?.getItem?.(settingsKey)||'{}').followReading===true}catch{return false}
    }
    function highlight(container,range,excludeSelector='',follow){
      if(!container)return false;
      if(container!==cachedContainer||excludeSelector!==cachedExclude||!cachedMap){
        cachedContainer=container;cachedExclude=excludeSelector;cachedMap=buildNormalizedTextMap(container,excludeSelector);
      }
      const domRange=rangeFromTextMap(cachedMap,range,doc);
      if(!domRange){clear();return false}
      if(highlights&&typeof HighlightCtor==='function')highlights.set(name,new HighlightCtor(domRange));
      if(typeof follow==='boolean'?follow:persistedFollow())centerDomRange(win,doc,domRange);
      return true;
    }
    return {highlight,clear,invalidate,get text(){return cachedMap?.text||''}};
  }

  function mountSelectionAction(options={}){
    const doc=options.document||root?.document;
    const container=options.container;
    const drawer=options.drawer;
    const getPayload=typeof options.getPayload==='function'?options.getPayload:()=>null;
    if(!doc||!container||!drawer||typeof doc.createElement!=='function')return null;

    const control=doc.createElement('button');
    control.type='button';
    control.className='ptts-selection-listen';
    control.textContent='🔊 Read selection';
    control.setAttribute('aria-label','Read selected text aloud');
    control.hidden=true;
    (doc.body||container).append(control);

    function hide(){control.hidden=true;control.removeAttribute('style')}
    function update(){
      const selection=doc.getSelection?.();
      const element=selectionElement(selection);
      if(!selection||selection.isCollapsed||!element||!container.contains(element)){hide();return}
      const text=clean(selection.toString());
      if(!text){hide();return}
      const range=selection.getRangeAt(0);
      const rect=range.getBoundingClientRect?.();
      if(!rect){hide();return}
      const viewportWidth=root?.innerWidth||doc.documentElement?.clientWidth||1024;
      const viewportHeight=root?.innerHeight||doc.documentElement?.clientHeight||768;
      const left=clamp(rect.left+(rect.width/2),72,Math.max(72,viewportWidth-72));
      const top=clamp(rect.bottom+8,8,Math.max(8,viewportHeight-44));
      control.style.left=`${left}px`;
      control.style.top=`${top}px`;
      control.hidden=false;
    }

    control.addEventListener('pointerdown',event=>event.preventDefault());
    control.addEventListener('click',event=>{
      event.preventDefault();
      drawer.setPayload?.(getPayload());
      drawer.playSection?.('selection');
      hide();
    });
    const onSelection=()=>update();
    const onScroll=()=>hide();
    const onKey=event=>{if(event.key==='Escape')hide()};
    doc.addEventListener('selectionchange',onSelection);
    root?.addEventListener?.('scroll',onScroll,{passive:true});
    doc.addEventListener('keydown',onKey);

    return {
      element:control,
      update,
      hide,
      destroy(){
        doc.removeEventListener('selectionchange',onSelection);
        root?.removeEventListener?.('scroll',onScroll);
        doc.removeEventListener('keydown',onKey);
        control.remove();
      }
    };
  }

  function mount(options={}){
    if(typeof document==='undefined')return null;
    const target=options.target;
    const getPayload=typeof options.getPayload==='function'?options.getPayload:()=>options.payload;
    const prepareSection=typeof options.prepareSection==='function'?options.prepareSection:null;
    if(!target)throw new Error('PotatoTTSDrawer.mount requires a target element.');

    const speechOk=Boolean(root?.speechSynthesis&&root?.SpeechSynthesisUtterance&&root?.PotatoTTS?.TTSEngine);
    const settingsKey=options.settingsKey||'potato-tts-settings';
    const readSettings=()=>{try{return JSON.parse(localStorage.getItem(settingsKey)||'{}')}catch{return{}}};
    const writeSettings=patch=>{try{localStorage.setItem(settingsKey,JSON.stringify({...readSettings(),...patch}))}catch{/* storage optional */}};

    let payload=normalizePayload(getPayload()||{});
    let state='closed';
    let sectionId=payload.sections.find(x=>x.id==='both')?.id||payload.sections[0]?.id||'';
    let activeText='';
    let currentWord=null;
    let voices=[];
    let selectedVoice=null;
    let engine=null;
    let preparing=false;
    let startRequest=0;
    let preparationController=null;

    const host=el('section','ptts-drawer');host.dataset.state=state;
    const closed=el('button','ptts-trigger','🔊 Listen');closed.type='button';closed.setAttribute('aria-expanded','false');
    const panel=el('div','ptts-panel');panel.hidden=true;
    const rail=el('div','ptts-rail');
    const collapse=button('Collapse reader','⌃');
    const play=button('Play','▶');const pause=button('Pause','Ⅱ');const stop=button('Stop','■');
    const scope=el('select','ptts-select');scope.setAttribute('aria-label','Reading scope');
    const voice=el('select','ptts-select ptts-voice');voice.setAttribute('aria-label','Voice');
    const mute=button('Mute','🔊');
    const volume=el('input','ptts-volume');volume.type='range';volume.min='0';volume.max='1';volume.step='.05';volume.setAttribute('aria-label','Volume');
    const speed=el('select','ptts-select ptts-speed');speed.setAttribute('aria-label','Speed');
    [['0.75×','.75'],['0.9×','.9'],['1.0×','1'],['1.1×','1.1'],['1.25×','1.25'],['1.5×','1.5'],['1.75×','1.75'],['2.0×','2']].forEach(([label,value])=>{const o=new Option(label,value);if(value==='1')o.selected=true;speed.add(o)});
    const follow=button('Follow reading','🎯');follow.setAttribute('aria-pressed','false');
    const expand=button('Expand reading view','▣');
    const status=el('span','ptts-status');status.setAttribute('aria-live','polite');
    rail.append(collapse,play,pause,stop,scope,voice,mute,volume,speed,status,follow,expand);
    const viewport=el('div','ptts-viewport');viewport.hidden=true;viewport.setAttribute('aria-live','off');
    const label=el('div','ptts-label');const reading=el('div','ptts-reading');viewport.append(label,reading);
    panel.append(rail,viewport);host.append(closed,panel);target.append(host);

    const saved=readSettings();volume.value=String(Number.isFinite(Number(saved.volume))?clamp(Number(saved.volume),0,1):1);speed.value=saved.speed||'1';
    let followReading=saved.followReading===true;
    let lastVolume=Number(volume.value)||1;

    function updateFollowButton(){
      follow.setAttribute('aria-pressed',String(followReading));
      follow.setAttribute('aria-label',followReading?'Stop following reading':'Follow reading');
      follow.title=followReading?'Stop following reading':'Follow reading';
      host.dataset.follow=followReading?'true':'false';
    }

    function setState(next){
      state=next;host.dataset.state=state;
      const open=state!=='closed';closed.hidden=open;panel.hidden=!open;viewport.hidden=state!=='expanded';closed.setAttribute('aria-expanded',String(open));expand.textContent=state==='expanded'?'▤':'▣';expand.setAttribute('aria-label',state==='expanded'?'Compact reading view':'Expand reading view');
    }

    function updateScope(){
      const previous=sectionId;scope.replaceChildren();payload.sections.forEach(section=>scope.add(new Option(section.label,section.id)));
      sectionId=payload.sections.some(x=>x.id===previous)?previous:(payload.sections.find(x=>x.id==='both')?.id||payload.sections[0]?.id||'');scope.value=sectionId;
      label.textContent=[payload.label,resolveSection(payload,sectionId)?.label].filter(Boolean).join(' · ');
    }

    function refreshVoices(){
      if(!speechOk)return;
      voices=[...root.speechSynthesis.getVoices()];
      const wanted=root.PotatoTTS.chooseVoice(voices,readSettings().voice);
      voice.replaceChildren();voices.forEach((v,i)=>voice.add(new Option(`${v.name} · ${v.lang}`,String(i))));
      selectedVoice=wanted||voices[0]||null;voice.value=String(Math.max(0,voices.indexOf(selectedVoice)));
    }

    function currentOptions(){return{voice:selectedVoice,rate:Number(speed.value)||1,volume:Number(volume.value),pitch:1,autoRecover:true,maxChars:180};}
    function showPlain(text){reading.textContent=text||'';}
    function showWord(range){
      if(state!=='expanded')return;
      const parts=renderFocusedText(activeText,range);reading.replaceChildren(document.createTextNode(parts.before),el('mark','ptts-word',parts.active),document.createTextNode(parts.after));
      const mark=reading.querySelector('.ptts-word');mark?.scrollIntoView?.({block:followReading?'center':'nearest',inline:'nearest'});
    }
    function updateButtons(){
      const s=engine?.state||'idle';
      play.disabled=!speechOk||preparing;
      pause.disabled=!speechOk||preparing||!['speaking','paused'].includes(s);
      stop.disabled=!speechOk||(s==='idle'&&!preparing);
      pause.textContent=s==='paused'?'▶':'Ⅱ';
      status.textContent=!speechOk?'speech unavailable':preparing?'loading text…':s==='speaking'?'reading':s==='paused'?'paused':'';
      host.dataset.speech=preparing?'preparing':s;
    }

    if(speechOk){
      engine=new root.PotatoTTS.TTSEngine({synth:root.speechSynthesis,Utterance:root.SpeechSynthesisUtterance,onEvent:event=>{
        if(event.type==='boundary'&&event.absoluteWord){currentWord=event.absoluteWord;showWord(currentWord)}
        if(event.type==='chunkstart'&&state==='expanded'&&!currentWord)showPlain(activeText);
        if(['complete','stop','error'].includes(event.type)){currentWord=null;if(state==='expanded')showPlain(activeText)}
        updateButtons();
        options.onEvent?.({...event,sectionId,followReading});
      }});
      refreshVoices();root.speechSynthesis.addEventListener?.('voiceschanged',refreshVoices);
    }else{
      [play,pause,stop,voice,volume,speed,mute].forEach(node=>node.disabled=true);status.textContent='speech unavailable';
    }

    function cancelPendingStart(){
      startRequest+=1;
      preparationController?.abort?.();
      preparationController=null;
      if(preparing){preparing=false;updateButtons()}
    }
    async function start(){
      const request=++startRequest;
      if(prepareSection){
        preparing=true;
        preparationController=typeof AbortController==='function'?new AbortController():null;
        const controller=preparationController;
        updateButtons();
        try{
          const next=await prepareSection(sectionId,{signal:controller?.signal});
          if(request!==startRequest)return;
          if(next)payload=normalizePayload(next);
        }catch(error){
          if(error?.name==='AbortError')return;
          if(request===startRequest){
            preparing=false;
            status.textContent='could not load text';host.dataset.speech='error';
            options.onEvent?.({type:'error',error,sectionId,followReading});
          }
          return;
        }finally{
          if(preparationController===controller)preparationController=null;
          if(request===startRequest&&preparing){preparing=false;updateButtons()}
        }
      }
      if(request!==startRequest)return;
      payload=normalizePayload(getPayload()||payload);updateScope();activeText=buildReadingText(payload,sectionId);if(!activeText)return;currentWord=null;showPlain(activeText);engine?.start(activeText,currentOptions());if(state==='closed')setState('open');
    }
    function restartLive(){if(engine?.state!=='speaking')return;const at=currentWord?.start||engine.cursor||0;engine.start(activeText,{...currentOptions(),startAt:at});}
    function setPayload(next){
      const normalized=normalizePayload(next||{});const changed=normalized.id!==payload.id;
      payload=normalized;updateScope();
      if(changed&&engine&&engine.state!=='idle')engine.stop();
      activeText=buildReadingText(payload,sectionId);if(state==='expanded')showPlain(activeText);
    }
    function playSection(id){
      setPayload(getPayload()||payload);
      if(payload.sections.some(section=>section.id===id))sectionId=id;
      updateScope();
      setState('open');
      void start();
    }

    closed.addEventListener('click',()=>{setPayload(getPayload()||payload);setState('open')});
    collapse.addEventListener('click',()=>{cancelPendingStart();engine?.stop();setState('closed')});
    expand.addEventListener('click',()=>{setState(state==='expanded'?'open':'expanded');activeText=buildReadingText(payload,sectionId);showPlain(activeText)});
    play.addEventListener('click',()=>{if(engine?.state==='paused')engine.resume();else void start()});
    pause.addEventListener('click',()=>{if(engine?.state==='paused')engine.resume();else engine?.pause()});
    stop.addEventListener('click',()=>{cancelPendingStart();engine?.stop()});
    scope.addEventListener('change',()=>{cancelPendingStart();sectionId=scope.value;activeText=buildReadingText(payload,sectionId);engine?.stop();showPlain(activeText);label.textContent=[payload.label,resolveSection(payload,sectionId)?.label].filter(Boolean).join(' · ')});
    voice.addEventListener('change',()=>{selectedVoice=voices[Number(voice.value)]||null;writeSettings({voice:root.PotatoTTS.voiceIdentity(selectedVoice)});restartLive()});
    speed.addEventListener('change',()=>{writeSettings({speed:speed.value});restartLive()});
    volume.addEventListener('input',()=>{const v=Number(volume.value);if(v>0)lastVolume=v;mute.textContent=v===0?'🔇':v<.5?'🔉':'🔊';writeSettings({volume:v});restartLive()});
    mute.addEventListener('click',()=>{if(Number(volume.value)>0){lastVolume=Number(volume.value);volume.value='0'}else volume.value=String(lastVolume||1);volume.dispatchEvent(new Event('input'))});
    follow.addEventListener('click',()=>{followReading=!followReading;updateFollowButton();writeSettings({followReading});if(followReading&&currentWord)showWord(currentWord)});

    updateScope();updateFollowButton();updateButtons();
    return {element:host,setPayload,getPayload:()=>payload,playSection,open:()=>setState('open'),expand:()=>setState('expanded'),close:()=>setState('closed'),stop:()=>{cancelPendingStart();engine?.stop()},isFollowing:()=>followReading,engine};
  }

  return {normalizePayload,resolveSection,buildReadingText,renderFocusedText,buildNormalizedTextMap,centerDomRange,createPageHighlighter,mountSelectionAction,mount};
});
