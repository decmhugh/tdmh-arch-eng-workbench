#!/usr/bin/env python3
"""Re-key confluence-page-mapping.json against the live page tree.

The mapping's keys encode a page's parent (`{parent_id}/{title}`), so any move in Confluence
makes them stale. A stale key is not fatal — the sync falls back to a title search and still
finds the page — but it hides real breakage: a page that was *deleted* looks identical to one
that merely moved, and the next sync silently recreates it as a duplicate.

This reads each mapped page's actual parent and title from Confluence and rewrites the keys.
Page ids are never invented or changed, so page history, comments and inbound links survive.

    python3 scripts/reconcile_page_mapping.py            # report only
    python3 scripts/reconcile_page_mapping.py --write    # rewrite the mapping

Dead ids are reported and kept, never dropped: deciding whether a missing page should be
recreated or forgotten needs a human, and dropping the entry quietly chooses "recreate".
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAPPING_FILE = REPO_ROOT / "references" / "confluence-page-mapping.json"


def _get(page_id: str) -> dict | None:
    base = os.environ["CONFLUENCE_BASE_URL"].rstrip("/")
    auth = f'{os.environ["CONFLUENCE_USER_EMAIL"]}:{os.environ["CONFLUENCE_API_TOKEN"]}'
    out = subprocess.run(
        ["curl", "-s", "-u", auth, f"{base}/rest/api/content/{page_id}?expand=ancestors"],
        capture_output=True, text=True,
    ).stdout
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None
    return data if "title" in data else None


def main() -> int:
    write = "--write" in sys.argv
    mapping = json.loads(MAPPING_FILE.read_text())

    rekeyed: dict[str, str] = {}
    moved, dead, unchanged = [], [], 0

    for key, page_id in mapping.items():
        if str(page_id).startswith("dry-"):
            continue  # a dry-run artefact, never a real page
        page = _get(page_id)
        if page is None:
            dead.append((key, page_id))
            rekeyed[key] = page_id
            continue
        ancestors = page.get("ancestors", [])
        parent = ancestors[-1]["id"] if ancestors else ""
        new_key = f'{parent}/{page["title"]}'
        rekeyed[new_key] = page_id
        if new_key != key:
            moved.append((key, new_key))
        else:
            unchanged += 1

    print(f"  unchanged : {unchanged}")
    print(f"  re-keyed  : {len(moved)}")
    for old, new in moved[:8]:
        print(f"      {old.split('/')[0]} -> {new.split('/')[0]}  {new.split('/', 1)[1][:52]}")
    if len(moved) > 8:
        print(f"      ... and {len(moved) - 8} more")
    if dead:
        print(f"  DEAD      : {len(dead)}  (kept in the mapping — needs a decision)")
        for key, page_id in dead:
            print(f"      {page_id}  {key}")

    if not write:
        print("\n  report only; pass --write to apply")
        return 0

    MAPPING_FILE.write_text(json.dumps(rekeyed, indent=2, ensure_ascii=False) + "\n")
    print(f"\n  wrote {MAPPING_FILE.relative_to(REPO_ROOT)} ({len(rekeyed)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
