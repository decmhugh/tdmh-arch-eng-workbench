#!/usr/bin/env python3
"""Convert Markdown to Confluence storage format (XHTML).

Features:
  - Mermaid diagrams → Aura HTML iframe macro (mermaid.js CDN render)
  - Tables, code blocks (with language highlighting)
  - Headings, lists (ordered & unordered)
  - Docusaurus/MkDocs admonitions → Confluence info/tip/warning macros
  - Inline formatting (bold, italic, code, links, images)
  - Frontmatter stripping
  - Table of Contents heading → native Confluence TOC macro

Usage (standalone):
    python3 scripts/md_to_confluence.py <markdown_file>

    # Outputs Confluence storage format XHTML to stdout.

Usage (as module):
    from md_to_confluence import md_to_confluence_storage, mermaid_to_aura
    html = md_to_confluence_storage(markdown_text)
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.parse


# ─── Mermaid → Aura HTML Macro ───────────────────────────────────────────────


def _build_aura_html_code(diagram: str) -> str:
    """Build the HTML string for the Aura params JSON."""
    return (
        "<html>\n"
        "  <body>\n"
        '    <pre class="mermaid">\n'
        f"{diagram}\n"
        "    </pre>\n"
        '    <script type="module">\n'
        "      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';\n"
        "    </script>\n"
        "  </body>\n"
        "</html>"
    )


def _encode_aura_params(html_code: str) -> str:
    """Encode the Aura params as URL-encoded JSON, then base64."""
    params_obj = {"htmlCode": html_code, "cssCode": "", "jsCode": "", "theme": "default"}
    json_str = json.dumps(params_obj, separators=(",", ":"))
    url_encoded = urllib.parse.quote(json_str, safe="")
    return base64.b64encode(url_encoded.encode("utf-8")).decode("utf-8")


def mermaid_to_aura(diagram: str) -> str:
    """Wrap a mermaid diagram in an Aura HTML iframe macro using base64 params."""
    html_code = _build_aura_html_code(diagram)
    encoded_params = _encode_aura_params(html_code)
    return (
        '<ac:structured-macro ac:name="aura-html" ac:schema-version="1">'
        f'<ac:parameter ac:name="params">{encoded_params}</ac:parameter>'
        "</ac:structured-macro>"
    )


def confluence_toc_macro() -> str:
    """Return native Confluence Table of Contents macro."""
    return '<ac:structured-macro ac:name="toc" ac:schema-version="1" />'


# ─── Markdown → Confluence Storage Format ────────────────────────────────────


def md_to_confluence_storage(md_content: str, image_map: dict | None = None) -> str:
    """Convert markdown to Confluence storage format (XHTML).

    Args:
        md_content: Raw markdown content.
        image_map: Dict mapping markdown image paths to attachment filenames.
                   e.g. {'/img/arch.png': 'arch.png'}
    """
    if image_map is None:
        image_map = {}

    # Remove frontmatter
    md_content = re.sub(r"^---\n.*?---\n", "", md_content, flags=re.DOTALL)

    lines = md_content.split("\n")
    html_parts: list[str] = []
    in_table = False
    table_rows: list[list[str]] = []
    in_code_block = False
    code_block_lang = ""
    code_block_content: list[str] = []
    in_list = False
    list_items: list[str] = []
    list_type = "ul"

    i = 0
    while i < len(lines):
        line = lines[i]

        # ── Code / Mermaid blocks ──
        if line.startswith("```"):
            if in_code_block:
                content = "\n".join(code_block_content)
                if code_block_lang == "mermaid":
                    html_parts.append(mermaid_to_aura(content))
                else:
                    lang_param = (
                        f'<ac:parameter ac:name="language">{code_block_lang}</ac:parameter>'
                        if code_block_lang
                        else ""
                    )
                    html_parts.append(
                        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
                        f"{lang_param}"
                        "<ac:plain-text-body><![CDATA["
                        + content
                        + "]]></ac:plain-text-body>"
                        "</ac:structured-macro>"
                    )
                in_code_block = False
                code_block_content = []
                code_block_lang = ""
            else:
                if in_list:
                    html_parts.append(_flush_list(list_items, list_type))
                    in_list = False
                    list_items = []
                in_code_block = True
                code_block_lang = line[3:].strip()
            i += 1
            continue

        if in_code_block:
            code_block_content.append(line)
            i += 1
            continue

        # ── Tables ──
        if "|" in line and line.strip().startswith("|"):
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            if not in_table:
                in_table = True
                table_rows = []
            stripped = line.strip()
            if re.match(r"^\|[\s\-:|]+\|$", stripped):
                i += 1
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            html_parts.append(_build_table(table_rows, image_map))
            in_table = False
            table_rows = []

        # ── Horizontal rule ──
        if line.strip() == "---":
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            html_parts.append("<hr />")
            i += 1
            continue

        # ── Headings ──
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if heading_match:
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            level = len(heading_match.group(1))
            heading_raw = heading_match.group(2).strip()
            text = _inline_format(heading_raw, image_map)
            html_parts.append(f"<h{level}>{text}</h{level}>")

            # Convert markdown TOC section to native Confluence TOC macro
            if heading_raw.lower() in {"table of contents", "contents"}:
                html_parts.append(confluence_toc_macro())
                i += 1
                while i < len(lines):
                    toc_line = lines[i]
                    if toc_line.strip() == "":
                        i += 1
                        continue
                    if re.match(r"^\s*[-*]\s+.+", toc_line) or re.match(
                        r"^\s*\d+\.\s+.+", toc_line
                    ):
                        i += 1
                        continue
                    break
                continue

            i += 1
            continue

        # ── Docusaurus / MkDocs admonitions ──
        admonition_match = re.match(
            r"^:::(info|tip|warning|danger|note|caution)\s*(.*)", line
        )
        if admonition_match:
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            admonition_type = admonition_match.group(1)
            title = admonition_match.group(2) or admonition_type.title()
            admonition_content: list[str] = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                admonition_content.append(lines[i])
                i += 1
            i += 1  # skip closing :::
            macro_type = {
                "info": "info",
                "tip": "tip",
                "warning": "warning",
                "danger": "warning",
                "note": "note",
                "caution": "warning",
            }.get(admonition_type, "info")
            content_html = md_to_confluence_storage(
                "\n".join(admonition_content).strip(), image_map
            )
            html_parts.append(
                f'<ac:structured-macro ac:name="{macro_type}" ac:schema-version="1">'
                f'<ac:parameter ac:name="title">{title}</ac:parameter>'
                f"<ac:rich-text-body>{content_html}</ac:rich-text-body>"
                "</ac:structured-macro>"
            )
            continue

        # ── MkDocs-material admonitions (??? / !!! syntax) ──
        mkdocs_admonition = re.match(r"^(?:\?\?\?|!!!)\s+(\w+)\s*\"?(.*?)\"?\s*$", line)
        if mkdocs_admonition:
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            adm_type = mkdocs_admonition.group(1).lower()
            title = mkdocs_admonition.group(2) or adm_type.title()
            adm_content: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith("    ") or lines[i].strip() == ""):
                adm_content.append(lines[i][4:] if lines[i].startswith("    ") else "")
                i += 1
            macro_type = {
                "info": "info",
                "tip": "tip",
                "warning": "warning",
                "danger": "warning",
                "note": "note",
                "example": "info",
                "abstract": "info",
                "success": "tip",
                "question": "info",
                "failure": "warning",
                "bug": "warning",
            }.get(adm_type, "info")
            content_html = md_to_confluence_storage("\n".join(adm_content).strip(), image_map)
            html_parts.append(
                f'<ac:structured-macro ac:name="{macro_type}" ac:schema-version="1">'
                f'<ac:parameter ac:name="title">{title}</ac:parameter>'
                f"<ac:rich-text-body>{content_html}</ac:rich-text-body>"
                "</ac:structured-macro>"
            )
            continue

        # ── Blockquotes ──
        if line.startswith("> "):
            if in_list:
                html_parts.append(_flush_list(list_items, list_type))
                in_list = False
                list_items = []
            quote_lines: list[str] = []
            while i < len(lines) and (lines[i].startswith("> ") or lines[i].startswith(">")):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            quote_html = md_to_confluence_storage("\n".join(quote_lines).strip(), image_map)
            html_parts.append(
                '<ac:structured-macro ac:name="info" ac:schema-version="1">'
                f"<ac:rich-text-body>{quote_html}</ac:rich-text-body>"
                "</ac:structured-macro>"
            )
            continue

        # ── Unordered list ──
        list_match = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if list_match:
            if not in_list:
                in_list = True
                list_items = []
                list_type = "ul"
            list_items.append(_inline_format(list_match.group(2), image_map))
            i += 1
            continue

        # ── Ordered list ──
        ol_match = re.match(r"^(\s*)\d+\.\s+(.*)", line)
        if ol_match:
            if not in_list:
                in_list = True
                list_items = []
                list_type = "ol"
            list_items.append(_inline_format(ol_match.group(2), image_map))
            i += 1
            continue

        # List continuation on blank line
        if in_list and line.strip() == "":
            i += 1
            continue

        # List item continuation — wrapped/indented text under a bullet is
        # folded into the current <li> so it renders as one readable item
        # instead of breaking out into a separate paragraph.
        if in_list and list_items and re.match(r"^\s+\S", line):
            list_items[-1] += " " + _inline_format(line.strip(), image_map)
            i += 1
            continue

        # End of list
        if in_list and line.strip() != "":
            html_parts.append(_flush_list(list_items, list_type))
            in_list = False
            list_items = []

        # ── Standalone image ──
        img_match = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
        if img_match:
            alt = img_match.group(1)
            src = img_match.group(2)
            html_parts.append(_build_image(alt, src, image_map))
            i += 1
            continue

        # ── Empty line ──
        if line.strip() == "":
            i += 1
            continue

        # ── Paragraph ── (join hard-wrapped lines into a single flowing paragraph)
        para_lines = [line.strip()]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            s = nxt.strip()
            if s == "":
                break
            if (
                s.startswith("```")
                or re.match(r"^#{1,6}\s", s)
                or s.startswith(">")
                or s == "---"
                or (("|" in nxt) and s.startswith("|"))
                or re.match(r"^[-*]\s+", s)
                or re.match(r"^\d+\.\s+", s)
                or re.match(r"^!\[(.*?)\]\((.*?)\)", s)
            ):
                break
            para_lines.append(s)
            i += 1
        text = _inline_format(" ".join(para_lines), image_map)
        html_parts.append(f"<p>{text}</p>")

    # Flush remaining state
    if in_table:
        html_parts.append(_build_table(table_rows, image_map))
    if in_list:
        html_parts.append(_flush_list(list_items, list_type))

    return "\n".join(html_parts)


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _inline_format(text: str, image_map: dict | None = None) -> str:
    """Apply inline markdown formatting."""
    if image_map is None:
        image_map = {}
    # Bold + italic
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
    # Inline images
    def replace_inline_image(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2)
        return _build_image_inline(alt, src, image_map)

    text = re.sub(r"!\[(.*?)\]\((.*?)\)", replace_inline_image, text)
    # Links
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)
    return text


def _build_image(alt: str, src: str, image_map: dict) -> str:
    """Build Confluence ac:image macro for a standalone image."""
    filename = _resolve_image_filename(src, image_map)
    if filename and filename.endswith(".drawio"):
        return f"<p>{_build_drawio_macro(filename)}</p>"
    if filename:
        return (
            f'<p><ac:image ac:alt="{alt}" ac:width="800">'
            f'<ri:attachment ri:filename="{filename}" />'
            "</ac:image></p>"
        )
    return f"<p><em>[Image: {alt} — source: {src}]</em></p>"


def _build_drawio_macro(filename: str) -> str:
    """Render a .drawio attachment through the draw.io macro.

    Unlike <ac:image>, this keeps per-shape links clickable — Confluence serves an embedded
    SVG through an <img> tag, which swallows any anchor inside it.

    `diagramName` must carry the `.drawio` extension. Given the bare stem the macro is still
    accepted and stored, then renders nothing at all — no error, no placeholder, just a gap.
    Verify a publish by counting "drawio" in `body.view`: zero means it silently failed.

    `lbox=0` and `links=blank` are about where a shape link lands. The macro renders in a
    Connect iframe and routes clicks itself; with the lightbox on, its viewer handles the
    click and the URL fragment is dropped, so a deep link arrives at the top of the target
    page and never scrolls. Opening in a new tab forces a full document load, which is the
    path that demonstrably honours the fragment.
    """
    return (
        '<ac:structured-macro ac:name="drawio" ac:schema-version="1">'
        f'<ac:parameter ac:name="diagramName">{filename}</ac:parameter>'
        f'<ac:parameter ac:name="diagramDisplayName">{filename}</ac:parameter>'
        '<ac:parameter ac:name="baseUrl">https://sunlife.atlassian.net/wiki</ac:parameter>'
        '<ac:parameter ac:name="lbox">0</ac:parameter>'
        '<ac:parameter ac:name="links">blank</ac:parameter>'
        "</ac:structured-macro>"
    )


def _build_image_inline(alt: str, src: str, image_map: dict) -> str:
    """Build inline ac:image macro."""
    filename = _resolve_image_filename(src, image_map)
    if filename:
        return (
            f'<ac:image ac:alt="{alt}" ac:width="600">'
            f'<ri:attachment ri:filename="{filename}" />'
            "</ac:image>"
        )
    return f"<em>[Image: {alt}]</em>"


def _resolve_image_filename(src: str, image_map: dict) -> str | None:
    """Resolve a markdown image path to a Confluence attachment filename."""
    if src in image_map:
        return image_map[src]
    basename = os.path.basename(src)
    for key, val in image_map.items():
        if os.path.basename(key) == basename or val == basename:
            return val
    if basename and ("." in basename):
        return basename
    return None


def _flush_list(items: list, list_type: str = "ul") -> str:
    tag = list_type
    items_html = "".join(f"<li><p>{item}</p></li>" for item in items)
    return f"<{tag}>{items_html}</{tag}>"


def _build_table(rows: list, image_map: dict | None = None) -> str:
    if not rows:
        return ""
    if image_map is None:
        image_map = {}
    html = "<table><colgroup>"
    for _ in rows[0]:
        html += "<col />"
    html += "</colgroup><thead><tr>"
    for cell in rows[0]:
        html += f"<th><p>{_inline_format(cell, image_map)}</p></th>"
    html += "</tr></thead><tbody>"
    for row in rows[1:]:
        html += "<tr>"
        for cell in row:
            html += f"<td><p>{_inline_format(cell, image_map)}</p></td>"
        html += "</tr>"
    html += "</tbody></table>"
    return html


# ─── CLI Entry Point ─────────────────────────────────────────────────────────


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: md_to_confluence.py <markdown_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    md_path = sys.argv[1]
    with open(md_path) as f:
        md_content = f.read()

    # Auto-detect images: scan for image references and build map
    image_map: dict[str, str] = {}
    for m in re.finditer(r"!\[.*?\]\((.*?)\)", md_content):
        src = m.group(1)
        basename = os.path.basename(src)
        if basename and "." in basename:
            image_map[src] = basename

    body = md_to_confluence_storage(md_content, image_map)
    print(body)


if __name__ == "__main__":
    main()
