# T1K Agent Control Plane — Team Working Agreement

> **Last Updated**: 2026-04-27
> **Jira Project**: [EACPP](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23091)
> **Stories Board**: [EACPP Stories Kanban](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/23490)

---

## Team Agreements

### Communication

- **Order of communication**:
  1. Teams (preferred for async)
  2. Meetings (for discussion/decisions)
  3. Email (external stakeholders only)
- Add comments into Jira tickets when there is a blocker and its resolution
- Inquiries into ticket status should happen in Jira, not Teams
- Planned training and PTO must be communicated and added to the team calendar

### Team Meetings

- Clear agenda for all meetings — stick to allocated time
- No recurring afternoon meetings
- Earliest meetings start at 9:30 AM ET

### Continuous Improvement

- At least one improvement opportunity from every retrospective
- Allocate time for innovating and rapid prototyping
- Identify training needs as part of scrum ceremonies and reflect in team capacity and story sizing
- Create CI tickets in the backlog when improvements are identified

### Documentation

- **Source of truth is in Bitbucket** (acp-specs repo and component repos)
- All documentation in markdown format
- Mermaid diagrams as default, draw.io for complex diagrams (machine-readable diagrams)
- If syncing documentation to Confluence, use the agent skill (auto-sync with disclaimer header)
- Capture learnings from interactions with pre-release and partner teams

### PR Expectations

- All changes must have a pull request — no direct commits to `main`
- As part of your PR, ensure automation flows through the user journey and is tested
- Everyone on the team should review PRs, but only leads can merge
- Make time every day to review PRs
- Squash commits to keep history clean — always rebase, never merge commits

---

## Jira Board — Issue Types

The EACPP project uses the following issue types:

| Type | Description |
|------|-------------|
| **Epic** | High-level component initiative. Each ACP component has one epic (e.g., EACPP-37: Agent Registry Hardening). Epics are created via AgilePlace Hub sync. |
| **Sub-task** | The primary work item. All stories, tasks, and spikes are created as sub-tasks under their parent epic. Sub-tasks should not be estimated independently — the parent epic reflects total effort. |
| **Risk** | Risks identified during planning or execution. Tracked with likelihood/impact and mitigation plan. |

> **Note**: EACPP does not use standalone Story, Task, or Spike issue types. All work
> items are **Sub-tasks** parented to an Epic. Use labels to distinguish work type
> (e.g., `spike`, `enabler`, `bug`).

### Sub-task Conventions

| Work Type | Label | Description |
|-----------|-------|-------------|
| Story | _(no label needed)_ | User-facing functionality with acceptance criteria |
| Task | `task` | Non-story technical work (infra, config, refactoring) |
| Spike | `spike` | Time-boxed research or proof of concept |
| Enabler | `enabler` | Architecture, infrastructure, or compliance work |
| Bug | `bug` | Defect that impairs or prevents expected functionality |

### Required Fields

Every sub-task must have:
- **Summary**: Imperative verb + what + context (e.g., "Implement lifecycle state machine for agent registry")
- **Description**: ADF-formatted with Context, Scope, Technical Approach, Files Affected (see [Jira ADF Formatting Guide](jira-adf-formatting.md))
- **Acceptance Criteria**: ADF taskList with interactive checkboxes in `customfield_10029` (see [Jira ADF Formatting Guide](jira-adf-formatting.md))
- **Epic label**: `epic:{component}` label (e.g., `epic:agent-registry`)
- **Priority**: Urgent, High, Medium, or Low

---

## Story Pointing

We use a modified Fibonacci scale for relative estimation:

| Points | Complexity | Knowledge | Dependencies | Team Definition |
|--------|-----------|-----------|--------------|-----------------|
| **1** | Very low | Everything known | None | Small trivial task, very low complexity |
| **2** | Low | Almost everything known | None | Basically a 1 with some added complexity. Little to no dependencies |
| **3** | Low–Medium | Almost everything known | None | More complex with additional work like testing, code changes, and test cases. Requirements are clearly understood |
| **5** | Medium | Most things known | Minor | More complexity, more unknowns. Less familiar with what needs to change. Could also be familiar but the work is large (e.g., several integrations to test) |
| **8** | Medium–High | Most things known | Some | Complex task requiring significant effort. Can contain cross-team dependencies. Maximum we can realistically do in a sprint. Requirements or technology might not be fully known |
| **13** | High | Almost nothing known | Major | Likely spans more than a sprint. More requirements or a spike needed. Work must be broken down further |

> **Rule**: If a task is 13 points, it **must** be broken down into smaller sub-tasks
> before it enters a sprint.

---

## Definition of Ready

Criteria that a work item must meet before being accepted into a sprint:

- [ ] User story, including acceptance criteria, is defined and clear
- [ ] Story is estimated with story points
- [ ] Story is small enough to be completed within a sprint (no 13-point stories)
- [ ] All known dependencies are identified and logged in Jira
- [ ] All known blockers are resolved
- [ ] All team members have reviewed the story and understand the acceptance criteria
- [ ] Team field has been populated
- [ ] Sub-task is linked to its parent Epic
- [ ] Solution designs reviewed for new features (D2 spec exists)
- [ ] Acceptance criteria use Gherkin format (Given / When / Then)

---

## Definition of Done

Shared understanding of what it means for work to be complete:

- [ ] Code or configuration is committed to Bitbucket
- [ ] Unit tests are automated and provide ≥80% code coverage for the new change
- [ ] Redundant commits are squashed to keep history clean
- [ ] Always rebase, never merge commits
- [ ] (If relevant) Integration tests are automated and passing
- [ ] (If relevant) Functional tests are automated and passing
- [ ] (If relevant) Performance tests are automated and passing
- [ ] All technical and user-facing documentation has been updated or created
- [ ] Flow/sequence/architecture diagrams created:
  - Documentation in Bitbucket in markdown format
  - Mermaid diagrams as default, draw.io for complex diagrams
- [ ] Acceptance criteria met
- [ ] Changes/code have been peer reviewed and approved
- [ ] As part of your PR, ensure automation flows through the user journey and is tested
- [ ] Pre-commit hooks pass (ruff, black, mypy)
- [ ] CI pipeline passes (lint, test, SonarQube, Snyk, Checkmarx)

---

## Team Ceremonies

| Ceremony | Occurrence | Time | Agenda | Attendees |
|----------|-----------|------|--------|-----------|
| **Stand-up** | Daily | 9:45–10:00 AM | What did I do yesterday? What am I doing today? Blockers? | Squad |
| **Retrospective** | End of sprint | Biweekly, 1–2 PM | Explore processes, discuss what worked/didn't, plan improvements | Squad |
| **Sprint Planning** | Start of sprint | Biweekly, 11 AM–12 PM | Review priority tickets, handle carryover, check velocity/capacity, set sprint goals | Squad |
| **Sprint Review** | Start of sprint | Biweekly, 10–11 AM | Demo completed work to stakeholders | All EDAE squads + stakeholders |
| **Backlog Refinement** | Weekly | TBD | Prioritize backlog, add detail, estimate stories | Squad |

---

## Git Conventions (ACP-Specific)

### Branch Naming

| Context | Pattern | Example |
|---------|---------|---------|
| Feature work | `feature/EACPP-{id}` | `feature/EACPP-84` |
| Bug fix | `bugfix/EACPP-{id}` | `bugfix/EACPP-178-fix-pipeline` |
| Spec advancement | `spec/{component}/d{N}` | `spec/agent-registry/d1` |

### Commit Convention

```
{type}({scope}): {description}

Types: feat, fix, chore, refactor, docs, test, perf, ci, spec
Scope: component name (agent-registry, management-plane, etc.)
```

### Rules

- Squash to one commit per PR via interactive rebase
- Never use `--no-verify`
- Jira ticket ID in commit when applicable: `feat(agent-registry): add kill switch [EACPP-84]`

---

## Board Configuration

### Epic Board (Board 28925)

The [EACPP Product Team Epic Board](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/28925) shows the product-team epics (filter: `labels = "acp-product-team"`), one column per [D0→D4 gate](process/d0-d4-overview.md) so the board reads as the SDD pipeline.

**An epic's Jira status *is* its gate.** Jira board columns can only map to statuses, and the EACPP Epic workflow has exactly six, so each gate borrows one:

| Column | Status | Meaning |
|--------|--------|---------|
| Backlog | *(none)* | Kanban backlog, unused |
| D0 · Discovery | Funnel | Problem, scope and capability selection |
| D1 · Requirements | In Analysis | Requirements agreed, gaps registered |
| D2 · Design | Ready for PI | Design agreed, schedulable |
| D3 · Implementation | Implementing | Tasks broken down and created in Jira |
| D4 · Verification | Done | Verified and released |
| Cancelled | Cancelled | Dropped |

> Columns are provisioned by [`scripts/manage_board_columns.py`](../scripts/manage_board_columns.py); the epic statuses behind them are kept in step with each spec's `current_gate` by [`scripts/sync_epic_gates.py`](../scripts/sync_epic_gates.py). Machine-readable config: [`specs/board-config.json`](../specs/board-config.json) (`epic_board.columns`).

Gate truth is `specs/epic-mapping.json` **on `main`** — gate progression rule 1 means a gate only counts once it is merged, so a D2 living on a feature branch must not move the board. `sync_epic_gates.py` moves epics **forward only**: an epic already further right than its spec gate is reported and left alone, because status also carries delivery signal (EACPP-1134 is being implemented while its spec sits at D2).

Real `D0`…`D4` statuses would need a Jira site admin; column renaming needs only board admin, and is reversible.

### Stories Kanban Board (Board 28926)

The [EACPP Product Team Stories](https://sunlife.atlassian.net/jira/software/c/projects/EACPP/boards/28926) board shows Tasks and Sub-tasks carrying the `acp-product-team` label, grouped into swimlanes by epic.

**Swimlane Configuration** (Board Settings → Swimlanes → base on **Queries**).

> Swimlanes are provisioned by [`scripts/manage_swimlanes.py`](../scripts/manage_swimlanes.py) — run it whenever an epic is added, removed, or renamed. Full runbook — how to add, remove, and reorder swimlanes, including the internal `greenhopper` API — lives in Confluence: [EDAE ACP Product Team – Jira Boards & Setup](https://sunlife.atlassian.net/wiki/spaces/T1KACP/pages/113053565824). Machine-readable config: [`specs/board-config.json`](../specs/board-config.json) (`swimlanes`).

Swimlane matching is **top-down, first match wins**, so the lane set is generated rather than hand-listed (it changes with every new epic):

| Order | Swimlane Name | JQL Query |
|-------|---------------|-----------|
| 0 | Expedite | `priority = Urgent` |
| 1…n | `EACPP-XXX · <epic summary>` — one per **open** epic, ascending by key | `parent = EACPP-XXX` |
| last | Everything Else | *(empty query — catchall)* |

Closed epics (Cancelled / Done) get no lane — pass `--include-closed` to keep them.

**Adding a swimlane for a new epic**: label the epic and its tasks `acp-product-team`, then re-run `scripts/manage_swimlanes.py`. Doing it by hand, add a lane named `EACPP-XXX · <short name>` with query `parent = EACPP-XXX` positioned above **Everything Else**; new lanes insert at the top, so reorder by drag (UI) or delete + recreate in reverse order (API) — see the runbook.

**Column Configuration** — delivery flow, unchanged (the D0→D4 gate view lives on the Epic board):

| Column | Statuses |
|--------|----------|
| To Do | Funnel, Ready for PI, In Analysis |
| In Progress | Ready, Integrating/Validating, In Review, Implementing, Complete & Measuring, Implementing: MVP |
| Done | Rejected, Done |
