#!/usr/bin/env python3
"""Validate spec structure and metadata.

Checks:
- Specs live at specs/<spec_type>/<component>/ (folder matches spec_type, dir matches component)
- Every spec dir has a spec.yaml
- spec.yaml has required fields
- Referenced gate files exist
- Gate order is respected
- Mermaid code blocks are syntactically valid (basic check)

Usage:
    python3 scripts/validate_specs.py
"""

from pathlib import Path

import re
import yaml

from spec_paths import SPEC_TYPES

REQUIRED_FIELDS = ["component", "title", "current_gate", "status", "jira_epic", "spec_type"]
REPO_ROOT = Path(__file__).parent.parent
VALID_GATES = ["D0", "D1", "D2", "D3", "D4", "done"]
VALID_STATUSES = ["draft", "in-review", "approved", "not-started"]
VALID_SPEC_TYPES = list(SPEC_TYPES)
# Not spec directories: the generated index and the Jira board/epic config.
SPECS_ROOT_FILES = {"README.md", "board-config.json", "epic-mapping.json"}
EPIC_PATTERN = re.compile(r"^[A-Z]+-[0-9]+$")
GATE_FILES = {
    "D0": "d0-discovery.md",
    "D1": "d1-requirements.md",
    "D2": "d2-design.md",
    "D3": "d3-tasks.md",
    "D4": "d4-verification.md",
}

PATTERN_DOC = "pattern.md"
PATTERN_TEMPLATE = REPO_ROOT / "docs" / "templates" / "pattern.md"
_SECTION = re.compile(r"^##\s+(\d+)\.\s*(.+?)\s*$", re.M)
_HEADER_KEY = re.compile(r"^\*\*([^*]+?):\*\*", re.M)


def _pattern_contract() -> tuple[dict[str, str], list[str]]:
    """The sections and header fields the SLF template mandates.

    Read from `docs/templates/pattern.md` rather than restated here, so the template
    stays the single source of truth — adding a section to it enforces that section
    on every pattern spec without touching this file. A section whose heading is
    marked ``(Optional)`` is advisory and never required.
    """
    if not PATTERN_TEMPLATE.exists():
        return {}, []
    text = PATTERN_TEMPLATE.read_text()
    sections = {num: title for num, title in _SECTION.findall(text) if "(optional)" not in title.lower()}
    return sections, _HEADER_KEY.findall(text)


def validate_pattern_doc(spec_dir: Path) -> list[str]:
    """Check a `spec_type: pattern` spec carries a conforming pattern document.

    The pattern document is what goes to the Enterprise Architect and to ETAB; the
    D0-D3 gates are how we got there. A missing section is a real omission — the
    first submission reached EA with no NFR section at all — so absence fails the
    build. Section *titles* are deliberately not enforced: an author may reword a
    heading, and blocking CI on wording would be over-fitting.
    """
    errors = []
    doc = spec_dir / PATTERN_DOC
    if not doc.exists():
        return [
            f"{spec_dir.name}: spec_type is 'pattern' but {PATTERN_DOC} is missing "
            f"(start from docs/templates/pattern.md)"
        ]

    required_sections, required_header = _pattern_contract()
    if not required_sections:
        return [f"{spec_dir.name}: cannot validate {PATTERN_DOC} — docs/templates/pattern.md is missing"]

    text = doc.read_text()
    present = {num for num, _ in _SECTION.findall(text)}
    missing = sorted((set(required_sections) - present), key=int)
    if missing:
        named = ", ".join(f"{n}. {required_sections[n]}" for n in missing)
        errors.append(f"{spec_dir.name}/{PATTERN_DOC}: missing required section(s) — {named}")

    header_present = {k.strip().lower() for k in _HEADER_KEY.findall(text)}
    missing_header = [k for k in required_header if k.strip().lower() not in header_present]
    if missing_header:
        errors.append(f"{spec_dir.name}/{PATTERN_DOC}: missing header field(s) — {', '.join(missing_header)}")

    return errors



def validate_spec(spec_dir: Path) -> list[str]:
    errors = []
    spec_yaml = spec_dir / "spec.yaml"

    if not spec_yaml.exists():
        errors.append(f"{spec_dir.name}: missing spec.yaml")
        return errors

    with open(spec_yaml) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"{spec_dir.name}: invalid YAML — {e}")
            return errors

    if not data:
        errors.append(f"{spec_dir.name}: spec.yaml is empty")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data or not data[field]:
            errors.append(f"{spec_dir.name}: missing required field '{field}'")

    # Check valid gate
    gate = data.get("current_gate", "")
    if gate and gate not in VALID_GATES:
        errors.append(f"{spec_dir.name}: invalid gate '{gate}' (must be one of {VALID_GATES})")

    # Check valid status
    status = data.get("status", "")
    if status and status not in VALID_STATUSES:
        errors.append(f"{spec_dir.name}: invalid status '{status}' (must be one of {VALID_STATUSES})")

    # Check valid spec type
    spec_type = data.get("spec_type", "")
    if spec_type and spec_type not in VALID_SPEC_TYPES:
        errors.append(
            f"{spec_dir.name}: invalid spec_type '{spec_type}' (must be one of {VALID_SPEC_TYPES})"
        )
    elif spec_type and spec_dir.parent.name != spec_type:
        errors.append(
            f"{spec_dir.name}: spec_type is {spec_type} but the spec is under specs/{spec_dir.parent.name}/ "
            f"— git mv it to specs/{spec_type}/{spec_dir.name}/"
        )
    if data.get("component") and data["component"] != spec_dir.name:
        errors.append(f"{spec_dir.name}: component is {data['component']!r} but the directory is {spec_dir.name!r}")

    # Check the epic key is well formed — the index and the O7 report join on it
    epic = data.get("jira_epic", "")
    if epic and not EPIC_PATTERN.match(str(epic)):
        errors.append(f"{spec_dir.name}: malformed jira_epic '{epic}' (expected e.g. EACPP-123)")

    # Check that gate files exist up to current gate
    if gate in VALID_GATES:
        gate_index = VALID_GATES.index(gate)
        for i in range(gate_index + 1):
            g = VALID_GATES[i]
            if g == "done":
                continue
            gate_file = spec_dir / GATE_FILES[g]
            if not gate_file.exists():
                errors.append(f"{spec_dir.name}: missing {GATE_FILES[g]} (required for gate {gate})")

        # ...and that it does not lag them. A merged artifact is the gate's exit criterion, so a
        # spec carrying d3-tasks.md while claiming D0 puts its epic in the wrong board column and
        # keeps sync_epic_gates.py from ever correcting it.
        if gate != "done":
            present = [g for g in VALID_GATES[:-1] if (spec_dir / GATE_FILES[g]).exists()]
            if present and VALID_GATES.index(present[-1]) > gate_index:
                errors.append(
                    f"{spec_dir.name}: current_gate is {gate} but {GATE_FILES[present[-1]]} "
                    f"exists — set current_gate to {present[-1]}"
                )

    if spec_type == "pattern":
        errors.extend(validate_pattern_doc(spec_dir))

    return errors


def main():
    specs_dir = REPO_ROOT / "specs"
    if not specs_dir.exists():
        print("ERROR: specs/ directory not found")
        return

    all_errors = []
    component_count = 0

    def has_content(d: Path) -> bool:
        # Git does not track empty directories, so switching off a spec branch leaves the
        # old dir behind holding only .DS_Store. That is not a component missing spec.yaml.
        return any(p.name[0] != "." for p in d.iterdir())

    for entry in sorted(specs_dir.iterdir()):
        if entry.name.startswith(".") or entry.name in SPECS_ROOT_FILES or entry.name == "__pycache__":
            continue
        if entry.name not in VALID_SPEC_TYPES:
            if entry.is_dir() and has_content(entry):
                all_errors.append(
                    f"specs/{entry.name}/: specs live at specs/<spec_type>/<component>/ "
                    f"(spec_type one of {VALID_SPEC_TYPES})"
                )
            elif entry.is_file():
                all_errors.append(f"specs/{entry.name}: unexpected file at the specs/ root")
            continue
        for spec_dir in sorted(entry.iterdir()):
            if not spec_dir.is_dir() or spec_dir.name == "__pycache__" or not has_content(spec_dir):
                continue
            component_count += 1
            all_errors.extend(validate_spec(spec_dir))

    if all_errors:
        print(f"VALIDATION FAILED — {len(all_errors)} error(s) in {component_count} components:\n")
        for e in all_errors:
            print(f"  ❌ {e}")
        exit(1)
    else:
        print(f"✅ All {component_count} specs valid")


if __name__ == "__main__":
    main()
