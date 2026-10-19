# Onboarding Corp IT's use case: AIMS — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Epic**: [EACPP-909](https://sunlife.atlassian.net/browse/EACPP-909) · Board label `acp-product-team`
> **Use case contact**: Dragna Sikimic (Corp IT)

## Sources and how to read this

Requirements are derived from two places and nothing else:

| Source | What it contributes |
|---|---|
| [`references/ACP-AIMS.docx`](references/ACP-AIMS.docx) | The use case's own success criteria, its fourteen technical requirements, and its OSFI self-assessment |
| [`d0-discovery.md`](d0-discovery.md) | Problem, opportunity, stakeholders, scope boundaries, risks |

Capability verdicts are taken from the **ACP Capability Map** and were re-verified for this spec on
2026-08-28 against `AI-Consortium/luminate` `origin/main` @ `b04b0021`. Four verdicts in this
document are **narrower than the map currently states** and are called out in §7 — the map should be
updated from them.

> ⚠️ **The capability selection in §3 is reconstructed, not confirmed.** The D0 was written on
> 2026-08-12, before the capability map existed, so it carries no Capability Requirements table. The
> map's rule is that a capability is "required" only when the use case says so out loud against a
> named capability ID. §3 is therefore a **proposal derived from the reference document**, and
> confirming it with AIMS in session is task **T1** of the D3 plan. Nothing downstream should treat
> it as signed off until then.

---

## 1. What is being onboarded

AIMS is an operations intelligence platform for Corp IT. It detects AWS Glue job failures, collects
diagnostics, uses a generative model to produce a root-cause analysis, and notifies support teams.
It is becoming a multi-agent system in four stages:

| Stage | Capability | Onboarding relevance |
|---|---|---|
| **S1** | **RCA Agent** — analyses a failure and identifies likely root causes | In POC scope |
| **S2** | **Incident Correlation Agent** — correlates related failures into one investigation | In POC scope |
| **S3** | **Governed tool access** — MCP access to Teams, Jira, knowledge repositories, AWS operations | In POC scope |
| **S4** | **Remediation Agent** — recommends, then executes, approved corrective actions; then confidence-based self-healing | **Out of POC scope.** Requirements captured here so the platform gaps are visible early |

### The estate as described

Recorded verbatim from the reference document, with the ambiguities preserved rather than resolved —
resolving them is T1.

| # | As stated | Onboarding consequence |
|---|---|---|
| E-1 | "AIMS projects are PoC — 6 of which are in MVP (MVP 4 in progress) — 3 of them are in production" | **Three production workloads.** Onboarding is not greenfield. Which of the nine are in scope is [Q1](#9-open-questions). |
| E-2 | "Using Strands and LangGraph running on proxies on OpenShift running on Lambdas" | Two frameworks, two or three runtime surfaces. Which agent runs where, and what "proxies" denotes, is [Q2](#9-open-questions). |
| E-3 | "Using Anthropic Models (Haiku, Sonnet)" | Model registration + a Bedrock offering per model. Supported (§7 Q3). |
| E-4 | "MCP servers on OpenShift — governed by Okta via API platform" | **The single largest technical risk.** See gap **G1**. |
| E-5 | "Local environment" | Developers expect to work against something locally. See gap **G12**. |
| E-6 | "AWS Quick used in other use cases" | Unparsed — most likely Amazon Q or QuickSight. Out of scope until identified ([Q3](#9-open-questions)). |

---

## 2. User stories

### US-1 — Register the AIMS estate

**As an** AIMS engineer, **I want** to register each AIMS agent, model and MCP server in the Luminate
catalog, **so that** nothing AIMS runs is shadow AI and each asset has an owner and a status.

- [ ] **Given** I hold *Agent Administrator* on the AIMS project, **when** I register the RCA Agent, **then** it appears in the catalog with a permanent key, an owning project and an `active` status.
- [ ] **Given** an agent is registered but has no deployment, **when** I look for its credentials, **then** the portal explains that a deployment is required rather than offering an action that would fail.
- [ ] **Given** an MCP server whose transport is `stdio`, **when** I attempt to onboard it, **then** it is rejected at design time, not silently skipped at deploy time.

### US-2 — Reach an approved model through the governed path

**As an** AIMS agent runtime, **I want** to obtain a completion from Claude Haiku or Sonnet through
the Luminate gateway using my own machine identity, **so that** every model call is authenticated,
authorized, guardrailed, traced and costed.

- [ ] **Given** a credential issued for my (agent, gateway) pair, **when** I exchange it at the portal token endpoint and call `/llm/v1/chat/completions`, **then** I receive a completion.
- [ ] **Given** no access policy exists from my agent to that model, **when** I call it, **then** I receive `403` and the denial is recorded.
- [ ] **Given** the call succeeds, **when** I look at the agent's **Usage & Cost** tab, **then** the request, its token counts, its latency and its cost are attributed to *this agent* and *this model*.

### US-3 — Constrain which agent may use which tools

**As** Corp IT risk, **I want** each AIMS agent restricted to exactly the tools its role requires,
**so that** the RCA agent cannot invoke a tool that changes infrastructure.

- [ ] **Given** the RCA Agent has a policy to the AWS-operations **read** server only, **when** it attempts a call to the **write** server, **then** the gateway denies it.
- [ ] **Given** a new tool is added to a server the agent already reaches, **when** the agent calls it, **then** it is permitted — because authorization is per server, not per tool. *This is a known limitation, see gap **G2**.*

### US-4 — Stop an agent

**As an** operator during an incident, **I want** to stop a specific AIMS agent from making any
further governed call, **so that** a misbehaving agent's blast radius is bounded.

- [ ] **Given** an agent is running, **when** I set its status to `inactive`, **then** within a bounded and published interval every subsequent governed call from it is denied.
- [ ] **Given** I have stopped it, **when** I need to evidence the intervention, **then** there is a record of who stopped it and when. *Partly unmet, see gap **G4**.*

### US-5 — See what it costs and how it performs

**As the** AIMS product lead, **I want** cost and usage per agent and per model, **so that** I can
justify the platform and spot a runaway agent.

- [ ] **Given** traffic has flowed for a week, **when** I open the project's usage view, **then** I see requests, tokens, latency and cost broken down by agent and by model.
- [ ] **Given** I want cost per *incident* rather than per *request*, **when** I join platform telemetry to AIMS's own records, **then** the trace identifier is present on both sides. *Requires an AIMS-side join, see gap **G8**.*

### US-6 — Evidence the governance claim

**As** Corp IT compliance, **I want** a defensible record of what each agent did, **so that** AIMS can
answer an OSFI E-23 / B-13 question without a bespoke evidence exercise.

- [ ] **Given** a governed call, **when** I inspect the audit trail, **then** the actor, the target, the decision and the timestamp are present and immutable.
- [ ] **Given** an examiner asks which framework controls AIMS is assessed against, **when** I look for a framework catalogue in the platform, **then** — **today there is none, and OSFI is not represented at all.** See gap **G10**.

---

## 3. Capability selection (proposed — confirm in T1)

Mandatory baseline capabilities apply whether or not AIMS raised them; they are listed so the use
case acknowledges them, not so it chooses them.

| CAP | Capability | Governance | Verified status | Why AIMS needs it |
|---|---|---|---|---|
| CAP-01 | Agent registry | Mandatory | ✅ | RCA, Correlation, later Remediation |
| CAP-02 | Model registry | Mandatory | ✅ | Haiku and Sonnet, replacing direct integrations (E-3) |
| CAP-03 | MCP tool registry | Conditional — **triggered** | ✅ registry / ⚠️ per-tool control | Jira, Teams, knowledge base, AWS operations |
| CAP-04 | Deployment registry | Mandatory | ✅ | Credentials and policy attach to a deployment, not a catalog entry |
| CAP-05 | SSO / human identity | Mandatory | ✅ | Corp IT engineers in the portal |
| CAP-06 | Machine identity | Mandatory | ✅ | Each agent runtime authenticates as itself |
| CAP-07 | RBAC and access policy | Mandatory | ✅ | The agent × target matrix in the D2 |
| CAP-08 | Governed gateway | Mandatory | ✅ | The carrier for every other runtime control |
| CAP-09 | Policy enforcement | Mandatory | ✅ | Fail-closed on every call |
| CAP-10 | Guardrails | Mandatory | ✅ | Glue diagnostics and logs may carry personal or confidential data |
| CAP-11 | Kill switch | Mandatory | 🟡 | Named explicitly by AIMS (E-4 list) |
| CAP-12 | Quotas and budgets | Mandatory | ⚠️ | Bounded blast radius; AIMS asked for cost profiles |
| CAP-13 | Attribute tagging | Mandatory | ✅ | Classification and governance applicability |
| CAP-14 | Lifecycle and approvals | Mandatory | 🟡 | Gates the S4 Remediation Agent |
| CAP-15 | Risk tiering | Mandatory | ⚠️ | An agent with AWS write access is not the same materiality as one that summarises logs |
| CAP-17 | Evaluation and assurance | Conditional — **triggered by AIMS's own ask** | 🟡 | "Evaluations required" |
| CAP-18 | Audit trail | Mandatory | 🟡 | The traceability requirement |
| CAP-19 | Regulatory reporting | Mandatory | 📐 | The OSFI mapping is the use case's own framing |
| CAP-20 | Observability and cost | Mandatory | ✅ | Cost profiles, latency, per-agent attribution |
| CAP-21 | Single pane of glass | Optional — selected | ✅ | How AIMS will actually operate all of the above |
| CAP-24 | Chain authorization | Conditional — **triggered** | 🟡 | AIMS is multi-agent by design |
| CAP-26 | Jurisdiction / data-flow control | Conditional — confirm | 📐 | Canadian FRFI; residency posture to confirm in T1 |

**Not selected**: CAP-16 (model cards) and CAP-22/23/25 — proposed as out of scope. CAP-16 becomes
mandatory if Corp IT determines AIMS's models are in E-23 scope; that determination is [Q6](#9-open-questions).

---

## 4. Functional requirements

| ID | Requirement | CAP | Priority |
|---|---|---|---|
| FR-1 | Every AIMS agent is a **registered catalog entry** in a single owning project, with a permanent key, an owner and a status. | CAP-01 | Must |
| FR-2 | The AIMS **detection pipeline** — the non-agent workload that watches Glue and triggers an investigation — is registered as an **Application**, not as an agent, so it gets an identity and governed egress without being misclassified in the inventory. | CAP-01, CAP-06 | Must |
| FR-3 | Claude **Haiku** and **Sonnet** are registered models with a stable gateway slug, each with a **Bedrock offering** in `ca-central-1`. | CAP-02 | Must |
| FR-4 | Every AIMS **MCP server** is registered with an `http` or `sse` transport and a complete backend URL including scheme and path. `stdio` servers are out of scope by construction. | CAP-03 | Must |
| FR-5 | Each agent and application has a **deployment** on the environment's gateway, and exactly one active **machine credential** per (resource, gateway) pair, stored in Vault or AWS Secrets Manager and never in an image, a repository or a message. | CAP-04, CAP-06 | Must |
| FR-6 | **All** AIMS model traffic egresses through the Luminate gateway. Direct provider calls from AIMS code are removed, not merely deprecated — a bypassed gateway voids every control in this table. | CAP-08 | Must |
| FR-7 | **All** AIMS MCP tool traffic egresses through the Luminate gateway. | CAP-03, CAP-08 | Must |
| FR-8 | Access is **declared, not assumed**: an explicit access policy per (agent → model) and (agent → MCP server) pair. Absence of a policy denies. | CAP-07, CAP-09 | Must |
| FR-9 | Tool access is constrained to the **minimum set each agent's role requires**. Where the platform cannot express this per tool, the design must achieve it by other means (see G2 and D2 §DD-5). | CAP-03, CAP-07 | Must |
| FR-10 | **Guardrail evaluation on both request and response** is enabled for AIMS traffic, covering personal data that may appear in Glue diagnostics, log excerpts and stack traces. | CAP-10 | Must |
| FR-11 | An operator can **stop a named agent** and every subsequent governed call from it is denied. The propagation interval must be **measured and published**, not assumed. | CAP-11 | Must |
| FR-12 | Per-request **usage, latency and cost** are attributed to both the calling agent and the model used, and are visible in the portal without a bespoke query. | CAP-20 | Must |
| FR-13 | Every governed call produces an **audit record** carrying actor, target, decision and timestamp, immutable after write. | CAP-18 | Must |
| FR-14 | Each AIMS agent, model and MCP server carries **governance attributes** — at minimum owner, data classification and risk tier — so applicability and policy can target it. | CAP-13, CAP-15 | Must |
| FR-15 | AIMS's own **task-level records** (incident id, investigation outcome, time-to-diagnosis) are joinable to platform telemetry on a shared trace identifier. The platform supplies the identifier; AIMS supplies the task semantics. | CAP-20 | Should |
| FR-16 | The **kill-switch runbook** is written, rehearsed and owned before any AIMS agent runs unattended, and names both the platform lever and the AIMS-side lever. | CAP-11 | Must |
| FR-17 | An **approval gate** stands between a remediation recommendation and any infrastructure change, with the approver recorded. *(S4 — specify now, build when CAP-14 supports it.)* | CAP-14 | Must (S4) |
| FR-18 | Inter-agent hops (RCA → Correlation → Remediation) are **documented as ungoverned** and attributed per hop, until CAP-24 delivers chain authorization. No material may claim the hop is governed. | CAP-24 | Must |
| FR-19 | AIMS engineers can develop against **something** without a cluster round trip, and the difference between that and the deployed environment is written down. | INT-09 | Should |
| FR-20 | **Pre-production evaluation** of each agent against a held-out set of historical Glue failures, with a recorded pass threshold. Platform support is partial; the method is AIMS's to define. | CAP-17 | Should |

---

## 5. Non-functional requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Availability | AIMS is an **incident-response** system. Governed egress becoming unavailable must degrade AIMS's diagnosis, not its detection or its notification. | Detection and notification have no dependency on the gateway |
| NFR-2 | Latency | Added latency from governed egress must not materially extend time-to-diagnosis. | Gateway overhead measured and agreed in T12; budget set from the measurement, not before it |
| NFR-3 | Security | No credential in an image, repository, ticket or message. Tokens fetched on demand, held in memory, never written to disk. | Vault / Secrets Manager only |
| NFR-4 | Residency | All governed traffic and all telemetry remain in `ca-central-1`. | Confirmed per model offering and per gateway |
| NFR-5 | Attribution | Every governed call resolves to exactly one AIMS agent or application. No shared or anonymous credential. | One credential per (resource, gateway) |
| NFR-6 | Blast radius | An AIMS agent must not be able to reach a model or tool outside its declared policy set, including after a new tool appears on a server it already reaches. | Enforced by server-splitting (DD-5) until G2 closes |
| NFR-7 | Reproducibility | A past authorization decision can be reconstructed from the audit record and the policy generation in force at the time. | Audit record + policy version |
| NFR-8 | Honesty of claim | No control may be presented to Corp IT risk as available unless it is enforced at runtime. §7 is the reference for what may be claimed. | §7 governs all AIMS-facing material |

---

## 6. Capability gap register

Classified per the **Capability Gap Escalation** process: *component change* if closing the gap
requires Luminate itself to behave differently; *integration* if it is about reaching a Sun Life
system.

| ID | Capability | What is missing | Classification | Impact on AIMS | Escalation |
|---|---|---|---|---|---|
| **G1** | CAP-03 / CAP-08 | **Outbound authentication to an Okta-protected MCP backend.** `MCPServerIdentityMode` declares `injected_credential` and `external_exchange` for servers fronted by a third-party authorization server, and the model's own docstring says *"Neither mechanism is implemented yet — a server in either mode is served like `GATEWAY_IDENTITY`, with no credential sent."* `token_forward` only works where the backend trusts the gateway's issuer, which Okta does not. | Component change | **Blocks launch** for E-4 as described. The gateway would call AIMS's Okta-fronted servers with no credential and be rejected. | New EACPP ticket → consortium idea. Interim measure below. |
| **G2** | CAP-03 / CAP-07 | **Per-tool authorization.** `AccessPolicyTargetType` stops at `mcp_server`. `AccessPolicy.allowed_tool_ids` exists on the model, in the admin, in the serializers and in the demo data — and appears at runtime **only in `audit_snapshot()`**. No `.rego` file mentions a tool; the gateway tree has zero references. Modelled and auditable, not enforced. | Component change | **Degrades** — this is AIMS's stated requirement *"which agents should have access to which tools"*. Mitigated by DD-5. | New EACPP ticket → consortium idea |
| **G3** | CAP-24 | **Governed agent-to-agent calls.** `/a2a/` resolves in the gateway's routing middleware and `AgentAssignment` exists in the portal bundle, but `ResourceTranslator.translate()` loops only `llm_assignments` and `mcp_assignments` — `agent_assignments` is counted in a log line and nothing more. The gateway's own documentation is explicit: *"the translator does not emit it yet … nothing A2A is currently pushed to agentgateway."* | Component change | **Degrades** — AIMS is multi-agent. The RCA → Correlation → Remediation hops are ungoverned and attribution is per hop. | EACPP-770 (`distributed-gateway`) |
| **G4** | CAP-11 | **First-class kill switch.** Stopping an agent is a status edit: the fact export publishes only `status=ACTIVE` agents, so an edit removes it from the next policy bundle. No dedicated stop action, no cascade, no audited stop event — and no design upstream. | Component change | **Degrades** a control AIMS named explicitly. Mandatory for every onboarding, not just this one. | EACPP-646 (`agent-registry`) |
| **G5** | CAP-12 | **Quota enforcement.** Nothing debits a counter. `matched_quota_ids` is telemetry on the authz decision; the gateway has no quota references. | Component change | **Degrades** — no runtime cap on request or token volume. | EACPP-834 (`inference-economics`) |
| **G6** | CAP-12 | **Spend budgets.** `QuotaDimension` is `requests` and `tokens` only; the enum's docstring places `spend` in a later phase. | Component change | **Blocks** any dollar-denominated control. Cost *visibility* is unaffected — see §7. | EACPP-834 |
| **G7** | CAP-17 | **Evaluation.** No pre-production evaluation, no drift detection, no auto-demotion, no adversarial testing, and no design. | Component change | **Degrades** — AIMS states "evaluations required". | EACPP-647, EACPP-842 |
| **G8** | CAP-20 | **Task-level and reasoning metrics.** Per-request latency and cost exist. There is no notion of a *task*, a *completion outcome* or *reasoning quality*, so "task completion metrics" and "which query types take longer" cannot be answered by the platform. | Component change | **Degrades** — mitigated by the trace-id join (FR-15, DD-9), which AIMS owns. | New EACPP ticket; low priority relative to G1–G4 |
| **G9** | CAP-15 | **Risk triage.** The band already sets how much rigour applies — required controls, approval depth, capture policy and trust tier all resolve from it. What is missing is the method that **assigns** the band; `obligations.py` names Risk Triage as the input and it does not exist. | Component change | **Degrades** — an agent with AWS write access gets the rigour of whatever band a human typed, with no assessment behind it. | EACPP-648 |
| **G10** | CAP-19 | **Signed evidence pack.** OSFI *is* expressible — Governance Mode ships the regime schema and a worked `ca-osfi.json` example covering E-23 and B-13, and Sun Life supplies its own control catalogue (INT-10). What is missing is the **signed, immutable evidence pack** with crosswalks, coverage scoring and attestor signoffs; the governance-scoped export that ships today says in its own payload that it is not that artifact. | Component change | **Degrades** — AIMS can be governed against E-23 and reported on informally; it cannot yet be handed to an examiner as a signed pack. Build in flight under AIC-154. | EACPP-649 |
| **G11** | CAP-14 | **Multi-step / segregation-of-duties approvals**, and an enforced agent lifecycle state machine — `AgentStatus` has no transition guard anywhere in the application. | Component change | **Blocks S4** (Remediation Agent execution). Does not block the POC. | EACPP-915, EACPP-646 |
| **G12** | INT-09 | **Local development environment.** There is no local Luminate target for an AIMS developer; the portal and gateway are cluster-deployed. | Integration | **Workaround available** — develop against dev with an issued credential. Document the delta. | Product team board; no consortium ask |
| **G13** | CAP-18 | **External audit ingest.** The audit contract states there is *deliberately no public producer REST endpoint*. AIMS's detection pipeline cannot contribute its own events to the platform's audit trail. | Component change | **Degrades** — the audit trail covers governed calls, not the whole AIMS incident lifecycle. | EACPP-826 |

### Interim measures

Everything shipped to work around a gap, and the condition under which it is removed. Each is
**explicitly temporary** — none of these are the destination.

| Gap | Interim measure | Removed when |
|---|---|---|
| G1 | Reach AIMS MCP servers on a network path that does not require the Okta hop — a cluster-internal Service address rather than the Okta-fronted Route — with the server's own authorization retained inside the server. Decided by spike **T13**. | `external_exchange` or `injected_credential` is implemented |
| G2 | **One MCP server per trust boundary.** Split AWS operations into a read server and a write server, so server-level policy becomes tool-level policy in effect (DD-5). | `allowed_tool_ids` is evaluated at the gateway |
| G3 | Inter-agent hops go direct, each agent authenticates independently to the gateway for its own egress, and attribution is per hop. Documented, never claimed as governed. | A2A assignments are emitted by the translator |
| G4 | Written kill-switch runbook using the status edit, with a **measured** propagation time, paired with an AIMS-side circuit breaker so there are two independent levers (DD-8). | A first-class kill control ships |
| G5, G6 | Cost and volume **alerting** off Langfuse metrics rather than enforcement, with a named owner and a response action. | The counter store lands |
| G8 | AIMS emits its own task records keyed by the platform trace id (DD-9). | A task/outcome model exists upstream |
| G10 | Evidence assembled by hand from audit and usage exports for any OSFI question. Effort estimated and stated so it is not mistaken for automation. | A reporting capability with OSFI in its framework set ships |

---

## 7. Correcting the reference document's OSFI self-assessment

The reference document's table marks eleven of fifteen requirements **✅ Covered**. Verified against
`origin/main` @ `b04b0021`, **five of those are not**. This table is the authority for what may be
said to Corp IT risk (NFR-8); the reference document is not.

| Reference document row | Its claim | Verified | Why the difference |
|---|---|---|---|
| Agents registered through ACP registries | ✅ | ✅ | Agrees |
| Models registered through ACP registries | ✅ | ✅ | Agrees |
| Insights on agent cost and usage | ✅ | ✅ **for visibility** | Langfuse per-request cost, pricing catalogue, per-agent and per-model attribution all ship. Cost *control* is a different thing and does not (G6). |
| MCP servers registered and governed | ✅ | 🟡 | The registry ships. Reaching AIMS's servers **as described** does not (G1). |
| Agent observability and execution monitoring | ✅ | ✅ | Agrees |
| Governance status, audit trails, policy enforcement | ✅ | 🟡 | Enforcement and audit ship. No governance *reporting* surface exists (G10). |
| Future approval workflows | 🟡 | 🟡 | Agrees, and correctly marked future |
| **Kill switches** | ✅ | **🟡** | A status edit that drops the agent from the next policy bundle. No dedicated action, no cascade, no audited stop event, no upstream design (G4). **The sharpest correction in this table.** |
| Traceability of which agent triggers which process/tool | ✅ | ✅ | Agrees, for traffic on the gateway path |
| Reasoning metrics | ✅ | **❌** | Latency and token counts exist. Nothing models reasoning quality (G8). |
| Task completion and performance metrics | ✅ | **❌** | The platform has no concept of a task or an outcome (G8). |
| Cost profiles at LLM and agent level | ✅ | ✅ | Agrees — this one is genuinely covered |
| Agent evaluations | 🟡 | 🟡 | Agrees; the document is right to hedge |
| Controls over MCP — which agents access which tools | ✅ | **⚠️** | Per **server**, not per tool. `allowed_tool_ids` is modelled and audited, never evaluated (G2). |
| MCP servers governed by Okta / API platform | 🟡 | **❌ as described** | The mechanism for a third-party-authorized backend is declared but unimplemented (G1). |

**And the row the document does not have.** Its entire regulatory framing is OSFI. That framing is
supportable — Governance Mode ships the regime schema and Sun Life supplies the E-23/B-13 control
catalogue — but the *examiner-facing artifact* is not built (G10). The platform can **govern** AIMS
against E-23 today and export what governance can stand behind; it cannot yet hand over a signed,
immutable evidence pack.

---

## 8. Constraints

- **Three AIMS workloads are already in production** (E-1). Onboarding must be additive and reversible per workload; a POC that requires a production cutover is the wrong shape.
- **Dev is the only environment available.** Test, stage and prod are "coming soon" in the published environments table. POC scope is dev.
- **`ca-central-1` only**, for both the Bedrock offering and the gateway (NFR-4).
- **Deployment, credential issuance, gateway/environment creation, quota setting and governance attributes cannot be delegated** by any role. Every one of those steps routes to the ACP Product Team, by design.
- **Project is permanent** on every registered resource, and a catalog entry cannot be deleted once deployed. Naming and project placement are one-way doors (DD-1).
- **Credentials are show-once**, one active per (resource, gateway), with **no overlap window** on rotation.
- A credential issued today may not carry the gateway audience (**AIC-589**); the platform team attaches it after issue until that fix ships.

---

## 9. Open questions

| ID | Question | Owner | Blocks |
|---|---|---|---|
| **Q1** | Which of the nine AIMS projects (6 MVP, 3 production) are in POC scope, and are any of the three production workloads included? | AIMS (Dragna) | T1, and the whole D3 sequence |
| **Q2** | Which agents run on Lambda, which on OpenShift, and what does "proxies" denote in E-2? Egress proxy, sidecar, or something else? | AIMS | T13, DD-4, DD-7 |
| **Q3** | What is "AWS Quick"? | AIMS | Scope only |
| **Q4** | Are the AIMS MCP servers reachable on a cluster-internal address, or only through the Okta-fronted Route? | AIMS + Platform | **G1 / T13 — the critical path** |
| **Q5** | Does AIMS have a Bedrock consumer account with Anthropic model access in `ca-central-1`, or does it consume Anthropic another way today? | AIMS + Platform | T6 |
| **Q6** | Are AIMS's models in OSFI E-23 scope as Corp IT reads it? Determines whether CAP-16 (model cards) becomes mandatory. | Corp IT risk | CAP-16 selection |
| **Q7** | What data classification applies to Glue diagnostics, log excerpts and stack traces reaching a model? Sets the guardrail configuration. | AIMS + data governance | T20 |
| **Q8** | Who is the named owner of the kill-switch runbook, and what is the acceptable propagation time? | AIMS + Platform | T18 |
| **Q9** | Does AIMS accept the interim per-hop attribution for its multi-agent flow (G3), or is governed A2A a launch condition? | AIMS | Sets G3 severity |

---

## 10. Traceability

| Requirement | CAP | Reference document ask | D0 success criterion |
|---|---|---|---|
| FR-1, FR-2 | CAP-01 | "Agents registered and managed through ACP agent registries" | All AIMS agents discoverable via ACP catalogue |
| FR-3 | CAP-02 | "Approved foundation models … instead of direct integrations" | Models consumed via registry |
| FR-4, FR-7, FR-9 | CAP-03 | "MCP servers … registered and governed"; "controls over MCP" | MCP registry operational |
| FR-5 | CAP-04, CAP-06 | Implicit in "ACP as the common platform" | — |
| FR-6, FR-8 | CAP-08, CAP-09 | "Policy enforcement" | Policy enforcement for approved models and tools |
| FR-10 | CAP-10 | Not raised — **mandatory baseline** | — |
| FR-11, FR-16 | CAP-11 | "Kill switches" | — |
| FR-12, FR-15 | CAP-20 | "Insights on cost and usage"; "cost profiles at LLM and agent level" | Cost per agent per week visible |
| FR-13 | CAP-18 | "Audit trails"; "which agent is triggering which process and tools" | 100% audit trail coverage |
| FR-14 | CAP-13, CAP-15 | Not raised — **mandatory baseline** | — |
| FR-17 | CAP-14 | "Future approval workflows" | Manual approval tracked for remediation |
| FR-18 | CAP-24 | Implicit in the multi-agent roadmap | — |
| FR-19 | INT-09 | "Local environment" | — |
| FR-20 | CAP-17 | "Evaluations required" | — |

Every functional requirement traces to a capability. Every capability that is not ✅ appears in §6.

## References

- Spec: [D0](d0-discovery.md) · [D2](d2-design.md) · [D3](d3-tasks.md)
- Epic: [EACPP-909](https://sunlife.atlassian.net/browse/EACPP-909)
- [ACP Capability Map](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/docs/capability-map.md) · [Capability Gap Escalation](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/docs/process/capability-gap-escalation.md)
- [Luminate User Guides](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides) — the operational procedures the D3 tasks follow
- Source: [`references/ACP-AIMS.docx`](references/ACP-AIMS.docx)
- Capability verification: `AI-Consortium/luminate` `origin/main` @ `b04b0021`, 2026-08-28
