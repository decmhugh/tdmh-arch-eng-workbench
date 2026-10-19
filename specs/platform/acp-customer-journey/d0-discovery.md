# ACP Customer Journey, Phase 1 — D0: Discovery (draft)

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: [EACPP-1134](https://sunlife.atlassian.net/browse/EACPP-1134)
> Source of truth for the flow: [customer-journey.mmd](customer-journey.mmd).

**Scope: Phase 1 only** — from first contact with a business group through to a use case being
specified, its pattern ruled on, and any new pattern built and verified. The journey ends at the
point the use case is ready to register an agent. Registration, runtime operation and change
management are deliberately out of scope and will be specified separately.

**This is the First Wave model — interim and high-touch by design.** ACP is early enough in its
lifecycle that every engagement is hand-run by the ACP Product Team rather than self-served. The
target state is a fully self-serve journey where the End User engages their Regional Architect
directly and the RA owns and drives the onboarding end to end; that end state is known, but when and
how the transition happens is not yet designed — see D2 DD-16.

## Problem Statement

Two questions arrive constantly and are answered differently each time:

1. **From a business group**: *"What is the process to be onboarded to ACP?"*
2. **From inside the ACP Product Team**: *"What is the process to build ACP capability when a use
   case does not fit an existing pattern?"*

No single artefact answers either:

| Artefact | Covers | Does not cover |
|----------|--------|----------------|
| `luminate-user-guides` | Using the Luminate portal once you have access | Who you talk to, in what order, to get there |
| `acp-onboarding-guide` | Onboarding onto ACP generally | Team accountability and approval gates |
| `docs/capability-map.md` | What ACP can do | The engagement that consumes the map |


Three consequences follow:

- Business groups leave discovery with no picture of what comes next, so they cannot plan and
  repeatedly ask "what now".
- Hand-offs to ACP EA, Domain Architects and Regional Architects are arranged ad hoc. Nobody can say
  from a document who is engaged when.
- Delivery ownership for a new pattern is settled in conversation, so ACP and the Consortium can
  each believe the other is building it.

## Opportunity

One versioned, reviewable spec that answers both questions from a single link, names an owner for
every hand-off, and puts the pattern and delivery-owner decisions on the record before build starts.

It also becomes the intake front door: each engagement instantiates the journey and produces its own
D0→D4 artefacts, which appear in `specs/README.md` and roll into the O7 report.

## Stakeholders

Roles and codes are defined once, in [d2-design.md](d2-design.md#actors). This table
records only what each party needs from the journey.

| Stakeholder | Key Concern |
|-------------|-------------|
| End User (business group / use-case owner) | "How long will this take, and what will you ask me for?" |
| ACP Product Team | A repeatable engagement that does not re-litigate process each time |
| GbyD / MRM prerequisite owners | The business arrives with a completed GenAI Risk Triage Form and a ready MBCT ID |
| ACP Enterprise Architect | Nothing is built before the new pattern is defined and a delivery owner is named |
| Consortium Team | A clear boundary for what routes to Luminate versus the harness |
| Regional (BG) Architects | Engaged early enough to influence, not after the design is fixed; own the pattern-fit ruling at 1.2 |
| Domain Architects | Reviews arrive scoped, with a complete `d2-design.md` |
| ACP PO (Lalit Summan) / SM (David Nguyen) | Engagements are prioritised and resourced against other ACP work |

Neither GbyD nor MRM is a Phase 1 actor: ACP checks before 1.1 that their outputs are present, not
whether it agrees with them (D2 DD-19). MRM remains a stakeholder in the wider journey, but ongoing
model-risk governance is out of scope.

## Scope

### In Scope

Phase 1 in full, steps 1.1 through 1.9:

- The interaction model across the six actors involved, from first business-group contact to a
  verified pattern, a communicated outcome and a use case ready to register.
- Verification before 1.1 that the business has supplied the completed GbyD GenAI Risk Triage Form
  and a ready MRM MBCT ID, performed manually by ACP and recorded before onboarding starts.
- The Regional Architect's pattern-fit ruling at 1.2, which screens the applicable shapes in
  `agent-patterns` (including other substrates against SUB-E/SUB-I) alongside `integration-patterns`,
  decides whether an engagement takes the short path or the full one, and initiates governance
  approval when a new pattern is required.
- A design review with the End User right after the solution architecture is drafted (1.6).
- A single closing communication at 1.9, on both paths.
- The conditional branches within Phase 1: exact match or new pattern required (1.2a/1.2b), design
  changes requested or confirmed (1.6a/1.6b), and ACP versus Consortium delivery (1.8a/1.8b).
- Named interaction points — every hand-off that crosses a team boundary.
- A responsibility model (RACI) covering each step.
- The artefact model: which D0→D4 file each step produces and who authors it.
- Mermaid source in `customer-journey.mmd` as the single source for the diagram, with
  a generated copy embedded in the spec.

### Out of Scope

- **Everything after Phase 1.** Agent registration (portal and programmatic), runtime monitoring,
  ongoing MRM governance and change management were drafted and have been deliberately cut. They
  need their own spec — see OQ-2.
- **Portal click-paths.** `luminate-user-guides` owns "which button, which field".
- **Governance intake and risk triage.** `governance-intake` defines a separate intake; it is not
  wired into this journey. Before 1.1, the business must provide the completed GbyD GenAI Risk
  Triage Form and a ready MRM MBCT ID; ACP manually verifies both but does not perform the risk
  triage or model-risk assessment. Platform PIA/ISRA/ATG approval is obtained by the Regional
  Architect at 1.2b-1. The approval request may be long-lead: discovery and design may proceed,
  but approval must be confirmed before any new-pattern implementation or upstream delivery — see
  D2 DD-10.
- **The capability map itself.** This spec consumes `docs/capability-map.md` at step 1.3; it does
  not define or duplicate capabilities.
- **Per-use-case content.** This is the journey template. Individual engagements (AIMS, ORCC, MDx,
  Waldo, US team) each get their own `spec_type: onboarding` spec.
- **Tooling to automate the journey.** No intake form, workflow engine or Jira automation is
  proposed here.
- **The internal ACP component roadmap.** "How to build ACP" here means how a *pattern* gets built
  in response to a use case, not the product backlog.

## Capability Requirements

Not applicable. That table belongs to `onboarding` and `integration` specs, where a named use case
selects from [the ACP Capability Map](../../../capability-map.md). This is a `platform` spec: it
defines the process by which that table gets filled in, at step 1.3.

Two capability-map rules constrain the journey design and are carried into D1 as FR-8 — capabilities
are **confirmed, never inferred**, and the **mandatory baseline applies whether or not it is
requested**.

## Success Criteria

| ID | Criterion | Measurement | Target |
|----|-----------|-------------|--------|
| SC-1 | A business group can answer "what happens next" from the spec alone | Use-case owners who can name the remaining steps and what they must produce, without asking ACP | 100% of engaged business groups |
| SC-2 | Every hand-off has a named accountable party | Interaction points with an owner and no `UNDEFINED` | 100% |
| SC-3 | Delivery ownership for a new pattern is recorded before build | Engagements where the delivery owner is written down at 1.7 before any 1.8 work | 100% |
| SC-4 | Exit paths are defined | Undefined negative outcomes in Phase 1 | 0 |
| SC-5 | Engagement duration becomes predictable | Step durations recorded against target for completed engagements | Targets exist and are met ≥ 70% |
| SC-6 | The published diagram never drifts from source | CI check that the embedded diagram matches the `.mmd` | Enforced, passing |
| SC-7 | Onboarding engagements are visible as specs | Engagements with a `specs/` directory and a Jira epic | 100% of active engagements |
| SC-8 | Entry prerequisites are verified | Engagements with a completed GbyD GenAI Risk Triage Form and ready MRM MBCT ID manually verified by ACP before 1.1 | 100% |
| SC-9 | Capability requirements are confirmed, never inferred | Selected capabilities in the engagement's `d0-discovery.md` carrying a named confirmer and date, with the mandatory baseline acknowledged | 100% |

SC-4 stands at zero because CG-5 is closed by assumption — governance approval for a new pattern is
taken to be eventually granted (D2 DD-10). The residual risk that the assumption is wrong is carried
as R-9, not as an undefined outcome.

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
| Pattern approval process definition | ACP Enterprise Architect | **Hard** | 1.7 gates every new-pattern build; 1.2 decides whether an engagement reaches it at all (D2 DD-17) |
| ACP ↔ Consortium delivery delineation | ACP + Consortium Team | Soft | Settled — the delineation rule and the close-the-loop hand-back are documented in `docs/process/capability-gap-escalation.md` §1 and §3 (D2 DD-4, DD-12) |
| `docs/capability-map.md` currency | ACP Product Team | Hard | Step 1.3 walks the map; a stale map misleads the use case |
| `integration-patterns` and `agent-patterns` as the pattern catalogues | ACP Product Team | **Hard** | At 1.2 the RA uses `integration-patterns` for the integration/adoption path and screens every applicable agent shape in [`agent-patterns`](../../pattern/agent-patterns/d2-design.md), recording the selected shape(s) and any open SUB-E/SUB-I criteria (D2 DD-8, DD-17) |
| `governance-intake` boundary | ACP + `governance-intake` owners | Soft | Settled for now — GbyD risk triage and MRM model-risk assessment occur before ACP onboarding; ACP manually verifies their outputs. For a new pattern, the RA initiates platform PIA/ISRA/ATG approval at 1.2b-1, and ACP confirms it before 1.8 (D2 DD-10) |
| A spec covering what follows Phase 1 | ACP Product Team | Soft | Narrowed — registration and the technical path are already covered elsewhere; runtime governance and change management are not (D2 DD-5) |
| Jira epic for this spec | ACP PO | Hard | Satisfied — [EACPP-1134](https://sunlife.atlassian.net/browse/EACPP-1134) |

## Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|------------|
| R-1 | The journey documents a process the named teams have not agreed to | High | High | D2 exit criteria require each actor to confirm its own accountability |
| R-2 | The spec publishes only the happy path | Low | High | Reduced by design: no step terminates an engagement, and the 1.6 design review lets the end user catch misalignment before the pattern is defined (D2 DD-14, DD-15). CG-5 is closed by an assumption — governance approval for a new pattern is eventually granted (D2 DD-10) — rather than a drawn refusal path, and that assumption's residual risk is R-9. The remaining open item, CG-4 (durations), is non-blocking |
| R-3 | Phase 1 alone does not answer the customer's actual question, which runs to a working agent | High | Medium | State the boundary in the lead paragraph; resolve OQ-2 so the follow-on spec is scheduled |
| R-4 | **Closed.** The pattern gate added latency to every engagement, including obvious existing-pattern cases | — | — | The fit ruling moved to the Regional Architect at 1.2; an exact match now skips 1.7 and 1.8 and never reaches the Enterprise Architect (D2 DD-17). The residual risk is a wrong ruling with no later checkpoint — D2 DQ-9, a correctness question distinct from R-9 |
| R-5 | Business stakeholders reject D0→D4 vocabulary as engineering jargon | Medium | Medium | Artefact table states each file's contents in plain terms; consider a business-facing one-pager |
| R-6 | The process is published once and then rots as teams reorganise | Medium | High | Ownership assigned to ACP Product Team; review cadence set at D3 |
| R-7 | **Closed.** The Miro board is retired; `customer-journey.mmd` is the only journey artefact, maintained by the ACP Product Team | — | — | No parallel copy exists to diverge from (D2 DD-6) |
| R-8 | Named individuals change; the spec hard-codes people | Medium | Low | Reference roles and Backstage groups, not names, except for reserved-action routing |
| R-9 | PIA / ISRA / ATG approval for a new pattern is outright refused, contrary to the Phase 1 assumption that it is eventually granted (D2 DD-10) | Low | High | No recovery path is drawn — if this occurs, the engagement escalates to the Regional Architect and platform governance outside the journey as documented. Revisit if it materialises. **Scoped to onboarding**: this is a risk to getting a use case through Phase 1, not to an agent's runtime operation — ongoing governance of an already-onboarded agent is out of scope (see Out of Scope) and owned by whichever spec covers OQ-2 |

## Open Questions

Scoping questions only. Gaps in the process itself are tracked once, in the
[D1 gap register](d1-requirements.md#capability-gaps).

- [x] **OQ-1** — Is this one `platform` spec, or a template each `onboarding` spec instantiates?
      **Answered: one `platform` spec.** It defines the process; each engagement instantiates it as
      its own `spec_type: onboarding` directory (FR-11). Registered as `spec_type: platform` in
      `spec.yaml`.
- [ ] **OQ-2** — What covers the ground after Phase 1 — registration, runtime, governance, change
      management — and who writes it? Until this is answered the customer-facing answer stops short
      of a working agent. Partly answered already: `integration-patterns` covers the technical path
      after readiness, [`agent-patterns`](../../pattern/agent-patterns/d2-design.md) covers the agent shapes and
      conformance criteria, and `luminate-user-guides` covers the registration click-path, so the
      gap is narrower than "everything after Phase 1".
- [ ] **OQ-3** — Where exactly does the boundary sit between this spec and `luminate-user-guides`?
- [x] **OQ-4** — Which Jira epic does this spec map to? **Answered: [EACPP-1134](https://sunlife.atlassian.net/browse/EACPP-1134)**,
      created for the spec. Sub-task EACPP-1041 remains the delivery ticket for the Mermaid
      conversion under EACPP-815.
