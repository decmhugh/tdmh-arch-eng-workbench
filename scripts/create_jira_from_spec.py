#!/usr/bin/env python3
"""Create a Jira Epic + Task ("story") tickets for a spec component, directly via
the Jira REST API (no AgilePlace/Planview Hub dependency).

Reads:
  - specs/board-config.json  — project id/key, issue-type ids, field ids
  - specs/<spec_type>/<component>/spec.yaml  — title, description, existing jira_epic
  - specs/<spec_type>/<component>/d3-tasks.md  — the `**T<n>**` task rows become Tasks

Behaviour:
  - Creates the Epic if spec.yaml.jira_epic is empty (Epic Name = title).
  - Creates one Task per D3 `**T<n>**` row, parented to the Epic.
  - Idempotent: skips the Epic if already set; skips Tasks whose summary already
    exists under the Epic.
  - Backfills spec.yaml.jira_epic and specs/epic-mapping.json.

Auth (Basic) is read from the environment (see .github/.env.example):
  JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN

Usage:
    set -a && source ../Control\\ Plane/.github/.env && set +a   # or this repo's .env
    python3 scripts/create_jira_from_spec.py sunlife-deployment [--dry-run]

Board 28926 ("EACPP Product Team Stories") filters project=EACPP issuetype in
(Task, Sub-task), so created Tasks appear on it automatically — no board edit needed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from jira_http import JiraHTTPError, request  # noqa: E402
from spec_paths import SPECS_DIR, find_spec_dir, spec_rel  # noqa: E402

REPO_ROOT = Path(__file__).parent.parent
BOARD_CONFIG = SPECS_DIR / "board-config.json"
EPIC_MAPPING = SPECS_DIR / "epic-mapping.json"

BITBUCKET_SPEC_BASE = "https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/specs"

LUMINATE_REPO = "https://ai-consortium.ghe.com/AI-Consortium/luminate"
CAPABILITY_MAP = "https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/docs/capability-map.md"

ACCEPTANCE = (
    "h3. Acceptance criteria\n"
    "* Implements the task and its referenced design decision (see D2).\n"
    "* Additive / backward-compatible per D2 NFRs; existing behaviour preserved.\n"
    "* Governance events emitted to {{audit_events}} where applicable.\n"
    "* Unit + integration tests; coverage per repo standard (Consortium \u2265 85% / Sun Life \u2265 90%).\n"
    "* Generic: no Sun Life-specific hardcoding (config/seed only)."
)


def _wiki(text: str) -> str:
    """Convert light markdown (links, code, bold) to Jira v2 wiki markup."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[\1|\2]", text)  # [t](u) -> [t|u]
    text = re.sub(r"`([^`]+)`", r"{{\1}}", text)                  # `x` -> {{x}}
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)              # **x** -> *x*
    return text.strip()


def _norm(text: str) -> str:
    """Whitespace-collapsed form for idempotent description comparison."""
    return re.sub(r"\s+", " ", text or "").strip()


def _iter_tables(d3_path: Path) -> list[tuple[list[str], list[list[str]]]]:
    """Parse every markdown table into (lower-cased header cells, data rows)."""
    tables: list[tuple[list[str], list[list[str]]]] = []
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in d3_path.read_text().splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and all(set(c) <= set("-: ") and c for c in cells):
                continue  # separator row
            if header is None:
                header, rows = [c.lower() for c in cells], []
            else:
                rows.append(cells)
        else:
            if header is not None:
                tables.append((header, rows))
            header, rows = None, []
    if header is not None:
        tables.append((header, rows))
    return tables


def _tid_in(cells: list[str]) -> tuple[int | None, str | None]:
    """Return (index, Tid) of the first cell that is a task id like `T3`/`**T3**`,
    optionally followed by a `<br/>` and its Jira link.

    The trailing-link form matters: once a D3 table is backfilled with keys the id
    cell reads `**T3**<br/>[EACPP-1180](...)`. Requiring an exact match would skip
    it and fall through to the Depends cell, silently retargeting the row at
    another task's ticket.

    The optional letter suffix matters for the same reason. D3 tables insert a task
    between two existing ones as `T6a` rather than renumber every row below it and
    orphan the tickets already carrying those ids. Without the suffix `**T6a**` does
    not match, the scan reaches that row's Depends cell (`T6`), and the row is read
    as T6 -- the retargeting this function exists to prevent.
    """
    for i, c in enumerate(cells):
        m = re.match(r"^\*{0,2}(T\d+[a-z]?)\*{0,2}(?:<br\s*/?>.*)?$", c.strip())
        if m:
            return i, m.group(1)
    return None, None


def _col(header: list[str], *needles: str) -> int | None:
    for i, h in enumerate(header):
        if any(n in h for n in needles):
            return i
    return None


def parse_sequencing(d3_path: Path) -> dict[str, dict[str, str]]:
    """Extract per-task {priority, code, deps} from the D3 'Sequencing, Dependencies
    & Priority' table. Header-aware; returns {} when no such table is present."""
    out: dict[str, dict[str, str]] = {}
    for header, rows in _iter_tables(d3_path):
        hjoin = " ".join(header)
        if "priority" not in hjoin or not ("merge" in hjoin or "code" in hjoin or "luminate" in hjoin):
            continue
        pri = _col(header, "priority")
        code = _col(header, "code", "luminate", "target")
        dep = _col(header, "depend", "cross-epic", "upstream")
        pri = 1 if pri is None else pri
        code = 3 if code is None else code
        dep = 4 if dep is None else dep
        for cells in rows:
            _i, tid = _tid_in(cells)
            if tid is None:
                continue
            out[tid] = {
                "priority": cells[pri] if pri < len(cells) else "",
                "code": _wiki(cells[code]) if code < len(cells) else "",
                "deps": _wiki(cells[dep]) if dep < len(cells) else "",
            }
    return out


def parse_confluence_url(d3_path: Path) -> str:
    m = re.search(r"https://sunlife\.atlassian\.net/wiki/\S*?pages/\d+", d3_path.read_text())
    return m.group(0) if m else ""


def parse_luminate_checks(d3_path: Path) -> dict[str, str]:
    """Extract per-task capability caveats from the D3 task table's optional
    'Luminate support' column.

    A non-empty cell names the capability or gap ids the task leans on that the
    capability map does not record as fully available. Returns {} when the column is
    absent, which is the case for every spec that has not opted in.
    """
    out: dict[str, str] = {}
    for header, rows in _iter_tables(d3_path):
        hjoin = " ".join(header)
        if "priority" in hjoin and ("merge" in hjoin or "code" in hjoin or "luminate" in hjoin):
            continue  # sequencing table, not the task list
        if "task" not in hjoin and "description" not in hjoin:
            continue
        col = _col(header, "luminate")
        if col is None:
            continue
        for cells in rows:
            _i, tid = _tid_in(cells)
            if tid is None or col >= len(cells):
                continue
            raw = cells[col].strip()
            if raw.strip("*_ ") in ("", "\u2014", "\u2013", "-", "n/a", "N/A", "none"):
                continue
            out.setdefault(tid, _wiki(raw))
    return out


def _luminate_warning(flag: str, component: str) -> str:
    """Panel warning that a task depends on a capability the map does not mark available.

    Re-verification is at pick-up time rather than authoring time because the map is a
    point-in-time snapshot: the capability may have shipped since, or the gap may have widened.
    """
    d1 = f"{BITBUCKET_SPEC_BASE}/{spec_rel(component)}/d1-requirements.md"
    return "\n".join([
        "{panel:title=\u26a0\ufe0f Check Luminate support before starting"
        "|borderColor=#ff991f|titleBGColor=#ffe9b3|bgColor=#fffae6}",
        f"This task leans on *{flag}*, which the ACP Capability Map does *not* record as fully "
        "available. Confirm the current position before building anything.",
        "",
        f"* Verify against [AI-Consortium/luminate|{LUMINATE_REPO}] {{{{origin/main}}}} \u2014 *not* "
        f"the [capability map|{CAPABILITY_MAP}], which is a snapshot and goes stale, and *not* a "
        "feature branch: an unmerged prototype is not a capability.",
        "* Separate *modelled* from *enforced*. A field that is only read to be logged is telemetry, "
        "not a control \u2014 find the runtime consumer before calling it available.",
        "* *If it has shipped since:* drop the interim measure and update the capability map.",
        f"* *If it is still missing:* use the interim measure recorded in the D2. Do not invent a "
        f"workaround, and do not present the control as available \u2014 see the gap register in "
        f"[D1 \u00a76|{d1}].",
        "{panel}",
        "",
    ])


def build_task_description(
    component: str,
    tid: str,
    desc: str,
    dep_keys: list[str],
    seq: dict[str, dict[str, str]],
    conf_url: str,
    checks: dict[str, str] | None = None,
) -> str:
    """Compose a rich, pick-up-ready Jira (v2 wiki-markup) description for a D3 task."""
    d2 = f"{BITBUCKET_SPEC_BASE}/{spec_rel(component)}/d2-design.md"
    d3 = f"{BITBUCKET_SPEC_BASE}/{spec_rel(component)}/d3-tasks.md"
    dd = ", ".join(sorted(set(re.findall(r"DD-\d+", desc)))) or "see D2"
    s = seq.get(tid, {})
    flag = (checks or {}).get(tid, "")
    parts = [_luminate_warning(flag, component)] if flag else []
    parts += [_wiki(desc), ""]
    if s.get("priority"):
        parts.append(f"*Priority:* {s['priority']}")
    parts.append(f"*Design decision:* {dd}")
    parts.append("")
    if s.get("code"):
        parts += ["h3. Luminate code targets", s["code"], ""]
    deplines = []
    if dep_keys:
        deplines.append("* Prerequisite stories: " + ", ".join(dep_keys))
    if s.get("deps") and s["deps"] not in ("\u2014", "-", ""):
        deplines.append("* Cross-epic / upstream design: " + s["deps"])
    if deplines:
        parts += ["h3. Dependencies", *deplines, ""]
    if "Done when" not in desc:  # task states its own criteria; the generic block would only add noise
        parts += [ACCEPTANCE, ""]
    refs = ["h3. References", f"* [D2 Design|{d2}]", f"* [D3 Tasks|{d3}]"]
    if conf_url:
        refs.append(f"* [Confluence|{conf_url}]")
    refs.append(f"* Component: {component} (D3 {tid})")
    parts.append("\n".join(refs))
    return "\n".join(parts)


def jira_api(method: str, endpoint: str, payload: dict | None = None, api: str = "2") -> dict | None:
    """Call the Jira REST API, returning None on failure rather than raising.

    Every caller already branches on a falsy result, so failures are reported and
    the run continues instead of aborting halfway through a batch of tickets.
    """
    try:
        return request(method, f"/rest/api/{api}{endpoint}", payload)
    except JiraHTTPError as exc:
        print(f"  ERROR {exc}", file=sys.stderr)
        return None


def parse_tasks(d3_path: Path) -> list[tuple[str, str, list[str], str]]:
    """Extract (Tid, description, [dep Tids], jira_key) from the D3 task table.

    Header-aware: handles the governed `| **T1** | desc | deps |` table and richer
    `| # | Task | ... | Depends On | Jira |` tables alike. Skips the Sequencing
    table (Priority + Merge/code columns) and any non-task tables.
    """
    tasks: list[tuple[str, str, list[str], str]] = []
    seen: set[str] = set()
    for header, rows in _iter_tables(d3_path):
        hjoin = " ".join(header)
        if "priority" in hjoin and ("merge" in hjoin or "code" in hjoin or "luminate" in hjoin):
            continue  # sequencing table, not the task list
        if "task" not in hjoin and "description" not in hjoin:
            continue  # not a task table
        desc_col = _col(header, "description")
        task_col = _col(header, "task")
        dep_col = _col(header, "depend")
        jira_col = _col(header, "jira")
        for cells in rows:
            ti, tid = _tid_in(cells)
            if tid is None or tid in seen:
                continue
            seen.add(tid)
            di = desc_col
            if di is None or di == ti:
                di = task_col if (task_col is not None and task_col != ti) else ((ti + 1) if ti is not None else 1)
            desc = cells[di] if di is not None and di < len(cells) else ""
            desc = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", desc)  # strip md links
            desc = re.sub(r"[`*]", "", desc).strip()
            deps = re.findall(r"T\d+[a-z]?", cells[dep_col]) if dep_col is not None and dep_col < len(cells) else []
            jira_key = ""
            if jira_col is not None and jira_col < len(cells):
                jm = re.search(r"[A-Z][A-Z0-9]+-\d+", cells[jira_col])
                jira_key = jm.group(0) if jm else ""
            tasks.append((tid, desc, deps, jira_key))
    return tasks


def task_summary(tid: str, desc: str) -> str:
    """`T<n>: <lead sentence>` — D3 rows open with a title phrase, so this beats
    truncating the whole description mid-word at the 255-char Jira limit."""
    head = desc.split(". ")[0].rstrip(".")
    if not 12 <= len(head) <= 120:
        head = desc
    return f"{tid}: {head}"[:250]


def existing_children(cfg: dict, epic_key: str) -> dict[str, tuple[str, str, str]]:
    """Return {Tid: (issue_key, summary, description)} for the epic's children,
    keyed by the `T<n>:` prefix so ticket identity is stable across edits."""
    # NOTE: /rest/api/2/search was REMOVED by Atlassian (CHANGE-2046).
    # Use the enhanced POST /rest/api/3/search/jql endpoint.
    payload = {"jql": f"parent = {epic_key}", "fields": ["summary", "description"], "maxResults": 100}
    res = jira_api("POST", "/search/jql", payload, api="3")
    out: dict[str, tuple[str, str, str]] = {}
    for issue in (res or {}).get("issues", []):
        m = re.match(r"(T\d+[a-z]?):", issue["fields"]["summary"])
        if m:
            raw = issue["fields"].get("description")
            cur = raw if isinstance(raw, str) else ""
            out[m.group(1)] = (issue["key"], issue["fields"]["summary"], cur)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: create_jira_from_spec.py <component> [--dry-run]")
        return 2
    component = sys.argv[1]
    dry = "--dry-run" in sys.argv

    cfg = json.loads(BOARD_CONFIG.read_text())
    proj_key = cfg["project"]["key"]
    it_epic = cfg["issue_types"]["epic"]
    it_task = cfg["issue_types"]["task"]
    f_epic_name = cfg["fields"]["epic_name"]

    comp_dir = find_spec_dir(component)
    if comp_dir is None:
        print(f"no spec for {component!r} under specs/<spec_type>/")
        return 2
    spec = yaml.safe_load((comp_dir / "spec.yaml").read_text())
    title = spec["title"]
    epic_key = spec.get("jira_epic") or ""

    # 1) Epic
    if not epic_key:
        summary = title
        desc = spec.get("description", "").strip() or title
        payload = {
            "fields": {
                "project": {"key": proj_key},
                "issuetype": {"id": it_epic},
                "summary": summary,
                f_epic_name: summary,
                "description": f"{desc}\n\nSource of truth: acp-product-specs/specs/{spec_rel(component)}/ (D0-D3).",
                "labels": ["spec-driven", "acp-product-team", f"component-{component}", "consortium-luminate"],
            }
        }
        print(f"Creating Epic: {summary}")
        if dry:
            print("  [dry-run] would POST /issue", json.dumps(payload["fields"], indent=2)[:400])
        else:
            res = jira_api("POST", "/issue", payload)
            if not res or "key" not in res:
                print(f"  FAILED to create epic: {res}")
                return 1
            epic_key = res["key"]
            print(f"  Epic created: {epic_key}")
    else:
        print(f"Epic already set: {epic_key} (skipping create)")

    # 2) Tasks — match by T-id prefix (stable across description edits): create new,
    #    update changed, skip unchanged.
    # D0-only specs (onboarding discovery) carry no task table — the Epic is the deliverable.
    d3_path = comp_dir / "d3-tasks.md"
    has_d3 = d3_path.exists()
    if not has_d3:
        print(f"No d3-tasks.md for {component} — Epic only, no tasks to sync.")
    tasks = parse_tasks(d3_path) if has_d3 else []
    seq = parse_sequencing(d3_path) if has_d3 else {}
    checks = parse_luminate_checks(d3_path) if has_d3 else {}
    conf_url = parse_confluence_url(d3_path) if has_d3 else ""
    print(f"Parsed {len(tasks)} D3 tasks ({len(seq)} with sequencing detail, {len(checks)} flagged for a Luminate support check)")
    existing = {} if dry or not epic_key else existing_children(cfg, epic_key)
    tid_to_key = {tid: existing[tid][0] for tid in existing}
    for tid, _d, _dp, jk in tasks:  # explicit D3 'Jira' column wins (handles non-T summaries)
        if jk:
            tid_to_key[tid] = jk
    created: dict[str, str] = {}
    for tid, desc, deps, jira_key in tasks:
        summary = task_summary(tid, desc)
        dep_keys = [tid_to_key.get(d, d) for d in deps]
        description = build_task_description(component, tid, desc, dep_keys, seq, conf_url, checks)
        target = jira_key or (existing[tid][0] if tid in existing else "")
        if target:
            has_cached = tid in existing and not jira_key
            cur_summary = existing[tid][1] if has_cached else ""
            cur_desc = existing[tid][2] if has_cached else None
            changed = (cur_desc is None) or (_norm(cur_desc) != _norm(description)) or bool(cur_summary and cur_summary != summary)
            if not dry and changed:
                fields: dict = {"description": description}
                if cur_summary.startswith(f"{tid}:"):  # own the T-prefix; don't clobber e.g. 'SLM:'
                    fields["summary"] = summary
                jira_api("PUT", f"/issue/{target}", {"fields": fields})
                print(f"  {tid}: updated ({target})")
            else:
                print(f"  {tid}: exists ({target})")
            continue
        payload = {
            "fields": {
                "project": {"key": proj_key},
                "issuetype": {"id": it_task},
                "summary": summary,
                "description": description,
                "labels": ["spec-driven", "acp-product-team", f"component-{component}"],
            }
        }
        if epic_key:
            payload["fields"]["parent"] = {"key": epic_key}
        if dry:
            print(f"  [dry-run] create {summary}")
            continue
        res = jira_api("POST", "/issue", payload)
        if res and "key" in res:
            created[tid] = res["key"]
            print(f"  {tid} -> {res['key']} (created)")
        else:
            print(f"  {tid} FAILED: {res}")

    # 3) Backfill spec.yaml + epic-mapping.json
    if epic_key and not dry:
        # Only rewrite when the value actually changes: safe_dump reflows block
        # scalars into one escaped line, so a no-op write mangles the spec.
        if spec.get("jira_epic") != epic_key:
            spec["jira_epic"] = epic_key
            (comp_dir / "spec.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
        mapping = json.loads(EPIC_MAPPING.read_text())
        if isinstance(mapping, dict):
            mapping[component] = epic_key
        else:
            for entry in mapping:
                if isinstance(entry, dict) and entry.get("component") == component:
                    entry["jira_key"] = epic_key
        EPIC_MAPPING.write_text(json.dumps(mapping, indent=2) + "\n")
        print(f"Backfilled spec.yaml + epic-mapping.json with {epic_key}")

    # 4) Dependency links (Blocks) from the D3 "Depends" column — idempotent.
    if epic_key and not dry:
        made = create_dependency_links(cfg, epic_key, tasks, created)
        print(f"Dependency links ensured: {made} new Blocks link(s) from D3 Depends column")

    print(f"\nDone. Epic={epic_key}, tasks created={len(created)}")
    return 0


def create_dependency_links(
    cfg: dict, epic_key: str, tasks: list[tuple[str, str, list[str], str]], created: dict[str, str]
) -> int:
    """Create 'Blocks' links so each task's Depends entries block it. Idempotent.

    For a Blocks link, outwardIssue is the blocker and inwardIssue is the blocked.
    When viewing an issue, each link carries only the *other* end, so we normalise
    to a global set of (blocker, blocked) pairs to avoid re-creating existing links.
    """
    tid_to_key = dict(created)
    for tid, _d, _dp, jk in tasks:  # explicit D3 'Jira' column (handles non-T summaries)
        if jk:
            tid_to_key.setdefault(tid, jk)
    payload = {"jql": f"parent = {epic_key}", "fields": ["summary", "issuelinks"], "maxResults": 100}
    res = jira_api("POST", "/search/jql", payload, api="3") or {}
    existing_pairs: set[tuple[str, str]] = set()
    for issue in res.get("issues", []):
        this_key = issue["key"]
        m = re.match(r"(T\d+[a-z]?):", issue["fields"]["summary"])
        if m:
            tid_to_key.setdefault(m.group(1), this_key)
        for link_row in issue["fields"].get("issuelinks", []):
            if link_row.get("type", {}).get("name") != "Blocks":
                continue
            if "outwardIssue" in link_row:  # other end is the blocker; self is blocked
                existing_pairs.add((link_row["outwardIssue"]["key"], this_key))
            elif "inwardIssue" in link_row:  # self is the blocker; other end is blocked
                existing_pairs.add((this_key, link_row["inwardIssue"]["key"]))
    made = 0
    for tid, _desc, deps, _jk in tasks:
        blocked = tid_to_key.get(tid)
        if not blocked:
            continue
        for dep in deps:
            blocker = tid_to_key.get(dep)
            if not blocker or blocker == blocked or (blocker, blocked) in existing_pairs:
                continue
            res = jira_api(
                "POST",
                "/issueLink",
                {"type": {"name": "Blocks"}, "outwardIssue": {"key": blocker}, "inwardIssue": {"key": blocked}},
            )
            if res is None:  # {} is the success shape here — /issueLink returns 201 with no body
                print(f"  WARN link {blocker} blocks {blocked} not created", file=sys.stderr)
                continue
            existing_pairs.add((blocker, blocked))
            made += 1
    return made


if __name__ == "__main__":
    raise SystemExit(main())
