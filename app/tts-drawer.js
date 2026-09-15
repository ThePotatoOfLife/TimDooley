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

  function mount(options={}){
    if(typeof document==='undefined')return null;
    const target=options.target;
    const getPayload=typeof options.getPayload==='function'?options.getPayload:()=>options.payload;
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
    const expand=button('Expand reading view','▣');
    const status=el('span','ptts-status');status.setAttribute('aria-live','polite');
    rail.append(collapse,play,pause,stop,scope,voice,mute,volume,speed,status,expand);
    const viewport=el('div','ptts-viewport');viewport.hidden=true;viewport.setAttribute('aria-live','off');
    const label=el('div','ptts-label');const reading=el('div','ptts-reading');viewport.append(label,reading);
    panel.append(rail,viewport);host.append(closed,panel);target.append(host);

    const saved=readSettings();volume.value=String(Number.isFinite(Number(saved.volume))?clamp(Number(saved.volume),0,1):1);speed.value=saved.speed||'1';
    let lastVolume=Number(volume.value)||1;

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
      const wanted=root.PotatoTTS.chooseVoice(voices,saved.voice);
      voice.replaceChildren();voices.forEach((v,i)=>voice.add(new Option(`${v.name} · ${v.lang}`,String(i))));
      selectedVoice=wanted||voices[0]||null;voice.value=String(Math.max(0,voices.indexOf(selectedVoice)));
    }

    function currentOptions(){return{voice:selectedVoice,rate:Number(speed.value)||1,volume:Number(volume.value),pitch:1,autoRecover:true,maxChars:180};}
    function showPlain(text){reading.textContent=text||'';}
    function showWord(range){
      if(state!=='expanded')return;
      const parts=renderFocusedText(activeText,range);reading.replaceChildren(document.createTextNode(parts.before),el('mark','ptts-word',parts.active),document.createTextNode(parts.after));
      const mark=reading.querySelector('.ptts-word');mark?.scrollIntoView?.({block:'nearest',inline:'nearest'});
    }
    function updateButtons(){const s=engine?.state||'idle';pause.disabled=!['speaking','paused'].includes(s);stop.disabled=s==='idle';pause.textContent=s==='paused'?'▶':'Ⅱ';status.textContent=s==='speaking'?'reading':s==='paused'?'paused':'';host.dataset.speech=s;}

    if(speechOk){
      engine=new root.PotatoTTS.TTSEngine({synth:root.speechSynthesis,Utterance:root.SpeechSynthesisUtterance,onEvent:event=>{
        if(event.type==='boundary'&&event.absoluteWord){currentWord=event.absoluteWord;showWord(currentWord)}
        if(event.type==='chunkstart'&&state==='expanded'&&!currentWord)showPlain(activeText);
        if(['complete','stop','error'].includes(event.type)){currentWord=null;if(state==='expanded')showPlain(activeText)}
        updateButtons();
      }});
      refreshVoices();root.speechSynthesis.addEventListener?.('voiceschanged',refreshVoices);
    }else{
      [play,pause,stop,voice,volume,speed,mute].forEach(node=>node.disabled=true);status.textContent='speech unavailable';
    }

    function start(){
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
      start();
    }

    closed.addEventListener('click',()=>{setPayload(getPayload()||payload);setState('open')});
    collapse.addEventListener('click',()=>{engine?.stop();setState('closed')});
    expand.addEventListener('click',()=>{setState(state==='expanded'?'open':'expanded');activeText=buildReadingText(payload,sectionId);showPlain(activeText)});
    play.addEventListener('click',()=>{if(engine?.state==='paused')engine.resume();else start()});
    pause.addEventListener('click',()=>{if(engine?.state==='paused')engine.resume();else engine?.pause()});
    stop.addEventListener('click',()=>engine?.stop());
    scope.addEventListener('change',()=>{sectionId=scope.value;activeText=buildReadingText(payload,sectionId);engine?.stop();showPlain(activeText);label.textContent=[payload.label,resolveSection(payload,sectionId)?.label].filter(Boolean).join(' · ')});
    voice.addEventListener('change',()=>{selectedVoice=voices[Number(voice.value)]||null;writeSettings({voice:root.PotatoTTS.voiceIdentity(selectedVoice)});restartLive()});
    speed.addEventListener('change',()=>{writeSettings({speed:speed.value});restartLive()});
    volume.addEventListener('input',()=>{const v=Number(volume.value);if(v>0)lastVolume=v;mute.textContent=v===0?'🔇':v<.5?'🔉':'🔊';writeSettings({volume:v});restartLive()});
    mute.addEventListener('click',()=>{if(Number(volume.value)>0){lastVolume=Number(volume.value);volume.value='0'}else volume.value=String(lastVolume||1);volume.dispatchEvent(new Event('input'))});

    updateScope();updateButtons();
    return {element:host,setPayload,getPayload:()=>payload,playSection,open:()=>setState('open'),expand:()=>setState('expanded'),close:()=>setState('closed'),stop:()=>engine?.stop(),engine};
  }

  return {normalizePayload,resolveSection,buildReadingText,renderFocusedText,mount};
});