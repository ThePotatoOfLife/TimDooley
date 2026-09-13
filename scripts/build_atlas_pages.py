#!/usr/bin/env python3
"""Build additive canonical Atlas pages without owning presentation logic."""
from __future__ import annotations
import os,shutil
from pathlib import Path

from atlas_runtime import build_runtime
from atlas_model import by_id
from atlas_render import page_shell,render_landing,render_node
from atlas_export import write_public_index

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
BASE_URL=os.environ.get('SITE_BASE_URL','https://thepotatooflife.github.io/TimDooley').rstrip('/')

def write(rel:str,text:str)->None:
    path=OUT/rel/'index.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

def copy_design_system()->None:
    source=ROOT/'app/design-system.css';target=OUT/'app/design-system.css';target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)

def build_pages()->list[str]:
    OUT.mkdir(parents=True,exist_ok=True);copy_design_system();model=build_runtime();nodes=by_id(model)
    urls=[f'{BASE_URL}/atlas/']
    write('atlas',page_shell('Atlas','Canonical current knowledge plane for the Potato of Life archive.',render_landing(model,nodes),canonical=urls[0],depth=1))
    for node in nodes.values():
        canonical=f'{BASE_URL}{node["route"]}'
        write(f'atlas/{node["id"]}',page_shell(node['title'],node['summary'],render_node(node,nodes),canonical=canonical,depth=2))
        urls.append(canonical)
    write_public_index(model,OUT/'data'/'atlas-index.json')
    return urls

def main()->int:
    urls=build_pages();print(f'ATLAS PAGES BUILT: {len(urls)-1} nodes + landing + public index');return 0

if __name__=='__main__':raise SystemExit(main())
