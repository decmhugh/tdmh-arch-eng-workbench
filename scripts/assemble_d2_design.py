#!/usr/bin/env python3
"""Assemble a consolidated ``d2-design.md`` from a spec's ``d2-design/`` pages.

Spec components keep their D2 design as a multi-page ``d2-design/`` directory
(the "broken down" version used by the MkDocs static site). This script
concatenates those pages — in MkDocs nav order where available — into a single
``d2-design.md`` artifact alongside the directory. The single file satisfies
``validate_specs.py`` (which expects ``d2-design.md``) and provides a readable,
self-contained document for Confluence sync and direct review.

Usage::

    python3 scripts/assemble_d2_design.py agent-registry model-registry
    python3 scripts/assemble_d2_design.py            # all dirs lacking d2-design.md

The directory remains the source of truth; the single file is generated.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from spec_paths import REPO_ROOT, SPECS_DIR, find_spec_dir, iter_spec_dirs

MKDOCS = REPO_ROOT / "mkdocs.yml"

PAGE_SEPARATOR = "\n\n---\n\n"

_IMAGE = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")
# A link to a sibling page: bare file name, no directory, no scheme.
_SIBLING_LINK = re.compile(r"((?<!!)\[[^\]]*\]\()([\w-]+\.md(?:#[^)]*)?)(\))")


def _rebase_images(body: str, page_dir: str) -> str:
    """Prefix relative image paths so they resolve from the parent directory."""

    def fix(match: re.Match[str]) -> str:
        src = match.group(2)
        if src.startswith(("http://", "https://", "/", "../")):
            return match.group(0)
        return f"{match.group(1)}{page_dir}/{src}{match.group(3)}"

    return _IMAGE.sub(fix, body)


def _rebase_sibling_links(body: str, page_dir: str) -> str:
    """Prefix links to sibling pages so they resolve from the parent directory."""
    return _SIBLING_LINK.sub(lambda m: f"{m.group(1)}{page_dir}/{m.group(2)}{m.group(3)}", body)


def _collect_nav_paths(node: object, acc: list[str]) -> None:
    """Walk the MkDocs nav structure, collecting markdown paths in order."""
    if isinstance(node, str):
        acc.append(node)
    elif isinstance(node, list):
        for item in node:
            _collect_nav_paths(item, acc)
    elif isinstance(node, dict):
        for value in node.values():
            _collect_nav_paths(value, acc)


def _nav_order(spec_dir: Path) -> list[Path]:
    """Return d2-design pages for the spec in MkDocs nav order (may be empty)."""
    if not MKDOCS.exists():
        return []
    # MkDocs uses a custom !!python tag for emoji; ignore unknown tags safely.
    loader = yaml.SafeLoader
    loader.add_multi_constructor("tag:yaml.org,2002:python/name:", lambda *_: None)
    data = yaml.load(MKDOCS.read_text(encoding="utf-8"), Loader=loader)  # noqa: S506
    paths: list[str] = []
    _collect_nav_paths(data.get("nav", []), paths)
    prefix = f"{spec_dir.relative_to(REPO_ROOT).as_posix()}/d2-design/"
    return [REPO_ROOT / p for p in paths if p.startswith(prefix) and p.endswith(".md")]


def _fallback_order(d2_dir: Path) -> list[Path]:
    """Order pages with ``index.md`` first, then the rest alphabetically."""
    pages = sorted(d2_dir.glob("*.md"))
    index = d2_dir / "index.md"
    if index in pages:
        pages.remove(index)
        pages.insert(0, index)
    return pages


def assemble(component: str) -> Path:
    """Generate ``specs/<spec_type>/<component>/d2-design.md`` from its directory pages."""
    spec_dir = find_spec_dir(component)
    if spec_dir is None:
        raise FileNotFoundError(f"No spec '{component}' under specs/<spec_type>/")
    d2_dir = spec_dir / "d2-design"
    if not d2_dir.is_dir():
        raise FileNotFoundError(f"No d2-design/ directory for '{component}'")

    pages = _nav_order(spec_dir) or _fallback_order(d2_dir)
    missing = [p for p in pages if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Nav references missing pages: {missing}")

    bodies = [
        _rebase_sibling_links(_rebase_images(p.read_text(encoding="utf-8").strip(), d2_dir.name), d2_dir.name)
        for p in pages
    ]
    header = (
        "<!-- GENERATED FILE — do not edit directly.\n"
        "     Source: d2-design/ pages. Regenerate with scripts/assemble_d2_design.py -->\n\n"
    )
    content = header + PAGE_SEPARATOR.join(bodies) + "\n"

    out = spec_dir / "d2-design.md"
    out.write_text(content, encoding="utf-8")
    return out


def _default_components() -> list[str]:
    """Components whose consolidated d2-design.md is missing or ours to rewrite.

    Skipping components that already had an output meant the documented bare
    invocation silently refreshed nothing, so editing a page left the generated
    file stale while the command still reported success. A hand-written
    d2-design.md is still left alone — only files carrying the generated banner
    are rewritten.
    """
    result = []
    for d2_dir in (d / "d2-design" for d in iter_spec_dirs(SPECS_DIR)):
        if not d2_dir.is_dir():
            continue
        out = d2_dir.parent / "d2-design.md"
        if not out.exists() or out.read_text()[:200].lstrip().startswith("<!-- GENERATED FILE"):
            result.append(d2_dir.parent.name)
    return result


def main(argv: list[str]) -> int:
    components = argv[1:] or _default_components()
    if not components:
        print("Nothing to assemble.")
        return 0
    for component in components:
        out = assemble(component)
        rel = out.relative_to(REPO_ROOT)
        pages = _nav_order(out.parent) or _fallback_order(out.parent / "d2-design")
        print(f"Assembled {rel} from {len(pages)} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
