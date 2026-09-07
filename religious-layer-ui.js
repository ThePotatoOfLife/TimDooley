const escReligious = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function mountReligiousLayerMap() {
  const page = document.querySelector('.belief-page');
  if (!page) return;
  try {
    const map = await fetch('data/religious-layer-map.json', {cache:'no-store'}).then(r => { if (!r.ok) throw new Error('layer map unavailable'); return r.json(); });
    const layers = map.layers || [];
    const section = document.createElement('section');
    section.className = 'religious-layer-map';
    section.innerHTML = `<div class="belief-research-summary"><strong>Religious knowledge graph</strong><span>${layers.length} registered backend layers · definitions → foundations → adjacent research → texts → evidence → cross-domain relationships</span></div><div class="belief-grid religious-layer-grid">${layers.map(layer => `<article class="mini"><span class="belief-type">${escReligious(layer.kind)}</span><h3>${escReligious(layer.id)}</h3><p>${escReligious(layer.purpose)}</p><small>${escReligious(layer.file)}</small></article>`).join('')}</div><p class="note">Layer map: ${escReligious(map.coupling_rules?.length || 0)} coupling rules. Backend records remain separate from blueprints and are joined through canonical IDs and relationships.</p>`;
    page.appendChild(section);
  } catch {
    // The main Ideas page remains usable if this optional visualization is unavailable.
  }
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mountReligiousLayerMap); else mountReligiousLayerMap();
