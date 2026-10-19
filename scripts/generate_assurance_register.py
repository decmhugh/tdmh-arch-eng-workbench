#!/usr/bin/env python3
"""Generate docs/assurance-records.md from references/assurance-records.yaml.

Also sweeps the repository for ATG / ISRA / risk identifiers that are not declared,
so a record raised in ServiceNow and mentioned in one spec header cannot stay
invisible to everyone else.

    python3 scripts/generate_assurance_register.py           # rebuild the page
    python3 scripts/generate_assurance_register.py --check    # CI: no-op + sweep
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "references" / "assurance-records.yaml"
OUTPUT = REPO_ROOT / "docs" / "assurance-records.md"
SWEEP_DIRS = ("specs", "docs")

# Identifier shapes. ISRA numbers are bare `26-1904`, which is too loose to sweep on its
# own, so the sweep only accepts one preceded by the word ISRA or sitting in a table cell
# next to it — see _sweep().
ATG = re.compile(r"\bATG\d{6,}\b")
ISRA = re.compile(r"\bISRA[\s_-]*(\d{2}-\d{4})\b|\*\*(\d{2}-\d{4})\*\*|\[\*\*(\d{2}-\d{4})\*\*\]")
GBYD = re.compile(r"\bGBYD\d{6,}\b")
RISK = re.compile(r"\bR0\d{5,}\b")

STATE_LABEL = {
    "approved": "Approved",
    "in-review": "In review",
    "drafting": "Drafting",
    "planned": "Planned",
}
STATE_ORDER = ["approved", "in-review", "drafting", "planned"]


def load() -> dict:
    data = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    for record in data["records"]:
        if record["state"] not in STATE_LABEL:
            sys.exit(f"{record['key']}: unknown state {record['state']!r}")
        if not any(record.get(f) for f in ("atg", "isra", "gbyd")) and record["state"] != "planned":
            sys.exit(f"{record['key']}: carries no record number, so its state must be 'planned'")
        # An unscoped record must at least say how we know it exists, or the register is
        # carrying an anonymous number — worse than not listing it.
        if not record.get("covers") and not record.get("source"):
            sys.exit(f"{record['key']}: has no 'covers', so it must give 'source'")
    return data


def _link(identifier: str | None, url: str | None) -> str:
    if not identifier:
        return "—"
    return f"[{identifier}]({url})" if url else f"`{identifier}`"


def _oneline(text: str | None) -> str:
    return " ".join((text or "").split())


def _anchor(heading: str) -> str:
    """The id python-markdown generates for a heading, so the summary rows link correctly.

    Punctuation is dropped, then runs of whitespace collapse to ONE hyphen — an em dash
    surrounded by spaces yields `-`, not `--`.
    """
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.lower()).strip())


def render(data: dict) -> str:
    records = sorted(
        data["records"], key=lambda r: (STATE_ORDER.index(r["state"]), r["scope"])
    )
    out: list[str] = []
    add = out.append

    add("# ACP Assurance Records\n")
    add(
        "Every architecture-governance (**ATG**), security-risk-assessment (**ISRA**) and\n"
        "GenAI-assessment (**GBYD**) record raised for the Agentic Control Plane, in one place,\n"
        "with the scope each one actually covers.\n"
    )
    add(
        "> **Generated** from `references/assurance-records.yaml` by\n"
        "> `scripts/generate_assurance_register.py`. Do not hand-edit this page \u2014 edit the\n"
        "> YAML and regenerate. CI fails if the two drift, and fails again if it finds an\n"
        "> ATG, ISRA or GBYD identifier anywhere under `specs/` or `docs/` that is not declared.\n"
    )
    add(
        "**ServiceNow is the system of record for whether any of these is approved.**\n"
        "Nothing here queries it. The *State* column is what this repository and Jira can\n"
        "evidence, and every row says where that evidence came from. Treat a state older than\n"
        "a few weeks as a question, not an answer.\n"
    )

    add("## Why this page exists\n")
    add(
        "The numbers were scattered: one spec puts them in `spec.yaml`, another in a pattern\n"
        "header, another in a prose paragraph halfway down a design, and two exist only on\n"
        "unmerged branches. Nothing validated any of it, so the only way to answer *what have we\n"
        "got approved* was to grep. The discrepancies called out below were found by assembling\n"
        "this page, not reported by anything.\n"
    )

    unscoped = [r for r in records if not r.get("covers")]
    if unscoped:
        add("## Needs confirming\n")
        add(
            f"{len(unscoped)} records below carry a number and a programme, but **no recorded\n"
            "assessed scope**. A number without a scope cannot be cited: there is no way to say\n"
            "whether a given change falls inside it or outside it, which is the only question an\n"
            "assurance record answers.\n"
        )
        for record in unscoped:
            ident = record.get("atg") or record.get("isra")
            add(f"- **{ident}** \u2014 {_oneline(record.get('source'))}")
        add("")
        add(
            "ServiceNow holds the scope for each of these and is not reachable from this repository.\n"
            "Someone with access needs to paste in the record title and its assessed scope, after\n"
            "which they become ordinary rows.\n"
        )
        slm = [
            r for r in records
            if r.get("component") == "slm-pipeline" and (r.get("atg") or r.get("isra"))
        ]
        if len(slm) > 2:
            add(
                f"Worth settling at the same time: **{len(slm)} separate records now sit against\n"
                "the one SLM programme**. That may well be correct \u2014 a mirror, a serving tier and a\n"
                "generalized pipeline are different things to assess \u2014 but nothing records what\n"
                "distinguishes them, so nobody can tell which one to cite for a given change.\n"
            )

    outstanding = [(r, a) for r in records for a in r.get("actions") or []]
    if outstanding:
        add("## Outstanding actions\n")
        add("| Record | Action |")
        add("|---|---|")
        for record, action in outstanding:
            ident = record.get("isra") or record.get("atg")
            add(f"| `{ident}` | {_oneline(action)} |")
        add("")

    add("## Summary\n")
    add("| Scope | ATG | ISRA | GenAI | State | Spec | Tracked in |")
    add("|---|---|---|---|---|---|---|")
    for record in records:
        jira = record.get("jira")
        jira_cell = f"[{jira}](https://sunlife.atlassian.net/browse/{jira})" if jira else "—"
        component = f"`{record['component']}`" if record.get("component") else "—"
        if record.get("branch"):
            component += " *(branch)*"
        state = STATE_LABEL[record["state"]]
        if not record.get("covers"):
            state += " *(scope not recorded)*"
        add(
            f"| [{record['scope']}](#{_anchor(record['scope'])}) "
            f"| {_link(record.get('atg'), record.get('atg_url'))} "
            f"| {_link(record.get('isra'), record.get('isra_url'))} "
            f"| {_link(record.get('gbyd'), record.get('gbyd_url'))} "
            f"| {state} "
            f"| {component} "
            f"| {jira_cell} |"
        )

    add("")
    add("**States.** " + " · ".join(
        f"**{STATE_LABEL[k]}** \u2014 {_oneline(v)}" for k, v in data["states"].items()
    ) + "\n")

    add("## Records\n")
    for record in records:
        add(f"### {record['scope']}\n")
        add("| Field | Value |")
        add("|---|---|")
        add(f"| ATG | {_link(record.get('atg'), record.get('atg_url'))} |")
        add(f"| ISRA | {_link(record.get('isra'), record.get('isra_url'))} |")
        add(f"| GenAI assessment | {_link(record.get('gbyd'), record.get('gbyd_url'))} |")
        if record.get("risk"):
            rating = f" ({record['risk_rating']})" if record.get("risk_rating") else ""
            add(f"| Risk | `{record['risk']}`{rating} |")
        add(f"| State | {STATE_LABEL[record['state']]} |")
        if record.get("component"):
            add(f"| Spec | `{record['component']}` |")
        if record.get("branch"):
            add(f"| Branch | `{record['branch']}` \u2014 **not on `main`** |")
        if record.get("jira"):
            add(
                f"| Jira | [{record['jira']}]"
                f"(https://sunlife.atlassian.net/browse/{record['jira']}) |"
            )
        add("")
        add(f"**Covers.** {_oneline(record['covers'])}\n")
        if record.get("note"):
            add(f"{_oneline(record['note'])}\n")
        if record.get("recorded_in"):
            add("Recorded in:\n")
            for path in record["recorded_in"]:
                add(f"- `{path}`")
            add("")

    if data.get("related"):
        add("## Related records\n")
        add(
            "Not assurance submissions, listed so nobody re-derives them from a spec footnote.\n"
        )
        add("| Record | Kind | What | Recorded in |")
        add("|---|---|---|---|")
        for item in data["related"]:
            add(
                f"| `{item['id']}` | {item['kind']} | {_oneline(item['what'])} "
                f"| `{item['recorded_in']}` |"
            )
        add("")
        add(
            "ServiceNow **RITM** provisioning requests are deliberately out of scope. They are\n"
            "requests for infrastructure, not assessments of it; they live in\n"
            "`luminate-sunlife-deploy` alongside the thing they provisioned.\n"
        )

    add("## Adding a record\n")
    add(
        "1. Declare it in `references/assurance-records.yaml`.\n"
        "2. Put `atg_reference`, `atg_url`, `isra_reference`, `isra_url` and, where one exists,\n"
        "   the GenAI assessment, in the spec's `spec.yaml`. `model-inference-patterns` is the\n"
        "   reference shape \u2014 it is the only spec carrying the ServiceNow URLs, which is what\n"
        "   makes a number checkable rather than merely quotable.\n"
        "3. Regenerate: `python3 scripts/generate_assurance_register.py`.\n"
        "4. Commit both the YAML and this page.\n"
    )
    add(
        "A pattern spec additionally carries the pair in its `pattern.md` header and in the\n"
        "`| Record | Identifier |` table at the top of `d2-design/assurance.md`. Those are\n"
        "reader-facing; the YAML is the one CI checks.\n"
    )
    return "\n".join(out).rstrip() + "\n"


def _declared(data: dict) -> set[str]:
    declared: set[str] = set()
    for record in data["records"]:
        for field in ("atg", "isra", "gbyd", "risk"):
            if record.get(field):
                declared.add(str(record[field]))
    for item in data.get("related", []):
        declared.add(item["id"])
    return declared


def _sweep(declared: set[str]) -> list[str]:
    """Every ATG / ISRA / risk id under specs/ and docs/ must be declared."""
    problems: list[str] = []
    for directory in SWEEP_DIRS:
        for path in sorted((REPO_ROOT / directory).rglob("*")):
            if not path.is_file() or path.suffix not in (".md", ".yaml", ".yml"):
                continue
            if path == SOURCE or path == OUTPUT:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            found = set(ATG.findall(text)) | set(GBYD.findall(text)) | set(RISK.findall(text))
            found |= {g for match in ISRA.findall(text) for g in match if g}
            for identifier in sorted(found - declared):
                problems.append(
                    f"{path.relative_to(REPO_ROOT)}: {identifier} is not declared in "
                    f"references/assurance-records.yaml"
                )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify instead of writing")
    args = parser.parse_args()

    data = load()
    rendered = render(data)
    problems = _sweep(_declared(data))

    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            problems.insert(
                0,
                f"{OUTPUT.relative_to(REPO_ROOT)} is stale. Run "
                f"'python3 scripts/generate_assurance_register.py' and commit the result.",
            )
        if problems:
            print("Assurance register check FAILED:")
            for problem in problems:
                print(f"  - {problem}")
            return 1
        print(f"Assurance register OK: {len(data['records'])} record(s), sweep clean.")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(data['records'])} records)")
    for problem in problems:
        print(f"  UNDECLARED: {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
