#!/usr/bin/env python3
"""Provision the **D0-D4 gate columns** on the Epic board via the internal greenhopper API.

Jira board columns can only map to *statuses* -- there is no arbitrary-column
mechanism -- and the EACPP **Epic** workflow has exactly six statuses. So the gate
view is built by naming each column after a gate and mapping the one status that
stands for it:

    D0 · Discovery       <- Funnel          (10043)
    D1 · Requirements    <- In Analysis     (10163)
    D2 · Design          <- Ready for PI    (12128)
    D3 · Implementation  <- Implementing    (10576)
    D4 · Verification    <- Done            (10002)
    Cancelled            <- Cancelled       (10055)

An epic's Jira status therefore **is** its SDD gate; ``scripts/sync_epic_gates.py``
keeps it aligned with ``specs/epic-mapping.json``. Real ``D0``..``D4`` statuses
would need a Jira site admin -- this needs only board admin.

The column layout is not exposed by the public REST API (``/rest/api/3``,
``/rest/agile/1.0`` are read-only here). The board UI drives it through:

    GET /rest/greenhopper/1.0/rapidviewconfig/editmodel.json?rapidViewId={id}
    PUT /rest/greenhopper/1.0/rapidviewconfig/columns  {rapidViewId, mappedColumns, ...}

Columns come from ``specs/board-config.json`` -> ``epic_board.columns.mapped``.
A status left out of every column disappears from the board, so the script
refuses to write a layout that drops one.

Auth from env (see .github/.env.example): JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN

Usage:
    set -a && source .github/.env && set +a
    python3 scripts/manage_board_columns.py --dry-run
    python3 scripts/manage_board_columns.py
    python3 scripts/manage_board_columns.py --board 29257    # override the board id
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


def edit_model(board: int) -> dict:
    return request("GET", f"/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?rapidViewId={board}")


def workflow_status_ids(model: dict) -> set[str]:
    """Every status the board can currently show, mapped or not."""
    config = model.get("rapidListConfig", {})
    ids = {s["id"] for col in config.get("mappedColumns", []) for s in col.get("mappedStatuses", [])}
    return ids | {s["id"] for s in config.get("unmappedStatuses", [])}


def mapped_status_names(model: dict) -> dict[str, str]:
    """{id: name} for statuses currently visible in a column."""
    return {s["id"]: s["name"]
            for col in model["rapidListConfig"]["mappedColumns"]
            for s in col.get("mappedStatuses", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision D0-D4 gate columns on the Epic board.")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, make no changes")
    parser.add_argument("--board", type=int, default=0, help="override the epic board id")
    args = parser.parse_args()

    cfg = json.loads(BOARD_CONFIG.read_text())
    board = args.board or cfg["epic_board"]["id"]
    desired = cfg["epic_board"]["columns"]["mapped"]

    model = edit_model(board)
    if not model.get("rapidListConfig", {}).get("canEdit"):
        print(f"ERROR: no permission to edit columns on board {board}", file=sys.stderr)
        sys.exit(1)

    available = workflow_status_ids(model)
    visible_now = mapped_status_names(model)
    wanted = {s["id"] for col in desired for s in col["statuses"]}
    # Only a status that is on the board today can vanish from it. An already-unmapped
    # status is invisible either way, and treating it as a loss blocks every write.
    if dropped := set(visible_now) - wanted:
        print("ERROR: these statuses would be left unmapped and vanish from the board: "
              + ", ".join(sorted(visible_now[i] for i in dropped)), file=sys.stderr)
        sys.exit(1)
    if unknown := wanted - available:
        print(f"ERROR: statuses not in this board's workflow: {sorted(unknown)}", file=sys.stderr)
        sys.exit(1)

    print(f"Board {board}  '{model.get('name')}'")
    print("Current columns (left -> right):")
    for col in model["rapidListConfig"]["mappedColumns"]:
        statuses = ", ".join(s["name"] for s in col["mappedStatuses"]) or "(none)"
        print(f"  {col['name']:<22}  {statuses}")
    print("Desired columns (left -> right):")
    for col in desired:
        statuses = ", ".join(s["name"] for s in col["statuses"]) or "(none)"
        gates = f"  [{', '.join(col.get('gates', []))}]" if col.get("gates") else ""
        print(f"  {col['name']:<22}  {statuses}{gates}")

    if args.dry_run:
        print("\n[dry-run] no changes made")
        return

    request("PUT", "/rest/greenhopper/1.0/rapidviewconfig/columns", {
        "rapidViewId": board,
        "currentStatisticsField": {
            "id": (model["rapidListConfig"].get("currentStatisticsField") or {}).get("id", "none_"),
        },
        "mappedColumns": [
            {
                "name": col["name"],
                "mappedStatuses": [{"id": s["id"]} for s in col["statuses"]],
                "min": "",
                "max": "",
                "isKanPlanColumn": col.get("kanplan", False),
            }
            for col in desired
        ],
    })

    print("\nFinal (left -> right):")
    for col in request("GET", f"/rest/agile/1.0/board/{board}/configuration") \
            .get("columnConfig", {}).get("columns", []):
        statuses = ", ".join(s["id"] for s in col.get("statuses", [])) or "(none)"
        print(f"  {col['name']:<22}  {statuses}")


if __name__ == "__main__":
    try:
        main()
    except JiraHTTPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
