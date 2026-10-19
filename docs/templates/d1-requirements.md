# {Component Name} — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: {EPIC-KEY}

## User Stories

### US-1: {Story Title}

**As a** {persona},
**I want** {capability},
**So that** {value/outcome}.

**Acceptance Criteria**:
- [ ] **Given** {precondition}, **When** {action}, **Then** {expected result}
- [ ] **Given** {precondition}, **When** {action}, **Then** {expected result}
- [ ] **Given** {precondition}, **When** {action}, **Then** {expected result}

### US-2: {Story Title}

**As a** {persona},
**I want** {capability},
**So that** {value/outcome}.

**Acceptance Criteria**:
- [ ] **Given** {context}, **When** {action}, **Then** {result}

## Functional Requirements

### FR-1: {Requirement}

{Description of what the system must do.}

**API Contract Sketch**:
```
POST /api/v1/{resource}
Request: { field1: string, field2: number }
Response: { id: string, status: string }
```

### FR-2: {Requirement}

{Description.}

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Performance | {e.g., API response time} | < 200ms p95 |
| NFR-2 | Availability | {e.g., Uptime} | 99.9% |
| NFR-3 | Security | {e.g., Auth requirement} | OAuth2 / mTLS |
| NFR-4 | Scalability | {e.g., Concurrent users} | 1000 concurrent |
| NFR-5 | Observability | {e.g., Metrics coverage} | All endpoints instrumented |

## Data Model Requirements

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| {Entity} | {field1, field2, ...} | {belongs_to X, has_many Y} |

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| {Edge case} | {What should happen} |

## Constraints

- {Regulatory constraint (OSFI, Quebec Law 25, etc.)}
- {Platform constraint (must run on OpenShift, AWS ca-central-1, etc.)}
- {Compatibility constraint (must maintain backward compat with v1 API)}

## Capability Gaps

> Every capability selected in D0 that is not ✅ Available in the
> [ACP Capability Map](../../../capability-map.md). Each row is classified and escalated
> per [Capability Gap Escalation](../../../process/capability-gap-escalation.md).

| Capability | What is missing | Classification | Impact on this use case | Escalation |
|---|---|---|---|---|
| {CAP-XX} | {The specific missing part, from the map} | Component change / Integration | Blocks launch / Degrades / Workaround available | {EACPP-XXXX, and the consortium ticket once raised} |

**Interim measures** — anything shipped to work around a gap, and the condition under which
it is removed:

| Gap | Interim measure | Removed when |
|---|---|---|
| {CAP-XX} | {What we do instead} | {The capability reaches ✅} |

## Traceability

| Requirement | Capability | D0 Success Criteria | Jira Story |
|-------------|-----------|-------------------|------------|
| FR-1 | {CAP-XX} | SC-1 | {EPIC-XX} |
| US-1 | {CAP-XX} | SC-2 | {EPIC-YY} |

Every functional requirement traces to a capability. A requirement with no capability behind
it is either out of ACP scope or an unrecorded gap — resolve it before leaving D1.
