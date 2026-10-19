# Archer GRC Sync — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **D2 Approved**: TBD
> **Epic**: EACPP-1003 · Board label `acp-product-team`

## Overview

Two decisions gate the build rather than any amount of code: how the external identifier is carried
(OQ-A1) and who authors the band (OQ-A3). T1 and T2 exist to close them, and building the field map
before T1 lands would mean rebuilding it.

After that the order is the same as before — everything that does not need Archer access ships
first. T10 is the access request, which runs in parallel and blocks only T11–T12. T13–T14 are Phase 3
and are blocked on Luminate, not on Archer. **T17–T23 are the inbound half**: proposals to Luminate
plus the decisions that must precede them. They are written as "raise it", not "build it", because
Sun Life proposes and the consortium disposes — and because nothing in Phases 0–2 waits on them.

**T24–T30 come out of the 14 September session** and are the use-case roll-up. T24 is the
walk-through and it goes first: it is cheap, it needs nothing running, and it is the thing most
likely to change the shape of T25–T30.

## Tasks

| Task | Description | Depends | Luminate support |
|------|-------------|---------|------------------|
| **T1** | Settle **OQ-A1** — how a high-cardinality Archer identifier is carried: member attribute with one value per resource, an upstream free-form external ref, or an adapter-side mapping table. Record the decision and its cost in D2 DD-4. | — | RG-1 |
| **T2** | Settle **OQ-A3** — the CMRM-approved classification becomes the `risk-band` attribute, and who holds `governance.metadata.update` to author it. Prove the round trip on dev before it is written down as agreed. | — | RG-2 |
| **T3** | Define the **member attributes**: Archer external ref and APM references, on `agent`, `model` and `mcp_server`, with `max_per_entity` set deliberately (APM refs are plural, the Archer ref is not). Create them **through the product's own API**, not the ORM — the band attribute shipped with a key the API would not accept, and every test passed over a path no operator could walk. | T1 | RG-1 |
| **T4** | Build **SyntheticArcher** against the Archer Content API contract, selectable by configuration, persisting what it receives, plus the **shared contract test suite** both it and the real client must pass. (DD-8, Q1) | — | — |
| **T5** | Define **`field-map.yaml`** — published concept → Archer application / level / field ids — validated at startup, no ids in code. (DD-9) | T3, T4 | — |
| **T6** | Implement the **lifecycle projection** as declared configuration: `AgentStatus` × `GovernanceState` → the single Archer field, with `out_of_scope` carried as a distinct reason and `Deployed` deliberately not synthesised. (DD-3) | T5 | RG-3 |
| **T7** | Implement the **durable outbox** — ordered, replayable, circuit breaker, bounded backoff — so an Archer outage delays publication and never fails a governance decision. (DD-7, NFR-3) | T4 | — |
| **T8** | Implement **Phase 1 publication**: read `POST /governance/pack/` and the published `GovernanceStatus`, project, map, and export/attach to the Archer validation record with no Archer API dependency. Carry the pack's own "not a signed evidence pack" disclaimer onto the record. (DD-2, DD-10, FR-6, FR-14) | T6, T7 | — |
| **T9** | Emit an **audit event for every exchange** — attempted / succeeded / failed / conflicted — carrying `version_token`, `generation` and `obligation_revision`. Prove Luminate's governance answer is byte-identical with publication disabled. (DD-11, FR-7, FR-11) | T7 | — |
| **T10** | Produce the **Archer API access-request scoping statement** — minimum object, operations, field set — and name who leads the onboarding conversation. (FR-12, AR-Q1, AR-Q2) | — | — |
| **T11** | Implement the **real Archer client** — Content API, Vault-sourced credentials, passing the same contract suite as SyntheticArcher. (FR-6, Phase 2) | T10 | — |
| **T12** | Constrain the publisher's principal to **`governance.pack.export` plus read**, with **no governance write verb**, and add a test that fails if a write verb is ever granted. Phase-4 inbound capabilities must be **separate principals**; the same test proves the publisher never acquires one. This is DD-1 as a mechanism rather than an intention. | T11 | NFR-7 |
| **T13** | Resolve **producer identity** (OQ-A6): pursue upstream so a service principal may be an `EvidenceProducer`, or run as a named service user in the interim and record the audit consequence. Until this lands, ACP-authored evidence is recorded `unattested` and counts toward nothing. | — | RG-10 |
| **T14** | Submit **ACP-authored evidence** — evaluation outcomes and degradation findings — as `EvidenceRecord`s against the right `control_ref`, and let the platform's own derivation decide compliance. Do not compute a compliance verdict in the adapter. (FR-13, Phase 3) | T13 | RG-9 |
| **T15** | Raise the **capability gaps that are not ours to fix** through the gap-escalation process: per-tool authorization (RG-7), the per-environment `GovernanceStatus` key collision (RG-12), autonomy tier and data residency (RG-5, RG-6). Each is a consortium ask or an accepted limitation, not adapter work. | — | RG-5, RG-6, RG-7, RG-12 |
| **T16** | **Retire the duplicate implementations.** `T1KACP/acp-agent-registry` `registry/archer_sync.py` is wired into `container.py` and live at `POST /governance/archer/sync` against an in-memory client; `EDAEACP/acp-adapter-archer` is the Content API build. Both encode the old internal registry's 14-state lifecycle and a `archer:use_case_id` tag convention that does not exist on Luminate. Keep one, delete the other, and record which. | T6 | RG-3 |
| **T17** | Write up **LC-1** (first-class external governance reference) as a consortium proposal with the RG-1 option costing, and raise it. This is the join key for everything else, so it goes first even though T3 can proceed on the interim. | T1 | RG-1 |
| **T18** | Write up **LC-2** (service principal as `EvidenceProducer`) and raise it. Include the failure mode that makes it urgent: evidence is accepted, marked `unattested`, and counts toward nothing — a `201 Created` that satisfies no control. | T13 | RG-10 |
| **T19** | Write up **LC-3** (authenticated external band assertion carrying source, decision reference and decided-at) and raise it. `obligations.py` already names `_band_for` as the Risk Triage swap point, so this is completing a seam the platform left open, not cutting a new one. | T2 | RG-2 |
| **T20** | Write up **LC-4** (external attribution on a `GovernanceVerdict`) and **LC-5** (capability-scoped external suspension with provenance and audit) and route both through gap escalation. These change the governance model and need a consortium conversation, not a pull request. LC-5 carries the acceptance test from FR-17: a suspended resource is **denied at the gateway**, measured. | T19 | — |
| **T21** | Write up **LC-6** (registration intent an external system of record can file for human approval) and raise it. Records the alternative explicitly — auto-create on approved-record poll, which is what `GenAI_Archer_Requirements_v2` ACP-001 asks for and what both existing implementations do — and why it is refused. | T20 | RG-11 |
| **T22** | Settle **OQ-A7** — the narrowed per-field authority for the four Phase-4 inbound fields, including what happens when the Archer band and the Luminate band disagree. Populate the D2 authority table's conflict column before any of LC-3…LC-6 is built. | T19 | — |
| **T23** | Write down the **interim for OQ-A2**: what a CMRM kill decision does *today*, before LC-5 exists. Today "CMRM decided" and "the gateway denies" are separated by a person remembering to act in a second system; that is a defensible interim and an indefensible surprise. | T2 | — |
| **T24** | **Walk a hypothetical use case end to end** across ACP, Governance by Design and Archer — Ryan's ask in the 14 Sep session, and the agreed next step. Needs no system running; the point is to stress-test the model before anything is built against it. Record where the walk-through stalls. | — | — |
| **T25** | Define the **project metadata contract** (OQ-A10): APM ID, GbD use-case ID, owner, and whatever else the roll-up needs to be answerable. Settle it before T26 builds against it. | T24 | RG-11 |
| **T26** | Build the **use-case view** — composition and governance state of every agent, model and MCP server under a project, published as one surface Governance by Design can read (FR-20, I-2). | T25 | RG-11 |
| **T27** | Hold the **use case inventory ACP-side as the Archer stand-in** (FR-21), keyed so that when API access lands it reconciles rather than rebuilds. | T26 | — |
| **T28** | Implement **divergence detection** (FR-23): surface a resource whose classification falls outside the bounds its use-case classification sets, and route reclassification back to GbD. Depends on OQ-A8 and OQ-A9 being settled. | T26 | RG-2 |
| **T29** | Configure and document the **self-serve bounds** (FR-24) — data classification, MCP server exclusions and regional model approvals. Name which are enforced and which are policy today. Intake is explicitly **not** a bound: prove a team with no use case ID can register and deploy to DEV/SIT (FR-25). | — | RG-6, RG-7 |
| **T30** | Publish ACP controls as **mitigations against an inherent rating** (FR-22), so the CMRM record keeps its inherent basis. Agree the shape with CMRM before publishing anything. | T26 | — |

## Definition of Done

- The external identifier and band questions are **decided and written down**, not deferred into the build.
- The full publication chain is built, tested and demonstrable against SyntheticArcher with no Archer access.
- Luminate produces its governance answer unchanged with publication disabled — proven, not asserted.
- The publisher's principal provably holds no governance write verb.
- Nothing is published to Archer as an enforced control unless a runtime consumer denies on it.
- The compliance pack's own disclaimer survives the trip into Archer.
- One Archer implementation exists, not three.

## What is deliberately not in this plan

- **An evidence store, obligation model or compliance report.** Luminate has all three; building a
  second would create a number Archer holds that Luminate cannot reproduce.
- **A `GRCConnector` implementation.** The consortium protocol (`EACPP-648` T5/T6) was specified for
  the internal build and has no counterpart in Luminate.
- **An adapter-side Archer→Luminate write path.** The bidirectional asks are in scope, but they are
  delivered as contributed, capability-scoped Luminate surfaces (T17–T21), never as the publisher
  reaching into governance state.
- **An Org Plugins host.** The plugin design is in review and not accepted. The publisher runs as a
  Sun Life service against the same public surface and can move into a host later without redesign.

## References

- Spec: [D0](d0-discovery.md) · [D1](d1-requirements.md) · [D2](d2-design.md)
- Luminate governance app — `backend/app/governance/` @ `origin/main` `a0d31c10e`
- Governance Mode D2 §*External governance repositories* — `luminate-designs` @ `013d406`
- `GenAI_Archer_Requirements_v2` §9.3 (ACP-001…013) — the requirements sent to the Archer team
- Repos: `EDAEACP/acp-adapter-archer` · `T1KACP/acp-agent-registry` (`registry/archer_sync.py`)
- Related product specs: [`governance-intake`](../../governance/governance-intake/d0-discovery.md) (EACPP-877) ·
  [`gbd-acp-integration`](../../onboarding/gbd-acp-integration/d0-discovery.md)
- Gap escalation — [`capability-gap-escalation.md`](../../../process/capability-gap-escalation.md)
- Decisions register: [D1, D2, D3, D15; Q1, Q4](../../governance/governance-intake/artifacts/2026-08-12-decisions-and-actions.md)
