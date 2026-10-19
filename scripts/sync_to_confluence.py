#!/usr/bin/env python3
"""Sync acp-product-specs markdown files to Confluence pages under T1KACP space.

Creates a hierarchy:
  Root (Agentic Control Plane - Specifications)
  ├── Agent Registry/
  │   ├── D0 Discovery
  │   ├── D1 Requirements
  │   └── D2 Design/
  │       ├── Overview
  │       ├── Sequences
  │       └── ...
  ├── Model Registry/
  │   └── ...
  └── ...

Usage:
    # Sync everything:
    python3 scripts/sync_to_confluence.py --all

    # Sync a single component:
    python3 scripts/sync_to_confluence.py specs/platform/agent-registry/

    # Sync every spec of one type:
    python3 scripts/sync_to_confluence.py specs/onboarding/

    # Sync a single file:
    python3 scripts/sync_to_confluence.py specs/platform/agent-registry/d0-discovery.md

    # Dry run (show what would be created/updated):
    python3 scripts/sync_to_confluence.py --all --dry-run

    # Sync the living capability map + gap escalation process:
    python3 scripts/sync_to_confluence.py --capability-map

Environment variables (from .github/.env):
    CONFLUENCE_BASE_URL=https://sunlife.atlassian.net/wiki
    CONFLUENCE_USER_EMAIL=your.email@sunlife.com
    CONFLUENCE_API_TOKEN=your_token
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
PAGE_MAPPING_FILE = REPO_ROOT / "references" / "confluence-page-mapping.json"
SPECS_DIR = REPO_ROOT / "specs"

# Import local converter (self-contained, no external dependencies)
sys.path.insert(0, str(SCRIPT_DIR))
from md_to_confluence import md_to_confluence_storage  # noqa: E402
from spec_paths import SPEC_TYPES, iter_spec_dirs  # noqa: E402

# ── Constants ──
# The T1KACP space was rebuilt in Sept 2026 (see slf-acp-confluence/handoff). Specs are no
# longer one flat tree: each is filed under the group matching its spec_type, and the old
# "EDAE ACP Product Team - Specifications" root is archived. Publishing into an archived tree
# succeeds silently, so there is no single ROOT_PAGE_ID any more — the parent is derived.
SPACE_KEY = os.environ.get("CONFLUENCE_SPACE_KEY", "T1KACP")

SPEC_TYPE_PARENTS = {
    "onboarding": "113215504421",   # 3. Product & Engineering > Sun Life ACP > Use Case Onboarding
    "platform": "113215766558",     #                                        > Platform
    "integration": "113216258062",  #                                        > Integration
    "governance": "113215864861",   #                                        > Governance
    "pattern": "113217798220",      #                                        > Patterns
}

# A few specs describe something the four build groups do not cover, and belong beside the
# page that owns the subject instead. Checked before spec_type.
COMPONENT_PARENTS = {
    # The journey spec is the intake/assessment/enablement process itself, which the IA already
    # has a home for under Onboarding & Adoption. Filing it under Platform because its
    # spec_type says so would bury a process doc in the build backlog.
    "acp-customer-journey": "113216159787",  # 4. Onboarding & Adoption > Use Case Intake & Prioritization
}

# Living documents sit outside the spec groups, each under the page that owns its subject.
# Keyed by published title rather than source path so a doc can move in the repo without
# silently re-homing the live page.
STANDALONE_PAGE_PARENTS = {
    "ACP Capability Map (Luminate)": "113216356466",  # > ACP Capability Map — At a Glance
    "ACP Capability Map — Future Roadmap": "113216356466",  # > ACP Capability Map — At a Glance
    "ACP Capability Map — At a Glance": "113214456432",  # > Design Process & Decisions
    "ACP Assurance Records": "113214456432",  # > Design Process & Decisions
    "Capability Gap Escalation": "113215602777",  # > Consortium Engagement Model
}


def spec_type_of(component_dir: Path) -> str | None:
    spec_file = component_dir / "spec.yaml"
    if not spec_file.exists():
        return None
    match = re.search(r"^spec_type:\s*(\S+)", spec_file.read_text(), re.M)
    return match.group(1).strip("\"'") if match else None


def component_parent(component_dir: Path) -> str:
    """The Confluence page a component's spec tree hangs off.

    An explicit override wins, otherwise the group matching spec_type. Raises rather than
    falling back: a default here would publish into the archived root, which the API accepts
    without complaint — the page simply never appears in the IA.
    """
    if component_dir.name in COMPONENT_PARENTS:
        return COMPONENT_PARENTS[component_dir.name]
    spec_type = spec_type_of(component_dir)
    if spec_type not in SPEC_TYPE_PARENTS:
        raise SystemExit(
            f"{component_dir.name}: spec_type {spec_type!r} has no Confluence parent. "
            f"Add one to SPEC_TYPE_PARENTS (known: {', '.join(sorted(SPEC_TYPE_PARENTS))})."
        )
    return SPEC_TYPE_PARENTS[spec_type]


DISCLAIMER_TEMPLATE = (
    "<p><em>Synced from {source} · {commit} on <code>{branch}</code> · {timestamp} · "
    "edit in git, not here.</em></p>"
)

# Human-readable component names
COMPONENT_TITLES = {
    "acp-core": "ACP Core",
    # Both of these name the page as it already exists in Confluence rather than as the
    # directory would title-case it. get_or_create_page matches on title, so a mismatch
    # creates a second page and strands the original's history.
    # "Acp Aws Harness Sdk" predates the EACPP-791 rename to acp-harness-sdk; renaming the
    # live page (and its four gate children) would fix the label but is a separate decision.
    "acp-harness-sdk": "Acp Aws Harness Sdk",
    "anthropic-client-acp-integration": "Anthropic Client Products & ACP Integration",
    "slm-pipeline": "SLM Pipeline",
    "agent-registry": "Agent Registry",
    "agentic-cloud-provisioning": "Agentic Cloud Provisioning Platform (CAH)",
    "ai-gateway": "AI Gateway",
    "aws-adapter": "AWS Adapter",
    "deployment-infrastructure": "Deployment Infrastructure",
    "evaluation-strategy": "Evaluation Strategy",
    "governance-integration": "Governance Integration",
    "governance-intake": "Governance Intake & Risk Classification (Sun Life)",
    "inference-economics": "Inference Economics",
    "kubernetes-adapter": "Kubernetes Adapter",
    "management-plane": "Management Plane",
    "mcp-registry": "MCP Registry",
    "mcp-server-patterns": "MCP Server Patterns",
    "model-registry": "Model Registry",
    "observability-monitoring": "Observability & Monitoring",
    "orchestration-backstage": "Orchestration & Backstage",
    # Title-casing the directory would give "Self Service Onboarding" and lose the hyphen,
    # which is the whole term.
    "self-service-onboarding": "Self-Service Onboarding",
    "snowflake-adapter": "Snowflake Adapter",
    "storage-persistence": "Storage & Persistence",
    "ui-advanced-features": "UI Advanced Features",
    "ui-management-console": "UI Management Console",
    "define-operating-model": "Define ACP Operating Model",
    "define-acp-financial-model": "Define ACP Financial Model",
    "acp-orqestra-integration": "ACP & orQEstra Integration",
    "acp-galileo-integration": "ACP & Galileo Integration",
    "feature-build-capability-requests": "Feature Build / Capability Requests",
    "acp-grs-accelerator-axion": "ACP GRS Accelerator for Axion",
    # Never published as of 2026-10-07; the title-cased directory names read badly.
    "acp-omega-integration": "ACP & Omega Integration",
    "acp-ras-dealer-transfer-in-xpress": "RA&S Dealer Transfer-in Xpress",
    "coarchitect-onboarding": "CoArchitect Onboarding",
    "corpit-tprm-usecase": "Corp IT Use Case — TPRM",
}

# Gate labels
GATE_TITLES = {
    "d0-discovery": "D0 \u2014 Discovery",
    "d1-requirements": "D1 \u2014 Requirements",
    "d2-architecture-overview": "Architecture Overview",
    "d2-design": "D2 \u2014 Design",
    "d2-architecture-overview": "Architecture Overview",
    "d3-tasks": "D3 Tasks",
    "pattern": "Design Pattern (SLF)",
}

# Living documents that publish as top-level pages under the root, outside the
# per-component spec hierarchy. These are referenced directly in use-case sessions,
# so they get their own stable pages rather than being buried under a component.
# The summary leads and the two detail views hang off it: a reader arrives at one screen and
# descends either for what exists today (the catalogue) or for what is coming (the roadmap),
# rather than landing in 27 rows of prose.
STANDALONE_DOCS = {
    "docs/capability-map-summary.md": "ACP Capability Map — At a Glance",
    "docs/capability-map.md": "ACP Capability Map (Luminate)",
    "docs/capability-roadmap.md": "ACP Capability Map — Future Roadmap",
    "docs/process/capability-gap-escalation.md": "Capability Gap Escalation",
    "docs/assurance-records.md": "ACP Assurance Records",
}

# SVGs to publish as an interactive draw.io macro instead of a flat <ac:image>. The macro
# renders from the sibling .drawio and is the only embed that honours per-shape links, which
# is how each capability card deep-links to its catalogue row. Opt-in by filename: every
# other .drawio/.svg pair in the repo keeps the plain image embed.
INTERACTIVE_DIAGRAMS = {
    "capability-map.svg",
    "capability-map-summary.svg",
    "mdx-governance-split.svg",
}

# D2 sub-page titles
D2_PAGE_TITLES = {
    "index": "Overview",
    "architecture": "Architecture",
    "sequences": "Sequence Diagrams",
    "api-design": "API Design",
    "data-model": "Data Model",
    "deployment": "Deployment & Operations",
    "lifecycle": "Lifecycle State Machine",
    "acd-design": "ACD & Sandbox Design",
    "discovery": "Agent Discovery",
    "governance-integration": "Governance Integration",
    "components": "Components & Risk Scoring",
    "integration-patterns": "Integration Patterns",
    "network-policy": "Network Policy",
    "kill-switch": "Kill Switch",
    "security": "Security & Access Control",
    "observability": "Observability & Evaluation",
    "testing": "Testing & Traceability",
    "data-governance": "Data Governance",
    "regulatory-compliance": "Regulatory Compliance",
    "cross-region": "Cross-Region",
    "registration": "Registration",
    "hosting": "Hosting Substrates",
    "topology": "Inference Topology",
    "provider-portability": "Provider Portability",
    "attribution": "Cost Attribution",
    "budgets": "Budgets & Enforcement",
    "model-access": "Model Access Governance",
    "identity": "Identity",
    "authorization": "Authorization",
    "api-access": "Reaching a REST API",
    "pipeline": "Build Pipeline",
    "operations": "Operations",
    "assurance": "Assurance \u2014 ETAB & ISRA",
    "segregation-of-duties": "Segregation of Duties",
    "gaps": "Gaps",
}


# ── Env / Git Helpers ──


def get_env(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        print(f"ERROR: {name} not set. Run: set -a && source .github/.env && set +a")
        sys.exit(1)
    return val


def get_git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip() or "unknown"


def get_git_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip() or "unknown"


def get_browse_base() -> str:
    """Bitbucket browse URL for origin, derived from the remote so a rename follows."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    match = re.search(r"(https?://[^/]+)/scm/([^/]+)/(.+?)(?:\.git)?$", result.stdout.strip())
    if not match:
        return ""
    host, project, repo = match.groups()
    return f"{host}/projects/{project}/repos/{repo}"


# ── Confluence API (curl-based, avoids macOS SSL issues) ──


def _curl_auth():
    email = get_env("CONFLUENCE_USER_EMAIL")
    token = get_env("CONFLUENCE_API_TOKEN")
    return f"{email}:{token}"


def api_get(path: str, params: dict | None = None) -> dict:
    base = get_env("CONFLUENCE_BASE_URL")
    url = f"{base}{path}"
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode(params)
    result = subprocess.run(
        ["curl", "-s", "-u", _curl_auth(), url], capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout[:500]}


def api_post(path: str, payload: dict) -> dict:
    base = get_env("CONFLUENCE_BASE_URL")
    url = f"{base}{path}"
    tmp_file = REPO_ROOT / ".tmp" / "confluence_payload.json"
    tmp_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file.write_text(json.dumps(payload))
    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST", "-u", _curl_auth(),
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_file}", url,
        ],
        capture_output=True, text=True,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout[:500]}


def api_put(path: str, payload: dict) -> dict:
    base = get_env("CONFLUENCE_BASE_URL")
    url = f"{base}{path}"
    tmp_file = REPO_ROOT / ".tmp" / "confluence_payload.json"
    tmp_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file.write_text(json.dumps(payload))
    result = subprocess.run(
        [
            "curl", "-s", "-X", "PUT", "-u", _curl_auth(),
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_file}", url,
        ],
        capture_output=True, text=True,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stdout[:500]}


def upload_attachments(page_id: str, md_path: Path) -> None:
    """Upload every local file the page references as an image, so <ac:image> resolves.

    Confluence rejects a create when the filename already exists, so an existing
    attachment is updated through its own /data endpoint instead.
    """
    base = get_env("CONFLUENCE_BASE_URL")
    md_content = md_path.read_text()
    for match in re.finditer(r"!\[.*?\]\((.*?)\)", md_content):
        src = match.group(1)
        if src.startswith(("http://", "https://")):
            continue
        asset = (md_path.parent / src).resolve()
        if not asset.exists():
            print(f"      WARN: image '{src}' not found on disk, skipping upload")
            continue

        # The draw.io macro renders from the source file, so upload that instead of the SVG.
        if asset.name in INTERACTIVE_DIAGRAMS:
            asset = asset.with_suffix(".drawio")
            if not asset.exists():
                print(f"      WARN: {asset.name} missing, cannot publish interactive diagram")
                continue

        name = asset.name
        existing = api_get(
            f"/rest/api/content/{page_id}/child/attachment", {"filename": name}
        ).get("results", [])
        if existing:
            path = f"/rest/api/content/{page_id}/child/attachment/{existing[0]['id']}/data"
        else:
            path = f"/rest/api/content/{page_id}/child/attachment"

        # Observed transient failures on large files; a silent miss is a broken
        # image on a published page, so retry before giving up.
        ok = False
        for attempt in range(3):
            result = subprocess.run(
                [
                    "curl", "-s", "-X", "POST", "-u", _curl_auth(),
                    "-H", "X-Atlassian-Token: nocheck",
                    "-F", f"file=@{asset}",
                    f"{base}{path}",
                ],
                capture_output=True, text=True,
            )
            ok = '"id"' in result.stdout
            if ok:
                break
            time.sleep(2 * (attempt + 1))
        suffix = "" if ok else f" FAILED after 3 attempts: {result.stdout[:160]}"
        print(f"      {'✓' if ok else 'WARN:'} attachment {name}{suffix}")


# ── Page Mapping (persisted JSON) ──


def load_page_mapping() -> dict:
    if PAGE_MAPPING_FILE.exists():
        return json.loads(PAGE_MAPPING_FILE.read_text())
    return {}


def save_page_mapping(mapping: dict) -> None:
    PAGE_MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PAGE_MAPPING_FILE.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n")


# ── Markdown to Confluence Conversion ──


def _to_confluence_anchors(html: str) -> str:
    """Confluence strips raw ``<a id>``/``href="#..."``, which silently kills every
    intra-page link. Swap both for the native anchor macro and ``ac:link``."""
    html = re.sub(
        r'<a id="([^"]+)"\s*></a>',
        lambda m: (
            '<ac:structured-macro ac:name="anchor" ac:schema-version="1">'
            f'<ac:parameter ac:name="">{m.group(1)}</ac:parameter>'
            "</ac:structured-macro>"
        ),
        html,
    )
    return re.sub(
        r'<a href="#([^"]+)">(.*?)</a>',
        lambda m: f'<ac:link ac:anchor="{m.group(1)}"><ac:link-body>{m.group(2)}</ac:link-body></ac:link>',
        html,
        flags=re.DOTALL,
    )


def _mkdocs_slug(heading: str) -> str:
    """The anchor python-markdown generates, so a link written for mkdocs can be matched."""
    s = re.sub(r"[^\w\s-]", "", heading.lower())
    return re.sub(r"\s", "-", s.strip())


def _confluence_anchor(heading: str) -> str:
    """The fragment Confluence generates: heading text, spaces as hyphens, non-ASCII encoded."""
    anchor = re.sub(r"\s+", "-", heading.strip())
    return "".join(c if ord(c) < 128 else urllib.parse.quote(c) for c in anchor)


# Resolved source path -> published title for every page of the component being synced, so a
# link from one gate or D2 page to another resolves to that page rather than a dead `.md` path.
_COMPONENT_PAGES: dict[Path, str] = {}


def _rewrite_doc_links(html: str, mapping: dict, md_path: Path | None = None) -> str:
    """Point relative markdown links at the pages those documents publish as.

    `capability-map.md#4-capability-catalogue` is meaningful to mkdocs and dead in Confluence
    twice over: the path resolves to nothing, and the mkdocs heading slug is not the id
    Confluence generates. Both halves are translated here so the markdown stays portable.
    """
    base = get_env("CONFLUENCE_BASE_URL").rstrip("/")
    pages: dict[str, tuple[str, str, Path]] = {}
    for rel_path, title in STANDALONE_DOCS.items():
        page_id = next(
            (v for k, v in mapping.items() if k.endswith(f"/{title}") and not v.startswith("dry-")),
            None,
        )
        if page_id:
            pages[os.path.basename(rel_path)] = (title, page_id, REPO_ROOT / rel_path)

    def component_entry(target: str) -> tuple[str, str, Path] | None:
        if md_path is None:
            return None
        resolved = (md_path.parent / target).resolve()
        title = _COMPONENT_PAGES.get(resolved)
        page_id = next(
            (v for k, v in mapping.items() if k.endswith(f"/{title}") and not v.startswith("dry-")),
            None,
        )
        return (title, page_id, resolved) if title and page_id else None

    def replace(match: re.Match) -> str:
        target, fragment = match.group(1), match.group(2) or ""
        entry = pages.get(os.path.basename(target)) or component_entry(target)
        if not entry:
            return match.group(0)
        title, page_id, md_path = entry
        slug = re.sub(r"[^A-Za-z0-9]+", "+", title).strip("+")
        url = f"{base}/spaces/{SPACE_KEY}/pages/{page_id}/{slug}"
        if fragment:
            anchor = fragment[1:]
            target_md = md_path.read_text()
            headings = {
                _mkdocs_slug(h): h for h in re.findall(r"^#{2,4}\s+(.+?)\s*$", target_md, re.M)
            }
            if anchor in headings:
                url += f"#{_confluence_anchor(headings[anchor])}"
            else:
                # An explicit <a id> already matches Confluence's own id; anything else is a
                # stale heading slug that would publish as a link to nowhere.
                if f'id="{anchor}"' not in target_md:
                    print(f"      WARN: '{target}#{anchor}' matches no heading or anchor")
                url += f"#{anchor}"
        return f'href="{url}"'

    return re.sub(r'href="([^"#]+\.md)(#[^"]*)?"', replace, html)


def convert_markdown(md_path: Path, mapping: dict | None = None) -> str:
    """Convert markdown to Confluence storage format using local converter."""
    md_content = md_path.read_text()

    # Auto-detect images for attachment mapping
    image_map: dict[str, str] = {}
    for m in re.finditer(r"!\[.*?\]\((.*?)\)", md_content):
        src = m.group(1)
        basename = os.path.basename(src)
        if basename and "." in basename:
            # An interactive diagram points at the .drawio the macro renders, not the SVG.
            if basename in INTERACTIVE_DIAGRAMS:
                basename = f"{Path(basename).stem}.drawio"
            image_map[src] = basename

    html = _to_confluence_anchors(md_to_confluence_storage(md_content, image_map))
    return _rewrite_doc_links(html, mapping, md_path) if mapping else html


# ── Sync Logic ──


def build_disclaimer(md_path: Path | None = None) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    commit = get_git_sha()
    branch = get_git_branch()
    base = get_browse_base()

    if not base:
        return DISCLAIMER_TEMPLATE.format(
            source="git", commit=f"<code>{commit}</code>", branch=branch, timestamp=timestamp
        )

    at = urllib.parse.quote(f"refs/heads/{branch}", safe="")
    repo = base.rsplit("/", 1)[-1]
    label = repo
    path = ""
    if md_path is not None:
        path = md_path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        label = f"{repo}/{path}"
    source = f'<a href="{base}/browse/{path}?at={at}">{label}</a>'
    commit_link = f'<a href="{base}/commits/{commit}"><code>{commit}</code></a>'
    return DISCLAIMER_TEMPLATE.format(
        source=source, commit=commit_link, branch=branch, timestamp=timestamp
    )


def build_toc() -> str:
    """Confluence-native TOC macro; renders from the page's own headings on view."""
    return (
        '<ac:structured-macro ac:name="toc" ac:schema-version="1">'
        '<ac:parameter ac:name="maxLevel">3</ac:parameter>'
        '<ac:parameter ac:name="minLevel">2</ac:parameter>'
        '<ac:parameter ac:name="outline">true</ac:parameter>'
        '<ac:parameter ac:name="style">none</ac:parameter>'
        "</ac:structured-macro>"
    )


def get_or_create_page(title: str, parent_id: str, mapping: dict, dry_run: bool = False) -> str:
    """Get existing page ID or create a new empty parent page. Returns page ID."""
    mapping_key = f"{parent_id}/{title}"
    if mapping_key in mapping:
        # Verify it still exists
        cached_id = mapping[mapping_key]
        if not cached_id.startswith("dry-"):
            return cached_id

    # Search Confluence by title in the space
    search = api_get("/rest/api/content", {"spaceKey": SPACE_KEY, "title": title, "expand": "version"})
    results = search.get("results", [])
    if results:
        page_id = results[0]["id"]
        mapping[mapping_key] = page_id
        return page_id

    if dry_run:
        print(f"    [DRY RUN] Would create parent page: {title}")
        fake_id = f"dry-{abs(hash(title)) % 100000}"
        mapping[mapping_key] = fake_id
        return fake_id

    # Create empty parent page with children macro
    body = (
        '<ac:structured-macro ac:name="children" ac:schema-version="1">'
        '<ac:parameter ac:name="sort">title</ac:parameter>'
        "</ac:structured-macro>"
    )
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    result = api_post("/rest/api/content", payload)
    page_id = result.get("id")
    if not page_id:
        print(f"    ERROR creating parent '{title}': {result.get('message', str(result)[:200])}")
        return ""
    print(f"  \u2713 Created parent: {title} (ID: {page_id})")
    mapping[mapping_key] = page_id
    time.sleep(0.5)
    return page_id


def sync_page(
    md_path: Path, title: str, parent_id: str, mapping: dict, dry_run: bool = False, toc: bool = False
) -> str | None:
    """Sync a single markdown file to Confluence. Returns page ID."""
    if not md_path.exists():
        return None

    body = convert_markdown(md_path, mapping)
    disclaimer = build_disclaimer(md_path)
    storage_body = disclaimer + "\n" + (build_toc() if toc else "") + body

    mapping_key = f"{parent_id}/{title}"

    if dry_run:
        print(f"    [DRY RUN] Would sync: {title} \u2190 {md_path.relative_to(REPO_ROOT)}")
        fake_id = mapping.get(mapping_key, f"dry-{abs(hash(title)) % 100000}")
        mapping[mapping_key] = fake_id
        return fake_id

    # Check if page already exists (by mapping or search)
    existing_id = mapping.get(mapping_key)
    if existing_id and not existing_id.startswith("dry-"):
        page_data = api_get(f"/rest/api/content/{existing_id}", {"expand": "version"})
        if "version" in page_data:
            version = page_data["version"]["number"] + 1
            payload = {
                "id": existing_id,
                "type": "page",
                "title": title,
                "space": {"key": SPACE_KEY},
                "body": {"storage": {"value": storage_body, "representation": "storage"}},
                "version": {"number": version},
            }
            result = api_put(f"/rest/api/content/{existing_id}", payload)
            if result.get("id"):
                print(f"    \u2713 Updated: {title} (v{version})")
                upload_attachments(existing_id, md_path)
                return existing_id
            print(f"    WARN: Update failed for '{title}', will try create")

    # Search by title
    search = api_get("/rest/api/content", {"spaceKey": SPACE_KEY, "title": title, "expand": "version"})
    results = search.get("results", [])
    if results:
        page = results[0]
        page_id = page["id"]
        version = page["version"]["number"] + 1
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "body": {"storage": {"value": storage_body, "representation": "storage"}},
            "version": {"number": version},
        }
        result = api_put(f"/rest/api/content/{page_id}", payload)
        if result.get("id"):
            print(f"    \u2713 Updated: {title} (v{version})")
            mapping[mapping_key] = page_id
            upload_attachments(page_id, md_path)
            return page_id
        print(f"    WARN: Update by search failed for '{title}'")

    # Create new page
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "ancestors": [{"id": parent_id}],
        "body": {"storage": {"value": storage_body, "representation": "storage"}},
    }
    result = api_post("/rest/api/content", payload)
    page_id = result.get("id")
    if page_id:
        print(f"    \u2713 Created: {title} (ID: {page_id})")
        mapping[mapping_key] = page_id
        upload_attachments(page_id, md_path)
        time.sleep(0.5)
        return page_id

    # Fabric editor workaround for complex pages
    err_msg = str(result.get("message", ""))
    if "unsupported extensions" in err_msg.lower() or "fabric" in err_msg.lower():
        minimal_payload = {
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "ancestors": [{"id": parent_id}],
            "body": {"storage": {"value": "<p>Loading...</p>", "representation": "storage"}},
        }
        result = api_post("/rest/api/content", minimal_payload)
        page_id = result.get("id")
        if page_id:
            time.sleep(0.3)
            payload = {
                "id": page_id,
                "type": "page",
                "title": title,
                "space": {"key": SPACE_KEY},
                "body": {"storage": {"value": storage_body, "representation": "storage"}},
                "version": {"number": 2},
            }
            api_put(f"/rest/api/content/{page_id}", payload)
            print(f"    \u2713 Created (2-step): {title} (ID: {page_id})")
            mapping[mapping_key] = page_id
            time.sleep(0.5)
            return page_id

    print(f"    ERROR creating '{title}': {err_msg[:300]}")
    return None


def sync_component(component_dir: Path, mapping: dict, dry_run: bool = False) -> None:
    """Sync all specs for a single component."""
    component_name = component_dir.name
    component_title = COMPONENT_TITLES.get(component_name, component_name.replace("-", " ").title())

    print(f"\n{'=' * 60}")
    print(f"  Component: {component_title} ({component_name})")
    print(f"{'=' * 60}")

    # Create/get component parent page
    component_page_id = get_or_create_page(
        component_title, component_parent(component_dir), mapping, dry_run
    )
    if not component_page_id:
        print(f"  SKIP: Could not create/find parent page for {component_title}")
        return

    # (source, title, parent) in publish order: flat gate files (d0-discovery.md, ...), then
    # the SLF pattern document on a `spec_type: pattern` spec (published beside the gate pages
    # rather than under references/, because it is the artifact the Enterprise Architect and
    # ETAB actually read, and `references/` is never synced), then the D2 pages, index first.
    plan: list[tuple[Path, str, str]] = []
    for gate_file in sorted(component_dir.glob("d*.md")):
        gate_key = gate_file.stem
        gate_title = GATE_TITLES.get(gate_key, gate_key.replace("-", " ").title())
        plan.append((gate_file, f"{component_title} \u2014 {gate_title}", component_page_id))

    pattern_file = component_dir / "pattern.md"
    if pattern_file.exists():
        plan.append(
            (pattern_file, f"{component_title} \u2014 {GATE_TITLES['pattern']}", component_page_id)
        )

    d2_dir = component_dir / "d2-design"
    if d2_dir.is_dir():
        d2_title = f"{component_title} \u2014 D2 Design"
        d2_parent_id = get_or_create_page(d2_title, component_page_id, mapping, dry_run)
        if d2_parent_id:
            index_file = d2_dir / "index.md"
            if index_file.exists():
                plan.append((index_file, f"{d2_title} \u2014 Overview", d2_parent_id))
            for sub_file in sorted(d2_dir.glob("*.md")):
                if sub_file.name == "index.md":
                    continue
                sub_key = sub_file.stem
                sub_title = D2_PAGE_TITLES.get(sub_key, sub_key.replace("-", " ").title())
                plan.append((sub_file, f"{d2_title} \u2014 {sub_title}", d2_parent_id))

    # Resolve every page id before writing any body, as sync_standalone_docs does, so links
    # between this component's pages resolve on the run that first creates a page.
    _COMPONENT_PAGES.clear()
    for md_path, title, parent_id in plan:
        get_or_create_page(title, parent_id, mapping, dry_run)
        _COMPONENT_PAGES[md_path.resolve()] = title

    for md_path, title, parent_id in plan:
        sync_page(md_path, title, parent_id, mapping, dry_run)
        time.sleep(0.3)


def sync_standalone_docs(mapping: dict, dry_run: bool = False) -> None:
    """Sync the living documents that live outside the per-component spec hierarchy."""
    print(f"\n{'=' * 60}")
    print("  Living Documents")
    print(f"{'=' * 60}")

    for title in STANDALONE_DOCS.values():
        if title not in STANDALONE_PAGE_PARENTS:
            raise SystemExit(f"{title!r} has no entry in STANDALONE_PAGE_PARENTS")

    # Resolve every page id before writing any body. These documents link to each other, and
    # _rewrite_doc_links can only translate a link whose target is already in the mapping — so
    # without this pass, the run that first adds a page publishes dead links in its siblings
    # and only a second run repairs them.
    for title, parent_id in (
        (t, STANDALONE_PAGE_PARENTS[t]) for t in STANDALONE_DOCS.values()
    ):
        get_or_create_page(title, parent_id, mapping, dry_run)

    for rel_path, title in STANDALONE_DOCS.items():
        md_path = REPO_ROOT / rel_path
        if not md_path.exists():
            print(f"  SKIP: {rel_path} not found")
            continue
        sync_page(md_path, title, STANDALONE_PAGE_PARENTS[title], mapping, dry_run, toc=True)
        time.sleep(0.3)


# ── Main ──


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mode = sys.argv[1]

    mapping = load_page_mapping()

    if mode == "--capability-map":
        sync_standalone_docs(mapping, dry_run)
        save_page_mapping(mapping)
        return

    if mode == "--all" or (not args and "--all" in sys.argv):
        for comp_dir in iter_spec_dirs(SPECS_DIR):
            sync_component(comp_dir, mapping, dry_run)

        sync_standalone_docs(mapping, dry_run)
        save_page_mapping(mapping)
        print(f"\n{'=' * 60}")
        print(f"  Sync complete! Mapping saved to {PAGE_MAPPING_FILE.relative_to(REPO_ROOT)}")
        print(f"{'=' * 60}")
        return

    # Single component or file
    target = Path(args[0]) if args else Path(mode)
    if not target.exists():
        target = REPO_ROOT / target
    if not target.exists():
        print(f"ERROR: {target} not found")
        sys.exit(1)
    # Normalise to an absolute path so downstream relative_to(REPO_ROOT) works
    # whether the caller passed a relative or absolute path.
    target = target.resolve()

    # A living document is not under specs/, so the component path below would try to
    # derive a spec_type for it and exit. Check it first.
    rel = target.relative_to(REPO_ROOT).as_posix() if target.is_relative_to(REPO_ROOT) else ""
    if rel in STANDALONE_DOCS:
        title = STANDALONE_DOCS[rel]
        parent_id = STANDALONE_PAGE_PARENTS[title]
        get_or_create_page(title, parent_id, mapping, dry_run)
        sync_page(target, title, parent_id, mapping, dry_run, toc=True)
        save_page_mapping(mapping)
        return

    if target.is_dir() and target.parent == SPECS_DIR.resolve() and target.name in SPEC_TYPES:
        for comp_dir in iter_spec_dirs(SPECS_DIR):
            if comp_dir.parent.name == target.name:
                sync_component(comp_dir, mapping, dry_run)
    elif target.is_dir():
        sync_component(target, mapping, dry_run)
    elif target.is_file():
        comp_dir = target.parent
        if comp_dir.name in ("d2-design", "artifacts"):
            comp_dir = comp_dir.parent
        component_name = comp_dir.name
        comp_title = COMPONENT_TITLES.get(component_name, component_name.replace("-", " ").title())
        comp_page_id = get_or_create_page(
            comp_title, component_parent(comp_dir), mapping, dry_run
        )
        if comp_page_id:
            gate_key = target.stem
            gate_title = GATE_TITLES.get(gate_key, gate_key.replace("-", " ").title())
            title = f"{comp_title} \u2014 {gate_title}"
            sync_page(target, title, comp_page_id, mapping, dry_run)

    save_page_mapping(mapping)


if __name__ == "__main__":
    main()
