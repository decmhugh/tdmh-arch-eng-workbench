#!/usr/bin/env python3
"""Align each product-team **epic's Jira status** with its spec's ``current_gate``.

The Epic board renders one column per SDD gate (see
``scripts/manage_board_columns.py``), so an epic's status *is* its gate. This
script transitions epics so the board tells the truth.

Gate authority is ``specs/epic-mapping.json`` **on origin/main** -- gate
progression rule 1 says a gate counts once it is merged to ``main``, so a D2 that
only exists on a feature branch must not move the board. Pass ``--worktree`` to
read the checked-out file instead.

Moves are **forward only** by default: an epic already further right than its
spec gate is left alone and reported, because Jira status also carries delivery
signal (an epic can be under construction while its spec sits at D2). Pass
``--allow-backwards`` to force an exact match. Epics in a closed status
(Cancelled / Done) are never touched, and epics with no spec are left alone.

Auth from env (see .github/.env.example): JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN

Usage:
    set -a && source .github/.env && set +a
    python3 scripts/sync_epic_gates.py --dry-run
    python3 scripts/sync_epic_gates.py
    python3 scripts/sync_epic_gates.py --allow-backwards
    python3 scripts/sync_epic_gates.py --worktree --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jira_http import JiraHTTPError, request  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
BOARD_CONFIG = REPO_ROOT / "specs" / "board-config.json"
EPIC_MAPPING = "specs/epic-mapping.json"
GATE_ORDER = ["D0", "D1", "D2", "D3", "D4", "done"]


def load_gates(ref: str | None) -> dict[str, str]:
    """Return {epic key: gate} from epic-mapping.json at ``ref`` (or the worktree)."""
    if ref:
        result = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{ref}:{EPIC_MAPPING}"],
                                capture_output=True, text=True)  # noqa: S603
        if result.returncode != 0:
            print(f"  ERROR git show {ref}:{EPIC_MAPPING}: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        entries = json.loads(result.stdout)
    else:
        entries = json.loads((REPO_ROOT / EPIC_MAPPING).read_text())
    return {e["jira_key"]: e["current_gate"] for e in entries
            if e.get("jira_key") and e.get("current_gate")}


def gate_to_status(cfg: dict) -> dict[str, tuple[str, str]]:
    """Return {gate: (status id, status name)} from the Epic board column mapping."""
    mapping = {}
    for col in cfg["epic_board"]["columns"]["mapped"]:
        for gate in col.get("gates", []):
            mapping[gate] = (col["statuses"][0]["id"], col["statuses"][0]["name"])
    return mapping


def transition_to(key: str, status_id: str) -> str | None:
    for tr in request("GET", f"/rest/api/2/issue/{key}/transitions").get("transitions", []):
        if tr["to"]["id"] == status_id:
            return tr["id"]
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync epic status to its spec's D0-D4 gate.")
    parser.add_argument("--dry-run", action="store_true", help="print the plan, make no changes")
    parser.add_argument("--worktree", action="store_true",
                        help="read the checked-out epic-mapping.json instead of origin/main")
    parser.add_argument("--allow-backwards", action="store_true",
                        help="also move epics that sit ahead of their spec gate")
    parser.add_argument("--ref", default="origin/main", help="git ref holding the gate truth")
    args = parser.parse_args()

    cfg = json.loads(BOARD_CONFIG.read_text())
    label = cfg["product_team_label"]
    gates = load_gates(None if args.worktree else args.ref)
    statuses = gate_to_status(cfg)
    # D4 and 'done' share the Done column, so keep the leftmost gate a status stands for.
    rank: dict[str, int] = {}
    for gate, (sid, _) in statuses.items():
        rank[sid] = min(rank.get(sid, len(GATE_ORDER)), GATE_ORDER.index(gate))

    found = request("POST", "/rest/api/3/search/jql", {
        "jql": f'project = EACPP AND issuetype = Epic AND labels = "{label}" ORDER BY key ASC',
        "fields": ["summary", "status"], "maxResults": 200,
    }).get("issues", [])

    source = "worktree" if args.worktree else args.ref
    print(f"Gate source: {source}  |  epics with the '{label}' label: {len(found)}")

    moves, skipped = [], []
    for issue in found:
        key, status = issue["key"], issue["fields"]["status"]
        gate = gates.get(key)
        if gate is None:
            skipped.append((key, status["name"], "no spec"))
            continue
        if gate not in statuses:
            skipped.append((key, status["name"], f"unknown gate {gate!r}"))
            continue
        target_id, target_name = statuses[gate]
        if status["id"] == target_id:
            continue
        # Done is a gate column (D4), so membership in `rank` does not imply the epic is
        # open — only the status category does. Without this, --allow-backwards drags a
        # finished epic back to D3.
        if status.get("statusCategory", {}).get("key") == "done":
            skipped.append((key, status["name"], "closed — not touched"))
            continue
        if status["id"] not in rank:
            skipped.append((key, status["name"], "status is on no gate column — not touched"))
            continue
        if rank[status["id"]] > rank[target_id] and not args.allow_backwards:
            skipped.append((key, status["name"], f"ahead of spec gate {gate} — left alone"))
            continue
        moves.append((key, status["name"], gate, target_id, target_name))

    print(f"\n{len(moves)} epic(s) to move:")
    for key, current, gate, _, target_name in moves:
        print(f"  {key:<11} {current:<16} -> {target_name:<16} (gate {gate})")
    print(f"\n{len(skipped)} epic(s) untouched:")
    for key, current, why in skipped:
        print(f"  {key:<11} {current:<16} {why}")

    if args.dry_run:
        print("\n[dry-run] no changes made")
        return

    failed = 0
    for key, _, _, target_id, target_name in moves:
        try:
            tid = transition_to(key, target_id)
            if tid is None:
                print(f"  WARN {key}: no transition to {target_name}", file=sys.stderr)
                failed += 1
                continue
            request("POST", f"/rest/api/2/issue/{key}/transitions", {"transition": {"id": tid}})
        except JiraHTTPError as exc:
            print(f"  FAILED {key} -> {target_name}: {exc}", file=sys.stderr)
            failed += 1
            continue
        print(f"  {key} -> {target_name}")

    if failed:
        print(f"\n{failed} of {len(moves)} transition(s) failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except JiraHTTPError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
