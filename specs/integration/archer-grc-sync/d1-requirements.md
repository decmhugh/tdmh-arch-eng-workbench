# Archer GRC Sync — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Verified against**: `luminate` @ `origin/main` `a0d31c10e` · `luminate-designs` @ `origin/main` `013d406` ·
> `luminate-sunlife-deploy` @ `origin/main` · re-verified 9 September 2026.

## 0. What changed: the target is Luminate

The original D0/D1 assumed ACP was a Sun Life build that owned its registries and its evidence
store, and that the Archer work was to package that store and push it. Both halves of that
assumption are now wrong, and in the more useful direction: **Luminate has built most of the
governance machinery this spec was going to specify**, and has already decided where an Archer
integration belongs.

Three findings drive everything below.

### 0.1 Luminate governance is real, and it denies

`backend/app/governance/` is no longer a schema with no consumer. It carries obligation profiles,
a control catalog, an append-only evidence contract, findings, verdicts with separation of duties,
freshness expiry, suspension, material-change detection, legal hold and disposal.

More importantly it reaches the request path. `policy_engine/rego/authz.rego` computes
`governance_denied` from `governance_non_compliant`, `governance_status_stale` and
`governance_status_untrusted`, and every `allow` rule for model, mcp_server and agent now carries
`not governance_denied`. `policy_engine/facts.py::_collect_governance` feeds it only statuses whose
rule has been **promoted to enforce**, so a rule left in `observe` decides exactly as it did before.

This changes what a kill switch *is*. A CMRM decision that lands as `governance_state = suspended`
produces `compliance_state = non_compliant`, which denies at the gateway for any resource under an
enforced rule. That is a real stop control, not a status label — subject to §0.3 on who may set it.

### 0.2 Governance Mode D2 scoped the Archer integration — and this spec extends it

Governance Mode D2 §*External governance repositories* (`luminate-designs`, rev 1.6, 16 Aug 2026)
names Archer specifically, places it **out of core**, and routes it to Org Plugins — which is itself
still in design review (PR #99, not accepted). It sets three constraints:

| Constraint | What it says | Standing |
|---|---|---|
| **External identifier** | Archer's control-domain or model-inventory id is *the member's, not the platform's*. It belongs on the resource as an attribute the member defines, so core never learns the vendor exists. | **Holds.** RG-1 works inside it. |
| **Direction** | *One-way out of the platform.* "An external inventory that could write back into scope, band or verdict would put the deciding record outside the system that has to fail closed." | **Extended** — see §2. The reasoning holds; the conclusion was scoped tighter than it needs to be. |
| **Boundary** | The sync holds `governance.pack.export` — the same verb a person holds — rather than opening a second, unaudited path out. | **Holds**, and generalises: an inbound path must likewise hold a named verb, not a private channel. |

That design is this spec owner's own, written when Governance Mode had no inbound story at all and
one-way was the safe default rather than a considered position on external systems of record. It is
not an external ruling to work around, and it is not frozen. What it got right is the *reason*: the
deciding record has to stay inside the system that fails closed. What it left unbuilt is the
legitimate case underneath `GenAI_Archer_Requirements_v2` §9.3 — an enterprise GRC system where a
named human makes a classification and a kill decision that Luminate then has to honour.

**So the v2 bidirectional asks stay in scope.** ACP-001 (approved Archer record drives registration)
and ACP-004 (Archer kill switch cascades) are not refused; they become **named Luminate
contributions** (LC-1…LC-6, §2), because the surfaces they need do not exist upstream yet. That is a
roadmap item, not a rejection — and it is the honest description, since Sun Life owns the design that
would have to change.

### 0.3 The adapter cannot currently be an evidence producer

`EvidenceProducer.principal` is a `OneToOneField` to `AUTH_USER_MODEL`, and
`register_evidence_producer` imports `app.iam.models.User`. Machine callers authenticate as
`AuthenticatedServicePrincipal`, which is documented as deliberately **not** a Django `User`
("without turning the `ServicePrincipal` into a Django `User`").

A machine principal therefore cannot be registered as a producer at all. Evidence it submits is
still accepted — the ingest boundary records rather than refuses, on purpose — but it is marked
`unattested` and **never counts toward a control**. The failure mode is silence: `201 Created`, and
a control that stays unsatisfied.

Compounding it, `SERVICE_PRINCIPAL_AUTH_ENABLED` is `"false"` in **all four** SLF values files
(dev, test, stage, prod), so machine authentication is wired but off today regardless.

### 0.4 What the 14 September session changed

Four decisions from the Archer × ACP × GbD working session, 14 September 2026 (transcript in `references/`), each of which moves
something this spec previously assumed.

**The flow splits by environment.** The single intake-to-production lifecycle is the **STAGE and
PROD** path. DEV and SIT are a self-serve path where governance observes. This is the largest
change and it is the one the architecture overview is built around.

**Governance by Design integrates with ACP, not with Archer.** Raised by Duncan Wyllie and agreed:
GbD has not started an Archer integration, ACP already owns one, and ACP is where the agent-level
detail is aggregated. So **ACP is the single integration point to Archer**, and the two direct
GbD → Archer arrows come out of the flow. This supersedes the INT-001…011 register in the previous
revision.

**A Luminate project is an AI use case, and ACP holds the use case inventory.** Ryan Bolick asked
whether ACP could carry a use case inventory as a stand-in while Archer access is unavailable;
Duncan supported it as the reason to integrate with ACP in the first place. The project already
groups the agents, models and MCP servers that a use case comprises, so the roll-up has somewhere
to live. The project carries the **APM ID** — the identifier already common to GbD, service
management, risk and architecture — as the join key.

**Model risk stays on an inherent basis.** Kalyan Adhikari's point that onboarding to ACP confers
governance, oversight and observability that could be templated as controls was accepted, with
Ryan's qualification: CMRM tracks **inherent** risk and records controls as separate mitigations.
So ACP's controls are published as mitigations against the inherent rating, never netted off it.

One boundary was sharpened rather than added: **intake is not a prerequisite for DEV or SIT.** A
team that has already been through Governance by Design intake — which is the current state today —
carries its use case ID in from the start, and that is welcome. A team that has not can still
register and work in the lower environments. The use-case intake and its ID become **required at the
promotion gate**, not before it. Requiring intake up front would reintroduce exactly the wait the
self-serve path exists to remove.

## 1. Phasing

| Phase | Trigger | Capability | Blocked on Archer access? |
|---|---|---|---|
| **0** | Now | External-identifier attributes; synthetic Archer; export→Archer field map exercised end to end | No |
| **1** | Now | One-way publication: compliance pack + governance status → Archer, by export/attach | No |
| **2** | Archer API access granted | The same publication over the Archer API instead of a file | Yes — deliberately |
| **3** | LC-2 accepted | ACP-authored evidence that actually counts toward a control | Yes — on Luminate, not on Archer |
| **4** | LC-3…LC-6 accepted | The inbound half: band assertion, external verdict attribution, suspension signal, registration intent | Yes — on Luminate |

Phases 0–2 are unchanged in intent from the original D1 and gate on nothing upstream. Phases 3 and 4
are where the bidirectional asks live, and they are honest about what they wait on: Luminate
contributions (§2), not Archer access.

## 2. Direction: bidirectional, with the deciding record still inside Luminate

The v2 requirements document asks for bidirectional sync and this spec keeps it. What it does not do
is deliver the inbound half by letting an adapter reach into governance tables — that is the failure
Governance Mode D2 was written to prevent, and it stays prevented.

**The invariant.** An inbound Archer fact enters as an *authored input carrying external provenance*,
through a capability-scoped, audited Luminate surface. Luminate still derives scope, obligations and
compliance state from its own inputs. Archer supplies premises; Luminate draws the conclusion.

That keeps the fail-closed property intact — Luminate never learns a verdict it cannot recompute —
while making the CMRM decision consequential rather than advisory. The cost is honest: most of the
inbound surfaces do not exist upstream today, so they are Sun Life contributions to Luminate, listed
below and sequenced in Phase 4.

| v2 ask | Direction | How it is satisfied | Needs |
|---|---|---|---|
| **ACP-002/003** — Agent IDs and lifecycle state written to Archer | Outbound | Direct. Read `governance_state` and the published `GovernanceStatus`; write Archer. | — ships today |
| **ACP-005** — evaluation evidence to Archer | Outbound | Direct, once §0.3 is resolved on the producing side. | LC-2 |
| **ACP-009** — Archer exposes the approved risk tier | Inbound, **already anticipated** | The band. `obligations.py` states it "will come from Risk Triage" and names `_band_for` as the swap point. Formalising that seam as an authenticated assertion is the smallest inbound contribution. | LC-3 |
| **ACP-003 (inbound)** — CMRM approval recorded against the resource | Inbound | A `GovernanceVerdict` that records the external approver and the Archer decision reference, so separation of duties is evaluated against the *human who actually approved* rather than the adapter. | LC-4 |
| **ACP-004** — Archer kill switch cascades to agents | Inbound | A capability-scoped transition to `governance_state = suspended` with actor provenance and an audit entry. Because `authz.rego` already denies on `suspended` under an enforced rule, this is a real stop control the moment it lands. | LC-5 |
| **ACP-001** — approved Archer use case drives agent registration | Inbound | **Correlate by default; register by request.** The Archer use case resolves to agents that already exist via the external identifier. Where CMRM genuinely originates the asset, Archer files a *registration intent* that a Luminate-side human approves — never a silent create. | LC-1, LC-6 |

### Luminate contributions this spec depends on

| # | Contribution | Why it is not adapter work | Blocks |
|---|---|---|---|
| **LC-1** | A first-class **external governance reference** on a resource — opaque, vendor-neutral, high-cardinality — so an Archer id does not have to be smuggled through the attribute vocabulary (RG-1). | Attributes are a controlled vocabulary by design; correlation ids break that. | Everything — it is the join key |
| **LC-2** | Allow an authenticated **machine principal to be an `EvidenceProducer`** (RG-10). | `EvidenceProducer.principal` is a `OneToOne` to `AUTH_USER_MODEL`; a service principal is deliberately not a `User`. Cannot be worked around downstream. | ACP-005, Phase 3 |
| **LC-3** | An authenticated **external band assertion** — the Risk Triage seam `obligations.py` already names — carrying source system, decision reference and decided-at. | `_band_for` is a documented swap point with nothing on the other side of it. | ACP-009, obligations |
| **LC-4** | **External attribution on a `GovernanceVerdict`** — approver identity, external decision reference — so an Archer approval is recorded as that human's, and self-approval checks still mean something. | SoD is currently evaluated against a Luminate `User`; an adapter-authored verdict would launder the approver. | ACP-003 inbound |
| **LC-5** | A capability-scoped **external suspension signal** with provenance and audit. | There is no verb for it. Today a CMRM kill relies on a human remembering to act in a second system. | ACP-004 |
| **LC-6** | A **registration-intent** object an external system of record can file for human approval. | Registration is a first-class authorized action; auto-create from an external poll is the exact anti-pattern. | ACP-001 |

LC-1, LC-2 and LC-3 are the ones with a near-term claim: each closes a gap the platform itself
already documents. LC-4, LC-5 and LC-6 change the governance model and want a consortium
conversation, not a pull request — route them through
[capability-gap-escalation](../../../process/capability-gap-escalation.md).

None of them gates Phases 0–2. Publication ships one-way while the inbound half is being agreed, so
the integration is useful before the contributions land.

## 3. Registry content gaps

What an Archer AI Use Case record needs, against what a Luminate resource actually carries.

Luminate's `Agent` (`backend/app/agents/models.py`) carries `key`, `name`, `description`, `status`
(`active|inactive|deprecated|unknown`), `governance_state`, `governance_state_reason`, `type`,
`framework`, `deployment_type`, `project`, `scope_tokens`, `configuration`, `created_by`.
`MCPServer` and `Model` carry `governance_state` on the same pattern.

| # | Archer needs | Luminate today | Gap | Severity |
|---|---|---|---|---|
| **RG-1** | An **external identifier** per resource — Archer use-case / control-domain id, plus APM refs (D15) | Attributes reach `agent`, `model`, `mcp_server`, `project`. `validate_attribute_value` permits colons, so `archer:UC-12345` is a legal token | The attribute system is a **controlled vocabulary**: `AttributeDefinition` → `AttributeValue` → `EntityAttribute`. A per-resource unique id needs one `AttributeValue` row per resource, so the vocabulary grows unbounded — it is built for enumerable dimensions (environment, location, band), not correlation ids | **High** — settle the shape before any mapping is built |
| **RG-2** | **Approved risk classification** driving obligations | `risk-band` governance-authoritative attribute; `ObligationProfile` keyed `(framework_ref, band)`; `_band_for` is the documented swap point for Risk Triage | No ingestion path from an external triage decision. `BandNotResolvable` resolves `indeterminate`, which **denies** — a resource brought into scope with no band is stopped, not merely unassessed | **High** — the biggest gap and the sanctioned inbound seam at once |
| **RG-3** | **Agent lifecycle state** (UC-012: registered, evaluating, approved, deployed, active, suspended, decommissioned) | Two axes: `AgentStatus` (4 operational values) and `GovernanceState` (7: `not_evaluated`, `out_of_scope`, `in_scope_unassessed`, `assessed`, `approved`, `suspended`, `retired`) | No single field maps to UC-012. The v2 vocabulary conflates operational and governance state; Luminate separates them deliberately. Needs a declared two-axis projection — and `deployed` has no resource-level equivalent, it is a property of a `Deployment` | **Medium** — a mapping, not a build |
| **RG-4** | **Owner / accountable executive** | `created_by` only | No accountable-owner field. `GovernanceVerdict` refuses self-approval by comparing `resource_owner`, so an owner concept exists at verdict time but is not carried on the resource | **Medium** |
| **RG-5** | **Autonomy tier** (UC-016, SDLC and enterprise frameworks) | Nothing — `autonomy` appears nowhere in the backend | Absent. Would be a member attribute | **Medium** |
| **RG-6** | **Data residency / region** (UC-014) | Nothing on the resource. Governance Mode D2 records `region` as declared in the per-request schema but **not populated** — the gateway does not track it | Absent, and known-absent upstream | **Low** for publication; **High** if an obligation ever depends on it |
| **RG-7** | **MCP tool bindings** — which tools an agent may use (ACP-011) | `AccessPolicy.allowed_tool_ids` exists on model, serializer and demo data. `AccessPolicyTargetType` = `mcp_server, agent, model, location, environment` — none is a tool. The only `tool` in `authz.rego` is a comment | **Per-tool authorization does not exist.** Publishing `allowed_tool_ids` to Archer would report a control that is not enforced. Server-level binding is the honest unit | **High** — a correctness trap, not a missing field |
| **RG-8** | **Model bindings** (ACP-012) | `AccessPolicy` with `target_type=model`, enforced in `authz.rego` via `allowed_models` | No gap. Publish these | — |
| **RG-9** | **Evaluation scores / degradation events** (MET-010…012, ACP-005) | `EvidenceRecord` with `control_ref`, `result`, `observed_at`, `trust_tier`, `covered_sections`, append-only by DB trigger (migration `0008`); `GovernanceFinding` with severity and state | The *store* exists and is better than what this spec proposed. Missing: a **producer identity for ACP** (§0.3), and any evaluation subsystem generating the scores | **High** — blocked on RG-10 |
| **RG-10** | An **authenticated machine producer** for ACP-authored evidence | `EvidenceProducer.principal` → `AUTH_USER_MODEL`; service principals are deliberately not `User`s; `SERVICE_PRINCIPAL_AUTH_ENABLED=false` in all four SLF envs | Machine evidence is accepted, marked `unattested`, and never counts — silently | **Blocker** for Phase 3 |
| **RG-11** | **Use case → agents** as a first-class 1:N relationship | `Project` groups resources; `scope_tokens` materialize the hierarchy | A project is the closest construct but it is ownership/visibility, not a governance use case. Whether an Archer use case maps to a project or an attribute-tagged set is undecided; v2 OQ-012 (1:N vs M:N) is still open | **Medium** |
| **RG-12** | Per-environment governance answers | `GovernanceStatus` is unique per resource **per environment** | `_collect_governance` keys the rego input on `entity_type:entity_id` only, so two environments' rows collide and whichever the queryset yields last wins. Documented in code as a known gap with a non-trivial fix | **Medium** — affects what a published status means |

### What is *not* a gap

Worth stating, because the previous D1 planned to build all of it:

- **Evidence store** — exists, append-only, with trust tiers, freshness horizons and supersession.
- **Obligation model** — `ObligationProfile` carries required controls, human-only controls, approval
  depth, freshness, retention, cadence, capture policy, and a `revision` bound into the version token
  so a text change cannot silently re-bless a resource.
- **Evidence packaging / report** — `POST /api/v1/governance/pack/`. Its own docstring is careful that
  it is **not** the signed evidence pack (that lives in Compliance Reporting, D1 with no build) and it
  says so in its own payload. Do not present it to CMRM as a signed artifact.
- **Reproducibility** — `version_token`, `input_digest`, `obligation_revision`, `evidence_digest` and
  `generation` on every published status. The old FR-11 is already satisfied by the platform.
- **Audit trail** — `governance/audit.py`; the verdict path records actor and reason.

## 4. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | No adapter write may set scope, band, verdict or governance state **as derived state**. Inbound facts enter only through a capability-scoped, audited Luminate surface carrying external provenance (§2). | Must |
| FR-2 | Carry the **Archer external identifier and APM references** on the resource as member-defined attributes, resolving RG-1's cardinality question first. | Must |
| FR-3 | Publish from the **platform's own surfaces** — `governance/pack/`, the published `GovernanceStatus`, the audit trail — not from a second query path over the same data. | Must |
| FR-4 | Hold the **Archer field map as configuration**; no vendor field ids, application ids or level ids in code. | Must |
| FR-5 | Provide a **synthetic Archer** implementing the same contract, selectable by configuration, so the chain is testable before access exists (Q1). | Must |
| FR-6 | Publish by **export/attach with no Archer API dependency** in Phase 1 and over the API in Phase 2, with the same field map and the same contract tests. | Must |
| FR-7 | Luminate must produce its governance answer with the Archer publication **disabled**; a publication failure degrades publication only (D2). | Must |
| FR-8 | Define the **two-axis lifecycle projection** (RG-3) — `AgentStatus` × `GovernanceState` → the single Archer lifecycle field — as declared configuration, not inline logic. | Must |
| FR-9 | Establish the **band ingestion path** from the CMRM-approved classification to the `risk-band` attribute (RG-2), authored under `governance.metadata.update` by an authorized actor. | Must |
| FR-10 | Publish **model bindings** (RG-8) and **server-level MCP bindings**; do **not** publish `allowed_tool_ids` as an enforced control (RG-7). | Must |
| FR-11 | Emit an **audit event for every Archer exchange** — attempted, succeeded, failed, conflicted — carrying the `version_token` of the status published. | Must |
| FR-12 | Produce the **Archer API access-request scoping statement**: minimum object, operations and field set (AR-Q2). | Must |
| FR-13 | Register ACP as an **authenticated evidence producer** and submit ACP-authored evidence that counts (RG-9, RG-10). | Should — Phase 3 |
| FR-14 | Label every published artifact with **what it is not**: the compliance pack disclaims being a signed evidence pack in its own payload. Do not strip that on the way to Archer. | Must |
| FR-15 | Deliver the **inbound half as Luminate contributions** LC-1…LC-6 (§2), each raised through the gap-escalation process with a named owner — not as adapter-side writes. | Must |
| FR-16 | Every inbound fact carries **external provenance**: source system, external decision reference, the human who decided it, and decided-at. A fact that cannot name its decider is not accepted. | Must — Phase 4 |
| FR-17 | A CMRM **stop decision must reach the access layer**, not just a field. Whichever mechanism LC-5 settles on, the acceptance test is that a suspended resource is denied at the gateway — measured, not asserted. | Must — Phase 4 |
| FR-18 | Governance by Design integrates with **ACP**, and ACP owns the **single** Archer integration point (§0.4). No second path from GbD to Archer. | Must |
| FR-19 | A Luminate **project represents an AI use case** and carries the **APM ID** and the GbD use-case ID, so ACP, GbD, service management, risk and architecture join on identifiers that already exist. | Must |
| FR-20 | ACP must publish a **use-case view** — the composition and governance state of every agent, model and MCP server under the project — that Governance by Design can read without querying resource by resource. | Must |
| FR-21 | ACP must hold the **use case inventory as a stand-in for Archer** while API access is unavailable, keyed so it reconciles rather than rebuilds when the sync lands. | Must |
| FR-22 | Publish ACP's governance controls as **mitigations against an inherent rating**, never netted off it, so the CMRM record stays on an inherent basis. | Must |
| FR-23 | Make **divergence detectable**: where a resource's classification falls outside the bounds set by its use-case classification, that must surface rather than be inferred. Reclassification routes back through GbD. | Must |
| FR-24 | The **self-serve path is bounded** — synthetic and non-sensitive data, no high-risk MCP servers, and regional model approvals still apply. Governance by Design intake is **not** among these bounds; it is required at the promotion gate (FR-25). | Must |
| FR-25 | **Intake is required at the promotion gate, not before it.** A use case ID supplied earlier is carried; its absence must not block registration or a DEV/SIT deployment. | Must |

## 5. Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **Archer is never on the critical path.** No Luminate capability may hard-depend on Archer availability or onboarding. | Must |
| NFR-2 | **Publish, do not fork.** Luminate does not mirror the Archer risk register; Archer does not become the deciding record. | Must |
| NFR-3 | **Resilient** — circuit breaker, bounded retry with backoff, durable outbox, so an Archer outage delays publication without losing it. | Must |
| NFR-4 | **Publish by reference** where a reference suffices; copy only what the Archer record must physically hold (Q3). | Must |
| NFR-5 | **Credentials from Vault**, never in configuration or code. | Must |
| NFR-6 | The synthetic target must be **contract-identical** to the real one, or it validates nothing. | Must |
| NFR-7 | The publisher holds **`governance.pack.export`** and read access and no broader verb. Inbound capabilities (Phase 4) are **separate principals with separate verbs** — the publisher never gains a write path. | Must |
| NFR-8 | A published artifact must be **traceable to the platform state it was built from** — `version_token`, `generation`, `obligation_revision`, `evidence_digest` — so a reader can tell whether it still describes reality. | Must |

## 6. Constraints & Assumptions

- **Org Plugins is not accepted.** Governance Mode D2 routes the Archer sync there but records it as a
  direction rather than a dependency. Sun Life must not block on PR #99: the adapter can run as a Sun
  Life service consuming the same public surface, and move into a plugin host later.
- **LC-1…LC-6 are proposals, not commitments.** Sun Life owns the Governance Mode design and can
  propose the change, but the consortium decides. Phases 0–2 are therefore built to be useful with
  none of them accepted, and every phase-4 requirement is written so that its absence degrades the
  integration rather than breaking it.
- **The compliance pack is not the signed evidence pack.** Compliance Reporting has a D1 and no build.
  If CMRM requires a signed, immutable artifact, that is a gap in Luminate — escalate it as a
  consortium ask rather than forging one locally.
- **`governance.pack.export` is organization-scoped.** Whether Sun Life is comfortable with the
  adapter's principal holding a bulk-export capability is a security review item, not an assumption.
- Archer API access is still not requested; AR-Q1 (who leads it) remains the largest schedule risk.
- The member attributes this spec adds (RG-1, RG-4, RG-5) are member-defined by design and need no
  consortium agreement.

## 7. Open Questions

Carried from D0: AR-Q1 (onboarding lead), AR-Q2 (minimum object), AR-Q4 (ongoing monitoring),
AR-Q5 (APM origin), AR-Q6 (retention / tamper-evidence).

AR-Q3 (per-field authority) **returns**, narrowed. It no longer covers every field — outbound fields
have one authority, Luminate. It covers the handful of fields Phase 4 lets Archer drive: band,
verdict attribution, suspension, registration intent. Those need a declared authority and a declared
conflict rule before LC-3…LC-6 are built, not after.

| # | Question | Owner |
|---|---|---|
| **OQ-A1** | How is a high-cardinality external identifier carried (RG-1)? A member attribute with one value row per resource, an upstream free-form external ref (LC-1), or a mapping table held by the adapter? | Seth, Luminate Squad 6 |
| **OQ-A2** | What does a CMRM kill decision do **before LC-5 exists**? An authorized human suspends in Luminate on the strength of it, or ACP raises a `GovernanceFinding` for a human to act on. One of these is the interim and it should be written down, because "CMRM decided" and "the gateway denies" are currently separated by a person's memory. | Ryan, Seth |
| **OQ-A3** | Does the CMRM-approved classification become the `risk-band` attribute directly, and who is authorized to author it (`governance.metadata.update`)? | Ryan, Kathryn, Seth |
| **OQ-A4** | Does an Archer AI Use Case map to a Luminate **project**, or to an attribute-tagged set of resources (RG-11, v2 OQ-012)? | Ryan, Seth |
| **OQ-A5** | Does CMRM accept the compliance pack — which explicitly disclaims being a signed evidence pack — as the validation artifact, or is Compliance Reporting a hard dependency? | Ryan |
| **OQ-A6** | Producer identity (RG-10): pursue upstream so a service principal may be an evidence producer, or run the adapter as a named service **user** in the interim and accept the audit consequence? | Seth, Luminate Squad 6 |
| **OQ-A7** | On the Phase-4 inbound fields, which side wins on divergence — and what happens to a resource whose Archer band and Luminate band disagree? (AR-Q3, narrowed) | Ryan, Seth |
| **OQ-A8** | Can the **same risk classification questionnaire** serve both the use case and the agent, or does the agent level need a tweaked instrument? Overlapping subjects, different granularity. | Ryan, Seth |
| **OQ-A9** | When an agent's classification diverges from its use case, is the **use case reclassified first**, or does the agent rating inform an updated use-case rating? | Ryan, Robert |
| **OQ-A10** | What **project-level metadata is mandatory** for the roll-up to be answerable — APM ID, GbD use-case ID, owner, and what else? | Kalyan, Duncan, Seth |
| **OQ-A11** | Does ACP become the front door for **non-agentic GenAI** as well? Models and apps already follow the same registry and promotion path; where "agent" ends is an open architecture question. | Robert, Ryan, ACP EA |

## 8. References

- Luminate governance app — `backend/app/governance/` @ `origin/main` `a0d31c10e`
- Governance denial — `backend/app/policy_engine/rego/authz.rego`; `policy_engine/facts.py::_collect_governance`
- Band resolution — `backend/app/governance/obligations.py` (`RISK_BAND_ATTRIBUTE`, `_band_for`, `BandNotResolvable`)
- Evidence contract — `backend/app/governance/models.py` (`EvidenceRecord`, `EvidenceProducer`); migration `0008_evidence_append_only_trigger`
- Governance Mode D2 §*External governance repositories* — `luminate-designs` @ `013d406`
- `GenAI_Archer_Requirements_v2` §9.3 (ACP-001…013), UC-011…016, MET-010…012, OQ-011…015
- Existing adapter — `EDAEACP/acp-adapter-archer`; superseded registry sync — `T1KACP/acp-agent-registry` `registry/archer_sync.py`
- Capability map — [`capability-map.md`](../../../capability-map.md)
