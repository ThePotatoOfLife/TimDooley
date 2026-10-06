(()=>{
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const fmtDate=s=>{if(!s)return '—';const d=new Date(s);if(Number.isNaN(+d))return s;return new Intl.DateTimeFormat('en-GB',{year:'numeric',month:'short',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false}).format(d)};
const dateOnly=s=>s?fmtDate(s).replace(/,? \d{2}:\d{2}$/,''):'undated';
Promise.all([fetch('../data/works/music-discography.json').then(r=>{if(!r.ok)throw new Error('master catalogue '+r.status);return r.json()}),fetch('../data/works/music-archive-dated.json').then(r=>{if(!r.ok)throw new Error('dated archive '+r.status);return r.json()})]).then(([master,dated])=>{
 const albums=new Map();
 const key=s=>String(s||'').toLowerCase().replace(/[’']/g,'').replace(/alternate version/g,'1').replace(/[^a-z0-9]+/g,' ').trim();
 (master.albums||[]).forEach(a=>albums.set(Number(a.number),{...a,source_kind:'master-sequence',tracks:(a.tracks||[]).map(t=>({...t,source_order:t.position,created_local:null,media_archived_separately:true}))}));
 (dated.albums||[]).forEach(a=>{
   const n=Number(a.number);
   if(albums.has(n)){
     const base=albums.get(n), byTitle=new Map((a.tracks||[]).map(t=>[key(t.title),t]));
     base.date_span=a.date_span;
     base.source_kind='master-sequence + dated-folder-manifest';
     base.tracks=(base.tracks||[]).map(t=>{const d=byTitle.get(key(t.title));return d?{...t,created_local:d.created_local,filename:d.filename||t.filename,format:d.format||t.format,size_display:d.size_display||t.size_display}:{...t}});
   } else albums.set(n,{...a,source_kind:'dated-folder-manifest'});
 });
 const albumList=[...albums.values()].sort((a,b)=>a.number-b.number);
 $('#statAlbums').textContent=dated.summary.album_count; $('#statTracks').textContent=dated.summary.track_count; $('#statDated').textContent=dated.summary.dated_manifest_album_numbers.length;
 const grid=$('#albumGrid'), filter=$('#albumFilter');
 albumList.forEach(a=>{const b=document.createElement('button');b.type='button';b.className='album-card';b.dataset.album=a.number;const span=a.date_span?`${dateOnly(a.date_span.first)} → ${dateOnly(a.date_span.last)}`:(a.runtime?`master runtime ${a.runtime}`:'dates unresolved');const status=a.source_kind==='master-sequence'?'supplied sequence':'dated folder manifest';b.innerHTML=`<em>Album ${a.number}</em><strong>${esc(a.title)}</strong><span>${a.track_count} tracks · ${esc(span)}</span><small>${esc(status)}</small>`;b.addEventListener('click',()=>{filter.value=String(a.number);$$('.album-card').forEach(x=>x.classList.toggle('active',x===b));render()});grid.appendChild(b);const o=document.createElement('option');o.value=a.number;o.textContent=`Album ${a.number} — ${a.title}`;filter.appendChild(o)});
 let all=[]; albumList.forEach(a=>(a.tracks||[]).forEach((t,i)=>all.push({...t,album_number:a.number,album_title:a.title,source_kind:a.source_kind,source_order:t.source_order??t.position??i+1})));
 const search=$('#trackSearch'), sort=$('#trackSort'), body=$('#trackBody'), count=$('#trackResultCount'), resultTitle=$('#trackResultTitle');
 function render(){const q=search.value.trim().toLowerCase(), av=filter.value;let rows=all.filter(t=>(av==='all'||String(t.album_number)===av)&&(!q||[t.title,t.album_title,t.created_local,t.format,t.media_title].filter(Boolean).join(' ').toLowerCase().includes(q)));const sv=sort.value;if(sv==='created-asc')rows.sort((a,b)=>(a.created_local||'9999').localeCompare(b.created_local||'9999')||a.album_number-b.album_number);else if(sv==='created-desc')rows.sort((a,b)=>(b.created_local||'').localeCompare(a.created_local||'')||a.album_number-b.album_number);else if(sv==='title')rows.sort((a,b)=>a.title.localeCompare(b.title));else rows.sort((a,b)=>a.album_number-b.album_number||(a.source_order||0)-(b.source_order||0));count.textContent=`${rows.length} of ${all.length} tracks`;resultTitle.textContent=av==='all'?'Catalogue':`Album ${av}`;body.innerHTML=rows.length?rows.map(t=>`<tr><td>${t.album_number}</td><td class="track-title">${esc(t.title)}${t.media_title&&t.media_title!==t.title?`<br><small class="track-muted">media title: ${esc(t.media_title)}</small>`:''}</td><td>${esc(fmtDate(t.created_local))}</td><td>${esc(t.duration||'—')}</td><td>${esc(t.format||'—')}<br><small class="track-muted">${t.media_archived_separately?'master archived separately':(t.source_kind==='master-sequence'?'supplied master sequence':'folder manifest')}</small></td></tr>`).join(''):`<tr><td colspan="5" class="track-empty">No matching tracks.</td></tr>`}
 search.addEventListener('input',render);sort.addEventListener('change',render);filter.addEventListener('change',()=>{$$('.album-card').forEach(x=>x.classList.toggle('active',x.dataset.album===filter.value));render()});render();
}).catch(err=>{document.querySelector('#trackBody').innerHTML=`<tr><td colspan="5" class="track-empty">Archive data failed to load: ${esc(err.message)}</td></tr>`;document.querySelector('#trackResultCount').textContent='load error'});

/* TimAmp */
const amp=$('#timamp'), audio=$('#ampAudio'), files=$('#ampFiles'), title=$('#ampTitle'), meta=$('#ampMeta'), clock=$('#ampClock'), seek=$('#ampSeek'), playlist=$('#ampPlaylist'), status=$('#ampStatus'), bars=$$('#ampBars i'), scene=$('#ampScene'), meterL=$('#ampMeterL'), meterR=$('#ampMeterR'), meterLDb=$('#ampMeterLDb'), meterRDb=$('#ampMeterRDb'), clipL=$('#ampClipL'), clipR=$('#ampClipR'), signalState=$('#ampSignalState'), signalFormat=$('#ampSignalFormat'), signalRate=$('#ampSignalRate'), peakHold=$('#ampPeakHold');let tracks=[],current=-1,shuffle=false,repeat=false,eqBypassed=false,ctx=null,source=null,analyser=null,data=null,timeData=null,raf=0,imgUrl='',preampNode=null,panNode=null,masterNode=null,eqNodes=[],peakHoldValue=0,clipUntil=0;
const time=s=>{if(!Number.isFinite(s)||s<0)return'00:00';return Math.floor(s/60).toString().padStart(2,'0')+':'+Math.floor(s%60).toString().padStart(2,'0')};
const clean=n=>n.replace(/\.[^.]+$/,'').replace(/[_-]+/g,' ').trim()||n;const ext=n=>(n.match(/\.([^.]+)$/)||['','AUDIO'])[1].toUpperCase();
function graph(){
 if(ctx)return;
 try{
  ctx=new(window.AudioContext||window.webkitAudioContext)();
  source=ctx.createMediaElementSource(audio);
  preampNode=ctx.createGain();
  const freqs=[31,62,125,250,500,1000,2000,4000,8000,16000];
  eqNodes=freqs.map((freq,i)=>{const f=ctx.createBiquadFilter();f.type='peaking';f.frequency.value=freq;f.Q.value=i<2?.8:1.05;f.gain.value=0;return f});
  panNode=ctx.createStereoPanner?ctx.createStereoPanner():ctx.createGain();
  masterNode=ctx.createGain();
  analyser=ctx.createAnalyser();analyser.fftSize=128;analyser.smoothingTimeConstant=.72;
  let node=source;node.connect(preampNode);node=preampNode;
  eqNodes.forEach(f=>{node.connect(f);node=f});
  node.connect(panNode);panNode.connect(masterNode);masterNode.connect(analyser);analyser.connect(ctx.destination);
  data=new Uint8Array(analyser.frequencyBinCount);timeData=new Uint8Array(analyser.fftSize);if(signalRate)signalRate.textContent=(ctx.sampleRate/1000).toFixed(1)+' kHz';
  preampNode.gain.value=Math.pow(10,(+$('#ampPreamp').value||0)/20);
  masterNode.gain.value=(+$('#ampVolume').value||82)/100;
  if(panNode.pan)panNode.pan.value=(+$('#ampBalance').value||0)/100;
  $('.amp-eq').forEach((el,i)=>{if(eqNodes[i])eqNodes[i].gain.value=+el.value||0});
 }catch(e){status.textContent='VISUALIZER / EQ FALLBACK ACTIVE.'}
}
function draw(){
 cancelAnimationFrame(raf);
 const db=v=>v<=.0001?-60:20*Math.log10(v);
 const loop=()=>{
  let levels,peak=0,avg=0;
  if(analyser&&data){
   analyser.getByteFrequencyData(data);
   analyser.getByteTimeDomainData(timeData);
   levels=bars.map((_,i)=>data[Math.min(data.length-1,Math.floor(i*data.length/bars.length))]/255);
   let sum=0;
   for(let i=0;i<timeData.length;i++){const v=Math.abs((timeData[i]-128)/128);peak=Math.max(peak,v);sum+=v*v}
   avg=Math.sqrt(sum/timeData.length);
  } else {
   levels=bars.map((_,i)=>audio.paused?.025:.12+Math.abs(Math.sin(Date.now()/190+i*.47))*.48);
   peak=audio.paused?0:.34;avg=audio.paused?0:.18;
  }
  bars.forEach((b,i)=>b.style.height=Math.max(3,Math.round(levels[i]*100))+'%');
  const wobble=analyser?Math.sin(performance.now()/47)*.018:0;
  const left=Math.max(0,Math.min(1,peak+wobble)),right=Math.max(0,Math.min(1,peak-wobble*.7));
  if(meterL)meterL.style.width=(left*100)+'%';if(meterR)meterR.style.width=(right*100)+'%';
  if(meterLDb)meterLDb.textContent=left?db(left).toFixed(1)+' dB':'-∞ dB';if(meterRDb)meterRDb.textContent=right?db(right).toFixed(1)+' dB':'-∞ dB';
  peakHoldValue=Math.max(peakHoldValue*.997,peak);if(peakHold)peakHold.textContent=peakHoldValue?db(peakHoldValue).toFixed(1)+' dB':'-∞ dB';
  if(peak>.96)clipUntil=performance.now()+900;const clipping=performance.now()<clipUntil;if(clipL)clipL.classList.toggle('on',clipping);if(clipR)clipR.classList.toggle('on',clipping);
  raf=requestAnimationFrame(loop)
 };
 loop()
}
function renderPlaylist(){playlist.innerHTML=tracks.length?'':`<div class="amp-status" style="padding:8px">[ MEDIA BAY EMPTY ]</div>`;tracks.forEach((t,i)=>{const b=document.createElement('button');b.type='button';b.className='amp-track'+(i===current?' active':'');b.innerHTML=`<span>${String(i+1).padStart(2,'0')}</span><span>${esc(clean(t.file.name))}</span><span>${esc(ext(t.file.name))}</span>`;b.addEventListener('click',()=>load(i,true));playlist.appendChild(b)})}
function load(i,autoplay){if(!tracks.length)return;current=Math.max(0,Math.min(i,tracks.length-1));const t=tracks[current];audio.src=t.url;title.textContent=clean(t.file.name).toUpperCase();meta.textContent='TRACK '+(current+1)+' / '+tracks.length+' · '+ext(t.file.name)+' · '+(t.file.size/1048576).toFixed(1)+' MB';if(signalFormat)signalFormat.textContent=ext(t.file.name);if(signalState)signalState.textContent='READY';seek.value='0';renderPlaylist();if(autoplay){graph();if(ctx&&ctx.state==='suspended')ctx.resume();audio.play().catch(()=>status.textContent='PRESS PLAY TO START SIGNAL.')}}
function add(fs){const arr=[...fs].filter(f=>f.type.startsWith('audio/')||f.type==='video/mp4'||/\.(mp3|m4a|mp4|aac|wav|ogg|flac)$/i.test(f.name));if(!arr.length){status.textContent='NO COMPATIBLE AUDIO FOUND.';return}arr.forEach(file=>tracks.push({file,url:URL.createObjectURL(file)}));if(current<0)load(0,false);else renderPlaylist();status.textContent=`${arr.length} FILE(S) PATCHED IN.`}
function nextIndex(){if(!tracks.length)return-1;if(shuffle&&tracks.length>1){let n=current;while(n===current)n=Math.floor(Math.random()*tracks.length);return n}return(current+1)%tracks.length}
files.addEventListener('change',e=>{add(e.target.files);files.value=''});
const setReadout=(sel,val)=>{const o=$(sel);if(o)o.textContent=val};
$('#ampPreamp').addEventListener('input',e=>{const v=+e.target.value;setReadout('#ampPreampOut',(v>0?'+':'')+v+' dB');if(preampNode)preampNode.gain.value=Math.pow(10,v/20)});
$('.amp-eq').forEach((el,i)=>el.addEventListener('input',e=>{const v=+e.target.value;const out=document.querySelector('[data-eq-out="'+e.target.dataset.freq+'"]');if(out)out.textContent=(v>0?'+':'')+v;if(eqNodes[i])eqNodes[i].gain.value=v}));
$('#ampEqFlat').addEventListener('click',()=>{$('.amp-eq').forEach((el,i)=>{el.value=0;const out=document.querySelector('[data-eq-out="'+el.dataset.freq+'"]');if(out)out.textContent='0';if(eqNodes[i])eqNodes[i].gain.value=0});$('#ampPreamp').value=0;setReadout('#ampPreampOut','0 dB');if(preampNode)preampNode.gain.value=1;status.textContent='EQ CURVE RESET // FLAT.'});
const eqPresets={warm:[2,2,1,1,0,0,-1,-1,0,1],presence:[-1,-1,0,0,1,2,3,2,1,0],loudness:[3,2,1,0,-1,-1,0,1,2,3],speech:[-3,-2,-1,0,1,3,3,1,-1,-2]};
function applyEq(values,name){$$('.amp-eq').forEach((el,i)=>{const v=values[i]??0;el.value=v;const out=document.querySelector('[data-eq-out="'+el.dataset.freq+'"]');if(out)out.textContent=(v>0?'+':'')+v;if(eqNodes[i])eqNodes[i].gain.value=eqBypassed?0:v});$('#ampEqState').textContent=name.toUpperCase();status.textContent='EQ PRESET // '+name.toUpperCase();}
$$('.amp-preset').forEach(btn=>btn.addEventListener('click',()=>applyEq(eqPresets[btn.dataset.preset]||[],btn.dataset.preset)));
$('#ampEqBypass').addEventListener('click',e=>{eqBypassed=!eqBypassed;e.currentTarget.textContent=eqBypassed?'EQ OUT':'EQ IN';$$('.amp-eq').forEach((el,i)=>{if(eqNodes[i])eqNodes[i].gain.value=eqBypassed?0:(+el.value||0)});$('#ampEqState').textContent=eqBypassed?'BYPASS':'ACTIVE';status.textContent='EQ '+(eqBypassed?'BYPASSED':'ENGAGED')+'.';});

$('#ampVolume').addEventListener('input',e=>{const v=+e.target.value;setReadout('#ampVolumeOut',v+'%');if(masterNode)masterNode.gain.value=v/100});
$('#ampBalance').addEventListener('input',e=>{const v=+e.target.value;setReadout('#ampBalanceOut',v===0?'C':v<0?'L '+Math.abs(v):'R '+v);if(panNode&&panNode.pan)panNode.pan.value=v/100});
$('#ampPlay').addEventListener('click',()=>{if(!tracks.length){status.textContent='MEDIA BAY EMPTY.';return}graph();if(ctx&&ctx.state==='suspended')ctx.resume();audio.play().then(()=>{if(signalState)signalState.textContent='PLAY'}).catch(()=>status.textContent='FORMAT NOT SUPPORTED.')});$('#ampPause').addEventListener('click',()=>{audio.pause();if(signalState)signalState.textContent='PAUSE'});$('#ampStop').addEventListener('click',()=>{audio.pause();audio.currentTime=0;if(signalState)signalState.textContent='STOP'});$('#ampPrev').addEventListener('click',()=>{if(!tracks.length)return;if(audio.currentTime>3)audio.currentTime=0;else load((current-1+tracks.length)%tracks.length,true)});$('#ampNext').addEventListener('click',()=>{const n=nextIndex();if(n>=0)load(n,true)});$('#ampShuffle').addEventListener('click',e=>{shuffle=!shuffle;e.currentTarget.textContent='SHUF '+(shuffle?'ON':'OFF');$('#ampModeOut').textContent=shuffle?'SHUFFLE':(repeat?'REPEAT':'NORMAL')});$('#ampRepeat').addEventListener('click',e=>{repeat=!repeat;e.currentTarget.textContent='RPT '+(repeat?'ON':'OFF');$('#ampModeOut').textContent=repeat?'REPEAT':(shuffle?'SHUFFLE':'NORMAL')});seek.addEventListener('input',()=>{if(audio.duration)audio.currentTime=(+seek.value/1000)*audio.duration});audio.addEventListener('timeupdate',()=>{seek.value=audio.duration?String(Math.round(audio.currentTime/audio.duration*1000)):'0';clock.textContent=time(audio.currentTime)+' / '+time(audio.duration)});audio.addEventListener('ended',()=>{if(repeat){audio.currentTime=0;audio.play()}else{const n=nextIndex();if(n>=0)load(n,true)}});audio.addEventListener('error',()=>status.textContent='DECODE ERROR / UNSUPPORTED SIGNAL.');
$$('.amp-skin').forEach(b=>b.addEventListener('click',()=>{amp.dataset.skin=b.dataset.skin;$$('.amp-skin').forEach(x=>x.classList.toggle('active',x===b));amp.style.removeProperty('--amp-bg');amp.style.removeProperty('--amp-rack');amp.style.removeProperty('--amp-lamp')}));$('#ampApplyCustom').addEventListener('click',()=>{amp.style.setProperty('--amp-bg',$('#ampBg').value);amp.style.setProperty('--amp-rack',$('#ampRack').value);amp.style.setProperty('--amp-lamp',$('#ampLampColor').value);$$('.amp-skin').forEach(x=>x.classList.remove('active'));status.textContent='CUSTOM HARDWARE SKIN APPLIED.'});$('#ampSkinImage').addEventListener('change',e=>{const f=e.target.files?.[0];if(!f)return;if(imgUrl)URL.revokeObjectURL(imgUrl);imgUrl=URL.createObjectURL(f);scene.style.backgroundImage=`linear-gradient(rgba(0,0,0,.18),rgba(0,0,0,.18)),url("${imgUrl}")`;status.textContent='CUSTOM SKIN IMAGE LOADED.'});$('#ampClearImage').addEventListener('click',()=>{if(imgUrl)URL.revokeObjectURL(imgUrl);imgUrl='';scene.style.backgroundImage='';$('#ampSkinImage').value='';status.textContent='SKIN IMAGE CLEARED.'});$('#ampClear').addEventListener('click',()=>{audio.pause();audio.removeAttribute('src');tracks.forEach(t=>URL.revokeObjectURL(t.url));tracks=[];current=-1;title.textContent='NO TRACK LOADED';meta.textContent='LOCAL SIGNAL WAITING';clock.textContent='00:00 / 00:00';seek.value='0';renderPlaylist();if(signalState)signalState.textContent='IDLE';if(signalFormat)signalFormat.textContent='—';peakHoldValue=0;if(peakHold)peakHold.textContent='-∞ dB';status.textContent='MEDIA BAY EJECTED.'});

// Hardware state persistence: skin + EQ + master/balance only; local media is never persisted or uploaded.
const saveAmpState=()=>{try{localStorage.setItem('timamp-state-v1',JSON.stringify({skin:amp.dataset.skin,eq:$('.amp-eq').map(x=>+x.value),pre:+$('#ampPreamp').value,vol:+$('#ampVolume').value,bal:+$('#ampBalance').value}))}catch(e){}};
const restoreAmpState=()=>{try{const s=JSON.parse(localStorage.getItem('timamp-state-v1')||'null');if(!s)return;if(s.skin){amp.dataset.skin=s.skin;$('.amp-skin').forEach(x=>x.classList.toggle('active',x.dataset.skin===s.skin))}if(Array.isArray(s.eq))s.eq.forEach((v,i)=>{const el=$('.amp-eq')[i];if(!el)return;el.value=v;const out=document.querySelector('[data-eq-out="'+el.dataset.freq+'"]');if(out)out.textContent=(v>0?'+':'')+v});if(Number.isFinite(s.pre)){$('#ampPreamp').value=s.pre;setReadout('#ampPreampOut',(s.pre>0?'+':'')+s.pre+' dB')}if(Number.isFinite(s.vol)){$('#ampVolume').value=s.vol;setReadout('#ampVolumeOut',s.vol+'%')}if(Number.isFinite(s.bal)){$('#ampBalance').value=s.bal;setReadout('#ampBalanceOut',s.bal===0?'C':s.bal<0?'L '+Math.abs(s.bal):'R '+s.bal)}}catch(e){}};
$('.amp-skin').forEach(x=>x.addEventListener('click',saveAmpState));$('.amp-eq').forEach(x=>x.addEventListener('change',saveAmpState));['#ampPreamp','#ampVolume','#ampBalance'].forEach(sel=>$(sel).addEventListener('change',saveAmpState));$('.amp-preset').forEach(x=>x.addEventListener('click',()=>setTimeout(saveAmpState,0)));$('#ampEqFlat').addEventListener('click',()=>setTimeout(saveAmpState,0));

// Drag/drop behaves like a physical patch bay.
['dragenter','dragover'].forEach(ev=>amp.addEventListener(ev,e=>{e.preventDefault();amp.classList.add('amp-drop');status.textContent='DROP MEDIA // PATCH INPUT ARMED.'}));
['dragleave','drop'].forEach(ev=>amp.addEventListener(ev,e=>{e.preventDefault();amp.classList.remove('amp-drop')}));
amp.addEventListener('drop',e=>{if(e.dataTransfer?.files?.length)add(e.dataTransfer.files)});

restoreAmpState();draw();
})();
