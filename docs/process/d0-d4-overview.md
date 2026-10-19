# D0→D4 Spec-Driven Development Process

## Overview

Spec-Driven Development (SDD) is a structured process where **specifications are the primary
artifact** — not just scaffolding that gets discarded once coding starts. Specs capture
requirements, design decisions, and implementation plans in a reviewable, versionable,
agent-actionable format.

This process draws from:
- **GitHub spec-kit**: constitution → specify → plan → tasks → implement
- **Amazon Kiro**: requirements → design → tasks (three-phase workflow)
- **Enterprise gate reviews**: D0→D4 maturity model with explicit review checkpoints
- **Design by Contract**: specifications and tests as complementary verification

## The Five Gates

### D0: Discovery

**Purpose**: Align stakeholders on *what* and *why* before investing in detailed requirements.

**Artifact**: `d0-discovery.md`

**Contents**:
- Problem statement (what pain exists today)
- Opportunity (what becomes possible)
- Stakeholders and their concerns
- Scope boundaries (what's in, what's out)
- **Capability requirements** — the mandatory baseline acknowledged, plus the capabilities
  the use case selects from the [ACP Capability Map](../capability-map.md), each with a
  business reason and a priority. Confirmed with the use case in session, never inferred
  from a transcript.
- Success criteria (how we know it's done)
- Dependencies on other components/teams
- Risks and unknowns

**Review**: Tech Lead + Product Owner
- Is the problem clearly stated?
- Is the scope bounded and achievable?
- Are dependencies identified?
- For an onboarding or integration spec: has the use case confirmed its capability
  selection, and has the mandatory baseline been acknowledged?

**Exit Criteria**: PR approved, D0 merged to `main`.

---

### D1: Requirements

**Purpose**: Define *what* the system must do in terms users and developers can verify.

**Artifact**: `d1-requirements.md`

**Contents**:
- User stories with acceptance criteria (Given/When/Then)
- Functional requirements (APIs, behaviors, data flows)
- Non-functional requirements (performance, security, scalability)
- API contract sketches (endpoints, request/response shapes)
- Data model requirements (entities, relationships)
- Edge cases and error scenarios
- Constraints (regulatory, platform, compatibility)
- **Capability gaps** — every capability selected in D0 that is not fully available,
  classified component-change vs integration and escalated per
  [Capability Gap Escalation](capability-gap-escalation.md)
- **Traceability** — every functional requirement traced to a capability ID

**Review**: Engineering team
- Are requirements testable?
- Are acceptance criteria unambiguous?
- Are non-functional requirements quantified?
- Does every requirement trace to a capability, and is every non-available capability in
  the gap register?

**Exit Criteria**: PR approved, D1 merged to `main`.

---

### D2: Design

**Purpose**: Define *how* the system will work — architecture, data models, APIs, and testing strategy.

**Artifact**: `d2-design.md`

**Contents**:
- Architecture overview (mermaid component diagram)
- Sequence diagrams for key flows
- API design (full endpoint specs, request/response schemas)
- Data model (database schemas, entity relationships)
- Error handling strategy
- Security considerations (auth, input validation, secrets)
- Testing strategy (unit, integration, e2e)
- Migration/rollback plan (if modifying existing systems)
- Observability (metrics, logging, alerting)

**Review**: Architecture review (cross-team)
- Does the design satisfy all D1 requirements?
- Are there architectural concerns (coupling, scalability, security)?
- Is the testing strategy sufficient?

**Exit Criteria**: PR approved, D2 merged to `main`.

---

### D3: Implementation Plan

**Purpose**: Break the design into **sprint-ready tasks** with estimates, dependencies, and sequencing.

**Artifact**: `d3-tasks.md`

**Contents**:
- Task breakdown (each task ≤ 3 story points)
- Task dependency graph
- Sprint allocation
- Risk mitigation tasks (spikes, POCs)
- Definition of Done per task
- Jira ticket mapping (ticket IDs after creation)

**Review**: PO + Tech Lead
- Are tasks small enough to complete in a sprint?
- Is the dependency graph acyclic?
- Are there clear acceptance criteria per task?

**Exit Criteria**: PR approved, D3 merged to `main`. Tasks created in Jira.

> **Agent Integration**: The AI agent can generate D3 from D2 automatically,
> then create Jira sub-tasks under the component's epic.

---

### D4: Verification

**Purpose**: Validate that implementation meets the spec. Close the loop.

**Artifact**: `d4-verification.md`

**Contents**:
- Test execution results (pass rates, coverage)
- Performance benchmarks vs. D1 NFRs
- Security review findings and remediations
- API conformance (actual vs. specified)
- Known issues and technical debt logged
- Deployment verification checklist
- Release notes

**Review**: QA + Tech Lead
- Do test results cover all D1 acceptance criteria?
- Are all security findings addressed?
- Is the release checklist complete?

**Exit Criteria**: PR approved, D4 merged to `main`. Component released.

---

## Gate Progression Rules

1. **Sequential**: D(N+1) cannot start until D(N) is merged to `main`
2. **PR-gated**: Each gate advances via a reviewed, approved pull request
3. **Reversible**: If implementation reveals design issues, create a new PR to update D2 before continuing D3
4. **Incremental**: A component can have multiple specs (v1, v2) for iterative enhancement
5. **Skip-ahead forbidden**: No implementing without a merged D2 design (exceptions require Tech Lead override documented in PR)

## Git Workflow

```
main ─────────────────────────────────────────────────
  │                                                   
  ├── spec/agent-registry/d0  (PR → merge)            
  │                                                   
  ├── spec/agent-registry/d1  (PR → merge)            
  │                                                   
  ├── spec/agent-registry/d2  (PR → merge)            
  │                                                   
  ├── spec/agent-registry/d3  (PR → merge)            
  │                                                   
  └── spec/agent-registry/d4  (PR → merge)            
```

**Branch naming**: `spec/{component}/{gate}`
**Commit convention**: `spec({component}): {description}`

Examples:
```
spec(agent-registry): draft D0 discovery
spec(agent-registry): advance to D1 — add requirements and API contracts
spec(acp-core): update D2 design — add event schema versioning
```

## Confluence Sync

Every merged spec gate is synced to Confluence automatically. Each Confluence page
includes a **prominent disclaimer header**:

> ⚠️ **Source of Truth**: This page is auto-synced from `acp-specs` repository.
> **Do not edit in Confluence.** Make changes in the repo and they will be synced here.
> Last synced: {timestamp} | Branch: main | Commit: {short_sha}

## Agent Integration

The spec-driven-planner agent skill can:
1. **Draft D0**: Analyze a component repo's `AGENTS.md` and codebase to generate discovery docs
2. **Draft D1**: Convert epic analysis into structured requirements with acceptance criteria
3. **Draft D2**: Generate architecture and sequence diagrams from codebase analysis
4. **Generate D3**: Break D2 design into sprint-ready tasks automatically
5. **Create Jira tickets**: Push D3 tasks to Jira as sub-tasks under the epic
6. **Sync to Confluence**: Publish all gates to Confluence page tree
