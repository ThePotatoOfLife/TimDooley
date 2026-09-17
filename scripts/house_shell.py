#!/usr/bin/env python3
"""Render shared Potato House navigation fragments from public surface authority."""
from __future__ import annotations

import html
import posixpath
from pathlib import Path, PurePosixPath

from house_public_surfaces import (
    child_rows,
    load_public_surfaces,
    parent_chain,
    primary_gateway_rows,
    surface_by_id,
    surfaces_by_id,
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def relative_href(from_route: str, to_route: str) -> str:
    """Return a directory-safe relative href between public canonical routes."""
    source = from_route if from_route.startswith("/") else "/" + from_route
    target = to_route if to_route.startswith("/") else "/" + to_route

    source_path = PurePosixPath(source.lstrip("/"))
    if source.endswith("/"):
        source_dir = source_path
    else:
        source_dir = source_path.parent

    target_path = target.lstrip("/") or "."
    rel = posixpath.relpath(target_path, start=str(source_dir) or ".")
    if target.endswith("/"):
        if rel == ".":
            return "./"
        if not rel.endswith("/"):
            rel += "/"
    return rel


def _nav_label(row: dict) -> str:
    return str(row.get("nav_label") or row.get("title") or row.get("id") or "")


def _anchor(from_route: str, row: dict, *, current_id: str | None = None, class_name: str = "") -> str:
    attrs = []
    if class_name:
        attrs.append(f'class="{esc(class_name)}"')
    if current_id and row.get("id") == current_id:
        attrs.append('aria-current="page"')
    attrs_text = (" " + " ".join(attrs)) if attrs else ""
    href = relative_href(from_route, row["canonical_route"])
    return f'<a href="{esc(href)}"{attrs_text}>{esc(_nav_label(row))}</a>'


def _top_level_door_id(root: Path, surface_id: str) -> str | None:
    chain = parent_chain(root, surface_id)
    primary_ids = {row["id"] for row in primary_gateway_rows(root)}
    for row in chain:
        if row["id"] in primary_ids:
            return row["id"]
    return surface_id if surface_id in primary_ids else None


def render_house_bar_for_route(
    root: Path,
    from_route: str,
    *,
    active_surface_id: str | None = None,
    compact: bool = False,
    data_surface: str = "generated",
) -> str:
    """Render House navigation for a route that may not have a durable registry row."""
    data = load_public_surfaces(root)
    by_id = surfaces_by_id(root)
    home = by_id["home"]
    active_door = _top_level_door_id(root, active_surface_id) if active_surface_id else None

    primary = "".join(
        _anchor(from_route, row, current_id=active_door, class_name="site-nav__link site-nav__link--door")
        for row in primary_gateway_rows(root)
    )

    utility_rows = []
    for utility_id in data.get("housebar_secondary_ids", []):
        row = by_id.get(utility_id)
        if row and row.get("status") == "active":
            utility_rows.append(row)
    secondary = "".join(
        _anchor(from_route, row, current_id=active_surface_id, class_name="site-nav__link site-nav__link--secondary")
        for row in utility_rows
    )

    compact_class = " site-housebar--compact" if compact else ""
    return (
        f'<header class="site-housebar{compact_class}" data-house-surface="{esc(data_surface)}">'
        '<div class="site-housebar__inner">'
        f'<a class="site-brand" href="{esc(relative_href(from_route, home["canonical_route"]))}" aria-label="Potato of Life home">'
        '<span class="site-brand__mark" aria-hidden="true">◆</span>'
        '<span class="site-brand__text">Potato of Life</span>'
        '</a>'
        '<nav class="site-primary-nav" aria-label="Primary Doors">'
        f'{primary}'
        '</nav>'
        '<nav class="site-secondary-nav" aria-label="House utilities">'
        f'{secondary}'
        '</nav>'
        '<details class="site-mobile-nav">'
        '<summary>Menu</summary>'
        '<div class="site-mobile-nav__panel">'
        '<div class="site-mobile-nav__group" aria-label="Primary Doors">'
        f'{primary}'
        '</div>'
        '<div class="site-mobile-nav__group" aria-label="House utilities">'
        f'{secondary}'
        '</div>'
        '</div>'
        '</details>'
        '</div>'
        '</header>'
    )


def render_house_bar(root: Path, surface_id: str, *, compact: bool = False) -> str:
    """Render the permanent House identity and global navigation layer."""
    surface = surface_by_id(root, surface_id)
    return render_house_bar_for_route(
        root,
        surface["canonical_route"],
        active_surface_id=surface_id,
        compact=compact,
        data_surface=surface_id,
    )


def render_specialist_house_escape(root: Path, surface_id: str, *, from_route: str | None = None) -> str:
    """Render a tiny House context trail for specialist apps without editorial chrome."""
    surface = surface_by_id(root, surface_id)
    if surface.get("shell_type") != "specialist":
        raise ValueError(f"surface is not specialist: {surface_id}")

    link_route = from_route or surface["canonical_route"]
    home = surface_by_id(root, "home")
    parent_id = surface.get("primary_parent")
    parts = [
        f'<a class="site-specialist-house__link site-specialist-house__home" href="{esc(relative_href(link_route, home["canonical_route"]))}">Potato of Life</a>'
    ]
    if parent_id and parent_id != "home":
        parent = surface_by_id(root, parent_id)
        parts.extend([
            '<span class="site-specialist-house__sep" aria-hidden="true">/</span>',
            f'<a class="site-specialist-house__link" href="{esc(relative_href(link_route, parent["canonical_route"]))}">{esc(_nav_label(parent))}</a>',
        ])
    parts.extend([
        '<span class="site-specialist-house__sep" aria-hidden="true">/</span>',
        f'<span class="site-specialist-house__current" aria-current="page">{esc(surface["title"])}</span>',
    ])
    return (
        f'<nav class="site-specialist-house" data-house-surface="{esc(surface_id)}" aria-label="House context">'
        + "".join(parts)
        + '</nav>'
    )


def render_breadcrumbs(root: Path, surface_id: str) -> str:
    surface = surface_by_id(root, surface_id)
    from_route = surface["canonical_route"]
    chain = parent_chain(root, surface_id)
    links: list[str] = []
    for index, row in enumerate(chain):
        if index == len(chain) - 1:
            links.append(f'<span aria-current="page">{esc(row["title"])}</span>')
        else:
            links.append(_anchor(from_route, row))
    return '<nav class="site-breadcrumbs" aria-label="Breadcrumb">' + '<span class="site-breadcrumbs__sep" aria-hidden="true">/</span>'.join(links) + '</nav>'


def render_route_breadcrumbs(
    root: Path,
    from_route: str,
    current_title: str,
    *,
    parent_surface_id: str | None = None,
) -> str:
    """Render a compact breadcrumb for generated pages outside the durable registry."""
    by_id = surfaces_by_id(root)
    rows: list[dict] = [by_id["home"]]
    if parent_surface_id and parent_surface_id in by_id and parent_surface_id != "home":
        chain = parent_chain(root, parent_surface_id)
        for row in chain:
            if row["id"] != "home" and row["id"] not in {item["id"] for item in rows}:
                rows.append(row)

    links = [_anchor(from_route, row) for row in rows]
    links.append(f'<span aria-current="page">{esc(current_title)}</span>')
    return '<nav class="site-breadcrumbs" aria-label="Breadcrumb">' + '<span class="site-breadcrumbs__sep" aria-hidden="true">/</span>'.join(links) + '</nav>'


def render_local_nav(root: Path, surface_id: str) -> str:
    surface = surface_by_id(root, surface_id)
    parent_id = surface.get("primary_parent")
    if not parent_id:
        return ""

    from_route = surface["canonical_route"]
    parent = surface_by_id(root, parent_id)
    siblings = child_rows(root, parent_id)
    rows = [parent, *siblings]

    seen: set[str] = set()
    unique_rows: list[dict] = []
    for row in rows:
        row_id = row["id"]
        if row_id in seen:
            continue
        seen.add(row_id)
        if row.get("status") == "active":
            unique_rows.append(row)

    if len(unique_rows) <= 1:
        return ""

    links = "".join(
        _anchor(from_route, row, current_id=surface_id, class_name="site-local-nav__link")
        for row in unique_rows
    )
    return f'<nav class="site-local-nav" aria-label="{esc(parent["title"])} section">{links}</nav>'


def render_related_routes(root: Path, surface_id: str) -> str:
    surface = surface_by_id(root, surface_id)
    from_route = surface["canonical_route"]
    by_id = surfaces_by_id(root)
    parent_id = surface.get("primary_parent")

    blocks: list[str] = []
    if parent_id and parent_id in by_id:
        parent = by_id[parent_id]
        blocks.append(
            '<div class="site-related__item"><span class="site-related__eyebrow">Up</span>'
            f'{_anchor(from_route, parent)}</div>'
        )

    if parent_id:
        siblings = [row for row in child_rows(root, parent_id) if row["id"] != surface_id][:3]
        if siblings:
            links = " · ".join(_anchor(from_route, row) for row in siblings)
            blocks.append(
                '<div class="site-related__item"><span class="site-related__eyebrow">Beside</span>'
                f'<span>{links}</span></div>'
            )

    explore = by_id.get("explore")
    sources = by_id.get("sources")
    deeper = [row for row in (explore, sources) if row and row["id"] != surface_id]
    if deeper:
        links = " · ".join(_anchor(from_route, row) for row in deeper)
        blocks.append(
            '<div class="site-related__item"><span class="site-related__eyebrow">Deeper</span>'
            f'<span>{links}</span></div>'
        )

    if not blocks:
        return ""
    return '<aside class="site-related" aria-label="Continue exploring">' + "".join(blocks) + "</aside>"


def render_house_footer_for_route(
    root: Path,
    from_route: str,
    *,
    current_surface_id: str | None = None,
) -> str:
    """Render the shared footer for registered or generated routes."""
    data = load_public_surfaces(root)
    by_id = surfaces_by_id(root)
    rows = [by_id[row_id] for row_id in data.get("footer_global_ids", []) if row_id in by_id]
    links = "".join(
        _anchor(from_route, row, current_id=current_surface_id, class_name="site-footer__link") for row in rows
    )
    return (
        '<footer class="site-footer">'
        '<div class="site-footer__brand">Potato of Life</div>'
        f'<nav class="site-footer__nav" aria-label="Footer navigation">{links}</nav>'
        '</footer>'
    )


def render_house_footer(root: Path, surface_id: str) -> str:
    surface = surface_by_id(root, surface_id)
    return render_house_footer_for_route(root, surface["canonical_route"], current_surface_id=surface_id)
