#!/usr/bin/env python3
"""Compile canonical science records into the public Science library and full documents."""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "knowledge" / "science"
OUT = ROOT / "_site" / "science"
PAPERS_DIR = OUT / "papers"
CATALOG_JSON = OUT / "catalog.json"
CATALOG_PAGE = OUT / "catalog" / "index.html"
SCIENCE_PAGE = OUT / "index.html"
MARKER = "<!-- SCIENCE_CATALOG_STATIC -->"
GITHUB_BLOB_BASE = "https://github.com/ThePotatoOfLife/TimDooley/blob/main/knowledge/science/"

TEXT_KEYS = ("abstract", "summary", "purpose", "importance", "core_thesis", "description", "scope")
PROVENANCE_KEYS = ("provenance_classes", "epistemic_classes", "source_class", "origin_class", "provenance", "provenance_rule")
EQUATION_KEYS = (
    "equation", "formula", "lagrangian", "differential", "curvature", "action",
    "operator", "formalism", "formal_core", "metric", "mapping", "coupling",
    "symmetry_breaking", "rg_", "field_equation", "dynamics", "hamiltonian",
    "transfer_function", "lie_bracket", "commutator", "continuity_equation",
)
FINDING_KEYS = ("conclusion", "finding", "result", "implication", "interpretation", "lesson", "takeaway", "strongest_result")
SCIENTIFIC_CONTENT_TOKENS = (
    "research_question", "model", "equation", "formula", "formal", "method", "finding",
    "result", "observable", "test", "falsification", "failure", "reference", "experiment",
    "mechanism", "dynamics", "derivation", "prediction", "field", "state_space", "hamiltonian",
    "lagrangian", "measurement", "benchmark", "parameter", "simulation", "calibration",
)
ADMIN_TOKENS = (
    "master-index", "source-ledger", "registry", "inventory", "router", "routing-index",
    "coverage-index", "integration-index", "completion-matrix", "theory-graph-index",
)
VALID_DOCUMENT_TYPES = (
    "Theory / Paper",
    "Research Programme",
    "Formal Note / Framework",
    "Scientific Audit",
    "Recovery / Archaeology",
    "Research Record",
)
FIELD_RULES = {
    "Physics": (
        "physics", "field theory", "lagrangian", "gauge", "higgs", "particle", "gravity",
        "relativity", "electromagnet", "boson", "fermion", "supergravity", "kaluza-klein",
        "black hole", "yang-mills", "standard model", "effective field theory", "eft",
    ),
    "Cosmology & Astronomy": (
        "cosmology", "astronomy", "astrophysics", "celestial", "galactic", "solar", "cmb",
        "dark sector", "dark matter", "dark energy", "orbit", "cosmic", "sirius", "regulus",
        "cosmological", "universe expansion", "sagittarius a",
    ),
    "Quantum Science": (
        "quantum", "entanglement", "decoherence", "hilbert", "density operator", "density matrix",
        "qft", "bell", "many-worlds", "wavefunction", "schrodinger", "path integral",
    ),
    "Neuroscience": (
        "neuroscience", "neural", "neuron", "brain", "microtubule", "tubulin", "consciousness",
        "synaptic", "axon", "dendrite", "thalam", "pineal", "cerebrospinal", "csf",
    ),
    "Biology": (
        "biology", "biological", "biophysical", "cellular", "cytoskeleton", "microtubule", "tubulin",
        "organism", "molecular biology", "biochemistry", "plant", "botany", "fermentation",
    ),
    "Chemistry": (
        "chemistry", "chemical", "molecular chemistry", "reaction chemistry", "fermentation",
        "distillation", "electrochem", "redox", "metabol", "biochemical transformation",
    ),
    "Psychology": (
        "psychology", "psychological", "cognition", "cognitive", "behavioral", "behavioural",
        "attention dynamics", "perception", "psychophysics",
    ),
    "Information Science": (
        "information theory", "mutual information", "entropy", "information geometry", "channel",
        "signal", "observer model", "compression", "identifiability", "data-processing", "spudlight",
    ),
    "Mathematics & Formal Systems": (
        "mathematical", "mathematics", "geometry", "topology", "dynamical systems", "lie bracket",
        "commutator", "group theory", "differential geometry", "logarithmic spiral", "formal system",
        "state space", "spectral dimension", "poincare", "holonomy", "topological",
    ),
}
MATH_HINT = re.compile(r"(=|→|↔|∂|∇|Σ|∫|√|ℒ|□|μ|ν|θ|φ|ψ|α|β|γ|lambda|alpha|beta|gamma|SU\(|SO\(|Spin\(|U\(1\)|d[A-Za-z_].*/d)")
URL_RE = re.compile(r"^https?://", re.I)


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def slugify(value: str) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "science-record"


def source_slug(relative_file: str) -> str:
    return slugify(Path(relative_file).with_suffix("").as_posix().replace("/", "-"))


def humanize_key(key: str) -> str:
    text = str(key).replace("_", " ").replace("-", " ").strip()
    replacements = {
        "upt": "UPT", "qft": "QFT", "sm": "SM", "eft": "EFT", "cmb": "CMB",
        "csf": "CSF", "rg": "RG", "g2": "G2", "u1": "U(1)", "11d": "11D",
    }
    words = []
    for word in text.split():
        low = word.lower()
        words.append(replacements.get(low, word if any(ch.isupper() for ch in word) else word.capitalize()))
    return " ".join(words)


def first_text(data: dict) -> str:
    for key in TEXT_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return " ".join(value.split())
    return ""


def flatten_strings(value, limit=40):
    out: list[str] = []
    if isinstance(value, str):
        if value.strip():
            out.append(" ".join(value.split()))
    elif isinstance(value, (list, tuple)):
        for item in value:
            if len(out) >= limit:
                break
            out.extend(flatten_strings(item, limit - len(out)))
    elif isinstance(value, dict):
        for item in value.values():
            if len(out) >= limit:
                break
            out.extend(flatten_strings(item, limit - len(out)))
    return out[:limit]


def flatten_keys(value) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key).lower())
            keys.update(flatten_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(flatten_keys(child))
    return keys


def get_provenance(data: dict) -> list[str]:
    values: list[str] = []
    for key in PROVENANCE_KEYS:
        if key in data:
            values.extend(flatten_strings(data[key], 16))
    return list(dict.fromkeys(values))[:16]


def walk_candidates(obj, equations=None, findings=None):
    equations = equations if equations is not None else []
    findings = findings if findings is not None else []
    if isinstance(obj, dict):
        for key, value in obj.items():
            low = str(key).lower()
            if any(token in low for token in EQUATION_KEYS):
                for text in flatten_strings(value, 36):
                    if MATH_HINT.search(text) and text not in equations:
                        equations.append(text)
            if any(token in low for token in FINDING_KEYS):
                for text in flatten_strings(value, 24):
                    if len(text) >= 18 and text not in findings:
                        findings.append(text)
            walk_candidates(value, equations, findings)
    elif isinstance(obj, list):
        for value in obj:
            walk_candidates(value, equations, findings)
    return equations[:48], findings[:32]


def classification_text(path: Path, data: dict) -> str:
    parts = [path.as_posix()]
    for key in (
        "title", "status", "abstract", "summary", "purpose", "importance", "scope",
        "research_question", "maturity", "kind", "domain", "discipline",
    ):
        value = data.get(key)
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, (list, dict)):
            parts.extend(flatten_strings(value, 24))
    for key in ("topics", "concepts", "keywords", "named_frameworks", "motifs", "domains", "fields"):
        if key in data:
            parts.extend(flatten_strings(data[key], 40))
    return " ".join(parts).lower()


def classify_fields(path: Path, data: dict) -> list[str]:
    """Assign broad multi-valued science fields using explicit auditable token rules."""
    text = classification_text(path, data)
    fields = [label for label, tokens in FIELD_RULES.items() if any(token in text for token in tokens)]
    return fields or ["Cross-disciplinary"]


def classify_document_type(path: Path, data: dict) -> str:
    """Classify what kind of document a reader is opening, independently of discipline."""
    explicit = data.get("document_type")
    if isinstance(explicit, str) and explicit in VALID_DOCUMENT_TYPES:
        return explicit

    title = str(data.get("title") or data.get("name") or data.get("id") or path.stem)
    status = str(data.get("status") or "")
    purpose = str(data.get("purpose") or "")
    maturity = str(data.get("maturity") or "")
    text = " ".join((title, status, purpose, maturity, path.stem)).lower()

    if "audit" in text:
        return "Scientific Audit"
    if "programme" in text or "program" in text:
        return "Research Programme"
    if any(token in text for token in ("formal framework", "formalism", "toy model", "formulation upgrade", "mathematical contribution", "framework")):
        return "Formal Note / Framework"
    if "theory" in title.lower() and not any(token in title.lower() for token in ("index", "graph", "matrix")):
        return "Theory / Paper"
    if any(token in text for token in ("recovery", "archaeology", "recovered")):
        return "Recovery / Archaeology"
    if any(token in text for token in ("candidate model", "model family", "physical proposal", "theory")):
        return "Theory / Paper"
    return "Research Record"


def scientific_content_groups(data: dict) -> set[str]:
    keys = flatten_keys(data)
    groups: set[str] = set()
    for token in SCIENTIFIC_CONTENT_TOKENS:
        if any(token in key for key in keys):
            groups.add(token)
    return groups


def qualifies_for_library(path: Path, data: dict, record: dict) -> bool:
    """Keep substantial reader-facing science while excluding pure routing/inventory records."""
    if not isinstance(data, dict) or not data:
        return False
    abstract = str(data.get("abstract") or "").strip()
    summary = record.get("abstract", "").strip()
    groups = scientific_content_groups(data)
    administrative = any(token in path.stem.lower() for token in ADMIN_TOKENS)
    title_status = f"{data.get('title','')} {data.get('status','')}".lower()
    administrative = administrative or any(token.replace("-", " ") in title_status for token in ADMIN_TOKENS)

    if administrative:
        return len(abstract) >= 120 and len(groups) >= 3
    if len(abstract) >= 80 and len(groups) >= 1:
        return True
    if len(summary) >= 80 and len(groups) >= 2:
        return True
    if len(summary) >= 40 and len(groups) >= 3:
        return True
    return False


def extract_keywords(data: dict) -> list[str]:
    values: list[str] = []
    for key in ("topics", "concepts", "keywords", "motifs", "named_frameworks", "connections"):
        if key in data:
            values.extend(flatten_strings(data[key], 32))
    clean: list[str] = []
    for value in values:
        text = " ".join(str(value).split())
        if 1 < len(text) <= 90 and text not in clean:
            clean.append(text)
        if len(clean) >= 24:
            break
    return clean


def record_from(path: Path) -> tuple[dict, dict]:
    relative_file = path.relative_to(SRC).as_posix()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        record = {
            "file": relative_file,
            "slug": source_slug(relative_file),
            "id": path.stem,
            "title": path.stem.replace("-", " ").title(),
            "status": "parse error",
            "maturity": "",
            "abstract": f"Could not parse record: {exc}",
            "provenance": [],
            "equations": [],
            "findings": [],
            "keywords": [],
            "fields": ["Cross-disciplinary"],
            "document_type": "Research Record",
            "updated": "",
            "qualifies": False,
        }
        return record, {}

    equations, findings = walk_candidates(data)
    title = data.get("title") or data.get("name") or data.get("id") or path.stem
    record = {
        "file": relative_file,
        "slug": source_slug(relative_file),
        "id": data.get("id") or path.stem,
        "title": str(title),
        "updated": data.get("updated") or data.get("date") or data.get("first_known_date") or "",
        "status": data.get("status") or "",
        "maturity": data.get("maturity") or "",
        "abstract": first_text(data) or f"Canonical science record for {title}.",
        "provenance": get_provenance(data),
        "equations": equations,
        "findings": findings,
        "keywords": extract_keywords(data),
        "fields": classify_fields(path, data),
        "document_type": classify_document_type(path, data),
    }
    record["qualifies"] = qualifies_for_library(path, data, record)
    return record, data


def is_equation_key(key: str) -> bool:
    low = str(key).lower()
    return any(token in low for token in EQUATION_KEYS)


def render_scalar(value, key: str = "") -> str:
    if isinstance(value, bool):
        return f"<p>{'Yes' if value else 'No'}</p>"
    if isinstance(value, (int, float)):
        return f"<p>{esc(value)}</p>"
    text = str(value or "").strip()
    if not text:
        return ""
    if URL_RE.match(text):
        return f'<p><a href="{esc(text)}" rel="noopener">{esc(text)}</a></p>'
    if is_equation_key(key) and MATH_HINT.search(text):
        return f'<pre class="paper-equation"><code>{esc(text)}</code></pre>'
    return f"<p>{esc(text)}</p>"


def render_value(value, depth: int = 0, key: str = "") -> str:
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return render_scalar(value, key)
    if isinstance(value, list):
        if all(isinstance(item, (str, int, float, bool)) for item in value):
            if is_equation_key(key):
                items = "".join(f'<pre class="paper-equation"><code>{esc(item)}</code></pre>' for item in value if str(item).strip())
                return items
            return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in value) + "</ul>"
        rendered = []
        for index, item in enumerate(value, 1):
            if isinstance(item, dict):
                label = item.get("title") or item.get("name") or item.get("id") or item.get("topic") or f"Item {index}"
                rendered.append(
                    '<article class="paper-item">'
                    f'<h{min(4 + depth, 6)}>{esc(label)}</h{min(4 + depth, 6)}>'
                    f'{render_mapping(item, depth + 1, skip_keys=("title", "name", "id", "topic"))}'
                    '</article>'
                )
            else:
                rendered.append(render_value(item, depth + 1, key))
        return "".join(rendered)
    if isinstance(value, dict):
        scalar_only = len(value) <= 14 and all(isinstance(item, (str, int, float, bool)) or item is None for item in value.values())
        if scalar_only and not any(is_equation_key(k) for k in value):
            rows = []
            for child_key, child in value.items():
                if child is None or child == "":
                    continue
                child_text = str(child)
                if URL_RE.match(child_text):
                    rendered = f'<a href="{esc(child_text)}" rel="noopener">{esc(child_text)}</a>'
                else:
                    rendered = esc(child)
                rows.append(f"<dt>{esc(humanize_key(child_key))}</dt><dd>{rendered}</dd>")
            return '<dl class="paper-defs">' + "".join(rows) + "</dl>"
        return render_mapping(value, depth + 1)
    return f"<p>{esc(value)}</p>"


def render_mapping(data: dict, depth: int = 0, skip_keys: tuple[str, ...] = ()) -> str:
    parts: list[str] = []
    for key, value in data.items():
        if key in skip_keys or value is None or value == "" or value == [] or value == {}:
            continue
        level = min(3 + depth, 6)
        parts.append(
            f'<section class="paper-block paper-depth-{min(depth, 3)}">'
            f'<h{level}>{esc(humanize_key(key))}</h{level}>'
            f'{render_value(value, depth, key)}'
            '</section>'
        )
    return "".join(parts)


PREFERRED_SECTION_KEYS = (
    "research_question", "purpose", "importance", "scope", "background", "core_thesis",
    "state_space_and_fields", "model", "model_family", "formal_model", "formalism", "formal_core",
    "recovered_master_lagrangian", "equation_context", "equations", "term_map", "mechanism",
    "methods", "method", "derivation", "derivations", "findings", "results", "strongest_result",
    "observable_program", "observables", "experimental_ladder", "testing_program", "advancement_gates",
    "falsification_and_failure_conditions", "failure_conditions", "hard_boundaries", "limitations",
    "boundaries", "unresolved_primary_questions", "new_research_questions", "completion_path", "next_steps",
    "lineage", "connections", "external_references", "sources", "sources_checked",
)
PAPER_METADATA_KEYS = {
    "id", "title", "name", "version", "updated", "date", "first_known_date", "status", "maturity",
    "abstract", "document_type",
}


def render_semantic_sections(data: dict) -> str:
    rendered: list[str] = []
    used: set[str] = set(PAPER_METADATA_KEYS)
    for key in PREFERRED_SECTION_KEYS:
        if key in data and key not in used:
            value = data[key]
            if value not in (None, "", [], {}):
                rendered.append(
                    f'<section class="paper-section"><h2>{esc(humanize_key(key))}</h2>{render_value(value, 0, key)}</section>'
                )
            used.add(key)
    for key, value in data.items():
        if key in used or value in (None, "", [], {}):
            continue
        rendered.append(
            f'<section class="paper-section"><h2>{esc(humanize_key(key))}</h2>{render_value(value, 0, key)}</section>'
        )
        used.add(key)
    return "".join(rendered)


def render_paper_page(record: dict, data: dict) -> str:
    relative_file = record["file"]
    source_href = "../../../knowledge/science/" + relative_file
    github_href = GITHUB_BLOB_BASE + quote(relative_file, safe="/-_.")
    canonical = f"https://thepotatooflife.github.io/TimDooley/science/papers/{record['slug']}/"
    fields = "".join(f'<span class="paper-chip">{esc(field)}</span>' for field in record["fields"])
    status_bits = [record["document_type"], record.get("updated") or "undated"]
    if record.get("maturity"):
        status_bits.append(str(record["maturity"]))
    meta = " · ".join(str(bit) for bit in status_bits if bit)
    status = str(record.get("status") or "").strip()
    status_html = f'<p class="paper-status"><strong>Status:</strong> {esc(status)}</p>' if status else ""
    body = render_semantic_sections(data)
    source_path = "knowledge/science/" + relative_file
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(record['title'])} — Science — Tim Dooley</title>
<meta name="description" content="{esc(record['abstract'][:300])}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<link rel="canonical" href="{esc(canonical)}">
<link rel="stylesheet" href="../../science-paper.css?v=20260911a">
</head>
<body><main class="paper-page">
<nav class="paper-nav"><a href="../../">← Science</a><a href="../../../">Home</a></nav>
<header class="paper-header">
<p class="paper-kicker">{esc(meta)}</p>
<h1>{esc(record['title'])}</h1>
<div class="paper-chips">{fields}</div>
<h2 class="paper-abstract-label">Abstract</h2>
<p class="paper-abstract">{esc(record['abstract'])}</p>
{status_html}
</header>
<article class="paper-content">{body}</article>
<footer class="paper-source">
<h2>Source & provenance</h2>
<p>This readable document is generated from the canonical structured record. Formatting does not change the scientific status recorded above.</p>
<div class="paper-source-actions">
<a class="source-action" href="{esc(source_href)}" download>Download source JSON</a>
<a class="source-action" href="{esc(github_href)}" rel="noopener">View source on GitHub</a>
</div>
<p class="paper-source-path"><code>{esc(source_path)}</code></p>
</footer>
</main></body></html>'''


def short_status(value: str, limit: int = 150) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def render_library_rows(records: list[dict]) -> str:
    rows: list[str] = []
    for record in records:
        fields = "|".join(record["fields"])
        field_label = " · ".join(record["fields"])
        status = short_status(record.get("maturity") or record.get("status") or "")
        equation = record["equations"][0] if record.get("equations") else ""
        equation_html = f'<code class="science-equation-preview">{esc(equation)}</code>' if equation else ""
        tags = record.get("keywords", [])[:4]
        tags_html = ""
        if tags:
            tags_html = '<div class="science-record-tags">' + "".join(f"<span>{esc(tag)}</span>" for tag in tags) + "</div>"
        read_label = "Read full paper →" if record["document_type"] == "Theory / Paper" else "Read full document →"
        source_href = "../knowledge/science/" + record["file"]
        search_blob = " ".join([
            record["title"], record["abstract"], record.get("status", ""), record.get("maturity", ""),
            record["document_type"], *record["fields"], *record.get("equations", [])[:6], *record.get("keywords", []),
        ]).lower()
        rows.append(f'''<article class="science-record" data-fields="{esc(fields)}" data-type="{esc(record['document_type'])}" data-search="{esc(search_blob)}">
  <div class="science-record-meta">
    <span class="science-record-kind">{esc(record['document_type'])}</span>
    <span class="science-record-fields">{esc(field_label)}</span>
    {f'<span class="science-record-status">{esc(status)}</span>' if status else ''}
  </div>
  <div class="science-record-body">
    <h2>{esc(record['title'])}</h2>
    <p class="science-abstract">{esc(record['abstract'])}</p>
    {equation_html}
    {tags_html}
  </div>
  <div class="science-record-actions">
    <a class="science-read" href="./papers/{esc(record['slug'])}/">{esc(read_label)}</a>
    <a class="science-source" href="{esc(source_href)}" download>Download source JSON</a>
  </div>
</article>''')
    return "\n".join(rows)


def render_catalog_redirect() -> str:
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,follow"><link rel="canonical" href="https://thepotatooflife.github.io/TimDooley/science/"><meta http-equiv="refresh" content="0; url=../"><title>Science library</title></head><body><p>The complete Science library is at <a href="../">Science</a>.</p><script>location.replace('../');</script></body></html>'''


def patch_science_page(rows: str) -> None:
    if not SCIENCE_PAGE.exists():
        raise SystemExit("_site/science/index.html missing")
    text = SCIENCE_PAGE.read_text(encoding="utf-8")
    if text.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one {MARKER} in science/index.html")
    SCIENCE_PAGE.write_text(text.replace(MARKER, rows, 1), encoding="utf-8")


def patch_legacy_readers() -> None:
    replacements = {
        OUT / "research-map" / "index.html": [
            ("the exact Spiral formula remains unrecovered.", "the exact Spiral formula is now recovered: r=a exp(bθ), with b=ln(φ)/(π/2)≈0.30635; a quarter-turn scales radius by φ."),
            ("<li>Exact April 21, 2025 Spiral Equation.</li>", "<li>Earliest primary variable meanings for a, r and θ in the recovered April 21, 2025 Spiral Equation.</li>"),
        ],
        OUT / "axis-11d-sun-spiral" / "index.html": [
            ("This is a genuine Sun + rotation + outward-flow + Spiral system. It is an external physics neighbor, not the missing April 2025 Spiral Equation.", "This is a genuine Sun + rotation + outward-flow + Spiral system. It is an external physics neighbor to the recovered April 2025 Potato Axis logarithmic spiral, not the same physical model."),
            ("<li>Exact April 21, 2025 Spiral Equation.</li>", "<li>Earliest primary variable meanings for a, r and θ in the recovered April 21, 2025 Spiral Equation.</li>"),
        ],
    }
    for path, pairs in replacements.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in pairs:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")


def public_record(record: dict) -> dict:
    return {
        "file": record["file"],
        "slug": record["slug"],
        "id": record["id"],
        "title": record["title"],
        "updated": record["updated"],
        "status": record["status"],
        "maturity": record["maturity"],
        "abstract": record["abstract"],
        "fields": record["fields"],
        "document_type": record["document_type"],
        "equation_preview": record["equations"][0] if record["equations"] else "",
        "keywords": record["keywords"],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    loaded = [record_from(path) for path in sorted(SRC.rglob("*.json"))]
    records = [record for record, _ in loaded]
    papers_with_data = [(record, data) for record, data in loaded if record.get("qualifies")]
    papers_with_data.sort(key=lambda item: item[0]["title"].casefold())
    papers = [record for record, _ in papers_with_data]

    for record, data in papers_with_data:
        target = PAPERS_DIR / record["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_paper_page(record, data), encoding="utf-8")

    fields = sorted({field for record in papers for field in record["fields"]})
    types = sorted({record["document_type"] for record in papers})
    field_counts = Counter(field for record in papers for field in record["fields"])
    type_counts = Counter(record["document_type"] for record in papers)
    payload = {
        "generated": date.today().isoformat(),
        "source_directory": "knowledge/science/",
        "record_count": len(records),
        "qualifying_count": len(papers),
        "fields": fields,
        "field_counts": dict(sorted(field_counts.items())),
        "document_types": types,
        "document_type_counts": dict(sorted(type_counts.items())),
        "papers": [public_record(record) for record in papers],
    }
    CATALOG_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    patch_science_page(render_library_rows(papers))
    CATALOG_PAGE.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PAGE.write_text(render_catalog_redirect(), encoding="utf-8")
    patch_legacy_readers()

    print(
        f"Built Science library: {len(records)} source records discovered; "
        f"{len(papers)} readable documents; {len(fields)} fields; {len(types)} document types."
    )


if __name__ == "__main__":
    main()
