# CAH Agentic Stack - ACP Onboarding Submission (V2)

> Onboarding payload from Sri's team (Cloud Infra AI Platform / Agentic Cloud Provisioning Platform) to ACP. We are the data plane asking to be registered and governed.

**Date:** 2026-08-30  
**Status:** publish-ready for ACP review  
**Audience:** Seth Chalmers / ACP internal MVP team  
**Framing:** client onboarding submission, not a peer architecture tour

**Settled decisions (do not re-open):**

- Integration seam is AgentGateway.
- Our preference is gateway-of-gateways: our AgentGateway stays in our cluster for tenant/app authorization and routes model, MCP, and A2A traffic to ACP. If ACP requires a full swap so their proxy sidecar is the front door with central policy management, we accept that. Not a blocker.
- Trust and credential model follows ACP's front-door design.
- Model, MCP, and A2A traffic are governed traffic classes through the gateway surface.
- Model calls route through the gateway to Bedrock in our account via assumed role, never direct agent-to-Bedrock for governed traffic.
- OTel emitted to the gateway path is auto-ingested by ACP.
- MCP routing behaviour is identical because ACP uses the same AgentGateway binary plus configuration.
- ACP governs the invocation of durable work through named Tool/MCP and A2A capabilities; Temporal engine internals remain ours.
- Pilot starts in DEV; DEV agents connect to ACP's PROD control plane as expected centrally managed behaviour.

**ACP governs four traffic classes across this surface:** **(1) front door**, **(2) Agent → Bedrock**, **(3) Agent → Tool / MCP**, and **(4) Agent → Agent (A2A)**. Calls that trigger Temporal-backed work are governed as class 3 or class 4; there is no separate Agent → Temporal integration seam.

---

## 1. Who we are

We are the Cloud Infra AI Platform (also called the Agentic Cloud Provisioning Platform / CAH Agentic Stack). We run durable, governed cloud-infrastructure work: workload account provisioning, FinOps analysis, CMDB and APM lookups, software audit, and related capabilities. Callers submit a request against a named capability, receive a handle, and poll status. We own retries, timeouts, persistence, and the approved capability set.

Four concerns, four owners: LangGraph talks to humans and chooses tools; AgentGateway is the trust boundary and tool proxy; webhook-receiver and domain MCP servers turn approved calls into durable work; Temporal plus workers execute that work. Business logic lives in workflows and activities. Everything else is transport.

**What we ask ACP to onboard:** the **AgentGateway surface** on our agentic EKS cluster. Nova, CloudFlux, Stratosphere, and any future LangGraph agent behind that surface inherit governance by construction. Those names are examples of agents behind the gateway, not a closed roster and not a fixed agent count.

---

## 2. Governance surface for ACP registry

ACP onboards and governs the **AgentGateway surface / service identity**, not a per-agent inventory.

| Item | Value |
| - | - |
| What is registered | The gateway surface that fronts model, MCP, HTTP capability doors, and A2A traffic |
| Proposed registry identity | `cah.agentgateway-surface` **(proposed; ask human)** for the final ACP registry string |
| What inherits governance | Every LangGraph agent and dual-entry capability behind that surface (examples: Nova, CloudFlux, Stratosphere, and future agents) |
| What is not registered | One ACP agent id per persona or deployment. Product personas remain our internal `AGENT_PROFILE` concern |

Agents behind the surface are MCP clients of AgentGateway. For normal capability work they are not Temporal clients; the default path is gateway → MCP/HTTP → webhook-receiver / domain MCP → Temporal inside our boundary.

---

## 3. Model access needs

**Governed traffic class 2: Agent → Bedrock.**

### Target governed models

| Use | Model family / id | Region | Transport |
| - | - | - | - |
| Assistant chat (Nova profile and similar) | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (configured across DEV/SIT/PROD overlays; settings default matches) | Primary: `ca-central-1` | Through AgentGateway |
| Automation assistant (CloudFlux profile) | Profile pin `us.anthropic.claude-opus-5`; overlay fallback `BEDROCK_MODEL_ID` Sonnet 4.5 if pin absent | `ca-central-1` | Through AgentGateway |
| Platform embeddings | `amazon.titan-embed-text-v2:0` on AgentGateway Bedrock embeddings backend | `ca-central-1` | Through gateway AI backend |

### What we need ACP to govern

- All governed model traffic routes **through AgentGateway** to **Bedrock in our workload account**. Direct agent-to-Bedrock is the anti-pattern ACP and we both want closed for governed paths.
- Assistants behind the surface must select the models above (and future Bedrock Anthropic / Titan ids we pin in config) without bypassing the gateway.
- ACP registry and gateway policy must constrain each surface to its approved model identifiers; unrestricted client-selected model forwarding is not the target contract.
- **Trust and credential model follows ACP's front-door design.** If ACP is the front door managing environments and regions, assumed-role trust packaging is defined by ACP. We do not assert self-managed versus Service Catalog as our choice.

### Model auth legs (inbound vs outbound)

Two distinct legs. Do not collapse them into one "API key to Bedrock" story.

| Leg | Direction | Auth |
| - | - | - |
| Inbound | Caller → AgentGateway PROD **:5557** platform model routes (`/v1/chat/completions`, `/v1/embeddings`) | AgentGateway **`apiKey`** policy, `mode: strict`. Wire header is **`Authorization: Bearer <platform-key>`** (Solo default; no `location` override in the PROD route policies). This is a platform API key, not an Entra JWT and not a Bedrock credential. |
| Outbound | AgentGateway → Bedrock | **SigV4**. Primary identity is **IRSA** on the AgentGateway ServiceAccount. Fallback is an IAM user credential projected from Vault. Cross-region inference: caller pods run in **`ca-central-1`**; the model may resolve in **`us-east-1`**. |

Token spend tracking exists on our side for assistant usage (SQL / spend-by-model artifacts in the langgraph deployment). Richer ACP budgeting is acknowledged as ACP roadmap; our minimum needs are in section 11.

---

## 4. MCP tools and capabilities catalog (target governed contracts)

**Governed traffic class 3: Agent → Tool / MCP.** Triggering a named Temporal-backed capability is governed here as a normal Tool/MCP invocation; the engine behind that capability remains internal.

We expose **named capabilities** only. We do not expose Temporal endpoints, namespaces, task queues, or workflow class names as an ACP interface.

Capabilities sit behind AgentGateway MCP federation and, for some, dual HTTP doors. Intended callers: agents behind the gateway surface, Backstage / C# Automation API service principals, and (via HTTP) pipelines that enter through the gateway.

**This section is the registry inventory for prioritization, not day-one pilot scope.** Section 13 defines pilot order. Non-reference capability rows are inventory only; contract details are supplied when a row is prioritized. Data Gravity remains live on the federated list.

### 4.1 Federated MCP backends (AgentGateway target list)

| MCP backend name | Role | Intended callers |
| - | - | - |
| `webhook-receiver` (`provisioning-tools` FastMCP name) | MCP surface hosting several tools | Agents via AG |
| `secops-mcp` | SecOps workflows (incident summary) | Agents via AG |
| `cmdb-mcp` | CMDB / app topology read APIs | Agents via AG |
| `observability-mcp` | Live APM agent/host metrics | Agents via AG |
| `provisioning-mcp` | Workload account provisioning trigger / status / approve | Agents via AG |
| `finops-mcp` | Cost analysis and related FinOps tools | Agents via AG |
| `devtools-mcp` | Dev tools (calculator, PR review helpers) | Agents via AG |
| `aws-identity-mcp` | AWS identity / session tools | Agents via AG |
| `datagravity-mcp` | CMDB-oriented Data Gravity tools | Governed CMDB-oriented callers |

### 4.2 Named capabilities (MCP and/or HTTP)

| Capability | MCP tool(s) | HTTP door | Notes |
| - | - | - | - |
| Workload account provisioning | `trigger_workload_provisioning`, `check_workload_provisioning_status`, `approve_provisioning` on `provisioning-mcp` | `POST /trigger-workload-provisioning`, `GET /workload-provisioning-status/{workflow_id}`, `POST /approve-provisioning/{workflow_id}`, `POST /reject-provisioning/{workflow_id}` on webhook-receiver (AG-fronted) | Reference dual-entry capability. Full field tables, OpenAPI stub, and operational detail are in **Appendix A**. |
| Cost analysis | `trigger_cost_analysis`, `check_cost_analysis_status` | `POST /trigger-cost-analysis`, status route on webhook-receiver | Durable FinOps |
| APM utilization analysis | `trigger_apm_analysis`, `check_apm_analysis_status` (webhook-receiver MCP) | `POST /trigger-apm-analysis`, `GET /apm-analysis-status/{workflow_id}` | Durable |
| Software audit | `trigger_software_audit`, `check_software_audit_status` | HTTP status/trigger patterns exist in receiver family | Durable |
| Business app search | `search_business_apps_tool` | Finops path also searches CMDB | Read-only helper |
| Computer search | `search_computers_tool` | n/a | Read-only CMDB helper |
| CMDB app inventory / topology | `cmdb_list_apps`, `cmdb_get_app_*`, fleet/compliance tools | n/a | Read-oriented |
| APM live status | `apm_get_host_agents_status`, `apm_get_app_agents_live`, `apm_get_agent_metrics` | n/a | Read-only |
| Incident summary | `trigger_incident_summary`, `check_incident_summary_status` | n/a | Durable secops |
| AWS identity helpers | `aws_identity_*` tools | n/a | Identity session helpers |
| Calculator / PR review | `calculate`, `nova_pr_review` | n/a | Devtools |
| LangGraph converse / REST | Not MCP tools; HTTP `/converse`, `/conversations`, `/health`, `/tools/dispatch` on :5555 | Backstage → AG → langgraph | Agent runtime surface, not a Temporal capability |

Version pins for each tool schema: **(ask human)** for the ACP registry version string we should publish per tool. Runtime list_tools via MCP is available on each server; whether ACP prefers discovery or a pinned catalog is an open alignment question (see section 15).

---

## 5. Agent-to-agent (A2A) surface

**Governed traffic class 4: Agent → Agent (A2A).** Reaching durable coding work through the adapter is governed as an A2A invocation; the engine behind the adapter remains internal.

### Adapter mechanism (code-grounded)

| Fact | Verified shape |
| - | - |
| Listener | AgentGateway port **5557** is an A2A passthrough / catch-all (same port also carries path-matched in-cluster MCP and platform Bedrock routes). |
| Gateway behaviour | Gateway terminates **Entra JWT** on the A2A catch-all, then **opaque-forwards** literal HTTP without A2A protocol awareness. |
| Protocol | Standalone adapter exposes `GET /.well-known/agent.json`, JSON-RPC 2.0 A2A **v0.2** methods `tasks/send`, and SSE `tasks/sendSubscribe` over HTTP/JSON-RPC/SSE. |
| Capability mapping | Adapter validates ticket id and requirements, starts durable coding work behind our boundary, waits or streams, and maps the result to an A2A Task artifact. |
| Credentials at adapter | Adapter holds **only** a Temporal client. No Bitbucket token and no Bedrock credentials. |
| Network trust | NetworkPolicy admits **only AgentGateway** ingress to the adapter. |
| Pattern evidence | One LangGraph path can call coding work through this adapter. That proves the adapter mechanism without making Coder a production agent inventory item or prescribing it as the default route. |

### A2A governance placement

Given this adapter shape, where does ACP governance sit: at the ACP front proxy, at the A2A route on the gateway, or in front of the adapter boundary? We describe the seam; placement is ACP's call.

---

## 6. Gateway deployment and trust

**Governed traffic class 1: front door.**

### Our preference: gateway-of-gateways

Our AgentGateway remains in our agentic EKS cluster. It continues to enforce our tenant/app authorization and routes model, MCP, and A2A traffic so ACP can see and govern it. Rationale:

- We already run Solo.io AgentGateway between Agent↔MCP, Agent↔LLM provider, and Agent↔Agent.
- ACP's gateway is the **same AgentGateway binary** with additional configuration (extAuthz to Management Plane, LLM proxy, Admin UI, ACP MCP registry backend). MCP routing behaviour stays identical.
- We continue to layer our own CEL / route policies in addition to ACP policies where ACP's model allows composition.

### Accepted reality: full swap

If ACP requires a full swap so their proxy sidecar is the front door with central policy management, we accept it. Not a blocker. Replacement shape is ACP-configured AgentGateway as the governed front door, not a parallel second data plane we run against ACP's intent.

### Trust / credentials

**Trust and credential model follows ACP's front-door design.** Assumed-role packaging for Bedrock in our account is defined by how ACP fronts environments and regions.

### Tenant and app authorization after a full swap

Does our tenant/app authorization survive the swap, and where is it enforced: at the ACP front door, or as a thin retained authz layer behind ACP? Identity detail is in section 8.

---

## 7. Network and TLS

### Server-side TLS (what is real)

AgentGateway serves a **verifiable DNS-name server certificate** provisioned from **HCP Vault** through a **VSO-managed** secret (`agentgateway-tls-cert`, fullchain leaf+CA+root). AgentGateway terminates TLS in-pod on the MCP HTTPS listener. This provides **transport encryption and server identity**. Caller identity is token-based and separate (section 8).

Any model, MCP, or A2A traffic that crosses a cluster or control-plane trust boundary must use this server-side TLS front door. Plain `:5557` traffic is an internal east-west hop only and is not the cross-boundary ACP contract.

| Item | Target fact |
| - | - |
| Cluster | Our agentic EKS clusters (DEV / SIT / PROD agentic). Exact cluster names and account identifiers: exchanged offline **(ask human)** for the formal allow-list packet; not embedded here. |
| NLB | Internal NLB, L4 passthrough for MCP HTTPS. Backend protocol TCP; **443 → 5555**. |
| TLS on :5555 | Native HTTPS in AG. Server certificate as above. |
| Cert / friendly URL work | **Reza** owns cert and friendly URL work for gateways. ACP overlay needs Traefik IngressRoute for ACP UI and TLS on the NLB for LLM/MCP endpoints; we align with Reza on that. |
| :5557 | Plain HTTP for in-cluster east-west (no TLS block on that listener in base). Trust is NetworkPolicy + route policy + jwtAuth/apiKey per path. |
| :5559 | Internal gRPC front used by our workers to reach Temporal. **Not an ACP application API.** |

### Ports

| Port | Role | Ours | ACP addition |
| - | - | - | - |
| 5555 | MCP over HTTPS + langgraph edge routes + AG-fronted REST prefixes | Yes | Keep 5555 (ACP default 3000 is fine to remap; we standardize on 5555) |
| 5557 | A2A + in-cluster MCP + platform LLM path matches | Yes | Governed by ACP config |
| 5559 | Internal worker → Temporal gRPC path | Yes | Engine-internal path, not one of the four governed agent traffic classes and not an ACP product API (section 14) |
| 4000 | LLM proxy | n/a | ACP addition |
| 15000 | Admin UI | n/a | ACP addition |
| 19000 | AG adminAddr (localhost in our config) | Local admin bind | Distinct from ACP Admin UI 15000 |

### Unknowns (do not invent)

- Public or private DNS names for friendly URLs: **(ask human)** (Reza + ACP)
- Private CA trust bundle ACP clients must install: **(ask human)**
- Cross-account / cross-cluster allow-list entries ACP needs from us: **(ask human)**
- Exact reachability from ACP Management Plane to our sidecar (peering, PrivateLink, etc.): **(ask human)**
- Ingress specifics for ACP UI Traefik route in our cluster: **(ask human)** with Reza

---

## 8. Identity and authorization

### Production scope (design rationale)

Production agents today do **assistant and RAG work, plus a few tools**. There is **no production infrastructure provisioning or action-taking agentic work**. That scope is why on-behalf-of (OBO) has not been required for production traffic.

### Service-identity auth at the gateway

Auth at AgentGateway is **service identity**. The gateway verifies the **Backstage application Entra token** using **`appid` / `tid`**. There is **no OBO flow** and the **end-user token is not verified at the gateway**.

Per-path auth detail for edge, east-west, A2A, and platform model routes is in **Appendix A.12**.

### Human approval provenance

Human approval for durable flows is authenticated and authorized in the **Backstage UI**. Backstage verifies the person is entitled to view and approve, then fires a **webhook** to the waiting Temporal flow. Approval provenance is intact at the UI layer. This is not an audit gap under the current Backstage-mediated approval path. At the ACP/receiving boundary the call presents as the Backstage service identity, so cross-system audit joins correlate the durable approval event back to Backstage's authenticated approval record.

### OBO as future target

OBO becomes relevant when request or approval moves **outside** Backstage (for example Teams), where the "UI already verified them" guarantee no longer holds and the user principal must travel.

**Recommended target for auditability:** for future capabilities with human requesters or approvers outside the Backstage UI, propagate the end-user principal into ACP using OBO or a forwarded user claim so traces and approvals are attributable to a person, aligning with the OSFI/NIST audit story.

### Model auth legs

Canonical inbound/outbound model auth is in the **section 3** table; the full per-path matrix is in **Appendix A.12**.

### Destination composition with ACP

- extAuthz hook from gateway to ACP **Management Plane**
- **CEL** policies evaluated locally at the gateway
- **OPA** / Management Plane fallback
- ACP test posture: **`failureMode: allow`** (non-blocking) while ACP tests, moving to enforce when ACP is ready
- We keep route-level jwtAuth / apiKey / NetworkPolicy layers and expect ACP policies to compose where the front-door model allows

### User principal at the ACP front door

Does ACP's front door consume and enforce a user principal, and does our current app-token trust model survive the swap?

Credential lifetimes and rotation procedures for platform API keys and Entra app secrets: **(ask human)** for the shared runbook; we do not publish values.

---

## 9. Observability and correlation

### What we accept / will do

- Emit **OTel / OTLP** to the **cluster collector** and keep governed traffic on the **gateway** path so ACP can auto-ingest traces.
- We do **not** POST telemetry directly to an ACP application server.
- Management Gateway sidecar emitting **authz decision** traces out-of-band is acknowledged and welcome.

### Target correlation model (two IDs)

| ID | Role |
| - | - |
| W3C **`traceparent`** | Distributed-trace key. Target format is W3C Trace Context (OpenTelemetry default propagation). Route through the gateway so an OTel-native ACP correlates automatically. |
| Durable opaque **`workflow_id`** | Our natural durable handle for Temporal-backed capabilities. One operation is findable by both IDs. This is intentional, not a compromise. |

**W3C is target, not current first-party emission.** Today LangGraph mints a server UUID `request_id` and may store optional `X-Correlation-ID` as `upstream_correlation_id` (neither used for auth); no first-party `traceparent` handling was found in LangGraph or worker source during this review.

### Other observability notes

- Temporal history remains source of truth for durable workflow progress **inside our boundary**; ACP should correlate on gateway/MCP/LLM spans, not by reading Temporal.
- ACP storage model (acknowledgement only): registries in **Postgres**; most traces as immutable **Iceberg** tables in **S3** (OSFI-oriented). We do not manage those stores.
- Langfuse is optional product LLM tracing, complementary to ACP's control-plane store, not a dependency for ACP onboarding.

### Unknowns

- Exact OTLP endpoint / protocol options in our clusters: **(ask human)**
- Whether ACP grants us read access to Iceberg/Postgres traces for joint incident work: **(ask human)**

### Correlation contract confirmation

Confirm ACP keys on **`traceparent`**. Should business identifiers (request id, change id) travel in W3C **Baggage** or be echoed on the handle, versus only the trace id? Baggage is plaintext and must contain **no secrets**.

---

## 10. Policy, guardrails, and kill switch

### We accept ACP's model

- **Redis pubsub** kill switch (near-instant)
- Policy bundle polling on the order of **~15 seconds**
- Non-blocking `failureMode: allow` during ACP test phase, moving to enforce when ACP is ready

### Our own named policies (grounded)

- AgentGateway **route policies**: Entra jwtAuth + appid/tid authorization rules on edge routes; apiKey on PROD platform LLM routes; NetworkPolicy namespace allow-lists for east-west.
- LangGraph **product guardrails**: identity lock, tool entitlement sets per profile (`entitled_tools`), navigation route allow-list for Nova, refusal of harmful/manipulative misuse.
- webhook-receiver **admission rules**: validated fields on workload provisioning; rate limits; AG-fronted vs bearer paths; fail-closed external isolated provisioning.
- Bedrock **content Guardrail** policy assignment for the ACP registry: **(ask human)**.

### Kill-switch granularity

We need ACP to clarify binary vs graduated kill for conversational agents vs side-effecting provisioning capabilities. Listed under open questions. Until then we assume ACP can stop gateway-routed traffic for our registered gateway surface.

---

## 11. Cost and tagging

### Baseline

- Basic **token tracking** on our side for assistant usage (spend-by-model style artifacts in langgraph).
- ACP basic token tracking acknowledged; richer budget and chargeback is **ACP roadmap**.

### Minimum needs we want ACP to support when available

| Dimension | Need |
| - | - |
| Per capability | e.g. workload provisioning vs cost analysis vs chat completion |
| Per run / handle | Tie spend to `workflow_id` / conversation where applicable |
| Per project | Tag from request metadata when present (business application, request id) |
| Per business unit / cost centre | We already collect `cost_centre` on workload provisioning; want that available for chargeback join |

**Granularity ACP can support in the MVP now:** **(ask human)** (also open questions). We will tag what we can at the gateway and in our own logs regardless.

---

## 12. Regulatory evidence needs

Pilot has **no hard OSFI/NIST bar yet**, but we design for retrieval on demand.

| Evidence class | Why we need it |
| - | - |
| Traces | Reconstruct who called which model/tool through the gateway |
| Authz / policy decisions | Prove allow/deny and extAuthz outcomes |
| Approvals | Workload provisioning has an explicit manager-approval mid-flow; approval events must be retrievable. Backstage UI authenticates the approver before the webhook to Temporal. |
| Agent and model registry snapshots | Which gateway surface / model versions were allowed at time T |

We rely on ACP's Iceberg/S3 immutability story for control-plane evidence. Our Temporal and application logs remain internal operational evidence, not a substitute for ACP's store.

---

## 13. Environments and pilot scope

| Stage | Scope |
| - | - |
| **First environment** | **DEV.** ACP manages environments and regions centrally, so our **DEV agents connect to ACP's PROD control plane**. DEV-to-ACP-prod is expected centrally managed behaviour, not SID-to-SID pairing. |
| **Slice 1 (DEV)** | **Model + MCP governance for assistant agents.** Route LLM and MCP traffic through the ACP-configured gateway; prove trace ingestion, policy enforcement, and kill switch. Low risk: mirrors what assistants already do through AgentGateway. |
| **Slice 2 (DEV)** | **One durable dual-entry workload-provisioning capability** governed end to end, to exercise the approval and audit path. This capability is **not in production today**. Staged **second**; it does **not** gate slice 1. |
| **Then** | SIT, then PROD, only after joint acceptance criteria. |
| **Timeline** | **(ask human)**, defined with Mark Hanson and Seth Chalmers |
| **Acceptance criteria** | **(ask human)**, defined with Mark Hanson and Seth Chalmers |

---

## 14. ACP governs the four traffic classes; the Temporal engine stays internal

**Constraint, not a negotiation.**

- ACP governs **all four traffic classes**: front-door ingress, Agent → Bedrock, Agent → Tool / MCP, and Agent → Agent.
- That governance includes calls that trigger durable, Temporal-backed work. A named capability invoked through Tool/MCP or A2A is governed at the **submit → handle → status** edge.
- ACP does **not** receive Temporal engine internals: no Temporal endpoints, namespaces, task queues, worker credentials, or generic "start any workflow" access.
- We expose **named capabilities** only. Handles are opaque ids (`workflow_id` strings); callers never need Temporal engine semantics.
- Port **5559** is our internal worker → Temporal path. It is not one of the four governed agent traffic classes and is not an ACP product API.

---

## 15. Open questions for ACP (alignment only)

These are questions **to ACP**, not invented answers.

1. **Gateway swap and tenant/app authorization:** If ACP is the front door, does our tenant/app authorization survive, and where is it enforced (ACP front door vs thin retained authz layer)? Does the front door consume/enforce a user principal, and does current app-token trust survive the swap?
2. **A2A governance placement:** For our JWT-terminate then opaque-forward A2A adapter shape, does ACP govern at the front proxy, the A2A route, or the adapter boundary?
3. **Runtime capability discovery** (MCP `list_tools`) versus a **pinned versioned contract** in the ACP registry. Which does MVP require?
4. **Correlation:** Confirm ACP keys on W3C `traceparent`. Should business request/change ids travel in W3C Baggage or be echoed on the handle? (No secrets in baggage.)
5. **Cost granularity and kill-switch granularity:** What cost dimensions does ACP MVP support now (token only vs per capability / per run / per project / per BU)? Is kill switch binary per surface, or graduated for side-effecting capabilities?

---

## Appendix A. Workload account provisioning reference contract

Reference dual-entry capability. HTTP contract from `webhook-receiver`; MCP contract from `provisioning-mcp`. Full detail lives here so the main submission stays short.

### A.1 Submit contract (HTTP `POST /trigger-workload-provisioning`)

Body is JSON. Fields read in code:

Defaults below are receiver fallbacks when a field is omitted. They are not recommended pilot or production values; ACP clients should send their approved values explicitly.

| Field | Type | Required | Default / enum / validation |
| - | - | - | - |
| `conversation_id` | string | **Yes** (with account_name, environment) | Non-empty after trim |
| `account_name` | string | **Yes** | 2-63 chars; must match `^[a-zA-Z0-9][a-zA-Z0-9._-]{1,62}$` |
| `environment` | string | **Yes** | Mapped then must be one of `development`, `staging`, `production`. Input aliases mapped: `dev`/`test`→development, `stage`/`staging`→staging, `prod`/`production`→production |
| `region` | string | No | Default `ca-central-1`. If set, one of: `ca-central-1`, `us-east-1`, `us-east-2`, `us-west-2`, `eu-west-1`, `eu-west-2`, `ap-southeast-1`, `ap-east-1` |
| `cost_centre` | string | No | Default `CC-12345`. If set, must match `^([A-Za-z]{1,5}-)?[0-9]{3,10}$` |
| `ad_groups` | string or string[] | No | Default `APP-PHOENIX-DEVOPS,APP-PHOENIX-READONLY`. Arrays joined with commas. Each group: `^[A-Za-z][A-Za-z0-9._-]{0,63}$` |
| `use_aap` | bool | No | Default `false` |
| `account_type` | string | No | Default `workload`. Enum: `workload`, `sandbox`, `poc`, `shared-services` |
| `account_owner` | string | No | Default `""`. If set, email regex |
| `contact_email` | string | No | Default `""`. If set, email regex |
| `organization` | string | No | Default `""`. Safe charset; max 256 |
| `data_classification` | string | No | Default `sl-confidential`. Enum includes `public`, `internal`, `sl-confidential`, `sl-restricted`, `sl-public`, `sl-internal` |
| `data_residency` | string | No | Default `""`. Safe charset; max 256 |
| `support_group` | string | No | Default `""`. Safe charset; max 256 |
| `business_application` | string | No | Default `""`. Safe charset; max 256 |
| `is_genai_workload` | string (or value stringified) | No | Default `"No"` |
| `tfcb_onboarding` | string (or value stringified) | No | Default `"No"` |
| `ad_group_domain` | string | No | Default `""` |
| `new_ad_group_name` | string | No | Default `""` |
| `existing_ad_group` | string | No | Default `""` |
| `requester` | string | No | Default `""`. Safe charset; max 256 |
| `department` | string | No | Default `""`. Safe charset; max 256 |
| `budget_amount` | string/number | No | Default `""`. If set, numeric 0..10_000_000 |
| `form_data_summary` | string | No | Default `""` |
| `request_id` | string | No | Default `""`. If set, must be UUID. When present **and** essential inline fields missing, receiver may fetch form data from C# API |

Required triad after fallback: `account_name`, `environment`, `conversation_id`.

### A.2 Handle response

HTTP 200 JSON:

```json
{
  "workflow_id": "workload-acct-<account_name_lower>-<8 hex chars>",
  "message": "Workload provisioning started for account <account_name>. Workflow ID: <workflow_id>."
}
```

`workflow_id` is the opaque **handle**.

### A.3 Status contract (`GET /workload-provisioning-status/{workflow_id}`)

Built by `build_workflow_status(..., result_key="provisioning_result")`.

| Field | When present | Meaning |
| - | - | - |
| `workflow_id` | always (on success path) | Handle |
| `status` | always | Temporal status **name** string from describe, or synthetic `NOT_FOUND` / `ERROR` before HTTP mapping |
| `progress` | when activity order used | e.g. `"3/8 steps complete"` |
| `steps` | when activity order used | Array of `{ "step": n, "name": "{label}", "status": "completed or pending" }` |
| `provisioning_result` | when Temporal status is `COMPLETED` | Terminal workflow result payload |
| `error` | failure / not found / result retrieval failure | Human-readable error string |
| `approval_required` | HTTP status handler when `RUNNING` and exactly 4 steps completed | `true` |
| `approval_message` | same | `"Manager approval is required to continue provisioning."` |

### A.4 Terminal result payload (two-layer status model)

The outer `status` reports the Temporal execution state. The business outcome is nested under `provisioning_result.status`. Approval rejection and approval timeout return normally from the workflow, so their outer Temporal status is `COMPLETED`, not `FAILED` or `TIMED_OUT`.

| Business outcome | `provisioning_result` fields |
| - | - |
| Provisioned | `status: "COMPLETED"`, `account_id`, `account_name`, `environment`, `region`, `approved_by`, `approval_timestamp`, `approval_source`, `approval_ip`, `results` |
| Approval rejected | `status: "REJECTED"`, `rejected_by`, `reason`, `results` |
| Approval expired | `status: "TIMED_OUT"`, `reason`, `results` |

`results` is an object keyed by completed activity name. Its child payloads are heterogeneous implementation outputs and are not a versioned ACP contract. ACP should branch on the documented top-level business fields; a stable external schema for per-phase outputs is **(ask human)**.

**Activity order / labels (8 phases):**

1. Validate Request & OU Mapping (`validate_request`)
2. Create AWS Account (AWS Service Catalog) (`create_aws_account`)
3. Wait for Account Ready (`wait_account_ready`)
4. Configure IAM & Security (`configure_iam_security`)
5. Provision Foundation Services (`provision_foundation_services`)
6. Enable AI/ML Services (Bedrock) (`enable_genai_services`)
7. Configure Networking (`configure_networking`)
8. Finalize & Send Notifications (`finalize_and_notify`)

### A.5 Status meanings

These strings are the current capability API wire vocabulary; ACP does not receive Temporal endpoints, namespaces, or queues and need not understand Temporal internals.

| Value | Kind | Caller meaning |
| - | - | - |
| `RUNNING` | Temporal | In progress; may set `approval_required` at 4/8 |
| `COMPLETED` | Temporal | Terminal success; read `provisioning_result` (may nest business `REJECTED` or `TIMED_OUT`) |
| `FAILED` | Temporal | Terminal failure; see `error` |
| `TERMINATED` | Temporal | Terminal; see `error` |
| `TIMED_OUT` | Temporal | Terminal; see `error` |
| `CANCELED` | Temporal | Terminal; see `error` |
| `CONTINUED_AS_NEW` | Temporal | The run continued as a new Temporal run. Callers poll the same opaque handle unless the published contract returns a replacement handle. |
| `UNKNOWN` | Temporal empty status | Treat as unhealthy / retry describe |
| `NOT_FOUND` | API synthetic | Mapped to **HTTP 404** |
| `ERROR` | API synthetic (Temporal RPC other than not-found) | Mapped to **HTTP 502** |

Do not conflate HTTP 503 "Temporal client not connected" with a workflow `FAILED`.

### A.6 Minimal OpenAPI 3 stub (HTTP door)

```yaml
openapi: 3.0.3
info:
  title: CAH Workload Account Provisioning (HTTP door)
  version: "0.1.0-code-derived"
paths:
  /trigger-workload-provisioning:
    post:
      summary: Start workload account provisioning
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkloadProvisioningSubmit'
      responses:
        '200':
          description: Started
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkloadProvisioningHandle'
        '400':
          description: Validation error
        '401':
          description: AgentGateway rejected missing or invalid Entra authentication before forwarding.
        '403':
          description: AgentGateway denied the authenticated caller under route authorization policy.
        '429':
          description: Rate limit exceeded
        '502':
          description: Failed to start Temporal workflow
        '503':
          description: Temporal client not connected
  /workload-provisioning-status/{workflow_id}:
    get:
      summary: Poll provisioning status
      parameters:
        - name: workflow_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Status payload
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkloadProvisioningStatus'
        '404':
          description: Workflow not found
        '502':
          description: Temporal error
        '503':
          description: Temporal client not connected
  /approve-provisioning/{workflow_id}:
    post:
      summary: Approve a waiting provisioning workflow
      parameters:
        - name: workflow_id
          in: path
          required: true
          schema: { type: string, maxLength: 256 }
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                approver_name: { type: string, maxLength: 200, default: Manager }
                signal_name: { type: string, enum: [all_approvals_complete, manager_approval], default: all_approvals_complete }
      responses:
        '200':
          description: Approval signal sent, or workflow already terminal
        '400': { description: Invalid workflow id, signal name, or approver length }
        '404': { description: Workflow not found }
        '502': { description: Temporal error }
        '503': { description: Temporal client not connected }
  /reject-provisioning/{workflow_id}:
    post:
      summary: Reject a waiting provisioning workflow
      parameters:
        - name: workflow_id
          in: path
          required: true
          schema: { type: string, maxLength: 256 }
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                rejected_by: { type: string, maxLength: 200, default: Manager }
                reason: { type: string, default: "" }
                signal_name: { type: string, enum: [approval_rejected], default: approval_rejected }
      responses:
        '200':
          description: Rejection signal sent, or workflow already terminal
        '400': { description: Invalid workflow id, signal name, or rejected_by length }
        '404': { description: Workflow not found }
        '502': { description: Temporal error }
        '503': { description: Temporal client not connected }
components:
  schemas:
    WorkloadProvisioningSubmit:
      type: object
      required: [conversation_id, account_name, environment]
      properties:
        conversation_id: { type: string }
        account_name: { type: string }
        environment: { type: string, enum: [development, staging, production] }
        region: { type: string }
        cost_centre: { type: string }
        ad_groups:
          oneOf:
            - type: string
            - type: array
              items: { type: string }
        use_aap: { type: boolean }
        account_type: { type: string }
        account_owner: { type: string }
        contact_email: { type: string }
        organization: { type: string }
        data_classification: { type: string }
        data_residency: { type: string }
        support_group: { type: string }
        business_application: { type: string }
        is_genai_workload: { type: string }
        tfcb_onboarding: { type: string }
        ad_group_domain: { type: string }
        new_ad_group_name: { type: string }
        existing_ad_group: { type: string }
        requester: { type: string }
        department: { type: string }
        budget_amount: { type: string }
        form_data_summary: { type: string }
        request_id: { type: string, format: uuid }
    WorkloadProvisioningHandle:
      type: object
      required: [workflow_id, message]
      properties:
        workflow_id: { type: string }
        message: { type: string }
    WorkloadProvisioningStatus:
      type: object
      properties:
        workflow_id: { type: string }
        status:
          type: string
          enum: [RUNNING, COMPLETED, FAILED, CANCELED, TERMINATED, CONTINUED_AS_NEW, TIMED_OUT, UNKNOWN]
        progress: { type: string }
        steps:
          type: array
          items:
            type: object
            properties:
              step: { type: integer }
              name: { type: string }
              status: { type: string, enum: [completed, pending] }
        provisioning_result: { type: object, additionalProperties: true }
        error: { type: string }
        approval_required: { type: boolean }
        approval_message: { type: string }
```

### A.7 MCP tool schema

**Code-grounded** on `provisioning-mcp` (preferred dual-entry MCP door):

**Tool:** `trigger_workload_provisioning`  
Parameters: `request_id` (str, default `""`), `conversation_id` (str, default `""`), `account_name` (str, default `""`), `environment` (str, default `""`), `region` (str, default `ca-central-1`), `cost_centre` (str, default `CC-12345`), `ad_groups` (str, default `APP-PHOENIX-DEVOPS,APP-PHOENIX-READONLY`), `use_aap` (bool, default `false`).  
Success JSON includes `workflow_id`, `request_id`, `status: "STARTED"`, `estimated_duration_seconds: 120`, `phases: 8`, `message`, plus agent-protocol fields `__pending_check` / `__enforcement`.

The MCP submit door intentionally exposes a reduced field set. The HTTP submit door accepts the full workload form. Both doors converge on the same workflow and share the same opaque handle/status model; full submit-field parity is not part of the published contract.

`estimated_duration_seconds: 120` is a tool-returned user-experience hint, not an SLO or completion guarantee. Published SLOs remain **(ask human)**.

**Tool:** `check_workload_provisioning_status`  
Parameter: `workflow_id` (str). Returns same status shape as HTTP, with approval hints when `RUNNING` and 4/8 complete.

**Tool:** `approve_provisioning`  
Parameters: `workflow_id` (str), `approver_name` (str, default `"Manager"`). Signals workflow; returns `status: "APPROVED"`.

**Proposed target schema** for ACP registry packaging (name/version string, input JSON Schema document id): **(ask human)**. Do not invent an ACP tool URN.

Note: webhook-receiver FastMCP still hosts other tools; workload trigger MCP ownership for agents is the provisioning-mcp server federated through AG.

### A.8 Error model

| Code | When (HTTP workload routes) |
| - | - |
| 400 | Validation failures (missing required fields, bad enums, bad UUID, bad email, etc.) |
| 401 | AgentGateway rejects missing or invalid Entra authentication before forwarding this AG-fronted route |
| 403 | AgentGateway denies an authenticated caller under its route authorization policy |
| 404 | Status poll, workflow not found |
| 429 | Rate limit exceeded (`detail`: rate limit message) |
| 502 | Temporal start/describe failure mapped from RPC / synthetic ERROR |
| 503 | Temporal client not connected |

MCP errors for these tools are typically **JSON payloads with an `error` field** inside tool results rather than a separate MCP error-code table in this code. Structured MCP error codes beyond that: **(ask human)** if ACP requires a standard envelope.

### A.9 Rate limit

- Workload trigger: **5 requests per 60 seconds**, keyed by client IP (`provision:{client_ip}`).
- Counter scope is one process instance; replicas have independent counters (in-memory `defaultdict` of timestamps).

### A.10 Idempotency

- Handle id format: `workload-acct-{account_name.lower()}-{uuid4.hex[:8]}`.
- Repeated submit starts a distinct workflow because the handle includes a random suffix.
- Route accepts no idempotency key.
- Retention of handles/results: **not defined in this code** → **(ask human)** for target idempotency and retention contract if ACP requires one.

### A.11 Status delivery

- **Polling via GET** `/workload-provisioning-status/{workflow_id}` exists and is the supported external pattern for this capability.
- Workflow activities may POST step callbacks to an internal webhook callback URL for SSE subscribers keyed by `conversation_id`. That is **not** a documented external callback contract for ACP clients of this capability.
- Do **not** claim external callbacks or subscriptions for this reference capability.

### A.12 Auth paths (consolidated)

Per-path auth for the gateway surface and the reference workload capability. One table; section 8 points here for detail.

| Traffic class / path | Auth | Notes |
| - | - | - |
| Edge MCP / langgraph on **:5555** | Entra **jwtAuth** `mode: strict` + CEL-style `authorization.rules` on `jwt.appid` and `jwt.tid` | Single Entra choke point for Backstage and C# API style edge callers. AG terminates JWT and forwards **without** the webhook-receiver static bearer. |
| HTTP workload routes through AgentGateway **:5555** (`/trigger-workload-provisioning`, approve/reject, related status) | Same :5555 Entra jwtAuth edge + NetworkPolicy | Receiver **bypasses** `WEBHOOK_AUTH_TOKEN` for AG-fronted prefixes (`/trigger-workload-provisioning`, approve/reject, `/trigger-rag-`). |
| MCP tools via AG federation | Edge :5555 Entra jwtAuth for external MCP clients; in-cluster :5557 `/mcp` uses NetworkPolicy only | Dual hop: edge token vs pod-to-pod NetworkPolicy. |
| In-cluster MCP on **:5557** `/mcp` | **No jwtAuth** on that path match. Pod identity + NetworkPolicy | Intentional. Edge Entra is the wrong trust layer for pod-to-pod. |
| A2A catch-all on **:5557** | Entra jwtAuth strict, audience pinned to A2A client id | Separate from the no-jwt `/mcp` path on the same port. |
| PROD platform model routes on **:5557** (`/v1/chat/completions`, `/v1/embeddings`) | AgentGateway **`apiKey`** policy (`mode: strict`); wire header **`Authorization: Bearer <platform-key>`** | `apiKey` names the policy type, not the header. Solo default header; PROD route policies have **no `location` stanza**. Platform API key, not Entra JWT, not a Bedrock credential. Separate traffic class from workload HTTP. |
| Outbound AgentGateway → Bedrock (after the inbound platform routes above) | **SigV4**; primary identity **IRSA** on the AgentGateway ServiceAccount; IAM-user-in-Vault fallback | Cross-region inference: caller pods in **`ca-central-1`**, model may resolve in **`us-east-1`**. Not an inbound API key. |

---

## Appendix B. Operational contract (Tier 2)

| Topic | Answer |
| - | - |
| SLOs | **(ask human)** no published capability SLOs in the inspected sources |
| Quotas beyond rate limit | Workload: 5/60s per instance IP. Others vary (e.g. forge 5/60s, search 20/60s). Cluster-wide quotas: **(ask human)** |
| Max payload | Workload body is ordinary JSON form fields; no explicit max body constant on this route. Internal admission elsewhere caps 1 MiB. Workload max payload: **(ask human)** if ACP needs a hard limit |
| Concurrency / backpressure | Temporal worker concurrency is internal. No caller-visible backpressure API beyond 429/503. **(ask human)** for target |
| Versioning / deprecation | Dual-entry hides Temporal internals; breaking change process and deprecation window: **(ask human)** |
| Polling | Supported for workload status |
| Callbacks | Not a supported external contract for this reference capability |
| Network reachability / DNS / private CA / allow-list | Section 7; details **(ask human)** with Reza |
| Authz / tenancy / capability allow-list registration | Edge allow-list is Entra appid/tid rules in AG config. ACP registry allow-list process: **(ask human)** |
| Onboarding steps DEV → SIT → PROD | Section 13; timeline and acceptance criteria **(ask human)** with Mark Hanson and Seth Chalmers |
| OTel correlation and trace access | Section 9; endpoint options and Iceberg read access **(ask human)** |

---

Last updated: 2026-08-31 by Srikanth Ramasubramanian / CAH team
