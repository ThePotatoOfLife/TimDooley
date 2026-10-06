// Optional sourced ADM1 statistics join. Geometry provenance remains owned by subdivision partitions.
const ROOT='../data/world-subdivisions/statistics/';
const INDEX_URL=ROOT+'index.json';
let indexPromise=null;
const datasets=new Map();

function clone(value){ return value == null ? value : structuredClone(value); }
function index(){
  if(!indexPromise) indexPromise=fetch(INDEX_URL,{cache:'force-cache'})
    .then(r=>{ if(!r.ok) throw new Error(`Subdivision statistics index unavailable (${r.status})`); return r.json(); });
  return indexPromise;
}
async function datasetFor(partition){
  const code=String(partition||'').toUpperCase();
  if(datasets.has(code)) return datasets.get(code);
  const idx=await index();
  const desc=idx?.datasets?.[code];
  if(!desc?.path){ datasets.set(code,null); return null; }
  const response=await fetch(ROOT+desc.path,{cache:'force-cache'});
  if(!response.ok) throw new Error(`Subdivision statistics ${code} unavailable (${response.status})`);
  const payload=await response.json();
  const byId=new Map((payload?.records||[]).map(row=>[String(row?.subdivision_id||''),row]).filter(([id])=>id));
  const state={descriptor:desc,payload,byId};
  datasets.set(code,state);
  return state;
}
function metricProvenance(metric,row,descriptor){
  const value=row?.[metric];
  if(value == null) return null;
  const meta=row?.[`${metric}_meta`] || row?.metadata || {};
  return {
    value:Number(value),
    period:meta.period || descriptor?.period || null,
    unit:meta.unit || (metric==='population'?'persons':metric==='area_km2'?'km²':null),
    source:meta.source || descriptor?.source || null,
    source_ref:meta.source_ref || descriptor?.source_ref || null,
    status:meta.status || descriptor?.status || 'sourced',
  };
}
function enrichFeature(feature,row,descriptor){
  if(!feature || !row) return feature;
  const out=clone(feature);
  const p=out.properties ||= {};
  const provenance={...(p.statistics_provenance||{})};
  const population=metricProvenance('population',row,descriptor);
  if(population && Number.isFinite(population.value) && population.value>0){
    p.population={value:population.value,period:population.period,unit:'persons',source:population.source,source_ref:population.source_ref};
    p.population_status='sourced';
    provenance.population=population;
  }
  const area=metricProvenance('area_km2',row,descriptor);
  const hasSourcedArea=Number.isFinite(Number(p.area_km2)) && Boolean(p.area_definition || p.area_source || p.statistics_provenance?.area_km2);
  if(area && Number.isFinite(area.value) && area.value>0 && !hasSourcedArea){
    p.area_km2=area.value;
    p.area_definition='sourced ADM1 statistics enrichment; not calculated from display geometry';
    p.area_source=area.source;
    p.area_source_ref=area.source_ref;
    provenance.area_km2=area;
  }
  const density=metricProvenance('density_per_km2',row,descriptor);
  if(density && Number.isFinite(density.value) && density.value>=0) provenance.density_per_km2=density;
  if(Object.keys(provenance).length) p.statistics_provenance=provenance;
  return out;
}
async function enrichCollection(partition,collection){
  const state=await datasetFor(partition);
  if(!state || !Array.isArray(collection?.features)) return collection;
  return {
    ...collection,
    features:collection.features.map(feature=>{
      const id=String(feature?.properties?.id || feature?.id || '');
      return enrichFeature(feature,state.byId.get(id),state.descriptor);
    })
  };
}
function status(){ return {loaded:[...datasets.entries()].filter(([,v])=>v).map(([k])=>k),known:[...datasets.keys()]}; }
window.__potatoAtlasSubdivisionStatistics=Object.freeze({enrichCollection,status,datasetFor});
window.dispatchEvent?.(new CustomEvent('potato-atlas-subdivision-statistics-ready'));
export { enrichCollection };
