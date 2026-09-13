#!/usr/bin/env python3
"""Convert heterogeneous canonical owners into human reader blocks.

Adapters never own facts. They select and label content already present in the
canonical owner so page composition stays stable without forcing every domain
into one JSON schema.
"""
from __future__ import annotations
from typing import Any


def block(block_id:str,title:str,text:str,*,meta:dict[str,Any]|None=None)->dict[str,Any]:
    return {"id":block_id,"title":title,"text":text.strip(),"meta":meta or {}}


def standard_sections(owner:dict[str,Any])->list[dict[str,Any]]:
    sections=owner.get("sections")
    if not isinstance(sections,dict):return []
    out=[]
    for key,value in sections.items():
        if not isinstance(value,dict):continue
        text=value.get("text")
        if not isinstance(text,str) or not text.strip():continue
        out.append(block(str(key),str(key).replace("_"," ").replace("-"," ").title(),text,meta={"epistemic_class":value.get("epistemic_class",[]),"source_ids":value.get("source_ids",[])}))
    return out


def potato_biology(owner:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    rule=owner.get("epistemic_rule")
    if isinstance(rule,str) and rule.strip():out.append(block("epistemic-rule","Biology before metaphor",rule))
    for index,row in enumerate(owner.get("core_biology",[]) if isinstance(owner.get("core_biology"),list) else []):
        if not isinstance(row,dict):continue
        topic=str(row.get("topic") or f"Biology {index+1}")
        fact=str(row.get("fact") or "").strip()
        deduction=str(row.get("timic_deduction") or row.get("project_upgrade") or row.get("systems_deduction") or "").strip()
        parts=[]
        if fact:parts.append(fact)
        if deduction:parts.append("Project relation: "+deduction)
        if parts:out.append(block(f"biology-{index+1}",topic.title(),"\n\n".join(parts)))
    return out


def body_systems(owner:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    rule=owner.get("reader_rule")
    if isinstance(rule,str) and rule.strip():out.append(block("reader-rule","How to read this body map",rule))
    for index,row in enumerate(owner.get("systems",[]) if isinstance(owner.get("systems"),list) else []):
        if not isinstance(row,dict):continue
        title=str(row.get("id") or f"Body system {index+1}").replace("-"," ").title()
        parts=[]
        if row.get("biology"):parts.append("Biology: "+str(row["biology"]))
        if row.get("project"):parts.append("Project mapping: "+str(row["project"]))
        if row.get("boundary"):parts.append("Boundary: "+str(row["boundary"]))
        if parts:out.append(block(f"body-{index+1}",title,"\n\n".join(parts)))
    return out


def vertical_geometry(owner:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    rule=owner.get("epistemic_rule")
    if isinstance(rule,str) and rule.strip():out.append(block("epistemic-rule","Geometry and interpretation",rule))
    geometry=owner.get("canonical_vertical_compass_construction")
    if isinstance(geometry,dict):
        preferred=("orientation","radius","upper_circle_center","lower_circle_center","center_distance","circle_intersections","relational_midpoint","plane","axis","critical_geometric_revelation")
        lines=[f"{key.replace('_',' ').title()}: {geometry[key]}" for key in preferred if key in geometry]
        if lines:out.append(block("canonical-geometry","Canonical vertical geometry","\n".join(lines)))
    points=owner.get("five_primary_vertical_points")
    if isinstance(points,dict):
        lines=[]
        for name,row in points.items():
            if isinstance(row,dict):lines.append(f"{name}: {row.get('coordinate','')} — {row.get('project_role','')}")
        if lines:out.append(block("primary-points","Five primary vertical points","\n".join(lines)))
    return out


def vesica_geometry(owner:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    rule=owner.get("epistemic_rule")
    if isinstance(rule,str) and rule.strip():out.append(block("epistemic-rule","Mathematics and symbolic overlay",rule))
    geometry=owner.get("vertical_vesica")
    if isinstance(geometry,dict):
        preferred=("radius","upper_circle","lower_circle","father_center","son_center","center_distance","lateral_intersections","relational_midpoint","plane","axis","full_lens_area")
        lines=[f"{key.replace('_',' ').title()}: {geometry[key]}" for key in preferred if key in geometry]
        if lines:out.append(block("vertical-vesica","Exact vertical Vesica","\n".join(lines)))
    relations=owner.get("critical_exact_relations")
    if isinstance(relations,list) and relations:
        out.append(block("critical-relations","Critical exact relations","\n".join(f"• {item}" for item in relations if isinstance(item,str))))
    taxonomy=owner.get("center_taxonomy")
    if isinstance(taxonomy,dict):
        lines=[f"{key.replace('_',' ').title()}: {value}" for key,value in taxonomy.items()]
        if lines:out.append(block("center-taxonomy","Center taxonomy","\n".join(lines)))
    return out


def adapt(owner:dict[str,Any],node_id:str)->list[dict[str,Any]]:
    standard=standard_sections(owner)
    if standard:return standard
    if node_id=="potato-biology-ecology-development-canon":return potato_biology(owner)
    if node_id=="body-system-master-atlas":return body_systems(owner)
    if node_id=="vertical-potato-mountain-plane-atlas":return vertical_geometry(owner)
    if node_id=="geometry-vesica-pisces-mandorla":return vesica_geometry(owner)
    purpose=owner.get("purpose") or owner.get("description") or owner.get("summary")
    return [block("overview","Overview",str(purpose))] if isinstance(purpose,str) and purpose.strip() else []
