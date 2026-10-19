# Governance Intake & Risk Classification (Sun Life) — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Amended** after the [12 August 2026 alignment session](artifacts/2026-08-12-decisions-and-actions.md) —
> FR-11 to FR-16 and the terminology note below carry decisions D4, D7, D8, D14, D15 and Q3.
> **Amended again** 9 September 2026 — FR-17 to FR-23 and NFR-9 carry the
> [Luminate integration review](artifacts/2026-09-09-luminate-band-integration-review.md),
> verified against `luminate` `origin/main` `a0d31c10e` rather than the design branches.
> **Amended again** 14 September 2026 — FR-24 to FR-30 and NFR-10 carry the Archer × ACP × GbD
> working session. See [Architecture Overview](d2-architecture-overview.md).
> **Amended again** 15 September 2026 — FR-31 to FR-38 carry the
> [risk classification module workshop](references/2026-09-15-risk-classification-module-workshop.docx):
> multiple risk domains, continuous retrieval for monitoring, evaluations feeding likelihood, and
> risk acceptance. RC-Q1 is answered; RC-Q10 to RC-Q14 are new.

## Terminology — "policies" are "obligations" (D4)

Ryan Bolick asked in session that the CMRM validation requirements be called **obligations**, not
policies, because "policy" already names one of six Sun Life corporate policies. Throughout this
spec and its downstream schema, **obligation** means a checkable governance requirement, and
**policy** is reserved for access / gateway enforcement policy, where the word is genuinely correct.
The obligation schema is domain-agnostic — privacy and other risk domains author against the same
convention (D5).

**"Classification" and "tiering" are not synonyms, and the distinction was settled in the 15 Sep
workshop.** *Classification* is the rule-based computation — an instrument, a set of rules, and
inputs. *Tier* or *band* is its published output. One is the process, the other is the result, and
the ambiguity matters because the enterprise tiering instrument and this module are being aligned
to a single vocabulary. This spec uses **band** for the output throughout; where an existing
process says "tier", it means the same thing.

## Capability Matrix (Legacy internal MVP vs Luminate target)

| Capability | Legacy internal (EACPP-21) | Luminate target (this spec) | Approach |
|---|---|---|---|
| Intake form | Manual / ad-hoc | Amazon Quick → Luminate/ACP APIs | Rebuild UX on Luminate |
| Risk classification | Client-side 12-Q engine (`riskClassification.js`) | Consortium `governance-risk-triage` engine, seeded w/ CMRM Field Guide | **Consume generic engine** |
| Band ↔ tier | Ad-hoc | Configured Sun Life band↔tier map | Config |
| Validation requirements | Spec + CEL templates | CMRM policies list bound as per-band gates | Config/seed |
| Required evaluations | Not tiered | Sun Life eval metric guide over `model-agent-evaluation` | Config |
| Policy content | Encoded in code | CMRM per-policy YAML ingested into `regulatory-reporting` registry | Seed data |
| Archer / ServiceNow | Adapter (mocked) | Bi-directional Archer sync + ServiceNow routing | SLF adapter |
| Lifecycle drive | Internal registries | Luminate Agent/Model/MCP registries | Integrate |
| Audit / evidence | Governance API | Luminate `audit_events` + `regulatory-reporting` evidence packages | Consume |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Provide an **intake flow** whose API contract is **drivable by any frontend** — ACP owns logic and storage, the UX layer is interchangeable. The **surface** that consumes this contract (front door, personas, form, assistance) is specified in [`governance-intake-ui`](../../onboarding/governance-intake-ui/d0-discovery.md); this spec owns only the contract. | Must |
| FR-2 | **Adopt the consortium risk-triage engine** (`governance-risk-triage`) and **seed it with the CMRM GenAI Model Risk Classification Field Guide** (questions, MAX/AVG scoring, matrix). No Sun Life risk engine is built here. | Must |
| FR-3 | Define the **band ↔ Sun Life Model Risk tier** mapping as configuration. | Must |
| FR-4 | Bind the **CMRM validation-requirement policies** as **per-band gates** (validations / PIA / ISRA / ATG / MRM review) with 1LoD/2LoD/3LoD sign-off; ingest CMRM's **per-policy YAML** into the `regulatory-reporting` policy/framework registry. | Must |
| FR-5 | Define the **evaluation metric guide** — required eval suites/scorers/thresholds **per risk band** — as configuration over `model-agent-evaluation`, enforced before APPROVED/ACTIVE. | Must |
| FR-6 | **Drive the Luminate registry lifecycle**: risk band determines auto-approve (below band), require-review / escalate (above), and gated deployment; wire to Agent/Model/MCP registries. | Must |
| FR-7 | **Archer bi-directional sync** (GRC system-of-record): ACP risk tier/lifecycle ↔ Archer risk record. | Should |
| FR-8 | **ServiceNow routing**: create PIA/ISRA/ATG work items from intake output. | Should |
| FR-9 | Produce **audit-ready evidence** per agent/model via `regulatory-reporting` evidence packages (OSFI E-23 / B-13 / NIST). | Should |
| FR-10 | Support **discovered-agent auto-triage** (auto-run the intake risk classification on discovery). | Could |
| FR-11 | Scope the **ACP-produced report to OSFI E-23**, per agent/model. Broader OSFI **technology-risk** reporting is produced by Governance-by-Design per application/use case. The boundary is stated in writing before either report is built, so two teams do not report the same control from different systems. (D7) | Must |
| FR-12 | Expose ACP governance data as a **documented, stable read interface** — a data product GbD consumes to aggregate across the lifecycle. The contract is published before GbD builds against it. (D8) | Must |
| FR-13 | Support **three distinct layers of evaluation and observability**: (a) registration/onboarding — assess risk, determine and run required evaluations; (b) **scheduled** re-evaluation at a risk-driven cadence; (c) **per-inference retrieval** — reconstruct a single execution end-to-end on demand (*"why was I denied?"*). Layers (a) and (b) are aggregated and reported; layer (c) remains in operational observability but must be retrievable. (D14) | Must |
| FR-14 | Carry **APM references** captured at GbD intake through the registry record, so technology dependencies tie to Archer use cases without inventing a platform-level Archer record type. (D15) | Should |
| FR-15 | Do **not duplicate evaluation artifacts**. Data may remain in workload accounts; the canonical *record* returns to ACP. Reference by default; copy only what a report or an Archer validation record must physically contain. (Q3, D1) | Must |
| FR-16 | Every approval, gate decision and evidence record carries the **governance content pack version** it was judged against, so a past decision is reproducible after thresholds or obligations change. (`governance-content-packs` FR-10) | Must |
| FR-17 | **Publish the risk band into Luminate** as the governance-authoritative `risk-band` attribute against `(entity_type, entity_id)`. Luminate's obligation resolution raises `BandNotResolvable` for a governed resource carrying no band, so Governance Mode is blocked closed until ACP publishes one. ACP is the band producer of record. (LB-1) | Must |
| FR-18 | **Seed the `risk-band` attribute** as deployment configuration — definition marked governance-authoritative, `max_per_entity = 1`, applicability for `agent`, `model`, `mcp_server` and `deployment`, and one curated value per band. Nothing in Luminate seeds it today. (LB-2) | Must |
| FR-19 | **Carry the content pack revision to Luminate** alongside the band, so FR-16 holds on the platform side and not only in the ACP store. A Luminate-side audit must be able to answer *"judged against what?"* without calling ACP. (LB-3) | Must |
| FR-20 | **Collect the agentic attributes at intake** — data reach, autonomy, regulatory scope, credentials, and for MCP servers the data classification and PII/PCI/government-data flags. Luminate models none of these, so they cannot be derived from the registry and must be captured. (LB-4) | Must |
| FR-21 | **Define the (re)classification trigger.** Luminate emits no outbound events of any kind, so nothing signals registration or material change. State whether ACP polls, the intake flow pushes, or a scheduled sweep reconciles — and what happens to a resource registered outside the intake flow. (LB-5) | Must |
| FR-22 | **Write the band under a dedicated least-privilege principal** scoped to the `risk-band` dimension. The write needs superuser or `governance.metadata.update`, which Luminate deliberately withholds from Administrator so that whoever can edit a resource cannot re-tag it out of scope. (LB-6) | Must |
| FR-23 | **Publish the risk-classification API on the Sun Life API Platform**, as its own app with its own Okta authorization server, audience and scopes — the pattern every other ACP API follows. This requires the service to verify **Okta JWTs** rather than the static bearer tokens it accepts today, and requires a **tenant claim** in the token, because tenancy is taken from the credential rather than the request. | Must |
| FR-24 | **Classify the AI use case**, anchored on a **Luminate project**. The project carries the use-case band, the APM id and the GbD / GCP id, so the roll-up has a concrete subject rather than a new entity. (RC-1) | Must |
| FR-25 | **Treat the use-case band as a ceiling, not an aggregate.** A resource band is **checked against** the use-case band; it is not summed, averaged or maxed into it. The use-case band is set independently from impact by Governance by Design. (RC-2) | Must |
| FR-26 | **Detect divergence continuously.** When an agent, model or MCP server classifies **above** its use case's ceiling, raise a finding. Classification is not a one-time gate — a resource that grows past what its use case was assessed for must be identifiable without anyone going looking. (RC-3) | Must |
| FR-27 | **Do not re-classify in ACP.** ACP raises the divergence; the re-classification decision belongs to Governance by Design. (RC-4) | Must |
| FR-28 | **Score inherent risk, and carry controls separately.** The band is produced from what a resource could do, independent of the controls around it; registration, ownership, inbound authentication, human review, evaluations and guardrails are tracked as **mitigations against the obligations the band demands**, never netted off the band itself. (RC-5) | Must |
| FR-29 | **Carry the environment on a band.** Classification runs in every environment from the start, but only enforces above SIT — DEV and SIT observe, the promotion gate into STAGE is where intake, approval and obligations bind. (RC-6) | Must |
| FR-30 | **Export a use-case risk classification pack at the promotion gate**, and use it to **pre-populate the governance intake form**. By promotion the control plane already holds the inventory of every agent, model and MCP server in the use case, each one's band, and the evidence behind it. Intake therefore starts from what was observed in the lower environments rather than from memory: the reviewer attests rather than re-enters, and the use-case classification is grounded in what is actually deployed. (RC-8) | Must |
| FR-31 | **Carry a classification per risk domain, and keep each one independently recalculable.** Model risk is one domain; privacy, information security and TPRM each run their own instrument, on their own scale, and those scales bear little resemblance to one another. Each domain must be able to reach its own questions and recompute its own result without the composite being unpicked. A single collapsed number that cannot be decomposed back into the domain that produced it does not meet this. (RC-9) | Must |
| FR-32 | **Surface a domain conflict rather than resolving it silently.** Two domains assessing the same resource may disagree, and the disagreement is the signal — taking the higher and discarding the other hides exactly the case that needs a human. The composite band still has to be produced, because obligations must resolve; the dissent has to remain visible beside it. (RC-10) | Must |
| FR-33 | **Expose the risk profile for continuous retrieval, not only at the gate.** Governance by Design monitors across the whole lifecycle and aggregates risk profiles for second line, so the platform must support being **pulled from** — current state and change over time, per resource and per use case — and must support **portfolio aggregation** so the organisation can read its position against risk appetite. Publishing only at promotion satisfies the gate and starves the monitoring layer. (RC-11) | Must |
| FR-34 | **Feed evaluation results into the likelihood axis.** Error rate is asked as a question and answered today from memory; evaluations measure it. Evaluation metrics must be admissible as the answer to the accuracy and error-rate questions, must move the inherent level when they move, and must ride in the export pack as evidence. (RC-12) | Must |
| FR-35 | **Make the export pack sufficient for risk acceptance.** The intake process ends in a business VP accepting the risk and the mitigations. The pack must therefore state both the band and **the obligations that band will cause to be enforced**, so the accountable owner is accepting a known enforcement posture rather than a score. (RC-13) | Must |
| FR-36 | **Carry the external governance identifiers on the use case** — the enterprise use-case id, the GRC record and any existing triage reference. The GRC platform must retain observability of the use case even while the control plane holds the inventory and no sync exists, and the identifiers are what make the eventual reconciliation possible rather than a re-keying exercise. (RC-14) | Must |
| FR-37 | **Define what qualifies for the observe-only path.** Absence of PII is not sufficient: what matters is also who consumes the output and whether a person acts on it, which the control plane cannot observe. The criteria must distinguish a self-contained experiment from resources operating inside a real use case, and must state what is assumed rather than verified. (RC-15) | Must |
| FR-38 | **Support conditional questions and hard triggers in an instrument.** The enterprise tiering instrument runs to roughly seventy questions with an agentic branch that opens only when earlier answers select it, plus trigger answers that set a floor outright. A pack must express activation conditions on questions and sections, so an instrument asks what applies and the unasked questions are recorded as not applicable rather than as absent. (RC-16) | Must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **Consume, don't fork** — adopt the consortium engines; Sun Life specifics are config/seed only. | Must |
| NFR-2 | **Config-first** — Field Guide, band↔tier, policies, eval matrix, gate names, OSFI frequencies are Sun Life configuration; nothing Sun Life-specific is hardcoded into a shared engine. | Must |
| NFR-3 | **CMRM = single source of truth** for policy/questionnaire content (authored once, ingested). | Must |
| NFR-4 | **Auditable** — every intake, risk assessment, gate decision, and GRC exchange emits an audit event. | Must |
| NFR-5 | **Frontend-agnostic** — Quick is UX; the API contract works for any client. | Must |
| NFR-6 | **Human-first, then codify.** Every gate has a manual mode; automation is an upgrade, not a precondition. Documentation ingestion (change log, assumptions, methodology) is the root prerequisite of the obligation dependency chain. (D10, D11) | Must |
| NFR-7 | **No hard dependency on Archer.** ACP produces a complete governance report with the Archer adapter disabled; sync is an enhancement. (D2) | Must |
| NFR-8 | **Tool-agnostic evidence.** Any evaluation tool may participate provided it meets the evidence contract; ACP does not mandate a tool, and lifecycle and approval state stay with the platform. (D12, D13) | Must |
| NFR-9 | **Band vocabulary conformance.** The value written to Luminate is from its ranked set — `low`, `medium`, `high`, `critical`. Sun Life's `AA`/`A`/`B`/`C`/`D` levels stay in the ACP record and the committee's language; a band outside Luminate's set is unrankable and fails closed without erroring. (LB-7) | Must |
| NFR-10 | **One vocabulary, several instruments.** Use case, agent, model and MCP server are assessed on different instruments — a use case asks what could happen to a person, a resource asks what it can reach — but all resolve to the same band vocabulary. Without that, there is nothing to compare and the containment check cannot exist. (RC-7) | Must |

## Constraints & Assumptions

- The generic risk/eval/compliance engines are delivered by the consortium specs; this spec is
  blocked on their availability (or the internal MVP as an interim).
- CMRM owns and maintains the questionnaire + policy content; ACP owns the config/integration.
- Amazon Quick production availability is uncertain — API contracts must not depend on it.

## Open Questions

- Does auto-approve/escalate mutate the Luminate lifecycle directly, or only the approval outcome?
- Where is the Sun Life config (band↔tier, eval matrix) held — ACP config store vs registry seed?
  *(Answered in part: it is held as versioned content packs — see `governance-content-packs`.)*
- Cadence for CMRM content refresh (questionnaire/obligations) and how changes re-trigger classification.
- **Q2** — what is the interface between GbD's assessment module / risk-scoring engine and ACP's
  risk-classification module? Taken offline by Seth and Duncan (10:45). The interface must accept an
  **external assessment provider**, because model risk is not the only input — other risk domains
  are being folded into an overall score that is under review (Kathryn, 8:19).
- **Q5** — which directives should teams prioritise first as they onboard to ACP? (Robert Chin, 41:31)
- Scope discipline: there are *"30 other risks that aren't handled by this"* (Mark Jarvis, 41:19).
  Each governance spec states its non-goals explicitly.
- **LB-Q1** — a `ServicePrincipal` cannot register as a Luminate `EvidenceProducer`, because that
  relation points at the Django user model and a machine principal is deliberately not a user.
  Evidence submitted by a service is attributed to `unregistered:`, counts toward nothing, and
  still returns `201`. Does ACP defer the evidence path until Machine Identity lands producer
  onboarding, or raise it as a consortium defect first?
- **LB-Q2** — where does the content pack revision live on the Luminate side (FR-19)? A second
  governance-authoritative attribute works today but puts version strings into a curated
  vocabulary. The alternatives need a platform change.
- **LB-Q3** — Luminate has no discovery: its inventory is registration-only, and there is no
  unregistered-resource concept. Does discovered-agent auto-triage (FR-10) require ACP to own
  discovery outright, and if so is that in this spec or its own?
- **LB-Q4** — `application` is deliberately not swept by Luminate governance and has no governance
  state, so a band published against one is inert. Does Sun Life still need application-level
  classification for ACP-side reporting, or does the unit of assessment become the agent?
- **RC-Q1** — *(answered, 15 Sep workshop)* a resource that exceeds its ceiling is stopped in the
  enforcing environments immediately, and that stop raises the signal for re-evaluation at the use
  case level. The agent does not wait for the use case to move, and it does not carry on while the
  re-evaluation is pending.
- **RC-Q2** — which signals are inherent and which are controls? The split is the decision; the
  arithmetic follows from it.
- **RC-Q3** — should Luminate govern a project? A project is a valid attribute target, so a
  use-case band can be **stored**; it is not swept and not band-covered, so nothing **enforces** it.
- **RC-Q4** — what happens to the resources in a use case whose band is *lowered*? Every child is
  then over-provisioned relative to its new ceiling.
- **RC-Q5** — is the use-case band per environment, or one band with per-environment enforcement?
- **RC-Q6** — who assigns a resource to a use case, and what happens to one that belongs to none?
- **RC-Q7** — how much of the intake form can the exported pack actually answer? *Narrowed by the
  15 Sep workshop*: evaluations can answer the accuracy and error-rate questions outright (FR-34),
  and the agentic attributes are observed. What the platform cannot supply is who consumes the
  output and whether a person acts on it — the impact axis. The remaining question is how much of
  the form that leaves.
- **RC-Q8** — should an unobserved signal score zero, or its worst case? The weighted engine scores
  a missing signal as zero and marks the result provisional, so a discovered agent with nine of
  eleven signals unknown scores 10 and bands `low`. The provisional flag carries the caveat, but
  the band is what a gate reads, and for a rogue resource low is the wrong direction.
- **RC-Q9** — should the raw score be published alongside the band? Cut points are calibrated per
  resource type, so 51 is critical for an MCP server while 60 is medium for an agent. Only the band
  is comparable; publishing the score next to it invites a comparison that does not hold.
- **RC-Q10** — how is a composite band derived from domains whose scales do not correspond
  (FR-31)? Obligations need one band, but a four-level model-risk grade and a low/moderate/high/
  critical security rating are not the same measurement, and mapping them onto one another is an
  assertion that needs owning rather than a calculation.
- **RC-Q11** — who arbitrates a domain conflict (FR-32), and what does the resource do while the
  conflict is open? Blocking on every disagreement stalls delivery; proceeding on the lower reading
  is the decision nobody wants to have made by default.
- **RC-Q12** — the same use case will be given a risk profile by the control plane and by
  Governance by Design. Which is displayed where, and what stops a user seeing two different
  numbers for one thing? The approved classification is authoritative (DD-27), but that settles
  precedence, not what each surface shows.
- **RC-Q13** — does the enterprise tiering instrument become the use-case instrument, or does it
  sit alongside the model-risk questionnaire? It already carries the agentic branch and the hard
  triggers, and a crosswalk from it to platform capabilities is already part-built. Running both is
  the outcome nobody chose.
- **RC-Q14** — lower environments are observe-only, but a lower environment can expose production
  data. Does a resource reaching production data in DEV or SIT enforce despite the environment, and
  if so, what else breaks the observe-only assumption (FR-37)?
