# Mark's follow-up list — verification against the transcript

> **Component**: `governance-intake` · **Type**: Artifact (verification)
> **Purpose**: Mark Jarvis circulated a Copilot-generated follow-up list in the absence of minutes and
> asked whether we have alignment on it. This checks each item against the
> [12 August 2026 transcript](2026-08-12-model-risk-gbd-alignment-minutes.md), timestamp by timestamp,
> and records what is confirmed, what needs correcting, and what the list omits.

**Verdict in one line:** five of the six items are accurate as written; one (evidence-provider
standardisation) records as open a question that was largely *answered* in the session. Two items
need an owner added. Eight material items from the meeting are missing from the list.

---

## 1. Item-by-item verification

### ✅ 1. Deployment Strategy Documentation — *accurate*

> *Send the ACP on a page draft slide deck to Anirban to provide a visual overview of the deployment
> strategy. (Colin)*

**Confirmed.** Anirban asked for a deployment visual at 2:52. Colin at 3:45: *"a commitment that by
the 21st, we'll have kind of ACP on a page draft one out… I'll bounce that slide deck to you."* At
4:52 he added that Anirban's orchestration work gets layered on top.

**One correction worth making:** the list omits the **date — the 21st was a commitment**, and it
omits Seth's parallel promise at 5:02 to send the deployment specs to Anirban. Two deliverables, not
one.

*Register refs:* D17, A2, A3, A4 · *Meeting:* M7

---

### ✅ 2. Risk Classification Module API Ownership — *accurate*

> *Hold a sidebar discussion to determine ownership and approach for exposing the risk classification
> module as an API and managing its configuration. (Seth, Duncan)*

**Confirmed, and it is the sharpest open item on the list.** Duncan at 9:09 described a GbD
assessment module with consolidated questions, templates and a risk-scoring engine that *"we could
expose by our API."* Seth at 9:53 proposed the split — ACP Product maintains the API interface, the
content is driven by Model Risk and GbD. Duncan at 10:45: *"probably take this away… have a sidebar
conversation and figure out the best way."*

**Context the list does not carry:** Kathryn at 7:33 and 8:19 established that model risk is *not*
the only input — other risk domains have to be represented in an overall risk score that is under
review right now, and Ryan's team is reviewing Mohamed's proposal against it. The interface must
therefore be designed for an external assessment provider, not for a fixed CMRM questionnaire.

*Register refs:* D9, Q2, A16 · *Meeting:* M1 · *Spec:* `governance-intake`, consortium `governance-risk-triage` (EACPP-648)

---

### ⚠️ 3. Policy Registry Integration — *accurate, but add Kathryn and split in two*

> *Schedule further conversations to define integration points and data sources for the policy
> registry between ACP, governance by design, and model risk teams. (Seth, Ryan, Duncan)*

**Confirmed** by Seth at 16:14: *"we'll have some further conversations on what all these sources
look like, how we integrate with them."*

**Two corrections:**

1. **Kathryn should be an owner, not Duncan alone.** It was Kathryn at 13:09 who framed this as
   *"probably a bit of a triangle"* and set the requirement that ACP and GbD carry consistent
   information and consistent Archer integration. Duncan's contribution here was the consumer
   statement at 42:05.
2. **This is two conversations, not one.** The integration-points discussion (Seth / Ryan / Duncan)
   is separable from the Archer-integration-and-model-risk-oversight discussion Kathryn explicitly
   asked for at 13:09, which is the three-way one.

**Terminology:** "policy registry" is superseded — see item D4 in §2 below. It is the **obligation
registry**.

*Register refs:* D4, D5, D6; A8, A18 · *Meetings:* M5 · *Spec:* `governance-content-packs`, consortium `EACPP-915`

---

### ✅ 4. Validation Workflow Collaboration — *accurate*

> *Partner to align information capture and flow for validation requirements across governance
> domains and ensure reviewers' needs are met. (Ryan, Kathryn, Duncan)*

**Confirmed.** Kathryn at 21:21 offered directly: *"would love to partner with you on your vision
for that information capture and flow and what your reviewers need"* — framed around **what
information is needed at what stage of maturity** (intake, initial approval, evaluation, ongoing)
and noting other governance domains will want the same information. Duncan's inclusion is fair;
Kathryn tied it to *"the work that Duncan is executing against right now with more of a focus on
architecture."*

**Worth adding:** Ryan at 18:28 and 19:43 set the sequencing constraint this conversation runs
inside — the process is **human-driven first**, then translated into something an agent can ingest,
with documentation ingestion (change log, assumptions, methodology) as the first gate and later
assessments taking it as a prerequisite. That is a design constraint, not just context.

*Register refs:* D10, D11; A6, A7, A17 · *Meeting:* M4

---

### ✅ 5. Artifact Storage Strategy — *accurate*

> *Conduct an offline discussion to determine the most efficient way to store evaluation artifacts
> produced by various evidence providers. (Kalyan, Seth)*

**Confirmed.** Kalyan raised it at 27:36 — how artifacts from Bedrock evaluations, Openlayer and
similar tie back to a use case and a requirement, on what schedule, and *"are we duplicating the same
artifacts in ACP or not?"* — and closed at 43:45: *"we'll just work on the efficient way of storage
of those artifacts. That is an offline discussion we can do."* Seth agreed at 43:59.

**The answer already given in-session, which the list omits:** Seth at 30:40 — data may remain in
workload accounts, but the record comes back to ACP; ACP is canonical. So the offline discussion is
about *reference versus copy and scheduling*, not about whether ACP holds the record.

*Register refs:* D1, Q3, A12 · *Meeting:* M2 · *Spec:* `archer-grc-sync` DD-4, `governance-intake`

---

### ⚠️ 6. Standardization of Evidence Providers — *records an open question that was largely answered*

> *Discuss and decide on standardizing the set of evidence provider tools to avoid operational
> complexity and tool sprawl across the enterprise. (Kalyan, Colin, Ryan)*

**The concern is accurately captured** — Kalyan at 45:17 warned that unbounded adapters are an
operational nightmare, and at 48:34 asked whether we standardise or keep it open.

**But the direction was decided in the room.** Colin at 49:00: *"I don't think we're in a position
to standardize everywhere, although I think we want to offer a standard suite of tools, but we don't
want to force a standard… the model owner is ultimately responsible… I want to make a baseline
evaluation system that captures 80% of the workloads easily usable so that people don't need to
think about it and people don't go looking for their own approach."* **Mark endorsed it at 50:05:**
*"You summed it up very well, Colin."*

Seth's architectural answer at 46:46 is the other half: the evaluation API and normalised evidence
contract make ACP tool-agnostic, so the **contract is the standard, not the tool list**.

**Restated accurately, the follow-up is:** *define the baseline evaluation suite covering ~80% of
workloads — easily usable, explicitly not mandated — and publish the evidence contract that lets any
other tool participate.* That is a build item with a decision already behind it, not an open debate.

**Owner correction:** **Mark belongs on this item.** Colin at 49:00 deferred to him directly —
*"that's probably more Mark and Ryan"* — on the grounds that the policy places accountability on the
model owner.

*Register refs:* D12, D13; A14 · *Meeting:* M6 · *Spec:* `acp-aws-harness-sdk` (EACPP-791), consortium `model-agent-evaluation` (EACPP-647)

---

## 2. Material items the list omits

Each was stated in the session and has downstream consequences.

| # | Item | Said by | Time | Why it matters |
|---|---|---|---|---|
| **O1** | **"Policies" are renamed "obligations"** — "policy" already means one of six Sun Life corporate policies. | Ryan | 12:32 | Renames schema fields across every governance spec. Cheap now, expensive later. |
| **O2** | **Reporting splits by scope.** OSFI **E-23** is produced by **ACP** per agent/model; broader OSFI **technology-risk** reporting comes out of **GbD** per application/use case. | Kathryn | 42:09 | Without this boundary in writing, two teams report the same control from different systems. |
| **O3** | **GbD is a consumer of ACP's data products** — *"we would be a consumer of your data products, essentially."* | Duncan | 42:05 | ACP owes GbD a documented, stable read interface. It cannot be an afterthought. |
| **O4** | **Three layers of evaluation/observability**: registration/onboarding, scheduled re-evaluation, and per-inference retrieval (*"why did I get denied?"*). Aggregate the first two; the third stays in operational observability but must be retrievable. | Colin | 35:05–38:16 | Defines what is aggregated versus merely retrievable — a storage and cost decision. |
| **O5** | **Metric library with calibration.** Detect uncalibrated LLM-as-judge; prove teams test their judges. | Ryan | 50:08 | An uncalibrated judge makes every downstream evaluation meaningless. |
| **O6** | **APM records** tie technology dependencies to Archer use cases, instead of inventing a platform-level Archer record. GbD intake captures the references and passes them on. | Ryan, Duncan | 23:53, 24:26 | Avoids a redundant Archer record type; needs the field carried end-to-end. |
| **O7** | **Synthetic / mock Archer** so Archer access is not the blocker. | Ryan | 32:33 | Archer onboarding is the longest-lead item; this is what takes it off the critical path. |
| **O8** | **Feedback on Mohamed's agent risk-classification proposal** — encompasses most model-risk questions plus other dimensions. | Ryan's team | 8:02 | Feeds directly into item 2 above; the interface should not be designed before it lands. |

---

## 3. Suggested reply to Mark

> Yes — five of the six are accurate as recorded, with two owner additions and one restatement:
>
> - **Item 1** — add that the 21st was a commitment, and that Seth is also sending the deployment specs.
> - **Item 3** — add **Kathryn**; she raised the three-way "triangle" requirement. It is also two
>   conversations: integration points, and the separate Archer-integration/oversight one.
> - **Item 6** — this was largely settled in the room. Colin proposed, and you endorsed, offering a
>   **baseline evaluation suite covering ~80% of workloads without mandating it**, with the model
>   owner remaining accountable. The residual work is *defining* that suite and publishing the
>   evidence contract — please add yourself as an owner, since Colin deferred to you on it.
>
> Eight further items came out of the session that the list does not carry — the **policies →
> obligations** rename, the **E-23 vs technology-risk reporting split**, **GbD as a consumer of ACP
> data products**, the **three layers of evaluation**, the **metric library with judge calibration**,
> **APM pass-through**, the **synthetic Archer**, and **feedback on Mohamed's proposal**. Full
> register with timestamps is attached.

---

## 4. Traceability

| Mark's item | Register decisions | Register actions | Meeting | Tracking ticket | Delivery |
|---|---|---|---|---|---|
| 1 Deployment strategy | D17 | A2, A3, A4 | M7 | EACPP-1026 | `sunlife-deployment` (EACPP-596) |
| 2 Risk classification API | D9, Q2 | A16 | M1 | EACPP-1027 | `governance-intake` (EACPP-877), EACPP-648 |
| 3 Obligation registry integration | D4, D5, D6 | A8, A18 | M5 | EACPP-1028, EACPP-1029 | `governance-content-packs` (EACPP-990), EACPP-915 |
| 4 Validation workflow | D10, D11 | A6, A7, A17 | M4 | EACPP-1030 | `governance-intake` (EACPP-877) |
| 5 Artifact storage | D1, Q3 | A12 | M2 | EACPP-1031 | `archer-grc-sync` (EACPP-1003), EACPP-877 T12 |
| 6 Evidence providers | D12, D13 | A14 | M6 | EACPP-1032 | `acp-aws-harness-sdk` T24 (EACPP-1021), EACPP-647 |

### Omitted items — where they now live

| # | Item | Tracking ticket |
|---|---|---|
| O1 | Policies → obligations rename | EACPP-1015 (`governance-intake` T8) |
| O2 | E-23 vs technology-risk reporting split | EACPP-1035, EACPP-1016 (T9) |
| O3 | GbD as consumer of ACP data products | EACPP-1035, EACPP-1017 (T10) |
| O4 | Three layers of evaluation | EACPP-1018 (T11) |
| O5 | Metric library judge calibration | EACPP-1022 (harness SDK T25) |
| O6 | APM pass-through | EACPP-1006 (`archer-grc-sync` T3) |
| O7 | Synthetic Archer | EACPP-1004 (`archer-grc-sync` T1) |
| O8 | Feedback on Mohamed's proposal | EACPP-1033 |

All follow-up (`FU*`) tickets sit under epic **EACPP-1025** — *ACP × Model Risk ×
Governance-by-Design Alignment — Follow-Ups (12 Aug 2026)*.

Sources: [transcript](2026-08-12-model-risk-gbd-alignment-minutes.md) ·
[decisions & actions register](2026-08-12-decisions-and-actions.md) ·
[roadmap & work split](2026-08-12-governance-alignment-roadmap.md)
