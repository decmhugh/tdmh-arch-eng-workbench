#!/usr/bin/env python3
"""Repoint Jira links at the typed spec layout (specs/<spec_type>/<component>/).

Specs moved from ``specs/<component>/`` to ``specs/<spec_type>/<component>/``. Jira tickets
created before the move link to the old Bitbucket paths, which now 404. This rewrites those
links in each ticket's description and Acceptance Criteria, using ``specs/epic-mapping.json``
(on the checked-out branch — run it from main after the move merges) as the component → path map.

Works on the Atlassian Document Format (api/3) so formatting is untouched: only text nodes and
link hrefs are rewritten. Idempotent — an already-typed path never matches.

Usage::

    python3 scripts/relink_jira_spec_paths.py              # dry run: report what would change
    python3 scripts/relink_jira_spec_paths.py --apply      # write the changes
    python3 scripts/relink_jira_spec_paths.py --jql 'key = EACPP-791' --apply
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jira_http import JiraHTTPError, request  # noqa: E402
from spec_paths import SPECS_DIR  # noqa: E402

DEFAULT_JQL = 'project = EACPP AND text ~ "acp-product-specs"'
FIELDS = ("description", "customfield_10029")  # customfield_10029 = Acceptance Criteria


def build_pattern(mapping: list[dict]) -> tuple[re.Pattern[str], dict[str, str]]:
    paths = {m["component"]: m["spec_dir"] for m in mapping if "/" in m.get("spec_dir", "")}
    if not paths:
        raise SystemExit("epic-mapping.json has no typed spec_dir values — run from a checkout after the move")
    names = sorted(paths, key=len, reverse=True)
    rx = re.compile(r"(acp-product-specs/(?:browse/|raw/)?specs/)(" + "|".join(map(re.escape, names)) + r")(?![\w-])")
    return rx, paths


def rewrite(node: object, rx: re.Pattern[str], paths: dict[str, str]) -> tuple[object, int]:
    """Return (node with every matching string rewritten, number of replacements)."""
    if isinstance(node, str):
        new, n = rx.subn(lambda m: m.group(1) + paths[m.group(2)], node)
        return new, n
    if isinstance(node, list):
        total, out = 0, []
        for item in node:
            new, n = rewrite(item, rx, paths)
            out.append(new)
            total += n
        return out, total
    if isinstance(node, dict):
        total, out = 0, {}
        for key, value in node.items():
            new, n = rewrite(value, rx, paths)
            out[key] = new
            total += n
        return out, total
    return node, 0


def search(jql: str):
    token = None
    while True:
        params = {"jql": jql, "fields": ",".join(("summary",) + FIELDS), "maxResults": 100}
        if token:
            params["nextPageToken"] = token
        page = request("GET", "/rest/api/3/search/jql?" + urllib.parse.urlencode(params))
        yield from page.get("issues", [])
        token = page.get("nextPageToken")
        if not token or page.get("isLast", True):
            return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--jql", default=DEFAULT_JQL)
    parser.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    args = parser.parse_args()

    rx, paths = build_pattern(json.loads((SPECS_DIR / "epic-mapping.json").read_text()))
    scanned = changed = links = failed = 0
    for issue in search(args.jql):
        scanned += 1
        update, count = {}, 0
        for field in FIELDS:
            value = issue["fields"].get(field)
            if value is None:
                continue
            new, n = rewrite(value, rx, paths)
            if n:
                update[field] = new
                count += n
        if not count:
            continue
        changed += 1
        links += count
        print(f"{issue['key']}: {count} link(s) in {', '.join(update)} — {issue['fields'].get('summary', '')[:70]}")
        if args.apply:
            try:
                request("PUT", f"/rest/api/3/issue/{issue['key']}?notifyUsers=false", {"fields": update})
            except JiraHTTPError as exc:
                failed += 1
                print(f"  FAILED: {exc}", file=sys.stderr)
    mode = "updated" if args.apply else "would update"
    print(f"\nscanned {scanned} issue(s); {mode} {changed} issue(s), {links} link(s); {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
