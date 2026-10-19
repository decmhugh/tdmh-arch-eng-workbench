# Governance Intake UI & AI-Assisted Triage — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Split from** [`governance-intake`](../../governance/governance-intake/d0-discovery.md) (EACPP-877) after the
> GbD × ACP session established that the UI flow and API handoff need their own design and
> implementation discussion, separate from the risk-assessment engine.
> **Predecessor**: `T1KACP/acp-specs/specs/ui-governance-intake` (EACPP-375) — internal-build scope.

## Why this is its own spec

`governance-intake` answers *how risk is assessed* — questionnaire, bands, obligations, gates,
evidence. It assumed an intake UX and moved on: one task (T1) covering "the intake API contract
plus the Amazon Quick form as UX".

That is no longer proportionate. Three things make the UI a design problem in its own right:

1. **The front door is undecided.** Users may stay in the Governance-by-Design UI, or move into
   ACP/Luminate. The session concluded this "requires a dedicated design and implementation
   discussion". Until it is settled, neither team can build.
2. **The delivery vehicle changed twice.** The internal build was a React module inside the ACP
   Management UI; `governance-intake` then assumed Amazon Quick; Quick's production availability is
   explicitly uncertain in that spec's own constraints. The runtime is now Luminate.
3. **It has different reviewers.** Personas and UX are Duncan and Kathryn; the API handoff is Seth.
   The risk engine's reviewers are CMRM. Bundling them makes the design PR unreviewable and blocks
   the engine on a UX decision it does not need.

The engine keeps the contract; this spec owns the surface.

## Problem Statement

- **No agreed front door.** Whether the existing governance UI remains the entry point and ACP
  capabilities are reached through APIs, or users move into the Luminate portal, is an open
  decision with build consequences on both sides.
- **Target personas are undefined.** The end-to-end experience has not been mapped to who is
  actually doing the work — requester, reviewer, 1LoD/2LoD/3LoD approver, governance analyst.
- **The API handoff is unspecified.** If GbD keeps the front end, the handoff into ACP — what is
  called, when, with what payload, and what comes back — does not exist as a contract.
- **The AI-assisted triage form may need to change.** The intake form and its AI assistance were
  designed against the internal build; the alignment session flagged them as potentially needing
  update, and nobody has yet confirmed what changes.
- **Redundant data entry persists.** The predecessor spec's core complaint stands: teams re-enter
  agent, model and tool metadata that the registries already hold.
- **Assistance has no agreed delivery mechanism on Luminate.** The internal build brokered to an
  externalised agent via `POST /assistant/intake-parse`; Amazon Quick was proposed, then flagged as
  uncertain. Neither has been re-decided for Luminate.

## Opportunity

- **One decision unblocks two teams.** Settling the front door lets GbD build its surface and ACP
  publish its contract, in parallel, without either guessing.
- **Auto-population from the Luminate catalog** — agent, model and MCP metadata already registered
  should pre-fill the form rather than being re-typed.
- **Assistance as an enhancement, not a dependency** — a deterministic-first form that works
  without the assistant, consistent with `governance-intake` NFR-6 ("human-first, then codify").
- **A frontend-agnostic contract** — `governance-intake` FR-1 already requires the flow be drivable
  by any client. Specifying the surface separately proves that requirement rather than asserting it.
- **Reuse of real design work.** The predecessor spec carries 11 sections, 120+ fields, conditional
  logic, the 12-question risk form and the bias assessment. That content is still valid; only its
  host and its assistance mechanism are in question.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| **Duncan Wyllie (GbD)** | Process owner | Whether the GbD UI remains the front door; form logic; intake agents |
| **Kathryn Vandenberg (GbD)** | Governance | Persona definition; consistency across risk domains |
| **Seth Chalmers (ACP Product)** | Implementer | API handoff contract, Luminate integration, registry auto-population |
| **Ryan Bolick (CMRM)** | Model Risk | Risk-scoring methodology and question content stay authoritative |
| **Yassine Ghalem** | Form design | Field definitions, conditional logic, UX |
| **Lalit Summan (ACP PO)** | Product | Sequencing against the mid-October GbD pilot |
| **Risk & Compliance** | Consumers | Scoring accuracy, audit completeness |
| **Enterprise Architecture** | Reviewers | Template standards; integration pattern conformance |

## Scope

### In Scope

| # | Capability | Description |
|---|-----------|-------------|
| 1 | **Front-door decision** | Decide and record whether users stay in the GbD UI or move into ACP/Luminate — an ADR, not a preference |
| 2 | **Persona + journey definition** | Target personas and the end-to-end experience across intake, review and approval |
| 3 | **API handoff contract** | What the front end calls, when, with what payload, and what returns — frontend-agnostic (`governance-intake` FR-1) |
| 4 | **Intake form specification** | Sections, fields and conditional logic, carried forward from the predecessor and re-confirmed against current obligations |
| 5 | **Registry auto-population** | Pre-fill from the Luminate catalog (agents, models, MCP servers) |
| 6 | **AI assistance mechanism** | Decide how assistance is delivered on Luminate; advisory only, with graceful degradation |
| 7 | **Risk + bias assessment surfaces** | The 12-question risk form and bias assessment as UI over the engine's scoring, never re-implementing it |
| 8 | **Artifact upload + evidence linkage** | Supporting documents attached to the use case and linked to the governance record |
| 9 | **Lifecycle + gate feedback** | Surface the resulting band, required gates and lifecycle state back to the user |
| 10 | **Content-pack versioning surfaced** | The user sees which content pack version their assessment was judged against (`governance-intake` FR-16) |

### Out of Scope

- **The risk engine itself** — scoring, bands, obligations, gates, evidence:
  [`governance-intake`](../../governance/governance-intake/d0-discovery.md).
- **Questionnaire and threshold content** —
  [`governance-content-packs`](../../governance/governance-content-packs/d0-discovery.md); CMRM and GbD author it.
- **GbD's assessment module / risk-scoring engine** — GbD's own build; ACP integrates via API.
- **Archer and ServiceNow form design** — consumed via API:
  [`archer-grc-sync`](../../integration/archer-grc-sync/d0-discovery.md).
- **Onboarding GbD's agents onto ACP** —
  [`gbd-acp-integration`](../gbd-acp-integration/d0-discovery.md).
- **Other risk-domain forms** (privacy, ATG) beyond making the shell extensible.
- **Collibra metamodel changes.**

## Success Criteria

- ✅ **Front-door decision recorded** as an ADR with both teams signed up.
- ✅ **Personas and journey documented** end to end.
- ✅ **API handoff contract published** and demonstrably drivable by a client that is not the
  reference UI.
- ✅ **Form specification re-confirmed** against current obligations and content packs.
- ✅ **Auto-population working** from the Luminate catalog for registered assets.
- ✅ **Assistance degrades gracefully** — the form is fully usable with the assistant unavailable.
- ✅ **A submission drives the engine** — band, gates and lifecycle state returned and surfaced.

## Dependencies

| Dependency | Owner | Type | Risk |
|---|---|---|---|
| **Front-door / persona decision** (Duncan, Kathryn, Seth) | GbD + ACP | Hard | **High — everything else waits on it** |
| Intake API contract | [`governance-intake`](../../governance/governance-intake/d3-tasks.md) T1 | Hard | Med |
| Obligation + questionnaire content | [`governance-content-packs`](../../governance/governance-content-packs/d0-discovery.md) | Hard | Med |
| Luminate catalog APIs for auto-population | [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md) (EACPP-596) | Hard | Med |
| Assistance mechanism decision | GbD + ACP | Hard | Med — Quick availability uncertain |
| Form field conditional logic | Yassine | Soft | Low — documented in the predecessor |
| Mid-October GbD pilot | [`gbd-acp-integration`](../gbd-acp-integration/d0-discovery.md) | Soft | Med — pilot may need a usable surface |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Front-door decision keeps slipping** | High | High | Time-boxed dedicated session with a named decision owner; default to "GbD UI stays, ACP exposes APIs" if undecided by the pilot date |
| Two front ends get built | Medium | High | The ADR is a precondition of implementation, not a parallel activity |
| Amazon Quick unavailable in production | Medium | Medium | Assistance is advisory; the form must work without it (`governance-intake` NFR-6) |
| UI re-implements the risk engine | Medium | High | The UI renders and submits; scoring stays in the engine — restated as a constraint in D1 |
| Predecessor form content assumed still valid | Medium | Medium | Re-confirm the field set against current obligations rather than porting blindly |
| Pilot needs a surface before the design lands | Medium | Medium | Pilot may use the existing GbD form with a manual handoff; automation follows |

## Open Questions

- [ ] Does the GbD UI remain the front door, or do users move into Luminate? *(the decision)*
- [ ] If GbD keeps the front end, does ACP still ship a reference UI for non-GbD use cases?
- [ ] How is AI assistance delivered on Luminate — Amazon Quick, an externalised agent behind an
      ACP endpoint, or a Luminate-native capability?
- [ ] Which personas are in the MVP — requester only, or reviewer and approver too?
- [ ] Do other risk domains share the form shell or get separate modules?
- [ ] What conditional logic governs field visibility, and is it still current?
- [ ] Where is form data stored, and what are the residency requirements?

## References

- Parent spec: [`governance-intake`](../../governance/governance-intake/d0-discovery.md) (EACPP-877) —
  [D3 T14](../../governance/governance-intake/d3-tasks.md) books the alignment session that resolves the decision
- Predecessor: `T1KACP/acp-specs/specs/ui-governance-intake` (EACPP-375) — 11 sections, 120+ fields,
  12-question risk form, bias assessment, conditional logic
- Related: [`governance-content-packs`](../../governance/governance-content-packs/d0-discovery.md) ·
  [`archer-grc-sync`](../../integration/archer-grc-sync/d0-discovery.md) ·
  [`gbd-acp-integration`](../gbd-acp-integration/d0-discovery.md) ·
  [`sunlife-deployment`](../../platform/sunlife-deployment/d0-discovery.md)
- Alignment session: [decisions & actions](../../governance/governance-intake/artifacts/2026-08-12-decisions-and-actions.md) ·
  [roadmap & work split](../../governance/governance-intake/artifacts/2026-08-12-governance-alignment-roadmap.md)
