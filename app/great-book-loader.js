(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.PotatoGreatBookLoader=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';

  function abortError(){
    const error=new Error('aborted');
    error.name='AbortError';
    return error;
  }

  function createChapterLoader(options={}){
    const fetchImpl=options.fetchImpl||((...args)=>fetch(...args));
    const sanitizePath=typeof options.sanitizePath==='function'?options.sanitizePath:value=>String(value||'');
    const onError=typeof options.onError==='function'?options.onError:()=>{};
    const inFlight=new Map();
    const fetchInFlight=new Map();
    const markupCache=new Map();

    async function prefetchPath(path,loadOptions={}){
      if(!path)return '';
      if(markupCache.has(path))return markupCache.get(path);
      if(loadOptions.signal?.aborted)throw abortError();
      if(fetchInFlight.has(path))return fetchInFlight.get(path);
      const task=(async()=>{
        const response=await fetchImpl(path,{signal:loadOptions.signal});
        if(!response?.ok)throw new Error(`${path} ${response?.status??'failed'}`);
        const markup=await response.text();
        if(loadOptions.signal?.aborted)throw abortError();
        markupCache.set(path,markup);
        return markup;
      })().finally(()=>fetchInFlight.delete(path));
      fetchInFlight.set(path,task);
      return task;
    }

    async function prefetchSlot(slot,loadOptions={}){
      if(!slot)return null;
      const path=sanitizePath(slot.dataset?.path);
      await prefetchPath(path,loadOptions);
      return slot;
    }

    async function loadSlot(slot,loadOptions={}){
      if(!slot)return null;
      if(slot.dataset?.loaded==='true')return slot;
      if(loadOptions.signal?.aborted)throw abortError();
      const key=slot.id||sanitizePath(slot.dataset?.path);
      if(inFlight.has(key))return inFlight.get(key);

      if(slot.dataset)slot.dataset.loaded='loading';
      const path=sanitizePath(slot.dataset?.path);
      const task=(async()=>{
        try{
          const markup=await prefetchPath(path,loadOptions);
          if(loadOptions.signal?.aborted)throw abortError();
          slot.innerHTML=markup;
          if(slot.dataset)slot.dataset.loaded='true';
          return slot;
        }catch(error){
          if(error?.name==='AbortError'){
            if(slot.dataset)slot.dataset.loaded='false';
            throw error;
          }
          if(slot.dataset)slot.dataset.loaded='error';
          onError(slot,error);
          throw error;
        }finally{
          inFlight.delete(key);
        }
      })();
      inFlight.set(key,task);
      return task;
    }

    async function loadSlots(slots,loadOptions={}){
      const queue=Array.from(slots||[]);
      const concurrency=Math.max(1,Math.min(queue.length||1,Number(loadOptions.concurrency)||4));
      const loaded=[];
      const failed=[];
      let cursor=0;

      async function worker(){
        while(cursor<queue.length){
          if(loadOptions.signal?.aborted)throw abortError();
          const index=cursor++;
          const slot=queue[index];
          try{
            const result=await loadSlot(slot,loadOptions);
            if(result)loaded.push(result);
          }catch(error){
            if(error?.name==='AbortError')throw error;
            failed.push({slot,error});
          }
        }
      }

      await Promise.all(Array.from({length:concurrency},()=>worker()));
      return {loaded,failed};
    }

    return {loadSlot,loadSlots,prefetchSlot};
  }

  return {createChapterLoader};
});
