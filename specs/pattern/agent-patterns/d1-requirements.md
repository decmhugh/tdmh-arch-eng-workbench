# Agent Patterns — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD
> **Epic**: [EACPP-1290](https://sunlife.atlassian.net/browse/EACPP-1290) · Board label `acp-product-team`

Two requirement sets, deliberately separated.

- **ASR-*n*** — the **Agent Conformance Profile**. What an *agent* must satisfy before the
  platform will serve it. This is the set an ISRA is written against and the set a team is
  assessed on. It is numbered `ASR-` so it can be cited alongside `mcp-server-patterns`'
  `MSR-` profile without collision.
- **FR-*n*** / **NFR-*n*** — what **ACP / Luminate and the Sun Life build platform** must provide
  so that conformance is achievable and verifiable.

Every ASR carries a **direction** (egress, ingress or both), an owner, an enforcement point and a
verification method. A requirement that cannot be evidenced is not a requirement.

## User Stories

### US-1: Know what is required, in each direction, before building

**As a** team about to build an agent,
**I want** one page stating what my agent must satisfy as a caller and, separately, as a callee,
**So that** I do not discover after the code is written that my agent is registered but not
reachable.

**Acceptance Criteria**:

- [ ] **Given** I only intend my agent to call models and tools, **When** I read the decision
      tree, **Then** it tells me I need no A2A endpoint and what that means for anyone who later
      wants to call me.
- [ ] **Given** I intend my agent to be invoked by another agent, **When** I read the ingress
      requirements, **Then** I know I need an `AgentDeployment`, an endpoint name, a reachable
      backend and a token my agent must validate.
- [ ] **Given** I have chosen a hosting substrate, **When** I read its annex, **Then** I can list
      every requirement that applies to me and how each will be verified.

### US-2: Register an agent that is actually reachable

**As a** platform administrator,
**I want** registration to state what makes an agent callable and to fail loudly when it does not,
**So that** a grant is never issued against an endpoint that does not exist.

**Acceptance Criteria**:

- [ ] **Given** an agent with no `AgentDeployment`, **When** somebody creates an
      `AccessPolicy(target_type=agent)` against it, **Then** the mismatch is surfaced rather than
      accepted silently. *(Today `claims-intake → claims-adjudicator` is exactly this.)*
- [ ] **Given** I register a `backend_endpoint`, **When** I save, **Then** a reachability test is
      run and its result is recorded, because nothing in the platform checks the URL.
- [ ] **Given** I register an AgentCore runtime, **When** I paste the console URL, **Then** the
      guidance tells me the ARN must be percent-encoded and the query string will be discarded.

### US-3: Stop an agent, and know what "stopped" means

**As a** platform operator handling an incident,
**I want** the stop path to be stated with its real reach,
**So that** I do not believe an agent is contained when it is still calling models.

**Acceptance Criteria**:

- [ ] **Given** I set an agent inactive, **When** I read the runbook, **Then** it tells me this
      denies calls **to** the agent and does not deny calls **from** it, and what to do instead.
- [ ] **Given** I need to stop egress, **When** I follow the runbook, **Then** I revoke the
      agent's credentials and revoke or suspend its source access policies, and the runbook says
      which takes effect first.
- [ ] **Given** an incident review, **When** I am asked how long containment took, **Then** the
      answer is a measured propagation interval for that environment, not a design claim.

### US-4: Assess an agent once, reuse the evidence

**As an** ISRA reviewer,
**I want** a control table with a verification method per control,
**So that** I can assess an agent without reading the gateway source or the Rego.

**Acceptance Criteria**:

- [ ] **Given** a registered agent, **When** I work the control table, **Then** every row has an
      owner, an enforcement point and evidence I can retrieve.
- [ ] **Given** a control that does not exist, **When** I read the table, **Then** it is named as
      a residual risk rather than presented as a control. *(`governance_state` is the one that
      matters here.)*
- [ ] **Given** a second agent on the same substrate, **When** I assess it, **Then** the
      substrate-level controls are already evidenced and only the agent-specific rows are new.

### US-5: Delegate to another agent and keep the caller's identity

**As an** architect designing a multi-agent flow,
**I want** to know what identity reaches the callee and what it can do with it,
**So that** an on-behalf-of chain is a design decision rather than an accident of configuration.

**Acceptance Criteria**:

- [ ] **Given** an A2A call, **When** I read the identity page, **Then** it states that the
      gateway swaps the caller's token for one audienced to the callee's **deployment**, and what
      the callee must validate.
- [ ] **Given** a gateway that cannot run the exchange, **When** I call, **Then** the endpoint is
      withheld and refused with a reason, not served as the gateway.
- [ ] **Given** I need the downstream cost to follow the original caller, **When** I read the
      operations page, **Then** it tells me the callee must forward the delegated token rather
      than use its own credential.

## The Agent Conformance Profile

**Class**: **M** = mandatory · **C** = conditional, with the condition stated · **R** =
recommended.
**Dir**: **E** = applies to the agent as a caller · **I** = applies to the agent as a callee ·
**E+I** = both.

### A. Direction and addressability

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-1** | M | E+I | The agent **declares which directions it operates in** — egress only, ingress only, or both — and the declaration is recorded at registration. Egress needs a credential and source policies; ingress additionally needs an `AgentDeployment`. Registering for egress does **not** make an agent callable. | Registration record (`description` / `metadata` until the product carries a field) | The declaration, reconciled against the agent's `AgentDeployment` rows |
| **ASR-2** | C | I | An ingress agent is a **remote HTTP service speaking A2A JSON-RPC 2.0** (`message/send` and the task lifecycle) at a stable absolute URL. A library, a queue consumer or a process invoked by SDK are not ingress-capable. | `AgentDeployment.backend_endpoint`; agentgateway `A2aPolicy` route | A `message/send` through `{gateway}/a2a/{endpoint_name}` returns a JSON-RPC envelope |
| **ASR-3** | C | I | The Luminate **endpoint name is a single URL-safe path segment** — no `/`, no blank. The authn gate reads it back as `upstream_path.split("/")[0]` while the route matches it as a prefix, so a name carrying `/` is gated under one name and served under another, and a blank one matches `/` and shadows every other agent on the lane. | `translate_agent_assignment` raises `ValueError`; `validate_key` on the field | Registration rejects a malformed value; the assignment is skipped with a logged reason if it slips through |
| **ASR-4** | C | I | The agent **tolerates being fronted**. Its route is matched on `/{endpoint_name}` and the path is rewritten to the component of `backend_endpoint` after the host, so the agent must not depend on its own hostname, must not emit absolute self-referential URLs, and must accept the rewritten path. | agentgateway `urlRewrite` + `pathPrefix` | Functional test through the gateway, not against the backend directly |
| **ASR-5** | M | I | The backend is **not reachable except from the serving gateway**. This is load-bearing: the gateway is where authentication, authorization, guardrails and audit happen, and a second path defeats all four at once. | NetworkPolicy, security group, private endpoint, resource policy or equivalent | Negative test from a non-gateway workload |
| **ASR-6** | M | I | The registered `backend_endpoint` carries **scheme, host and the complete path**, percent-encoded where a path segment contains reserved characters. **Any query string is silently discarded** — `_split_api_base` returns `parsed.path` only. An AgentCore ARN must be percent-encoded (`arn%3Aaws%3A…runtime%2F…`); a raw ARN splits across path segments. | `_split_api_base`; the emitted `urlRewrite.path.full` | Read the rewritten path back from the gateway's `/config_dump` and compare it to the intended URL |
| **ASR-7** | M | I | **Reachability is proven after registration, not assumed.** Nothing in the platform probes an agent backend: `MCPServerDeployment` carries `health_status`, `last_checked_at` and `last_error`; **`AgentDeployment` carries only `endpoint_name` and `backend_endpoint`**. Registration accepts any well-formed URL. | Onboarding process | A recorded successful call through `{gateway}/a2a/{endpoint_name}` |

### B. Catalogue and lifecycle

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-8** | M | E+I | `type`, `framework` and `deployment_type` are drawn from a **controlled vocabulary**, published in the guidance. All three are free-text `CharField`s; the live estate carries `bedrock-agentcore`, `langgraph`, `strands`, `Strands Framewrok`, `Other`, a stale package name and a blank, which makes "how many agents run on AgentCore" an eyeball question. | Registration process (the platform does not constrain them) | `GET /api/v1/catalog/agents` grouped by `framework` — every value in the vocabulary |
| **ASR-9** | M | E+I | Each environment is served by a **distinct backing runtime**, or the sharing is a recorded exception with a stated blast radius. Prod today registers one AgentCore runtime under four gateways spanning dev, SIT, stage and prod. | Deployment records | The distinct `backend_endpoint` values across an agent's deployments |
| **ASR-10** | M | E+I | `governance_state` moves **only through the guarded transition action** (`POST …/transition`), never a direct write, and every move carries a reason. The state is **recorded, not enforced** — it has no runtime consumer — so it must not be presented as an operating control. | `GovernanceTransitionMixin`; direct writes refused with `GovernanceTransitionRequiredError` | The state, its reason and the audit entry; a refused direct write |
| **ASR-11** | M | I | **No grant without an endpoint.** An `AccessPolicy(target_type=agent)` is created only against an agent that has an `AgentDeployment` on the gateway the policy applies to. | Onboarding process; FR-3 makes it queryable | The reconciliation query returns zero mismatches |
| **ASR-12** | M | E+I | The agent **declares its capabilities and its reach** — what it does, which models and MCP servers it needs, and which agents it delegates to — in the catalogue record. Nothing in the platform serves or proxies an A2A agent card (`grep -rin "agent-card\|agent.json\|agentcard"` over `gateway/app` and `backend/app` **returns zero**), and `/.well-known/` is answered locally by the gateway, so the catalogue entry is the only capability inventory an assessor can read. | Catalogue `description` / `metadata`; attributes | The record, diffed against the agent's actual access policies |

### C. Identity and credentials

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-13** | M | I | An agent endpoint is served **only where the on-behalf-of exchange runs**. Every routable agent deployment is a delegated target — there is no identity mode to opt out of — so an endpoint whose `delegated_identity_audience` is empty is reached with the caller's credential passed through unchanged, and the gateway's own reasoning for that (*"LLM and A2A upstreams are the platform's own"*) does not hold for a third-party runtime. A gateway that cannot exchange **withholds** the endpoint. | `_agent_downstream_exchange`; `_withhold_unexchangeable_agents`; `_authenticate_a2a` returns 503 `endpoint_withheld` | The route's `backendAuth.oauthTokenExchange` block in `/config_dump`. **Absent = non-conforming.** |
| **ASR-14** | C | I | A served ingress agent **validates the presented token**: signature against the platform JWKS, expected issuer, expiry, and `aud` equal to **its own deployment audience** (`agent-<agentUUID>-<deploymentUUID>`). The audience is deployment-scoped precisely so a staging token cannot be spent against production. | Agent-side | Present a token minted for another deployment — expect refusal |
| **ASR-15** | C | I | Where the agent is hosted on a substrate with its own inbound authorizer, that authorizer is **configured to accept the platform's bearer**. Luminate emits an OAuth bearer on every hop and **never SigV4**, so an AgentCore runtime needs a custom JWT authorizer trusting the platform issuer and the deployment audience; IAM-only inbound auth cannot be reached through the gateway. | Substrate configuration | The runtime's inbound auth configuration; an end-to-end call |
| **ASR-16** | M | E | The agent's egress credential is **issued on a `Deployment`**, not on the catalogue entry. Registration alone issues nothing; `CREDENTIAL_RESOURCE_TYPES = {agent, application, mcp_server}` and the mint is `POST /api/v1/deployment/deployments/{id}/generate-credentials`. The secret is **show-once** — a lost secret is rotated, never regenerated. | `DeploymentViewSet.generate_credentials` | The `OAuthCredential` row and its `client_secret_prefix` |
| **ASR-17** | C | E | An `lum_` **API key is used only where the target endpoint admits one**. A delegated A2A endpoint refuses it with 403 `api_key_not_exchangeable`, and a `token_forward` MCP endpoint refuses it with 403 `platform_minted_not_forwardable`. Since every routable agent endpoint is delegated, **an agent that delegates to another agent must hold client credentials, not an API key.** | `gateway/app/middleware/authn.py` `_refuse_agent_unexchangeable` | Negative test — expect the named refusal, not a generic 403 |
| **ASR-18** | C | E | An agent acting **on a user's behalf** is registered for delegated access and uses a `lud_at_` token, and its reach is bounded by the delegation ceiling rather than by its own machine grants. | `app/user_oauth`; `access_policies/reach.py` | The grant record; a call outside the ceiling refused |
| **ASR-19** | M | E+I | **Credential material never appears in a prompt, a log, a trace attribute or a tool argument.** An agent composes text that is stored and replayed; a credential in that text is a credential in the audit trail. | Agent-side | Log and trace review |

### D. Authorization and content control

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-20** | M | E | Egress is **least privilege and explicit**: one `AccessPolicy` per target the agent actually needs, constrained by gateway and environment where those differ. There is no implicit access; `_source_matches` requires a policy naming the token subject. | `AccessPolicy(source_type=agent)` | The policy list for the agent, reviewed against ASR-12's declared reach |
| **ASR-21** | M | I | **Everything the agent receives is untrusted** — the inbound A2A message, tool output and model output alike. The agent bounds what an inbound message can cause it to do and does not treat instructions in content as authority. | Agent-side | Design review; a prompt-injection test case |
| **ASR-22** | M | I | Because **no guardrail can be bound to an agent as a callee** — there is no `target_agent` scope and `_TARGET_SCOPED_FLOWS` is `{"model", "mcp_server"}` — an ingress agent that accepts regulated content requires **caller-side guardrails** on every agent granted it, with `agent` in `applies_to_target_types`, and states that requirement in its onboarding record. | `GuardrailAttachment` on each calling agent | The attachment list per caller; a positive detection test. **An ungoverned caller is an unscanned path.** |
| **ASR-23** | M | E | The agent carries a **substrate-side bound** on its own call volume and spend. Quotas are not enforced anywhere — `grep -ril quota gateway/app/` **returns zero files** and the dimension enum stops at requests and tokens — so the bound is the agent's own concurrency limit, its runtime's concurrency ceiling, or a provider-side rate limit. | Agent / substrate | The configured limit; a load test |
| **ASR-24** | C | E+I | Where the agent's privileges differ materially by task — read versus write, or across classification tiers — those are **split into separate agents**, because a grant is per agent and covers everything that agent may do. | Design review | The architecture record; the policy list per agent |

### E. Build and supply chain

Inherited from [`mcp-server-patterns`](../mcp-server-patterns/d1-requirements.md) MSR-19 to
MSR-23 and re-checked against `CSDP/pipeline-libraries`. The substance is identical; an agent is
not exempt because it is "just a client".

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-25** | M | E+I | Built by the **approved Jenkins JTE pipeline** using the Sun Life libraries — `pod_template`, `git`, the language library, `sonarqube`, `snyk`, `checkmarx`, and `quay` or `ecr`. Ad-hoc image builds are not acceptable for a served agent. | `Jenkinsfile` + `pipeline_config.groovy` | The build job and its stage list |
| **ASR-26** | M | E+I | **SAST — Checkmarx.** A Checkmarx project exists, PR scanning is configured, `enforce_checkmarx_gate = true`, and `branches_to_scan` matches the repository's real integration branch (the library default is `["develop"]`). A green stage is **not** evidence: the step reads an existing PR scan and logs `New repository PR does not exist. Checkmarx scan is skipped.` when there is none. | `libraries/checkmarx/steps/code_analysis.groovy` | The scan id and gate evaluation recorded on the build |
| **ASR-27** | M | E+I | **SCA — Snyk.** `run_snyk_scan = true`, `enforce_snyk_gate = true`, `severity_threshold` no weaker than the library default `high`, `snyk-sbom.json` retained. Agent stacks pull large, fast-moving dependency trees; this is where that shows up. | `libraries/snyk` / language-library `sca_scan` | `snyk-results.html`, `snyk-sbom.json` |
| **ASR-28** | M | E+I | **SonarQube runs and its gate is enforced**, and the **image is produced by that pipeline** and pushed to Quay or ECR, referenced by immutable tag or digest — never `latest`. Any disabled gate carries a `disable_gate_reason_*` with an owner and an expiry, recorded as an exception. | `libraries/sonarqube`; `quay` / `ecr` | Project + gate status; registry digest vs deployed digest |

### F. Runtime and secrets

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-29** | C | E+I | On a Sun Life Kubernetes or OpenShift cluster the agent runs **non-root** with `allowPrivilegeEscalation: false`, `capabilities: drop: ["ALL"]`, and **CPU and memory requests *and* limits on every container including init containers**. Gatekeeper denies a pod without them and the denial is invisible in `rollout status` — the deployment reports `generation == observedGeneration` with no updated replicas, and the real error appears only in `kubectl get events`. | Gatekeeper `container-must-have-limits-and-requests` | No admission denial in events; the pod is running |
| **ASR-30** | M | E+I | The agent's **own secrets** — provider keys, database credentials, its Luminate client secret — come from Vault via the Vault Secrets Operator, or AWS Secrets Manager. Never baked into an image, never a literal in a ConfigMap or a manifest, never in the catalogue `configuration` blob. `Agent.audit_snapshot()` deliberately omits `configuration` precisely because it is free-form operator JSON landing in an append-only store that cannot be redacted afterwards. | INT-02 | Manifest review; the secret's source |

### G. Observability, cost and lifecycle

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-31** | C | E | Where the **downstream cost of a delegation must follow the original caller**, the callee **forwards the delegated token** it received rather than calling out on its own machine credential. Per-agent usage is materialised per `SubjectType.AGENT`, so a callee that uses its own credential books the cost to itself and the caller sees nothing. | Agent-side | A trace showing the caller's principal on the callee's downstream call |
| **ASR-32** | M | E+I | The agent has a **stop path that has been exercised**, and its owner knows what it reaches. Setting `Agent.status = inactive` denies calls **to** the agent and does **not** deny calls **from** it — the Rego's source rule matches on the token subject alone and never reads the agent's status, and `verify_api_key` never reads `owner_agent.status`. Stopping egress means **revoking the credential and revoking or suspending the source access policies**. Governance suspension enforces nothing. | `facts.py::_collect_agents`; `authz.rego` `allowed_agents`; credential revocation | A recorded drill: the measured interval from action to first refused call, in each direction, per environment |
| **ASR-33** | R | E+I | The agent **sends `x-luminate-session-id`** so its runs are correlatable. On the model and agent lanes this is the run-correlation unit; absent it, correlation falls back to `traceparent` and, absent that, to nothing. The harness SDK's `x-session-id` is **not** read by Luminate (`grep -ri "x-session-id"` over `gateway/` and `backend/` **returns zero**). | `gateway/app/middleware/authz.py::_raw_session_id` | A trace showing a stable session across the calls of one run |
| **ASR-34** | M | E+I | The agent **declares the data it reaches and its classification**, and **does not log prompts, tool arguments or model output** carrying regulated or personal data. An agent composes and stores text on its own account; what it writes is not covered by the platform's redaction. | Catalogue `metadata` / attributes; agent-side | The declared reach with classifications; a log review |

### H. Resource type and enterprise API access

| ID | Class | Dir | Requirement | Enforcement point | Verification |
|---|:--:|:--:|---|---|---|
| **ASR-35** | M | E+I | The workload is registered as an **Agent** only if something may need to **call** it; otherwise it is an **Application**. A chatbot, batch job, UI backend or internal service is an Application. This is structural, not stylistic: there is no `ApplicationDeployment` and no `application` member on `AccessPolicyTargetType`, so an Application can never be routed to or granted. An Application also has **no `status`**, **no `governance_state`**, and is **deliberately excluded from the governance sweep** (`SWEPT_REGISTRIES` = agent, model, mcp_server), and has no member in the usage ledger's `SubjectType`. | Resource type at registration | The catalogue record and the recorded rationale; the guides state no rule, so the decision must be written down |
| **ASR-36** | M | E | An agent reaches an **enterprise REST API only through an MCP server**, never directly. The gateway matches `/llm/`, `/mcp/` and `/a2a/` and nothing else, and no `target_type` names an API — so a direct call carries no access decision, no guardrail, no audit event and no cost attribution. Per the 2026-09-02 Enterprise Architecture decision, the MCP server then calls the API through the **API Platform gateway** (light4j / Okta light-proxy) unchanged. | `gateway/app/middleware/proxy.py::_resolve_route`; onboarding review | The agent's egress inventory: every business-system call resolves to a registered MCP server |
| **ASR-37** | M | E | The agent **never holds an enterprise API credential**. The upstream credential belongs to the MCP server behind the API Platform. A credential in the agent is a copy of a secret on a path neither gateway can see. | Design review; ASR-30 | Agent configuration and secret sources |
| **ASR-38** | M | E | The **identity the REST API actually receives is recorded** at onboarding. By default it is the **MCP server's own Okta service identity, not the end user** — Okta will not validate a Keycloak-issued token, and Luminate holds no Okta provider and can mint no Okta token (`delegated_exchange_provider()` returns the one deploy-time provider). Carrying the user through requires the MCP server to exchange, which needs **Okta to trust the Luminate issuer** — a federation decision, not a configuration change. | Onboarding record | The recorded answer, and the API's own audit showing which principal it logged |

## Functional Requirements — what the platform must provide

### FR-1: Publish the pattern as a self-service artefact

Published in
[`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse)
as the page a team is pointed at before it builds, with the egress-or-ingress question first and
the substrate annex second.

### FR-2: Record direction and the identity decision at registration

Registration captures whether an agent is egress-only, ingress-only or both, and — for ingress —
the recorded confirmation that the callee validates the deployment audience. Until the product
carries fields, both live in the catalogue `metadata` and the onboarding record.

### FR-3: Make non-conformance queryable

The estate can be queried for each of the following. All are answerable from the existing
catalogue and deployment APIs; none is exposed as a view today.

| Question | Why it matters |
|---|---|
| Agents with an `AccessPolicy(target_type=agent)` but **no** `AgentDeployment` | An active grant against a route that does not exist — one such policy is live in dev |
| Agent deployments whose emitted `delegated_identity_audience` is **empty** | Served with the caller's credential passed through, or with none — all four in prod |
| Agent deployments whose `backend_endpoint` is `http://` | Plain text on the gateway→agent hop |
| Agents at `governance_state = not_evaluated` | 10 of 10 in dev |
| Agents whose `framework` is outside the vocabulary | The inventory question |
| Agents with an active credential and **no** source access policy, or the reverse | A credential with no reach, or a grant with no holder |

```text
GET /api/v1/catalog/agents
  → id, key, name, status, governance_state, type, framework, deployment_count
GET /api/v1/deployment/deployments?resource_type=agent
  → id, gateway, environment, endpoint_name, backend_endpoint
```

### FR-4: State the direction distinction in the product surface

The portal's agent screen distinguishes "this agent may call X" from "X may call this agent", and
the deployment form states that an `AgentDeployment` is what makes the agent reachable.

### FR-5: Correct CAP-01, CAP-10, CAP-11 and CAP-14 in the capability map

- **CAP-01** — registration produces a governed caller; reachability requires a deployment.
- **CAP-08** — upgraded: the A2A lane is live, with per-deployment routes, TLS and RFC 9728.
- **CAP-10** — guardrails are caller-scoped for agents; there is no target-agent binding.
- **CAP-11** — downgraded: deactivation is asymmetric, and governance suspension enforces nothing.
- **CAP-14** — the governance axis for agents is ⚠️ modelled, not enforced.

### FR-6: Provide a reference implementation

A reference agent — an A2A JSON-RPC service, a `Dockerfile`, a `Jenkinsfile`, a
`pipeline_config.groovy` with the gates on, a deployment manifest satisfying ASR-29 and ASR-30,
and token validation satisfying ASR-14 — so conformance is the starting point rather than an
audit finding.

### FR-7: Publish the substrate annex

One page per substrate — OpenShift, EKS, Bedrock AgentCore, Lambda — stating reachability, TLS,
network control, egress path and build path — plus the **SUB-E / SUB-I admission criteria** any
other platform is assessed against, with worked assessments as examples rather than a closed list.

### FR-8: Publish the failure-mode table for the agent lane

The refusals a caller can receive, by cause, so a 403 is diagnosable: policy denial;
`api_key_not_exchangeable`; `not_exchangeable` (a plain user token with no actor);
`endpoint_withheld` (503 — the gateway cannot run the exchange); portal-unreachable fail-closed;
and the case that produces no refusal at all — a grant against an agent with no route, which
fails at the proxy hop.

### FR-9: Fix the harness SDK's A2A path

Four defects, each with a test (D3 T19):

1. `A2AClient.invoke_gateway` attaches no `Authorization` header — resolve and attach the
   provider, as `GatewayClient` does.
2. Against a delegated endpoint the SDK's preferred gateway credential (a `lum_` API key) is
   refused; the A2A path must select client credentials.
3. The method addresses `{a2a_gateway_url}/a2a/{target_agent_id}` while Luminate routes by
   **endpoint name**, and the default `a2a_gateway_url` already ends in `/a2a`, composing
   `…/a2a/a2a/{id}`.

Additionally, emit `x-luminate-session-id` so run correlation works — `x-session-id` is not read.

### FR-10: Measure the stop-path propagation

The interval between each stop action — deactivation, credential revocation, policy revocation,
governance suspension — and the first refused call, measured per environment and published.
Configuration reaches gateways by a long-lived push stream rather than polling, but the number
must be measured, never quoted. The measurement must cover **both directions**, because they do
not behave the same way.

### FR-11: Reconcile the environments before any A2A grant is made in prod

Prod runs a build predating the on-behalf-of exchange, and serves A2A routes with no
`backendAuth`. The image is uplifted, or `target_type = agent` policies remain at zero, before the
lane is used.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| **NFR-1** | Availability | The control plane is on the request path — every call makes a `CheckAccess` RPC with no local cache, and a portal outage denies rather than fails open | Design around it; state it in the ISRA |
| **NFR-2** | Latency | Gateway overhead per lane — authn, authz RPC, token exchange on A2A, guardrails, forward. The A2A exchange adds a token round trip the LLM lane does not have | Measured and published per environment |
| **NFR-3** | Security | No agent backend reachable from outside its serving gateway | 100%, verified by negative test |
| **NFR-4** | Security | No agent endpoint served without a credential reaching it, where the backend is not the platform's own | 100% of ingress agents |
| **NFR-5** | Observability | Every served request attributable to caller, target and lane | 100% of requests through the gateway |
| **NFR-6** | Auditability | Every control-plane mutation of an agent record and every data-plane decision recorded in the append-only trail | 100% |
| **NFR-7** | Supply chain | Every served agent image traceable to a pipeline build with SAST, SCA and SonarQube evidence | 100% of agents |
| **NFR-8** | Recoverability | Egress and ingress can each be stopped, and the interval measured | Both paths documented; target under 60s once the action is taken |
| **NFR-9** | Cost | Every agent's model and tool spend attributable to the agent | 100%; delegated chains per ASR-31 |

## Data Model Requirements

The platform-side model exists; this records it so the profile can reference it.

| Entity | Key fields | Relationships |
|---|---|---|
| `Agent` | `key`, `name`, `description`, `status`, `governance_state` (+ `_reason`), `type`, `framework`, `deployment_type`, `configuration`, `scope_tokens` | belongs to `Project`; has many `Deployment`. **No `identity_mode`** — unlike `MCPServer` |
| `Deployment` | `resource_type = "agent"`, `deployment_key`, `gateway`, `environment`, `location`, `project` | one per (gateway, `deployment_key`, agent); carries the credential |
| `AgentDeployment` | `endpoint_name`, `backend_endpoint` | one-to-one with `Deployment`; **its presence is what makes the agent callable** |
| `OAuthCredential` | `client_id`, `client_secret_prefix`, `status`, `rotated_at`, `revoked_at` | FK `agent` / `application` / `mcp_server` / `gateway` |
| `APIKey` | `key_hash`, `status`, `expires_at`, `owner_agent` | owner may be user, application, agent or MCP server |
| `AccessPolicy` | `source_type`/`source_agent`, `target_type`/`target_agent`, `status`, constraints | both `AccessPolicySourceType` and `AccessPolicyTargetType` carry `agent` |
| `GuardrailAttachment` | scope FK (exactly one of org/project/api_key/**agent**/mcp_server/application, or `target_model`/`target_mcp_server`), `applies_to_target_types`, `applies_to_directions`, `mode`, `action` | **no `target_agent`** |
| `AgentAssignment` *(wire)* | `endpoint_name`, `backend_endpoint`, `delegated_identity_audience`, `agent_id`, `environment_id` | **no `backend_auth`** — a non-empty audience is the only signal |
| `UsageBucket` | counters keyed by `SubjectType` ∈ {org, agent, model, mcp_server} | the per-agent cost ledger |

## Edge Cases

| Scenario | Expected behaviour |
|---|---|
| Agent registered with no `AgentDeployment` | Registration succeeds. The agent is a governed caller and is **not callable**. Nothing surfaces this. |
| `AccessPolicy(target_type=agent)` against an agent with no deployment | The policy is accepted and active. The call authorizes and then **fails at the proxy hop**, because no route was ever emitted. Live in dev today. |
| `AgentDeployment` with an empty `backend_endpoint` | No audience is minted and no route is translated — the assignment is skipped with a logged reason. The agent is not served. |
| Agent deployment whose gateway cannot run the exchange | The endpoint is **withheld**: `_withhold_unexchangeable_agents` records it, `_authenticate_a2a` returns **503 `endpoint_withheld`**, and RFC 9728 discovery 404s for it. Serving it would reach the agent as the gateway. |
| Delegated agent endpoint reached with a `lum_` API key | 403 `api_key_not_exchangeable`. This is what the harness SDK's default configuration produces. |
| Delegated agent endpoint reached with a plain user token (no actor) | 403 `not_exchangeable` — the exchange needs a delegated or machine identity |
| Agent endpoint that is **not** delegated | Admits whatever valid credential arrived and forwards it unchanged. Correct where the upstream is the platform's own; wrong where it is a third party's. All four prod routes are in this state. |
| Backend endpoint registered with a query string | The query is **silently discarded** from the rewritten path |
| AgentCore ARN registered un-encoded | The ARN's `/` becomes a path separator and the rewritten path is wrong. Nothing validates it; the failure is an AWS-side 404 at call time |
| Agent set `inactive` | Calls **to** it deny at `CheckAccess`. Calls **from** it are unaffected. Its API keys still authenticate. |
| Agent moved to `governance_state = suspended` | The state is recorded, the cascade is previewed and audited, and **no call is refused** |
| Two agents sharing one endpoint name on one gateway | Not possible — uniqueness is per (gateway, `deployment_key`, agent). The same name on two **gateways** is legitimate and is what makes it one promoted resource |
| Callee agent calls a model using its own credential | The cost books to the callee; the original caller sees nothing |
| Agent backend behind Sun Life corporate ingress, CA absent from the gateway bundle | agentgateway `invalid peer certificate: UnknownIssuer` → surfaces as **500 upstream service error**, naming neither TLS nor the certificate |

## Constraints

- **There is no agent identity mode.** Unlike `MCPServer`, `Agent` has no `identity_mode` field
  and `AgentAssignment` has no `backend_auth`. Every routable agent deployment is a delegated
  target; the only alternative is the degrade path, which sends no credential.
- **No health probing for agents.** `MCPServerDeployment` carries `health_status`,
  `last_checked_at` and `last_error`; `AgentDeployment` carries neither those nor a probe.
  Liveness is entirely the hosting platform's job.
- **No guardrail can target an agent.** Architectural, not configurable — the Rego has no agent
  branch.
- **Quotas are not enforced on any lane.**
- **`governance_state` is inert** until the enforcement epic lands.
- **The kill switch is asymmetric** and cannot be made symmetric locally.
- **Sun Life clusters deny pods without requests and limits** (Gatekeeper), init containers
  included, and the denial does not surface in `rollout status`.
- **No `docker.io` egress from Sun Life cluster pods** — every base image must be mirrored.
- **`us-east-1` has no egress from these clusters** — an AgentCore or Bedrock dependency there is
  unreachable.
- **The token endpoint is rate-limited**, which bounds any per-invocation mint (see S4, Lambda).
- **Regulatory**: OSFI E-23 model and system inventory and change control; OSFI B-13 Principle 15
  (least privilege) and Principle 17 (incident response); Quebec Law 25 and PIPEDA where an agent
  reaches personal information.

## Capability Gaps

| Capability | What is missing | Classification | Impact | Escalation |
|---|---|---|---|---|
| **CAP-11** — Kill switch | The source side of the Rego never reads the agent's status; `verify_api_key` never reads `owner_agent.status`. Deactivation stops ingress only | Component change (consortium) | An operator cannot stop an agent calling by deactivating it | Consortium ask · D3 T25 |
| **CAP-10** — Guardrails | No `target_agent` attachment scope and no agent branch in `authz.rego`, so a callee cannot require a scan of its own inbound traffic | Component change (consortium) | Content control on A2A ingress depends on every caller carrying one | Consortium ask · D3 T31 |
| **CAP-14** — Lifecycle governance | `governance_state` has zero runtime consumers; suspension records without denying | Component change (consortium) + integration (SLF) | The governance axis decides nothing | Consortium ask · D3 T27 · `governance-intake` (EACPP-877) |
| **CAP-01** — Agent registry | No health or reachability probe for an agent backend; no reconciliation between a `target_type=agent` grant and an existing endpoint | Component change (consortium) | A wrong URL and an unroutable grant are both accepted in silence | Consortium ask · D3 T28 |
| **CAP-01** — Agent registry | No agent card, and `/.well-known/` is served locally so a callee's own card cannot be fetched through the gateway | Component change (consortium) | The A2A discovery contract cannot be met; capability inventory is manual | Consortium ask · D3 T29 |
| **CAP-13** — Quotas | Not enforced on any lane; `grep -ril quota gateway/app/` returns zero | Component change (consortium) | An autonomous caller is unbounded by the platform | Consortium ask (already raised by `mcp-server-patterns`) |
| **CAP-08** — Governed AI gateway | No REST/HTTP lane and no API target type, so an enterprise API can only be governed by wrapping it as an MCP server. `API Resources` D1 would change this but is **unmerged and pending**, and would need reconciling with the 2026-09-02 Option-2 decision that the API Platform keeps the REST estate | Component change (consortium) + **SLF architecture decision** | Every REST integration carries an MCP wrapper, or goes ungoverned | Consortium ask + EA decision · D3 T32 |
| **CAP-24** — Delegated access | No cross-IdP exchange. Luminate registers `keycloak`, `authentik` and `entra` — **no Okta provider** — and `delegated_exchange_provider()` returns a single deploy-time provider, so a Keycloak→Okta on-behalf-of hop is not expressible | Component change (consortium) + **Okta trust federation (SLF)** | The end user's identity does not reach the REST estate; the API sees a service identity | D3 T33 |
| **CAP-20** — Observability | The agent lane stamps no GenAI operation name, so an A2A hop is an untyped span and the delegation's downstream cost does not follow the caller by default | Component change (consortium) | Per-delegation cost attribution needs a caller-side convention | Consortium ask · D3 T30 |
| — | `_split_api_base` discards the registered query string on the A2A hop | Component change (consortium) | A non-default AgentCore qualifier silently routes to `DEFAULT` | Consortium ask · D3 T26 |
| **INT-08** — Build and release | Scanning gates disabled estate-wide; the Checkmarx gate passes without a scan | Integration (Sun Life) | The supply-chain control is nominal | D3 T11–T13 · shared with `mcp-server-patterns` |
| — | Harness SDK A2A path sends no credential, prefers a refused credential shape, and addresses the wrong key | Integration (Sun Life) | The stated adoption path cannot reach the lane | D3 T19 |
| — | Prod runs a build predating the A2A exchange | Integration (Sun Life) | A2A in prod is served with no credential | D3 T4 |

**Interim measures**

| Gap | Interim measure | Removed when |
|---|---|---|
| Asymmetric kill switch | ASR-32 makes credential revocation plus policy revocation the documented stop path, drilled and measured | The source rule reads the agent's status |
| No agent-target guardrails | ASR-22 requires caller-side guardrails on every agent granted the endpoint, and the requirement is recorded on the callee's onboarding record | A `target_agent` scope with an agent branch in the Rego |
| Inert governance state | ASR-10 records it as evidence, never as a control. It is a residual risk in the ISRA, not a mitigation | The enforcement epic reads it |
| No reachability probe | ASR-7 makes a post-registration call a release-time obligation; FR-3 makes the mismatch query available | The platform probes agent backends |
| No agent card | ASR-12 makes the catalogue record the capability inventory | Agent-card publication or proxying lands |
| Quotas not enforced | ASR-23 pushes the bound to the substrate | The dimension is enforced at the gateway |
| Query string discarded | ASR-6 states it; the AgentCore annex says to use the default qualifier | The translator preserves the query |
| Prod predates the exchange | FR-11: no `target_type = agent` policy in prod until the image is uplifted | The uplift ships |

## Traceability

| Requirement | Capability | D0 Success Criteria |
|---|---|---|
| ASR-1 … ASR-7 | CAP-01, CAP-04, CAP-08 | SC-1, SC-2, SC-6 |
| ASR-8 … ASR-12 | CAP-01, CAP-14 | SC-2, SC-5, SC-6 |
| ASR-13 … ASR-19 | CAP-06, CAP-24, INT-03 | SC-3, SC-6 |
| ASR-20 … ASR-24 | CAP-07, CAP-09, CAP-10, CAP-13 | SC-1, SC-8 |
| ASR-25 … ASR-28 | INT-08 | SC-3, SC-8 |
| ASR-29 … ASR-30 | INT-02, INT-03 | SC-3 |
| ASR-31 … ASR-34 | CAP-11, CAP-18, CAP-20 | SC-4, SC-8 |
| ASR-35 | CAP-01, CAP-07, CAP-14 | SC-2, SC-5 |
| ASR-36 … ASR-38 | CAP-08, CAP-09, CAP-18, INT-03 | SC-1, SC-6, SC-8 |
| FR-1, FR-6, FR-7 | — | SC-1, SC-3 |
| FR-2, FR-4 | CAP-01, CAP-04 | SC-2 |
| FR-3, FR-5 | CAP-01, CAP-10, CAP-11, CAP-14 | SC-5, SC-6 |
| FR-8 | CAP-08, CAP-24 | SC-1 |
| FR-9 | — | SC-7 |
| FR-10 | CAP-11 | SC-4 |
| FR-11 | CAP-08, CAP-24 | SC-6 |
