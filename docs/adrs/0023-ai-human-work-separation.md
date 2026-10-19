---
parent: Decisions
nav_order: 23
title: ADR-0023 AI vs Human Work Separation
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0023: AI vs Human Work Separation

## Status

**Draft**

## Context and Problem Statement

As AI agents become integral to development workflows, we need to consider:
- Should AI-generated work have separate tracking from human work?
- How do we maintain visibility into what AI is doing vs humans?
- How do we audit AI contributions vs human contributions?
- Should AI work have different review/approval gates?

**Key question**: Do we need separate Jira boards/projects for AI vs human work, or a different approach entirely?

## Decision Drivers

* AI agents can create many small tasks (ticket explosion)
* Humans need visibility without noise
* Audit trail for AI-generated changes
* Different review criteria for AI vs human work
* Team velocity metrics accuracy
* Compliance and governance requirements

## Options

### Option A: Single Board with Labels/Components

**One board, differentiate with metadata.**

```
EACPP Board
├── EACPP-100: [human] Design AI Gateway API
├── EACPP-101: [ai-generated] Implement rate limiting
├── EACPP-102: [ai-generated] Add unit tests
└── EACPP-103: [human] Review AI implementations
```

**Implementation:**
- Add `contributor-type` label: `human`, `ai-assisted`, `ai-generated`
- Use Jira components for filtering
- Create saved filters for "Human Only" view
- Use automation rules to tag AI-created tickets

**Pros:**
- Single source of truth
- Context preserved (AI work linked to human stories)
- Simple setup
- Standard Jira usage

**Cons:**
- Board can get noisy
- Velocity metrics mix AI and human work
- Harder to see "human-only" progress at a glance

---

### Option B: Separate Boards, Same Project

**One project, two boards with different filters.**

```
EACPP Project
├── Human Board (filter: contributor-type != ai-generated)
│   ├── EACPP-100: Design AI Gateway API
│   └── EACPP-103: Review AI implementations
│
└── AI Work Board (filter: contributor-type = ai-generated)
    ├── EACPP-101: Implement rate limiting
    └── EACPP-102: Add unit tests
```

**Implementation:**
- Keep single EACPP project
- Create board for human work (filtered)
- Create board for AI work (filtered)
- Issues still linked, just viewed separately

**Pros:**
- Clean human view by default
- AI work visible when needed
- Same project = linked context
- Separate velocity tracking possible

**Cons:**
- Two boards to maintain
- Risk of AI board becoming dumping ground
- Need discipline to check both

---

### Option C: Separate Projects

**Distinct projects for human vs AI work.**

```
EACPP (Human Work)
├── EACPP-100: Design AI Gateway API
└── EACPP-103: Review AI implementations

EACPP-AI (AI Work)
├── EACPPAI-1: Implement rate limiting
└── EACPPAI-2: Add unit tests
```

**Implementation:**
- EACPP = human-driven work
- EACPP-AI = AI-generated tasks
- Cross-project links between them
- Different workflows per project

**Pros:**
- Complete separation
- Different workflows (AI work may need less ceremony)
- Clean metrics per "team"
- Audit trail very clear

**Cons:**
- Context fragmentation
- Cross-project linking overhead
- May feel like "second class" work
- Harder to see full picture

---

### Option D: AI Work as Subtasks Only

**AI never creates top-level issues. Always subtasks under human work.**

```
EACPP-100: Design AI Gateway API (human)
├── EACPP-100-1: [AI] Implement rate limiting
├── EACPP-100-2: [AI] Add unit tests
└── EACPP-100-3: [AI] Generate documentation
```

**Implementation:**
- AI can only create subtasks
- Human owns the parent story
- AI work rolls up to human story
- Human responsible for review/merge

**Pros:**
- AI work always has human context
- Clear accountability
- No ticket explosion at board level
- Human always "owns" the work

**Cons:**
- AI can't identify new work (only execute)
- Subtask limits in Jira
- May not fit all AI use cases
- AI agents need human to create parent first

---

### Option E: AI Agent Has Own "User" + Activity Log

**AI treated like team member with activity tracking.**

```
EACPP Board (normal)
├── EACPP-100: Design AI Gateway API
│   Assignee: Human Developer
│   AI Activity: 3 commits, 45 lines added
│
└── EACPP-101: Implement rate limiting
    Assignee: AI-Agent-01 (review: Human Developer)
    AI Activity: Full implementation
```

**Implementation:**
- AI agent has Jira user account
- All AI work assigned to AI user
- Human "reviewer" field required
- Activity log shows AI contributions per issue

**Pros:**
- AI is visible team member
- Natural Jira patterns
- Clear who did what
- Metrics track AI contribution

**Cons:**
- AI as "user" may have license implications
- Need review assignment workflow
- Capacity planning gets complex

---

## Decision Criteria

| If You Value... | Choose |
|-----------------|--------|
| Simplicity | Option A (labels) |
| Clean human view | Option B (separate boards) |
| Strict separation | Option C (separate projects) |
| Human accountability | Option D (subtasks only) |
| AI as team member | Option E (AI user) |

## Recommendation for Discussion

**Start with Option B (Separate Boards, Same Project)** because:

1. Single project = context preserved
2. Human board is clean by default
3. AI board available when needed
4. Easy to implement (just Jira filters)
5. Can evolve to Option C later if needed

**Workflow:**
1. Human creates Story in EACPP
2. AI agent creates subtasks/linked issues with `ai-generated` label
3. Human board shows Story (hides AI subtasks)
4. AI board shows all AI work for review
5. Human reviews and merges AI work

---

## Additional Considerations

### AI Work Requires Human Approval Gate

Regardless of option chosen:
- AI-generated PRs require human review
- AI-created issues should have human reviewer assigned
- AI cannot close its own work without human sign-off

### Metrics Implications

Consider tracking separately:
- Human velocity (story points)
- AI throughput (tasks completed)
- AI efficiency (tasks per human prompt)
- Review overhead (time to review AI work)

### Future State: AI Agents as First-Class Team Members

As AI matures, we may evolve to:
- AI agents with their own capacity
- AI "sprint commitments"
- AI performance reviews (accuracy, quality)
- AI specialization (testing agent, docs agent, etc.)

## Consequences

**Good:**
- Clear visibility into AI contributions
- Audit trail for compliance
- Human oversight maintained
- Metrics accuracy improved

**Bad:**
- Additional process overhead
- Risk of over-engineering
- May slow down AI utilization initially

## More Information

* Related: ADR-0004 (Jira Project Tracking)
* Related: ADR-0009 (CI/CD Automation)
* Consider: GitHub Copilot Workspace patterns
* Consider: How other AI-first teams handle this
