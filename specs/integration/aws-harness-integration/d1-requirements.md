# AWS Harness Integration with Luminate — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD

## Internal ACP → Luminate Contract Deltas

| Surface | Harness today (internal ACP) | Luminate contract | Update needed |
|---|---|---|---|
| Model egress endpoint | internal AgentGateway `/v1/chat/completions` | OpenAI-compatible under **`/llm`** (`/llm/v1/chat/completions`) | Repoint + prefix |
| Egress auth | **`x-acp-agent-id`** header | **`Authorization: Bearer <JWT>`** | Replace header with Bearer JWT |
| Token source | Okta client-credentials (SLF API Platform) | Portal **`POST /api/v1/iam/auth/token`** (Authentik-backed) | New token provider |
| Registration | internal registry endpoints, flat schema | **`/api/v1/catalog/{agents,mcp-servers,models}`** DRF viewsets | Repoint + schema map |
| Entity schema | `RegisteredModel`/agent flat fields | `key`, `name`, `transport`, **`project` FK**, **`scope_tokens`**, **mandatory tags**, `configuration` | Payload mapping |
| Bedrock invocation | cross-account assume-role (consumer acct) | Luminate **gateway pod role** in consuming account | **Drop** assume-role for Luminate |
| Attribution/identity | agent id in header | agent identity in **JWT claims** (`sub`) + gateway authz | Identity via token, not header |

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | `GatewayClient` SHALL target Luminate's **OpenAI-compatible** endpoint under the **`/llm`** prefix (`/llm/v1/chat/completions`, `/llm/v1/models`) via a configurable base URL. | Must |
| FR-2 | `GatewayClient` SHALL authenticate with **`Authorization: Bearer <JWT>`**; the `x-acp-agent-id` header SHALL no longer be required for Luminate egress. | Must |
| FR-3 | A **Luminate token provider** SHALL obtain a JWT from **`POST /api/v1/iam/auth/token`** (client-credentials, Authentik-backed) and supply it to both the catalog APIs and the gateway, with auto-refresh on 401/403. | Must |
| FR-4 | `RegistryClient` SHALL register/read against Luminate's **catalog viewsets** (`/api/v1/catalog/agents`, `/mcp-servers`, `/models`) using DRF create/list/retrieve semantics. | Must |
| FR-5 | Registration payloads SHALL map to Luminate's schema: `key`, `name`, `transport`, **`project`** (FK/slug), **`scope_tokens`**, **mandatory tags**, `configuration` — the harness SHALL expose `project` and `scope`/`tags` as config. | Must |
| FR-6 | MCP tool/server registration SHALL use the Luminate `mcp-servers` catalog (server + tools/resources/prompts), not the internal MCP registry path. | Should |
| FR-7 | When targeting Luminate, the harness SHALL **not** assume a cross-account Bedrock role; model calls SHALL go **through the Luminate gateway** (which owns the Bedrock pod-role invocation). | Must |
| FR-8 | The **`acp-agentcore-sample` examples** (incl. the migrated ai-ready-data agent, and any component calling Bedrock directly via boto3) SHALL be updated to the Luminate-supporting harness version and route model calls through the Luminate `GatewayClient`. | Should |
| FR-9 | `ACPSettings` SHALL expose Luminate config: portal base URL, catalog prefix, gateway `/llm` URL, token endpoint, default `project` + `scope_tokens`/tags. | Must |
| FR-10 | The harness SHALL support **provider-agnostic auth** so the token source can later switch from Authentik to Okta/Entra without call-site changes (the gateway is IdP-agnostic — issuer/JWKS config). | Should |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **No call-site churn** — consumers keep using `GatewayClient.chat/complete` and `RegistryClient.register_*`; only configuration/targets change. | Must |
| NFR-2 | **Backward-compatible** — the harness SHOULD support both internal-ACP and Luminate targets via a config switch during migration. | Should |
| NFR-3 | **HTTPS-only**; Bearer token in `Authorization` header only; token custody via Secrets Manager / portal client credentials. | Must |
| NFR-4 | **Governed by default** — no component bypasses the Luminate gateway for model calls. | Must |
| NFR-5 | **Contract tests** against the Luminate gateway (`/llm`, Bearer) and catalog viewsets (schema). | Should |

## Constraints & Assumptions

- Luminate gateway is OpenAI-compatible (streaming tool-call normalization handled
  gateway-side) — the harness body format is already compatible.
- Registration requires a **`project`** and **mandatory tags**; the deploying component must
  be assigned a Luminate project/scope.
- M2M stays **Authentik** near-term (portal token endpoint); IdP swap is config-only later.
- `acp-adapter-aws` / `acp-aws-service-catalog` internals unread this session — confirm the
  role model boundary vs Luminate's in-account gateway before D3.

## Open Questions

- Exact catalog URL prefix (`/api/v1/catalog/...` per partner answer vs the DRF router's
  app-prefixed routes) — confirm against the running Luminate API root.
- Does Luminate issue the component's Authentik client credentials at registration, or must
  they be pre-provisioned (per-entity dynamic client)? (Ties to the M2M spec.)
- Token audience/scope required by the gateway for `/llm` egress.
