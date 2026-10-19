# AWS Harness Integration with Luminate — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Repo**: `EDAEACP/acp-product-specs` (product-team specs)
> **Scope**: what must change in the AWS Harness SDK (`acp-harness-sdk`) and its
> consumers to work against the **Luminate** deployment's APIs and stack.
> **Analysis basis**: `acp-harness-sdk`, `acp-agentcore-sample` (the reference examples,
> which now include the migrated ai-ready-data agent + Sirius Data MCP server), and the
> Luminate stack (`luminate/gateway`,
> `luminate/backend/app`).

## Problem Statement

The AWS Harness SDK today targets the **internal ACP** stack: it registers against the
internal Agent/Model/MCP registry endpoints, and routes model traffic to the internal
AgentGateway using an **`x-acp-agent-id`** attribution header. Sun Life is now standing up
the **Luminate** (consortium) stack in the SLF environment, whose APIs and auth model are
**different**. For AWS-hosted components (AgentCore / EKS agents, the Sirius Data MCP
server, the evaluation service) to run against Luminate, the harness must be updated to
Luminate's contracts.

The three surfaces that must change:

1. **Gateway (model egress).** Luminate's gateway is **OpenAI-compatible** but served under
   a **`/llm`** prefix (`gateway/app/middleware/proxy.py` strips `/llm/v1/chat` → `/v1/chat`)
   and authenticates with a **`Authorization: Bearer <JWT>`** token, **not** the
   `x-acp-agent-id` header (`gateway/app/middleware/authn.py` validates bearer tokens / API
   keys). The gateway performs its own CEL/OPA authz (`gateway/app/routers/authz.py`).
2. **Control plane (registration).** Luminate exposes **DRF catalog viewsets**
   (`/api/v1/catalog/{agents,mcp-servers,models}`, per the partner API answer) with
   Luminate's schema — `key`, `name`, `transport`, **`project` FK**, **`scope_tokens`**,
   **mandatory tags**, `configuration` — not the internal registry's flat schema.
3. **Identity.** Luminate mints a **JWT via the portal client-credentials token endpoint**
   `POST /api/v1/iam/auth/token` (`gateway/app/settings.py` `oauth_token_endpoint`),
   Authentik-backed for internal M2M. The harness's `OktaAuthProvider` must be able to
   obtain a **Luminate/Authentik token** and present it as a Bearer JWT to both the catalog
   APIs and the gateway.

A fourth, simplifying difference: **Luminate deploys its gateway *into* the Bedrock-
consuming account** and invokes Bedrock via its **pod role** (region + source-VPC
constrained). So when targeting Luminate, the harness/component **does not** need the
cross-account assume-role model — it just talks to the Luminate gateway, which owns the
Bedrock call.

## Background & Drivers

- The harness is Sun Life-specific infrastructure → this integration work is **product-team
  spec**, not a consortium contribution.
- The M2M decision (see the M2M Identity decision doc) keeps **Authentik** for internal M2M
  near-term, so the harness's Luminate auth path targets the **portal token endpoint**
  (Authentik-backed), with Okta/Entra as a later provider swap (the gateway is IdP-agnostic
  — issuer/JWKS config).
- Consumers today: the **`acp-agentcore-sample`** reference examples — the agent + MCP + A2A
  examples plus the **migrated ai-ready-data agent** and **Sirius Data MCP server** (moved
  into `acp-agentcore-sample`). Some examples still call **Bedrock directly** and must move
  to the Luminate gateway to be governed.

## Opportunity

A focused set of harness updates lets every AWS-hosted component register in and route
through **Luminate** unchanged at the call sites: point the gateway client at Luminate's
`/llm` OpenAI-compatible endpoint with Bearer-JWT auth, point the registry client at
Luminate's catalog viewsets with the project/scope/tag schema, and obtain the token from
the portal client-credentials endpoint — dropping the cross-account role dependency.

## Scope

### In Scope

- **GatewayClient → Luminate gateway**: `/llm/v1/chat/completions`, **Bearer JWT** auth
  (replace `x-acp-agent-id`), OpenAI-compatible body (already compatible).
- **RegistryClient → Luminate catalog APIs**: endpoint + **schema mapping** (project,
  scope_tokens, mandatory tags), agent + MCP-tool + model registration.
- **Auth provider → Luminate/Authentik token**: obtain JWT from
  `POST /api/v1/iam/auth/token` (client credentials); present as Bearer to catalog + gateway.
- **ACPSettings**: Luminate endpoints (portal base, catalog prefix, gateway `/llm`, token
  endpoint), project/scope defaults.
- **Drop cross-account assume-role** when targeting Luminate (gateway owns Bedrock).
- Migrate the **direct-Bedrock** examples in `acp-agentcore-sample` to the Luminate gateway,
  and update all `acp-agentcore-sample` examples to the Luminate-supporting harness version.

### Out of Scope

- Internal-ACP compatibility cleanup (version pins, wheel vendoring, env-name drift) — not
  relevant to Luminate compatibility.
- The gateway-side cross-account role model — owned by `sunlife-deployment` DD-6 (only
  referenced; for Luminate it is the gateway's concern, not the harness's).
- Changes to Luminate itself (its APIs are the target contract).

## Stakeholders

| Stakeholder | Role | Key Concern |
| - | - | - |
| Sun Life ACP Product Team / AI Enablement | Owner | Harness works against Luminate |
| Platform (Luminate deployment) | Dependency | Gateway `/llm`, catalog APIs, portal token |
| Security / IAM | Governance | Authentik token, gateway pod role |
| Component teams (`acp-agentcore-sample` examples: agent, ai-ready-data, MCP, A2A) | Consumers | Register + route via Luminate |

## References

- Harness: `acp-harness-sdk/src/acp_harness_sdk/{config,gateway,registry,auth}.py`.
- Luminate gateway: `luminate/gateway/app/{settings.py,middleware/{proxy,authn,authz}.py,
  routers/authz.py}`.
- Luminate control plane: `luminate/backend/app/api_router.py` (catalog viewsets),
  `backend/app/iam/` (`/api/v1/iam/auth/token`).
- Partner API answer (Ian Donaldson, Q5): `/api/v1/catalog/{applications,agents,
  mcp-servers,models}`; (Q6) M2M via Authentik; (Q7) gateway in the Bedrock-consuming account.
- `sunlife-deployment` DD-5/DD-6 (gateway-side / cost — referenced, not owned here).
