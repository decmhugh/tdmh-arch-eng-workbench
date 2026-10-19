"""Where spec directories live: specs/<spec_type>/<component>/.

Every script that walks or addresses specs goes through here, so the layout is defined once.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "specs"

# Each spec_type is a folder under specs/; a spec must sit in the folder matching its spec_type.
SPEC_TYPES = ("onboarding", "integration", "platform", "governance", "pattern")


def iter_spec_dirs(specs_dir: Path = SPECS_DIR) -> Iterator[Path]:
    """Yield every spec directory (one containing spec.yaml), sorted by component name."""
    dirs = [d for t in SPEC_TYPES for d in (specs_dir / t).glob("*/") if (d / "spec.yaml").exists()]
    yield from sorted(dirs, key=lambda d: d.name)


def find_spec_dir(component: str, specs_dir: Path = SPECS_DIR) -> Path | None:
    """The directory of `component`, or None if no spec of that name exists."""
    for t in SPEC_TYPES:
        candidate = specs_dir / t / component
        if (candidate / "spec.yaml").exists():
            return candidate
    return None


def spec_type_of(spec_dir: Path) -> str | None:
    """The spec_type declared in a spec directory's spec.yaml."""
    spec_file = spec_dir / "spec.yaml"
    if not spec_file.exists():
        return None
    match = re.search(r"^spec_type:\s*(\S+)", spec_file.read_text(), re.M)
    return match.group(1).strip("\"'") if match else None


def spec_rel(component: str, specs_dir: Path = SPECS_DIR) -> str:
    """`<spec_type>/<component>` — the component's path relative to specs/."""
    spec_dir = find_spec_dir(component, specs_dir)
    if spec_dir is None:
        raise SystemExit(f"no spec directory for component {component!r} under specs/<spec_type>/")
    return f"{spec_dir.parent.name}/{component}"
