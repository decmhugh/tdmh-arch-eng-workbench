# MCP Server Patterns — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Epic**: [EACPP-1176](https://sunlife.atlassian.net/browse/EACPP-1176) · Board label `acp-product-team`

Two requirement sets, deliberately separated.

- **MSR-*n*** — the **MCP Server Conformance Profile**. What a *server* must satisfy to be served.
  This is the set an ISRA is written against and the set a team is assessed on.
- **FR-*n*** / **NFR-*n*** — what **ACP / Luminate and the Sun Life build platform** must provide
  so that conformance is achievable and verifiable.

Every MSR carries an owner, an enforcement point and a verification method. A requirement that
cannot be evidenced is not a requirement.

## User Stories

### US-1: Know what is required before building

**As a** team about to build an MCP server,
**I want** one page stating what my server must satisfy,
**So that** I do not discover a blocking requirement after the code is written.

**Acceptance Criteria**:

- [ ] **Given** I have chosen a hosting substrate, **When** I read the profile, **Then** I can list
      every requirement that applies to me and how each will be verified.
- [ ] **Given** I intend to use `stdio`, **When** I read the first decision, **Then** I learn
      immediately that it cannot be onboarded remotely and what to do instead.
- [ ] **Given** I have no security-scanning pipeline yet, **When** I read the build section,
      **Then** I have the exact JTE libraries, steps and configuration keys to adopt.

### US-2: Choose an identity mode deliberately

**As a** platform administrator registering a server,
**I want** the identity-mode choice presented as a matrix with its consequences,
**So that** the mode is a recorded decision rather than an untouched default.

**Acceptance Criteria**:

- [ ] **Given** a server whose tools reach regulated data, **When** I select an identity mode,
      **Then** the matrix tells me which modes are acceptable and what the server must validate.
- [ ] **Given** I select `gateway_identity`, **When** I save, **Then** a rationale and a
      compensating network control are recorded.
- [ ] **Given** I select a mode that is not implemented, **When** I read the matrix, **Then** I
      learn that the server will be reached with **no credential**, not that it will fail.

### US-3: Understand the trust boundary

**As an** architect designing a tool set,
**I want** the authorization granularity stated plainly,
**So that** I put the right tools behind one endpoint.

**Acceptance Criteria**:

- [ ] **Given** the profile, **When** I read the authorization section, **Then** it states that a
      grant is per **server** and covers every tool that server exposes, now and in future.
- [ ] **Given** a mixed read/write tool set, **When** I apply the design rule, **Then** I split it
      into separate servers or implement server-side tool authorization.
- [ ] **Given** an ISRA reviewer asks "how is tool X restricted", **When** I answer, **Then** the
      answer is a named control, not an assumption about the platform.

### US-4: Assess a server once, reuse the evidence

**As an** ISRA reviewer,
**I want** a control table with a verification method per control,
**So that** I can assess an MCP server without reading the gateway source.

**Acceptance Criteria**:

- [ ] **Given** a registered server, **When** I work the control table, **Then** every row has an
      owner, an enforcement point and evidence I can retrieve.
- [ ] **Given** a second server on the same substrate, **When** I assess it, **Then** the
      substrate-level controls are already evidenced and only the server-specific rows are new.
- [ ] **Given** a residual risk, **When** I read the table, **Then** it is named as residual rather
      than absent.

### US-5: Operate the estate

**As a** platform operator,
**I want** to see which servers are non-conforming and to withdraw one quickly,
**So that** an incident is bounded.

**Acceptance Criteria**:

- [ ] **Given** an incident, **When** I withdraw a server, **Then** every agent granted it loses
      access at the next config push, and the propagation time is a measured number.
- [ ] **Given** a suspension, **When** I preview it, **Then** I see which deployments and access
      policies it takes down before I commit.
- [ ] **Given** the estate, **When** I ask which servers are non-conforming, **Then** the answer is
      queryable rather than a survey.

## The MCP Server Conformance Profile

Legend for **Class**: **M** = mandatory for every server · **C** = conditional, with the condition
stated · **R** = recommended.

### A. Protocol and transport

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-1** | M | The server implements MCP over a **remote transport** — Streamable HTTP (preferred) or HTTP+SSE — and declares the MCP specification revision it implements. | Catalogue `transport`; gateway `MCPTransportType` | Registration record; `initialize` response |
| **MSR-2** | M | The server is **not** `stdio`. A local-process server must be re-hosted behind HTTP before onboarding. | `backend/app/gateways/sync.py::_mcp_assignment_for` refuses with `stdio_transport_not_supported_for_remote_gateway` | The deployment appears in the bundle's `skipped` list if violated |
| **MSR-3** | M | The backend is reachable at a **stable absolute URL including scheme and path** (e.g. `https://host/mcp`), and its Luminate endpoint name is a **single URL-safe path segment** — no `/`, no dot segment, no character that percent-encodes differently on the two matchers. | `MCPServerDeployment.backend_endpoint` (URLField) and `endpoint_name` (`validate_key`) | Registration rejects a malformed value |
| **MSR-4** | M | The server tolerates being **fronted**: it works behind the path prefix `/{endpoint_name}`, emits no absolute self-referential URLs that assume its own hostname, and round-trips `Mcp-Session-Id` if it is stateful. | agentgateway route `path_prefix` | Functional test through `{gateway}/mcp/{endpoint_name}` |

### B. Catalogue and tool contract

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-5** | M | The server is **registered before any caller is granted it**: `key`, `name`, `transport` and owning `project` are mandatory; `description`, `version` and `documentation` are populated. | `POST /api/v1/catalog/mcp-servers` | Catalogue record |
| **MSR-6** | M | **Tool, resource and prompt records are current at every release.** There is no automatic discovery on `origin/main`; the records are hand-maintained and are the only inventory an assessor can read. Each tool carries `name`, `description`, `input_schema` and `access_level`. | `MCPTool` / `MCPResource` / `MCPPrompt` | Diff the catalogue against the server's live `tools/list` at release |
| **MSR-7** | M | The **tool contract is change-controlled**. Adding a tool, widening an input schema, or raising a tool's `access_level` is a governed change — not a silent deploy — because an existing grant automatically covers it. | Release process + MSR-13 | Change record referencing the catalogue diff |
| **MSR-8** | R | Tool **names and descriptions are written for a model**, are unambiguous within the server, and do not embed instructions to the calling agent. | Design review | Review record |

### C. Identity and reachability

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-9** | M | `identity_mode` is a **recorded decision with a rationale**, chosen from the matrix in [D2 · Identity](d2-design/identity.md). The default is `delegated_exchange`; the estate is currently entirely `gateway_identity`. | `MCPServer.identity_mode` (audited — it is in `audit_snapshot()`) | Catalogue record + decision note |
| **MSR-10** | M | The backend is **not reachable except from the serving gateway**. Mandatory for every mode and load-bearing for `gateway_identity`, where the server receives no credential and therefore cannot authenticate anyone. | NetworkPolicy, security group, private endpoint or equivalent | Negative test from a non-gateway workload |
| **MSR-11** | C | **TLS on the gateway→server hop** wherever the hop leaves the pod network. If the leaf is issued by Sun Life PKI, the issuing CA must be present in the **gateway's merged trust bundle** — `gateway.caBundle` merges, `slf.caBundle` substitutes; only the former is correct for a gateway. | agentgateway TLS; `SSL_CERT_FILE=/etc/ssl/merged/ca-bundle.crt` | `grep -c BEGIN "$SSL_CERT_FILE"` in the gateway pod; a successful call |
| **MSR-12** | C | A **`delegated_exchange`** server **validates the presented token**: signature against the portal's JWKS, expected issuer, `aud` equal to its own deployment audience, and expiry. It must reject a token audienced to a different deployment. | Server-side | Test with a token minted for another deployment — expect refusal |
| **MSR-13** | C | A **`token_forward`** server trusts **the same issuer as the gateway** and validates accordingly. The gateway refuses to forward a platform-minted credential (`lum_` API key or `lud_at_` delegated token) to a forward-mode endpoint, so the server will only ever see an IdP-signed JWT. | `gateway/app/middleware/authn.py::_refuse_platform_minted` | 403 `platform_minted_not_forwardable` on a negative test |
| **MSR-14** | C | A server fronted by a **third-party authorization server** is **not onboardable today**. `injected_credential` and `external_exchange` are enum members whose mechanisms are not implemented; a server in either mode is served like `gateway_identity`, with **no credential sent**. | `MCPServerIdentityMode` docstring, `origin/main` | Confirm the mode's behaviour before onboarding; escalate as a gap |

### D. Authorization and content control

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-15** | M | **One server per trust boundary.** Every tool behind a single endpoint shares one grant, one classification tier and one blast radius. Read and write tools with materially different privilege are split into separate servers. | Design review; the platform grants at server granularity only | Architecture record; the tool inventory of each server |
| **MSR-16** | C | Where MSR-15 cannot be met, the server implements **its own per-tool authorization** from the identity it receives. This is only possible in `delegated_exchange` or `token_forward` — a `gateway_identity` server has no identity to authorize. | Server-side | Test that a caller entitled to tool A cannot invoke tool B |
| **MSR-17** | C | **Guardrails are configured on the MCP lane** wherever tool inputs or outputs may carry PII. `GuardrailTargetType.MCP_SERVER` supports banned words, PII detection and Model Armor, on request and response, in enforce or warn mode. | `backend/app/guardrails/` | Guardrail binding on the server; a positive detection test |
| **MSR-18** | M | **Tool output is treated as untrusted.** The server bounds output size and does not return content that instructs the calling model. Prompt injection through tool results is a named residual risk. | Server-side + response guardrails | Review; response-guardrail configuration |

### E. Build and supply chain

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-19** | M | The server is built by the **approved Jenkins JTE pipeline** using the Sun Life libraries — `pod_template`, `git`, the language library (`python` / `npm` / `maven` / `gradle` / `dotnet`), `sonarqube`, `snyk`, `checkmarx`, and `quay` or `ecr`. Ad-hoc image builds are not acceptable for a served server. | `Jenkinsfile` + `pipeline_config.groovy` | The build job and its stage list |
| **MSR-20** | M | **SAST — Checkmarx.** The repository has a Checkmarx project, pull-request scanning is configured, `enforce_checkmarx_gate = true`, and `branches_to_scan` matches the repository's actual integration branch (the library default is `["develop"]`). A green stage is **not** evidence: the step reads an existing PR scan and logs `New repository PR does not exist. Checkmarx scan is skipped.` when there is none. | `libraries/checkmarx/steps/code_analysis.groovy` | The Checkmarx scan id and gate evaluation recorded on the build |
| **MSR-21** | M | **SCA — Snyk.** `run_snyk_scan = true`, `enforce_snyk_gate = true`, `severity_threshold` no weaker than the library default `high`, and the generated `snyk-sbom.json` retained as a build artifact. Where an APM number exists it is passed so findings are attributable. | `libraries/snyk` / `libraries/python` `sca_scan` | Build artifacts `snyk-results.html`, `snyk-sbom.json` |
| **MSR-22** | M | **Static analysis — SonarQube** runs and its quality gate is enforced. Any disabled gate carries a `disable_gate_reason_*` with an owner and an expiry, recorded as an exception rather than left as a default. | `libraries/sonarqube` `static_code_analysis` | The SonarQube project and its gate status |
| **MSR-23** | M | The **image is produced by that pipeline** and pushed to an approved registry (Quay or ECR). The deployment references an immutable tag or digest — never `latest`. | `quay` / `ecr` library; deploy manifest | Registry digest vs deployed digest |

### F. Runtime and secrets

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-24** | M | The container runs **non-root** with `allowPrivilegeEscalation: false`, and declares **CPU and memory requests *and* limits** on every container including init containers. On Sun Life clusters Gatekeeper denies a pod without them, and the failure is silent in `rollout status`. | Gatekeeper `container-must-have-limits-and-requests` | `kubectl get events` shows no admission denial; the pod is running |
| **MSR-25** | M | The server's **own secrets** — upstream API keys, database credentials — come from Vault via the Vault Secrets Operator, or AWS Secrets Manager. Never baked into the image, never a literal in a ConfigMap or a manifest. | INT-02 | Manifest review; the secret's source |
| **MSR-26** | M | **Health and lifecycle**: a readiness probe, a graceful shutdown, and a named owner. Luminate does **not** probe MCP server health — `MCPServer.status` is operator-set and there is no readiness check anywhere in the backend — so liveness is the hosting platform's job entirely. | Deployment manifest | Probe configuration; an owner in the catalogue record |

### G. Data and observability

| ID | Class | Requirement | Enforcement point | Verification |
|---|:---:|---|---|---|
| **MSR-27** | M | **Every tool declares the data it reaches and its classification.** A tool touching regulated or personal data is identified at registration, not discovered at assessment. | Catalogue `metadata` / attributes; data governance | The tool inventory with classifications |
| **MSR-28** | M | The server **does not log tool arguments or results** that carry sensitive data, and its logs carry no credential material. | Server-side | Log review |
| **MSR-29** | R | The server **propagates `Mcp-Session-Id`**, which the gateway uses as the run-correlation unit on the MCP lane in preference to any other header. Without it, per-run correlation falls back to `traceparent` or nothing. | `gateway/app/middleware/authz.py` | A trace showing a stable session across calls |
| **MSR-30** | M | The server is **registered against a `governance_state`** and moves through it by the guarded transition action rather than a direct write. A server that has never been assessed reads `not_evaluated`, which is distinguishable from `out_of_scope`. | `POST /api/v1/catalog/mcp-servers/{id}/transition` | The governance state and its recorded reason |

## Functional Requirements — what the platform must provide

### FR-1: Publish the conformance profile as a self-service artefact

The profile is published in
[`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse)
as a page a team is pointed at before it builds, with the decision tree first.

### FR-2: Record the identity-mode rationale

Registration captures why an identity mode was chosen. Until the product carries a field, the
rationale is recorded in the server's `description` or `metadata` and in the onboarding record.

### FR-3: Make non-conformance queryable

The estate can be queried for: servers on `gateway_identity`, servers with zero tool records,
servers whose backend endpoint is `http://`, and servers at `governance_state = not_evaluated`.

**API sketch** — all four are answerable from the existing catalogue API:

```text
GET /api/v1/catalog/mcp-servers?transport=http
  → id, key, name, transport, status, identity_mode, tool_count, deployment_count
```

### FR-4: State the authorization boundary in the product surface

The portal's access-policy screen states that a grant on an MCP server covers every tool that
server exposes. `allowed_tool_ids` is not presented as a control until it has a runtime consumer.

### FR-5: Correct CAP-03 in the capability map

CAP-03 is downgraded from ✅ Available to reflect that tool-granular binding is modelled but not
enforced, with server-granular binding confirmed as available.

### FR-6: Provide a reference implementation

A reference MCP server — FastMCP, Dockerfile, `Jenkinsfile`, `pipeline_config.groovy` with the
gates on, and a deployment manifest satisfying MSR-24 and MSR-25 — so conformance is the starting
point rather than an audit finding.

### FR-7: Publish the substrate annex

One page per substrate — OpenShift, EKS, Bedrock AgentCore, vendor-hosted, AWS Lambda — stating reachability,
TLS, network control and the build path for that shape.

### FR-8: Publish the failure-mode table for the MCP lane

The refusals a caller can receive, by cause, so a 403 is diagnosable: policy denial, endpoint
credential ineligibility (`api_key_not_exchangeable`, `not_exchangeable`,
`platform_minted_not_forwardable`), withheld endpoint, and portal-unreachable fail-closed.

### FR-9: Expose RFC 9728 discovery in the guidance

`{gateway}/.well-known/oauth-protected-resource/mcp/{endpoint_name}` describes a delegated MCP
endpoint and is deliberately unauthenticated. A non-delegated endpoint returns 404 — an intended
answer, not a fault. Server implementers must know this exists before they build their own
discovery.

### FR-10: Measure kill-switch propagation

The interval between withdrawing a server and the last gateway ceasing to serve it is measured per
environment and published. Configuration reaches gateways by a long-lived push stream, not
polling — but the number must be measured, never quoted.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| **NFR-1** | Availability | The control plane is on the request path — every MCP call makes a `CheckAccess` RPC with no local cache, and a portal outage denies rather than fails open | Design around it; state it in the ISRA |
| **NFR-2** | Latency | Gateway overhead on an MCP call — authn, authz RPC, guardrails, forward | Measured and published per environment |
| **NFR-3** | Security | No MCP backend reachable from outside its serving gateway | 100%, verified by negative test |
| **NFR-4** | Security | No platform-minted credential leaves the gateway to a third-party backend | Enforced in code; verified by negative test |
| **NFR-5** | Observability | Every served MCP request is attributable to caller, server, endpoint and JSON-RPC method | 100% of requests through the gateway |
| **NFR-6** | Auditability | Every control-plane mutation of a server record and every data-plane access decision is recorded in the append-only audit trail | 100% |
| **NFR-7** | Supply chain | Every served MCP server image traceable to a pipeline build with SAST, SCA and SonarQube evidence | 100% of servers |
| **NFR-8** | Recoverability | Withdrawing a server takes effect across every serving gateway | Measured; target under 60s |

## Data Model Requirements

The platform-side model exists; this records what it is so the profile can reference it.

| Entity | Key fields | Relationships |
|---|---|---|
| `MCPServer` | `key`, `name`, `transport`, `status`, `identity_mode`, `governance_state`, `version`, `tags`, `metadata` | belongs to `Project`; has many `MCPTool` / `MCPResource` / `MCPPrompt`; has many `MCPServerDeployment` |
| `MCPTool` | `name`, `description`, `input_schema`, `access_level` (`admin` / `read` / `write`) | belongs to `MCPServer`; unique on (`server`, case-insensitive `name`) |
| `MCPResource` | `uri`, `name`, `mime_type` | belongs to `MCPServer`; unique on (`server`, `uri`) |
| `MCPPrompt` | `name`, `description`, `input_schema` | belongs to `MCPServer` |
| `Deployment` | `resource_type = "mcp_server"`, `deployment_key`, gateway, environment, location, project | one per (gateway, `deployment_key`, server) |
| `MCPServerDeployment` | `endpoint_name`, `backend_endpoint` | one-to-one with `Deployment` |
| `AccessPolicy` | `source_*`, `target_type = "mcp_server"`, `scope_type`, `created_by` | the grant; `allowed_tool_ids` exists but has no runtime consumer |

## Edge Cases

| Scenario | Expected behaviour |
|---|---|
| Server registered with `stdio` transport | Registration succeeds; the deployment is **silently skipped** from the gateway bundle with `stdio_transport_not_supported_for_remote_gateway`. The server is never served and nothing surfaces in the portal. |
| Deployment with an empty `backend_endpoint` | Skipped with `missing_backend_endpoint`; never translated into a route |
| `delegated_exchange` server on a gateway with no token endpoint or client id | The target is **withheld entirely** rather than served as the gateway. Serving it would silently substitute the gateway's identity for the user's. |
| Caller presents `lum_` API key to a delegated endpoint | 403 `api_key_not_exchangeable` — reads identically to a policy denial unless the eligibility rule is known |
| Caller presents a plain user JWT (no actor) to a delegated endpoint | 403 `not_exchangeable` |
| Caller presents `lum_` or `lud_at_` to a `token_forward` endpoint | 403 `platform_minted_not_forwardable`; the credential must not leave the gateway |
| Caller presents an API key to a `none` (gateway_identity) endpoint | Admitted — the gateway strips the credential before the backend call |
| Bare `/mcp/` with no endpoint name | 404 once routes exist; there is one route per server and no multiplexed shorthand |
| Backend leaf issued by Sun Life PKI, CA absent from the gateway bundle | agentgateway `invalid peer certificate: UnknownIssuer` → surfaces as **500 upstream service error**, naming neither TLS nor the certificate |
| Server's tool set grows after the grant | The existing grant covers the new tool immediately. This is why MSR-7 makes the tool contract change-controlled. |
| Server suspended in governance | The suspension cascade must be previewed first; the preview names the deployments and access policies it will take down |
| Same `endpoint_name` on two gateways | Legitimate — uniqueness is per `(gateway, deployment_key, server)`; the same key across gateways is what makes it one promoted resource |

## Constraints

- **Server granularity is a platform property, not a configuration.** Tool-level authorization
  cannot be turned on; the compensating control is architectural.
- **No tool discovery on `origin/main`.** The catalogue is hand-maintained until the consortium
  merges discovery.
- **Two identity modes are enum-only.** `injected_credential` and `external_exchange` are served as
  `gateway_identity` with no credential. Any plan depending on them is blocked.
- **Sun Life clusters deny pods without resource requests and limits** (Gatekeeper), including init
  containers, and the denial does not surface in `rollout status`.
- **No `docker.io` egress from Sun Life cluster pods.** Every base and runtime image must be
  mirrored to Quay or ECR.
- **The Checkmarx gate is PR-driven.** A repository without merged-PR scans passes without being
  scanned.
- **The default `branches_to_scan` is `["develop"]`.** A repository whose integration branch is
  `main` matches nothing unless it overrides.
- **Regulatory**: OSFI E-23 model/tool inventory and change control; OSFI B-13 Principle 15 (least
  privilege) and Principle 17 (incident response); Quebec Law 25 and PIPEDA where tools reach
  personal information.

## Capability Gaps

| Capability | What is missing | Classification | Impact | Escalation |
|---|---|---|---|---|
| **CAP-03** — MCP Tool Registry | Tool-granular authorization. No tool member on `AccessPolicyTargetType`; `allowed_tool_ids` has no runtime consumer; the JSON-RPC method is parsed after the decision, for telemetry only | Component change (consortium) | A grant covers every tool on the server. Compensated by MSR-15 / MSR-16 | Consortium ask · D3 T20 |
| **CAP-03** — MCP Tool Registry | Automatic tool discovery. `feature/mcp-tool-discovery` is unmerged; the catalogue is hand-entered and a live server carries zero tool records | Component change (consortium) | The catalogue is not an inventory; MSR-6 makes it a manual release obligation | Consortium ask · D3 T21 |
| **CAP-24** — Delegated access | `injected_credential` and `external_exchange` unimplemented | Component change (consortium) | A server fronted by a third-party authorization server cannot be onboarded with a credential | Consortium ask · D3 T22 |
| **CAP-24** — Delegated access | Per-user third-party credentials. Neither mode reaches a vendor as the individual user; `injected_credential` is one shared credential per deployment | Component change (consortium) | A vendor tool that must act with the person's own three-legged OAuth token cannot be onboarded at all | [ACPDIS-165](https://ai-consortium.atlassian.net/browse/ACPDIS-165) · [EACPP-1444](https://sunlife.atlassian.net/browse/EACPP-1444) |
| **CAP-11** — Kill switch | No stop endpoint, no cascade beyond the config push, propagation interval unmeasured | Component change (consortium) + local measurement | Withdrawal is a status or governance edit whose effect is not timed | D3 T13 (measure) · consortium ask T23 |
| **INT-08** — Build and release | Scanning gates disabled estate-wide; Checkmarx gate vacuous without PR scans | Integration (Sun Life) | The supply-chain control is nominal | D3 W3 |
| **CAP-14** — Lifecycle governance | Governance rulesets are deployed but inert — zero applicability rules, so every server sits at `not_evaluated` | Integration (Sun Life) | The governance axis exists and decides nothing | `governance-intake` (EACPP-877) |
| — | No MCP-server health probing anywhere in the platform | Component change (consortium) | A dead backend is discovered by a failing call | Consortium ask · D3 T24 |

**Interim measures**

| Gap | Interim measure | Removed when |
|---|---|---|
| Tool-granular authorization | MSR-15 one server per trust boundary; MSR-16 server-side tool authorization where it cannot be met | A tool target type is enforced at runtime |
| Tool discovery | MSR-6 makes catalogue accuracy a release-time obligation, verified by diffing against live `tools/list` | Discovery merges and runs on a schedule |
| Third-party-fronted servers | Not onboarded. No workaround — `gateway_identity` sends no credential at all | `injected_credential` or `external_exchange` lands |
| Health probing | Hosting-platform probes plus alerting on gateway 5xx per endpoint | The platform probes registered backends |
| Vacuous Checkmarx gate | MSR-20 requires evidence of a completed scan, not a green stage | The gate fails closed on a missing scan |

## Traceability

| Requirement | Capability | D0 Success Criteria |
|---|---|---|
| MSR-1 … MSR-4 | CAP-08 | SC-1, SC-2 |
| MSR-5 … MSR-8 | CAP-03, CAP-04 | SC-6 |
| MSR-9 … MSR-14 | CAP-06, CAP-24, INT-03 | SC-3 |
| MSR-15 … MSR-18 | CAP-07, CAP-09, CAP-10 | SC-4 |
| MSR-19 … MSR-23 | INT-08 | SC-5 |
| MSR-24 … MSR-26 | INT-02, INT-03 | SC-2 |
| MSR-27 … MSR-30 | CAP-13, CAP-14, CAP-18, CAP-20 | SC-6, SC-7 |
| FR-1, FR-6, FR-7 | — | SC-1, SC-2 |
| FR-2, FR-3 | CAP-04 | SC-3 |
| FR-4, FR-5 | CAP-03, CAP-07 | SC-4, SC-7 |
| FR-8, FR-9 | CAP-08, CAP-24 | SC-1 |
| FR-10 | CAP-11 | SC-7 |
