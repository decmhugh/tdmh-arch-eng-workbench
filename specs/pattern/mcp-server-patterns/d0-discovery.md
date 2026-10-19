# MCP Server Patterns — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: [EACPP-1176](https://sunlife.atlassian.net/browse/EACPP-1176)
> **Owner**: Sun Life ACP Product Team
> **Scope**: The generalized pattern for building, deploying, registering and consuming an MCP
> server on ACP / Luminate, and the conformance requirements a server must meet before it is
> served.

## Where the ground truth comes from

Every factual claim in this spec is verified against a named source at a named revision. Nothing
here is inferred from a design document.

| Source | Revision | What it settles |
|---|---|---|
| `AI-Consortium/luminate` (GHE) | `origin/main` @ `10d6ee89`, 2026-09-01 | The catalogue model, the identity modes, the gateway translation and the request-time gates |
| SLF dev Luminate, `slf-eks-t1k-ca-dev` ns `luminate` | queried 2026-09-01 | What is actually registered and how it is actually configured |
| `CSDP/pipeline-libraries` (Bitbucket) | default branch, read 2026-09-01 | The approved JTE libraries, their steps and their gate defaults |
| `EDAEACP/luminate-user-guides` | `origin/main` | What a team is told today |

Where a claim is an absence, the absence was proved — a search that returns nothing is cited as
such rather than left as "no evidence found".

## Problem Statement

MCP is now the way a governed agent reaches a tool, and MCP servers are arriving on the estate
faster than any statement of what one has to be. There is no page a team can be sent to.

### The estate has one identity posture, and nobody chose it

Four MCP servers are registered in SLF dev. **All four are `identity_mode = gateway_identity`** —
the mode whose documented meaning is that *the backend receives no credential at all*. None is on
the platform's own default, `delegated_exchange`.

| Server | Transport | Identity mode | Backend endpoint | Tool records |
|---|---|---|---|---|
| `claims-tools` | http | `gateway_identity` | `http://claims-tools.luminate.svc.cluster.local:8000/mcp` | 5 |
| `underwriting-tools` | http | `gateway_identity` | `http://underwriting-tools.luminate.svc.cluster.local:8000/mcp` | 5 |
| `pharmacy-mcp-server` | http | `gateway_identity` | `https://dev-corp-aws-ca1-k8s.sunlifecorp.com/dev-genai-pharmacymcp-ns/pharmacy-mcp-server/mcp` | **0** |
| `claims-tools-bedrock` | http | `gateway_identity` | *(deprecated)* | 5 |

Two consequences follow, and neither is written down anywhere a team would find it:

- **Two of the three live servers are reached over plain HTTP** on a cluster-internal address. The
  gateway is the only client, so this is defensible — but it is defensible only because of a
  network property nobody has stated as a control, and it stops being defensible the moment a
  server moves namespace or the estate grows a second caller.
- **The server itself performs no authentication.** In `gateway_identity` mode the gateway
  deliberately strips the caller's credential before the backend call, so the server cannot
  authenticate the caller even if it wanted to. Whether that is right depends entirely on what the
  tools do — and nothing in the registration flow asks.

### Authorization stops at the server, and the capability map overstates it

The [ACP Capability Map](../../../capability-map.md) marks **CAP-03 MCP Tool Registry as
✅ Available**, described as *"tools bound to agents rather than assumed"*. Verified against
`origin/main`, that is stronger than what runs:

- `AccessPolicyTargetType` has five members — `mcp_server`, `agent`, `model`, `location`,
  `environment`. **None of them is a tool.**
- `AccessPolicy.allowed_tool_ids` exists as a column, is exposed by the serializer, and has
  **no runtime consumer** — no reader in the gateway tree, none in the policy engine, none in any
  Rego package.
- The gateway *does* parse the JSON-RPC method out of the request body
  (`gateway/app/middleware/authz.py::_mcp_request_method`), but it does so **after**
  `check_access` has already returned. The method is stamped onto the span as
  `x-luminate-mcp-method` and used to type the Langfuse observation. It is **never** an input to
  the decision — `AuthzRequest` carries the endpoint name as `selector` and nothing finer.

So an access policy granting an agent an MCP server grants it **every tool that server exposes,
now and in future**. That is a defensible platform position, but it makes the *server* the unit of
trust, and therefore makes "which tools live together behind one endpoint" an architecture
decision a team is currently making by accident.

### The tool catalogue is not evidence

`MCPTool`, `MCPResource` and `MCPPrompt` rows are entered by hand. There is **no discovery on
main** — a search for `last_discovery` across the backend returns zero. `pharmacy-mcp-server`, the
one server on a real corporate-ingress path, carries **zero tool records**, while its tools are
live.

An ISRA that treats the catalogue as an inventory of what a server exposes is treating a manual
copy as a source of truth. Tool discovery exists on an unmerged branch
(`feature/mcp-tool-discovery`); it is not on `origin/main` and must not be assumed.

### Security scanning is not attached to MCP servers as a class

Sun Life has an approved build path — the JTE libraries in
[`CSDP/pipeline-libraries`](https://bitbucket.sunlifecorp.com/projects/CSDP/repos/pipeline-libraries/browse),
62 of them, including `sonarqube`, `snyk`, `checkmarx`, `python`, `npm`, `maven`, `quay` and `ecr`.
The gates are **on by default**: `snyk` ships `RUN_SNYK_SCAN = true`, `ENFORCE_SNYK_GATE = true`,
`SEVERITY_THRESHOLD = "high"`; `checkmarx` ships `ENFORCE_CHECKMARX_GATE = true`.

Two things undercut that in practice:

- **Every ACP repository turns the gates off.** `acp-agent-registry`, `acp-mcp-registry` and
  `agent-control-plane-ui` all carry `enforce_snyk_gate = false` and
  `enforce_checkmarx_gate = false`, each with a `disable_gate_reason_*` string that describes a
  setup-era workaround. The scans run; nothing fails on them.
- **The Checkmarx step does not scan.** `libraries/checkmarx/steps/code_analysis.groovy` resolves
  the latest *merged pull request* for the repo, looks up the scan Checkmarx already ran for that
  PR, waits for its gate evaluation and reports it. A repository with no merged PR logs
  `New repository PR does not exist. Checkmarx scan is skipped.` and passes. Default
  `BRANCHES_TO_SCAN` is `["develop"]` — a repo on `main` matches nothing unless it overrides.

So "we scan with Snyk and Checkmarx" is true as a statement about the toolchain and, today, close
to vacuous as a statement about the ACP estate. An MCP server is an internet-shaped protocol
handler executing tool code on behalf of an autonomous caller; it is exactly the class of workload
where that gap matters.

### The substrate is unbounded

Today it is FastMCP on OpenShift and plain ASGI services on EKS. In flight are Bedrock AgentCore
runtimes and AgentCore Gateway, and a vendor-hosted SaaS MCP endpoint is a live ask. Each has a
different reachability story, a different TLS story, a different credential story and a different
build path — and none of that is written down.

Two failure modes are already on record from the platform side and will recur for every team:

- **`stdio` cannot be onboarded.** The catalogue models it, but the bundle builder refuses it with
  `stdio_transport_not_supported_for_remote_gateway`. A local-process MCP server is not a remote
  MCP server, and teams routinely start with the former.
- **A corporate-ingress backend needs Sun Life PKI in the gateway's trust store.** Leaves under
  `*.sunlifecorp.com` are issued by `Sun Life Financial Issuing CA3`, which no public root store
  carries. Before this was fixed the gateway returned `500 upstream service error`, which names
  neither TLS nor the certificate.

### There is nothing to take to ETAB

ETAB needs one architecture and one set of decisions. An ISRA needs a control set per deployment
shape, each control with a verification method. Neither exists. The material is spread across the
gateway source, four cluster runbooks, a user guide and a capability map row that overstates one
of the capabilities.

## Opportunity

- **One conformance profile.** A numbered requirement set an MCP server is assessed against once.
  The same profile serves the ETAB submission, the ISRA control table and the team's own checklist.
- **A decision tree by substrate.** OpenShift, EKS, AgentCore, vendor-hosted, Lambda — pick the row, get
  the requirements.
- **The identity-mode decision becomes real.** Five modes exist, two are unimplemented, and the
  choice determines what credential (if any) the server sees and therefore what it must validate.
  Presented as a matrix, it becomes a design decision with consequences rather than a default
  nobody touched.
- **The trust boundary gets stated.** Once "the server is the unit of authorization" is written
  down, "one server per trust boundary — split read from write" becomes a design rule a team can
  follow, and the compensating control an ISRA can be written against.
- **Scanning gets an owner.** Naming the exact libraries, steps and configuration keys turns
  "we scan" into a gate with an evidence path.
- **The onboarding specs get shorter.** `gbd`, `mdx`, `aims`, `orcc`, `waldo`, `nova` and
  `ai-ready-data` each reference this profile instead of re-deriving the MCP half of their design.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| Business teams building MCP servers | Consumers | One page that says what is required, before they build |
| Sun Life ACP Product Team | Owner | One profile referenced by every onboarding spec |
| Security Architecture / ISRA reviewers | Governance | A control set per deployment shape, each with a verification method |
| ETAB | Approvers | One architecture, the decisions taken, and the residual risks named |
| GDS / DevOps AppDev | Providers | The approved pipeline libraries are used as intended, and the gates mean something |
| Platform administrators | Operators | Deployment, endpoint naming and identity-mode choices they can execute consistently |
| Data governance | Governance | What the tools reach, how it is classified, and what is logged |
| AI Enablement | Consumers | AgentCore and Bedrock substrates are first-class, not exceptions |

## Scope

### In Scope

| # | Capability | Description |
|---|---|---|
| 1 | **Conformance profile** | The numbered requirements an MCP server must meet — protocol, transport, identity, authorization, supply chain, runtime, data, lifecycle |
| 2 | **Catalogue model** | Server, tool, resource and prompt records; what registration requires; what the records are and are not evidence of |
| 3 | **Deployment substrates** | OpenShift, EKS, Bedrock AgentCore, vendor-hosted, AWS Lambda — reachability, TLS, network policy and what each must satisfy |
| 4 | **Identity** | The five outbound identity modes, the inbound credential eligibility each implies, and RFC 9728 discovery |
| 5 | **Authorization** | Access policies, the server-granularity boundary, guardrails on the MCP lane, and the compensating design rule |
| 6 | **Build and supply chain** | The approved JTE path, the SonarQube / Snyk / Checkmarx gates, image provenance and SBOM |
| 7 | **Operations** | Audit events, tracing attribution, session correlation, health and lifecycle governance |
| 8 | **ETAB / ISRA artefacts** | The architecture to present and the control table to assess against |

### Out of Scope

- **Building any specific MCP server.** This spec states requirements; the teams build.
- **The credential, invocation and inference patterns shared with every lane** —
  [`integration-patterns`](../../platform/integration-patterns/d0-discovery.md) (EACPP-1112) owns the
  four credential shapes, the token exchange and the `/llm` `/mcp` `/a2a` surfaces. This spec
  goes deeper on `/mcp` only.
- **Gateway and environment topology** —
  [`gateway-environment-strategy`](../../platform/gateway-environment-strategy/d0-discovery.md) (EACPP-1089).
- **The standalone ACP MCP Registry service.** A separate component with its own governance scope.
- **Designing tool-granular authorization.** Raised here as a consortium ask, not solved here.
- **Gateway internals.** Routing, guardrail evaluation and the proxy data path are
  consortium-owned.
- **Onboarding any specific use case.** Each has its own spec.
- **Authoring the end-user guides** — the canonical home is
  [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse).

## Capability Requirements

Assessed against the [ACP Capability Map](../../../capability-map.md). This is a platform spec
rather than a use-case onboarding, so the table records which capabilities the pattern depends on
and whether the map's status survives verification.

| Capability | Why this pattern needs it | Status in the map | Verified status | Note |
|---|---|---|---|---|
| **CAP-03 — MCP Tool Registry** | The catalogue of servers and tools this pattern registers into | ✅ Available | **⚠️ Modelled, not enforced at tool granularity** | The map's *"tools bound to agents rather than assumed"* does not hold: no tool target type, no runtime consumer of `allowed_tool_ids`. Server-granularity binding **is** real. Correction proposed in D3. |
| **CAP-04 — Deployment & environment registry** | An MCP server is reachable only via a `Deployment` + `MCPServerDeployment` on a gateway | ✅ Available | ✅ Confirmed | Uniform with agents and models |
| **CAP-06 — Machine identity** | The calling agent or application authenticates to the gateway | ✅ Available | ✅ Confirmed for the data plane | Registry M2M remains default-off — see `integration-patterns` |
| **CAP-07 — RBAC and access policy** | `AccessPolicy(source → target_type=mcp_server)` is the grant | ✅ Available | ✅ Confirmed at server granularity | The boundary this spec makes explicit |
| **CAP-08 — Governed AI gateway** | `/mcp/{endpoint_name}` is the only governed path to a tool | ✅ Available | ✅ Confirmed | One route per server; the multiplexed shorthand is gone |
| **CAP-09 — Policy enforcement** | Fail-closed `CheckAccess` on every MCP request | ✅ Available | ✅ Confirmed | Portal unreachable denies |
| **CAP-10 — Guardrails** | Banned words, PII and Model Armor on the MCP lane | ✅ Available | ✅ Confirmed | `GuardrailTargetType.MCP_SERVER` exists |
| **CAP-11 — Kill switch** | Withdrawing a server from the fleet | 🟡 Partial | 🟡 Confirmed partial | Status edit plus governance `SUSPENDED`; propagation is push, but must be measured not quoted |
| **CAP-14 — Lifecycle governance** | The `governance_state` axis on the server record | 🟡 Partial | **🟢 Stronger than the map says** | A guarded transition action, a self-approval refusal and a suspension cascade preview all exist on `origin/main` |
| **CAP-18 — Audit trail** | Control-plane mutations and data-plane access events | ✅ Available | ✅ Confirmed | `AccessProtocol.MCP` |
| **CAP-20 — Observability and cost accounting** | Per-server, per-method attribution | ✅ Available | ✅ Confirmed | `x-luminate-mcp-method`, `tools/call` typed as `execute_tool` |
| **CAP-24 — Delegated access** | On-behalf-of calls to an MCP server | 🟡 Partial | 🟡 Confirmed partial | `delegated_exchange` is implemented; `injected_credential` and `external_exchange` are not |
| **INT-02 — Secrets (Vault / VSO)** | Where a server's own secrets live | — | — | Requirement, not a gap |
| **INT-03 — Network and ingress** | Gateway-to-backend reachability and TLS trust | — | — | Requirement, not a gap |
| **INT-08 — Build and release (Jenkins JTE, Quay/Artifactory)** | The approved build path and its scanning gates | — | **⚠️ Gates disabled estate-wide** | Named in D1 as MSR-15 to MSR-18 |

## Success Criteria

| Criterion | Measurement | Target |
|---|---|---|
| **SC-1** A team can self-serve the requirements | A team registers a conforming server without a platform-team design conversation | First new server after publication |
| **SC-2** Every substrate is covered | Each of OpenShift, EKS, AgentCore, vendor-hosted and Lambda has a stated requirement set | 5 of 5 |
| **SC-3** Identity mode is a decision, not a default | Every registered server has a recorded rationale for its `identity_mode` | 100% of servers |
| **SC-4** The trust boundary is enforced by design | Every server's tool set is within one trust boundary, or is split | 100% of servers reviewed |
| **SC-5** The scanning gate means something | SonarQube, Snyk and Checkmarx enforced on every MCP server repository, with evidence retrievable per build | 100% of MCP server repos |
| **SC-6** The catalogue matches reality | Tool records present and current for every registered server | 100%, re-verified per release |
| **SC-7** ETAB and ISRA are unblocked | The architecture and control table are accepted as the submission basis | Accepted |

## Dependencies

| Dependency | Component / Team | Type | Risk if delayed |
|---|---|---|---|
| Shared credential and invocation patterns | `integration-patterns` (EACPP-1112) | Soft | Duplication between the two specs |
| Gateway and environment topology | `gateway-environment-strategy` (EACPP-1089) | Soft | Endpoint naming collides across environments |
| Luminate deployment and gateway trust store | `sunlife-deployment` (EACPP-596) | Hard | A corporate-ingress backend is unreachable |
| JTE pipeline libraries | GDS / DevOps AppDev (`CSDP/pipeline-libraries`) | Hard | No approved path to enforce scanning |
| Checkmarx project + PR scan configuration per repo | Security / AppSec | Hard | The Checkmarx gate passes without scanning |
| Tool discovery | Consortium (`feature/mcp-tool-discovery`, unmerged) | Soft | The catalogue stays a manual copy |
| Tool-granular authorization | Consortium | Soft | The one-server-per-trust-boundary rule remains the only control |
| Governance rulesets and applicability rules | `governance-intake` (EACPP-877) | Soft | `governance_state` stays at `not_evaluated` for every server |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Teams read "the gateway authorizes MCP calls" as tool-level control | **High** | **High** | State the boundary in the profile; make one-server-per-trust-boundary a requirement, not advice |
| `gateway_identity` stays the estate default by inertia | **High** | Medium | MSR-8 requires a recorded rationale; D3 T7 re-assesses the existing four |
| The catalogue diverges from what servers expose | High | Medium | MSR-6 makes tool records a release-time obligation until discovery lands |
| Checkmarx gate passes vacuously | Medium | **High** | MSR-17 requires evidence of a completed scan, not merely a green stage |
| An MCP server is exposed outside the gateway | Medium | **High** | MSR-9 requires the backend to be unreachable except from the gateway, verified by NetworkPolicy or equivalent |
| A tool reaches production data with no classification | Medium | **High** | MSR-20 requires per-tool data classification at registration |
| Prompt injection via tool output | **High** | Medium | MSR-21 requires response guardrails and bounded output; named as a residual risk for ETAB |
| Substrate proliferation outruns the profile | Medium | Medium | The profile is substrate-independent; only the reachability annex is per-substrate |
| `stdio` servers are built first and cannot be onboarded | Medium | Low | Stated as MSR-2 and in the decision tree's first question |

## Open Questions

- [ ] Is a **vendor-hosted / third-party MCP server** in scope for onboarding at all before
      `injected_credential` or `external_exchange` is implemented? Today such a server can only be
      reached as `gateway_identity` — with no credential — which is unlikely to be acceptable.
- [ ] Who owns **enabling the scanning gates** on MCP server repositories — the building team, the
      ACP product team or AppSec — and what is the exception process?
- [ ] Should ACP publish a **reference MCP server template** (FastMCP + Dockerfile + JTE
      `pipeline_config.groovy` + Helm/kustomize) so conformance is the default rather than an
      audit?
- [ ] Does an MCP server need its own **APM number** for Snyk tagging and ISRA registration, or
      does it inherit the consuming application's?
- [ ] For AgentCore-hosted servers, is the governed route `{gateway}/mcp/{endpoint}` or
      SigV4-direct to the runtime ARN? Only the first is governed — the same question
      `integration-patterns` T5 raises for agents.
- [ ] Where does **tool-output data classification** live — the tool record, an attribute, or the
      server's data contract?
