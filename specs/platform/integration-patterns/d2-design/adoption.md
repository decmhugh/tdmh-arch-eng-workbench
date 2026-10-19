# Adoption — SDK, raw HTTP, and what registration really needs

## Two ways in

```mermaid
flowchart LR
    subgraph SDK["Harness SDK · acp-harness-sdk"]
        S1["ACPSettings"] --> S2["GatewayClient"] & S3["RegistryClient"] & S4["auth providers"]
    end
    subgraph HTTP["Raw HTTP"]
        H1["POST /iam/auth/token"] --> H2["POST /llm/v1/chat/completions"]
    end
    SDK -->|"token cache, refresh,<br/>retries, streaming,<br/>typed errors"| GW["Gateway"]
    HTTP -->|"you own all of that"| GW
```

The SDK is a convenience, not a dependency — every pattern works over plain HTTP. What the SDK buys
is token caching and refresh (the throttling failure mode disappears), typed errors
(`PolicyDeniedError`, `KillSwitchActiveError`, `GuardrailBlockedError`, `RateLimitedError`),
streaming with reconnect, and **portability**.

## Portability is the reason to use it

```mermaid
flowchart LR
    CODE["Your call sites"] --> CFG["ACP_TARGET"]
    CFG -->|"=acp"| I["Internal build"]
    CFG -->|"=luminate"| L["Luminate"]
    style CODE fill:#e8f5e9,stroke:#2e7d32
```

`ACP_TARGET=luminate` re-points the same clients at a Luminate stack. Combined with per-environment
configuration, an application's **call sites do not change** between the internal build and
Luminate, or between DEV and PROD — only its `ACP_`-prefixed configuration does.

Auth providers, by target:

| Provider | For |
|---|---|
| `OktaAuthProvider` | Internal build; credentials from Secrets Manager or JSON |
| `LuminateAuthProvider` | Luminate portal client-credentials |
| `ApiKeyAuthProvider` | A pre-issued `lum_` key; static, non-refreshable |

## Registration: portal UI today

This is the part that surprises teams, so lead with it.

```mermaid
flowchart TD
    Q{"Registering a<br/>resource?"} -->|"today"| UI["Portal UI<br/>platform admin deploys"]
    Q -.->|"when SERVICE_PRINCIPAL_AUTH_ENABLED"| API["RegistryClient<br/>from code"]
    API -.-> NEED["needs: issuer / JWKS / audience<br/>+ a ServicePrincipal whose external_id<br/>matches the token subject"]
    style UI fill:#e8f5e9,stroke:#2e7d32
    style API fill:#eceff1,stroke:#546e7a,stroke-dasharray: 4 4
```

Machine-to-machine auth on the portal catalogue ships **default-off**. Against current deployments,
`RegistryClient` calls return `401` — **while the entire gateway path works normally**. That
asymmetry is the thing to communicate: *register in the portal, invoke from code*.

`self_register()` likewise returns 401 on Luminate, and `list_models()` returns 403 because
authorization resolves the model from the request body and a list has none.

## What a team provides to register

| Resource | Required | Then |
|---|---|---|
| **Agent** | Name, key (permanent slug), project | Platform admin deploys + grants access policy |
| **Model** | Name, key, project, author, type, context window, max tokens, gateway slug | Platform admin creates the offering (provider credentials + quota) |
| **MCP server** | Name, key, project, transport, backend URL (scheme + path) | Platform admin creates the deployment; access by policy |

Then — and only then — a credential can be issued, because it belongs to the `(resource, gateway)`
pair.

## The end-to-end a team actually walks

```mermaid
flowchart LR
    R["1 · Register<br/>portal"] --> D["2 · Deploy<br/>platform admin"]
    D --> C["3 · Credential<br/>shown once"]
    C --> S["4 · Store<br/>Secrets Mgr / Vault"]
    S --> T["5 · Exchange<br/>for a token, cache it"]
    T --> I["6 · Invoke<br/>/llm · /mcp · /a2a"]
    I -.->|"traces, tokens"| O["7 · Observe<br/>Langfuse"]
```

Steps 2 and 3 are **platform-admin actions** and cannot be delegated today — the constraint that
`gateway-environment-strategy` raises as its
second consortium ask.

## Worked examples to copy

[`acp-agentcore-sample`](https://bitbucket.sunlifecorp.com/projects/T1KACP/repos/acp-agentcore-sample/browse)
carries deployable examples, each demonstrating one shape:

| Example | Shape |
|---|---|
| `01-single-agent-mcp` | Agent → MCP tools, LLM governed. The smallest complete integration |
| `01-single-agent-mcp-luminate` | The **same agent** against Luminate — a configuration-only swap |
| `02-agent-to-agent` | Orchestrator → worker delegation |
| `03-single-agent-slm` | Agent against a small local model |

That `01-…` and `01-…-luminate` differ only in configuration is the portability claim, demonstrated
rather than asserted.
