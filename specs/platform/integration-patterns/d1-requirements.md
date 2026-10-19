# ACP / Luminate Integration Patterns — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD

## Maturity labels

Every pattern in [D2](d2-design.md) carries one. The labels are the point of the document — a
catalogue that does not distinguish working from aspirational is worse than no catalogue.

| Label | Meaning |
|---|---|
| **Works today** | Verified against a running Luminate deployment |
| **Partial** | Works with a documented caveat or manual step |
| **Blocked** | Designed or desired, with a named blocker and consortium ask |

## Functional Requirements

### Catalogue

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Publish a **pattern catalogue** with a decision tree that routes a team to its pattern from the shape of its application — where it runs, whether it has an AWS account, what it needs to call. | Must |
| FR-2 | Each pattern states: **credential shape, invocation path, what governs it, failure modes, and maturity label**. | Must |
| FR-3 | Every pattern is documented in **both** the harness SDK form and the **raw HTTP** form, so the SDK is a convenience and not a dependency. | Must |
| FR-4 | The catalogue is **referenced by the onboarding specs** rather than duplicated into them. | Must |

### Identity and credentials

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5 | Document the **four credential shapes** the gateway accepts — `X-API-Key`, `Bearer lum_…`, `Bearer lud_at_…`, OIDC JWT — with what each is validated against and which endpoints accept it. | Must |
| FR-6 | Document the **client-credentials exchange**: `POST {portal}/api/v1/iam/auth/token`, its inputs, `expires_in`, and that the endpoint is **rate-limited** so per-request fetching fails under load. | Must |
| FR-7 | State the **credential ordering rule** plainly: a credential belongs to a `(resource, gateway)` pair, so the resource must be **deployed before a credential exists**. This is the most common blocker. | Must |
| FR-8 | Document **secret storage** options by runtime — Secrets Manager, Vault→Kubernetes, OpenShift secret, env var for dev only — and that the secret is **shown once**. | Must |
| FR-9 | Document the **delegated / on-behalf-of** path for MCP: what mints it, which identities are eligible, and why an API key is refused with 403. | Should |

### Invocation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10 | Document the **three gateway surfaces** — `/llm`, `/mcp`, `/a2a` — with exact path shape and the OpenAI-compatible request/response for `/llm`. | Must |
| FR-11 | Document the **authorization call** the gateway makes per request, what it carries, and that a **portal outage denies** rather than fails open. | Must |
| FR-12 | Map **failure modes to causes** — 401 by validator reason, 403 by policy vs endpoint-eligibility — so an operator can tell a bad token from a denied policy. | Must |
| FR-13 | Document **streaming** where supported, and its reconnect/token-refresh behaviour. | Should |

### Model inference

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-14 | Document the **consumer-account pattern** — the gateway assumes a role in the **consumer's** AWS account, provisioned there by the published [`acp-aws-service-catalog`](https://bitbucket.sunlifecorp.com/projects/T1KACP/repos/acp-aws-service-catalog/browse) product, so the Bedrock call executes in the consumer's account and **AWS bills the consumer directly**. No chargeback machinery required. | Must |
| FR-15 | Document the **centralized pattern** — Bedrock enabled in the **ACP workload account** where the gateway runs, invoked with the gateway's own pod role. State both blockers: **ACP fronts the spend**, and the **hub account is SCP-denied on `bedrock:*`**, so enabling it is an organisation-level change rather than configuration. | Must |
| FR-16 | Document the **hosting shapes** — team AWS account, Bedrock AgentCore runtime, OpenShift/Kubernetes — as a **separate axis** that composes with either billing pattern, and recommend one MCP route for AgentCore. | Must |
| FR-17 | State, per pattern, **whose account is invoked**, **who AWS bills**, and **what is attributable**. | Must |
| FR-18 | Give teams **without an AWS workload account** — Strands agents on OpenShift/Kubernetes being the motivating case — a named, supported pattern. Only centralized serves them, because there is no consumer account to assume into. | Must |
| FR-19 | Document the **role-chain mechanics** for the consumer-account pattern: web identity → hub role → consumer spoke role, gated by an **ExternalId**, with **no OIDC provider required in the consumer account** and **no app-side assume-role**. Note that chaining exists for a second reason beyond billing — SCPs are evaluated in the spoke, where Bedrock is permitted. | Must |

### Cost and attribution

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-20 | State what exists for cost: a **pricing catalogue** with per-token USD costs and **per-entity attribution**, and that token counts ride on spans. | Must |
| FR-21 | State plainly that there is **no aggregated billing ledger** and **no `spend` quota dimension**, so chargeback is showback-by-query today. | Must |
| FR-22 | Describe what **chargeback would require**, as a consortium ask rather than a local build. | Should |

### Documentation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-23 | The **mechanics** live in [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse); this spec owns *which patterns exist*, the guides own *how to use them*. No duplication. | Must |
| FR-24 | Prefer **diagrams to prose**. A pattern that cannot be drawn is probably two patterns. | Should |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **Evidence-based.** Every "works today" claim is verified against running code or a live deployment, and says which. | Must |
| NFR-2 | **No fork.** Gaps become consortium asks; workarounds must be configuration only. | Must |
| NFR-3 | **Portable call sites.** A pattern should survive an environment change as configuration, not code — the property `ACP_TARGET` already provides. | Must |
| NFR-4 | **Least credential.** A pattern must not require a workload to hold a broader credential than its function needs; prefer gateway-held provider credentials over distributing them. | Must |
| NFR-5 | **Legible failure.** Every documented failure names its cause. | Must |
| NFR-6 | **Maintained where regenerated.** Screenshots and step-by-step belong in the guides, which are asserted against a running instance; this spec carries only structure. | Should |

## Constraints and Assumptions

**Constraints — verified, not assumed:**

- The gateway **denies when the portal is unreachable**. There is no local policy cache, so
  availability of the control plane is on the request path.
- The JWT path requires a **non-empty `scp` / `scope` / `roles` claim** in addition to signature,
  issuer, audience and expiry — an app-only token without one is refused.
- **Registry machine-to-machine auth is default-off** (`SERVICE_PRINCIPAL_AUTH_ENABLED`), so
  `RegistryClient` calls return 401 while the gateway path works normally. Registration is the
  portal UI today.
- **Credentials are `(resource, gateway)` pairs**, issued only after deployment, secret shown once.
- The **token endpoint is rate-limited**; a token must be cached and reused.
- `Quota.dimension` is `requests` or `tokens` only — **no `spend`**.
- **Deploying and issuing credentials are platform-admin actions**; no role can delegate them today.

**Assumptions:**

- Luminate remains the go-forward runtime and the internal build is not extended.
- The harness SDK's Luminate target (EACPP-707) continues, keeping call sites portable.
- The consortium takes Sun Life gaps as upstream contributions.

## Out of Scope

Restated: environment/gateway topology (`gateway-environment-strategy`),
onboarding individual use cases, governance intake, building the SDK, deploying Luminate, and
authoring the end-user guides.

## Open Questions

Carried from [D0](d0-discovery.md#open-questions); the load-bearing ones:

- [ ] Is the centralized inference pattern **offered** to teams without AWS accounts? *(FR-18)*
- [ ] Is showback sufficient, or is a billing ledger required? *(FR-20, FR-21)*
- [ ] What is the **default** recommended pattern for an unconstrained new team? *(FR-1)*
- [ ] For AgentCore, is MCP **SigV4-direct or gateway-routed**? *(FR-16)*
