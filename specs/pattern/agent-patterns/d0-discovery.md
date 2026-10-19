# Agent Patterns — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: [EACPP-1290](https://sunlife.atlassian.net/browse/EACPP-1290)
> **Owner**: Sun Life ACP Product Team
> **Scope**: The generalized pattern for how an agent is built, hosted, registered, governed and
> invoked on ACP / Luminate, and the conformance requirements it must meet before the platform
> will serve it.

## Where the ground truth comes from

Every factual claim in this spec is verified against a named source at a named revision. Nothing
is inferred from a design document, and nothing is carried over from an earlier spec without
being re-checked — two of the defects this pattern was expected to report have since been fixed,
and one verdict published elsewhere is now wrong.

| Source | Revision | What it settles |
|---|---|---|
| `AI-Consortium/luminate` (GHE) | `origin/main` @ `1c4a0003`, 2026-09-08 | The catalogue model, the A2A translation, the request-time gates, the fact bundle and the Rego |
| `AI-Consortium/luminate-designs` (GHE) | `origin/main` @ `013d406`, 2026-09-08 | What is designed but not built |
| SLF **dev** Luminate — `slf-eks-t1k-ca-dev` ns `luminate` | queried 2026-09-08; backend `sha-650f011`, gateway `sha-89356d7` | What is registered in dev and how the gateway is actually configured |
| SLF **prod** Luminate — `slf-eks-t1k-ca-prod` ns `luminate`, `luminate-gw-{dev,sit,stage}` | queried 2026-09-08; all components `sha-89356d7` | What is registered in prod and what its gateways actually serve |
| `EDAEACP/luminate-sunlife-deploy` (Bitbucket) | `origin/main` @ `e7c9750`, 2026-09-08 | The Helm chart, trust bundle, NetworkPolicy and AWS role chain |
| `EDAEACP/acp-harness-sdk` (Bitbucket) | `origin/main` @ `4634fe2`, v0.13.0 | What the adoption path does and does not do |
| `CSDP/pipeline-libraries` (Bitbucket) | default branch | The approved JTE libraries and their gate defaults |

Where a claim is an absence, the absence was proved — the search is quoted and the result stated
as zero. Where something is modelled but has no runtime consumer it is marked
**⚠️ modelled, not enforced**, because a field, a serializer and an admin page are not a control.

### Two verdicts that were stale, and are corrected here

- **A2A is implemented.** It was documented as unwired for months after it shipped, and that
  passage was repeated verbatim into two later documents. On `origin/main` the translator emits
  an A2A bind, and in dev **port 5000 is bound** and two agent routes are live with an
  on-behalf-of token exchange attached.
- **The two A2A defects reported in August are closed.** `translate_agent_assignment` now emits
  `backend_tls=BackendTlsPolicy() if scheme == "https" else None`, and the wire alias is
  `backendTLS` in all four places it is declared, matching agentgateway's own dumps (7 of 7 in
  `gateway/tests/testdata/config_dumps/`). Neither is a gap and neither belongs in the register.

## Problem Statement

### An agent is a caller *and* a callee, and only one of those is what teams register

This is the framing everything else hangs off, and the product does not draw it.

| | **Egress** — the agent as caller | **Ingress** — the agent as callee |
|---|---|---|
| What it is | The agent reaches a model, a tool or another agent | Another agent invokes this agent |
| What makes it work | An `Agent` record, a credential on a `Deployment`, and an `AccessPolicy` with `source_type = agent` | An `AgentDeployment` carrying `endpoint_name` and `backend_endpoint`, plus an `AccessPolicy` with `target_type = agent` |
| Gateway path | `/llm/…`, `/mcp/{endpoint}`, `/a2a/{endpoint}` | `/a2a/{endpoint_name}` on **this** agent's endpoint |
| Who must build what | The agent must hold a credential and call out | The agent must be an HTTP service speaking A2A JSON-RPC, reachable from the gateway |

Registering an agent and granting it a model produces a governed caller. It produces nothing a
caller can reach. The live estate shows the consequence: **eight of the ten agents registered in
SLF dev have no `AgentDeployment` at all** and are therefore not callable by anything, and no
record anywhere says that was a decision rather than an omission.

### The live estate

**SLF dev** — 10 agents, 2 reachable:

| Agent | `framework` | `status` | `governance_state` | Callable over A2A? |
|---|---|---|---|:--:|
| `policy-assistant` | `langgraph` | active | `not_evaluated` | ✅ `policy-assistant` → `http://policy-assistant.luminate.svc.cluster.local:8080` |
| `fdes-pharmacy-agent` | `Strands Framewrok` *(sic)* | active | `not_evaluated` | ✅ `pharmacy-agent-endpoint` → AgentCore via VPC endpoint |
| `claims-intake` | `bedrock-agentcore` | active | `not_evaluated` | ❌ |
| `claims-adjudicator` | `bedrock-agentcore` | active | `not_evaluated` | ❌ — *and it is the target of an active `agent → agent` policy* |
| `risk-assessor` | `bedrock-agentcore` | active | `not_evaluated` | ❌ |
| `underwriting-intake` | `bedrock-agentcore` | active | `not_evaluated` | ❌ |
| `slm-analyst` | `strands` | active | `not_evaluated` | ❌ |
| `acp-harness-sample` | `acp-aws-harness-sdk` | active | `not_evaluated` | ❌ |
| `aims-rca-agent` | `Other` | active | `not_evaluated` | ❌ |
| `aims-incident-correlation` | *(blank)* | active | `not_evaluated` | ❌ |

Three things follow, and none is written down anywhere a team would find it.

- **`claims-intake → claims-adjudicator` is an active `target_type = agent` access policy against
  an agent that has no A2A endpoint.** The grant is real, the route does not exist, and nothing
  in the portal reconciles the two. The call fails at the proxy hop, not at a gate that explains
  why.
- **Every agent sits at `governance_state = not_evaluated`.** 10 of 10. The axis exists, it is
  audited, and it has decided nothing.
- **`framework` is free text and reads like it.** `bedrock-agentcore`, `langgraph`, `strands`,
  `Strands Framewrok`, `Other`, `acp-aws-harness-sdk` (a package name renamed months ago) and one
  blank. It cannot be queried, and an inventory question — *how many agents run on AgentCore* —
  is answered by eye.

**SLF prod** — 1 agent, 4 deployments, and they are all the same runtime:

`acp-harness-sample` is deployed on all four gateways (`Luminate Gateway (prod)`,
`luminate-gateway-dev`, `luminate-gateway-sit`, `luminate-gateway-stage`) under the same
endpoint name, and **all four point at one AgentCore runtime ARN in account `131935619052`**.
Four workload environments, one backing agent. Whether that is a demo convenience or a pattern
nobody has ruled out is exactly the question a substrate annex should answer, and does not today.

### The stop control is asymmetric, and the asymmetry runs the wrong way

Withdrawing an agent is the control an incident depends on. Verified against `origin/main`,
setting `Agent.status = inactive`:

- **Stops other agents calling it.** `_collect_agents()`
  (`backend/app/policy_engine/facts.py:674`) selects `status=ACTIVE` only, and
  `authz.rego` requires `agent.status == "active"` before an `allowed_agents` grant is admitted.
  An inactive agent drops out of the fact bundle, so every A2A call to it denies.
- **Does not stop it calling anything.** The source side of the same Rego is
  `_source_matches(policy) if { policy.source_id == input.jwt.sub }` — one line, matching a
  policy against the token subject. It never consults `input.agents`. `_collect_policies()`
  filters on `AccessPolicyStatus.ACTIVE`, not on the source agent's status. So a deactivated
  agent still reaches every model and every MCP server it was granted.

`Agent.status` has exactly **three** non-test runtime consumers across the whole repository —
`facts.py:674`, `access_policies/reach.py:274` (the delegation ceiling) and the model default.
None of them is on the egress path.

`APIKey` verification does not close it either: `AuthNService.verify_api_key` checks the key's
own status and expiry and never looks at `owner_agent.status`. Four agent-owned API keys are
active in dev.

**Stopping a misbehaving agent today means revoking its credential or revoking its access
policies — not deactivating it.** Nothing says so.

### Governance state is modelled, audited and inert

`Agent.governance_state` has a full guarded state machine, a self-approval refusal, a suspension
cascade preview and an audit trail. It has no runtime consumer:

```text
grep -rn "governance_state" backend/app/policy_engine/ backend/app/access_policies/ gateway/app/
  → 0
grep -rn "governance" backend/app/policy_engine/rego/
  → 0
```

`backend/app/governance/suspension.py` says it in its own words:

> Setting `governance_state` to suspended makes the derivation report non_compliant, which denies
> at the access layer — **but only once Epic H reads it. Until then the state is real and the
> denial is not**, and this module is careful not to pretend otherwise.

An ISRA that presents governance suspension as a stop control is presenting a control that does
not exist. This spec presents it as a record, and names the credential/policy path as the control.

### Guardrails cannot be attached to an agent as a callee

`GuardrailTargetType` has an `AGENT` member, so it is easy to read the capability map as saying
content control covers the agent lane. What it covers is the agent **as caller**.

- `GuardrailAttachment`'s target-side scopes are `target_model` and `target_mcp_server`.
  `grep -rn "target_agent" backend/app/guardrails/` **returns zero**.
- `backend/app/policy_engine/facts.py:885` sets
  `_TARGET_SCOPED_FLOWS = frozenset({"model", "mcp_server"})`, with the reason stated in the
  docstring: *"`authz.rego` has a model branch and an mcp_server branch and **no agent branch**"*.

So an agent that accepts A2A traffic **cannot require a prompt-injection or PII scan on its own
inbound requests**. Scanning happens only if every caller independently carries a source-scoped
guardrail with `agent` in `applies_to_target_types`. In dev the number of guardrail attachments
of any kind is **zero**.

Where a scan does run on the A2A lane, its unit is the **raw request body as UTF-8 text** —
`extract_input` recognises the OpenAI chat shape for `target_type = model` and falls through to
the raw body for everything else. A JSON-RPC envelope is scanned as a blob, not as a message.

### The two environments disagree about what an A2A call is

Both were read from the live agentgateway config dump on 2026-09-08.

**Dev** — `pharmacy-agent-endpoint`:

```json
"inlinePolicies": [
  {"a2a": {}},
  {"backendTLS": {"systemRoots": true}},
  {"backendAuth": {"oauthTokenExchange": {
      "grantType": "tokenExchange",
      "audiences": ["agent-01a01b8b-…-01a01d3b-…"],
      "subjectToken": {"source": {"header": {"name": "authorization", "prefix": "Bearer "}}} }}}
]
```

**Prod** — `acp-harness-sample-endpoint`:

```json
"inlinePolicies": [ {"a2a": {}}, {"backendTLS": {"systemRoots": true}} ]
```

No `backendAuth`. The prod cluster runs `sha-89356d7` throughout — 49 commits behind `main` and
**before** the on-behalf-of exchange landed. At that revision `backend/app/agents/audiences.py`
does not exist and `_build_agent_assignments` carries the docstring *"Agents aren't routed
through agentgateway"*. Every A2A assignment in prod therefore emits an empty
`delegated_identity_audience`.

Two sources describe what that means and they say subtly different things, so both belong here.
The portal side records the intent — `AgentAssignment.delegated_identity_audience`: *"Empty means
the gateway calls the agent as itself."* The gateway side decides the wire:
`_forwards_caller_credential` returns `True` for any non-MCP target on the stated grounds that
*"LLM and A2A upstreams are the platform's own"*, and with no `backendAuth` there is nothing to
overwrite the `Authorization` header with — so **the caller's own bearer travels to the backend**
while no platform identity is attached. In prod the A2A upstream is
`bedrock-agentcore.ca-central-1.amazonaws.com`, which is AWS's.

This is not exploitable today, and the reason is worth stating precisely: prod has **zero**
`target_type = agent` access policies, so every A2A request is refused at `CheckAccess` before it
is proxied. The control holding the line is the absence of a grant, not the credential handling.

### The A2A discovery contract cannot be met through the gateway

A2A clients expect an agent card. Nothing in Luminate serves, stores or proxies one:

```text
grep -rin "agent-card|agent.json|agentcard" gateway/app backend/app --include=*.py
  → 0
```

and `/.well-known/` is deliberately **served locally** by the gateway rather than proxied
(`gateway/app/middleware/proxy.py`), so a caller cannot reach a callee's own card even if the
agent publishes one. The only discovery document on the lane is RFC 9728 protected-resource
metadata at `{gateway}/.well-known/oauth-protected-resource/a2a/{endpoint_name}`, which describes
the *audience*, not the agent's capabilities, and 404s by design for a non-delegated endpoint.

### The adoption path does not reach the lane it advertises

`acp-harness-sdk` v0.13.0 is how teams are told to onboard. Its A2A method does not work against
a Luminate gateway, for three independent reasons, all read from `origin/main` at `4634fe2`:

1. **It sends no credential.** `A2AClient.invoke_gateway` sets `content-type` and
   `x-acp-agent-id` and nothing else; `build_http_client` adds only `x-session-id`. Searching
   `a2a.py` for `auth|authorization|bearer|get_token` returns three hits, **all of them prose in
   docstrings**. A Luminate gateway answers an unauthenticated proxy request with 401.
2. **Its default credential is the one shape a delegated A2A endpoint refuses.**
   `resolve_auth_provider(..., surface="gateway")` prefers a `lum_` API key when one is set, and
   `_refuse_agent_unexchangeable` returns 403 `api_key_not_exchangeable` for an API key on a
   delegated endpoint — which, on `main`, is every routable agent endpoint.
3. **It addresses the wrong key.** The method takes `target_agent_id` and builds
   `{a2a_gateway_url}/a2a/{target_agent_id}`, but the gateway route matches
   `pathPrefix=/{endpoint_name}`. In dev those differ: `fdes-pharmacy-agent`'s endpoint name is
   `pharmacy-agent-endpoint`. The default `a2a_gateway_url` also already ends in `/a2a`, so the
   composed URL is `…/a2a/a2a/{id}`.

Two of its headers are also inert against Luminate: `grep -ri "x-session-id"` and
`grep -ri "x-acp-agent-id"` across `gateway/` and `backend/` **each return zero**. Run correlation
falls back to `traceparent`, or to nothing.

### Quotas, cost and the missing operation name

- **Quotas are not enforced on any lane.** `grep -ril quota gateway/app/` **returns zero files**.
  The dimension enum still stops at requests and tokens.
- **The agent lane stamps no GenAI operation name.** `_stash_genai_operation` is explicit:
  *"The agent lane stamps nothing for now — it is a proxied A2A call, and which operation name
  fits it is a question for whoever brings that lane's measures up."* Langfuse therefore types an
  A2A hop as a plain span, not a generation.
- Per-agent usage and cost **do** exist — `UsageBucket` carries `SubjectType.AGENT` and
  `agent_model_timeseries` reads it — but they measure the agent's **own** model calls. When A
  delegates to B and B calls a model on its own credential, the cost lands on B. A caller cannot
  see what a delegation cost it unless B forwards the delegated token rather than using its own.

### The substrate is unbounded

Live today: an in-cluster ClusterIP service on EKS over plain HTTP, and two Bedrock AgentCore
runtimes — one reached through an interface VPC endpoint in dev, one through the public regional
endpoint in prod. In flight: OpenShift-hosted agents behind corporate ingress, and Lambda. Each
has a different reachability, TLS, identity, cold-start and build story and none is written down.

Two registration hazards are already visible in the live data:

- **The registered query string is silently dropped.** `_split_api_base` returns `parsed.path`
  and discards the query, so prod's registered `…/invocations?qualifier=DEFAULT` is rewritten to
  `…/invocations`. Harmless for `DEFAULT`; a silent mis-route for any other qualifier.
- **Two registrations of the same shape disagree on encoding.** Dev's AgentCore path carries the
  ARN percent-encoded (`arn%3Aaws%3A…runtime%2F…`); prod's carries it raw
  (`arn:aws:…runtime/…`), which splits the ARN across two path segments. Registration validates
  that the value is a URL and nothing more — there is no reachability check anywhere.

### There is nothing to take to ETAB

ETAB needs one architecture and one set of decisions. An ISRA needs a control set per deployment
shape with a verification method per control. Neither exists for the agent lane, and the material
is spread across the gateway source, the Rego, two cluster estates that disagree, a deploy chart
and an SDK whose docstrings describe a different product.

## Opportunity

- **One conformance profile.** ASR-1 to ASR-38, assessed once per agent, serving the ETAB
  submission, the ISRA control table and the team's own checklist.
- **Direction becomes a decision.** Egress and ingress are asked as two questions with two
  requirement sets, so "is my agent callable" is answered at registration rather than in support.
- **The stop control becomes honest.** What deactivation reaches, what it does not, and what an
  operator must actually do — stated, with the propagation interval measured rather than quoted.
- **A decision tree by substrate.** OpenShift, EKS, AgentCore, Lambda — pick the row, get the
  requirements. And a **published admission bar** (SUB-E1–E7, SUB-I1–I5) so any other platform is
  assessed against stated criteria instead of negotiated, with an open criterion rather than a
  refusal where it falls short.
- **The adoption path gets a defect list.** Three concrete SDK fixes, each with a test.
- **The onboarding specs get shorter.** `vulcan`, `aims`, `nova`, `gbd`, `mdx`, `orcc` and
  `waldo` reference this profile instead of re-deriving the agent half of their design.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| Business teams building agents | Consumers | One page that says what is required, in each direction, before they build |
| Sun Life ACP Product Team | Owner | One profile referenced by every onboarding spec |
| Security Architecture / ISRA reviewers | Governance | A control set per deployment shape, each with a verification method |
| ETAB | Approvers | One architecture, the decisions taken, and the residual risks named |
| AI Enablement | Consumers | AgentCore and Lambda are first-class substrates, not exceptions |
| Platform administrators | Operators | Deployment, endpoint naming and stop procedures they can execute consistently |
| GDS / DevOps AppDev | Providers | The approved pipeline libraries are used as intended and the gates mean something |
| Data governance | Governance | What an agent reaches, how it is classified, and what is logged |
| Consortium (Luminate) | Component owner | The asks are separated from Sun Life's own work and each is stated once |

## Scope

### In Scope

| # | Capability | Description |
|---|---|---|
| 1 | **Conformance profile** | The numbered requirements an agent must meet — direction, catalogue, identity, authorization, supply chain, runtime, data, observability, lifecycle |
| 2 | **Registration and deployment** | The catalogue model, what registration requires, what makes an agent reachable, and where credentials hang |
| 3 | **Egress governance** | Source access policies, the credential shapes an agent can hold, guardrails and the quota position |
| 4 | **Ingress / A2A** | Route translation, the on-behalf-of exchange, withholding, RFC 9728 discovery and the agent-card gap |
| 5 | **Hosting substrates** | S1 OpenShift, S2 EKS, S3 Bedrock AgentCore, S4 AWS Lambda — reachability, TLS, network control, egress — plus the **SUB-E / SUB-I admission bar** any other platform is assessed against |
| 6 | **Build and supply chain** | The approved JTE path, the SonarQube / Snyk / Checkmarx gates, image provenance |
| 7 | **Operations** | Audit events, tracing attribution, run correlation, cost attribution, the stop path |
| 8 | **ETAB / ISRA artefacts** | The architecture to present and the control table to assess against |

### Out of Scope

- **Building any specific agent.** This spec states requirements; the teams build.
- **The MCP server an agent calls** — [`mcp-server-patterns`](../mcp-server-patterns/d0-discovery.md)
  (EACPP-1176) owns the callee side of `/mcp`.
- **The credential, invocation and inference patterns shared with every lane** —
  [`integration-patterns`](../../platform/integration-patterns/d0-discovery.md) (EACPP-1112).
- **Gateway and environment topology** —
  [`gateway-environment-strategy`](../../platform/gateway-environment-strategy/d0-discovery.md) (EACPP-1089).
- **Re-specifying the harness SDK.** [`acp-harness-sdk`](../../platform/acp-harness-sdk/d0-discovery.md)
  (EACPP-791) is referenced and three defects are raised against it; it is not redesigned here.
- **Agent framework selection.** LangGraph, Strands, AgentCore and the rest are substrate.
- **Gateway internals.** Routing, guardrail evaluation and the proxy data path are
  consortium-owned.
- **Onboarding any specific use case.** Each has its own spec.
- **Authoring the end-user guides** — the canonical home is
  [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse).

## Capability Requirements

Assessed against the [ACP Capability Map](../../../capability-map.md). This is a platform pattern
rather than a use-case onboarding, so the table records which capabilities the pattern depends on
and whether the map's status survives verification.

| Capability | Why this pattern needs it | Status in the map | Verified status | Note |
|---|---|---|---|---|
| **CAP-01 — Agent registry** | The catalogue this pattern registers into | ✅ Available | ✅ Confirmed for egress · **⚠️ Incomplete for ingress** | Registration makes a governed caller. Reachability needs an `AgentDeployment`, and nothing in the product says so |
| **CAP-04 — Deployment & environment registry** | An agent is reachable only via `Deployment` + `AgentDeployment` on a gateway | ✅ Available | ✅ Confirmed | Uniform with MCP servers and models |
| **CAP-06 — Machine identity** | The agent authenticates to the gateway | ✅ Available | ✅ Confirmed for the data plane | Registry M2M stays default-off — see `integration-patterns` |
| **CAP-07 — RBAC and access policy** | `AccessPolicy(source_agent → …)` and `(… → target_agent)` are the grants | ✅ Available | ✅ Confirmed both directions | `AccessPolicySourceType` and `AccessPolicyTargetType` both carry `agent` |
| **CAP-08 — Governed AI gateway** | `/llm`, `/mcp/{endpoint}` and `/a2a/{endpoint}` are the only governed paths | ✅ Available | **🟢 Stronger than the map says** | The A2A lane is live: one route per agent deployment, `backendTLS` on https, RFC 9728 discovery, port 5000 bound in dev |
| **CAP-09 — Policy enforcement** | Fail-closed `CheckAccess` on every request, both directions | ✅ Available | ✅ Confirmed | Portal unreachable denies; no cache |
| **CAP-10 — Guardrails** | Content control on what an agent sends and receives | ✅ Available | **⚠️ Caller-side only for agents** | No `target_agent` scope, no agent branch in the Rego. An agent cannot require a scan of its own inbound traffic |
| **CAP-11 — Kill switch** | Withdrawing an agent | 🟡 Partial | **🔴 Weaker than the map says** | Deactivation stops ingress and **not** egress. Governance suspension enforces nothing |
| **CAP-13 — Quotas / budgets** | Bounding an autonomous caller | ⚠️ Modelled, not enforced | ⚠️ Confirmed | `grep -ril quota gateway/app/` returns zero |
| **CAP-14 — Lifecycle governance** | The `governance_state` axis on the agent record | 🟡 Partial | **⚠️ Modelled, not enforced** | Full state machine, zero runtime consumers, 10 of 10 dev agents at `not_evaluated` |
| **CAP-18 — Audit trail** | Control-plane mutations and data-plane access events | ✅ Available | ✅ Confirmed | `CaptureProtocol.a2a` exists |
| **CAP-20 — Observability and cost accounting** | Per-agent attribution | ✅ Available | 🟡 Confirmed partial | `UsageBucket` carries `SubjectType.AGENT`; the A2A hop itself stamps no operation name and produces no generation |
| **CAP-24 — Delegated access** | Reaching a callee agent as the calling user | 🟡 Partial | **🟢 Stronger than the map says** | Every routable agent deployment is a delegated target on `main`; there is no identity mode to opt out of |
| **INT-02 — Secrets (Vault / VSO)** | Where an agent's own secrets live | — | — | Requirement, not a gap |
| **INT-03 — Network and ingress** | Gateway-to-agent reachability and TLS trust | — | — | Requirement, not a gap |
| **INT-08 — Build and release (Jenkins JTE)** | The approved build path and its scanning gates | — | **⚠️ Gates disabled estate-wide** | Named in D1 as ASR-24 to ASR-27; inherited from `mcp-server-patterns` and re-checked |

## Success Criteria

| Criterion | Measurement | Target |
|---|---|---|
| **SC-1** A team can self-serve the requirements | An agent is onboarded in both directions without a platform-team design conversation | First new agent after publication |
| **SC-2** Direction is explicit | Every registered agent records whether it is egress-only, ingress-only or both, and the record matches its deployments | 100% of agents |
| **SC-3** Every substrate is covered, and any new one is assessable | Each of OpenShift, EKS, AgentCore and Lambda has a stated requirement set, and the SUB-E / SUB-I criteria are published so a new platform is assessed rather than negotiated | 4 of 4 + the bar published |
| **SC-4** The stop control is understood and adequate | An operator can withdraw an agent in both directions, and the propagation interval is a measured number per environment | Measured; documented runbook |
| **SC-5** Governance state means something | Every agent has moved off `not_evaluated`, or the axis is explicitly declared non-operational | 100% of agents |
| **SC-6** The estate is consistent | No agent is the target of an access policy without a matching A2A endpoint; no environment serves A2A without the exchange | 0 mismatches |
| **SC-7** The adoption path works | The harness SDK can invoke a Luminate A2A endpoint end-to-end | Green integration test |
| **SC-8** ETAB and ISRA are unblocked | The architecture and control table are accepted as the submission basis | Accepted |

## Dependencies

| Dependency | Component / Team | Type | Risk if delayed |
|---|---|---|---|
| MCP server pattern | `mcp-server-patterns` (EACPP-1176) | Soft | The tool half of an agent's egress is re-derived here |
| Shared credential and invocation patterns | `integration-patterns` (EACPP-1112) | Soft | Duplication between the two specs |
| Gateway and environment topology | `gateway-environment-strategy` (EACPP-1089) | Hard | Endpoint naming collides across environments; the prod/dev A2A divergence is not resolvable |
| Prod image uplift past the A2A exchange | `sunlife-deployment` (EACPP-596) | **Hard** | Prod continues to serve A2A with no credential |
| Harness SDK A2A fixes | `acp-harness-sdk` (EACPP-791) | Hard | The stated adoption path cannot reach the lane |
| Luminate deployment and gateway trust store | `sunlife-deployment` (EACPP-596) | Hard | An agent behind corporate ingress is unreachable |
| JTE pipeline libraries | GDS / DevOps AppDev (`CSDP/pipeline-libraries`) | Hard | No approved path to enforce scanning |
| Governance rulesets and applicability rules | `governance-intake` (EACPP-877) | Soft | `governance_state` stays at `not_evaluated` for every agent |
| Egress kill switch | Consortium | **Hard** | There is no way to stop an agent calling by deactivating it |
| Agent-target guardrails | Consortium | Soft | A callee agent cannot require a scan of its own inbound traffic |
| AgentCore inbound authorizer configuration | AI Enablement / AWS account owners | Hard | A delegated A2A hop to AgentCore cannot be authenticated |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| A team registers for egress and assumes its agent is callable | **High** | Medium | ASR-1 makes direction an explicit declaration; the decision tree asks it first |
| An operator deactivates an agent during an incident and believes it is stopped | **High** | **High** | ASR-31 states the real stop path; D3 W4 raises the consortium ask and publishes the runbook |
| `governance_state` is presented to an assessor as an operating control | **High** | **High** | Declared ⚠️ modelled-not-enforced throughout; named as residual risk R-3 |
| Prod continues to serve A2A with no credential as grants are added | Medium | **High** | ASR-13 forbids serving a non-delegated agent endpoint; D3 T4 uplifts the prod image before any `target_type = agent` policy is created |
| Prompt injection reaches an agent with no scan configurable on its ingress | **High** | **High** | ASR-19 requires caller-side guardrails as the interim; named as residual risk R-2 and a consortium ask |
| A registered `backend_endpoint` is wrong and nothing detects it | **High** | Medium | ASR-6 states the encoding and query-string rules; ASR-7 requires a post-registration reachability test |
| One agent instance backs four environments | Medium | **High** | ASR-9 requires a distinct backing runtime per environment, or a recorded exception |
| An autonomous caller runs unbounded because quotas are not enforced | **High** | Medium | ASR-22 requires a substrate-side bound; residual risk R-5 |
| The A2A hop's downstream cost is invisible to the caller | Medium | Medium | ASR-30 requires the delegated token to be forwarded where cost must follow the caller |
| Substrate proliferation outruns the profile | Medium | Medium | The profile is substrate-independent; only the hosting annex is per-substrate |
| Frameworks proliferate and the inventory is unqueryable | **High** | Low | ASR-8 fixes a controlled vocabulary for `framework` and `type` |

## Open Questions

- [ ] **Is an egress-only agent a complete registration, or an incomplete one?** Eight of ten dev
      agents are in that state. If it is legitimate, the catalogue should say so; if not, the
      portal should warn.
- [ ] **What is the stop control meant to be?** Deactivation is asymmetric and governance
      suspension is inert. Does Sun Life ask the consortium for a source-side status check, or
      operate a credential-revocation runbook and accept the latency?
- [ ] **Does a callee agent get to require a guardrail on its own inbound traffic?** Today it
      cannot. This is the single largest asymmetry with the MCP lane, which has target-scoped
      guardrails.
- [ ] **Can one AgentCore runtime legitimately back four workload environments?** Prod does this
      today. If not, what is the promotion model — one runtime per environment, or aliases?
- [ ] **Does an AgentCore runtime accept Luminate's exchanged bearer?** Luminate emits an OAuth
      bearer, never SigV4, so the runtime needs a custom JWT authorizer trusting the platform's
      issuer. Confirmed for dev's VPC-endpoint deployment by the fact that the exchange is
      configured; the inbound authorizer configuration itself lives in an account outside ACP's
      reach and must be confirmed by the account owner.
- [ ] **Is Lambda in scope as an A2A callee?** It needs a stable URL and a warm token, and the
      token endpoint is rate-limited. D2 records a verdict; the cost model behind it needs
      confirming.
- [ ] **Does an agent need its own APM number** for Snyk tagging and ISRA registration, or does it
      inherit the consuming application's? Same question `mcp-server-patterns` leaves open.
- [ ] **Where does an agent's data classification live** — the catalogue `metadata`, an attribute,
      or the owning use case's data contract?
