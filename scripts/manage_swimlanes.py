#!/usr/bin/env python3
"""Sync per-epic **swimlanes** on the Stories board via the internal greenhopper API.

The public Jira Cloud REST API (``/rest/api/3``, ``/rest/agile/1.0``) does **not**
expose board swimlanes. The board UI drives them through internal
``/rest/greenhopper/1.0/swimlanes/{boardId}`` endpoints, which work with Basic
auth + the ``X-Atlassian-Token: no-check`` header:

    GET    /rest/greenhopper/1.0/swimlanes/{boardId}                -> list
    POST   /rest/greenhopper/1.0/swimlanes/{boardId}  {name,query,description} -> create
    DELETE /rest/greenhopper/1.0/swimlanes/{boardId}/{swimlaneId}   -> delete

There is **no reorder endpoint**, and new swimlanes are inserted at the **top**.
This script therefore converges the board to the desired order by deleting every
non-default swimlane and recreating them in reverse (so the last-created ends up
on top). Swimlane matching is top-down, first-match-wins.

Desired order (top -> bottom):
    Expedite (priority = Urgent)                 [kept unless --no-expedite]
    <one lane per open epic, ascending by key>   parent = EACPP-XXX
    Everything Else (default, empty query)       [left untouched]

Closed epics (status category ``done`` -- Cancelled / Done) get no lane; pass
``--include-closed`` to keep them.

Reads ``specs/board-config.json`` -> ``stories_board.id`` and
``product_team_label`` (the label whose epics get a lane).

Auth from env (see .github/.env.example): JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN

Usage:
    set -a && source .github/.env && set +a
    python3 scripts/manage_swimlanes.py --dry-run
    python3 scripts/manage_swimlanes.py
    python3 scripts/manage_swimlanes.py --no-expedite     # drop the Expedite lane
    python3 scripts/manage_swimlanes.py --include-closed  # keep lanes for closed epics
    python3 scripts/manage_swimlanes.py --board 29258     # override the board id
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jira_http import JiraHTTPError, request  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
BOARD_CONFIG = REPO_ROOT / "specs" / "board-config.json"
EXPEDITE = ("Expedite", "priority = Urgent", "All issues with the highest priority.")
NAME_CAP = 60


def search_epics(label: str, include_closed: bool = False) -> list[tuple[str, str]]:
    """Return [(key, summary), ...] for epics carrying ``label``, ascending by key."""
    jql = f'project = EACPP AND issuetype = Epic AND labels = "{label}"'
    if not include_closed:
        jql += " AND statusCategory != Done"
    data = request("POST", "/rest/api/3/search/jql",
                   {"jql": jql + " ORDER BY key ASC", "fields": ["summary"], "maxResults": 200})
    return [(i["key"], i["fields"]["summary"]) for i in data.get("issues", [])]


def lane_name(key: str, summary: str) -> str:
    """`KEY · <summary>` trimmed of boilerplate and capped for readability."""
    text = summary.replace("(Consortium Contribution)", "").strip(" —-·")
    text = " ".join(text.split())
    name = f"{key} · {text}"
    return name if len(name) <= NAME_CAP else name[: NAME_CAP - 1].rstrip() + "…"


def list_swimlanes(board: int) -> list[dict]:
    return request("GET", f"/rest/greenhopper/1.0/swimlanes/{board}").get("swimlaneEntries", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync per-epic swimlanes on the Stories board.")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, make no changes")
    parser.add_argument("--no-expedite", action="store_true", help="do not keep an Expedite lane")
    parser.add_argument("--include-closed", action="store_true",
                        help="also give Cancelled/Done epics a lane")
    parser.add_argument("--board", type=int, default=0, help="override the stories board id")
    args = parser.parse_args()

    cfg = json.loads(BOARD_CONFIG.read_text())
    board = args.board or cfg["stories_board"]["id"]
    label = cfg["product_team_label"]

    epics = search_epics(label, include_closed=args.include_closed)
    desired: list[tuple[str, str, str]] = []
    if not args.no_expedite:
        desired.append(EXPEDITE)
    for key, summary in epics:
        desired.append((lane_name(key, summary), f"parent = {key}", f"Swimlane for epic {key}"))

    print(f"Board {board}  label '{label}'  epics={len(epics)}")
    print("Desired swimlanes (top -> bottom):")
    for name, query, _ in desired:
        print(f"  {name:<62}  {query}")
    print(f"  {'Everything Else':<62}  (default, untouched)")

    if args.dry_run:
        print("\n[dry-run] no changes made")
        return

    # There is no reorder endpoint, so the only way to set order is to delete every
    # lane and recreate. Print what is about to be destroyed: if a create then fails,
    # this transcript is the only record of what the board used to look like.
    existing = [s for s in list_swimlanes(board) if not s.get("isDefault")]
    print(f"\nDeleting {len(existing)} lane(s) before recreating:")
    for swimlane in existing:
        print(f"  {swimlane['name']:<62}  {swimlane.get('query') or '(none)'}")
    for swimlane in existing:
        request("DELETE", f"/rest/greenhopper/1.0/swimlanes/{board}/{swimlane['id']}")

    # Recreate in reverse: each create inserts at the top, so reversed input
    # yields the desired top -> bottom order.
    for name, query, desc in reversed(desired):
        request("POST", f"/rest/greenhopper/1.0/swimlanes/{board}",
                {"name": name, "query": query, "description": desc})

    print("\nFinal (top -> bottom):")
    for swimlane in sorted(list_swimlanes(board), key=lambda x: x.get("position", 0)):
        print(f"  {swimlane['name']:<62}  {swimlane.get('query') or '(all remaining)'}")


if __name__ == "__main__":
    try:
        main()
    except JiraHTTPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
