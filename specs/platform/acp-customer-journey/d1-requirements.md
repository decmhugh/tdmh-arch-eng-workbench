# ACP Customer Journey, Phase 1 — D1: Requirements (draft)

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: [EACPP-1134](https://sunlife.atlassian.net/browse/EACPP-1134)
> Traces to [d0-discovery.md](d0-discovery.md). Design in [d2-design.md](d2-design.md).

**Scope: Phase 1 only** — steps 1.1 to 1.9, ending when a use case is specified, its pattern ruled
on, any new pattern verified and the outcome communicated. Registration, runtime and governance are
out of scope (D0 OQ-2).

**What is being specified.** The deliverable is a process definition and its published artefact, not
software. "The system" below means the journey spec, the mermaid source, and the practices that keep
them true. Requirements are therefore about completeness, accuracy, discoverability and non-drift,
not latency or throughput.

## User Stories

### US-1: A business group understands the process before the first meeting

**As a** use-case owner in a business group,
**I want** to read the ACP intake process from one link,
**So that** I arrive at discovery knowing what will be asked of me and what happens next.

**Acceptance Criteria**:
- [ ] **Given** no prior ACP context, **When** I read the journey, **Then** I can name every step
      from first contact to pattern readiness without asking a person.
- [ ] **Given** any step, **When** I look it up, **Then** it states what I produce, who I hand it
      to, and what I get back.
- [ ] **Given** I have asked for a discovery session, **When** I read step 1.3, **Then** it is clear
      that the engagement proceeds by default and 1.3 produces `d0-discovery.md` rather than a
      qualification verdict.
- [ ] **Given** I want to start ACP onboarding on any ACP platform instance, **When** I read the
      journey, **Then** I know the business must provide a completed GbyD GenAI Risk Triage Form and
      a ready MRM MBCT ID, which ACP manually verifies and records before 1.1.
- [ ] **Given** my Regional Architect rules at 1.2, **When** I ask what it means for me, **Then** the
      journey states which steps my engagement will run — the short path on an exact match, or the
      full path with pattern definition and delivery on a new pattern.
- [ ] **Given** Phase 1 completes, **When** I ask what follows, **Then** the spec says plainly that
      registration onward is covered elsewhere, rather than trailing off.

### US-2: An ACP facilitator runs an engagement without re-deriving the process

**As an** ACP Product Team member facilitating an engagement,
**I want** a defined sequence with named hand-offs and artefacts,
**So that** every engagement runs the same way and nothing is skipped.

**Acceptance Criteria**:
- [ ] **Given** a new engagement, **When** I open the journey, **Then** each step names its actor,
      trigger, output artefact and expected response.
- [ ] **Given** a cross-team hand-off, **When** I consult the interaction points table, **Then** I
      know which team to engage and what to send them.
- [ ] **Given** an engagement stalls, **When** I look up the stalled step, **Then** exactly one
      party is accountable for it.
- [ ] **Given** Phase 1 is complete, **When** I check my outputs, **Then** I hold `d0-discovery.md`,
      `d1-requirements.md` and `d2-design.md` for the use case.
### US-3: The pattern decision is made by the right party, on the right input

**As the** Regional Architect and the ACP Enterprise Architect,
**I want** pattern fit and pattern definition to be separate steps with separate owners,
**So that** obvious cases are not queued behind an architecture review, and nothing is built before
a delivery owner is named.

**Acceptance Criteria**:
- [ ] **Given** a completed business-internal assessment, **When** I rule at 1.2, **Then** I rule
      against `integration-patterns` and, for agent solutions, screen every applicable shape in
      [`agent-patterns`](../../pattern/agent-patterns/d2-design.md): Agent vs Application, egress vs ingress,
      S1-S4, and any other substrate against SUB-E/SUB-I. I record the finding as 1.2a or 1.2b,
      with the selected shape(s), the evidence and any open criteria; the use case need not fit every
      shape, and an open or unexercised criterion alone does not mean the shape is refused or a new
      pattern is required.
- [ ] **Given** I rule "exact match" (1.2a), **When** the decision is recorded, **Then** the
      engagement runs 1.3 to 1.6, skips 1.7 and 1.8, and closes at 1.9.
- [ ] **Given** I rule "new pattern required" (1.2b), **When** the decision is recorded, **Then**
      the applicable governance approval request is initiated before discovery starts and
      approval is confirmed before any 1.8 implementation or upstream delivery.
- [ ] **Given** a submission at 1.7, **When** I receive it, **Then** it includes a complete
      `d2-design.md` — architecture, pattern selection, integration design, security and
      governance controls, deployment approach, open questions — already reviewed with the end
      user at 1.6.
- [ ] **Given** I define a new pattern at 1.7, **When** I confirm it, **Then** the delivery owner —
      ACP or Consortium — is named in the same decision record.
- [ ] **Given** the pattern question, **When** I consult the journey, **Then** it yields exactly two
      outcomes — exact match or new pattern required — with no decision step to reject the
      submission; a new-pattern finding always proceeds to definition and build.

### US-4: A new pattern comes back verified, whoever delivers it

**As the** ACP Product Team,
**I want** each delivery track to end in verification ACP has confirmed,
**So that** an externally delivered pattern is as trustworthy as one we built.

**Acceptance Criteria**:
- [ ] **Given** the ask is classified integration, **When** delivery completes, **Then**
      `d3-tasks.md` and `d4-verification.md` exist in the engagement's own spec directory.
- [ ] **Given** the ask is classified a component change, **When** it is raised, **Then** ACP has
      registered it on the Sun Life board and written a delta spec in `acp-consortium-specs` stating
      what Luminate does today, what is missing and what should change.
- [ ] **Given** consortium work lands upstream, **When** ACP resumes the engagement, **Then** ACP
      re-verifies it, updates the capability map and closes the Sun Life ticket referencing the
      consortium ticket — the close-the-loop step (D2 DD-12).
- [ ] **Given** a consortium ask is not yet accepted, **When** the use case needs to move, **Then**
      an explicitly temporary interim measure is recorded with the condition that removes it
      (D2 DD-13).
- [ ] **Given** a pattern is delivered, **When** ACP resumes the engagement, **Then** the request
      status reads "new pattern ready" before the use case proceeds to registration.
- [ ] **Given** either path reaches readiness, **When** the engagement closes, **Then** ACP issues
      the 1.9 communication to the End User, ACP EA, CT, RA and DA (D2 DD-18).

### US-5: The published journey cannot silently drift from its source

**As the** owner of the journey spec,
**I want** the diagram generated from `customer-journey.mmd`,
**So that** an edit to one is never quietly absent from the other.

**Acceptance Criteria**:
- [ ] **Given** the `.mmd` changes, **When** CI runs, **Then** a stale embedded copy fails the build
      and names the file to regenerate.
- [ ] **Given** the spec renders in MkDocs and Confluence, **When** a reader opens it, **Then** the
      diagram displays without requiring the `.mmd` repo.
- [ ] **Given** a stakeholder-facing view of the journey is wanted, **When** one is produced, **Then**
      it is rendered from the `.mmd` rather than redrawn — no second editable copy is kept anywhere.

## Functional Requirements

### FR-1: Actor definition
The journey defines each participating team with a short code, a role statement, and its
accountability. Six actors: EU, ACP, ACP EA, CT, RA, DA. No step may reference an actor outside this
set — the Forward Deployed Engineering Team was removed from Phase 1 in D2 review (D2 DD-9).

### FR-2: Step model
Phase 1 is decomposed into numbered steps 1.1 to 1.9. Every step carries: actor, action, and — where
it produces one — an output artefact. Step numbering is explicitly not stable across revisions.

### FR-3: Interaction points register
Every hand-off crossing a team boundary is a numbered row with: step, from → to, trigger, hand-off
content, and response expected. This register is the answer to "who do I talk to, and when".

### FR-4: Responsibility model
A RACI covering every step, with exactly one **A** per step. Two accountabilities must be stated
explicitly because they are commonly misread: the **Regional Architect** owns the pattern-fit
decision at 1.2 (D2 DD-17), and the **ACP Enterprise Architect**, not the ACP Product Team, defines
the new pattern and names its delivery owner at 1.7.

### FR-5: Artefact model
Each step names the D0→D4 artefact it produces, its author, and its contents in plain language.
Use-case onboarding runs on the same gate model as ACP component specs.

### FR-6: Conditional branches
Every branch is modelled explicitly, with its selecting condition:

| Branch | Selects between | Decider |
|---|---|---|
| 1.2a / 1.2b | Exact match to an existing pattern / new pattern required, with the required governance approval initiated first and confirmed before 1.8 | **RA** |
| 1.6a / 1.6b | Changes requested, returning to 1.5 / design alignment confirmed | EU |
| 1.8a / 1.8b | ACP delivers via the harness / the consortium delivers upstream | ACP EA, on the delineation rule |

### FR-7: Exit and failure paths
Phase 1 models no negative or exit outcome: **no path terminates an engagement.** A business group
that has entered the journey has already decided to onboard, so there is no go/no-go step (D2
DD-14), and the pattern question at 1.2 always ends in either an exact match or a build (D2 DD-11).
Both paths close at 1.9.

One path does return to an earlier step, and it is rework rather than an exit: requested changes at
the 1.6 design review send the design back to 1.5 to be redrafted and re-presented (1.6a). The
engagement continues throughout.

### FR-8: Capability map integration
Step 1.3 walks [the ACP Capability Map](../../../capability-map.md) live with the use case, and
must encode both governing rules: capabilities are **confirmed, never inferred**, and the
**mandatory baseline applies whether or not it is requested**. Any selected capability that is not
fully available opens a gap row and follows
[Capability Gap Escalation](../../../process/capability-gap-escalation.md).

### FR-9: Single-source diagram
`customer-journey.mmd` is the source, and it is the **only** editable copy — the Miro board it came
from is retired (D2 DD-6). `d2-design/journey.md` carries a copy between
`BEGIN/END GENERATED: journey` markers, written by `scripts/sync_mermaid_embeds.py`. Editing the
copy in place is prohibited and mechanically caught: `sync_mermaid_embeds.py --check` fails CI when
the two disagree. Any stakeholder-facing view is a render of the `.mmd`, never a redraw.

### FR-10: Scope boundary
The spec ends at pattern readiness and says so. Where a reader needs what comes next — registration,
runtime, governance — it names the boundary and links out rather than trailing off or restating
`luminate-user-guides`.

### FR-11: Per-engagement instantiation
Each engagement produces its own `spec_type: onboarding` directory with a `spec.yaml` and a Jira
epic, so it appears in `specs/README.md` and rolls into the O7 report. This spec is the template,
not the record of any one engagement.

### FR-12: Entry prerequisite verification
Before Phase 1 step 1.1, the business must provide a completed GenAI Risk Triage Form from the
Governance by Design team (GbyD) and a ready MBCT ID from Model Risk Management (MRM). The ACP
Product Team manually verifies that both prerequisites are present and records the verification
result. This applies to onboarding onto **any ACP platform instance** — Luminate DEV as much as
PROD — so starting on a lower instance does not exempt a use case. Onboarding is paused when either
prerequisite is missing. ACP does not perform GbyD risk triage or MRM model-risk assessment.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Completeness | Decision points resolve to a fully defined outcome | **4 of 4** — the entry gate resolves to prerequisites present or missing (onboarding pauses until supplied); 1.2 resolves to exact match (1.2a) or new pattern required (1.2b); 1.6 resolves to changes-requested (1.6a, returns to 1.5) or alignment-confirmed (1.6b); the delivery branch decided at 1.7-9 resolves to an ACP (1.8a) or a Consortium (1.8b) delivery owner. No rejection outcome exists at any of them |
| NFR-2 | Accountability | Steps with exactly one accountable party | 100%, zero `UNDEFINED` |
| NFR-3 | Accuracy | Actors who have confirmed their own row in the responsibility model | All 6, recorded with name and date |
| NFR-4 | Non-drift | Embedded diagram matches `.mmd` | CI-enforced, build fails on drift |
| NFR-5 | Discoverability | Reachable from `specs/README.md`, MkDocs nav, and Confluence | All three |
| NFR-6 | Currency | Review cadence with a named owner | Quarterly, ACP Product Team |
| NFR-7 | Stability | Step numbering may change between revisions; the phase name does not | Stated in the spec |
| NFR-8 | Predictability | Target duration published per step | Every step *(CG-4)* |
| NFR-9 | Traceability | Every user story and functional requirement traces to a D0 success criterion; non-functional requirements trace where they express an outcome rather than a convention | 100% of user stories and FRs — see Traceability |

## Data Model Requirements

The journey has no database. Its "entities" are the records an engagement produces.

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| Entry Prerequisite Verification | GbyD form present, MRM MBCT ID present, verifier, date, result | precedes the Engagement; recorded by ACP at the entry gate |
| Engagement | use case, business group, current step, ACP facilitator, start date | has_many Artefacts; has one Pattern Decision |
| Artefact | gate (D0–D4), author, status, path | belongs_to Engagement |
| Pattern Decision | fit ruling existing/new (RA, 1.2), pattern definition (ACP EA, 1.7), delivery owner (ACP/CT, named at 1.7-9), date | belongs_to Engagement; has_many Delivery Artefacts |
| Capability Selection | capability ID, priority, status today, confirmed by, date | belongs_to Engagement; may open a Capability Gap |

## Edge Cases

Scenarios that are already defined. The undefined ones are in the gap register below.

| Scenario | Expected Behavior |
|----------|-------------------|
| Exact match to an existing pattern | 1.7 and 1.8 are skipped entirely; the engagement runs 1.3–1.6 and closes with the 1.9 communication |
| End user requests changes at the 1.6 design review | ACP revises `d2-design.md` and re-presents it; the design does not proceed until the end user confirms alignment |
| Business group has already built the agent before contacting ACP | The journey is entered at 1.1 regardless; the 1.2 fit ruling, discovery and capability confirmation are not waived |
| Use case needs a modelled-not-enforced capability, such as quotas | D0 records it against the map; D1 opens a gap row with an interim measure and a removal condition |
| Both ACP and Consortium believe the other is delivering | Prevented by FR-6 — the delivery owner is named at 1.7-9, in the same decision record as the pattern definition, not agreed informally |
| Use case turns out to be a poor fit for ACP | Handled as a conversation between ACP and the business group and recorded in `d0-discovery.md`. It is not a drawn path: no step in Phase 1 terminates an engagement (D2 DD-14) |
| A use case arrives without the wider governance approvals its own use case requires — distinct from the entry-gate prerequisites below | Surfaced at 1.3. Those approvals are a precondition, not a Phase 1 step, so the engagement does not proceed on the assumption that they are held (D2 DD-10) |
| A use case arrives without the GbyD form or MRM MBCT ID | Caught at the entry gate before 1.1. ACP checks only that both are present — it neither approves them nor re-runs the assessment behind them — and onboarding does not start until they are. Most use cases already hold both |
| A 1.2a exact-match ruling turns out to be wrong | The behaviour is defined: nothing between 1.3 and 1.6 re-tests the finding. Whether that is sufficient, or a checkpoint is needed, is a correctness question — **D2 DQ-9** — not an undefined outcome, and it does not count against SC-4 |

## Constraints

- **Governance is not optional.** The mandatory baseline applies to every use case irrespective of
  what it requests, and the OSFI and Quebec Law 25 obligations behind it are settled at step 1.3,
  not deferred to whoever runs the agent later.
- **Entry prerequisites and governance approval are preconditions, not Phase 1 steps.** Before 1.1,
  the business must provide the completed GbyD GenAI Risk Triage Form and ready MRM MBCT ID; ACP
  manually verifies both. ACP does not perform risk triage or model-risk assessment. The
  `governance-intake` remains a future ACP capability. Platform-level PIA/ISRA/ATG approval
  is initiated by the Regional Architect at 1.2b-1. A long-lead approval may complete while
  discovery and design proceed, but ACP must confirm approval before 1.8 implementation or
  upstream delivery (D2 DD-10, DD-17).
- **Luminate-only.** The Sun Life internal MVP is not a delivery target and must not appear as an
  alternative platform.
- **Reserved actions.** Deployment, credentials, gateways, environments, quotas and attributes
  cannot be delegated by any Luminate role. Phase 1 does not perform them, but a solution
  architecture at 1.4 must not assume they are self-service.
- **Repository.** `specs/README.md` and `specs/epic-mapping.json` are generated; `spec.yaml`
  requires `component`, `title`, `current_gate`, `status`, `jira_epic`, `spec_type`.

## Capability Gaps

Not the capability-map sense — this is a `platform` spec. These are gaps in the **process itself**:
points where the journey is drawn but not defined. This table is the single register; D0 and D2 both
refer to it rather than repeating it.

| ID | What is missing | Impact | Escalation |
|----|-----------------|--------|------------|
| CG-1 | **Closed — no longer applicable.** Pattern rejection was withdrawn from the journey entirely; the **Regional Architect's ruling at 1.2** now yields exact-match or new-pattern-required only, with no decision step to reject a submission — see D2 DD-11, DD-17 | — | — |
| CG-2 | **Resolved.** Accepted consortium work lands upstream; ACP then re-verifies it, updates the capability map and closes the Sun Life ticket referencing the consortium ticket — the close-the-loop step, see D2 DD-12 | — | ACP + Consortium Team |
| CG-3 | **Closed — no longer applicable.** FDES engagement criteria were the open gap; FDES was removed from Phase 1 in D2 review, so there is no decision left to define (D2 DD-9) | — | — |
| CG-4 | No target durations per step | Blocks NFR-8; this is the first question customers ask | ACP PO |
| CG-5 | **Closed as an assumption, not a design change.** Phase 1 assumes PIA / ISRA / ATG approval for a new pattern is eventually granted. The request is initiated at 1.2b-1 and must be confirmed before 1.8; outright refusal is treated as out of scope for this journey. A conditional approval returns to 1.2b-1 for rework — see the interim measure below | Resolves SC-4 at zero. The residual risk that the assumption is wrong — a use case is refused outright with no drawn recovery — is carried as D0 R-9, not as a process gap | RA + platform governance |

**Interim measures**

| Gap | Interim measure | Removed when |
|-----|-----------------|--------------|
| CG-4 | Set expectations verbally at 1.2, stating that durations are indicative | Targets published per step |
| CG-5 | Treat a conditional approval as a return to 1.2b-1: the Regional Architect reworks the pattern intent against the stated conditions and resubmits. Discovery and design may continue, but 1.8 remains blocked until approval is confirmed. Outright refusal is assumed not to occur for Phase 1 and has no interim measure — see D0 R-9 | Not applicable — closed as an assumption, tracked as a risk (D0 R-9) rather than a gap awaiting a design change |

## Traceability

| Requirement | D0 Success Criteria | Risk addressed | Jira Story |
|-------------|--------------------|----------------|------------|
| US-1, FR-2, FR-5, NFR-5 | SC-1 | R-5 | TBD |
| US-2, FR-1, FR-3, FR-4 | SC-2 | R-1 | TBD |
| US-3, FR-6 | SC-3 | R-4 | TBD |
| US-4, FR-6, CG-2 | SC-3 | — | TBD |
| US-5, FR-9, NFR-4 | SC-6 | R-7 | TBD |
| FR-7, CG-1, CG-5, NFR-1 | SC-4 | R-2 | TBD |
| FR-8 | SC-9 | — | TBD |
| FR-10 | SC-1 | R-3 | TBD |
| FR-11 | SC-7 | R-6 | TBD |
| FR-12 | SC-8 | R-1 | TBD |
| NFR-8, CG-4 | SC-5 | — | TBD |
| NFR-2, NFR-3, NFR-6 | SC-2 | R-1, R-6, R-8 | TBD |

`NFR-7` (step numbering may change; the phase name does not) and `NFR-9` (this table) trace to no
success criterion by design: both are documentation conventions rather than outcomes an engagement
can be measured against, and NFR-9 tracing to itself would be circular.

## D1 exit criteria

- [ ] Each of the six actors has confirmed its own responsibility-model rows
- [x] D0 OQ-1 answered — `platform` spec, registered in `spec.yaml`
- [ ] D0 OQ-2 answered so the follow-on spec covering registration onward is scheduled
- [x] Jira epic assigned — [EACPP-1134](https://sunlife.atlassian.net/browse/EACPP-1134)
