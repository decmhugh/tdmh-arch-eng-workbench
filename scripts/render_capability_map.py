#!/usr/bin/env python3
"""Render the ACP capability map and its forward roadmap as draw.io diagrams.

Both diagrams are generated from the markdown rather than drawn by hand, so neither can
drift from the tables it illustrates. Regenerate whenever a status or a rank changes:

    python3 scripts/render_capability_map.py --export

The detailed diagram comes from section 4 of docs/capability-map.md. The summary adds two
band from docs/capability-roadmap.md - the proposed rank - because the question that view
is put in front of is "which of these do we rank", and a number in a footnote cannot be
clicked, argued with, or traced back to the group it lands in.

Without --export it writes the .drawio only. The SVG export shells out to the draw.io
desktop CLI and pins --embed-svg-fonts false: the default (true) rasterises every label
into a base64 PNG, which Confluence then renders through an <img> tag where foreignObject
is disabled, and the diagram arrives with no readable text at all.

Every shape is html=0 for the same reason. HTML labels let draw.io style individual runs,
but it emits them inside foreignObject with only a "viewer does not support" text fallback
- which is what Confluence and Bitbucket both fall back to. Plain labels cost per-run bold
and buy text that renders everywhere.

That fallback also refuses to wrap: a label too wide for its shape is truncated to one line
with an ellipsis rather than flowed onto a second. So cards are sized to the longest label
and carry exactly one line.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SOURCE = REPO_ROOT / "docs" / "capability-map.md"
ROADMAP = REPO_ROOT / "docs" / "capability-roadmap.md"
OUT_DIR = REPO_ROOT / "docs" / "assets"
DRAWIO_APP = Path("/Applications/draw.io.app/Contents/MacOS/draw.io")

# Every card deep-links to a heading on the page that carries its detail.
#
# Two details, both learned the hard way. The URL needs the page-title slug: without it
# Confluence normalises the path and drops the fragment, dumping the reader at the top of the
# page. And the fragment is the *heading text with spaces as hyphens* - not the
# PageTitleNoSpaces-anchor form the REST body.view still reports, which is the legacy
# renderer's and does not match what the live page uses.
#
# Capability cards target the group heading rather than the individual row because a row
# anchor depends on the anchor macro, whose fragment format is unverified here. A group
# heading is a real heading in the source markdown, lands the reader on the table containing
# the capability, and is the exact format of a link copied from the live page.
DETAIL_PAGE_ID = os.environ.get("CAPABILITY_MAP_PAGE_ID", "113134797174")
DETAIL_PAGE_TITLE = os.environ.get("CAPABILITY_MAP_PAGE_TITLE", "ACP Capability Map (Luminate)")
ROADMAP_PAGE_ID = os.environ.get("CAPABILITY_ROADMAP_PAGE_ID", "113235853863")
ROADMAP_PAGE_TITLE = os.environ.get(
    "CAPABILITY_ROADMAP_PAGE_TITLE", "ACP Capability Map \u2014 Future Roadmap"
)
CONFLUENCE_BASE = os.environ.get("CONFLUENCE_BASE_URL", "https://sunlife.atlassian.net/wiki")
# Deliberately not CONFLUENCE_SPACE_KEY: the shared credential file exports that as DPEP, which
# would silently bake links to the wrong space into every card.
SPACE_KEY = os.environ.get("CAPABILITY_MAP_SPACE_KEY", "T1KACP")


def _page_link(page_id: str, page_title: str, heading: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "+", page_title).strip("+")
    anchor = re.sub(r"\s+", "-", heading.strip())
    # Confluence leaves ASCII punctuation literal in a fragment and encodes the rest.
    anchor = "".join(c if ord(c) < 128 else quote(c) for c in anchor)
    return f"{CONFLUENCE_BASE}/spaces/{SPACE_KEY}/pages/{page_id}/{slug}#{anchor}"


def _detail_link(heading: str) -> str:
    return _page_link(DETAIL_PAGE_ID, DETAIL_PAGE_TITLE, heading)


def _roadmap_link(heading: str) -> str:
    return _page_link(ROADMAP_PAGE_ID, ROADMAP_PAGE_TITLE, heading)


# Where a ranked card lands, keyed on its "Where it stands" cell. The heading text must match
# the roadmap page exactly, because the link fragment is derived from it.
STANDS = {
    "Accepted": ("4. Accepted, awaiting capacity", "#FFF2CC", "#D6B656"),
    "Ballot": ("5. The full ballot", "#DAE8FC", "#6C8EBF"),
    "Nothing": ("6. Not in Luminate at all", "#F8CECC", "#B85450"),
}

# The summary view has narrower cards than the detailed one and its labels must stay on a
# single line, so a handful of catalogue names are abbreviated. Only shortenings that keep
# the capability recognisable belong here - the full name is one click away on the parent
# page. _check_fits() fails the build if a label still overflows, so this cannot silently
# fall back to a truncated card.
SHORT = {
    "CAP-06": "Machine identity",
    "CAP-13": "Attribute tagging & classification",
    "CAP-17": "Evaluation & quality gating",
    "CAP-19": "Regulatory reporting & evidence",
    "CAP-20": "Observability & cost",
    "CAP-22": "Federated gateways",
    "CAP-24": "Chain authorization",
    "CAP-26": "Conditional access",
    "CAP-27": "Agent skills registry",
}

# Keyed on the status glyph, which is the one stable token in the status cell.
STATUS_LABEL = {
    "\u2705": "Available",
    "\U0001f7e1": "Partial",
    "\u26a0": "Modelled, not enforced",
    "\U0001f4d0": "Designed, not built",
    "\u274c": "Gap",
}

# The four delivery states the diagrams colour by. The catalogue keeps all five glyphs because
# modelled-versus-enforced is the distinction it exists to make; a picture answers a coarser
# question - can we use it, is anyone building it, has anyone designed it - and on that question
# a modelled-but-unenforced control and a partial one land in the same place.
DELIVERY = [
    ({"\u2705"}, "#D5E8D4", "#82B366", "Capabilities available today"),
    ({"\U0001f7e1", "\u26a0"}, "#FFF2CC", "#D6B656", "Partly built, or in the AIC backlog"),
    ({"\U0001f4d0"}, "#DAE8FC", "#6C8EBF", "Designed \u2014 no build, no AIC ticket"),
    ({"\u274c"}, "#F8CECC", "#B85450", "Capabilities with nothing at all"),
]
STYLE = {g: (fill, stroke) for glyphs, fill, stroke, _ in DELIVERY for g in glyphs}


def delivery_counts(groups: list[dict]) -> list[tuple[int, str, str, str]]:
    """Capability counts per delivery band, in legend order."""
    seen: dict[str, int] = {}
    for grp in groups:
        for cap in grp["caps"]:
            seen[cap["glyph"]] = seen.get(cap["glyph"], 0) + 1
    return [(sum(seen.get(g, 0) for g in glyphs), fill, stroke, label)
            for glyphs, fill, stroke, label in DELIVERY]

CARD_W, CARD_H, CARD_GAP = 410, 44, 8
COL_GAP, ROW_GAP = 26, 26
PAD, HEADER = 14, 34
MARGIN_X, TITLE_H, LEGEND_H = 24, 62, 54

# Condensed one-page view.
S_CARD_W, S_CARD_H, S_CARD_GAP = 300, 30, 6
S_PAD, S_HEADER, S_COL_GAP, S_ROW_GAP = 10, 26, 20, 20
S_MARGIN, S_FONT = 22, 10

# Helvetica averages a shade over half the point size per character. Deliberately
# pessimistic: an underestimate here reappears as a silently truncated card.
CHAR_W_RATIO = 0.55

ROW_RE = re.compile(r'^\| <a id="cap-\d+"></a>\*\*(CAP-\d+)\*\* \| \*\*(.+?)\*\* \|')
GROUP_RE = re.compile(r"^### (Group [A-Z]) \u2014 (.+)$")
# The ranked table carries section-header rows with an empty rank cell; those do not match and
# are skipped, which is what keeps the 1..N check meaningful.
RANKED_RE = re.compile(
    r"^\| \*\*(\d+)\*\* \| (.+?) \| ([A-F]) \| .*?\| \*{0,2}(Accepted|Ballot|Nothing)\*{0,2} \|"
)


def parse() -> list[dict]:
    """Pull the group and capability rows out of section 4."""
    text = SOURCE.read_text(encoding="utf-8")
    section = text[text.index("## 4. Capability catalogue") : text.index("## 5.")]

    groups: list[dict] = []
    for line in section.splitlines():
        g = GROUP_RE.match(line)
        if g:
            groups.append({"id": g.group(1), "name": g.group(2), "caps": []})
            continue
        m = ROW_RE.match(line)
        if not m or not groups:
            continue
        status_cell = [c.strip() for c in line.split("|")][4]
        glyph = next((k for k in STATUS_LABEL if status_cell.startswith(k)), None)
        if glyph is None:
            raise SystemExit(f"unrecognised status for {m.group(1)}: {status_cell!r}")
        groups[-1]["caps"].append({"id": m.group(1), "name": m.group(2), "glyph": glyph})
    if not groups:
        raise SystemExit("no capability groups parsed - has section 4 changed shape?")
    return groups


def parse_roadmap() -> dict:
    """Pull the ranked and underway rows the summary view renders as cards.

    Read from the roadmap's own tables rather than restated, for the same reason the
    catalogue diagram is generated from section 4: a hand-maintained second copy of a
    ranking is one that silently disagrees with the list people actually meet on.
    """
    roadmap = ROADMAP.read_text(encoding="utf-8")
    gap_src = SOURCE.read_text(encoding="utf-8")

    def section(text: str, start: str, end: str) -> str:
        return text[text.index(start) : text.index(end)]

    ranked_src = section(roadmap, "## 1. Proposed ranking", "## 2. Work underway")
    gap = section(gap_src, "## 6. Gap register", "## 6a.")

    ranked = [
        {
            "rank": int(m.group(1)),
            "name": m.group(2).strip(),
            "group": m.group(3),
            "stands": m.group(4),
        }
        for m in (RANKED_RE.match(ln) for ln in ranked_src.splitlines())
        if m
    ]
    if not ranked:
        raise SystemExit("no ranked rows parsed - has section 1 of the roadmap changed shape?")
    if [r["rank"] for r in ranked] != list(range(1, len(ranked) + 1)):
        raise SystemExit(f"ranks are not 1..N: {[r['rank'] for r in ranked]}")

    return {
        "ranked": ranked,
        "nothing": len([r for r in ranked if r["stands"] == "Nothing"]),
        "gaps": len([ln for ln in gap.splitlines() if ln.startswith(("| [CAP", "| **"))]),
    }


def _check_fits(label: str, width: int, font: int) -> None:
    limit = int((width - 2 * S_PAD - 8) / (CHAR_W_RATIO * font))
    if len(label) > limit:
        raise SystemExit(
            f"label would be truncated: {label!r} is {len(label)} chars, {limit} fit. "
            f"Shorten it at the source, or add a SHORT entry."
        )


def box(nid, label, x, y, w, h, style, parent="1", link=None) -> str:
    # Literal newlines in an XML attribute get normalised to spaces, so encode them.
    value = escape(label).replace("\n", "&#xa;")
    geometry = f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
    if link:
        # A linked shape has to be wrapped: the label and id move onto the UserObject.
        return (
            f'<UserObject label="{value}" link={quoteattr(link)} id="{nid}">'
            f'<mxCell style="{style}" vertex="1" parent="{parent}">{geometry}</mxCell>'
            "</UserObject>"
        )
    return (
        f'<mxCell id="{nid}" value="{value}" style="{style}" vertex="1" parent="{parent}">'
        f"{geometry}</mxCell>"
    )


def build(groups: list[dict]) -> str:
    cols = 3
    rows = [groups[i : i + cols] for i in range(0, len(groups), cols)]
    col_w = CARD_W + 2 * PAD

    cells: list[str] = []
    total, generated = sum(len(g["caps"]) for g in groups), 0

    y = TITLE_H + LEGEND_H
    for row in rows:
        heights = {
            g["id"]: HEADER + len(g["caps"]) * (CARD_H + CARD_GAP) + PAD for g in row
        }
        for ci, group in enumerate(row):
            gx = MARGIN_X + ci * (col_w + COL_GAP)
            cells.append(
                box(
                    f'grp-{group["id"].replace(" ", "-")}',
                    f'{group["id"]} \u2014 {group["name"]}',
                    gx,
                    y,
                    col_w,
                    heights[group["id"]],
                    "swimlane;html=0;startSize=34;fontSize=13;fontStyle=1;"
                    "fillColor=#F7F9FC;strokeColor=#1A1A2E;fontColor=#1A1A2E;"
                    "swimlaneFillColor=#FFFFFF;rounded=0;",
                )
            )
            cy = HEADER + PAD // 2
            for cap in group["caps"]:
                fill, stroke = STYLE[cap["glyph"]]
                cells.append(
                    box(
                        f'{cap["id"].lower()}',
                        f'{cap["id"]}  \u00b7  {cap["name"]}',
                        PAD,
                        cy,
                        CARD_W,
                        CARD_H,
                        f"rounded=1;arcSize=8;html=0;whiteSpace=wrap;align=left;"
                        f"spacingLeft=10;spacingRight=8;verticalAlign=middle;fontSize=11;"
                        f"fillColor={fill};strokeColor={stroke};fontColor=#22222E;",
                        parent=f'grp-{group["id"].replace(" ", "-")}',
                        link=_detail_link(f'{group["id"]} \u2014 {group["name"]}'),
                    )
                )
                cy += CARD_H + CARD_GAP
                generated += 1
        y += max(heights.values()) + ROW_GAP

    width = MARGIN_X * 2 + cols * col_w + (cols - 1) * COL_GAP

    cells.insert(
        0,
        box(
            "title",
            "ACP Capability Map \u2014 Luminate coverage",
            MARGIN_X,
            16,
            width - 2 * MARGIN_X,
            30,
            "text;html=0;align=left;verticalAlign=middle;fontSize=20;fontStyle=1;fontColor=#1A1A2E;",
        ),
    )
    cells.insert(
        1,
        box(
            "subtitle",
            f"{total} capabilities, verified against built code. "
            "Generated from docs/capability-map.md \u2014 do not edit by hand.",
            MARGIN_X,
            44,
            width - 2 * MARGIN_X,
            16,
            "text;html=0;align=left;verticalAlign=middle;fontSize=11;fontColor=#5A5A6E;",
        ),
    )

    legend = [(f"{n}  {label}", fill, stroke, 1, int(30 + len(label) * CHAR_W_RATIO * 11))
              for n, fill, stroke, label in delivery_counts(groups)]

    lx = MARGIN_X
    for i, (text_, fill, stroke, sw, w) in enumerate(legend):
        cells.insert(
            2,
            box(
                f"legend-{i}",
                text_,
                lx,
                TITLE_H + 6,
                w,
                26,
                f"rounded=1;arcSize=10;html=0;align=left;spacingLeft=8;verticalAlign=middle;"
                f"fontSize=10.5;fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
                f"fontColor=#22222E;",
            ),
        )
        lx += w + 8

    if generated != total:
        raise SystemExit(f"card count mismatch: {generated} rendered, {total} parsed")

    return _document("Capability map", "capability-map", cells, width, y)


def _document(name: str, ident: str, cells: list[str], width: int, height: int) -> str:
    return (
        '<mxfile host="app.diagrams.net">'
        f'<diagram name="{name}" id="{ident}">'
        f'<mxGraphModel dx="{width}" dy="{height}" grid="0" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{width}" pageHeight="{height}" math="0" shadow="0">'
        f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(cells)}</root>'
        "</mxGraphModel></diagram></mxfile>"
    )


def build_summary(groups: list[dict], roadmap: dict) -> str:
    """The condensed one-page view: the catalogue, then the roadmap, all of it clickable."""
    cols = 3
    rows = [groups[i : i + cols] for i in range(0, len(groups), cols)]
    col_w = S_CARD_W + 2 * S_PAD
    width = S_MARGIN * 2 + cols * col_w + (cols - 1) * S_COL_GAP
    inner = width - 2 * S_MARGIN

    bands = delivery_counts(groups)
    total = sum(len(g["caps"]) for g in groups)
    ranked = roadmap["ranked"]

    cells = [
        box("title", "ACP Capability Map \u2014 at a glance", S_MARGIN, 18, inner, 28,
            "text;html=0;align=left;verticalAlign=middle;fontSize=21;fontStyle=1;fontColor=#1A1A2E;"),
        box("subtitle",
            f"Luminate coverage of the capabilities a Sun Life onboarding needs, and the "
            f"{len(ranked)} ranked next. Every card is a link.",
            S_MARGIN, 48, inner, 16,
            "text;html=0;align=left;verticalAlign=middle;fontSize=11;fontColor=#5A5A6E;"),
    ]

    # The four bands are the summary: a count and what the colour means, at a size that reads
    # from across a room. There is no separate tile row - a total nobody acts on was taking the
    # space the key needed.
    band_w = (inner - 3 * 14) // 4
    for i, (n, fill, stroke, label) in enumerate(bands):
        bx = S_MARGIN + i * (band_w + 14)
        cells.append(box(f"band-{i}", "", bx, 76, band_w, 76,
                         f"rounded=1;arcSize=8;html=0;fillColor={fill};strokeColor={stroke};"
                         f"strokeWidth=2;"))
        cells.append(box(f"band-{i}-n", str(n), bx + 14, 86, band_w - 28, 32,
                         "text;html=0;align=left;verticalAlign=middle;fontSize=28;fontStyle=1;"
                         "fontColor=#1A1A2E;"))
        _check_fits(label, band_w, 10)
        cells.append(box(f"band-{i}-l", label, bx + 14, 120, band_w - 28, 18,
                         "text;html=0;align=left;verticalAlign=middle;fontSize=10;fontColor=#22222E;"))

    y, rendered = 176, 0
    for row in rows:
        heights = {g["id"]: S_HEADER + len(g["caps"]) * (S_CARD_H + S_CARD_GAP) + S_PAD for g in row}
        for ci, group in enumerate(row):
            gid = f'sgrp-{group["id"].replace(" ", "-")}'
            cells.append(box(gid, f'{group["id"]} \u2014 {group["name"]}',
                             S_MARGIN + ci * (col_w + S_COL_GAP), y, col_w, heights[group["id"]],
                             "swimlane;html=0;startSize=26;fontSize=11;fontStyle=1;"
                             "fillColor=#F7F9FC;strokeColor=#1A1A2E;fontColor=#1A1A2E;"
                             "swimlaneFillColor=#FFFFFF;rounded=0;"))
            cy = S_HEADER + S_PAD // 2
            for cap in group["caps"]:
                fill, stroke = STYLE[cap["glyph"]]
                label = f'{cap["id"]}  \u00b7  {SHORT.get(cap["id"], cap["name"])}'
                _check_fits(label, S_CARD_W, S_FONT)
                cells.append(
                    box(f's-{cap["id"].lower()}', label, S_PAD, cy, S_CARD_W, S_CARD_H,
                        f"rounded=1;arcSize=8;html=0;align=left;spacingLeft=8;spacingRight=6;"
                        f"verticalAlign=middle;fontSize={S_FONT};fillColor={fill};"
                        f"strokeColor={stroke};fontColor=#22222E;",
                        parent=gid,
                        link=_detail_link(f'{group["id"]} \u2014 {group["name"]}'))
                )
                cy += S_CARD_H + S_CARD_GAP
                rendered += 1
        y += max(heights.values()) + S_ROW_GAP

    if rendered != total:
        raise SystemExit(f"summary card mismatch: {rendered} rendered, {total} parsed")

    def band(ident: str, title: str, subtitle: str, items: list[dict], card, top: int) -> int:
        """A full-width swimlane of clickable cards, in the same 3 columns as the groups."""
        per_col = -(-len(items) // cols)
        height = S_HEADER + 18 + per_col * (S_CARD_H + S_CARD_GAP) + S_PAD
        cells.append(box(ident, title, S_MARGIN, top, inner, height,
                         "swimlane;html=0;startSize=26;fontSize=12;fontStyle=1;"
                         "fillColor=#F7F9FC;strokeColor=#1A1A2E;fontColor=#1A1A2E;"
                         "swimlaneFillColor=#FFFFFF;rounded=0;"))
        cells.append(box(f"{ident}-sub", subtitle, S_PAD, S_HEADER - 2, inner - 2 * S_PAD, 14,
                         "text;html=0;align=left;verticalAlign=middle;fontSize=9.5;"
                         "fontColor=#5A5A6E;", parent=ident))
        for i, item in enumerate(items):
            label, fill, stroke, link = card(item)
            _check_fits(label, S_CARD_W, S_FONT)
            col, row_i = divmod(i, per_col)
            cells.append(box(
                f"{ident}-{i}", label,
                S_PAD + col * (col_w + S_COL_GAP),
                S_HEADER + 16 + row_i * (S_CARD_H + S_CARD_GAP),
                S_CARD_W, S_CARD_H,
                f"rounded=1;arcSize=8;html=0;align=left;spacingLeft=8;spacingRight=6;"
                f"verticalAlign=middle;fontSize={S_FONT};fillColor={fill};strokeColor={stroke};"
                f"fontColor=#22222E;",
                parent=ident, link=link))
        return height

    def ranked_card(r: dict):
        heading, fill, stroke = STANDS[r["stands"]]
        return (f'#{r["rank"]} \u00b7 {r["group"]} \u00b7 {r["name"]}', fill, stroke,
                _roadmap_link(heading))

    y += 4
    y += band(
        "roadmap-ranked",
        "Future roadmap \u2014 proposed rank for the next Product Board round",
        f'Same colours as above. Amber = in the AIC backlog \u00b7 blue = an idea on the ballot '
        f'\u00b7 red = nothing in Luminate at all \u2014 no idea, no design, no code \u2014 so ranking it '
        f'achieves nothing ({roadmap["nothing"]} of {len(ranked)}).',
        ranked, ranked_card, y)

    return _document("Capability map \u2014 summary", "capability-map-summary", cells, width,
                     y + S_MARGIN)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--export", action="store_true", help="also export SVG via the draw.io CLI")
    args = ap.parse_args()

    groups = parse()
    roadmap = parse_roadmap()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = sum(len(g["caps"]) for g in groups)

    outputs = {
        "capability-map": build(groups),
        "capability-map-summary": build_summary(groups, roadmap),
    }
    for stem, xml in outputs.items():
        (OUT_DIR / f"{stem}.drawio").write_text(xml, encoding="utf-8")
    print(
        f"  wrote {len(outputs)} diagrams - {len(groups)} groups, {total} capabilities, "
        f"{len(roadmap['ranked'])} ranked"
    )

    if not args.export:
        return 0
    if not DRAWIO_APP.exists():
        print(f"  draw.io CLI not found at {DRAWIO_APP} - skipping SVG export", file=sys.stderr)
        return 1
    for stem in outputs:
        svg = OUT_DIR / f"{stem}.svg"
        subprocess.run(
            [str(DRAWIO_APP), "--export", "--format", "svg", "--embed-svg-fonts", "false",
             "--border", "12", "--output", str(svg), str(OUT_DIR / f"{stem}.drawio")],
            check=True, capture_output=True,
        )
        print(f"  wrote {svg.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
