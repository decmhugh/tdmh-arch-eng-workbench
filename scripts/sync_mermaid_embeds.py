#!/usr/bin/env python3
"""Sync fenced mermaid blocks in spec pages from their ``.mmd`` source files.

A spec page marks a generated diagram with a pair of comments::

    <!-- BEGIN GENERATED: journey (source: ../customer-journey.mmd) -->
    ```mermaid
    ...
    ```
    <!-- END GENERATED: journey -->

The block between the markers is rewritten from the source file, so the
published copy cannot drift from the diagram it claims to render. The source
path is relative to the page.

Usage::

    python3 scripts/sync_mermaid_embeds.py            # rewrite in place
    python3 scripts/sync_mermaid_embeds.py --check    # fail if any block is stale

``--check`` is what CI runs; it never writes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "specs"

BLOCK = re.compile(
    r"(?P<begin><!-- BEGIN GENERATED: (?P<name>[\w-]+) \(source: (?P<src>[^)]+)\) -->\n)"
    r"```mermaid\n(?P<body>.*?)```\n"
    r"(?P<end><!-- END GENERATED: (?P=name) -->)",
    re.DOTALL,
)

# Leading %% lines are authoring notes for the .mmd itself, not part of the diagram.
COMMENT_PREFIX = "%%"

# Assembled pages (d2-design.md) copy the markers from their source pages; syncing them
# would resolve the relative source path from the wrong directory.
GENERATED_MARKER = "<!-- GENERATED FILE"


def _diagram_source(mmd_path: Path) -> str:
    """Return the renderable diagram body, dropping leading ``%%`` authoring notes."""
    lines = mmd_path.read_text(encoding="utf-8").splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.strip().startswith(COMMENT_PREFIX) or not line.strip():
            start = index + 1
            continue
        break
    return "\n".join(lines[start:]).strip() + "\n"


def sync_page(page: Path, *, check: bool) -> list[str]:
    """Rewrite (or verify) every generated block in ``page``. Returns stale block names."""
    original = page.read_text(encoding="utf-8")
    stale: list[str] = []

    def replace(match: re.Match[str]) -> str:
        src = (page.parent / match.group("src")).resolve()
        if not src.exists():
            raise FileNotFoundError(f"{page}: source '{match.group('src')}' not found")
        body = _diagram_source(src)
        if body != match.group("body"):
            stale.append(match.group("name"))
        return f"{match.group('begin')}```mermaid\n{body}```\n{match.group('end')}"

    updated = BLOCK.sub(replace, original)
    if stale and not check:
        page.write_text(updated, encoding="utf-8")
    return stale


def main(argv: list[str]) -> int:
    check = "--check" in argv
    pages = sorted(SPECS_DIR.glob("**/*.md"))
    stale_pages: list[tuple[Path, list[str]]] = []
    synced = 0

    for page in pages:
        text = page.read_text(encoding="utf-8")
        if text.startswith(GENERATED_MARKER):
            continue
        names = sync_page(page, check=check)
        if names:
            stale_pages.append((page, names))
        elif BLOCK.search(text):
            synced += 1

    if not stale_pages:
        print(f"All generated mermaid blocks are in sync ({synced} page(s) checked).")
        return 0

    for page, names in stale_pages:
        rel = page.relative_to(REPO_ROOT)
        verb = "STALE" if check else "updated"
        print(f"  {verb}: {rel} — {', '.join(names)}")

    if check:
        print("\nERROR: embedded diagrams are stale. Run:")
        print("  python3 scripts/sync_mermaid_embeds.py")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
