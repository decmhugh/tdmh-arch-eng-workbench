# Confluence Sync Process

## Overview

Specs are synced to Confluence so non-developer stakeholders (POs, architects, governance)
can review them in a familiar format. **The repo is always the source of truth.**

## Disclaimer Header

Every synced page includes this header at the top:

```html
<ac:structured-macro ac:name="warning">
  <ac:rich-text-body>
    <p><strong>⚠️ Source of Truth: <code>acp-specs</code> repository</strong></p>
    <p>This page is auto-synced from the <code>acp-specs</code> git repository.
    <strong>Do not edit in Confluence.</strong> Changes made here will be overwritten
    on the next sync.</p>
    <p>To propose changes, submit a pull request in the repository.</p>
    <p><em>Last synced: {timestamp} | Commit: {short_sha}</em></p>
  </ac:rich-text-body>
</ac:structured-macro>
```

## Page Structure in Confluence

```
ACP Specs (root page)
├── Process
│   ├── D0→D4 Overview
│   ├── Design Review Guide
│   └── GitOps Workflow
├── acp-core
│   ├── D0: Discovery
│   ├── D1: Requirements
│   ├── D2: Design
│   ├── D3: Tasks
│   └── D4: Verification
├── Agent Registry
│   ├── D0: Discovery
│   └── ...
└── ... (one section per component)
```

## Sync Commands

### Sync a Single Component

```bash
set -a && source .github/.env && set +a
python3 scripts/sync_to_confluence.py specs/platform/agent-registry/
```

### Sync All Components

```bash
python3 scripts/sync_to_confluence.py --all
```

### Sync Process Docs

```bash
python3 scripts/sync_to_confluence.py docs/process/
```

### Sync the Living Documents

The capability map and the gap escalation process publish as top-level pages directly under
the specs root, outside the per-component hierarchy — they are referenced live in use-case
sessions, so they get their own stable pages.

```bash
CONFLUENCE_SPACE_KEY=T1KACP python3 scripts/sync_to_confluence.py --capability-map
```

The space key is set inline because the shared credential file exports `DPEP`, which overrides
the script default and publishes into the wrong space.

This publishes three pages: the capability map, its **At a Glance** summary as a child of the
map, and the gap escalation process. Regenerate the map's diagrams first if the catalogue
changed — `python3 scripts/render_capability_map.py --export`.

Re-run this whenever the capability map is re-verified against a new Luminate release. A
stale map is how a use case gets promised a control that does not exist.

## What Gets Synced

| Source | Confluence Page Title | When |
|--------|----------------------|------|
| `specs/{spec_type}/{component}/d0-discovery.md` | `{Component} — D0: Discovery` | After D0 merge |
| `specs/{spec_type}/{component}/d1-requirements.md` | `{Component} — D1: Requirements` | After D1 merge |
| `specs/{spec_type}/{component}/d2-design.md` | `{Component} — D2: Design` | After D2 merge |
| `specs/{spec_type}/{component}/d3-tasks.md` | `{Component} — D3: Tasks` | After D3 merge |
| `specs/{spec_type}/{component}/d4-verification.md` | `{Component} — D4: Verification` | After D4 merge |

## Mermaid Diagrams

Mermaid code blocks in specs are converted to rendered images during sync using the
Confluence Aura HTML macro approach (same as the `confluence` agent skill).

## Prerequisites

```bash
# Required in .github/.env
CONFLUENCE_BASE_URL=https://sunlife.atlassian.net/wiki
CONFLUENCE_USER_EMAIL=your.email@sunlife.com
CONFLUENCE_API_TOKEN=your_token
CONFLUENCE_SPACE_KEY=EACPP   # or whatever space is allocated
```

## Page Mapping

After first sync, a `references/page-mapping.md` is generated that maps spec files
to Confluence page IDs. This enables idempotent updates (create once, update thereafter).
