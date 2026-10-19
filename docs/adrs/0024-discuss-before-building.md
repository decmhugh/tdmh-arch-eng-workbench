---
parent: Decisions
nav_order: 24
title: ADR-0024 Discuss Before Building Philosophy
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0024: Discuss Before Building Philosophy

## Status

**Draft**

## Context and Problem Statement

Engineering teams often jump straight to building without aligning on the "why" and "how". This leads to:
- Rework when assumptions don't match
- Technical debt from rushed decisions
- Misaligned implementations across team members
- Knowledge silos

**Key question**: When should we pause to discuss vs. just build?

## Decision Drivers

* Speed vs. alignment tradeoff
* Distributed team challenges
* AI-assisted development changes the equation
* Documentation as alignment artifact
* Avoiding "two people solving the same problem differently"

## Decision Outcome

**Adopt a "Discuss First" culture for decisions with long-term consequences.**

### When to Discuss First

| Scenario | Discuss First? | Why |
|----------|----------------|-----|
| New technology adoption | Yes | Long-term maintenance impact |
| API contract changes | Yes | Consumer dependencies |
| Data model changes | Yes | Migration complexity |
| Process changes | Yes | Team-wide impact |
| Security decisions | Yes | Compliance/audit |
| Architecture patterns | Yes | Consistency matters |
| Quick bug fix | No | Just fix it |
| Typo in docs | No | Just fix it |
| Local refactor (no API change) | Maybe | Use judgment |

### How to Discuss

**1. Lightweight (Slack/Teams thread)**
- For small decisions
- Time-boxed (24-48 hour response window)
- Document outcome in commit message or PR

**2. ADR (Architecture Decision Record)**
- For significant decisions
- Written proposal with options
- Async review, sync meeting if needed
- Permanent documentation of decision

**3. Design Review Meeting**
- For complex or contentious decisions
- When written discussion isn't converging
- Record decision in ADR after meeting

### The ADR Workflow

```
1. Identify decision needed
2. Draft ADR with options (this is "discuss" not "decide")
3. Share for review (async first)
4. Discuss in meeting if needed
5. Update ADR with decision
6. Implement based on agreed approach
7. Reference ADR in implementation PRs
```

### AI Agents and "Discuss First"

**AI should not make architectural decisions autonomously.**

| AI Can Do | AI Should Ask First |
|-----------|---------------------|
| Implement agreed patterns | Propose new patterns |
| Fix bugs | Change data models |
| Add tests | Add new dependencies |
| Refactor within bounds | Change API contracts |
| Generate code per spec | Deviate from spec |

**Workflow:**
1. Human identifies work needed
2. Human/AI drafts ADR if decision required
3. Team discusses and decides
4. AI implements based on decision
5. Human reviews and approves

### Benefits

- **Alignment**: Everyone knows the "why" before building
- **Documentation**: Decisions are recorded for future reference
- **Onboarding**: New team members can read ADRs to understand context
- **Reduced rework**: Fewer "I didn't know we decided that" moments
- **Better AI**: AI agents have clear guidance on patterns to follow

### Risks

- **Overhead**: Discussion takes time
- **Paralysis**: Over-discussing small decisions
- **Stale ADRs**: Decisions change but ADRs not updated

### Mitigation

- Use the "When to Discuss" table as guide
- Time-box discussions (48 hours async, then meeting if needed)
- Treat ADRs as living documents (can be superseded)
- Review ADRs quarterly for relevance

## This ADR is Self-Referential

This very ADR exemplifies the philosophy:
- We're discussing whether to adopt "discuss first" before doing it
- We're documenting the decision for future reference
- The team can review and agree (or modify) before implementing

## Consequences

**Good:**
- Shared understanding of approach
- Reduced rework and surprises
- Better onboarding for new members
- Clear guidance for AI agents

**Bad:**
- Slower initial velocity
- More meetings/docs initially
- Need discipline to follow process

**Mitigation:**
- Start with high-impact decisions only
- Keep ADRs short and focused
- Use templates to reduce overhead

## More Information

* Related: ADR-0001 (Spec-Driven Development)
* Related: ADR-0002 (D0-D4 Stage Gates)
* Inspiration: "The most expensive bugs are disagreements about requirements"
