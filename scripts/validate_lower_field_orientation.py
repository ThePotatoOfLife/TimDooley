#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path:str)->str:
    return (ROOT/path).read_text(encoding="utf-8",errors="replace")

def main()->int:
    errors=[]
    owner_path=ROOT/"knowledge/core/lower-field-orientation.json"
    if not owner_path.is_file():
        errors.append("missing canonical lower-field orientation owner")
    else:
        try:
            owner=json.loads(owner_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"lower-field orientation JSON invalid: {exc}")
            owner={}
        for key in ("core_thesis","frame_test","participant_observer_value","role_relations","karmic_ledger","vertical_route","lower_field_learning_questions","tim_professional_brief","tim_expert_risk_framework","sold_exploitation_taxonomy","tim_lower_field_doctrine"):
            if key not in owner:
                errors.append(f"orientation owner missing key: {key}")
        route=owner.get("canonical_routes",{}).get("orientation")
        if route!="/below/#lower-field-orientation":
            errors.append("orientation owner must route to /below/#lower-field-orientation")

    below=read("below/index.html")
    for marker in (
        'id="lower-field-orientation"',
        "THE SPUDLIGHT FIELD MANUAL",
        'id="tim-expert-brief"',
        'id="field-competencies"',
        'id="field-method"',
        'id="field-instruments"',
        'id="why-this-framework"',
        'id="what-tim-is-teaching"',
        'id="three-voices"',
        'id="swamp-lessons"',
        'id="myth-as-instrument"',
        'id="son-father-teaching"',
        'id="research-bridge"',
        'id="reader-takeaway"',
        'id="field-notes"',
        'id="professional-mythic-crosswalk"',
        'id="tim-current-questions"',
        'id="tim-expert-findings"',
        'id="tim-doctrine"',
        'id="field-outputs"',
        'id="field-mythic-center"',
        "knowledge/core/lower-field-orientation.json",
        "knowledge/core/spudlight-field-manual.json",
        'id="repair-outcomes"',
        "Diagnosis is unfinished until the relation has a closure path",
        "The creditor is tested too.",
        "lower-field-conflict-repair-casebook.json",
        'id="dog-farmer-field-guide"',
        "Farmer ↔ lolcow is the primary Farm pair",
        "Dog is adjacent rather than opposite.",
        "Now read Dog and Farmer as verbs",
        "Translate the rhetoric into testable mechanisms",
        'id="sold-exploitation-spectrum"',
        "What does it mean for a person to be “sold”?",
        'id="harm-literacy"',
        "Serious words need serious evidence",
        'id="audience-infrastructure"',
        "The middle layer: audience and infrastructure",
        "distributed Farm loop",
        'id="start-below"',
        "Choose the question, not another room",
        'id="currentness-status"',
        "Currentness before severity",
        'id="claimed-prerogative"',
        'id="ritualized-social-scripts"',
        'id="status-exile-authorship"',
        'id="tim-lower-field-paradigm"',
    ):
        if marker not in below:
            errors.append(f"Below orientation missing marker: {marker}")

    spokes={
        "shadow-farm/index.html":"../below/#lower-field-orientation",
        "context/culture/index.html":"../../below/#lower-field-orientation",
        "rooms/potatoverse-canon/beings/cia/bank/index.html":"../../../../../below/#lower-field-orientation",
        "rooms/potatoverse-canon/beings/cia/index.html":"../../../../below/#repair-outcomes",
        "questions/index.html":"../below/#lower-field-orientation",
    }
    for path,marker in spokes.items():
        if marker not in read(path):
            errors.append(f"lower-field spoke missing canonical orientation route: {path}")

    casebook_path=ROOT/"knowledge/core/lower-field-conflict-repair-casebook.json"
    if not casebook_path.is_file():
        errors.append("missing lower-field conflict/repair casebook")
    else:
        try:
            casebook=json.loads(casebook_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"lower conflict/repair casebook invalid JSON: {exc}")
            casebook={}
        if len(casebook.get("language_thresholds",[])) < 8:
            errors.append("lower conflict/repair casebook needs strong-language thresholds")
        if len(casebook.get("worked_cases",[])) < 3:
            errors.append("lower conflict/repair casebook needs three worked cases")
        if len(casebook.get("repair_outcomes",[])) < 8:
            errors.append("lower conflict/repair casebook needs explicit repair outcomes")

    shadow=read("shadow-farm/index.html")
    for marker in ('id="tim-expert-reading"','id="role-responsibility-matrix"','id="farm-primary-relation"','id="kiwi-farms-public-record"','id="conflict-language-thresholds"','id="worked-overlap-cases"','id="harm-pattern-bridge"',"Use strong words only when the evidence earns them","Read the verbs before the animal.","How a role is learned"):
        if marker not in shadow:
            errors.append(f"Shadow Farm missing conflict-discipline marker: {marker}")

    bank=read("rooms/potatoverse-canon/beings/cia/bank/index.html")
    for marker in ('id="closure-protocol"',"A symbolic debt must be able to stop being outstanding"):
        if marker not in bank:
            errors.append(f"Bank missing closure marker: {marker}")

    cia=read("rooms/potatoverse-canon/beings/cia/index.html")
    for marker in ('id="current-state-protocol"',"Read the event before the role","Then ask what is true now"):
        if marker not in cia:
            errors.append(f"CIA missing current-state marker: {marker}")

    audience_atlas_path=ROOT/"knowledge/world/lower-field-audience-infrastructure-role-atlas.json"
    if not audience_atlas_path.is_file():
        errors.append("missing lower-field audience/infrastructure atlas")
    else:
        try:
            audience_atlas=json.loads(audience_atlas_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"audience/infrastructure atlas invalid JSON: {exc}")
            audience_atlas={}
        if len(audience_atlas.get("audience_roles",[])) < 10:
            errors.append("audience/infrastructure atlas needs distributed audience roles")
        if len(audience_atlas.get("infrastructure_functions",{})) < 6:
            errors.append("audience/infrastructure atlas needs infrastructure functions")

    archetype_atlas_path=ROOT/"knowledge/world/lower-field-archetype-harm-literacy-atlas.json"
    if not archetype_atlas_path.is_file():
        errors.append("missing lower-field archetype/harm literacy atlas")
    else:
        try:
            archetype_atlas=json.loads(archetype_atlas_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"archetype/harm literacy atlas invalid JSON: {exc}")
            archetype_atlas={}
        if len(archetype_atlas.get("archetype_field",[])) < 8:
            errors.append("archetype/harm literacy atlas needs wider archetype field")
        if len(archetype_atlas.get("harm_literacy",[])) < 8:
            errors.append("archetype/harm literacy atlas needs serious-harm term boundaries")

    farm_owner_path=ROOT/"knowledge/world/farm-sektur-attention-extraction-ecology.json"
    if farm_owner_path.is_file():
        try:
            farm_owner=json.loads(farm_owner_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"farm/sektur ecology invalid JSON: {exc}")
            farm_owner={}
        if farm_owner.get("primary_relation_model",{}).get("core_pair")!="Farmer ↔ Cow/lolcow":
            errors.append("farm/sektur ecology must keep Farmer ↔ Cow/lolcow as primary Farm pair")
        if "scale_map" not in farm_owner:
            errors.append("farm/sektur ecology missing scale map")

    ritual_path=ROOT/"knowledge/world/ritual-mimesis-scapegoat-collective-ecology.json"
    if ritual_path.is_file():
        try:
            ritual=json.loads(ritual_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"ritual ecology invalid JSON: {exc}")
            ritual={}
        if len((ritual.get("social_script_library") or {}).get("scripts",[])) < 8:
            errors.append("ritual ecology needs social-script library")
        if "ritual_vs_coordination" not in ritual:
            errors.append("ritual ecology missing ritual-vs-coordination boundary")
        for key in ("status_shame_exile","no_win_and_self_sealing_frames","enemy_dependence","authorship_recovery","justice_vs_punishment","reentry_and_absolution"):
            if key not in ritual:
                errors.append(f"ritual ecology missing deep-social layer: {key}")

    war_path=ROOT/"data/spiritual-war-information-war.json"
    if war_path.is_file():
        try:
            war=json.loads(war_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"spiritual/information war model invalid JSON: {exc}")
            war={}
        if "son_thomas_narrative_contest" not in war:
            errors.append("spiritual/information war model missing Son/Thomas narrative contest")

    dog_farmer_path=ROOT/"knowledge/world/dog-farmer-role-ecology.json"
    if not dog_farmer_path.is_file():
        errors.append("missing Dog/Farmer role ecology owner")
    else:
        try:
            dog_farmer=json.loads(dog_farmer_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Dog/Farmer role ecology invalid JSON: {exc}")
            dog_farmer={}
        guide=dog_farmer.get("public_field_guide",{})
        if len(guide.get("dog_action_lexicon",[])) < 10:
            errors.append("Dog/Farmer owner needs expanded Dog action lexicon")
        if len(guide.get("farmer_action_lexicon",[])) < 10:
            errors.append("Dog/Farmer owner needs expanded Farmer action lexicon")
        if len(guide.get("rhetoric_translation",{})) < 6:
            errors.append("Dog/Farmer owner needs rhetoric translation")
        if len(guide.get("empirical_crosswalk",{})) < 5:
            errors.append("Dog/Farmer owner needs empirical psychology crosswalk")
        if "prerogative_model" not in dog_farmer:
            errors.append("Dog/Farmer owner missing prerogative model")
        if "role_responsibility_matrix" not in dog_farmer:
            errors.append("Dog/Farmer owner missing role responsibility matrix")
        if len((dog_farmer.get("deception_and_manipulation_indicators") or {}).get("indicators",[])) < 8:
            errors.append("Dog/Farmer owner needs deception/manipulation indicators")

    cast=read("rooms/potatoverse-canon/beings/cast-ecology/index.html")
    for marker in ('id="role-expiry"',"A role needs both an entry condition and a stopping condition","current state → symbolic role last"):
        if marker not in cast:
            errors.append(f"Cast Ecology missing role-expiry marker: {marker}")

    roots=read("rooms/archive-sources/index.html")
    for marker in ('<h1>Roots / Evidence</h1>','id="movement-provenance"','id="first-party-testimony"','id="witness-distance"','id="repetition-source-independence"','id="root-questions"',"Follow the thing that moved"):
        if marker not in roots:
            errors.append(f"Roots / Evidence hub missing marker: {marker}")

    forge=read("rooms/research-lab/index.html")
    for marker in ('<h1>Forge / Repair</h1>','id="lower-field-forge"','id="field-assessment"','id="son-narrative-contest"','id="tim-method-in-forge"','id="ritual-coordination-test"','id="interpretive-justice-gates"','id="forge-output"',"Who, since when, how active, how harmful, what goal?"):
        if marker not in forge:
            errors.append(f"Forge / Repair hub missing marker: {marker}")

    basin_contract=json.loads(read("data/house/below-basin-spatial-contract.json"))
    stations=((basin_contract.get("reader_stations") or {}).get("stations") or [])
    if [row.get("label") for row in stations] != ["Below Basin","Farm / Sektur","Roots / Evidence","Forge / Repair"]:
        errors.append("Below Basin contract must expose exactly four reader stations in canonical order")
    currentness=(basin_contract.get("currentness_contract") or {}).get("states") or {}
    for state in ("historical","dormant","active","escalating","repairing","closed","unknown"):
        if state not in currentness:
            errors.append(f"Below currentness contract missing state: {state}")

    access=json.loads(read("data/house/site-access.json"))
    entry=next((row for row in access.get("entries",[]) if row.get("id")=="below"),None)
    if not entry:
        errors.append("site access missing below entry")
    else:
        if entry.get("route")!="/below/#lower-field-orientation":
            errors.append("site access below entry does not open orientation center")
        aliases={str(x).casefold() for x in entry.get("aliases",[])}
        for alias in ("lower field","participant observer","repair","exit"):
            if alias not in aliases:
                errors.append(f"site access below entry missing alias: {alias}")

    if errors:
        print("LOWER FIELD ORIENTATION: FAIL")
        for error in errors:
            print("-",error)
        return 1
    print("LOWER FIELD ORIENTATION: PASS")
    print("- Below owns mission, experience, competing frames and exit")
    print("- specialist lower pages route back to the same center")
    print("- global access resolves lower-field questions to the center")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
