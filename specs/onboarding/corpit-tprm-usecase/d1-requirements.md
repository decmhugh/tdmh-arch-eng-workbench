# Corp IT TPRM Use Case — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Epic**: [EACPP-1318](https://sunlife.atlassian.net/browse/EACPP-1318) · Board label `acp-product-team`
> **Use case contacts**: Grant Du (solution architect) · Deepankar Pant (product) · Priyanshu Dhama (engineering) · Dragana Sikimic (CorpAI lead) · Kamal Boorghani (architecture)

## Sources and how to read this

| Source | What it contributes |
|---|---|
| [`references/corp-it-tprm-acp-discovery-session.txt`](references/corp-it-tprm-acp-discovery-session.txt) | The architecture Grant Du presented, release phasing, governance status, LVT, model concern. Cited below as `[mm:ss]`. |
| [`d0-discovery.md`](d0-discovery.md) | Business framing, stakeholders, the D0 capability exposures |
| [AIMS D1–D3](../aims-acp-integration/d1-requirements.md) | The sibling Corp IT onboarding. TPRM reuses its shape; the TPRM agents have no MCP servers and no agent-to-agent calls, so TPRM is a subset of it. |

Capability verdicts were re-verified for this spec against `AI-Consortium/luminate` `origin/main` @
`5c98145d4` (2026-09-30), `EDAEACP/acp-harness-sdk` `origin/main` @ `a0d62e9`, and a **read-only
query of the dev install** (`slf-eks-t1k-ca-dev`) on 2026-10-01. Where this document is sharper than
the [capability map](../../../capability-map.md), it says so.

> ⚠️ **This D1 is written ahead of three answers that can change it.** The discovery session left
> the *shape of the ACP-enabled release* undefined (§0, C-1), the *model* unassigned (Q6) and the
> *AgentCore network path* unproven (Q7). The requirements below are written for the architecture
> presented on the call. Task **T1** of the D3 plan exists to confirm that architecture before
> anything is built against it.

---

## 0. What the D0 left out or got wrong

The D0 was written from the transcript but dropped the architecture, which is where most of the
onboarding consequences are. Recorded here rather than by rewriting the D0.

| # | Point | Transcript | Consequence |
|---|---|---|---|
| **C-1** | **The release plan is internally contradictory.** Dragana: *"we cannot go on production if we are using Agent Core without ACP"* `[11:49]`. Later, Dragana and Deepankar agree MVP1 goes live **without Agent Core and without ACP**, with both incorporated in a later MVP `[30:25–30:43]`. But the architecture Grant presented runs both agents **on AgentCore** `[08:00]`. | What runs in production in November, and what the ACP-enabled release looks like, are not stated anywhere. | **Q1 — blocks the plan.** This D1 designs against the presented (AgentCore) architecture. |
| **C-2** | The D0 omits the architecture. | ServiceNow polled every 4 h → S3 input → **Step Functions** → two **AgentCore** agents → **Bedrock foundation models with Bedrock Guardrails** and a **Bedrock Knowledge Base** → **Lambdas** for document ingestion and PDF report generation → S3 output → ServiceNow API through the outbound gateway `[07:22–08:31]`, `[16:11–16:26]`. | Three of those pieces — Guardrails, the Knowledge Base and the Lambdas — each need an onboarding decision (§1, G1, G2, Q5). |
| **C-3** | "Canadian models" is recorded only as "confirm the model with Sandra Lai". | Dragana: *"they raised a concern about some models because we are using Canadian models"* `[28:31]`. | A **residency requirement**, not just a model choice. See NFR-4 and G8. |
| **C-4** | Stakeholder table omits the delivery team. | Deepankar Pant, Priyanshu Dhama and Dragana Sikimic were on the call; Grant asked for Deepankar and Priyanshu in the working chat `[22:31]`. | Header above corrected. |
| **C-5** | "Human approvals are enforced" through ACP (D0 success criteria). | Human review happens **in ServiceNow**: relationship managers check the result and can override the scoring `[14:23]`. | ACP does not and should not enforce the RM decision. ServiceNow remains the system of record for the risk decision (§8). |
| **C-6** | "TPRM workflow is registered in ACP". | — | Luminate registers **agents, applications and models**, not workflows. The Step Functions workflow is not a catalog object (D2 DD-2). |
| **C-7** | Overlap with Governance by Design is not recorded. | Agreed with Katharine to proceed separately and reconvene when GbD picks up this module `[06:26–06:54]`. | Recorded as a dependency to revisit, not a blocker (Q13). |
| **C-8** | Governance status is paraphrased. | *"Most of these related requests are already approved, like ISRA … but at the ETAB we got conditional approval"* `[09:25]`. | The ETAB **conditions** are not recorded anywhere this team can see (Q8). The ATG number is unconfirmed: the Confluence *Enterprise Agentic AI — Technology Register* lists a "TPRM AI Analysis" ATG dated 3 Aug 2026, which may be this one. |

---

## 1. What is being onboarded

The TPRM Third-Party Submission workflow. Vendors answer risk questionnaires on the external
ServiceNow portal; today relationship managers (RMs) check every response against Sun Life policy by
hand `[04:50–05:28]`. The solution assesses each response automatically and writes a PDF analysis and
a risk rating back to ServiceNow for the RM's final decision.

### The estate as described

| # | As stated | Onboarding consequence |
|---|---|---|
| E-1 | Poller extracts new questionnaires and attachments from ServiceNow **every four hours** into an S3 input bucket `[07:44]` | Not an AI workload. Nothing to register unless it calls a model (Q5). |
| E-2 | **Step Functions** orchestrates a deterministic workflow `[07:53]` | Not an agent. Not registered (D2 DD-2). Its schedule is the natural application-side stop lever (D2 DD-8). |
| E-3 | **Risk Assessment Agent** and **Validation Agent** on **AgentCore** `[08:00]` | Two registered agents. AgentCore runtimes must run in **VPC network mode** — `networkMode: PUBLIC` is denied by an org SCP (seen on ACP's own AgentCore runtimes) — and need a route to the gateway (Q7). |
| E-4 | Agents call **Bedrock foundation models with guardrails** `[08:10]` | Model calls move to the gateway. **Bedrock Guardrails do not travel with them** — see G1. |
| E-5 | Agents **leverage a knowledge base** — the TPRM manuals and guidelines `[05:51]`, `[08:14]` | Bedrock Knowledge Base retrieval is not a gateway route — see G2. |
| E-6 | **Lambdas** for document ingestion and PDF report generation `[08:19]` | Registered as **Applications** only if they call a model (Q5). |
| E-7 | Result written to S3, then to ServiceNow over its API, through the outbound gateway `[08:25]`, `[16:21]` | No MCP server. The agents never touch ServiceNow directly `[16:11]`. |
| E-8 | UI is ServiceNow; RMs can check and override the scoring `[14:18–14:37]` | Human oversight lives outside ACP (C-5). |
| E-9 | No MCP `[13:43]`. No evaluation pipeline `[14:06]`. | CAP-03 not triggered. CAP-17 triggered by decision impact, with no method in place (G4). |
| E-10 | LVT **objective L4 V4 T4**, **capability L2 V2 T2** `[15:33]` | Which of the two drives the risk band is not stated (Q10). |
| E-11 | Production target **first week of November**, without ACP `[10:00]`, `[13:14]` | The November release is not gated by this plan. |

---

## 2. User stories

### US-1 — Register the TPRM agents

**As a** TPRM engineer, **I want** the Risk Assessment and Validation agents registered in a TPRM
project on Luminate, **so that** each has an owner, a status and an identity of its own.

- [ ] **Given** I hold *Agent Administrator* on the TPRM project, **when** I register the Risk Assessment Agent, **then** it appears with a permanent key and an `active` status.
- [ ] **Given** a Lambda in the workflow calls a model, **when** it is onboarded, **then** it is registered as an **Application**, not as an agent.

### US-2 — Assess a vendor response through the governed path

**As the** Risk Assessment Agent, **I want** every completion I request to go through the Luminate
gateway on my own credential, **so that** each call is authenticated, authorized, guardrailed, traced
and costed.

- [ ] **Given** a credential for my (agent, gateway) pair held in Secrets Manager, **when** I exchange it and call `/llm/v1/chat/completions`, **then** I receive a completion from the assigned model.
- [ ] **Given** my runtime's IAM role, **when** I attempt `bedrock:InvokeModel` directly, **then** it is denied — the governed path is the only path.
- [ ] **Given** no access policy from me to a model, **when** I call it, **then** I receive `403`.

### US-3 — Trace one vendor case end to end

**As an** RM or TPRM lead, **I want** every model call made for one questionnaire to carry that
case's ServiceNow identifier, **so that** I can see what both agents did, and what it cost, for a
given vendor assessment.

- [ ] **Given** the workflow is processing ServiceNow case *X*, **when** either agent calls the gateway, **then** the request carries `x-luminate-session-id: X` and appears under that session in Langfuse.
- [ ] **Given** the two agents are different entities, **when** I look for case *X*, **then** I find two sessions — `agent:<risk-id>:X` and `agent:<validation-id>:X` — because the gateway namespaces the session per entity. The join is on the raw case id.

### US-4 — Keep the approved content controls

**As** Corp IT risk, **I want** the guardrail controls that the current approvals rely on to remain
in force after the model calls move to the gateway, **so that** onboarding does not quietly weaken an
approved control.

- [ ] **Given** a vendor response containing personal data, **when** it reaches a model through the gateway, **then** the gateway's request guardrail detects and redacts or blocks it.
- [ ] **Given** Bedrock Guardrails policies are part of the approved design (Q3), **when** the agent processes a case, **then** those policies are still evaluated, and the evaluation is recorded.

### US-5 — Stop the workflow

**As an** operator, **I want** to stop the TPRM agents from making further model calls and stop new
cases from starting, **so that** a misbehaving assessment run is bounded.

- [ ] **Given** the agents are running, **when** I use the platform lever, **then** within a **measured** interval their governed calls are refused.
- [ ] **Given** I disable the workflow's schedule, **then** no new case starts, independently of the platform.

### US-6 — Show that the agents are fit for purpose

**As** Corp IT risk, **I want** a recorded measure of how often the agents' rating matches the RM's
final rating, **so that** an agent that influences a vendor-risk decision has evidence behind it.

- [ ] **Given** RMs override ratings in ServiceNow, **when** a period of cases has been reviewed, **then** an agreement rate per agent is computed against a recorded threshold.

---

## 3. Capability selection (proposed — confirm in T1)

Status column: map status, **corrected** where this spec's verification differs.

| CAP | Capability | Governance | Status | Why TPRM needs it |
|---|---|---|---|---|
| CAP-01 | Agent registry | Mandatory | ✅ | Two agents |
| CAP-02 | Model registry | Mandatory | ✅ | The model Sandra Lai assigns |
| CAP-03 | MCP tool registry | Conditional — **not triggered** | ✅ | No MCP `[13:43]`. Becomes triggered only if D2 DD-5's Knowledge Base option B is chosen. |
| CAP-04 | Deployment registry | Mandatory | ✅ | Credentials hang off deployments |
| CAP-05 | SSO / human identity | Mandatory | ✅ | TPRM engineers in the portal |
| CAP-06 | Machine identity | Mandatory | ✅ | Each agent authenticates as itself |
| CAP-07 | RBAC and access policy | Mandatory | ✅ | Agent → model matrix |
| CAP-08 | Governed gateway | Mandatory | ✅ | Every model call |
| CAP-09 | Policy enforcement | Mandatory | ✅ | Fail-closed on every call |
| CAP-10 | Guardrails | Mandatory | ✅ gateway / **❌ Bedrock Guardrails** | Vendor responses and attachments may carry personal data. The gateway's guardrails are banned words, PII (Presidio) and Model Armor only — see G1. |
| CAP-11 | Kill switch | Mandatory | ✅ per map / **🟡 for a calling agent** | See G3 — the runtime governance gate is keyed on the call's *target*. |
| CAP-12 | Quotas and budgets | Mandatory | ⚠️ | A 4-hourly batch can burst; nothing caps it (G5) |
| CAP-13 | Attribute tagging | Mandatory | ✅ | Owner, classification, risk band |
| CAP-15 | Risk tiering | Mandatory | ✅ platform / **Sun Life method missing** | Band assignment from LVT is undefined (G12) |
| CAP-17 | Evaluation | Conditional — **triggered** | 🟡 | Both agents influence a vendor-risk decision (D0). Evidence ingest has merged; nothing runs an evaluation (G4). |
| CAP-18 | Audit trail | Mandatory | ✅ gateway calls / external producer 🟡 | The case lifecycle stays in ServiceNow (G6) |
| CAP-19 | Regulatory reporting | Mandatory | 🟡 | OSFI context `[12:51]`; signed evidence pack not built (G7) |
| CAP-20 | Observability and cost | Mandatory | ✅ | Per-agent, per-case cost — see G9 for chargeback |
| CAP-26 | Jurisdiction / data-flow control | Conditional — **triggered** | 📐 | Canadian residency (C-3, G8) |

**Not selected:** CAP-14 approvals beyond the platform default (the RM decision is in ServiceNow),
CAP-16 model cards (becomes mandatory if Corp IT places the model in E-23 scope — Q10), CAP-24 chain
authorization (Step Functions sequences the agents; they do not call each other).

---

## 4. Functional requirements

| ID | Requirement | CAP | Priority |
|---|---|---|---|
| FR-1 | The Risk Assessment and Validation agents are **registered catalog entries** in one TPRM project under the existing `Corp IT` folder, with permanent keys and an owner. | CAP-01 | Must |
| FR-2 | Any Lambda or Step Functions state that calls a model is registered as an **Application**; components that call no model are not registered. | CAP-01, CAP-06 | Must |
| FR-3 | The model(s) TPRM uses are reachable as a catalog entry with a **Bedrock offering in `ca-central-1` whose provider model id is fulfilled in Canada** (NFR-4). | CAP-02, CAP-26 | Must |
| FR-4 | Each agent and application has a **deployment** on the dev gateway and exactly one **machine credential** per (resource, gateway), held in AWS Secrets Manager in the TPRM account. | CAP-04, CAP-06 | Must |
| FR-5 | **All** TPRM model inference goes through the gateway. The runtime IAM roles **lose** `bedrock:InvokeModel*` and `bedrock:Converse*` so a direct call fails rather than succeeding ungoverned. | CAP-08 | Must |
| FR-6 | An explicit **access policy** per (agent → model) pair; absence denies. | CAP-07, CAP-09 | Must |
| FR-7 | Gateway **guardrails on request and response** for TPRM traffic, configured from the data classification of vendor responses (Q9). | CAP-10 | Must |
| FR-8 | Bedrock Guardrails policies that the approved design relies on stay in force, evaluated by the agent through the standalone **`ApplyGuardrail`** API on input and output (D2 DD-4). | CAP-10 | Must, if Q3 confirms they are relied on |
| FR-9 | Knowledge Base use is **retrieval only** (`bedrock-agent-runtime:Retrieve`). `RetrieveAndGenerate` is removed from the runtime role, because it performs model inference outside the gateway. | CAP-08 | Must |
| FR-10 | Every gateway call carries **`x-luminate-session-id`** set to the ServiceNow case identifier. | CAP-20 | Must |
| FR-11 | Per-request **usage, latency and cost** attributed per agent and per model, and rolled into the chargeback ledger against the TPRM project's **cost centre**. | CAP-20 | Must |
| FR-12 | An operator can stop both agents; the platform lever's propagation interval is **measured and published**, and the schedule-disable lever is documented beside it. | CAP-11 | Must |
| FR-13 | Governance attributes — owner, data classification, risk band — on both agents and the model grant. | CAP-13, CAP-15 | Must |
| FR-14 | A **pre-production evaluation method** per agent, using RM decisions as ground truth, with a recorded pass threshold, before the ACP-enabled release is promoted beyond dev. | CAP-17 | Must (before promotion) |
| FR-15 | Every governed call produces an immutable **audit record** (actor, target, decision, timestamp). | CAP-18 | Must |

---

## 5. Non-functional requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Availability | The gateway being unavailable delays a batch; it must not lose a case. | Step Functions retries the agent step; the case stays in S3 until processed |
| NFR-2 | Latency | Batch workload every 4 h — latency is not a user-facing constraint. | Gateway overhead measured in T13 and recorded, not budgeted in advance |
| NFR-3 | Security | No credential in an image, repository, ticket or message. | Secrets Manager; AgentCore execution role scoped to its own secret ARN |
| NFR-4 | Residency | Inference for TPRM data is **fulfilled in Canada**. The offering's `region` field is **not** evidence of this: it records the endpoint the gateway calls. A `us.`-prefixed provider model id is a US geographic inference profile. | Fulfilment region checked per model id before the access policy is created |
| NFR-5 | Attribution | Every governed call resolves to exactly one TPRM agent or application. | One credential per (resource, gateway) |
| NFR-6 | Blast radius | A TPRM runtime cannot reach any model outside its policy set, and cannot reach Bedrock inference at all except through the gateway. | FR-5 + FR-6 |
| NFR-7 | Honesty of claim | Nothing is presented to Corp IT risk or ETAB as a control unless it is enforced at runtime. | §6 and D2 §8 govern TPRM-facing material |

---

## 6. Capability gap register

Classified per the [Capability Gap Escalation](../../../process/capability-gap-escalation.md) process.

| ID | CAP | What is missing | Class | Impact on TPRM |
|---|---|---|---|---|
| **G1** | CAP-10 | **Bedrock Guardrails are not carried through the gateway.** The gateway speaks the OpenAI chat format; Luminate's guardrail types are `BannedWordsConfig`, `PIIDetectionConfig` and `ModelArmorConfig` (`packages/types/src/luminate_types/guardrails.py`). There is no field for a Bedrock `guardrailConfig`, and no contextual-grounding check. | Component change | **Degrades** — a control that may be cited in the approvals (Q3) silently disappears on migration unless the agent calls `ApplyGuardrail` itself (D2 DD-4). |
| **G2** | CAP-08 | **Knowledge Base retrieval is not a gateway route.** No `bedrock-agent-runtime` or Retrieve path exists in `gateway/`. The KB's query embedding runs inside Corp IT's account, outside the gateway. `RetrieveAndGenerate` would run a **model** outside it. | Integration | **Degrades** — retrieval stays direct and declared (D2 DD-5 option A). Wrapping it as an MCP server (option B) is Sun Life harness work, not a consortium ask. |
| **G3** | CAP-11 | **Stopping a *calling* agent.** Suspension sets `governance_state` and `authz.rego` refuses — but the rego files that status under the call's **target** (`input.target_type:target_id`, or `model:<id>`). TPRM's agents are always **callers**. Whether suspending one refuses its outbound model calls — through the AIC-467 cascade to the access policies naming it, or otherwise — is not established by reading the code. The operational `status=inactive` edit and per-policy `suspend` both work (`facts.py` exports only ACTIVE agents and ACTIVE policies). | To verify | **Unknown until drilled** — T18 measures all three levers. |
| **G4** | CAP-17 | **No evaluation runner.** Evaluation evidence ingest merged upstream on 2026-09-16 (AIC-38: `backend/app/evaluations/` reads scores from Langfuse, records them as governance evidence, detects degradation). Nothing runs an evaluation, and no documented path exists for a **tenant** to write scores into the platform's Langfuse. | Component change + TPRM-owned method | **Blocks promotion** of an agent that influences a vendor-risk decision (FR-14). Does not block dev onboarding. |
| **G5** | CAP-12 | Quotas are not enforced; `gateway/` has no quota references. | Component change | **Degrades** — a 4-hourly batch has no runtime cap. Alerting only. |
| **G6** | CAP-18 | No external audit producer — *"deliberately no public producer REST endpoint"* (`audit_events/ingest.py`). | Component change | **Accepted** — the case lifecycle and RM decision stay in ServiceNow, the system of record. Platform audit covers governed calls. |
| **G7** | CAP-19 | Signed, immutable evidence pack not built. | Component change | **Degrades** — OSFI questions answered from exports by hand. |
| **G8** | CAP-26 | **Residency is not a platform control.** Jurisdiction control is designed, not built. On the dev install, every Anthropic entry newer than Claude 3.5 / Opus 4.5 carries a `us.` provider model id, and a tenant (AIMS) owns two of them. Only the choice of offering and the access policy stand between TPRM and US-fulfilled inference. | Component change (CAP-26) + configuration | **Constrains model choice** — the tension Dragana raised `[28:59]`. Resolved per model in T2. |
| **G9** | CAP-20 | **Chargeback attribution is not configured.** A keyless Bedrock offering runs through the gateway's role chain into the ACP spoke account, so inference **moves off Corp IT's AWS bill**. The chargeback ledger attributes by project `cost_centre`, which is **empty on all 15 projects** on the dev install (queried 2026-10-01). | Configuration | **Degrades** — cost is visible per agent but cannot be charged back until the TPRM project carries a cost centre (T4). |
| **G10** | CAP-20 | **Harness SDK session-header defect.** `acp_harness_sdk/middleware.py` sets `x-session-id`; the gateway reads `x-luminate-session-id`. SDK users get no session correlation. | Sun Life SDK fix | **Degrades US-3** unless TPRM sets the header explicitly (D2 DD-7). Fix belongs in `acp-harness-sdk`. |
| **G11** | — | **No tenant has been onboarded to the prod install**, and gated stage/prod promotion has not been exercised by any tenant. | Platform readiness | **Blocks production** for the ACP-enabled release — a dependency on `gateway-environment-strategy` and `self-service-onboarding`, not on TPRM. |
| **G12** | CAP-15 | The platform enforces the band's rigour; **who assigns the band, and from which LVT figure**, is a Sun Life method that does not exist. | Sun Life method | **Degrades** — the band tag is set by hand from Q10. |

---

## 7. Constraints

- **Dev install only** for this plan (`slf-eks-t1k-ca-dev`, gateway `luminate-gateway-dev`). Every tenant is onboarded there; putting TPRM on the prod install would make it the first (G11).
- **AgentCore runtimes run in VPC mode.** `networkMode: PUBLIC` is denied by an organization SCP.
- **Deployment, credential issuance, access policies and governance attributes cannot be delegated** by any role — they route to the ACP Product Team (D2 DD-9).
- **Project and keys are permanent**, and a deployed catalog entry cannot be deleted.
- **Credentials are show-once**, one active per (resource, gateway), with no rotation overlap.
- The November production release does **not** depend on this plan `[13:14]`.

---

## 8. What ACP will and will not do for TPRM

| TPRM asks for | ACP provides | Stays with TPRM / ServiceNow |
|---|---|---|
| Govern model calls | Gateway authn/authz, guardrails, trace, cost, audit per call | — |
| Keep human decision authority | — | RM review and override in ServiceNow; ServiceNow is the record of the decision |
| Evidence the agents are fit | Stores evaluation scores as governance evidence (AIC-38) | Running the evaluation; RM decisions as ground truth (FR-14) |
| Stop the agents | Status / policy / governance suspension | Disabling the schedule |
| Per-case view | Session correlation on the ServiceNow case id | Setting the header |

---

## 9. Open questions

These are the follow-ups for the TPRM team. They are also posted on the PR.

| ID | Question | Owner | Blocks |
|---|---|---|---|
| **Q1** | What runs in production in November — AgentCore or not — and what are the architecture and target date of the ACP-enabled release? (C-1) | Grant Du, Deepankar Pant, Dragana Sikimic | **Everything** |
| **Q2** | Which agent framework (Strands, LangGraph, other), and how do the agents call Bedrock today — Converse via boto3, LangChain `ChatBedrock`, other? | Priyanshu Dhama | T12 code change |
| **Q3** | Which Bedrock Guardrails policies are configured (content filters, denied topics, PII, **contextual grounding**), and are they cited as a control in the ISRA or the ETAB conditions? | Grant Du | FR-8, T15 |
| **Q4** | Knowledge Base: `Retrieve` or `RetrieveAndGenerate`? Which embedding model? Classification of the manuals and guidelines? | Priyanshu Dhama | FR-9, T16 |
| **Q5** | Do the ingestion or report Lambdas, or any Step Functions state, call a model (including Textract or Bedrock Data Automation)? | Priyanshu Dhama | FR-2, inventory |
| **Q6** | Which model is assigned, and is Canadian fulfilment a hard requirement? If so, which in-region model id? | Sandra Lai, Dragana Sikimic | FR-3, T2 |
| **Q7** | AgentCore network: VPC, subnets, security groups, DNS resolution of `*.apps.slf-eks-t1k-ca-dev.aws.sunlifecorp.com`, and whether egress goes through the same outbound gateway used for ServiceNow. | Grant Du, Kamal Boorghani | **T3 spike** |
| **Q8** | ATG number, and the ETAB conditions verbatim. | Grant Du | Assurance scope |
| **Q9** | Data classification of questionnaire responses and attachments, including personal data about vendor staff. | Deepankar Pant | FR-7 guardrail configuration |
| **Q10** | Which LVT figure — objective L4V4T4 or capability L2V2T2 — sets the risk band, and is the model in E-23 scope? What is the agent-failure impact assessment? | Grant Du, Dragana Sikimic | FR-13, CAP-16 |
| **Q11** | Who is the TPRM project Owner, which AD group holds the engineers, and which cost centre pays? | Deepankar Pant | T4, T5 |
| **Q12** | Can RM overrides be exported from ServiceNow as (agent rating, final RM rating) per case? What agreement rate is acceptable? | Deepankar Pant | FR-14, T19 |
| **Q13** | Is there a reuse commitment with Governance by Design (Katharine)? | Dragana Sikimic | Scope only |
| **Q14** | Who owns the stop runbook, and what stop interval is acceptable? | Dragana Sikimic | T18 |

---

## 10. Traceability

| Requirement | CAP | D0 success criterion | Transcript |
|---|---|---|---|
| FR-1, FR-2 | CAP-01 | TPRM agents registered in ACP | `[10:13]` |
| FR-3 | CAP-02, CAP-26 | Model assignment approved | `[28:31]` |
| FR-4, FR-6 | CAP-04, CAP-06, CAP-07 | AI assistance is governed | — |
| FR-5 | CAP-08 | 100% of model calls via ACP | `[11:49]` |
| FR-7, FR-8 | CAP-10 | — (mandatory baseline) | `[08:10]` |
| FR-9 | CAP-08 | — | `[08:14]` |
| FR-10, FR-11 | CAP-20 | Vendor review evidence is traceable | — |
| FR-12 | CAP-11 | — (mandatory baseline) | `[12:14]` |
| FR-13 | CAP-13, CAP-15 | Risk-aligned controls | `[15:33]` |
| FR-14 | CAP-17 | Evaluation approach before promotion | `[14:06]` |
| FR-15 | CAP-18 | Review process remains auditable | — |

## References

- Spec: [D0](d0-discovery.md) · [D2](d2-design.md) · [D3](d3-tasks.md)
- Epic: [EACPP-1318](https://sunlife.atlassian.net/browse/EACPP-1318)
- Sibling onboarding: [AIMS D2](../aims-acp-integration/d2-design.md)
- [ACP Capability Map](../../../capability-map.md) · [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
- Verification: `AI-Consortium/luminate` @ `5c98145d4` (2026-09-30) · `EDAEACP/acp-harness-sdk` @ `a0d62e9` · dev install, read-only, 2026-10-01
