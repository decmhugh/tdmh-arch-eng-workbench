# ACP Specs — Spec-Driven Development

> **Sun Life fork (EDAEACP).** This is a fork of `T1KACP/acp-specs` scoped to a
> **single component — `sunlife-deployment`** — capturing the Sun Life Product Team
> work breakdown (D0–D3) for deploying the consortium **Luminate** platform into the
> Sun Life environment. The full ACP spec set lives in the upstream repo.

> Component-level specifications for the Enterprise Agentic Control Plane (ACP).

## What Is This?

This repository contains **markdown specifications** for every ACP component, organized
in a **D0→D4 maturity gate** model. Specs are the source of truth for design decisions,
requirements, and implementation plans — reviewed via pull requests, synced to Confluence
for broader visibility, and used by AI agents to generate sprint-ready Jira tickets.

**Jira Boards**:
- [Spec-Driven Epic Board](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23827) — 18 component epics aligned to D0→D4 gates
- [Spec-Driven Stories Board](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23828) — Sub-tasks/stories by epic
- [MVP Epic Board](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23091) — Original MVP delivery epics (archived)
- [MVP Stories Kanban](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23490) — Original MVP stories (archived)

## D0→D4 Maturity Gates

| Gate | Name | Purpose | Artifact | Review |
|------|------|---------|----------|--------|
| **D0** | Discovery | Problem statement, opportunity, stakeholders | `d0-discovery.md` | Tech Lead + PO |
| **D1** | Requirements | User stories, acceptance criteria, API contracts | `d1-requirements.md` | Team review |
| **D2** | Design | Architecture, sequence diagrams, data models, testing strategy | `d2-design.md` | Architecture review |
| **D3** | Implementation Plan | Sprint-ready tasks, dependencies, estimates | `d3-tasks.md` | PO + Tech Lead |
| **D4** | Verification | Test results, performance, security review, release checklist | `d4-verification.md` | Release approval |

Each spec progresses through gates via **pull requests** — a spec at D1 means D0 has
been reviewed and merged, and D1 is in review or approved.

## Quick Start

1. **Browse specs**: See [specs/README.md](specs/README.md) for the full index
2. **Create a new spec**: Copy from `docs/templates/`, fill in D0, open a PR
3. **Review a spec**: Comment on the PR, approve to advance to next gate
4. **Generate tasks**: Use the agent skill to convert D2→D3 automatically
5. **Sync to Confluence**: Run the sync script to publish specs for stakeholder review

## Repository Structure

```
acp-product-specs/
├── docs/
│   ├── AGENTS.md                   # Rules for the living documents in this directory
│   ├── capability-map-summary.md   # At a Glance — the one-page entry point
│   ├── capability-map.md           # THE living ACP capability map (Luminate-only)
│   ├── capability-roadmap.md       # Future Roadmap — underway, accepted, and on the ballot
│   ├── process/                    # D0→D4 process documentation
│   │   ├── d0-d4-overview.md       # Full process guide
│   │   ├── capability-gap-escalation.md  # Gap → consortium backlog process
│   │   ├── design-review-guide.md  # How to conduct design reviews
│   │   ├── gitops-workflow.md      # PR-based spec progression
│   │   └── confluence-sync.md      # Confluence sync process
│   ├── reference/                  # OSFI / NIST regulatory source material
│   └── templates/                  # Spec templates (copy for new specs)
│       ├── d0-discovery.md
│       ├── d1-requirements.md
│       ├── d2-design.md
│       ├── d3-tasks.md
│       ├── d4-verification.md
│       └── spec.yaml
├── specs/                          # Component specifications, grouped by spec_type
│   ├── README.md                   # Spec index with status dashboard (generated)
│   ├── epic-mapping.json           # Spec ↔ Jira epic join (generated)
│   ├── board-config.json           # Jira board/project config
│   ├── onboarding/                 # One folder per spec_type:
│   ├── integration/                #   onboarding | integration | platform
│   ├── platform/                   #   | pattern | governance
│   ├── pattern/
│   └── governance/
│       └── governance-intake/      # One directory per component
│           ├── spec.yaml           # Metadata (spec_type, owner, epic, links)
│           ├── d0-discovery.md
│           ├── d1-requirements.md
│           ├── d2-design.md
│           ├── d3-tasks.md
│           └── d4-verification.md
├── scripts/                        # Automation
│   ├── spec_paths.py               # Where specs live — every script resolves paths here
│   ├── sync_to_confluence.py       # Publish specs to Confluence
│   ├── render_capability_map.py    # Regenerate both capability-map diagrams
│   ├── refresh_roadmap_jira.py     # Refresh the roadmap's dates from consortium Jira
│   ├── generate_spec_index.py      # Regenerate specs/README.md
│   └── validate_specs.py           # Validate spec structure and metadata
└── .github/                        # Copilot customization + agent skills
    ├── copilot-instructions.md
    ├── skills/
    │   ├── spec-driven-planner/    # Agent skill for spec workflows
    │   └── capability-map-refresh/ # Agent skill for refreshing the map
    └── prompts/                    # Slash commands
```

## Spec Lifecycle

```
┌──────────┐    PR     ┌──────────┐    PR     ┌──────────┐    PR     ┌──────────┐    PR     ┌──────────┐
│    D0    │ ────────> │    D1    │ ────────> │    D2    │ ────────> │    D3    │ ────────> │    D4    │
│Discovery │  Review   │  Reqs    │  Review   │  Design  │  Review   │  Tasks   │  Review   │  Verify  │
└──────────┘           └──────────┘           └──────────┘           └──────────┘           └──────────┘
     │                      │                      │                      │                      │
     ▼                      ▼                      ▼                      ▼                      ▼
  Stakeholder           Team                 Architecture            PO + TL               Release
  Alignment             Review               Review                 Approval               Approval
```

## Integration Points

| System | Integration | Direction |
|--------|-------------|-----------|
| **Jira** | Epics link to specs via `spec.yaml`; D3 tasks become Jira sub-tasks | Specs → Jira |
| **AgilePlace** | Feature cards link to epic specs | Specs → AgilePlace |
| **Confluence** | Specs synced as pages under a parent page tree | Specs → Confluence |
| **Bitbucket** | PRs gate spec progression; spec branch per component | Specs ← Bitbucket |
| **AI Agent** | Agent reads specs to generate tasks, tickets, and plans | Specs ↔ Agent |
| **Consortium** | Capability gaps escalate to the Luminate backlog as ideas | Specs → Consortium |

## Capability Map

Three documents, published to Confluence as one page tree.
[**At a Glance**](docs/capability-map-summary.md) is the entry point and the parent; the two
detail views hang off it.

| Document | Answers | Verified against |
|---|---|---|
| [`docs/capability-map.md`](docs/capability-map.md) | *What can ACP do for my use case **today**?* | Built code on `AI-Consortium/luminate` `origin/main` |
| [`docs/capability-roadmap.md`](docs/capability-roadmap.md) | *What is **coming**, when, and what can I vote for?* | `luminate-designs`, and the `AIC` / `ACPDIS` projects on the consortium Jira tenant |

The catalogue marks each capability available / partial / modelled-not-enforced / designed /
gap, and **mandatory**, conditional or optional. It is **Luminate only**, and it is the menu
walked through in use-case discovery: D0 records what a use case selects; D1 traces
requirements to capability IDs and registers the gaps. Anything a use case needs that Luminate
does not deliver routes through
[Capability Gap Escalation](docs/process/capability-gap-escalation.md) — a change to Luminate
itself becomes a consortium idea, while making ACP reach a Sun Life system is integration and
the harness absorbs it.

The roadmap separates work underway from work accepted-and-waiting from the ballot a Product
Board representative ranks, and names the Sun Life asks that have no consortium track at all.

Both diagrams are generated from the catalogue's own tables, and the roadmap's dates come from
live consortium Jira:

```bash
python3 scripts/render_capability_map.py --export
python3 scripts/refresh_roadmap_jira.py --write
CONFLUENCE_SPACE_KEY=T1KACP python3 scripts/sync_to_confluence.py --capability-map
```

The space key is set inline because the shared credential file exports `DPEP`.

To refresh any of the three, run `/capability-map-refresh` or read
[`.github/skills/capability-map-refresh/SKILL.md`](.github/skills/capability-map-refresh/SKILL.md).

## Credentials

```bash
set -a && source .github/.env && set +a
# Required: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN
# Optional: CONFLUENCE_BASE_URL, CONFLUENCE_USER_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY
# Optional: AGILEPLACE_BASE_URL, AGILEPLACE_API_TOKEN, AGILEPLACE_BOARD_ID
```

## Related

- [Control Plane AGENTS.md](https://bitbucket.sunlifecorp.com/projects/T1KACP/repos/agent-control-plane/browse/WORKSPACE_AGENTS.md) — workspace-level context for all ACP repos
- [agent-skill-qip-planner](https://bitbucket.sunlifecorp.com/users/go84/repos/agent-skill-qip-planner/browse) — QIP planning skill (predecessor)
- [GitHub spec-kit](https://github.com/github/spec-kit) — inspiration for spec-driven workflows
- [Kiro specs](https://kiro.dev/docs/specs/) — requirements → design → tasks model
