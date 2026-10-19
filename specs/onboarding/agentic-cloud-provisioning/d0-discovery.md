# Agentic Cloud Provisioning Platform — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Approved 2026-09-02 | **Epic**: [EACPP-1163](https://sunlife.atlassian.net/browse/EACPP-1163)
>
> **Sources**: the use-case review session of 2026-08-29
> ([transcript](references/2026-08-29-use-case-review-transcript.txt),
> [original captions](references/2026-08-29-use-case-review.vtt)) and the written onboarding
> submission the CAH team published the following day
> ([V2](references/2026-08-30-onboarding-submission-v2.md)). Platform facts were verified against
> `luminate` at `origin/main` `1c477cec` and `luminate-sunlife-deploy` at `origin/main` `0bba585`
> on 2026-08-31; every such claim below carries the file it came from.

## Problem Statement

The Cloud Infra AI Platform — the team calls it the Agentic Cloud Provisioning Platform, or the
CAH Agentic Stack — is not asking ACP to help it build something. It is built. Workload account
provisioning, FinOps analysis, CMDB and APM lookups, software audit and incident summary all run
today as durable Temporal workflows behind a Solo.io AgentGateway, in the team's own agentic EKS
clusters, with LangGraph agents in front and a webhook-receiver plus nine domain MCP servers in
between. It runs in test. The team expects to be production-ready within a week.

It is blocked for a governance reason, not a technical one. The submission puts it plainly and
the session made it plainer: an executive sponsor made going through ACP a precondition for the
ETAB submission, so the platform cannot present until this alignment exists.

> *"we're blocked right now because we're using Agent Gateway to do that because we want policies
> and we need it to be super locked into just what we want it to do, so it doesn't go rogue. And
> it was asked that we wait for the agentic control plane and use that instead before we even go
> to ETAB for approval."* — CAH sponsor, 00:00:03

That framing decides what this spec is for. The deliverable that unblocks the team is not a
finished migration; it is a **defensible, written statement of what ACP governs, what it does not
govern yet, and on what evidence** — plus a working DEV slice that demonstrates it. Everything
else follows from that.

Three things are true at once, and the tension between them is the substance of this onboarding:

1. **The integration is unusually cheap.** ACP's gateway *is* agentgateway — `v1.4.1`, pinned in
   `gateway/Dockerfile` (`ARG AGENTGATEWAY_VERSION=v1.4.1`), the exact version Srikanth pinned to
   after hitting Bedrock routing defects in earlier releases. MCP routing semantics are identical
   because it is the same binary. The team is already on the target substrate.
2. **The deployment cannot yet do what both sides assumed it could.** ACP gateways are Helm
   releases of the `luminate-portal` chart, installed *into the ACP cluster*, reaching the control
   plane at `luminate-backend.luminate.svc.cluster.local:50051` over plaintext gRPC, admitted by a
   NetworkPolicy that lists **namespaces**. Neither "our gateway stays in our cluster and ACP
   governs it" nor "ACP's gateway runs in our cluster" is deployable against that shape today.
3. **No ACP gateway is reachable from outside its cluster at all.** Every gateway values file sets
   `slf.traefik.enabled: false`, with the reason written next to it: there is no hostname, no DNS
   record and no certificate SAN for a gateway host. That work is
   [EACPP-1155](https://sunlife.atlassian.net/browse/EACPP-1155), and it sits in **Funnel**.

So the gap is not in the protocol, the wire format or the policy model. It is in reachability and
topology. That is a good problem to have — it is deployment work, not platform redesign — but it
has to be named at D0 rather than discovered in week two of a DEV pilot.

## What the session settled, and what it changed

The written submission was published *after* the session and still carries the pre-session
position in three places. The session is authoritative; this table is the reconciliation, and it
is the first thing to walk through with the team.

| Topic | Submission V2 says | Session settled | Consequence |
|---|---|---|---|
| Front door | "Our preference is gateway-of-gateways… if ACP requires a full swap we accept it" | **Full swap.** *"Swap the gateway, essentially"* (Seth, 08:06). *"So the front door is also ACP then. Any client comes in, they come in through ACP." — "Yep."* (00:05:13) | The gateway-of-gateways option is closed. D2 designs one front door |
| Tenant / app authorization | Open question: "does our tenant/app authorization survive the swap?" | It does not survive as CAH's own layer. *"you wouldn't want to be doing your own authentication to any of those"* (Seth, 00:04:38) | CAH's Entra `appid`/`tid` route rules are replaced by ACP identity, not composed with it |
| Observability | "Langfuse is optional… not a dependency for ACP onboarding" | CAH drops its own Langfuse — which it cannot deploy anyway (public-schema conflict) — and uses ACP's | Correct in direction, wrong in detail: see the Langfuse finding below |
| Identity | Entra app token verified at CAH's gateway | ACP fronts identity; Entra federates for portal SSO, ACP has its own Keycloak | CAH obtains credentials from ACP, not from its own Entra registration |
| Environments | "DEV agents connect to ACP's PROD control plane" (proposed) | Confirmed, and it is how ACP is already built (`values/gateways/prod-dev.yaml`, DD-1) | Not a special arrangement — it is the standing design |
| Component versions | Not covered | Asked for and not answered in session (Seth: *"I don't have a document right now"*) | **Answered here**: agentgateway `v1.4.1`; Luminate gateway `2.2.4` running in prod |

Two session statements need qualifying against the code before they are repeated to the team.
Both are recorded as risks rather than as complaints — they were made in good faith about a
platform that is moving weekly.

- *"we'll just leverage yours and we'll get a project in there"* (Srikanth, 00:03:52), agreed in
  the moment. **There is one Langfuse instance per environment cluster and one project inside it**
  — `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are single scalars in
  `backend/app/settings.py`. Tenancy is by attribution header, not by project.
- *"they do credential rotation within Secrets Manager, Google, Azure, and we're working on the
  HashiCorp Vault integration"* (Seth, 00:06:57), in answer to Matthew Clark's rotation question.
  `backend/app/credentials/secret_backends/` contains `aws_sm.py`, `gcp_sm.py` and `env.py`.
  `vault`, `azure_kv` and `aws_role` exist as enum choices and as schemes named in a docstring;
  `test_backends_registry.py` asserts `unknown backend 'vault'`. Sun Life's *deployment* uses
  Vault and VSO for Luminate's own secrets — that is a different claim from Luminate resolving a
  provider credential out of Vault, and only the first is true.

## Opportunity

Four things make this a good second onboarding, and one makes it a hard one.

**Same binary, same semantics.** ACP is not asking CAH to adopt a new proxy. It is asking CAH to
let ACP configure the proxy it already runs, at the same version.

**A2A is real now, and CAH is the first use case that needs it.** As of `1c477cec`,
`ResourceTranslator.translate()` loops `bundle.agent_assignments` and emits `_build_a2a_bind`;
`agent_endpoint_auth.py` carries the delegated-audience logic; `config-dump-verification.md`
records verification against the pinned v1.4.1 binary plus
`tests/integration/test_a2a_config_verification.py`. Material written before 2026-08-28 says the
translator does not emit A2A. **That is out of date.** CAH's JSON-RPC 2.0 / A2A v0.2 adapter is
the first Sun Life workload that can exercise it.

**Four traffic classes in one onboarding.** Front door, model, MCP tool and agent-to-agent. No
previous Sun Life use case has put all four through the gateway. Whatever this onboarding proves
is reusable for every gateway-fronted use case behind it.

**A real cost-centre join already exists on both sides.** CAH collects `cost_centre` on workload
provisioning; ACP's `ProjectUsageDaily` ledger carries `cost_centre` as a first-class column, not
an attribute to join. Chargeback at BU granularity is a query, not a build.

**And the hard part.** CAH proposes to register *the gateway surface*, not the agents behind it:
*"ACP onboards and governs the AgentGateway surface / service identity, not a per-agent
inventory."* ACP's attribution granularity is the entity a credential resolves to — API keys scope
per user, application, **agent** or MCP server (`gateway/app/middleware/authn.py`). One registered
surface means one entity, which means one line in the usage ledger, one audit subject and one kill
target for Nova, CloudFlux, Stratosphere and everything added later. It also sits against
[CAP-01](../../../capability-map.md#cap-01), which is mandatory precisely because an
unregistered agent is shadow AI. This is the central negotiation of D0 and it is cheap to resolve:
registering an agent is a registry row and a scoped key, and it is what makes cost, audit and
containment granular. D1 carries it as a requirement rather than an argument.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| CAH sponsor (`@1` in the anonymised transcript) | Cloud Automation leadership | Getting to ETAB. Explicitly willing to accept a rough experience: *"We're okay if things break… it's all about a learning journey"* (00:11:43) |
| Srikanth Ramasubramanian | CAH platform engineering owner | That the swap does not cost him the routing behaviour he already tuned; version stability of the agentgateway binary |
| Matthew David Andrew Clark | CAH engineering, identity and secrets | Client-secret rotation and where machine credentials live. Raised the Keycloak-sprawl question for Temporal, which was parked at D0 approval and is **in scope as of 2026-09-08** — see FR-33/FR-34 and gap G-M |
| Mohsen Norouzi | Architecture / ETAB path | The ETAB slot; Temporal's own approval is tracked separately and is not in ACP scope |
| Reza (CAH) | Certificates and friendly URLs for gateways | Owns the hostname and certificate work on the CAH side; the ACP-side counterpart is EACPP-1155 |
| Karen (CAH ops) | Named in session as the engineer available for this spec | Operational ownership through DEV → SIT → PROD |
| Seth Chalmers | ACP architecture and gateway | That the governance claim ACP makes on CAH's behalf is one the platform can honour |
| Lalit Summan | ACP delivery | Sequencing against eleven other queued use cases, and the operating model that does not exist yet |
| Robert Chin | ACP prioritisation | Which driver a use case has; CAH's is a sanctioned executive one |
| Mark Hanson | ACP product | Acceptance criteria and timeline, jointly with Seth |

## Scope

### In scope

- **Traffic class 1 — front door.** CAH callers (Backstage, the C# Automation API, VS Code,
  Nova-style clients) reach an ACP-governed gateway, authenticate with an ACP credential, and are
  authorized by ACP policy. CAH's Entra `appid`/`tid` route rules are retired on the governed path.
- **Traffic class 2 — model.** LLM and embedding traffic through the ACP gateway to Bedrock,
  including the question of *which AWS account* Bedrock is called in.
- **Traffic class 3 — tool / MCP.** CAH's federated MCP backends registered in ACP and served
  through the ACP gateway, including the trust-boundary split that per-server policy forces.
- **Traffic class 4 — A2A.** The standalone adapter registered as an ACP agent endpoint, governed
  at the ACP gateway's A2A route.
- **Registration granularity** — the surface-versus-agents question above, settled with a written
  answer rather than an assumption.
- **Machine credential issuance, and the OAuth question Temporal raises.** ACP's Keycloak issues
  the credentials CAH's non-interactive callers use to reach ACP, with rotation (FR-33). Temporal's
  own OAuth is answered too, and the answer is **Entra as a shared root of trust** — not ACP's
  Keycloak, which federates identity inward by design. ACP identity travels one hop past the
  gateway, to CAH's side-effecting backend, via the built `token_forward` mode (FR-14). Raised by
  Matthew Clark in session (00:14:57), parked at D0 approval, brought in scope on 2026-09-08. No
  platform capability is needed for any of it.
- **Correlation** — carrying `workflow_id` and `conversation_id` into ACP's attribution model so
  one durable operation is findable from both sides.
- **Evidence** — which of CAH's four regulatory evidence classes ACP actually holds, and which
  stay in Backstage and Temporal with a correlation key.
- **The DEV slice**, in the two stages the submission proposes: assistant model + MCP first,
  then one durable dual-entry capability.

### Out of scope

- **Temporal engine internals.** ACP governs the submit → handle → status edge of a named
  capability. It receives no Temporal endpoints, namespaces, task queues or worker credentials,
  and port 5559 is not an ACP interface. The submission states this as a constraint and ACP
  accepts it. Temporal's own ETAB approval is Mohsen's track, not this one. Examining the OAuth
  question did not weaken this — it reinforced it: ACP never contacts Temporal at all, because the
  durable path terminates at CAH's MCP backend, which holds its own Temporal client (FR-34).
- **ACP hosting or operating CAH's MCP servers, webhook-receiver, workers or agents.** ACP
  configures a gateway in front of them. Ownership does not move.
- **Rewriting CAH's LangGraph agents, prompts, workflows or activities.** The integration is at
  the gateway, and the gateway is already there.
- **CAH's internal `AGENT_PROFILE` personas.** Product personas stay CAH's concern; what ACP needs
  is a registered identity per agent, which is not the same thing.
- **ACP acting as Temporal's identity provider.** Examined rather than assumed, and the answer is
  no — on the architecture, not on preference. Luminate federates identity **inward**: Keycloak is
  an aggregator in front of the platform, credentials are minted per registered entity, and the
  entity types are `agent`, `application`, `mcp_server`, `gateway`. Temporal is none of them. Its
  own designs say so in terms: *"Luminate does not become an identity provider that third-party
  applications use to authenticate their own users."* So Temporal Web UI SSO, worker authentication
  and namespace claims all route to **Entra**, which is the better answer anyway — one root of
  trust, two consumers, nothing to build. This is the substantive reply to Matthew Clark's *"is that
  then sprawl to the ACP?"* (00:14:57): it would be, and structurally so.
- **Making CAH's own Langfuse work.** It is being dropped, not fixed.
- **Bedrock content guardrail policy selection.** ACP guardrails apply on the governed path;
  which Bedrock-native Guardrail CAH also assigns is CAH's, pending their own decision.

## Capability Requirements

> **Status: proposed, not yet confirmed.** The
> [D0 process](../../../process/d0-d4-overview.md) requires this table to be completed *with the
> use case, in session, against named capability IDs*. That session has not happened — the
> 2026-08-29 review was an alignment conversation, not a capability walkthrough. Everything below
> is ACP's reading of the submission and the transcript mapped onto the
> [ACP Capability Map](../../../capability-map.md). **Confirming it is the D0 exit condition.**

### Mandatory baseline — acknowledgement pending

Every use case inherits the mandatory capabilities whether or not it asks. Three are not
enforceable today, and this use case is more exposed to two of them than most, because it
side-effects: it creates AWS accounts.

| Confirmed with | Date | Notes |
|---|---|---|
| *Pending — Srikanth Ramasubramanian, CAH sponsor* | *TBC* | **CAP-11 kill switch** is a status edit plus a config push, not an incident-response control, and has no design. **CAP-12 quotas** are modelled but nothing debits a counter, and the dimension enum cannot express spend at all — so the submission's §11 cost asks are measurement, not limits. **CAP-15 risk tiering** is an attribute nobody derives. Two more the team should hear directly: **per-tool authorization does not exist** (`AccessPolicyTargetType` names `mcp_server`, `agent`, `model`, `location`, `environment` — none of them a tool), and **ACP cannot ingest audit events from an external producer**, so the Backstage approval record stays in Backstage |

### Selected capabilities — proposed

| Capability | Why this use case needs it | Priority | Status today | Confirmed by |
|---|---|---|---|---|
| [CAP-08](../../../capability-map.md#cap-08) — Governed AI gateway | The whole integration. All four traffic classes ride it, and it is the same agentgateway binary CAH already runs | P0 launch | ✅ Available — **but no gateway is externally reachable; see D-1** | *Pending* |
| [CAP-04](../../../capability-map.md#cap-04) — Deployment & environment registry | CAH has DEV, SIT and PROD agentic clusters and needs each mapped to a gateway and an ACP environment | P0 launch | ✅ Available | *Pending* |
| [CAP-01](../../../capability-map.md#cap-01) — Agent registry | The registration-granularity question. Mandatory regardless of how it is answered | P0 launch | ✅ Available | *Pending* |
| [CAP-02](../../../capability-map.md#cap-02) — Model registry | Claude Sonnet 4.5, the Opus pin and Titan embeddings, with regional offerings and the pricing that makes cost real | P0 launch | ✅ Available | *Pending* |
| [CAP-03](../../../capability-map.md#cap-03) — MCP tool registry | Nine federated backends. Conditional-mandatory the moment a tool is called, which is immediately | P0 launch | ✅ Available — **but policy stops at the server, not the tool** | *Pending* |
| [CAP-05](../../../capability-map.md#cap-05) — SSO / human identity | Backstage users request and approve provisioning. Today ACP sees only the Backstage service identity | P0 launch | ✅ Available | *Pending* |
| [CAP-06](../../../capability-map.md#cap-06) — Machine identity | Backstage and the C# Automation API are non-interactive callers; so is every LangGraph agent. Temporal's own machine credentials route to Entra, not ACP (FR-34) | P0 launch | ✅ Available for the **data path** (API keys), and `token_forward` carries caller identity to the side-effecting tier. **Default-off for the control plane in all four Sun Life environments**; see D-2 | *Pending* |
| [CAP-07](../../../capability-map.md#cap-07) — RBAC and access policy | Replaces CAH's `appid`/`tid` route rules. Self-service project administration was promised in session and is real | P0 launch | ✅ Available | *Pending* |
| [CAP-09](../../../capability-map.md#cap-09) — Policy enforcement | Fail-closed authorization per call. Note it is *literally* fail-closed — see the risk register | P0 launch | ✅ Available | *Pending* |
| [CAP-10](../../../capability-map.md#cap-10) — Guardrails | Provisioning prompts carry account names, AD groups, cost centres and owner emails. Mandatory, and request- and response-side scanning applies to those payloads | P0 launch | ✅ Available | *Pending* |
| [CAP-13](../../../capability-map.md#cap-13) — Attribute tagging | `cost_centre`, business application, environment, data classification. CAH already collects all four on the provisioning form | P0 launch | ✅ Available | *Pending* |
| [CAP-18](../../../capability-map.md#cap-18) — Audit trail | The record of who invoked which capability. Underpins the submission's §12 | P0 launch | 🟡 Partial — no external-producer path | *Pending* |
| [CAP-20](../../../capability-map.md#cap-20) — Observability and cost accounting | Traces, token counts and the cost-centre ledger. Replaces CAH's own Langfuse | P0 launch | ✅ Available — **per-capability and per-run cost are not; see D1** | *Pending* |
| [CAP-24](../../../capability-map.md#cap-24) — Delegated access and chain authorization | The A2A hop, and the on-behalf-of case the submission names as its future target when approvals move outside Backstage | P1 fast follow | 🟡 Partial — RFC 8693 exchange exists; the full per-link OBO model is designed, not built | *Pending* |
| [CAP-11](../../../capability-map.md#cap-11) — Kill switch | A platform that creates AWS accounts is the case where stopping it must be an action. The submission asks binary versus graduated; the answer is in D1 | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-12](../../../capability-map.md#cap-12) — Quotas and budgets | §11 of the submission. Needs the candid version: the authoring model is real, nothing debits, and spend is not expressible | P1 fast follow | ⚠️ Modelled, not enforced | *Pending* |
| [CAP-14](../../../capability-map.md#cap-14) — Lifecycle governance | Approval routing exists; an enforced agent state machine does not | P1 fast follow | 🟡 Partial | *Pending* |
| [CAP-21](../../../capability-map.md#cap-21) — Single pane of glass | How CAH administers its own project, policies and keys without building a console. Promised in session and real | P1 fast follow | ✅ Available | *Pending* |
| [CAP-19](../../../capability-map.md#cap-19) — Regulatory reporting and evidence | §12 of the submission. The pilot has no hard OSFI bar, which is fortunate | P2 later | 📐 Designed, nothing shipping | *Pending* |
| [CAP-15](../../../capability-map.md#cap-15) — Risk tiering | A side-effecting infrastructure agent is the materiality argument for tiering to exist at all | P2 later | ⚠️ Modelled, not enforced | *Pending* |

### Capabilities offered and expected to be declined

| Capability | Why not |
|---|---|
| [CAP-22](../../../capability-map.md#cap-22) — Federated per-BU gateways | This is the capability CAH's "gateway-of-gateways" preference actually named, and it is 📐 Designed, not built. Recorded here so the decline is a fact about the platform, not a preference. If it ships, revisit |
| [CAP-25](../../../capability-map.md#cap-25) — JIT and break-glass access | Provisioning approval is a mid-workflow human signal, not time-bound elevated access. Revisit if break-glass provisioning is ever required |
| [CAP-26](../../../capability-map.md#cap-26) — Conditional access and data-flow control | No residency driver identified: callers, gateway and workflows are all `ca-central-1`. Re-test if cross-region inference to `us-east-1` carries prompt content that residency rules reach |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation and quality gating | The submission describes deterministic agents that choose tools rather than generate customer-facing decisions. Revisit if an assistant persona starts advising on infrastructure change |
| [CAP-23](../../../capability-map.md#cap-23) — Feedback capture | No identified consumer |
| [CAP-16](../../../capability-map.md#cap-16) — Model cards | Bedrock foundation models, not Sun Life models. Inherits whatever the model registry carries |

> Any selected capability that is not ✅ becomes a row in the D1 capability-gap register and
> follows [Capability Gap Escalation](../../../process/capability-gap-escalation.md).

## Success Criteria

| ID | Criterion | Measurement | Target |
|---|---|---|---|
| SC-1 | A CAH caller reaches an ACP gateway from outside the ACP cluster | A request from a CAH DEV cluster pod to the gateway hostname returns a governed response, TLS verified without `-k` | One green call. **Blocked on EACPP-1155 today** |
| SC-2 | Assistant inference is served through ACP | A Nova-profile conversation completes with the model resolved from ACP's registry and no Bedrock credential in the LangGraph pod | One green conversation in DEV |
| SC-3 | Bedrock is called in the intended account | The account the Bedrock call lands in is named, agreed and demonstrated — CAH's workload account or ACP's shared spoke | Recorded decision plus a CloudTrail entry that proves it |
| SC-4 | An MCP capability is invoked through ACP | `search_business_apps_tool` (read-only) succeeds and is attributed to a registered entity | One green call, visible in the portal |
| SC-5 | Policy refuses something | A capability the caller is not entitled to returns a refusal that names ACP as the decider, not a generic 500 | Deny observed and traced |
| SC-6 | The A2A adapter is governed | A JSON-RPC `tasks/send` reaches the adapter through the ACP gateway's A2A route, and the adapter's NetworkPolicy admits only that gateway | One green task, one blocked direct attempt |
| SC-7 | A durable capability is governed end to end | `trigger_workload_provisioning` → handle → approval → status, entirely through ACP, with the approval event retrievable | One complete run in DEV |
| SC-8 | One operation is findable by both ids | A run is retrievable in ACP by the correlation identifier and in Temporal by `workflow_id`, without a manual join | Demonstrated on the SC-7 run |
| SC-9 | Cost lands on the right cost centre | Period cost for CAH's entities, grouped by `cost_centre`, retrieved from ACP with no manual mapping | One period reconciles |
| SC-9b | Cost is attributable **per capability** | Provisioning spend separated from cost-analysis spend | Achievable only if capabilities are separately registered entities — see D1 |
| SC-10 | Containment works, and its speed is known | Deactivate a CAH entity in ACP and **measure** how long until the next call is refused | A published measured number, never a quoted one |
| SC-11 | The governance story is written down, gaps included | A statement of what ACP holds for each of the four evidence classes in submission §12, with CAP-11, CAP-12, CAP-15 and the audit-producer gap disclosed | Reviewed with the team and usable at ETAB |
| SC-12 | The side-effecting tier knows who called it | A `trigger_workload_provisioning` call arrives at `provisioning-mcp` carrying the caller's validated identity via `token_forward`, and the workflow input records caller, capability and decision — so a provisioning run is attributable at CAH's own boundary, not only at ACP's | One green run showing the caller in the workflow input, plus a rejected token proving the backend validates rather than trusts |

## Dependencies

| ID | Dependency | Owner | Type | Risk if it slips |
|---|---|---|---|---|
| **D-1** | Gateway hostname, DNS record and certificate SAN | ACP deployment — [EACPP-1155](https://sunlife.atlassian.net/browse/EACPP-1155), **Funnel** | **Hard** | Nothing can be reached from a CAH cluster. Every gateway values file has `slf.traefik.enabled: false` with this as the stated reason. **This is the single blocking dependency for slice 1** |
| **D-2** | Machine authentication to the ACP control plane | ACP deployment | **Hard for control-plane automation, not for the pilot** | `SERVICE_PRINCIPAL_AUTH_ENABLED` is `"false"` in all four Sun Life values files, blocked on the same DNS work. Data-path calls use gateway API keys and are unaffected |
| **D-3** | A decision on which AWS account Bedrock is called in, and the IAM to match | ACP deployment + CAH cloud | **Hard** | The gateway's credential chain is a pod-level `~/.aws/config` with one `spokeRoleArn`. Calling Bedrock in CAH's account needs a CAH-dedicated gateway release and a trust-policy change in CAH's account |
| **D-4** | Network path from CAH's agentic EKS clusters to the ACP gateway | CAH cloud + ACP deployment | **Hard** | Both are `ca-central-1` EKS in different accounts. The submission lists this as `(ask human)`; it stays open |
| **D-5** | Gateway release per CAH environment | ACP deployment | **Hard** | DD-3 makes the gateway the failure domain and the kill boundary. CAH's DEV, SIT and PROD each need their own |
| **D-6** | The ACP operating model — SLAs, incident response, remediation | ACP delivery (Lalit) | **Hard for PROD, soft for DEV** | Stated in session as not yet stood up (00:10:48). This, not the technology, is what gates CAH's PROD |
| **D-7** | ETAB slot | Mohsen / CAH | **Hard for CAH's own timeline** | The reason this spec exists. ACP's deliverable is the evidence, not the slot |
| **D-8** | Registration-granularity decision | CAH + ACP | **Hard** | Every downstream requirement — attribution, audit subject, kill target — resolves differently depending on the answer |
| **D-9** | CAH-side certificates and friendly URLs | Reza (CAH) | Soft | Mirrors D-1 on the CAH side |
| **D-10** | Named ACP engineer for the spec | ACP delivery | Soft | Offered in session; Karen named on the CAH side |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Speed versus readiness.** CAH expects to be PROD-ready in a week; ACP has no operating model and no reachable gateway | **High** | **High** | Separate the two deliverables. The DEV slice can start as soon as D-1 lands and is what unblocks ETAB. PROD waits on D-6. Say this before it is discovered |
| **D-1 is not scheduled.** The one hard blocker sits in Funnel | **High** | **High** | Escalate EACPP-1155 with a named consumer attached. A scheduling ask carries better with demand behind it |
| **Fail-closed is literal.** Every governed request makes a synchronous gRPC `CheckAccess` to the control plane; `portal_unreachable` returns `deny`, with no cache and no permissive mode. The submission expects `failureMode: allow` during ACP's test phase | **Medium** | **High** | Correct the expectation at D1. Then treat control-plane availability as a first-class NFR: one backend deployment serves all four workload environments, so its availability is CAH's availability on the governed path |
| **The surface-registration model collapses attribution** to a single entity, and quietly declines CAP-01 | Medium | **High** | Resolve at D0 exit, not at D2. Registering agents is cheap; the alternative silently forfeits per-agent cost, audit and containment |
| **Per-tool policy is assumed.** CAH's webhook-receiver hosts read-only search tools *and* `trigger_workload_provisioning` on one server | **High** | **High** | Policy's finest target is the MCP server. The workaround that genuinely enforces is one server per trust boundary — split read from side-effecting. This is a change to CAH's topology and must be raised now |
| **"ACP auto-ingests our OTel" is not how it works.** There is no external OTLP receiver; ACP sees a call because the call went through its gateway | Medium | Medium | Restate at D1: correlation is caller-driven via `x-luminate-session-id`, with `traceparent` as fallback. CAH's own collector path is unaffected and stays theirs |
| **Cost expectations exceed the ledger.** §11 asks for per-capability and per-run; the ledger aggregates by date, project, cost centre, entity and model | Medium | Medium | Per cost centre and per project work today. Per capability is achievable by modelling capabilities as separate entities. Per run is a platform gap, already raised elsewhere |
| **Vault rotation was promised in session and does not exist** | Medium | Medium | Correct it directly with Matthew Clark. Distinguish "Luminate's own secrets come from Vault via VSO" (true) from "Luminate resolves provider credentials from Vault" (not implemented) |
| **Losing edge Entra terminates a control CAH currently relies on.** In-cluster MCP on `:5557` has no jwtAuth by design; if ACP's gateway becomes the caller, the Entra check at `:5555` disappears | Medium | **High** | The replacement is ACP identity plus NetworkPolicy admitting only the ACP gateway. That is a deliberate posture change and CAH's security reviewers must accept it explicitly, not inherit it |
| **A2A is newly landed.** CAH would be its first real consumer | Medium | Medium | Verified against the pinned binary with an integration test, but never run against a third-party adapter. Make it an explicit PoC exit criterion |
| **Twelve queued use cases.** CAH is not the only claimant on the same delivery capacity | Medium | Medium | CAH has a sanctioned executive driver and has offered engineering help. Both belong in the prioritisation record |

## Open Questions

- [ ] **Run the capability confirmation session.** Walk the table above with Srikanth against named
      capability IDs and record confirmations, priorities and declines. This is the D0 exit condition.
- [ ] **Registration granularity.** Surface only, or surface as a deployment plus one registered
      agent per LangGraph agent? Everything downstream depends on the answer.
- [ ] **Which AWS account does Bedrock get called in?** CAH's workload account, as the submission
      requires, or ACP's shared spoke `131935619052`, as the current chain does? The first needs a
      CAH-dedicated gateway release and a trust-policy change; the second needs CAH to accept that
      Bedrock spend lands outside their account.
- [ ] **Where does the CAH network path to the ACP gateway come from** — VPC peering, PrivateLink,
      Transit Gateway — and who owns building it?
- [ ] **Does CAH accept losing the edge Entra `appid`/`tid` check** on the governed path, and have
      their security reviewers signed that off?
- [ ] **Will CAH split its MCP servers by trust boundary?** Without it, a policy that permits
      `search_business_apps_tool` also permits `trigger_workload_provisioning`.
- [ ] **Is the reduced MCP submit field set acceptable under ACP?** The MCP door takes eight fields;
      the HTTP door takes the full form. If both are governed, is the divergence intentional?
- [ ] **What is the kill boundary CAH wants?** Per gateway — which is what DD-3 gives — per agent,
      or per capability? Only the first two exist.
- [ ] **Does registry `list_tools` discovery or a pinned catalogue win?** Submission open question 3.
- [ ] **What replaces the Backstage approval record in ACP's evidence story**, given there is no
      external audit producer path?
- [ ] **Which CAH environment maps to which ACP environment and gateway**, and does CAH's SIT map to
      ACP's `sit` or its `test`?
- [ ] **Who is the ACP engineer** assigned to this spec, and what is the joint acceptance criteria
      set Mark Hanson and Seth Chalmers own?
- [ ] **What is CAH's concurrency shape?** Nothing in the submission or the session states expected
      requests per second, and the gateway's capacity pool is per release.
