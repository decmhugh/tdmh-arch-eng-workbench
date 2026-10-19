# ACP / Luminate Integration Patterns — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Owner**: Sun Life ACP Product Team
> **Scope**: The catalogue of supported patterns for integrating an existing application with
> ACP / Luminate — how it authenticates, how it reaches models, MCP tools and other agents, and
> where model inference actually executes.

## Problem Statement

Seven use cases are specced for onboarding — `gbd`, `mdx`, `aims`, `orcc`, `waldo`, `nova`,
`ai-ready-data` — and each one is currently rediscovering the same integration decisions from
scratch. There is no document that says *these are the patterns; pick one*.

- **No pattern catalogue exists.** A team asking "how do I call a governed model from my app?" is
  answered by a conversation, not a page. The answer differs depending on who they ask.
- **The credential story is genuinely non-obvious.** A Luminate credential belongs to a
  `(resource, gateway)` pair, not to a user and not to a catalogue entry. The secret is shown
  once. Until the resource is deployed to a gateway there is nothing to issue. This is the single
  most common blocker, and it is documented in one guide that teams do not find first.
- **Registration and invocation have different answers today.** The gateway data path works with
  a machine credential; the *catalogue* path does not, because machine-to-machine auth on the
  registry is default-off. So teams register in the portal UI and invoke from code — and nothing
  tells them that up front.
- **The gateway accepts four credential shapes** — `X-API-Key`, `Bearer lum_…`, `Bearer lud_at_…`
  and a plain OIDC JWT — with different validation and different eligibility per endpoint. An MCP
  delegated endpoint rejects an API key with a 403 that looks identical to a policy denial.
- **Model inference has two billing patterns and teams conflate them with hosting.** Either the
  gateway assumes a role in the **consumer's** AWS account, so AWS bills the consumer directly; or
  Bedrock is enabled in the **ACP workload account**, so ACP fronts the spend and needs a chargeback
  model. In both the gateway makes the call — what differs is whose account is invoked. Where the
  workload *runs* is a separate question.
- **Teams without an AWS workload account have no documented path.** A Strands agent on OpenShift
  is a real and increasingly common shape. Only the centralized pattern serves it — there is no
  consumer account to assume into — which is exactly why chargeback gates it.

## Opportunity

- **One page per pattern, chosen by a decision tree.** A team identifies its shape in a minute
  instead of a meeting.
- **The onboarding specs stop re-deriving.** `gbd`, `mdx`, `aims`, `orcc`, `waldo` and
  `ai-ready-data` reference a pattern rather than inventing one, and their D1s get shorter.
- **The non-AWS path becomes real.** Documenting the centralized inference pattern gives
  OpenShift/Kubernetes workloads — Strands agents in particular — a supported route to Bedrock
  without an AWS workload account.
- **Chargeback gets a stated position.** The pricing catalogue and per-entity attribution already
  exist; the ledger does not. Saying so plainly is better than teams assuming showback works.
- **The harness SDK earns its keep.** `ACP_TARGET=luminate` already re-points the same client at
  Luminate. A pattern catalogue that leads with the SDK makes the call sites portable between
  the internal build and Luminate, and between environments.

## Scope

### In Scope

| # | Capability | Description |
|---|---|---|
| 1 | **Pattern catalogue** | The supported integration shapes, with a decision tree for choosing |
| 2 | **Identity & credentials** | Credential types, the Keycloak/portal flows, token exchange, TTL, caching, storage |
| 3 | **Gateway invocation** | The `/llm`, `/mcp`, `/a2a` surfaces — paths, headers, authz, failure modes |
| 4 | **MCP patterns** | Registering a server, calling tools, and the delegated / on-behalf-of path |
| 5 | **Model inference patterns** | Consumer-account (gateway assumes into the consumer's account) vs centralized (Bedrock in the ACP account), and the hosting shapes that compose with them |
| 6 | **Cost attribution & chargeback** | What exists (pricing catalogue, per-entity attribution) and what does not (a ledger) |
| 7 | **Adoption paths** | Harness SDK vs raw HTTP; what registration actually requires today |
| 8 | **Gaps and asks** | Where a pattern is blocked, and the consortium ask that unblocks it |

### Out of Scope

- **Environment and gateway topology** — `gateway-environment-strategy`
  (EACPP-1089) owns DEV/SIT/STAGE/PROD and how many gateways exist.
- **Onboarding any specific use case** — each has its own spec; this one gives them patterns.
- **Governance intake and risk classification** — [`governance-intake`](../../governance/governance-intake/d0-discovery.md).
- **Building the SDK** — [`acp-harness-sdk`](../acp-harness-sdk/d0-discovery.md) (EACPP-791)
  and [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md) (EACPP-707).
- **Gateway internals** — routing, guardrails and the proxy data path are consortium-owned.
- **Deploying Luminate** — [`sunlife-deployment`](../sunlife-deployment/d0-discovery.md) (EACPP-596).
- **Writing the end-user guides** — the canonical home is
  [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse);
  this spec decides *what* patterns exist, the guides explain *how* to use them.

## Stakeholders

| Stakeholder | Role | Key concern |
|---|---|---|
| Business teams onboarding | Consumers | A pattern that matches their shape, without a meeting |
| Sun Life ACP Product Team | Owner | One catalogue, referenced by every onboarding spec |
| Teams without an AWS account | Consumers | A supported route to Bedrock from OpenShift/Kubernetes |
| AI Enablement | Consumers | Bedrock access model, consumer-account vs centralized |
| Security / IAM | Governance | Credential handling, role chaining, token TTL and storage |
| FinOps / cost owners | Consumers | Attribution and chargeback per team and model |
| Governance-by-Design | Governance | Every pattern passes through the governed gateway |
| Consortium Engineering | Upstream | Gaps raised, not forked |

## Success Criteria

- ✅ **A team can pick its pattern from a diagram** without asking the platform team.
- ✅ **Each pattern states its credential shape, invocation path and failure modes.**
- ✅ **The three inference patterns are distinguished**, with the IAM and cost consequence of each.
- ✅ **A workload with no AWS account has a documented route** to a governed model.
- ✅ **The chargeback position is explicit** — what exists, what does not, what would be needed.
- ✅ **The onboarding specs reference this catalogue** instead of re-deriving.
- ✅ **Every gap is a named consortium ask**, not a local workaround.

## Dependencies

| Dependency | Owner | Type | Risk |
|---|---|---|---|
| Luminate dev reachable for verification | [`sunlife-deployment`](../sunlife-deployment/d0-discovery.md) (EACPP-596) | Hard | Low — dev is live |
| Harness SDK Luminate target | [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md) (EACPP-707) | Medium | Med — SDK-led patterns depend on it |
| `SERVICE_PRINCIPAL_AUTH_ENABLED` for registry M2M | Consortium (AIC-434 / AIC-493) | Medium | **Med — default-off, so registration is portal-UI today** |
| Gateway/environment topology | `gateway-environment-strategy` (EACPP-1089) | Soft | Low — patterns are topology-agnostic |
| `luminate-user-guides` as the docs home | ACP Product Team | Soft | Low |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The catalogue documents aspiration rather than what works | High | High | Every pattern is marked **works today / partial / blocked**, with the evidence |
| Patterns drift as Luminate changes | High | Medium | The spec names the pattern; the mechanics live in `luminate-user-guides`, regenerated against a running instance |
| Teams pick the centralized inference pattern expecting chargeback | Medium | High | State plainly that pricing and attribution exist and a billing ledger does not |
| Cross-account role chaining is copied without its guardrails | Medium | High | Document the trust direction and that no OIDC provider is needed in the spoke |
| Registration confusion persists | High | Medium | Lead with the portal-UI reality and the credential ordering (deploy first, then credential) |
| The SDK is presented as mandatory | Medium | Low | Every pattern also documents the raw HTTP shape |

## Open Questions

- [ ] Is the **centralized inference pattern** pursued at all? It needs both a chargeback model and
      an **SCP exception** — the ACP hub account is denied `bedrock:*` today.
- [ ] When is the **first real consumer** onboarded onto its own spoke? The Service Catalog product
      is published and verified, but all three environments still point at one test consumer
      account.
- [ ] Does chargeback need a **billing ledger**, or is showback from spans and the pricing
      catalogue sufficient for the first year?
- [ ] Which pattern is the **default recommendation** for a new team with no constraints?
- [ ] Do we support **raw HTTP** integration as a first-class pattern, or steer everyone to the SDK?
- [ ] When `SERVICE_PRINCIPAL_AUTH_ENABLED` lands, does registration move to code, or stay in the
      portal for governance reasons?
- [ ] For AgentCore workloads, is the MCP path **SigV4 direct to the runtime ARN** or **through the
      gateway**? Both work; only one should be recommended.

## References

**Code** — `Code/Luminate/luminate`
- `gateway/app/middleware/authn.py`, `authz.py`, `proxy.py` · `gateway/app/providers/jwt_validator.py`,
  `portal_grpc.py` · `backend/app/iam/views.py` · `backend/app/metrics/models.py` ·
  `backend/app/model_pricing_catalog/models.py`

**Deployment** — [`luminate-sunlife-deploy`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-sunlife-deploy/browse)
- `helm/luminate-portal/templates/gateway/aws-config-configmap.yaml`, `gateway/deployment.yaml`,
  `values/values-<env>.yaml`

**SDK & samples**
- [`acp-harness-sdk`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-harness-sdk/browse) v0.11.0 ·
  [user guide](https://bitbucket-static.sunlifecorp.com/pages/EDAEACP/acp-harness-sdk/bb-pages/browse/)
- [`acp-agentcore-sample`](https://bitbucket.sunlifecorp.com/projects/T1KACP/repos/acp-agentcore-sample/browse)

**User documentation**
- [`luminate-user-guides`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/luminate-user-guides/browse) —
  `docs/building/using-credentials.md`, `harness-sdk.md`, `register-*.md`, `docs/administration/credentials.md`

**Related specs**
- `gateway-environment-strategy` (EACPP-1089) ·
  [`acp-harness-sdk`](../acp-harness-sdk/d0-discovery.md) (EACPP-791) ·
  [`aws-harness-integration`](../../integration/aws-harness-integration/d0-discovery.md) (EACPP-707)
