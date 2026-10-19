#!/usr/bin/env python3
"""Check the Future Roadmap's Jira columns against the live consortium tenant.

The roadmap quotes an epic status and a release window for every row, and those move without
anyone editing this repo. Hand-checking forty rows before a Product Board round is how a page
ends up quoting a date that slipped a month ago, so the mechanical half is done here:

    python3 scripts/refresh_roadmap_jira.py            # report drift, exit 1 if any
    python3 scripts/refresh_roadmap_jira.py --write    # rewrite the window cells in place

What it does NOT do is decide which section a row belongs in. Moving a row from the ballot to
"accepted" is a judgement about what the consortium agreed, and reading it off a status
transition would promote work nobody committed to. The script reports the mismatch and stops.

Auth: `ai-consortium.atlassian.net` is a separate tenant but Atlassian tokens are
account-level, so the same JIRA_USER_EMAIL / JIRA_API_TOKEN that reaches sunlife works here.

    set -a && . ~/.config/ai-env/load.sh sunlife && set +a

curl is used rather than urllib for the same reason as `jira_http.py`: Python's SSL on macOS
rejects the corporate CA chain.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROADMAP = REPO_ROOT / "docs" / "capability-roadmap.md"

BASE_URL = os.environ.get("CONSORTIUM_ATLASSIAN_BASE_URL", "https://ai-consortium.atlassian.net")
# Jira Cloud's "start date" is a custom field, and its id is instance-specific. This is the one
# on the consortium tenant; overridable so a rename does not need a code change.
START_FIELD = os.environ.get("CONSORTIUM_JIRA_START_FIELD", "customfield_10015")

ISSUE_RE = re.compile(r"\b(AIC-\d+|ACPDIS-\d+)\b")
# A window cell is either "start → due", "→ due" or the italic no-dates marker.
WINDOW_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})?\s*(?:→\s*(\d{4}-\d{2}-\d{2}))?$")
NO_DATES = "*no dates*"

SECTIONS = {
    "1": "## 1. Proposed ranking",
    "2": "## 2. Work underway",
    "4": "## 4. Accepted, awaiting capacity",
    "5": "## 5. The full ballot",
}
# statusCategory a row's epic must be in for the section it sits in. "new" covers To Do and
# Backlog; "indeterminate" is In Progress / In Review. §1 spans all three by design and §5 is
# ideas rather than epics, so neither is constrained.
EXPECTED_CATEGORY = {"2": {"indeterminate"}, "4": {"new"}}


def _credentials() -> str:
    email = os.environ.get("CONSORTIUM_ATLASSIAN_EMAIL") or os.environ.get("JIRA_USER_EMAIL")
    token = os.environ.get("CONSORTIUM_ATLASSIAN_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        raise SystemExit(
            "No credentials. Run: set -a && . ~/.config/ai-env/load.sh sunlife && set +a"
        )
    return f"{email}:{token}"


def fetch(keys: list[str]) -> dict[str, dict]:
    """One JQL call per 50 keys, rather than one call per row."""
    out: dict[str, dict] = {}
    for i in range(0, len(keys), 50):
        batch = keys[i : i + 50]
        # -w appends the status: curl -s exits 0 on 4xx, so a rejected call would otherwise
        # read as an empty result set and silently report every row as missing.
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [
                "curl", "-sS", "--max-time", "45",
                "-u", _credentials(),
                "-H", "Accept: application/json",
                "-w", "\n%{http_code}",
                "--get", f"{BASE_URL}/rest/api/3/search/jql",
                "--data-urlencode", f"jql=key in ({','.join(batch)})",
                "--data-urlencode", f"fields=summary,status,duedate,{START_FIELD}",
                "--data-urlencode", f"maxResults={len(batch)}",
            ],
            capture_output=True, text=True, check=True,
        )
        body, _, status = result.stdout.rpartition("\n")
        if status.strip() != "200":
            raise SystemExit(f"Jira returned {status.strip()}: {' '.join(body.split())[:300]}")
        for issue in json.loads(body)["issues"]:
            f = issue["fields"]
            out[issue["key"]] = {
                "summary": f["summary"],
                "status": f["status"]["name"],
                "category": f["status"]["statusCategory"]["key"],
                "start": f.get(START_FIELD),
                "due": f.get("duedate"),
            }
    return out


def window(issue: dict) -> str:
    start, due = issue.get("start"), issue.get("due")
    if not start and not due:
        return NO_DATES
    return f"{start} → {due}" if start else f"→ {due}"


def section_of(text: str, offset: int) -> str | None:
    """Which numbered section a character offset falls in.

    Raises on a heading it cannot find rather than skipping it: a renamed section would
    otherwise turn the placement guard off silently, and a checker that has quietly stopped
    checking is worse than one that fails.
    """
    current = None
    for key, heading in SECTIONS.items():
        idx = text.find(heading)
        if idx == -1:
            raise SystemExit(f"roadmap has no heading {heading!r} - update SECTIONS")
        if idx <= offset:
            current = key
    return current


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="rewrite the window cells in place")
    args = ap.parse_args()

    text = ROADMAP.read_text(encoding="utf-8")
    keys = sorted({m.group(1) for m in ISSUE_RE.finditer(text)})
    if not keys:
        raise SystemExit(f"no AIC/ACPDIS keys found in {ROADMAP.relative_to(REPO_ROOT)}")

    live = fetch(keys)
    missing = [k for k in keys if k not in live]
    drift: list[str] = []
    lines = text.splitlines()

    for n, line in enumerate(lines):
        if not line.startswith("| ") or "---" in line:
            continue
        cells = [c.strip() for c in line.split("|")]
        # A markdown link repeats the key in both the text and the href, so dedupe while
        # keeping first-seen order — the first key is the one whose window the row quotes.
        row_keys = list(
            dict.fromkeys(
                k for k in ISSUE_RE.findall(line) if k in live and k.startswith("AIC-")
            )
        )
        if not row_keys:
            continue

        sect = section_of(text, sum(len(x) + 1 for x in lines[:n]))

        # The window cell is the one that parses as a date range or carries the no-dates marker.
        for ci, cell in enumerate(cells):
            if cell != NO_DATES and not WINDOW_RE.match(cell.replace("*", "")):
                continue
            if cell == "" or ci == 0:
                continue
            expected = window(live[row_keys[0]])
            if cell != expected:
                drift.append(f"  L{n + 1} {row_keys[0]}: {cell!r} → {expected!r}")
                cells[ci] = expected
                lines[n] = "|".join(
                    [""] + [f" {c} " for c in cells[1:-1]] + [""]
                ).replace("|  |", "| |")
            break

        if sect in EXPECTED_CATEGORY:
            for key in row_keys:
                if live[key]["category"] not in EXPECTED_CATEGORY[sect]:
                    drift.append(
                        f"  L{n + 1} {key} is {live[key]['status']!r} but sits in section {sect}"
                        " — move it by hand, this script will not"
                    )

    if missing:
        print(f"  {len(missing)} key(s) not found in Jira: {', '.join(missing)}")

    if not drift:
        print(f"  {len(keys)} issues checked — roadmap matches Jira")
        return 1 if missing else 0

    print(f"  {len(drift)} difference(s) against {BASE_URL}:")
    print("\n".join(drift))
    if args.write:
        ROADMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n  rewrote {ROADMAP.relative_to(REPO_ROOT)} — review the diff before committing")
        return 0
    print("\n  re-run with --write to apply the date changes")
    return 1


if __name__ == "__main__":
    sys.exit(main())
