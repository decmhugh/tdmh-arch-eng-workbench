# Onboard Waldo Use Case to ACP — D0 Discovery

## Problem Statement

- **Waldo assets are not yet onboarded to ACP governance** — the CTO/Waldo Luminate project and Owner access were provisioned in dev, but the onboarding exchange reported no agent or MCP server registrations; confirm the current portal inventory before registration
- **No centralized audit trails for Waldo incident triage** — current observability tracks tool usage and telemetry; does not provide governance audit ledger required for regulatory discovery (OSFI, NIST); Waldo outputs documented but not governed
- **LLM routing and MCP selection not audited** — Waldo's intelligent tool selection (prompt-based routing) lacks governance gates, risk classification, or human-in-the-loop controls; no way to demonstrate due diligence on LLM choices
- **Evaluation framework not integrated with enterprise governance** — Waldo uses self-hosted Langfuse for app-level traces and evaluation scoring (enabled in the inspected dev configuration; production enablement is not confirmed); correlation with ACP traces and evidence requirements still need to be defined
- **Waldo-family agents may already run in production without ACP registration** — the inspected configuration has dev and prod Kubernetes overlays for four agents (`waldo`, `waldo-incidents`, `waldo-net1`, `waldo-vroom`), and the MCP router's prod agent ACL names all four. Confirm which are live; any running agent is unregistered today, and the planned incident-triage multi-agent architecture will add further registrations, policies and risk-based routing
- **Risk boundary for Waldo tools is not yet agreed** — Waldo reports 50+ MCP servers and ~500 tools. The inspected router source has 38 instance directories with ~527 tool definitions, and prod enables 19 instances (notably not `incident_management`) behind one aggregating router. Verify current counts and owners before deciding which server or tool requires an individual risk classification and policy
- **Waldo's tool identity and third-party credentials depend on custom headers** — the CTO.AI gateway's per-user OAuth 3LO vault injects Atlassian, ServiceNow and Splunk tokens as request headers, and the router derives user attribution and its agent ACL from `X-User-*` and `X-Agent-ID` headers. Luminate forwards only an allow-list of standard headers, so this design does not survive a Luminate MCP route as built
- **Multi-region expansion blocked without governance clarity** — Waldo currently deployed in Canadian region only; expansion to US and other regions requires regulatory alignment and proof of governance; ACP integration clarifies this path

## Opportunity

- **Unified registration and asset inventory** — register the Waldo agent and pilot router; reconcile the downstream server/tool inventory and agree which backends need independent ACP registration rather than assuming one router registration covers every downstream action
- **Correlated audit evidence for incident management** — retain Waldo's operational telemetry alongside ACP governance records; correlate traces and define what incident decisions, context gathering, and recommendations can be retrieved for regulatory review
- **Risk-based governance for tool selection** — apply risk tiers (AA/A/B/C/D) to MCP servers based on access scope; use ACP kill switch and access policy for high-risk tools (e.g., infrastructure modification MCPs). ACP has no human-in-the-loop approval capability, so HITL stays in Waldo's approval-required tool list
- **Evaluation integration with compliance evidence** — keep Waldo's self-hosted Langfuse for app-level spans and scoring; define how its evaluation results and ACP governance evidence can be correlated for OSFI/NIST review
- **Incident-focused agentic roadmap** — confirm the deployment status, source and ownership of `waldo-incidents` before scoping its ACP governance or inbound A2A work. It has a Dockerfile, prod overlay, published image reference and a 19-instance router ACL entry, but the inspected agent source tree has no `waldo_incidents` package even though Waldo's readiness notes mark that package split as done
- **Multi-region deployment pathway** — align Waldo's Canadian-to-US expansion with ACP's regulatory requirements; reuse governance framework across regions without rework
- **Competitive advantage via trustworthy AI** — demonstrate to stakeholders (CTO leadership, regulators, internal audit) that Waldo's AI recommendations are governed, audited, and trustworthy
- **Foundation for future agentic complexity** — establish pattern for how orchestrators integrate with ACP; inform future onboarding of other orchestrators and agent platforms

## Stakeholders

| Stakeholder | Role | Interests |
|---|---|---|
| **Bill Dubreuil (Waldo Product Lead)** | Product Owner | Minimal disruption to current architecture; clear technical specifications for ACP integration; unblocks agentic roadmap |
| **Waldo CTO Teams** | End Users | Single pane of glass maintained; incident triage efficiency preserved; governance overhead minimal |
| **Waldo Engineering (Vikas Choata, Tech Lead)** | Implementation | Technical onboarding guidance; orchestrator-level vs. MCP-level registration clarity; correlation of existing evaluations with ACP evidence |
| **ACP Engineering (Kalev Gonvick)** | Platform engineering contact | Coordinate Waldo technical onboarding, gateway integration, and technical guidance with the ACP team |
| **Lalit Summan (ACP Product/Delivery)** | Product reviewer | ACP-side D0 scope review, prioritization, and delivery alignment |
| **Enterprise Risk / Model Risk** | Governance | Regulatory requirements for Waldo; OSFI incident management governance; evidence collection and reporting |
| **Internal Audit / CMRM** | Compliance | Audit trail for incident recommendations; compliance evidence for regulatory reviews; attestation of governance controls |
| **Data Privacy / Information Security** | Data Handling | Data residency for Waldo telemetry; encryption and access controls for incident metadata; sensitivity of infrastructure insights |
| **IT Operations / CTO Infrastructure** | Operations | Integration testing with ACP gateway; incident response workflow compatibility; support model during transition |
| **Future Agentic Workload Teams** | Planning | Incident management agent architecture; governance gate requirements; escalation model for agentic decisions |

## Scope (MVP)

**In Scope:**
- **Waldo agent registration in ACP** — confirm which Waldo-family agents run in production (`waldo`, `waldo-incidents`, `waldo-net1`, `waldo-vroom`) and register each live agent with asset metadata (description, team ownership, data classification, region); do not treat Waldo as a single orchestrator
- **MCP inventory and gateway onboarding** — reconcile the reported 50+ downstream MCP servers with the inspected source (38 instance directories, ~527 tool definitions) and the 19 instances enabled in prod; record their tools with owners, access scope and risk classification; pilot registration and deployment of Waldo's aggregating Streamable HTTP router at `/mcp`. Decide with Waldo and Risk whether each downstream server also needs a separate ACP registration/policy boundary before promising them as individually governed routes.
- **Agent registration versus invocation** — register the Waldo agent's governance metadata independently of any gateway Agent Deployment. Its current OpenAI-compatible `/chat/completions` endpoint is not an A2A `message/send` endpoint; only scope an adapter and `/a2a/<endpoint>` deployment if inbound invocation by another agent is required.
- **Traffic routing through ACP gateway** — inventory direct Bedrock model calls and MCP client paths in Waldo's shared core, agent nodes, auxiliary flows (e.g. feedback) and MCP servers (the `mcp_rag` instance calls Bedrock embeddings directly) before migrating the agreed pilot traffic. Moving model calls to Luminate means replacing `ChatBedrockConverse` with an OpenAI-compatible client pointed at Luminate `/llm`; the ACP Harness SDK has no LangChain adapter and does not route Waldo's existing MCP clients. Decide which AWS account carries Waldo's Bedrock quota and spend (see dependency 10). Define which calls must traverse ACP, how bypasses are detected, and a rollback before promising full coverage.
- **Router authentication and deployment** — validate gateway reachability/TLS to Waldo's router `/mcp`, configure the Luminate token's JWKS, issuer and deployment-scoped audience on the router, require JWT at the exposed edge, and create and verify a separately deployed Luminate MCP endpoint and access policy. Existing dev MCP JWT enforcement is off; prod trusts CTO.AI gateway tokens, not Luminate tokens. The router validates a single JWKS URL and issuer, so switching it to Luminate would lock out existing CTO.AI-gateway callers; plan a parallel router deployment or a dual-issuer code change.
- **Identity and third-party credentials** — confirm the delegated end-user identity and MCP token exchange before registration. Waldo's per-user OAuth 3LO vault for Atlassian, ServiceNow and Splunk lives in the CTO.AI gateway and reaches the router as custom headers that Luminate strips. Agree how 3LO-dependent tools, user attribution and the router's agent ACL work through Luminate (for example, resolving vault tokens and agent identity from delegated token claims at the router, or keeping 3LO-dependent tools off the Luminate route) before the pilot; Luminate does not yet broker third-party tokens. Per-user third-party access is a named consortium ask, [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) *Per-User Third-Party Connections*, recorded on the Sun Life side as [EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444); until it lands, any interim vault lookup keys on the delegated user identity, not a custom header
- **Incident management use case governance** — define governance policies for incident triage and reconcile them with Waldo's existing approval-required tool list, role mapping and router agent ACL before enabling new callers. `WALDO_OPERATOR_GROUPS: "*"` grants every authenticated caller the operator role, and the router ACL defaults to `allow_all` for an unidentified agent; confirm a least-privilege policy before accepting Luminate-issued identities. Do not assume all incident tools are read-only or that every mutating tool is on the approval list.
- **Existing observability preservation** — add OpenTelemetry context propagation to Waldo (it sends no `traceparent` today) for cross-system trace correlation while retaining Waldo's telemetry (token consumption, latency, feedback, user activity); ACP's collector does not ingest ordinary app spans without `gen_ai.system`
- **Langfuse evaluation integration** — confirm Waldo's Langfuse is enabled in production, retain it for app-level spans and scoring, and agree on a way to associate Waldo evaluations with ACP governance evidence without assuming an ACP-native import or per-tenant trace export
- **Risk classification for MCP ecosystem** — validate the reported inventory with Waldo and Risk, and define policy enforcement per agreed router, server and tool boundary
- **Initial agent readiness (pilot)** — design governance model for incident management agents (supervisor agent + specialized agents), starting from any that are already deployed; agree on a new pilot date with Waldo and ACP
- **Compliance evidence baseline** — establish OSFI/NIST evidence collection for Waldo incident triage; demonstrate governance audit trail for regulatory inquiry
- **Regulatory clarification** — coordinate with Enterprise Risk to document specific OSFI and NIST requirements driving ACP integration
- **Prompt and completion data handling** — agree with Risk and Privacy on ACP trace content, residency, access, and retention. Luminate cannot redact streamed (SSE) responses: decide whether sensitive incident content uses a non-streamed path, accepts stream termination after delivery, or needs a documented exception before it is carried through the gateway
- **Technical onboarding specification** — ACP team delivers detailed specs: orchestrator integration patterns, MCP registration workflow, agent-to-MCP governance, evaluation framework mapping

**Out of Scope (Backlog):**
- Multi-agent orchestration between Waldo and external agents
- Inference governance (retention, lifecycle of generated recommendations)
- Cost attribution and chargeback per MCP or use case
- Self-healing governance or automated remediation
- Advanced anomaly detection on Waldo execution patterns
- Multi-region federation across Canada, US, other geographies (separate work)
- HIPAA or privacy-specific data governance (addressed separately with privacy team)
- Advanced threat detection for MCP supply chain
- CLI-based developer self-service for Waldo integration
- Replacement of Waldo's third-party OAuth 3LO vault with a Luminate-native per-user connection before [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) is delivered

## Capability Requirements

> **Proposed, not confirmed.** The candidate capabilities below are ACP's reading of Waldo's D0 scope and the Waldo/ACP onboarding exchange, mapped to the [ACP Capability Map](../../../capability-map.md). Bill and Vikas (Waldo) have not reviewed the map or confirmed priorities, and no capability has been explicitly declined. Do not treat this proposal as Waldo's selection or D0 approval.

### Mandatory baseline — acknowledgement pending

All sixteen [mandatory capabilities](../../../capability-map.md#3-the-governance-baseline-mandatory-for-every-onboarding) apply to Waldo regardless of the proposed selection below.

| Confirmed with | Date | Notes |
|---|---|---|
| *Pending — Bill Dubreuil (Waldo product owner) and Vikas Choata (Waldo tech lead)* | *TBC* | Present the full baseline. In particular, CAP-12 quotas are ⚠️ modelled, not enforced; CAP-14 lifecycle and CAP-18 audit are 🟡 partial; CAP-11 kill switch and CAP-15 risk tiering are now ✅ available but require the applicable governance rule to be enforced. CAP-10 response guardrails cannot redact streamed output (see Dependency 9). Conditional capabilities triggered by Waldo: CAP-03 (calls MCP tools) and CAP-24 (acts for a user). |

### Selected capabilities — proposed for discussion

These priorities are a starting point for the Waldo/ACP review, not a selection made by Waldo. Mandatory capabilities apply even if omitted here; rows below call out the ones with a specific Waldo integration or evidence question.

| Capability | Why Waldo may need it | Proposed priority | Status today | Confirmed by |
|---|---|---|---|---|
| [CAP-01](../../../capability-map.md#cap-01) — Agent registry | Register every live Waldo-family agent (`waldo`, and `waldo-incidents`, `waldo-net1`, `waldo-vroom` if deployed) with named ownership. | P0 launch | ✅ Available | *Pending* |
| [CAP-02](../../../capability-map.md#cap-02) — Model registry | Use approved models in the Canadian environment; request any missing model through the ACP product team. | P0 launch | ✅ Available | *Pending* |
| [CAP-03](../../../capability-map.md#cap-03) — MCP tool registry | Inventory Waldo's MCP servers and control which tools each agent may call, alongside or replacing the router's header-based agent ACL; conditional baseline triggered by tool use. | P0 launch | ✅ Available | *Pending* |
| [CAP-06](../../../capability-map.md#cap-06) — Machine identity | Attribute Waldo's non-interactive gateway calls to a service principal. | P0 launch | ✅ Available | *Pending* |
| [CAP-08](../../../capability-map.md#cap-08) — Governed AI gateway | Route Waldo's LLM and MCP traffic through a governed path without losing its streaming chat experience; the gateway forwards only allow-listed headers, which breaks Waldo's header-based tool identity. | P0 launch | ✅ Available | *Pending* |
| [CAP-10](../../../capability-map.md#cap-10) — Guardrails | Protect sensitive incident prompts and completions. `ENFORCE` redaction applies to requests and non-streamed responses; streamed responses are at best terminated after delivery. | P0 launch | ✅ Available | *Pending* |
| [CAP-11](../../../capability-map.md#cap-11) — Kill switch | Stop a governed incident agent or MCP resource when a high-risk tool must be withdrawn. | P0 launch | ✅ Available | *Pending* |
| [CAP-12](../../../capability-map.md#cap-12) — Quotas and budgets | Bound traffic during multi-call incident workflows; no gateway counter or blocking exists yet and Waldo's own per-hour limits are disabled, so nothing bounds traffic today. | P0 launch | ⚠️ Modelled, not enforced | *Pending* |
| [CAP-13](../../../capability-map.md#cap-13) — Attribute tagging | Record ownership, region, data classification and policy selectors for Waldo resources. | P0 launch | ✅ Available | *Pending* |
| [CAP-14](../../../capability-map.md#cap-14) — Lifecycle governance | Control approval, suspension and retirement of Waldo's registered resources; multi-step approvals remain incomplete. | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-15](../../../capability-map.md#cap-15) — Risk tiering | Apply a governance-authoritative risk band to each in-scope asset; confirm with Enterprise Risk how Waldo's AA/A/B/C/D labels map to ACP bands. | P0 launch | ✅ Available — band supplied by Sun Life | *Pending* |
| [CAP-18](../../../capability-map.md#cap-18) — Audit trail | Capture governed model and tool decisions; Waldo-only incident events have no external producer path today. | P0 launch | 🟡 Partial | *Pending* |
| [CAP-19](../../../capability-map.md#cap-19) — Regulatory evidence and attestation | Retrieve incident governance evidence for review; signed evidence packs and attestor signoffs are not built. | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-20](../../../capability-map.md#cap-20) — Observability and tracing | Correlate ACP traces with Waldo's self-hosted Langfuse without replacing app-level spans or evaluations. | P0 launch | ✅ Available | *Pending* |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation and assurance | Relate Waldo's incident-quality evaluations to governance evidence; ask Risk whether the conditional customer-affecting-decision trigger applies. | P1 fast follow | 🟡 Partial — build in flight | *Pending* |
| [CAP-24](../../../capability-map.md#cap-24) — Delegated access | Mandatory because Waldo acts for a user. Preserve the requesting user's identity at MCP backends; Luminate does not broker Waldo's third-party OAuth 3LO tokens and strips the headers that carry them today; consortium ask [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) ([EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444)). | P0 launch | 🟡 Partial | *Pending* |
| [CAP-26](../../../capability-map.md#cap-26) — Conditional access and data-flow control | Confirm whether Canadian data-residency requirements trigger jurisdiction controls; do not assume the designed control is available. | P1 fast follow | 📐 Designed | *Pending* |

The catalogue marks CAP-19 mandatory, although it is absent from the sixteen-item baseline summary, and the baseline summary shows CAP-18 as ✅ while its catalogue row is 🟡 Partial; clarify both inconsistencies with the capability-map owners during review. Every non-✅ capability that Waldo confirms, and every mandatory baseline gap, needs an entry in the D1 gap register.

### Capabilities explicitly not required — pending review

| Capability | Why not |
|---|---|
| *None confirmed* | Waldo has not reviewed and declined any named capability. Out-of-scope roadmap items are not recorded as explicit declines. |

## Success Criteria

- ✅ **Live Waldo agents registered and visible in ACP registry** — every Waldo-family agent confirmed as deployed is registered with complete, searchable asset metadata (team, region, classification)
- ✅ **MCP inventory classified at the agreed policy boundary** — validate the reported downstream server/tool inventory; classify owners, access scopes and risks, then verify which backends need independent registration versus router-level governance
- ✅ **Agreed incident triage traffic routed through ACP gateway** — measure model and MCP call-path coverage against a baseline of every relevant Waldo call site (including auxiliary model calls); set a cutover target with Waldo and Risk and measure latency/availability without implying that unmodified paths are governed
- ✅ **Governed audit coverage is demonstrated** — collect and retrieve ACP records for pilot calls that traverse its gateway; identify Waldo-only decisions, tool selections, recommendations and feedback that cannot enter the ACP audit ledger through an external producer, and agree how to correlate or report that evidence separately
- ✅ **Waldo evaluations and ACP traces correlated for review** — shared trace IDs and an agreed evidence retrieval path link Waldo's evaluation results to ACP records; baseline quality metrics established (e.g., hallucination rate, tool relevance)
- ✅ **Identity and content controls proven in the pilot** — delegated identity is validated at the MCP backend; a 3LO-dependent tool call through the agreed route uses the correct user's third-party credentials; an unidentified caller cannot reach instances outside its ACL; and sensitive incident content follows the agreed non-streamed, terminate-on-match or exception path before it is cut over
- ✅ **Incident-agent readiness established** — Waldo confirms which specialist agents are deployed and where their source lives, then documents their governance model and any A2A protocol work separately from agent catalog registration
- ✅ **OSFI/NIST evidence baseline established** — compliance artifacts generated (audit trail sample, governance policy document, evaluation summary); regulators briefed on Waldo governance approach
- ✅ **Technical onboarding specification complete** — detailed documentation of orchestrator-to-ACP integration, MCP registration workflow, agent governance model, evaluation framework alignment
- ✅ **Zero disruption to incident response operations** — Waldo incident triage performance unchanged; user experience preserved; support model defined
- ✅ **Team readiness for agentic roadmap** — Waldo and ACP engineering teams aligned on agent registration, governance, routing, and a rebaselined pilot schedule

## Dependencies

**Critical Blockers:**

1. **ACP technical onboarding specification** — detailed specs required from ACP team on orchestrator integration, MCP registration model, gateway replacement, agent-to-MCP governance, evaluation framework alignment
2. **Risk tier classification framework alignment** — confirm with Enterprise Risk how MCP servers map to AA/A/B/C/D tiers (e.g., read-only knowledge → A; infrastructure query → B; remediation capability → C/D); apply policy enforcement
3. **Orchestrator-level vs. MCP-level registration clarity** — ACP to clarify whether orchestrator registers as single agent or each MCP as individual agent; implications for governance, audit trails, escalation
4. **OSFI and NIST regulatory requirements** — Enterprise Risk to document specific incident management governance requirements driving ACP integration
5. **Gateway migration and coverage** — Waldo's graph nodes and auxiliary paths call Bedrock directly through `ChatBedrockConverse`, the `mcp_rag` MCP instance calls Bedrock embeddings directly, and Waldo's FastMCP clients connect to the router with `forward_user_jwt`. Inventory all model/tool paths, decide which are in the pilot, and define cutover, fallback, route verification and monitoring of direct-call bypasses. CTO.AI's own gateway is a distinct auth/routing service, not Luminate.
6. **Streaming compatibility validation** — LLM SSE streaming (`GatewayClient.stream()` / `stream_sync()`, `ACPClient.chat_stream()`; EACPP-812) is released in ACP Harness SDK v0.16.0 (tagged on the EACPP-812 merge and published to Artifactory on 2026-10-01). It is synchronous only, although the SDK D1 specifies an async variant; it covers LLM chat completions only (no A2A `message/stream` or MCP progress events); and the SDK has no LangChain adapter. Waldo is an async FastAPI/LangGraph service, so the realistic path is an OpenAI-compatible LangChain chat model pointed at Luminate `/llm`, not the SDK stream API. Waldo also uses Bedrock extended thinking (`additional_model_request_fields`), which the SDK's `ChatChunk` does not surface; verify that Luminate `/llm` accepts the thinking parameters and returns reasoning content. Waldo's own LangGraph stream emits progress and `ui_render` frames as well as text/tool events, and no OpenAI chat-chunk parser substitutes for that agent-to-UI stream. Verify model streaming through the deployed Luminate gateway without losing Waldo's UI/event behavior, tool calls, auth, errors, latency or audit visibility.
7. **Identity and credential boundary** — Luminate forwards only an allow-list of request headers (content type, authorization, MCP session and trace context). Waldo's router depends on headers that would be stripped: per-user third-party tokens (`X-Atlassian-User-Token`, `X-Servicenow-User-Token`, `X-Splunk-User-Token`, injected by the CTO.AI gateway's 3LO vault and forwarded by the agent), user attribution (`X-User-ID`, `X-User-Email`) and `X-Agent-ID` for the agent ACL. Agree how these work through Luminate before the pilot. Before resource registration, confirm the caller principal, MCP `DELEGATED_EXCHANGE` audience and issuer, and how the router maps that identity to the user's 3LO tokens. Injected credentials and external exchange for third-party SaaS are not implemented, and the ask raised for them ([EACPP-1282](https://sunlife.atlassian.net/browse/EACPP-1282)) is one shared credential per deployment, which cannot reach a vendor as the individual user; the per-user case is [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165), recorded as [EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444). The router validates a single JWKS URL and issuer, and its prod settings trust the CTO.AI gateway: run a parallel Luminate-facing router deployment or add dual-issuer support, then configure and test the Luminate issuer, JWKS, audience and `MCP_JWT_REQUIRED=true` at its exposed edge, including verifying that the issuer setting reaches the supervisor-managed router process. Separately verify Luminate gateway-to-router reachability, deployment, access policy, `tools/list` and a safe `tools/call`. Do not replace Waldo's 3LO flow prematurely.
8. **Waldo authorization boundary** — review `WALDO_OPERATOR_GROUPS: "*"`, the admin/operator tool roles, and the explicit `WALDO_APPROVAL_REQUIRED_TOOLS` list against delegated caller claims and risk tiers. The list omits tools such as `submit_intake_form` and `update_intake_form`; test that unlisted mutating tools cannot silently bypass approval. The router's prod agent ACL trusts the self-asserted `X-Agent-ID` header and defaults to `allow_all` for unlisted agents; set `deny_unlisted` or bind agent identity to token claims before opening a new caller path. Decide whether an agent deployment is needed only after establishing an inbound A2A use case and protocol compatibility; agent registration and outbound model/MCP use do not require A2A.
9. **Tracing and content review** — confirm with ACP and Risk that ACP Langfuse stores prompt and completion text in the Canadian deployment, who can retrieve it without per-tenant export, and the retention requirements. Test PII guardrails in `ENFORCE` mode on requests and non-streamed responses; `WARN` does not redact. Luminate's posture for streamed responses is a gateway-wide setting (`GATEWAY_GUARDRAIL_RESPONSE_STREAMING`) whose source default is `audit`, which scans after the stream ends and neither blocks nor redacts. `enforce` ends the stream on a match, but only after the matched content has been delivered; no mode redacts streamed output. Confirm the deployed setting and agree with Risk which path sensitive incident content takes.
10. **Model onboarding and pilot performance** — onboard Waldo's models (Claude Sonnet 4.6 and Haiku 4.5, plus Opus 4.6 if enabled) in the Luminate catalog. Decide whether Waldo's Bedrock traffic runs in an ACP shared spoke account or a Waldo-owned spoke: Luminate's per-project offering account binding (AIC-783) can route Waldo's project to Waldo's own account, attributed in CloudTrail/CUR by the STS session name `luminate-<project-id>`, but needs a spoke role in Waldo's account and a Luminate install that includes AIC-783. Confirm capacity and cost ownership for the chosen option. Measure p50/p99 latency and availability for Waldo's multi-call tool loops against a direct-route baseline. Gateway authz was described as uncached per request; ACP quotas are not enforced and Waldo's own per-hour request and token limits are disabled, so agree on rollout notice, traffic bounds and 429 handling.
11. **Langfuse / evaluation evidence mapping** — confirm Waldo's Langfuse is enabled in production (only the dev overlay enables it in the inspected configuration). Waldo has no OpenTelemetry context propagation today, so add `traceparent` instrumentation, then agree how Waldo's app spans and evaluations correlate with ACP traces and how Risk retrieves evidence without assuming per-tenant export.
12. **Incident management agent architecture** — confirm whether `waldo-incidents` is already deployed; obtain approval from CTO leadership and ACP team on the supervisor + specialized agents design; define governance gates
13. **Data residency and encryption** — confirm ACP's data handling for Waldo telemetry (Canadian region residency, encryption at rest/in-transit, access controls). Waldo's current direct Bedrock calls use `us.anthropic.*` cross-region inference profiles, so inference may be processed in US regions. Migrating to Luminate does not by itself change where inference runs: the newer Anthropic offerings in the Luminate catalog (Sonnet 4.6, Haiku 4.5) are also `us.anthropic.*` cross-region profiles and execute in US regions. Risk must decide which inference profile type (in-region, `us.`, or `global.`) is acceptable for incident content, for both migrated and unmigrated paths
14. **MCP server ownership and metadata** — Waldo team to reconcile the reported inventory with the 19 instances enabled in prod and the instances in source, recording owner, risk classification, data classification, access scope and routing path
15. **Pilot agent selection** — identify specific incident management agent (or subset of incident types) for the initial pilot; define governance gates and escalation model

## Risks

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **Waldo architecture changes required for ACP integration** | Project delay; rework of orchestrator gateway logic | Medium | Early design review with ACP team; modular integration approach; pilot single MCP first |
| **Direct Bedrock calls remain outside ACP** | Apparent pilot success masks ungated model calls in graph nodes, auxiliary flows or other agents | Medium | Inventory model call sites, route the agreed coverage set through ACP, measure direct-call bypasses, and only claim governance over verified paths |
| **Gateway replacement causes performance regression** | Incident response latency increases >5%; user adoption resistance | Medium | Performance testing protocol; fallback to direct routing if thresholds breached; gradual traffic migration |
| **Waldo streaming behavior differs from gateway streaming** | Streaming chat, extended-thinking output, tool-call events, or error handling breaks during migration | Medium | SDK streaming (v0.16.0) is synchronous and LLM-only, so plan on an OpenAI-compatible LangChain client; run an end-to-end Waldo streaming pilot through the deployed Luminate gateway and compare event behavior, reasoning output, auth, latency, and audit records before cutover |
| **Streamed content cannot be redacted** | Sensitive incident completions reach users and ACP trace storage unredacted | High | Route sensitive content through a non-streamed path with `ENFORCE` redaction, or accept `enforce` stream termination after delivery, or document a Risk-approved exception; confirm the deployed streaming posture |
| **Luminate strips Waldo's identity and token headers** | 3LO tool calls to Atlassian, ServiceNow and Splunk fail; user attribution is lost; the router agent ACL falls back to `allow_all` | High | Agree the identity design before the pilot; set the ACL to `deny_unlisted` or bind it to token claims; prove a 3LO tool call and an ACL denial through Luminate; keep the existing CTO.AI path until then |
| **Router issuer switch cuts off existing callers** | Production Waldo loses tools while the router trusts only Luminate tokens | Medium | Run a parallel Luminate-facing router deployment or add dual-issuer support; stage the cutover |
| **Waldo agents already run in production unregistered** | Unregistered production AI under CAP-01; governance scope understated | Medium | Confirm deployment status of `waldo-incidents`, `waldo-net1` and `waldo-vroom`; register any live agent in the first wave |
| **Downstream tools hidden behind a single router registration** | ACP policies and evidence cover the router route but may not distinguish high-risk downstream tool calls | Medium | Validate the inventory and tool-level behavior; decide with Risk whether independent registrations or additional Waldo controls are required before claiming per-tool enforcement |
| **Planned incident management agents slipped or deprioritized** | ACP integration becomes "nice-to-have" rather than required; loses urgency | Medium | Reconfirm CTO leadership's agent roadmap and pilot timing at ACP project kickoff |
| **Technical specification from ACP team delayed** | Waldo team cannot start integration work; project stalls | Medium | Schedule ACP spec delivery date at project kickoff; escalate if blocked; coordinate Lalit (ACP) and Vikas (Waldo) on specification priority |
| **OSFI regulatory requirements conflict with Waldo's current design** | Governance policy enforcement requires major architectural rework | Low-Medium | Early regulatory clarification from Enterprise Risk; design for flexibility (policy-driven, not code-driven governance) |
| **Waldo and ACP evidence cannot be correlated or retrieved together** | Compliance review cannot connect Waldo evaluations to governed model and tool calls | Medium | Pilot shared trace IDs, document which `gen_ai.system` spans ACP retains, and agree on evidence access while per-tenant export is unavailable |
| **Waldo incident response workflow incompatible with ACP governance gates** | User experience degrades; adoption resistance from CTO teams | Low | Workflow design review with incident responders; HITL approvals stay in Waldo and are scoped to high-risk tools only |
| **Multi-region expansion timeline misaligned with ACP readiness** | Waldo expansion delayed until ACP governance for US region is ready | Low-Medium | Decouple Waldo expansion from ACP in terms of project planning; ACP can follow Waldo deployment if needed |
| **Agent-to-agent communication requirements not addressed** | Future multi-agent incident orchestration cannot be governed; rework required | Low | Design for future agent-to-agent governance; position incident management agent architecture as foundation for broader agentic ecosystem |

## Next Steps

**Timeline:**

The dates below are the original August 2026 planning targets, not confirmed completion dates or a current delivery commitment. As of 2026-10-01, D0 approval is still pending, the first three targets have passed, and the pilot MCP onboarding target (2026-10-01) has not started. Capability selection, the pilot, and subsequent milestones need to be rebaselined with Waldo and ACP before D1.

| Milestone | Original target | Status (2026-10-01) | Owner | Action |
|---|---|---|---|---|
| **D0 Approval & Stakeholder Alignment** | TBD — pending Waldo availability | Pending | Lalit (ACP) / Bill (Waldo) | Review D0; confirm scope, dependencies, risks and capability selection; obtain CTO leadership sign-off |
| **Technical Specification Delivery** | 2026-08-31 | Missed — rebaseline | ACP Engineering (delivery owner to confirm) | Detailed specs: agent integration, identity and header design, MCP registration, gateway replacement, agent governance, evaluation framework |
| **Risk Tier Classification Complete** | 2026-08-31 | Missed — rebaseline | Waldo Engineering + Enterprise Risk | Reconcile the MCP inventory; classify by AA/A/B/C/D; document policy enforcement per tier |
| **ACP Integration Design Review** | 2026-09-15 | Missed — rebaseline | Waldo + ACP Engineering | Co-design traffic flow, gateway replacement, pilot MCP selection, performance testing plan |
| **Pilot MCP Onboarding** | 2026-10-01 | Not started — rebaseline | Waldo + ACP Engineering | Register first MCP; route through ACP gateway; validate performance and audit trail capture |
| **Full MCP Inventory Onboarded** | 2026-10-15 | Rebaseline | Waldo + ACP Engineering | Register remaining MCPs; enforce governance policies per risk tier; validate observability preservation |
| **Incident Management Agent Design Approval** | 2026-10-22 | Rebaseline | CTO + ACP + Waldo | Approve supervisor + specialized agents architecture; governance gates; escalation model |
| **Compliance Evidence Baseline Ready** | 2026-11-01 | Rebaseline | ACP + Internal Audit | OSFI/NIST evidence artifacts; audit trail sample; governance policy documentation; regulator brief |
| **Agent Pilot Deployment** | 2026-11-15 | Rebaseline | Waldo + ACP | First incident management agent routed through ACP; governance gates active; audit trail validated |
| **Full Production Rollout** | 2026-12-15 | Rebaseline | Waldo + ACP | All Waldo agents + MCPs under ACP governance; compliance evidence collection validated |

**Key Actions:**

1. **ACP Team:** Deliver agent integration specification (architecture, identity and header design for 3LO tools and the router ACL, MCP registration model, gateway replacement, agent governance, evaluation framework mapping); confirm the deployed streamed-response guardrail posture
2. **Waldo Team:** Confirm which Waldo-family agents are in production; complete MCP inventory and risk classification; confirm whether Langfuse runs in production; confirm the current incident management agent roadmap and pilot timing
3. **Enterprise Risk:** Document OSFI/NIST requirements driving ACP integration; clarify regulatory evidence expectations
4. **ACP + Waldo:** Schedule design review and co-design gateway replacement and pilot MCP onboarding
5. **CTO Leadership:** Confirm incident management agent roadmap timing; align with ACP project
6. **Internal Audit:** Define compliance evidence requirements for Waldo incident triage governance

