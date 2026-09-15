/* PotatoTTS core — deterministic one-at-a-time speech engine. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoTTS=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
  const finite=(value,fallback)=>Number.isFinite(Number(value))?Number(value):fallback;

  function lastBoundary(text, regex, minimum){
    regex.lastIndex=0;
    let match=null, chosen=-1;
    while((match=regex.exec(text))){
      const end=match.index+match[0].length;
      if(end>=minimum)chosen=end;
      if(match[0].length===0)regex.lastIndex+=1;
    }
    return chosen;
  }

  function chunkResult(text,start,end){
    const raw=text.slice(start,end);
    const leading=raw.length-raw.trimStart().length;
    const trailing=raw.length-raw.trimEnd().length;
    const textStart=start+leading;
    const textEnd=Math.max(textStart,end-trailing);
    return {text:raw.slice(leading,raw.length-trailing),start,end,textStart,textEnd};
  }

  function nextChunk(input,start=0,maxChars=180){
    const text=String(input??'');
    const safeStart=clamp(Math.trunc(finite(start,0)),0,text.length);
    const limit=Math.max(8,Math.trunc(finite(maxChars,180)));
    if(safeStart>=text.length)return {text:'',start:safeStart,end:safeStart,textStart:safeStart,textEnd:safeStart};

    const hardEnd=Math.min(text.length,safeStart+limit);
    if(hardEnd===text.length){
      return chunkResult(text,safeStart,hardEnd);
    }

    const windowText=text.slice(safeStart,hardEnd);
    const minimum=Math.max(1,Math.floor(windowText.length*0.38));
    const boundaries=[
      /\n[\t ]*\n+/g,
      /[.!?…]+[”’"')\]]*[\t \n]+/g,
      /\n+/g,
      /[,;:]+[\t ]+/g,
      /[\t ]+/g,
    ];
    let relativeEnd=-1;
    for(const regex of boundaries){
      relativeEnd=lastBoundary(windowText,regex,minimum);
      if(relativeEnd>0)break;
    }
    if(relativeEnd<=0)relativeEnd=windowText.length;
    const end=Math.max(safeStart+1,safeStart+relativeEnd);
    return chunkResult(text,safeStart,end);
  }

  function boundaryRange(input,charIndex=0,charLength=0){
    const text=String(input??'');
    if(!text)return {start:0,end:0,text:''};
    let start=clamp(Math.trunc(finite(charIndex,0)),0,text.length);
    const reportedLength=Math.max(0,Math.trunc(finite(charLength,0)));
    if(reportedLength>0){
      const end=clamp(start+reportedLength,start,text.length);
      return {start,end,text:text.slice(start,end)};
    }
    const isWordChar=char=>Boolean(char&&/[\p{L}\p{N}\p{M}'’_-]/u.test(char));
    while(start<text.length&&!isWordChar(text[start]))start+=1;
    if(start>=text.length)return {start:text.length,end:text.length,text:''};
    let end=start+1;
    while(end<text.length&&isWordChar(text[end]))end+=1;
    return {start,end,text:text.slice(start,end)};
  }

  function voiceIdentity(voice){
    if(!voice)return null;
    return {
      voiceURI:String(voice.voiceURI||''),
      name:String(voice.name||''),
      lang:String(voice.lang||''),
    };
  }

  function chooseVoice(voices,saved){
    const list=Array.isArray(voices)?voices:[];
    if(!list.length)return null;
    if(!saved)return list.find(v=>v.default)||list[0];
    const wanted=typeof saved==='string'?{voiceURI:saved}:saved;
    const uri=String(wanted.voiceURI||'');
    const name=String(wanted.name||'');
    const lang=String(wanted.lang||'');
    return (uri&&list.find(v=>String(v.voiceURI||'')===uri))
      ||(name&&lang&&list.find(v=>v.name===name&&v.lang===lang))
      ||(name&&list.find(v=>v.name===name))
      ||(lang&&list.find(v=>v.lang===lang))
      ||list.find(v=>v.default)
      ||list[0];
  }

  function defaultWatchdogFor(chunkLength,rate){
    const safeRate=clamp(finite(rate,1),0.25,4);
    const estimatedMs=(Math.max(1,chunkLength)/(12*safeRate))*1000;
    return clamp(Math.round(estimatedMs+7000),10000,35000);
  }

  class TTSEngine{
    constructor(config={}){
      if(!config.synth)throw new Error('A speechSynthesis-compatible object is required.');
      if(typeof config.Utterance!=='function')throw new Error('A SpeechSynthesisUtterance constructor is required.');
      this.synth=config.synth;
      this.Utterance=config.Utterance;
      this.setTimer=config.setTimer||((fn,ms)=>setTimeout(fn,ms));
      this.clearTimer=config.clearTimer||(id=>clearTimeout(id));
      this.watchdogFor=config.watchdogFor||defaultWatchdogFor;
      this.onEvent=typeof config.onEvent==='function'?config.onEvent:()=>{};
      this.baseMaxChars=Math.max(8,Math.trunc(finite(config.maxChars,180)));
      this.minChars=Math.max(8,Math.min(this.baseMaxChars,Math.trunc(finite(config.minChars,80))));
      this.maxRecoveries=Math.max(0,Math.trunc(finite(config.maxRecoveries,2)));
      this.effectiveMaxChars=this.baseMaxChars;
      this.state='idle';
      this.session=0;
      this.utteranceSerial=0;
      this.text='';
      this.cursor=0;
      this.currentChunk=null;
      this.currentUtterance=null;
      this.currentSerial=0;
      this.watchdogTimer=null;
      this.recoveriesForChunk=0;
      this.recoveryCount=0;
      this.pendingNext=false;
      this.options={voice:null,rate:1,pitch:1,volume:1,autoRecover:true};
    }

    get progress(){return this.text.length?clamp(this.cursor/this.text.length,0,1):0;}

    _emit(type,extra={}){
      this.onEvent({
        type,state:this.state,cursor:this.cursor,total:this.text.length,
        progress:this.progress,chunk:this.currentChunk,
        recoveryCount:this.recoveryCount,effectiveMaxChars:this.effectiveMaxChars,
        ...extra,
      });
    }

    updateOptions(patch={}){
      if('voice'in patch)this.options.voice=patch.voice||null;
      if('rate'in patch)this.options.rate=clamp(finite(patch.rate,1),0.5,2.5);
      if('pitch'in patch)this.options.pitch=clamp(finite(patch.pitch,1),0,2);
      if('volume'in patch)this.options.volume=clamp(finite(patch.volume,1),0,1);
      if('autoRecover'in patch)this.options.autoRecover=Boolean(patch.autoRecover);
      if('maxChars'in patch){
        this.baseMaxChars=Math.max(this.minChars,Math.trunc(finite(patch.maxChars,this.baseMaxChars)));
        this.effectiveMaxChars=this.baseMaxChars;
      }
      return {...this.options,maxChars:this.baseMaxChars};
    }

    start(input,options={}){
      const text=String(input??'');
      const startAt=clamp(Math.trunc(finite(options.startAt,0)),0,text.length);
      this.session+=1;
      this.utteranceSerial+=1;
      this._clearWatchdog();
      try{this.synth.cancel();}catch(_){/* browser quirk */}
      this.text=text;
      this.cursor=startAt;
      this.currentChunk=null;
      this.currentUtterance=null;
      this.currentSerial=0;
      this.recoveriesForChunk=0;
      this.recoveryCount=0;
      this.pendingNext=false;
      this.effectiveMaxChars=Math.max(this.minChars,Math.trunc(finite(options.maxChars,this.baseMaxChars)));
      this.updateOptions(options);
      if(!text.trim()||startAt>=text.length){
        this.state='idle';
        this._emit('empty');
        return false;
      }
      this.state='speaking';
      const session=this.session;
      this._emit('start');
      this._speakNext(session);
      return true;
    }

    pause(){
      if(this.state!=='speaking')return false;
      this._clearWatchdog();
      try{this.synth.pause();}catch(_){return false;}
      this.state='paused';
      this._emit('pause');
      return true;
    }

    resume(){
      if(this.state!=='paused')return false;
      try{this.synth.resume();}catch(_){return false;}
      this.state='speaking';
      this._emit('resume');
      if(this.pendingNext||!this.currentUtterance){
        this.pendingNext=false;
        this._speakNext(this.session);
      }else if(this.currentChunk){
        this._armWatchdog(this.session,this.currentSerial,this.currentChunk);
      }
      return true;
    }

    stop(){
      this.session+=1;
      this.utteranceSerial+=1;
      this._clearWatchdog();
      this.currentUtterance=null;
      this.currentChunk=null;
      this.currentSerial=0;
      this.pendingNext=false;
      this.state='idle';
      try{this.synth.cancel();}catch(_){/* browser quirk */}
      this._emit('stop');
      return true;
    }

    _valid(session,serial){
      return session===this.session&&serial===this.currentSerial&&(this.state==='speaking'||this.state==='paused');
    }

    _speakNext(session){
      if(session!==this.session||this.state!=='speaking')return;
      if(this.cursor>=this.text.length){
        this._clearWatchdog();
        this.currentChunk=null;
        this.currentUtterance=null;
        this.state='idle';
        this.cursor=this.text.length;
        this._emit('complete');
        return;
      }
      let chunk=null;
      while(this.cursor<this.text.length){
        chunk=nextChunk(this.text,this.cursor,this.effectiveMaxChars);
        if(chunk.end<=this.cursor){
          this.state='error';
          this._emit('error',{message:'The text chunker could not advance.'});
          return;
        }
        if(chunk.text)break;
        this.cursor=chunk.end;
      }
      if(this.cursor>=this.text.length&&!chunk?.text){
        this._clearWatchdog();
        this.currentChunk=null;
        this.currentUtterance=null;
        this.state='idle';
        this.cursor=this.text.length;
        this._emit('complete');
        return;
      }
      const utterance=new this.Utterance(chunk.text);
      utterance.voice=this.options.voice||null;
      if(this.options.voice?.lang)utterance.lang=this.options.voice.lang;
      utterance.rate=this.options.rate;
      utterance.pitch=this.options.pitch;
      utterance.volume=this.options.volume;
      const serial=++this.utteranceSerial;
      this.currentSerial=serial;
      this.currentChunk=chunk;
      this.currentUtterance=utterance;

      utterance.onstart=()=>{
        if(!this._valid(session,serial))return;
        this._emit('chunkstart');
        this._armWatchdog(session,serial,chunk);
      };
      utterance.onboundary=(event)=>{
        if(!this._valid(session,serial))return;
        const local=clamp(Math.trunc(finite(event?.charIndex,0)),0,chunk.text.length);
        const charLength=Math.max(0,Math.trunc(finite(event?.charLength,0)));
        const absolute=clamp((chunk.textStart??chunk.start)+local,chunk.textStart??chunk.start,chunk.textEnd??chunk.end);
        const advanced=absolute>this.cursor;
        if(advanced)this.cursor=absolute;
        const word=boundaryRange(chunk.text,local,charLength);
        const offset=chunk.textStart??chunk.start;
        const absoluteWord={start:offset+word.start,end:offset+word.end,text:word.text};
        this._emit('boundary',{boundary:{charIndex:local,charLength,name:String(event?.name||'')},word,absoluteWord});
        if(advanced&&this.state==='speaking')this._armWatchdog(session,serial,chunk);
      };
      utterance.onend=()=>{
        if(!this._valid(session,serial))return;
        this._clearWatchdog();
        this.cursor=chunk.end;
        this.currentUtterance=null;
        this.currentChunk=null;
        this.recoveriesForChunk=0;
        this._emit('chunkend',{chunk});
        if(this.state==='paused')this.pendingNext=true;
        else this._speakNext(session);
      };
      utterance.onerror=(event)=>{
        if(!this._valid(session,serial))return;
        this._clearWatchdog();
        const code=String(event?.error||'speech-error');
        if(this.options.autoRecover&&code!=='not-allowed'&&code!=='audio-busy'){
          this._recover('error:'+code,session,serial);
        }else{
          this._fail(`Speech synthesis error: ${code}`,session,serial);
        }
      };

      this._emit('chunkqueued');
      try{
        this.synth.speak(utterance);
        this._armWatchdog(session,serial,chunk);
      }catch(error){
        this._fail(error?.message||'Unable to start speech synthesis.',session,serial);
      }
    }

    _armWatchdog(session,serial,chunk){
      this._clearWatchdog();
      if(!this.options.autoRecover||this.state!=='speaking')return;
      const ms=Math.max(1000,finite(this.watchdogFor(chunk.text.length,this.options.rate),15000));
      this.watchdogTimer=this.setTimer(()=>{
        this.watchdogTimer=null;
        if(this._valid(session,serial)&&this.state==='speaking')this._recover('watchdog',session,serial);
      },ms);
    }

    _clearWatchdog(){
      if(this.watchdogTimer!==null){
        try{this.clearTimer(this.watchdogTimer);}catch(_){/* noop */}
        this.watchdogTimer=null;
      }
    }

    _recover(reason,session,serial){
      if(!this._valid(session,serial)||this.state!=='speaking')return;
      this._clearWatchdog();
      if(this.recoveriesForChunk>=this.maxRecoveries){
        this._fail('Speech stalled repeatedly. Playback stopped instead of looping forever.',session,serial);
        return;
      }
      this.recoveriesForChunk+=1;
      this.recoveryCount+=1;
      const restartAt=this.currentChunk?.start??this.cursor;
      this.cursor=restartAt;
      this.effectiveMaxChars=Math.max(this.minChars,Math.floor(this.effectiveMaxChars*0.72));
      this.currentSerial=++this.utteranceSerial;
      this.currentUtterance=null;
      this.pendingNext=false;
      try{this.synth.cancel();}catch(_){/* browser quirk */}
      this._emit('recovery',{reason});
      const currentSession=this.session;
      this.setTimer(()=>{
        if(currentSession===this.session&&this.state==='speaking')this._speakNext(currentSession);
      },80);
    }

    _fail(message,session,serial){
      if(session!==this.session)return;
      if(serial!==undefined&&serial!==this.currentSerial)return;
      this._clearWatchdog();
      this.currentSerial=++this.utteranceSerial;
      this.currentUtterance=null;
      this.state='error';
      try{this.synth.cancel();}catch(_){/* browser quirk */}
      this._emit('error',{message});
    }
  }

  return {nextChunk,boundaryRange,voiceIdentity,chooseVoice,defaultWatchdogFor,TTSEngine};
});
