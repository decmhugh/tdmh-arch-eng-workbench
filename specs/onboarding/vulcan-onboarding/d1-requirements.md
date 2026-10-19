# Vulcan Onboarding — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: **Approved 2026-09-03** | **Epic**: [EACPP-1133](https://sunlife.atlassian.net/browse/EACPP-1133)
>
> **Verified against**: `AGI/vulcan-agent-langchain` @ `main` and
> `AGI/ai-agent-orchestration-api` @ `main`, both read 2026-08-28;
> `Code/Luminate/luminate` @ `origin/main` `89356d74` (re-verified 2026-08-30);
> `luminate-sunlife-deploy` @ `origin/main` `623f1b2`. Every claim below about what exists on
> either side is drawn from those trees, not from a transcript.

## 0. The framing that shapes every requirement

The target-run-journey architecture puts ACP in two of the use case's columns. Those two columns
land on two different seams, in two different repositories, with two different failure modes, and
they can be delivered independently. Keeping them apart is what makes this tractable:

- **Column 1 — control plane.** One synchronous question, asked once per run, by a Java service:
  *is this agent still approved to run?* It is a **dispatch gate**. If it is wrong, a run that
  should not have started, starts.
- **Column 2 — data plane.** Every LLM call and, later, every tool call the running job makes.
  It is **continuous enforcement**. If it is wrong, the run is wrong while it is happening.

Two things follow that are worth stating before the requirements, because they change what
"done" means.

### The seams already exist

This is not a normal integration. Both codebases put the boundary in the right place before ACP
was in the conversation:

| Seam | What it is today | What it becomes |
|---|---|---|
| `vulcan.tools.llm.get_llm()` | Returns a LangChain `BaseChatModel`. Agent nodes never import `ChatGithubCopilot` or `ChatBedrockConverse`. Provider chosen by `llm.provider` in `vulcan.yaml`. | A third provider, `acp`, alongside `github` and `bedrock` |
| `AgentRegistry.resolve(agentId)` | A one-method Java interface. The only implementation, `JsonAgentRegistry`, reads `agent-registry/agents.json` from the classpath at startup. | A second implementation that asks ACP |

Neither change touches a LangGraph graph, a prompt, a remediation pattern, or the Job factory.
That is the whole reason this onboarding is worth doing before September rather than after.

### September is a fork, not a deadline

Vulcan stated it will proceed with an interim Bedrock-and-Okta deployment if ACP integration is
not available by the end of September. That is not a risk to be argued down — **the interim path
is already built and merged**. `src/vulcan/providers/bedrock/auth.py` performs an Okta
client-credentials grant, exchanges the token through STS `AssumeRoleWithWebIdentity`, and caches
the resulting credentials; the decision is recorded in `.roadmap/aws-bedrock-provider.md` dated
2026-08-26, and `agents.json` already mounts an `aws-okta-credentials` Secret into both Vulcan
agents.

So the real requirement is not "beat September". It is: **the ACP path must be additive and
switchable by one configuration key, so that a Vulcan already running on Bedrock can move to ACP
by changing `llm.provider`, not by re-integrating.** Every requirement below is written to hold
whether Vulcan arrives at ACP before or after it ships the interim.

---

## 1. What Vulcan is today — verified

Requirements that misdescribe the system they attach to are worse than no requirements.

### The runtime

`ai-agent-orchestration-api` is a Java 21 Spring Boot service. `POST /api/v1/agent-runs` takes
`{agentId, parameters}`, calls `agentRegistry.resolve(agentId)`, and dispatches a Kubernetes Job
built from the returned `AgentDefinition`. Run state is an in-memory `ConcurrentHashMap`. Its own
`docs/ARCHITECTURE.md` is explicit that this is a POC — "Identity: no caller authentication" —
with OIDC and per-run authorization as the target.

`agents.json` currently holds three definitions, two of which are Vulcan:

| Field | `vulcan-modernizer` / `vulcan-sast-fixer` |
|---|---|
| `status` | `ACTIVE` (enum: `DRAFT`, `ACTIVE`, `DEPRECATED`, `REVOKED`) |
| `image` | `quay.prod-openshift-na.hybrid.sunlifecorp.com/devopsagi/ai-agent-vulcan:0.1.0-…` — **tag, not digest** |
| `args` | `["vulcan", "modernize"\|"fix-sast", "$(REPOSITORY)"]` |
| `envFrom` | `["aws-okta-credentials"]` |
| `timeoutSeconds` | `120` |

`vulcan-agent-langchain` is a Python LangGraph CLI with two agents. Both share a graph spine:
clone and branch → detect stack → platform subgraph → commit-and-push gate → Jenkins → open or
update pull request. Java with Maven or Gradle is the only registered platform.

### What the job calls out to

Every one of these is a **direct call from inside the job container**, authenticated by a
long-lived token supplied as an environment variable from a Kubernetes Secret:

| Dependency | How it is called | Credential |
|---|---|---|
| GitHub Copilot *or* Bedrock | `providers/{github,bedrock}/llm.py` | Copilot token cache, or `AWS_BEARER_TOKEN_BEDROCK` / Okta→STS |
| Bitbucket Server (clone, push, pull request) | `tools/git.py`, `tools/pull_request.py` | `BITBUCKET_USER` / `BITBUCKET_TOKEN` |
| Snyk | `tools/snyk.py`, CLI | `SNYK_TOKEN` |
| Checkmarx One | `tools/checkmarx.py`, the `cx` CLI | `CX_APIKEY` |
| Jenkins | `tools/jenkins.py`, REST | `JENKINS_USER` / `JENKINS_API_TOKEN` |
| Artifactory | `tools/version_resolver.py` | anonymous or configured |
| AI Agent Usage Metrics API | `services/metrics.py` | Okta client credentials, scope `ai-agent-usage-api.usages.uad` |

**There is no MCP anywhere in Vulcan.** Not a client, not a server, not a dependency. Every tool
is a direct CLI invocation or a REST call. This is the single most important fact for column 2b
and it is addressed in §5.

### What Vulcan measures today

`shared/tokens.py` attaches a LangChain callback that counts tokens with `tiktoken`
(`o200k_base`) — a **client-side estimate**, chosen because the comment says it is "close enough
for any model behind GitHub Copilot". `services/metrics_runtime.py` publishes to the usage API:
`agentName`, `agentVersion`, `status`, per-node steps with durations, Snyk vulnerability counts
before and after, Checkmarx scan identifiers, the pull-request URL, and token counts as free-text
`inputParameters`.

Two defects follow from that, and both are fixed as a side effect of routing through ACP rather
than by separate work:

- `aiModel` is `cfg.pr.model or "gpt-5.4"` — a **hardcoded literal fallback**, not the model that
  actually served the run.
- There is **no cost figure at all**, because a token estimate with no authoritative model
  identity cannot be priced.

`executed_by_env` defaults to empty, with the comment "intentionally optional while executedBy
source is undecided". That field is the natural landing place for an ACP entity identifier.

---

## 2. What ACP enforces today — verified

| Capability | State at `89356d74` | Consequence for Vulcan |
|---|---|---|
| LLM data path | Gateway routes `/llm/` → agentgateway port 4000, exposing `/llm/v1/chat/completions` | Vulcan can use LangChain's `ChatOpenAI` against it. No bespoke client |
| Gateway credentials | `X-API-Key`, or `Authorization: Bearer` with `lum_` (API key), `lud_at_` (delegated token), else a validated JWT | The Job pod has a supported way in |
| API key scoping | Unique per user, application, **agent**, or MCP server | A key can be minted for `vulcan-modernizer` specifically |
| Run correlation | `x-luminate-session-id` is **caller-supplied**, sanitised, namespaced `{entity_type}:{entity_id}:{raw}`, mapped to the Langfuse session id; falls back to the `traceparent` trace-id | FR-17 needs a header, not a design |
| Chargeback reporting | `/api/v1/chargeback` — `rows`, `summary` and streaming CSV `export` over a worker-materialised `ProjectUsageDaily` ledger, filterable by **cost centre**, project, entity type, model and date | FR-19's grouping dimension already exists |
| Usage reporting | `/api/v1/metrics` — per-model, per-agent and per-entity usage, read from Langfuse per request | Per-agent cost separation is a query, not a build |
| Provider auth | `ProviderAuthMethod` = `api_key` (secret in AWS/GCP Secrets Manager) or `keyless` (IRSA / workload identity) | **Centralised inference is real**: ACP can hold the Bedrock credential itself, keyless |
| Attribution | Langfuse cost per request, attributable per model (`luminate_model_id`) and per entity (`luminate_entity_id`), plus latency keys | SC-4 and SC-5 are satisfiable; SC-5b is not, see G-J |
| Machine identity to the control plane | `BearerServicePrincipalAuthentication` exists (EACPP-760/761) — an enterprise IdP bearer JWT admitted as a `ServicePrincipal`, under the same RBAC and audit as any principal | Column 1 has a mechanism — **but see G-A** |
| Policy | Rego (Regorus) evaluated inline, fail-closed, versioned bundles | Per-call enforcement is real |
| Agent status | `active` / `inactive` / `deprecated` / `unknown`; `policy_engine/facts.py` only exports `ACTIVE` agents to the bundle | Deactivation removes an agent from the next bundle — eventually, not immediately |

---

## 3. Functional Requirements

### Column 1 — dispatch approval

#### FR-1: ACP is the authority for "may this agent run"

A second `AgentRegistry` implementation resolves the agent definition by asking ACP instead of
reading the classpath JSON. `JsonAgentRegistry` remains, selected by configuration, so the
orchestrator can run without ACP in local and CI contexts.

```
GET {ACP_BASE}/api/v1/catalog/agents?<selector>
Authorization: Bearer <IdP JWT for the orchestrator's service principal>

200 → { id, name, status, ... }
```

The orchestrator maps ACP status to a dispatch decision. Only `active` permits dispatch.

#### FR-2: A refusal is a first-class outcome, not an error

When ACP reports the agent is not approved, the orchestrator refuses the submission with a
distinct status and a reason that names ACP as the decider. It does not surface as a generic
`500`. The existing `AgentNotAvailableException` → `409 Conflict` path is the right shape and
should carry the ACP reason through.

#### FR-3: The approval check has a declared failure posture

ACP being unreachable must resolve to a **configured** behaviour, not an accidental one. The
options and their consequences are set out in D2; the requirement here is that the posture is
explicit, logged distinctly from a genuine refusal, and bounded in time if it permits dispatch.

#### FR-4: Status enums are reconciled

Vulcan models `DRAFT`/`ACTIVE`/`DEPRECATED`/`REVOKED`. ACP models
`active`/`inactive`/`deprecated`/`unknown`. `REVOKED` — the state that matters most for a stop —
**has no ACP equivalent**, and ACP's `unknown` has no Vulcan equivalent. A mapping is defined,
and any ACP state not explicitly mapped to "may run" is treated as "may not run".

#### FR-5: The orchestrator authenticates as a machine principal

The orchestrator presents an IdP-issued bearer JWT and is resolved to exactly one
`ServicePrincipal` in ACP. It holds read-only registry scope. It never presents a user credential
and never presents an end user's token.

### Column 2a — inference

#### FR-6: A third LLM provider, `acp`

`vulcan.providers.acp.llm.create_llm()` returns a `BaseChatModel` pointed at ACP's
OpenAI-compatible endpoint. Selection is `llm.provider: acp`. The existing `github` and `bedrock`
providers are untouched, so the switch is one key.

```yaml
llm:
  provider: acp
  model: <acp-registered-model-id>
  acp:
    base_url: https://<acp-gateway-host>/llm/v1
    api_key_env: ACP_GATEWAY_API_KEY
```

#### FR-7: The credential is agent-scoped and carries attribution

The credential the Job presents resolves in ACP to the specific Vulcan agent
(`vulcan-modernizer` or `vulcan-sast-fixer`), not to a shared Vulcan identity, so cost and audit
separate the two agents without a downstream join.

#### FR-8: No cloud provider credential in the Job pod

When `llm.provider: acp`, the Job carries no AWS credential, no `AWS_BEARER_TOKEN_BEDROCK`, and
no Okta client secret for Bedrock. The `aws-okta-credentials` `envFrom` entry is removed from the
agent definition. This is the observable form of "Vulcan needs no workload account".

#### FR-9: Provider-reported usage supersedes the local estimate

When running through ACP, the run records the token counts the provider returned, not the
`tiktoken` estimate, and records the model identity ACP resolved rather than the `"gpt-5.4"`
literal fallback. The estimate may be retained alongside for one release to quantify the variance
(SC-4), then dropped.

#### FR-10: Failure modes are provider-neutral and distinguishable

An ACP refusal (`403` from policy), a guardrail block, a rate-limit response and a transport
failure are distinguishable in the run record. A policy refusal must not be retried as though it
were transient. Vulcan's existing `AuthError` / provider-neutral error contract in
`shared/errors.py` is extended rather than bypassed.

#### FR-11: Long runs survive credential lifetime

A Vulcan run spans a clone, a full build, a test cycle and multiple scans, and makes many LLM
calls over that window. Whatever credential the Job holds must remain valid for the whole run, or
refresh without agent-visible failure. The interim Bedrock path solved this with an on-disk STS
cache; the ACP path must solve it explicitly rather than inherit an assumption.

The mechanism exists and should not be rebuilt: `acp-harness-sdk`'s auth providers
(`LuminateAuthProvider`, `OktaAuthProvider`) hold an expiry-aware token cache with
`get_token(force_refresh=True)` and `get_expires_in()`. Using them is the requirement; writing a
second token cache inside Vulcan is not.

### Column 2b — tool access

#### FR-12: Tools are registered before they are brokered

Bitbucket, Snyk, Checkmarx and Jenkins are registered in ACP's MCP registry with owner, approval
state and access level, and bound to the Vulcan agents. Registration is achievable now and
delivers inventory, ownership and policy authoring. **It does not by itself deliver enforcement**
— see FR-13 and G-B.

#### FR-13: Brokered tool calls are Phase 2, with a named precondition

A tool call is only governed by ACP once it traverses the gateway, which requires an MCP server
in front of the tool. ACP does not build or operate those servers. The requirement is therefore
scoped as: for each tool, identify the owner, establish whether an MCP surface exists or is
planned, and record the backend authentication mode it would need. Vulcan's tools are fronted by
their own credentials, which lands them in `INJECTED_CREDENTIAL` — **not implemented today**
(G-B). Until then, tool access remains direct and outside ACP enforcement, and the spec says so
rather than implying otherwise.

#### FR-14: The credential-handling boundary is stated

Where a tool is not brokered, Vulcan continues to hold its functional-ID token. That is the
status quo, not a regression, and it is not silently attributed to ACP governance. The
`allowed_tool_ids` field on an ACP access policy is authoring metadata only — at runtime it
appears solely in `audit_snapshot()` — so it must not be cited as per-tool enforcement.

### Cross-cutting — registration, attribution and chargeback

#### FR-15: Both agents and their models are registered

`vulcan-modernizer` and `vulcan-sast-fixer` are registered as ACP agents with owner, business
area, cost centre and environment attributes. The models they use are registered with provider,
regional offering and pricing, so cost is derivable rather than estimated.

#### FR-16: One source of truth per fact

ACP owns model identity, token counts and cost. The AI Agent Usage Metrics API owns remediation
outcomes — vulnerabilities before and after, fix iterations, pull-request URL, run status. Neither
duplicates the other's facts, and a correlation identifier present in both permits the join.

#### FR-17: A run is correlatable end to end

A single identifier links the orchestrator's run record, the Job, the ACP requests for that run,
and the usage-metrics execution record. Without it, a cost figure cannot be attributed to a
remediation outcome and the value case cannot be computed.

The mechanism exists: the gateway reads a caller-supplied `x-luminate-session-id`, sanitises it,
namespaces it as `{entity_type}:{entity_id}:{raw}` and maps it to the Langfuse session id. It
falls back to the `traceparent` trace-id, and invents nothing when the caller declares nothing.
Sending the run identifier on that header is the whole of the requirement on the ACP side.

#### FR-18: Cost is retrievable at the granularity chargeback needs

Two different consumers, and they are **not** served by the same surface today:

| Consumer | Granularity needed | Surface |
|---|---|---|
| Cost-centre chargeback | Period totals per cost centre, entity and model | `/api/v1/chargeback` — `rows`, `summary`, CSV `export`, filterable by cost centre, entity type, model and date range |
| Attributing spend to one remediation | **Per run**, joinable to the outcome for that run | Langfuse session grouping only. The chargeback ledger aggregates by `usage_date` and has **no run dimension** |

The requirement is that both are answerable. The second is the one to verify and, if absent,
raise — see [L-3](#l-3) in the Luminate register.

#### FR-19: Chargeback responsibilities are written down before build

A split of what ACP is accountable for — metering, attribution, the provider billing relationship,
the data feed — versus what stays with the use case and the finance function — recovery to
consuming teams, cost-centre mapping, dispute handling. Reviewed against the existing automated
cloud cost-distribution process before any code is written, because a chargeback model discovered
late is a chargeback model reconciled by hand.

ACP already carries `cost_centre` as a first-class dimension on the usage ledger, which is the
grouping this requirement depends on.

#### FR-20: A spend control exists, and its strength is stated wherever it appears

The use case requires a per-run spend limit. That requirement stands and is recorded here whether
or not the platform can meet it today.

What can be built now is **detection**: threshold alerting computed from the usage and cost data,
per agent and per period. What cannot be built now is a **cap** — nothing debits a quota counter,
and spend is not an expressible dimension at all. Until that changes, every artefact carrying the
control states which of the two it is. See [L-4](#l-4) and [L-5](#l-5).

---

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Latency (dispatch) | The ACP approval check adds negligible time to submission | < 500 ms p95, and it must not dominate `POST /api/v1/agent-runs` |
| NFR-2 | Latency (inference) | Gateway overhead per LLM call, excluding model time | < 200 ms p95 added; the end-to-end run-duration delta is **measured in the PoC**, not asserted |
| NFR-3 | Availability | The ACP gateway must be at least as available as the runs it carries | 99.5% within the run window; a documented behaviour for the remainder |
| NFR-4 | Credential lifetime | Whatever the Job holds outlives the run or refreshes transparently | Longest observed run × 2, with no agent-visible refresh failure |
| NFR-5 | Security | No cloud-provider credential and no model-provider secret in the Job pod under `llm.provider: acp` | Verified by inspecting the rendered Job spec, not by intent |
| NFR-6 | Security | The orchestrator's ACP credential is read-only registry scope | It cannot mutate any ACP record |
| NFR-7 | Attribution completeness | Every ACP request from a Vulcan run carries the agent entity and the correlation identifier | 100%; a request with neither is a defect |
| NFR-8 | Observability | Approval decisions, policy refusals, guardrail outcomes and token/cost per call are all retrievable for a named run | No manual log correlation required |
| NFR-9 | Failure isolation | A metrics or audit publication failure never fails a remediation run | Matches Vulcan's existing `fail_open: true` posture for the usage API |
| NFR-10 | Reversibility | Reverting to `llm.provider: bedrock` requires no image rebuild | Config-only, proven by exercising it |
| NFR-11 | Guardrail suitability | Real remediation prompts — proprietary source, vulnerability detail, stack traces — do not trigger false blocks at a rate that makes runs unreliable | False-block rate quantified in the PoC before wider rollout |
| NFR-12 | Scale | The design holds for the batch shape Vulcan is aiming at, not just a single run | Concurrent-run target stated by Vulcan and load-tested against the gateway |

---

## 5. Capability gaps — prioritised

Every capability selected in D0 that is not ✅, classified and escalated per
[Capability Gap Escalation](../../../process/capability-gap-escalation.md).

| ID | Capability | What is missing | Classification | Impact | Escalation |
|---|---|---|---|---|---|
| **G-A** | [CAP-06](../../../capability-map.md#cap-06) Machine identity | `BearerServicePrincipalAuthentication` is **default-off** — `SERVICE_PRINCIPAL_AUTH_ENABLED` is `false` in Luminate's defaults *and* `"false"` in every Sun Life environment values file. It is also appended per-view rather than sitting in `DEFAULT_AUTHENTICATION_CLASSES`. Separately, the trusted issuer is a **single** configured value (Keycloak in dev, Authentik in UAT) while Vulcan's services hold Okta tokens. | **Integration** (enable + configure) with a possible **component change** if multiple issuers are needed | **Blocks column 1 entirely** | Sun Life deployment work — enable the flag, seed the service principal, resolve the issuer. Raise the multi-issuer question upstream only if a second issuer proves necessary |
| **G-B** | [CAP-03](../../../capability-map.md#cap-03) MCP tool registry | `MCPServerIdentityMode.INJECTED_CREDENTIAL` and `EXTERNAL_EXCHANGE` are **not implemented**. The model docstring is explicit: *"Neither mechanism is implemented yet — a server in either mode is served like `GATEWAY_IDENTITY`, with no credential sent."* Every Vulcan tool is fronted by its own token, so every one of them lands in exactly that unimplemented mode. | **Component change** | **Blocks brokered tool access.** Registration and policy authoring still work; enforcement does not | Consortium — this is the gap that decides whether column 2b is real. Sun Life is unlikely to be the only member with PAT-fronted enterprise tools |
| **G-C** | [CAP-12](../../../capability-map.md#cap-12) Quotas | No counter store; nothing debits and nothing blocks. `matched_quota_ids` is recorded on a span and returned on the decision — telemetry, not enforcement. The gateway tree has zero quota references. | **Component change** | Degrades: the per-run budget this use case requires cannot be enforced | [EACPP-834](https://sunlife.atlassian.net/browse/EACPP-834). Design and a working prototype both exist; the ask is scheduling, not specification |
| **G-D** | [CAP-12](../../../capability-map.md#cap-12) Spend budgets | The dimension enum stops at requests and tokens. `dimension=spend` is Phase 2, gated on the pricing catalogue and cost tracking. | **Component change** | Degrades: **no dollar budget can be expressed**, which is materially different from "not enforced" | [EACPP-834](https://sunlife.atlassian.net/browse/EACPP-834). Carry the distinction into every downstream artefact rather than softening it |
| **G-E** | [CAP-11](../../../capability-map.md#cap-11) Kill switch | Stopping an agent is a status edit. The policy fact export filters to `ACTIVE`, so an inactive agent drops out of the *next* bundle. No stop endpoint, no cascade, no audited stop event — **and no design**. | **Component change** | Degrades: for an agent that edits source and opens pull requests, this is the control that matters most | [EACPP-646](https://sunlife.atlassian.net/browse/EACPP-646). Needs a consortium idea before it can be specified. **Bundle propagation interval must be measured for Vulcan, never quoted** |
| **G-F** | [CAP-14](../../../capability-map.md#cap-14) Lifecycle | No enforced state machine or transition guards on `AgentStatus`, and the two enums do not align — Vulcan's `REVOKED` has no ACP equivalent. | **Component change** | Degrades: ACP cannot express Vulcan's strongest stop state | [EACPP-915](https://sunlife.atlassian.net/browse/EACPP-915), [EACPP-646](https://sunlife.atlassian.net/browse/EACPP-646) |
| **G-G** | [CAP-18](../../../capability-map.md#cap-18) Audit | No external-producer path. The audit contract states *"there is deliberately no public producer REST endpoint; producers call these functions in-process."* Vulcan's orchestrator cannot contribute the dispatch decision to ACP's audit store. | **Component change** | Degrades: the dispatch-time approval lives in Vulcan's logs, the runtime decisions live in ACP's | [EACPP-826](https://sunlife.atlassian.net/browse/EACPP-826) |
| **G-H** | [CAP-15](../../../capability-map.md#cap-15) Risk tiering | Tier is an attribute nobody derives and nothing acts on. | **Component change** | Degrades the E-23 proportionality claim for every onboarding, including this one | [EACPP-648](https://sunlife.atlassian.net/browse/EACPP-648) |
| **G-I** | [CAP-17](../../../capability-map.md#cap-17) Evaluation | No pre-production evaluation, drift detection or auto-demotion. | **Component change** | P2: remediation quality is measured by pull-request review, not by ACP | [EACPP-647](https://sunlife.atlassian.net/browse/EACPP-647) |
| **G-J** | [CAP-20](../../../capability-map.md#cap-20) Cost granularity | The chargeback ledger `ProjectUsageDaily` aggregates by `usage_date`, project, cost centre, entity and model. It carries **no run dimension**, so it cannot answer "what did this remediation cost". Per-run figures exist only as a Langfuse session grouping, which is not the surface the finance path reads. | **Component change** | Degrades: cost-centre chargeback works; per-run attribution to a remediation outcome does not | New — raise as [L-3](#l-3) |
| **G-K** | [CAP-20](../../../capability-map.md#cap-20) Chargeback authorization | `ChargebackViewSet` gates on `IsAuthenticated` plus an `_is_usage_admin` stopgap and sits in the RBAC `_PENDING_MIGRATION` backlog. Its own docstring says registering a dedicated permission string would be *"actively unsafe until the portal RBAC cutover"*. | **Component change** | Degrades: a machine consumer of the chargeback feed has no proper permission to hold, and machine auth is itself default-off (G-A) | New — raise as [L-6](#l-6) |

### The two that decide the shape of this onboarding

**G-A gates column 1 and it is Sun Life's to fix.** No consortium change is needed to enable a
flag and seed a service principal. The issuer question is the substantive part: ACP trusts one
issuer, Vulcan's services carry Okta tokens, and something has to give. Options are to issue the
orchestrator a token from ACP's configured IdP, to point ACP's service-principal issuer at Okta,
or — if both are needed simultaneously — to ask upstream for multi-issuer support. That decision
belongs in D2 with an owner, not in a build ticket.

**G-B decides whether column 2b is real.** It is not a scheduling gap; the mechanism does not
exist. A Bitbucket, Snyk or Checkmarx MCP server fronted by its own token cannot be credentialed
by the gateway today, and a server declared in that mode is silently served *with no credential
at all* — which fails, rather than falling back to something insecure. The honest position for
D2 is: register the tools now, get inventory and ownership and policy authoring now, and be
explicit that brokered enforcement waits on `INJECTED_CREDENTIAL`.

There is one workaround worth naming because it genuinely enforces something: **one MCP server
per trust boundary**. Splitting read from write — a read-only Bitbucket surface separate from the
one that pushes and opens pull requests — gives real separation using `mcp_server`-level policy.
`AccessPolicyTargetType` offers `mcp_server`, `agent`, `model`, `location` and `environment`, and
**none of them is a tool**, so the server is the finest boundary policy can name. The workaround
does not remove G-B, but it means "per-tool authorization" is not being promised on a substrate
that cannot deliver it.

### Interim measures

| Gap | Interim measure | Removed when |
|---|---|---|
| G-A | Keep `JsonAgentRegistry` as the configured implementation until the flag is enabled and the principal is seeded | Machine auth is on in the target environment |
| G-B | Tools stay direct; register them in ACP for inventory, ownership and policy authoring only. Label the state "registered, not brokered" wherever it is reported | `INJECTED_CREDENTIAL` is implemented |
| G-C, G-D | Detection and alerting on ACP usage and cost data. Every artefact that shows it says "monitoring, not enforcement" | The counter store lands; the spend dimension lands |
| G-E | Two-layer containment: deactivate the agent in ACP **and** stop dispatch at the orchestrator. Measure the ACP-side propagation delay and publish the measured number | A first-class kill control exists |
| G-F | Map `REVOKED` onto ACP `inactive` plus an attribute, and treat every unmapped ACP state as "may not run" | An enforced lifecycle state machine lands |
| G-G | Dispatch decisions stay in the orchestrator's own audit, correlated by run identifier | An external-producer audit path exists |
| G-J | Join ACP's Langfuse session grouping to the usage-metrics record on the run identifier, outside the chargeback surface | The usage ledger carries a run dimension |
| G-K | Read the chargeback feed with a human admin credential until machine auth and the RBAC cutover land | `ChargebackViewSet` leaves the `_PENDING_MIGRATION` backlog |

---

## 5a. Luminate register — what to verify, and what to raise

> The gap register above says what is missing. This one says **what to do about it against
> Luminate specifically**: check whether the functionality exists in the form this use case needs,
> and where it does not, carry it as a build item. Splitting them matters because several items
> below turned out to be *partly* built — a capability can be present and still not answer the
> question being asked of it, and that distinction is invisible in a gap table.
>
> **A requirement does not disappear because the platform cannot meet it yet.** Every row keeps
> the requirement it serves, so a later re-verification can tell whether the platform moved.

| ID | Verify in Luminate | Known answer as of `89356d74` | Raise if absent / insufficient | Serves |
|---|---|---|---|---|
| <a id="l-1"></a>**L-1** | Can a machine principal authenticate to the control-plane API, and does the deployment trust the issuer this use case's caller holds? | Mechanism exists (`BearerServicePrincipalAuthentication`) but is **default-off everywhere**, and the trusted issuer is a **single** configured value | Enable and seed it (deployment work). Raise **multi-issuer support** upstream only if one issuer genuinely cannot serve both | FR-5, G-A |
| <a id="l-2"></a>**L-2** | Can the gateway present a stored credential to an MCP backend fronted by its own authorization server? | **No.** `INJECTED_CREDENTIAL` and `EXTERNAL_EXCHANGE` are declared but unimplemented; such a server is served with no credential | Raise as a consortium component change. This is the single item that decides whether brokered tool access is real | FR-13, G-B |
| <a id="l-3"></a>**L-3** | Can cost be retrieved **per run**, joinable to that run's outcome? | **Partly.** `x-luminate-session-id` groups a run in Langfuse, but the chargeback ledger aggregates by `usage_date` with no run dimension | Raise: add a run/session dimension to the usage ledger, or expose a supported session-level cost read | FR-17, FR-18, G-J |
| <a id="l-4"></a>**L-4** | Does anything debit a quota counter and refuse a call? | **No.** The gateway has zero quota references; `matched_quota_ids` is telemetry | Already tracked as [EACPP-834](https://sunlife.atlassian.net/browse/EACPP-834). Add this use case as a named consumer — a scheduling ask carries better with demand behind it | FR-20, G-C |
| <a id="l-5"></a>**L-5** | Can a **spend** limit be expressed at all? | **No.** The dimension enum stops at requests and tokens; `dimension=spend` is a later phase | Same track as L-4, but state it separately: this is "cannot be expressed", not "not enforced" | FR-20, G-D |
| <a id="l-6"></a>**L-6** | Can the chargeback feed be read by a non-interactive consumer under a proper permission? | **No.** `ChargebackViewSet` gates on an `_is_usage_admin` stopgap and sits in the RBAC `_PENDING_MIGRATION` backlog | Raise: a first-class permission for chargeback reads, sequenced with the portal RBAC cutover | FR-19, G-K |
| <a id="l-7"></a>**L-7** | Is there a first-class stop control for a running agent, and how fast does deactivation take effect? | **No control**, and no design. Deactivation drops the agent from the *next* policy bundle; the interval is undocumented | Raise the control ([EACPP-646](https://sunlife.atlassian.net/browse/EACPP-646)); **measure** the interval and publish the number rather than quoting one | G-E |
| <a id="l-8"></a>**L-8** | Can a system that is not the gateway contribute an audit event? | **No.** The contract states there is deliberately no public producer endpoint | Raise an external-producer profile ([EACPP-826](https://sunlife.atlassian.net/browse/EACPP-826)) | FR-16, G-G |
| <a id="l-9"></a>**L-9** | Does the agent lifecycle enforce transitions, and can it express a revoked state? | **No** transition guard; no `REVOKED` equivalent | Raise with the lifecycle track ([EACPP-915](https://sunlife.atlassian.net/browse/EACPP-915)) | FR-4, G-F |
| <a id="l-10"></a>**L-10** | Does `acp-harness-sdk` offer a LangChain / LangGraph chat model, so a framework-based agent can reach the gateway without hand-rolling one? | **No.** `GatewayClient` is a raw httpx client (`chat(messages) -> ChatResult`); the package declares only `httpx`, `pydantic`, `pydantic-settings` and contains no LangChain and no `bind_tools`. The adapter is specified as `ACPChatModel` / `ACPToolkit` under **US-P3 Framework Adapters** with unchecked acceptance criteria, and is listed among the capabilities not present in the shipped version | Raise against the [`acp-harness-sdk` spec](../../platform/acp-harness-sdk/d1-requirements.md) with this use case as the named consumer. **Not Vulcan-specific** — every LangChain or LangGraph workload hits it, and the SDK's own D0 names LangGraph as a target framework | FR-6, DD-1 |

**How to use this table.** L-1 is deployment configuration and is the only one that blocks a
committed phase. L-3, L-6 and L-10 are small, well-shaped additions that this use case is the
first to need concretely — better raised now, with a named consumer, than discovered during
chargeback reconciliation or during the build. L-2, L-4, L-5 and L-7 are consortium-scale and are
already or newly on that track; the useful contribution here is demand and a precise statement of
the shortfall, not another design.

**L-10 is the one with a workaround that costs nothing to reverse.** Vulcan uses LangChain's own
`ChatOpenAI` against the gateway in the meantime (D2 DD-1). Because every agent node goes through
`get_llm()`, adopting `ACPChatModel` when it ships is a change inside one function — so raising
the gap and shipping without it are not in tension.

---

## 6. Data model requirements

| Entity | Key fields | Relationships |
|---|---|---|
| ACP Agent | `id`, `name`, `status`, attributes (`cost_centre`, `business_area`, `environment`) | One per Vulcan agent; referenced by the orchestrator's approval check |
| ACP API Key | scoped to agent, `lum_` prefix, hashed at rest | One per Vulcan agent per environment |
| ACP Service Principal | subject claim, source, RBAC bindings | One for the Orchestration API; read-only registry scope |
| ACP Model + offering | model id, provider, region, pricing | Referenced by `llm.model`; the source of cost |
| Correlation identifier | run id | Present on the orchestrator run, the Job labels, ACP request attribution, and the usage-metrics execution record |
| Usage-metrics execution | `executedBy`, `aiModel`, tokens, vulnerability deltas, `prUrl` | Joined to ACP usage by the correlation identifier |

The orchestrator already labels Jobs with `agi.sunlife.ca/agent-run-id`. That is the natural
correlation identifier and it should be propagated rather than a new one invented.

---

## 7. Edge cases

| Scenario | Expected behaviour |
|---|---|
| ACP unreachable at dispatch | The configured posture from FR-3, logged distinctly from a refusal, bounded in time if it permits dispatch |
| ACP deactivates the agent mid-run | The run continues to completion unless the gateway refuses a subsequent call. The propagation delay is measured and published, not assumed |
| Gateway returns `403` on a policy refusal | Fail the run with a governance outcome, not a transient error. Never retried |
| Guardrail blocks a legitimate remediation prompt | Recorded as a guardrail outcome and surfaced in the run record; the run fails cleanly rather than silently degrading the fix |
| Credential expires mid-run | FR-11: refresh transparently, or the credential outlives the longest run. A mid-run auth failure after twenty minutes of build and scan is the worst possible failure mode |
| Model unavailable or demoted in ACP | Provider-neutral error naming the model and the ACP reason |
| Usage metrics API unavailable | Run completes; publication fails open (existing behaviour) |
| Vulcan run exceeds a configured quota | Nothing happens today (G-C). Must not be described as a control |
| Two agents share one API key | Rejected at design: FR-7 requires agent-scoped credentials so cost separates without a join |
| Job pod restarts (`backoffLimit`) | Correlation identifier is stable across attempts, or attempts are distinguishable — cost must not be double-counted |

---

## 8. Constraints and assumptions

**Constraints**

- OSFI E-23 and B-13 apply. ACP carries the inventory, access, logging and incident-response
  obligations on Vulcan's behalf — with CAP-11, CAP-12 and CAP-15 disclosed as not yet
  enforceable rather than claimed.
- Vulcan runs on OpenShift; ACP's Sun Life deployment is EKS in `ca-central-1`. Cross-cluster
  network reachability from the OpenShift job namespace to the ACP gateway is a hard prerequisite
  and is not assumed.
- The job container already routes through the corporate proxy (`proxy-dev-http.ca.sunlife:8080`,
  hardcoded in `AgentRunService`), with `.sunlifecorp.com` in `no_proxy`. The ACP gateway host has
  to fall on the correct side of that split.
- Java with Maven or Gradle, and Bitbucket Server or TFS, are the only supported platforms.
- Vulcan's `timeoutSeconds` is currently `120` in `agents.json`, which is far below a realistic
  remediation run. Whatever the real deadline becomes bounds NFR-4.

**Assumptions**

- The Orchestration API's own hardening — caller authentication above all — lands independently.
  An approval gate in front of an unauthenticated dispatch endpoint constrains very little, and
  ACP does not absorb that work.
- Vulcan will run the interim Bedrock path. The ACP path is designed to be additive to it.
- No data-residency constraint has been identified beyond keeping traffic inside the Sun Life
  estate. If ACP's Bedrock offering is not in `ca-central-1`, that assumption is re-tested.
- Vulcan's own registry stays authoritative for *how* the agent runs — image, args, resources,
  deadline. ACP is authoritative for *whether* it may.

---

## 9. Traceability

| Requirement | Capability | D0 success criterion | Gap |
|---|---|---|---|
| FR-1, FR-2, FR-4 | CAP-01, CAP-14 | SC-3 | G-F |
| FR-3 | CAP-01 | SC-3 | — |
| FR-5 | CAP-06 | SC-3 | **G-A** |
| FR-6, FR-7 | CAP-08, CAP-06 | SC-1 | — |
| FR-8 | CAP-08 | SC-2 | — |
| FR-9 | CAP-20, CAP-02 | SC-4 | — |
| FR-10 | CAP-09, CAP-10 | SC-8 | — |
| FR-11 | CAP-06 | SC-1 | — |
| FR-12 | CAP-03 | SC-8 | — |
| FR-13, FR-14 | CAP-03 | SC-8 | **G-B** |
| FR-15 | CAP-01, CAP-02, CAP-13 | SC-6, SC-8 | — |
| FR-16, FR-17 | CAP-20, CAP-18 | SC-5 | G-G, G-J |
| FR-18 | CAP-20, CAP-02 | SC-5, SC-5b, SC-7 | **G-J** |
| FR-19 | CAP-20 | SC-7 | **G-K** |
| FR-20 | CAP-12 | SC-7 | **G-C, G-D** |
| NFR-5, NFR-6 | CAP-06, CAP-07 | SC-2 | — |
| NFR-11 | CAP-10 | SC-1 | — |
| — | CAP-11 | SC-8 | **G-E** |
| — | CAP-15 | SC-8 | G-H |

Every functional requirement traces to a capability. The rows with no requirement — CAP-11 and
CAP-15 — are mandatory capabilities this use case inherits and cannot currently be given; they
appear here so the omission is deliberate and visible rather than absent. Every gap in turn
carries a row in the [Luminate register](#5a-luminate-register-what-to-verify-and-what-to-raise),
so no shortfall stops at being described.

---

## 10. Open questions — these need answers before D3

- [ ] **Issuer.** Which IdP issues the token the orchestrator presents, and does ACP trust it?
      This is the single decision that unblocks column 1.
- [ ] **Failure posture.** Refuse on ACP unavailability, or proceed on cached approval? For how
      long? Who signs off on the risk of the answer?
- [ ] **Job credential shape.** Static agent-scoped API key in a Kubernetes Secret, or a
      short-lived credential? A static key repeats the pattern this onboarding exists to retire,
      but FR-11 makes short-lived credentials harder.
- [ ] **Model and region.** The interim was approved for `us-east-2` / `anthropic.claude-opus-4-8`;
      ACP's deployment is `ca-central-1`. Which model, which region, and does the answer create a
      residency question?
- [ ] **Run deadline.** `timeoutSeconds: 120` is not a real remediation budget. What is it, and
      what does that imply for NFR-4?
- [ ] **Network path.** Is the ACP gateway reachable from the OpenShift `agent-workloads`
      namespace, and on which side of the proxy `no_proxy` split does it fall?
- [ ] **Concurrency.** How many simultaneous Vulcan runs is the target? NFR-12 cannot be tested
      against an unstated number.
- [ ] **Tool sequencing.** Which tool is brokered first, who owns its MCP surface, and is anyone
      building it? If nobody is, column 2b is registration-only and should be said so in D2.
- [ ] **Chargeback mechanics.** The platform already streams a filterable CSV export and a JSON
      rows/summary API over the usage ledger. Which of those does the cost-recovery function
      actually consume, at what cadence, and keyed on what?
- [ ] **`executedBy`.** Does the currently-empty field become the ACP entity identifier, and does
      that satisfy Vulcan's recovery-by-consumer requirement?
- [ ] **Value baseline.** What are the current remediation success rate and engineer-hours-per-fix
      on the interactive version? Without it, SC-driven value claims have no denominator.

---

## References

- [ACP Capability Map](../../../capability-map.md)
- [Capability Gap Escalation](../../../process/capability-gap-escalation.md)
- [D0 Discovery](d0-discovery.md)
- `AGI/ai-agent-orchestration-api` — `docs/ARCHITECTURE.md`, `agentregistry/`, `agentrun/`
- `AGI/vulcan-agent-langchain` — `docs/architecture/index.md`, `providers/`, `shared/config.py`,
  `shared/tokens.py`, `services/metrics_runtime.py`, `.roadmap/aws-bedrock-provider.md`
