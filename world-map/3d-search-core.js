export function normalizeSearchText(value) {
  return String(value ?? '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

function countryNameMap(countries = []) {
  const map = new Map();
  for (const country of countries) {
    const code = String(country?.iso3 || country?.cca3 || country?.code || '').toUpperCase();
    const name = String(country?.name?.common || country?.name || country?.official_name || code || '').trim();
    if (code) map.set(code, name || code);
  }
  return map;
}

function cleanAliases(values = []) {
  const seen = new Set();
  return values.flatMap(value => Array.isArray(value) ? value : [value])
    .map(value => String(value ?? '').trim())
    .filter(Boolean)
    .filter(value => {
      const key = normalizeSearchText(value);
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

export function subdivisionSearchRows(index = {}) {
  const rows = [];
  for (const [parentIso3, descriptor] of Object.entries(index?.partitions || {})) {
    const parentName = String(descriptor?.parent_name || descriptor?.country_name || '').trim();
    for (const item of descriptor?.search_records || []) {
      const id = String(item?.id || '').trim();
      const name = String(item?.name || '').trim();
      if (!id || !name) continue;
      rows.push({
        ...item,
        id,
        name,
        parent_iso3:String(item?.parent_iso3 || parentIso3).toUpperCase(),
        parent_name:item?.parent_name || parentName || undefined,
      });
    }
  }
  return rows;
}

export function buildSearchRecords({countries = [], subdivisions = [], places = []} = {}) {
  const countryNames = countryNameMap(countries);
  const records = [];

  for (const country of countries) {
    const code = String(country?.iso3 || country?.cca3 || country?.code || '').toUpperCase();
    const name = String(country?.name?.common || country?.name || country?.official_name || code || '').trim();
    if (!code || !name) continue;
    const aliases = cleanAliases([country?.name?.official, country?.official_name, country?.iso2, country?.cca2, country?.aliases]);
    records.push({id:code,type:'country',name,parent:'',code,aliases,display:`${name} · Country`,payload:country});
  }

  for (const subdivision of subdivisions) {
    const id = String(subdivision?.id || '').trim();
    const name = String(subdivision?.name || '').trim();
    if (!id || !name) continue;
    const code = String(subdivision?.code || subdivision?.postal_code || '').trim();
    const parentCode = String(subdivision?.parent_iso3 || subdivision?.parent || '').toUpperCase();
    const parent = subdivision?.parent_name || countryNames.get(parentCode) || subdivision?.country || subdivision?.parent || '';
    const typeLabel = String(subdivision?.subdivision_type || 'Subdivision').replace(/\b\w/g, c => c.toUpperCase());
    records.push({id,type:'subdivision',name,parent:String(parent || ''),code,aliases:cleanAliases([code, subdivision?.aliases]),display:`${name} · ${typeLabel}${parent ? ` · ${parent}` : ''}`,payload:subdivision});
  }

  for (const place of places) {
    const id = String(place?.id || '').trim();
    const name = String(place?.name || '').trim();
    if (!id || !name) continue;
    const iso3 = String(place?.iso3 || '').toUpperCase();
    const country = place?.country || countryNames.get(iso3) || iso3;
    const admin = place?.admin_region || place?.subdivision_name || '';
    const parent = [admin, country].filter(Boolean).join(' · ');
    records.push({id,type:'city',name,parent,code:'',aliases:cleanAliases(place?.aliases || []),display:`${name} · City${admin ? ` · ${admin}` : ''}${country ? ` · ${country}` : ''}`,payload:place});
  }

  return records;
}

function scoreRecord(record, query) {
  const q = normalizeSearchText(query);
  if (!q) return null;
  const fields = [record.id, record.code, record.name, ...(record.aliases || []), record.parent, record.display].map(normalizeSearchText).filter(Boolean);
  let best = Infinity;
  fields.forEach((field, index) => {
    if (field === q) best = Math.min(best, index <= 3 ? index : 4);
    else if (field.startsWith(q)) best = Math.min(best, 10 + index);
    else if (field.includes(q)) best = Math.min(best, 20 + index);
  });
  return Number.isFinite(best) ? best : null;
}

const TYPE_ORDER = {country:0, subdivision:1, city:2};

export function rankSearchRecords(records, query, limit = 12) {
  const ranked = [];
  for (const record of records || []) {
    const score = scoreRecord(record, query);
    if (score == null) continue;
    ranked.push({record, score});
  }
  ranked.sort((a, b) => a.score - b.score || (TYPE_ORDER[a.record.type] ?? 9) - (TYPE_ORDER[b.record.type] ?? 9) || a.record.display.localeCompare(b.record.display));
  return ranked.slice(0, Math.max(0, Number(limit) || 0)).map(item => item.record);
}
