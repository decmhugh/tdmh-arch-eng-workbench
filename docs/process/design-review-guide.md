# Design Review Guide

## Purpose

Design reviews are the primary quality gate in spec-driven development. Every spec
gate advancement requires a reviewed and approved pull request. This guide standardizes
how reviews are conducted across the ACP team.

## Review Types by Gate

| Gate | Review Type | Reviewers | Focus |
|------|------------|-----------|-------|
| D0 → D1 | Scope review | Tech Lead + PO | Is the problem real? Is scope bounded? |
| D1 → D2 | Requirements review | Engineering team (2+ reviewers) | Are requirements testable? Complete? |
| D2 → D3 | Architecture review | Cross-team architects (2+ reviewers) | Sound architecture? Security? Scale? |
| D3 → D4 | Sprint readiness | PO + Tech Lead | Tasks sized? Dependencies mapped? |
| D4 → Done | Release review | QA + Tech Lead | Tests pass? Security clear? Ready to ship? |

## Review Checklist

### D0 Discovery Review

- [ ] Problem statement is specific and evidence-based
- [ ] Scope boundaries are explicit (in-scope / out-of-scope)
- [ ] Stakeholders are identified with their concerns
- [ ] Success criteria are measurable
- [ ] Dependencies on other components are listed
- [ ] Risks are identified with mitigation strategies
- [ ] No solution prescribed (discovery is about the *problem*)

### D1 Requirements Review

- [ ] Every requirement has acceptance criteria
- [ ] Acceptance criteria follow Given/When/Then format
- [ ] Non-functional requirements have quantified targets (latency < 100ms, etc.)
- [ ] API contracts are sketched (endpoints, methods, key fields)
- [ ] Edge cases and error scenarios are documented
- [ ] Requirements trace back to D0 success criteria
- [ ] No design decisions smuggled into requirements

### D2 Design Review

- [ ] Architecture diagram present (mermaid)
- [ ] Sequence diagrams for all key flows
- [ ] API design covers all D1 functional requirements
- [ ] Data model supports all required queries
- [ ] Error handling strategy is comprehensive
- [ ] Security considerations addressed (auth, validation, secrets)
- [ ] Testing strategy covers unit, integration, and e2e
- [ ] Migration/rollback plan for existing systems
- [ ] Observability plan (metrics, logging, alerting)
- [ ] Design decisions are justified (why this approach, what alternatives considered)

### D3 Task Review

- [ ] Every task is ≤ 3 story points
- [ ] Tasks have clear Definition of Done
- [ ] Dependency graph is acyclic
- [ ] Sprint allocation is realistic given team capacity
- [ ] Risk mitigation tasks (spikes) are front-loaded
- [ ] Tasks trace back to D2 design components
- [ ] Jira ticket mapping is included

### D4 Verification Review

- [ ] All D1 acceptance criteria have corresponding test results
- [ ] Test coverage meets threshold (≥ 90% new code)
- [ ] Performance benchmarks meet D1 NFR targets
- [ ] Security review completed with no critical findings
- [ ] API conformance verified (actual matches D2 spec)
- [ ] Known issues documented and tracked
- [ ] Deployment checklist completed

## Conducting a Review

### As a Reviewer

1. **Read the full spec** — don't skim. Specs are the design artifact.
2. **Check completeness** — use the checklist above for the relevant gate.
3. **Challenge assumptions** — ask "what if?" and "how do we know?"
4. **Be specific** — "this API endpoint doesn't handle the 404 case from D1-REQ-3" > "needs more error handling"
5. **Approve or request changes** — no "LGTM" without checklist completion.
6. **Time-box**: Reviews should take 30-60 minutes. If longer, the spec is too large — ask to split.

### As an Author

1. **Self-review first** — run through the checklist before requesting review.
2. **Provide context** — PR description should summarize what changed and why.
3. **Link dependencies** — reference related specs, Jira epics, and architecture docs.
4. **Respond to all comments** — resolve or explain, never ignore.
5. **Don't advance without approval** — the gate is the gate.

## Review SLA

| Priority | First review within | Resolution within |
|----------|-------------------|-------------------|
| Critical (blocking other teams) | 1 business day | 2 business days |
| Normal | 2 business days | 5 business days |
| Low (no time pressure) | 5 business days | 10 business days |

## Escalation

If a review is blocked (disagreement on approach):
1. Schedule a 30-minute sync with reviewers
2. If unresolved, escalate to Architecture Council
3. Decision is documented in the PR and spec
