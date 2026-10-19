# ACP AWS Harness SDK — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: EACPP-TBD

## Scope

This D1 spec defines the requirements for the `acp-harness-sdk` **as shipped in v0.7.0** — a
thin Python SDK that lets an existing AWS-hosted agent runtime (Amazon Bedrock / Bedrock AgentCore
and companion harnesses) **self-register** with the Agentic Control Plane (ACP) and route its LLM,
MCP, and agent-to-agent (A2A) traffic through the ACP **centralized gateway** for governed egress —
instead of calling `bedrock-runtime`, an MCP runtime, or a peer agent directly.

The SDK packages the reusable glue an egress harness needs: env-driven configuration, an
OpenAI-compatible gateway client, a registry client, an Okta client-credentials auth provider, an
A2A delegation client, and an MCP-through-gateway session helper. All governance enforcement (policy
evaluation, rate limiting, kill switches, guardrails, token exchange, cross-account role assumption,
routing) remains **server-side** in the ACP gateway and registries — the SDK is a convenience layer,
never a bypass vector.

Every ACP component / URL / header / account / model / identity is configurable via `ACP_`-prefixed
environment variables (or constructor kwargs); defaults target the ACP **dev EKS** control plane, so
the SDK runs with zero configuration in dev.

| Area | Description | Public symbol(s) |
|------|-------------|------------------|
| Configuration | Env-driven settings with dev-EKS defaults | `ACPSettings` |
| LLM egress | OpenAI-compatible completions through the gateway | `GatewayClient`, `ChatResult` |
| Registration | Dev self-register + governed (Okta) registration/binding | `RegistryClient` |
| Authentication | Okta client-credentials token minting + caching | `OktaAuthProvider`, `OktaCredentials` |
| A2A delegation | AgentCore-to-AgentCore (SigV4) + in-cluster (gateway A2A router) | `A2AClient` |
| MCP egress | MCP tool sessions routed through the gateway (no client-side SigV4) | `gateway_mcp_session`, `gateway_mcp_url` |

---

## User Stories

### US-1: Zero-Config Settings (Env-Driven)

**As an** agent developer deploying an existing Bedrock/AgentCore agent,
**I want** all ACP endpoints, headers, identity, and TLS behaviour to load from `ACP_`-prefixed env
vars (or a local `.env`) with sensible dev defaults,
**So that** the SDK runs against the ACP dev control plane with no configuration.

**Acceptance Criteria**:
- [ ] **Given** no configuration, **When** `ACPSettings()` is constructed, **Then** it populates gateway LLM URL, registry URLs, MCP/A2A gateway URLs, agent-id header name, default model, region, and account with the documented dev-EKS defaults
- [ ] **Given** an env var such as `ACP_GATEWAY_LLM_URL` or `ACP_AGENT_ID`, **When** `ACPSettings()` loads, **Then** the env value overrides the default (env prefix `ACP_`, `.env` file supported)
- [ ] **Given** an internal dev CA, **When** `ACP_TLS_VERIFY=false` is set, **Then** the SDK's HTTP clients skip TLS verification for ACP endpoints
- [ ] **Given** an unknown env var, **When** settings load, **Then** it is ignored (`extra="ignore"`) rather than raising

### US-2: Route LLM Egress Through the Gateway

**As an** agent developer,
**I want** to call `GatewayClient(settings).complete(prompt)` (or `.chat(messages)`),
**So that** my LLM traffic flows through the governed ACP gateway instead of `bedrock-runtime`.

**Acceptance Criteria**:
- [ ] **Given** an authenticated agent id in settings, **When** `complete(prompt, system=..., max_tokens=...)` is called, **Then** the SDK POSTs an OpenAI-shaped body to `{gateway_llm_url}/v1/chat/completions` and returns a typed `ChatResult`
- [ ] **Given** a raw messages array, **When** `chat(messages, model=..., max_tokens=...)` is called, **Then** the SDK sends the OpenAI `messages` payload and returns a `ChatResult` with `text`, `model`, `usage` (`input`/`output`/`total`), and `raw`
- [ ] **Given** `settings.agent_id` is set, **When** any gateway request is made, **Then** the SDK sends the attribution header (`settings.agent_id_header`, default `x-acp-agent-id`) so the gateway can attribute the call
- [ ] **Given** a non-2xx gateway response, **When** the SDK receives it, **Then** it raises via `httpx` `raise_for_status()` (the gateway is the policy authority)
- [ ] **Given** a `with GatewayClient(...) as client:` block, **When** the block exits, **Then** the underlying HTTP client is closed

### US-3: Function-Calling / Tool Context via `extra_body`

**As an** agent developer building a function-calling agent,
**I want** to pass extra OpenAI request fields (`tools`, `tool_choice`, `temperature`) to the gateway,
**So that** I can drive tool-use reasoning without the SDK constraining the request shape.

**Acceptance Criteria**:
- [ ] **Given** `extra_body={"tools": [...], "tool_choice": "auto"}`, **When** `chat(..., extra_body=extra_body)` is called, **Then** the SDK merges those fields into the completion payload
- [ ] **Given** the model returns tool calls, **When** the `ChatResult` is inspected, **Then** the tool-call detail is readable from `ChatResult.raw`

### US-4: List Available Models

**As an** agent developer,
**I want** to call `GatewayClient(settings).list_models()`,
**So that** I can see which model ids the gateway advertises.

**Acceptance Criteria**:
- [ ] **Given** an initialized client, **When** `list_models()` is called, **Then** the SDK GETs `{gateway_llm_url}/v1/models` and returns a list of model id strings parsed from the OpenAI `data[]` shape

### US-4A: Generate Embeddings Through the Gateway

**As an** agent developer (or any caller — agent, Lambda, BFF, or client application),
**I want** to call `GatewayClient(settings).embed(input, model=...)`,
**So that** I can generate text embeddings through the governed ACP gateway using embedding
models like Amazon Titan, without constructing the HTTP request or handling the response parsing
myself.

**Acceptance Criteria**:
- [ ] **Given** a text string or list of strings, **When** `embed(input, model=...)` is called,
  **Then** the SDK POSTs an OpenAI-compatible body to `{gateway_llm_url}/v1/embeddings` and
  returns a typed `EmbeddingResult`
- [ ] **Given** a single string input, **When** `embed("text to embed")` is called, **Then** the
  SDK sends `{"model": "...", "input": "text to embed"}` and returns the embedding vector(s)
- [ ] **Given** a list of strings, **When** `embed(["text one", "text two"])` is called, **Then**
  the SDK sends `{"model": "...", "input": ["text one", "text two"]}` and returns one embedding
  per input in the same order
- [ ] **Given** `settings.agent_id` is set, **When** the embedding request is made, **Then** the
  SDK sends the attribution header (same governance as chat completions)
- [ ] **Given** a non-2xx gateway response, **When** the SDK receives it, **Then** it raises via
  the typed error hierarchy (`PolicyDeniedError`, `RateLimitedError`, etc.) — identical to the
  chat completions error path
- [ ] **Given** the gateway returns an OpenAI-compatible embedding response, **When** the SDK
  parses it, **Then** `EmbeddingResult` exposes `embeddings` (list of float vectors), `model`,
  `usage` (`{prompt_tokens, total_tokens}`), and `raw` (full response body)
- [ ] **Given** no explicit model is provided, **When** `embed(input)` is called, **Then** the SDK
  uses `settings.embedding_model` (env var `ACP_EMBEDDING_MODEL_ID`, no default — embedding model
  must be explicitly configured)

### US-5: Dev Self-Registration (No Token)

**As an** agent developer onboarding in dev,
**I want** to call `RegistryClient(settings).self_register()`,
**So that** I obtain an `agent_id` for gateway attribution without setting up Okta.

**Acceptance Criteria**:
- [ ] **Given** settings-derived agent metadata (name, owner, model, account tags), **When** `self_register()` is called, **Then** the SDK POSTs to `{agent_registry_url}/agents/self-register` (no bearer token) and returns the registry body `{"agent": {...}, ...}`
- [ ] **Given** a successful registration, **When** the developer reads `response["agent"]["agent_id"]` and sets `settings.agent_id`, **Then** subsequent gateway calls are attributed to that agent
- [ ] **Given** a non-2xx response, **When** `self_register()` runs, **Then** it raises via `raise_for_status()`

### US-6: Governed Registration with Okta

**As an** agent developer promoting an agent to a governed (prod-like) registry,
**I want** `register_agent()` to authenticate with an Okta bearer token automatically,
**So that** I register against a token-protected registry without hand-managing tokens.

**Acceptance Criteria**:
- [ ] **Given** a `RegistryClient(settings, auth=OktaAuthProvider(...))`, **When** `register_agent()` is called with no explicit token, **Then** the SDK mints/caches an Okta token via the provider and sends it as `Authorization: Bearer {token}`
- [ ] **Given** an explicit `token=` argument, **When** `register_agent(token=...)` is called, **Then** the SDK uses the supplied token and does **not** auto-refresh
- [ ] **Given** an auth-provider-minted token that the registry rejects with 401/403, **When** the SDK detects it, **Then** it invalidates the cached token, mints a fresh one, and retries the request **once**
- [ ] **Given** a full agent record, **When** `register_agent(payload=...)` is called, **Then** the supplied payload overrides the settings-derived default body

### US-7: Register and Bind MCP Servers / Tools

**As an** agent developer wiring up governed MCP tools,
**I want** to register an MCP server, register its tools, and bind a tool to an agent,
**So that** the gateway can resolve and authorize those tools at runtime.

**Acceptance Criteria**:
- [ ] **Given** a server record, **When** `register_mcp_server(server, token=...)` is called, **Then** the SDK POSTs to `{mcp_registry_url}/api/servers` with bearer auth (explicit token or provider)
- [ ] **Given** a `server_id` and tool record, **When** `register_mcp_tool(server_id, tool, token=...)` is called, **Then** the SDK POSTs to `{mcp_registry_url}/api/servers/{server_id}/tools`
- [ ] **Given** an `agent_id` and binding record, **When** `bind_agent_tool(agent_id, binding, token=...)` is called, **Then** the SDK POSTs to `{agent_registry_url}/agents/{agent_id}/tools`
- [ ] **Given** any governed write, **When** the token is provider-minted and rejected (401/403), **Then** the single-retry refresh behaviour from US-6 applies

### US-8: Look Up and List Registry Resources

**As an** agent developer,
**I want** read methods for agents, MCP servers, and their tools,
**So that** I can inspect what is registered without constructing HTTP requests.

**Acceptance Criteria**:
- [ ] **Given** an `agent_id` (or `settings.agent_id`), **When** `get_agent(agent_id)` is called, **Then** the SDK returns the agent record, or `None` on 404
- [ ] **Given** `list_agents()`, `list_mcp_servers()`, `list_mcp_tools(server_id)`, or `list_agent_tools(agent_id)`, **When** called, **Then** the SDK GETs the collection endpoint and normalizes both `[...]` and `{"items": [...]}` response shapes into a list
- [ ] **Given** an unauthenticated read against an open dev endpoint, **When** called, **Then** it succeeds without a token

### US-9: Okta Client-Credentials Token Provider

**As an** agent developer,
**I want** an `OktaAuthProvider` that mints and caches a client-credentials bearer token,
**So that** governed registry calls stay authenticated with zero token code in my agent.

**Acceptance Criteria**:
- [ ] **Given** `OktaCredentials{token_url, client_id, client_secret, scope?}`, **When** `get_token()` is called, **Then** the SDK performs a `client_secret_post` grant (form-encoded, `application/x-www-form-urlencoded`) and returns the `access_token`
- [ ] **Given** a cached token, **When** `get_token()` is called again before expiry, **Then** the cached token is returned; **When** within 30s of expiry, **Then** a fresh token is minted
- [ ] **Given** an empty `scope`, **When** the token is requested, **Then** `scope` is omitted from the request body
- [ ] **Given** an AWS Secrets Manager secret id, **When** `OktaAuthProvider.from_secrets_manager(secret_id, region=...)` is called, **Then** the provider loads credentials from the secret (requires the `aws` extra / boto3)
- [ ] **Given** a raw secret JSON string or mapping, **When** `OktaAuthProvider.from_secret(...)` is called, **Then** the provider is built without touching AWS
- [ ] **Given** the helpers, **When** `refresh_cached_token()`, `invalidate_token()`, or `get_expires_in()` are used, **Then** they force-refresh, clear the cache, and report remaining TTL respectively

### US-10: Invoke MCP Tools Through the Gateway

**As an** agent developer,
**I want** an MCP client session that routes through the ACP gateway,
**So that** every MCP tool call is SigV4-signed and forwarded by the gateway (traced + authorized) —
without client-side AWS signing.

**Acceptance Criteria**:
- [ ] **Given** a registered server name, **When** `async with gateway_mcp_session("server") as session:` is entered, **Then** the SDK opens an initialized streamable-HTTP MCP session pointed at `{mcp_gateway_url}/{server}`
- [ ] **Given** an open session, **When** `await session.list_tools()` / `await session.call_tool(name, args)` is called, **Then** the gateway signs and forwards to the governed AgentCore MCP runtime and returns the result
- [ ] **Given** `settings.agent_id` (or an `agent_id=` override), **When** the session is opened, **Then** the SDK sends the attribution header so the tool call is attributable
- [ ] **Given** an untrusted server name containing `..`, whitespace, `\`, `?`, or `#`, **When** `gateway_mcp_url(server)` is called, **Then** it raises `ValueError` (path/URL-injection guard)
- [ ] **Given** the `mcp` package is not installed, **When** `gateway_mcp_session(...)` is used, **Then** a `RuntimeError` instructs the developer to install the `mcp` extra

### US-11: Delegate to an AgentCore Peer Agent (SigV4)

**As an** agent developer orchestrating multiple AgentCore agents,
**I want** to delegate a sub-task to another Bedrock AgentCore runtime,
**So that** I can compose agents while each still routes its own LLM through the ACP gateway.

**Acceptance Criteria**:
- [ ] **Given** a target agent runtime ARN, **When** `A2AClient(settings).invoke_runtime(arn, prompt, session_id=...)` is called, **Then** the SDK calls `bedrock-agentcore` `InvokeAgentRuntime` (SigV4) with a JSON `{"prompt": ...}` payload and a ≥33-char runtime session id
- [ ] **Given** a JSON response body, **When** the runtime replies, **Then** the SDK returns the parsed object; **Given** a non-JSON body, **Then** it returns `{"answer": <decoded text>}`
- [ ] **Given** boto3 is not installed, **When** `invoke_runtime(...)` is called, **Then** a `RuntimeError` instructs the developer to install the `aws` extra

### US-12: Delegate to an In-Cluster Peer Agent via the Gateway A2A Router

**As an** agent developer,
**I want** to delegate to an in-cluster A2A-enabled agent through the gateway's governed A2A router,
**So that** the delegation hop itself is authorized, traced, and killable.

**Acceptance Criteria**:
- [ ] **Given** a target agent id, **When** `A2AClient(settings).invoke_gateway(target_agent_id, text, message_id=...)` is called, **Then** the SDK POSTs an A2A JSON-RPC 2.0 `message/send` request to `{a2a_gateway_url}/a2a/{target_agent_id}`
- [ ] **Given** `settings.agent_id` is set, **When** the request is sent, **Then** the attribution header is included
- [ ] **Given** a successful call, **When** the router responds, **Then** the SDK returns the parsed A2A JSON-RPC response object; a non-2xx status raises via `raise_for_status()`

### US-13: Minimal Runtime Footprint with Optional Extras

**As an** agent developer wary of dependency bloat,
**I want** a minimal core install with optional extras for AWS and MCP,
**So that** I only pull in boto3 or the MCP client when I actually use those code paths.

**Acceptance Criteria**:
- [ ] **Given** `pip install acp-harness-sdk`, **When** installed, **Then** only the core runtime deps are pulled (`httpx`, `pydantic`, `pydantic-settings`) on Python ≥ 3.11
- [ ] **Given** `pip install 'acp-harness-sdk[aws]'`, **When** installed, **Then** boto3 is available for Secrets Manager loading and AgentCore `invoke_runtime`
- [ ] **Given** `pip install 'acp-harness-sdk[mcp]'`, **When** installed, **Then** the `mcp` client is available for `gateway_mcp_session`
- [ ] **Given** an extra is missing at runtime, **When** the dependent code path is exercised, **Then** a clear `RuntimeError` names the exact extra to install

---

## Planned — Streaming (Next Delivery, target v0.8.0)

> **Status**: 🔜 Planned — **Next Delivery**. Not implemented in v0.7.0. Streaming will use
> **Server-Sent Events (SSE)** over the existing `POST /v1/chat/completions` HTTP path with
> `stream=true`. This is a transport change from the earlier D1 draft, which specified bidirectional
> WebSocket. The decision to use SSE instead of WebSocket was driven by five findings from the
> EACPP-812 implementation review (PR #5):
>
> 1. **No WS endpoint exists to enable.** The SDK's `connect()` targeted
>    `/v1/chat/completions/stream` over `wss` with a bespoke frame protocol (`delta`,
>    `tool_call_delta`, `usage`, `done`, `error`, close codes 4401/4403/4423/4429). Grepping
>    the entire Control Plane workspace — every service, spec, and gateway config —
>    `chat/completions/stream` and `tool_call_delta` return zero hits. Nothing implements or
>    specifies this protocol. Serving the SDK as written would require building a new WebSocket
>    microservice — its own spec, repo, threat model, and deploy.
> 2. **Governance gap.** AgentGateway upstream explicitly documents that streaming (SSE) responses
>    retain full policy enforcement (prompt guards, JWT auth, rate limiting), while the Realtime
>    (WebSocket) route type does **not** support prompt guards, prompt enrichment, or request-body
>    rate limiting (agentgateway#2956). Moving LLM calls onto a transport where guardrails provably
>    do not apply is a governance regression requiring an explicit, documented exception — not a
>    side effect of an SDK transport choice.
> 3. **SSE delivers the same streaming outcome.** Verified against dev with
>    `anthropic.claude-3-haiku-20240307-v1:0` — proper incremental `chat.completion.chunk` deltas
>    over SSE. If a consuming app needs a WebSocket toward its own clients, it should terminate the
>    socket at the app/BFF edge and relay the SSE deltas onto it: the browser-facing contract is
>    unchanged, the governed path is preserved, and no gateway change is required.
> 4. **Prior decisions align.** The UI advanced-features D2 chose SSE over WebSocket deliberately
>    ("WebSocket requires additional ingress annotations"). The AI Gateway D1 (AC line 153) states
>    that on a WS upgrade only the initial handshake is captured and WebSocket data frames are not
>    captured as metrics.
> 5. **Version risk.** The gateway image wraps upstream v1.1.0, which carries agentgateway#2095 —
>    WS upgrades fail when the upstream returns a capitalized `Upgrade` token.
>
> **WebSocket streaming is not abandoned** — it is deferred to a future phase, gated on a concrete
> bidirectional use case that SSE genuinely cannot serve, a dedicated D1/D2 spec for the WS protocol,
> and a signed-off governance exception. See *Deferred — Bidirectional WebSocket Streaming* below.
>
> **Design implications:**
> - **Gateway support is production-ready today** — the existing AgentGateway OSS (Rust) gateway
>   already serves `POST /v1/chat/completions` with `stream=true` over HTTP/SSE with full policy
>   enforcement. No gateway change is required.
> - **No new client dependency** — `httpx` natively supports SSE via async streaming response
>   iteration. No optional `[ws]` extra is needed; the `[stream]` extra is unnecessary.
> - **Sync + async** — SSE works over standard HTTP, so both sync and async interfaces are
>   supported (`httpx.Client` / `httpx.AsyncClient`).
> - **Auth on every request** — each SSE request carries the bearer token and attribution header
>   as standard HTTP headers. No handshake-only auth limitation; token refresh works normally.
> - **Full governance** — prompt guards, rate limiting, guardrails, and body-based policies all
>   apply to SSE streaming responses per upstream documentation.

### US-14: LLM Streaming over SSE — *Planned*

**As an** agent developer building responsive LLM experiences,
**I want** to stream completions incrementally via SSE,
**So that** I can render output token-by-token without waiting for the full response.

**Acceptance Criteria**:
- [ ] **Given** a configured gateway, **When** `async for chunk in GatewayClient(settings).stream(messages, model=..., max_tokens=..., extra_body=...)` is called, **Then** the SDK sends `POST /v1/chat/completions` with `stream=true` and yields typed `ChatChunk` events (`type="delta"` with `delta` text) as SSE `data:` lines arrive
- [ ] **Given** a sync context, **When** `for chunk in GatewayClient(settings).stream_sync(messages, ...)` is called, **Then** the SDK provides the same typed `ChatChunk` iteration over a synchronous `httpx.Client` SSE stream
- [ ] **Given** `settings.agent_id` is set, **When** the stream request is sent, **Then** the attribution header and bearer token are included as standard HTTP headers (full governance enforcement applies)
- [ ] **Given** the stream completes, **When** the terminal `data: [DONE]` SSE event arrives, **Then** the SDK yields a final `ChatChunk` with `type="done"` and `usage` (`{input, output, total}`) when provided by the gateway
- [ ] **Given** the SSE connection drops mid-stream, **When** the read fails, **Then** the SDK raises a typed `StreamDisconnectedError` (chunks already yielded remain observable)

### US-15: Streamed Tool-Call Deltas over SSE — *Planned*

**As an** agent developer running function-calling loops,
**I want** tool-call decisions surfaced incrementally in the SSE stream,
**So that** I can begin processing tool calls before the full response completes.

**Acceptance Criteria**:
- [ ] **Given** `extra_body={"tools": [...], "tool_choice": "auto"}` on a `stream(...)` call, **When** the model streams a tool-use decision, **Then** the SDK yields `ChatChunk` events with `type="tool_call"` carrying incremental `tool_call` deltas (`name`, `arguments` fragments) from the SSE `chat.completion.chunk` events
- [ ] **Given** fragmented `arguments` across SSE events, **When** the tool-call completes (signalled by a subsequent chunk or `[DONE]`), **Then** the SDK exposes the reassembled arguments (or the raw fragments via `ChatChunk.raw`)
- [ ] **Given** the caller has executed a tool and needs to continue, **When** a new `stream(...)` call includes the tool result in the messages array, **Then** the model continuation streams back over a fresh SSE connection (each turn is a separate HTTP request)

### US-16: A2A Task Streaming over SSE — *Planned*

**As an** agent developer delegating a task to a peer agent,
**I want** to stream task status updates from the peer agent via SSE,
**So that** I receive real-time progress without polling.

**Acceptance Criteria**:
- [ ] **Given** a target agent id, **When** `async for event in A2AClient(settings).send_task_stream(target_agent_id, text)` is called, **Then** the SDK sends an A2A `message/stream` request to `{a2a_gateway_url}/a2a/{target_agent_id}` and yields typed A2A events (`TaskStatusEvent`, `TaskArtifactEvent`, `TaskResultEvent`) from the SSE response
- [ ] **Given** `settings.agent_id` is set, **When** the stream request is sent, **Then** the attribution header is included
- [ ] **Given** the task finishes, **When** the terminal SSE event arrives, **Then** a `TaskResultEvent` with the final result is yielded
- [ ] **Given** the peer agent requires follow-up input, **When** the stream yields a `TaskInputRequiredEvent`, **Then** the caller initiates a new `send_task_stream(...)` with the follow-up input (each interaction is a separate HTTP request)

### US-17: MCP Streaming Progress over SSE — *Planned*

**As an** agent developer invoking long-running MCP tools through the gateway,
**I want** streamed progress notifications from the MCP tool execution,
**So that** I can display progress to the user while a tool runs.

**Acceptance Criteria**:
- [ ] **Given** a running MCP tool call via `gateway_mcp_session`, **When** the server emits `progress` notifications over the MCP Streamable HTTP transport, **Then** the SDK surfaces them as typed `ProgressEvent` objects (`progress`, `total`) while the tool call is in flight
- [ ] **Given** the MCP Streamable HTTP transport already uses SSE framing internally, **When** the `mcp` library processes the stream, **Then** no additional transport layer is needed — progress events are already delivered over the governed HTTP path
- [ ] **Given** the `mcp` extra is not installed, **When** `gateway_mcp_session(...)` is used, **Then** a `RuntimeError` names the exact extra to install

### US-18: SSE Stream Lifecycle & Error Semantics — *Planned*

**As an** agent developer,
**I want** SSE stream failures surfaced as typed errors with clean teardown,
**So that** dropped connections don't leak resources or hide governance denials.

**Acceptance Criteria**:
- [ ] **Given** the SSE connection drops mid-stream, **When** the read fails, **Then** the SDK raises a typed `StreamDisconnectedError` (chunks already yielded remain observable)
- [ ] **Given** the gateway returns a non-2xx status on the streaming request (e.g. 401, 403, 429, 423), **When** the HTTP response is received, **Then** the SDK raises the appropriate typed error (`AuthenticationError`, `PolicyDeniedError`, `RateLimitedError`, `KillSwitchActiveError`) with reason + correlation id — identical to the non-streaming error path
- [ ] **Given** a streaming response, **When** the `async for` / `for` loop exits (break, exception, or completion), **Then** the HTTP connection is closed deterministically (context-manager / response close)
- [ ] **Given** a guardrail violation detected mid-stream by the gateway, **When** the gateway terminates the SSE stream with an error event, **Then** the SDK raises `GuardrailBlockedError` carrying the reason and correlation id

### Deferred — Bidirectional WebSocket Streaming (Future Phase)

> **Status**: 🔒 **On hold** — revisit when a concrete use case requires real-time, two-way
> interaction that SSE genuinely cannot serve.
>
> The original D1 (pre-amendment) specified bidirectional WebSocket (`wss://`) for all streaming
> paths. The EACPP-812 implementation review demonstrated that:
> - No gateway endpoint implements the bespoke WS frame protocol the SDK targeted.
> - The Realtime (WebSocket) route type does not support prompt guards, prompt enrichment, or
>   request-body rate limiting — a governance regression for a control plane whose purpose is
>   enforcing policy on model traffic.
> - SSE delivers equivalent incremental streaming with full governance enforcement.
>
> WebSocket streaming remains a valid future direction for use cases requiring true server-initiated
> push (e.g. MCP sampling/elicitation callbacks, A2A follow-up input without polling). Before
> proceeding, the following gates MUST be met:
> - A concrete use case is identified that SSE cannot serve.
> - A dedicated D1/D2 spec defines the WS frame protocol, close codes, and auth lifecycle.
> - A governance exception is documented and signed off, explicitly acknowledging the guardrail
>   and rate-limiting limitations of the WebSocket transport.
> - The gateway team implements and deploys the WS listener (EACPP-211 coordination).
>
> The user stories from the original draft (US-14-WS through US-18-WS: duplex LLM session,
> duplex A2A channel, duplex MCP session, WS lifecycle/typed errors) are preserved in version
> control and can be restored when the gates above are satisfied.

> **Delivery note (v0.8.0 scope):** introduces `ChatChunk` and A2A/MCP streaming event types,
> SSE streaming methods (`GatewayClient.stream()` / `stream_sync()`,
> `A2AClient.send_task_stream()`), and typed streaming errors. Sync + async support; no new
> optional extra required. No public break to the v0.7.0 request/response methods — SSE streaming
> is purely additive. **Testable today** against the existing AgentGateway (already serves SSE on
> `POST /v1/chat/completions` with `stream=true`); no gateway change is required.

---

## Functional Requirements

### FR-1: OpenAI-Compatible LLM Egress

`GatewayClient` MUST send OpenAI-shaped requests to the gateway LLM listener:

```
POST {gateway_llm_url}/v1/chat/completions
Headers:
  content-type: application/json
  {agent_id_header}: {agent_id}          # e.g. x-acp-agent-id, only when agent_id set
Body:
  { "model": "...", "messages": [...], "max_tokens": 1024, ...extra_body }

GET {gateway_llm_url}/v1/models           # → ["model-id", ...]
```

`ChatResult` MUST expose `text`, `model`, `usage` (`{input, output, total}`), and `raw`.

`GatewayClient` MUST also send OpenAI-shaped embedding requests to the gateway LLM listener:

```
POST {gateway_llm_url}/v1/embeddings
Headers:
  content-type: application/json
  {agent_id_header}: {agent_id}          # e.g. x-acp-agent-id, only when agent_id set
Body:
  { "model": "...", "input": "..." | ["...", "..."] }
```

`EmbeddingResult` MUST expose `embeddings` (list of float vectors), `model`,
`usage` (`{prompt_tokens, total_tokens}`), and `raw`. The `/v1/embeddings` path shares the same
LLM listener, authentication, authorization, and attribution as `/v1/chat/completions` — no
additional gateway configuration is required.

### FR-2: Registry Operations

`RegistryClient` MUST support:

| Operation | Method | Endpoint | Auth |
|-----------|--------|----------|------|
| Dev self-register | `self_register()` | `POST {agent_registry_url}/agents/self-register` | none |
| Governed register | `register_agent(payload?, token?)` | `POST {agent_registry_url}/agents` | bearer (explicit or provider) |
| Fetch agent | `get_agent(agent_id?)` | `GET {agent_registry_url}/agents/{id}` | none; `None` on 404 |
| List agents | `list_agents()` | `GET {agent_registry_url}/agents` | none |
| Bind tool to agent | `bind_agent_tool(agent_id, binding, token?)` | `POST {agent_registry_url}/agents/{id}/tools` | bearer |
| List agent tools | `list_agent_tools(agent_id)` | `GET {agent_registry_url}/agents/{id}/tools` | none |
| Register MCP server | `register_mcp_server(server, token?)` | `POST {mcp_registry_url}/api/servers` | bearer |
| List MCP servers | `list_mcp_servers()` | `GET {mcp_registry_url}/api/servers` | none |
| Register MCP tool | `register_mcp_tool(server_id, tool, token?)` | `POST {mcp_registry_url}/api/servers/{id}/tools` | bearer |
| List MCP tools | `list_mcp_tools(server_id)` | `GET {mcp_registry_url}/api/servers/{id}/tools` | none |

Governed writes MUST refresh a provider-minted token once on 401/403 and retry.

### FR-3: Okta Client-Credentials Auth

`OktaAuthProvider` MUST:
- Perform the `client_secret_post` grant (form body, `application/x-www-form-urlencoded`)
- Cache the token and refresh it within a 30-second skew of expiry
- Default to a 600-second lifetime when `expires_in` is absent
- Omit `scope` from the request when empty
- Load credentials from a JSON string/mapping (`from_secret`) or AWS Secrets Manager (`from_secrets_manager`, `aws` extra)
- Never log or embed the token or client secret in messages

### FR-4: A2A Delegation (Two Topologies)

`A2AClient` MUST provide:
- `invoke_runtime(arn, prompt, session_id?)` — Bedrock AgentCore `InvokeAgentRuntime` (SigV4, boto3), ≥33-char session id, JSON-or-fallback response parsing
- `invoke_gateway(target_agent_id, text, message_id?)` — A2A JSON-RPC `message/send` to `{a2a_gateway_url}/a2a/{target_agent_id}` with attribution header

### FR-5: MCP-Through-Gateway Session

`gateway_mcp_session` MUST open an initialized streamable-HTTP MCP session to
`{mcp_gateway_url}/{server}` with no client-side AWS signing, sending the attribution header.
`gateway_mcp_url` MUST reject server names containing `..`, whitespace, `\`, `?`, or `#`.

### FR-6: Configuration Resolution

`ACPSettings` MUST load from `ACP_`-prefixed env vars or a `.env` file, ignore unknown keys, and
default to the documented dev-EKS control plane. All URLs, header names, model, region, account, and
identity MUST be overridable.

### FR-7: Streaming (Planned — Next Delivery, v0.8.0)

Streaming MUST be delivered over **SSE** (`POST /v1/chat/completions` with `stream=true`), additive
to the v0.7.0 request/response methods (no public break). Bidirectional WebSocket is deferred to a
future phase pending a concrete use case and governance exception sign-off:

| Path | Method(s) | Wire | Yields |
|------|-----------|------|--------|
| LLM | `GatewayClient.stream()` / `stream_sync()` | `POST /v1/chat/completions` `stream=true` → SSE | `ChatChunk{type, delta, tool_call?, usage?, raw}` |
| A2A | `A2AClient.send_task_stream()` | A2A `message/stream` → SSE | `TaskStatusEvent` / `TaskArtifactEvent` / `TaskInputRequiredEvent` / `TaskResultEvent` |
| MCP | `gateway_mcp_session()` (existing) | MCP Streamable HTTP (SSE framing handled by `mcp` library) | `ProgressEvent{progress, total}` + terminal `ToolResult` |

Requirements:
- **Sync + async** — SSE streams over standard HTTP, so both `httpx.AsyncClient` and `httpx.Client`
  are supported. No new client dependency is required.
- **Auth on every request** — the bearer token and attribution header are sent as standard HTTP
  headers on each streaming request. Token refresh works normally between requests.
- **Full governance enforcement** — SSE streaming retains prompt guards, JWT auth, rate limiting,
  and all body-based policies per upstream AgentGateway documentation.
- HTTP responses MUST be closed deterministically on completion, `break`, or error (context-manager /
  `response.close()`).
- Failures MUST surface as typed errors: `StreamDisconnectedError` (connection drop),
  `GuardrailBlockedError` / `PolicyDeniedError` / `RateLimitedError` / `AuthenticationError`
  (non-2xx or mid-stream error event), carrying reason + correlation id.
- **Tool-call continuation** — after executing a tool, the caller sends a new `stream()` request
  with the tool result appended to the messages array. Each turn is a separate HTTP request.

---

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Footprint | Minimal core runtime dependencies | 3 core deps: `httpx`, `pydantic`, `pydantic-settings` |
| NFR-2 | Compatibility | Supported Python runtime | Python ≥ 3.11 |
| NFR-3 | Modularity | Heavy deps behind extras | `aws` (boto3), `mcp` (mcp) optional; clear `RuntimeError` when missing |
| NFR-4 | Type safety | Public interfaces typed; ships `py.typed` | mypy clean; PEP 561 marker present |
| NFR-5 | Quality | Lint + type + coverage gates | `ruff` + `mypy` clean; unit tests ~100% (httpx `MockTransport`) |
| NFR-6 | Security | No secrets/tokens in logs or exceptions | Token + client secret never logged |
| NFR-7 | Governance | SDK cannot bypass gateway controls | All egress via gateway/registry endpoints; policy stays server-side |
| NFR-8 | Configurability | Zero-config dev default; full override | Runs against dev EKS with no env; every value overridable via `ACP_` env |
| NFR-9 | TLS | Verify TLS by default; opt-out for dev CA | `tls_verify=True` default, `ACP_TLS_VERIFY=false` opt-out |
| NFR-10 | Resource hygiene | HTTP clients closable | Context managers + `close()` on `GatewayClient`, `RegistryClient`, `A2AClient` |

---

## Public API Surface

| Symbol | Kind | Purpose |
|--------|------|---------|
| `ACPSettings` | class | Env-driven config (`ACP_` prefix): gateway/registry/MCP/A2A URLs, agent id + header, model, region, account, TLS |
| `GatewayClient` | class | OpenAI-compatible LLM egress — `chat()`, `complete()`, `embed()`, `list_models()`; sets attribution header |
| `RegistryClient` | class | `self_register()`, `register_agent()`, `register_mcp_server()`, `register_mcp_tool()`, `bind_agent_tool()`, `get_agent()`, `list_*()` |
| `OktaAuthProvider` | class | Mint + cache Okta control-plane token (`client_secret_post`); `from_secrets_manager()` / `from_secret()` / `get_token()` |
| `OktaCredentials` | dataclass | Okta secret shape `{token_url, client_id, client_secret, scope}` |
| `A2AClient` | class | A2A delegation — `invoke_runtime()` (AgentCore SigV4), `invoke_gateway()` (in-cluster A2A router) |
| `gateway_mcp_session` | async ctx mgr | Open a governed MCP session through the gateway |
| `gateway_mcp_url` | function | Build/validate the gateway MCP endpoint URL for a server name |
| `ChatResult` | dataclass | Parsed completion (`text`, `model`, `usage`, `raw`) |
| `EmbeddingResult` | dataclass | Parsed embedding (`embeddings`, `model`, `usage`, `raw`) |
| `__version__` | str | Package version |

---

## Configuration (`ACP_` Environment Variables)

| Env var | Default (dev EKS) | Purpose |
|---------|-------------------|---------|
| `ACP_GATEWAY_LLM_URL` | `…/agentgateway/llm` | OpenAI-compatible LLM listener base |
| `ACP_AGENT_ID_HEADER` | `x-acp-agent-id` | Attribution header name (gateway contract) |
| `ACP_AGENT_REGISTRY_URL` | `…/agent-registry` | Agent Registry base |
| `ACP_MCP_REGISTRY_URL` | `…/mcp-registry` | MCP Registry base |
| `ACP_A2A_GATEWAY_URL` | `…/agentgateway/a2a` | A2A router base (`/a2a/{target_agent_id}`) |
| `ACP_MCP_GATEWAY_URL` | `…/agentgateway-mcp/mcp` | MCP egress base (`/{server}`) |
| `ACP_TLS_VERIFY` | `true` | Verify TLS against ACP ingress |
| `ACP_BEDROCK_MODEL_ID` | `anthropic.claude-3-haiku-20240307-v1:0` | Default model + registration model |
| `ACP_EMBEDDING_MODEL_ID` | *(none — must be set explicitly)* | Default embedding model for `embed()` (e.g. `amazon.titan-embed-text-v2:0`) |
| `ACP_AWS_REGION` | `ca-central-1` | AWS region |
| `ACP_AWS_ACCOUNT_ID` | `131935619052` | Workload account (registration tag) |
| `ACP_AGENT_ID` | `""` | Registry-assigned id (attribution header value) |
| `ACP_AGENT_NAME` / `ACP_AGENT_OWNER` / `ACP_AGENT_VERSION` | `acp-aws-harness-agent` / `you@sunlife.com` / `0.1.0` | Registration metadata |

---

## Data Model Requirements

| Entity | Key Fields | Notes |
|--------|-----------|-------|
| `ChatResult` | `text`, `model`, `usage{input,output,total}`, `raw` | Parsed from OpenAI completion response |
| `EmbeddingResult` | `embeddings`, `model`, `usage{prompt_tokens,total_tokens}`, `raw` | Parsed from OpenAI embedding response; `embeddings` is `list[list[float]]` |
| `OktaCredentials` | `token_url`, `client_id`, `client_secret`, `scope?` | Mirrors AWS Secrets Manager JSON shape; `from_json()` |
| Agent registration payload | `name`, `owner`, `agent_type`, `autonomy_level`, `platform`, `model_id`, `approved_models`, `tags{aws_account,…}` | Settings-derived default; overridable via `payload=` |

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| `agent_id` unset | Attribution header omitted; gateway calls remain unattributed |
| Provider token rejected (401/403) on governed write | Invalidate cache, mint fresh token, retry once |
| Explicit `token=` rejected | No auto-refresh; error surfaces via `raise_for_status()` |
| Token response omits `expires_in` | Default 600s lifetime assumed |
| Empty Okta `scope` | Omitted from token request body |
| `get_agent()` → 404 | Return `None` (not an exception) |
| Collection endpoint returns `{"items":[…]}` vs `[…]` | Both normalized to a list |
| Non-JSON AgentCore runtime response | Wrapped as `{"answer": <decoded text>}` |
| Malicious MCP server name (`..`, space, `\`, `?`, `#`) | `gateway_mcp_url` raises `ValueError` |
| `aws` / `mcp` extra not installed | `RuntimeError` naming the exact extra to install |
| Internal dev CA | `ACP_TLS_VERIFY=false` disables verification |
| `embed()` with no model and no `ACP_EMBEDDING_MODEL_ID` | `ValueError` raised before the network call — embedding model must be explicit |
| `embed()` against a non-embedding model | Gateway returns the provider's error (e.g. Bedrock 400); SDK surfaces via typed error hierarchy |

---

## Constraints

- **Governance is server-side** — the SDK MUST NOT implement policy, routing, guardrails, or token
  exchange for downstream services; those remain in the ACP gateway/registries.
- **Python ≥ 3.11**; distributed via internal SLF Artifactory (`pypi-local`), not public PyPI.
- **Okta on the SLF API Platform** — governed control-plane calls use `client_secret_post`
  client-credentials, matching the enterprise DPEP Okta pattern.
- **Workload-local Bedrock** — the gateway assumes a cross-account role into the agent's workload
  account to invoke Bedrock; the SDK never signs Bedrock calls itself.
- **AgentCore session ids** MUST be ≥ 33 characters for `InvokeAgentRuntime`.
- **Secrets** MUST live in AWS Secrets Manager / `.github/.env`; never hardcoded or logged.

---

## Transport & Streaming (v0.7.0)

All client calls in v0.7.0 are **request/response over HTTP(S)** — there is **no WebSocket transport
and no client-facing streaming API**:

| Path | Transport | Streaming behaviour |
|------|-----------|---------------------|
| LLM (`GatewayClient`) | Sync HTTP `POST /v1/chat/completions` (buffered `httpx`) | None — the full completion is parsed via `resp.json()`; `stream=true` is **not** supported |
| A2A gateway (`A2AClient.invoke_gateway`) | HTTP A2A JSON-RPC `message/send` | None — single buffered JSON-RPC response (no `message/stream`) |
| A2A runtime (`A2AClient.invoke_runtime`) | AWS `InvokeAgentRuntime` (SigV4, boto3) | None — the full response body is read and returned |
| MCP (`gateway_mcp_session`) | MCP **Streamable HTTP** transport (`streamablehttp_client`) | Request/response tool calls only — the SDK does not expose token/progress streaming |

> **Note:** "Streamable HTTP" in the MCP path is the **transport name** (HTTP POST with optional
> server-sent event framing handled inside the `mcp` library), **not** a WebSocket and **not** an
> SDK-level streaming capability in v0.7.0.
>
> **Next delivery (v0.8.0):** first-class streaming is planned via **SSE** (`stream=true` on the
> existing `POST /v1/chat/completions` HTTP path) across the LLM and A2A paths — see **US-14 → US-18**
> under *Planned — Streaming* and **FR-7**. Uses the existing AgentGateway SSE support (production-ready
> today); no gateway change or new client dependency required. Bidirectional WebSocket is deferred to a
> future phase pending a concrete use case and governance exception sign-off.

---

## Out of Scope (Deferred / Future Phase)

The following appeared in the aspirational D0 / earlier drafts but are **not** in v0.7.0 and are
explicitly out of scope for this D1:

- A unified `ACPClient` façade with `invoke()` / `stream()` / `call_tool()` / `send_task()` methods
- **Bidirectional WebSocket** transport — deferred to a future phase pending a concrete use case
  that SSE cannot serve, a dedicated WS protocol spec, and a governance exception sign-off (see
  *Deferred — Bidirectional WebSocket Streaming* under the Planned Streaming section)

> **Reclassified as Next Delivery (not out of scope):** typed streaming events and SSE streaming
> variants of the LLM/A2A/MCP calls are now **planned for v0.8.0** — see **US-14 → US-18** and
> **FR-7**. They are simply not present in v0.7.0.
- A typed error hierarchy (`PolicyDeniedError`, `RateLimitedError`, `CircuitOpenError`, …) — errors
  currently surface via `httpx` `raise_for_status()`
- Automatic retry middleware for 429/503, session (`X-Session-Id`) propagation, and correlation-id seeding
- Framework adapters (Strands `ACPToolProvider`, LangChain/LangGraph `ACPChatModel` / `ACPToolkit`)
- Internal agentic tool loop (`run()` / `run_stream()`) and sync/async dual-mode variants
- AWS IAM → ACP token-exchange auth and API-key auth (only Okta client-credentials is implemented)
- Gateway-side discovery methods (`discover_tools()` / `discover_models()` / `discover_agents()`) —
  discovery today is via the registry `list_*` reads

---

## Roadmap Requirements (Future Deliveries — v0.8.0+)

> These requirements are **not** implemented in v0.7.0. They capture the agreed enhancement roadmap
> so the design (D2) and task breakdown (D3) have an authoritative source. They are grouped into
> capability tracks. Governance stays **server-side** for every track — the SDK never becomes a
> policy/eval authority; it standardizes how an agent runtime *talks to* the ACP control plane.
>
> **Motivation.** Two ACP deployments (dev EKS control plane and the AgentCore-native workload
> pattern) currently re-implement the same glue — a governed tool-calling loop, MCP↔LLM adapters,
> evaluation submission, telemetry — inside sample code. The harness roadmap **absorbs that glue**
> so consumers depend on one governed SDK, and so the same concepts extend from AWS Bedrock/AgentCore
> to future platforms without rewriting each agent.

### Track E — Evaluation Integration (net-new)

> ACP already runs a consolidated evaluation service (`evaluation-api`, port 8006) that is the
> score **producer/bridge**, while the **registries own the canonical record**
> (`POST /models/{id}/evaluations`, `POST /agents/{id}/evaluation-evidence`). Scores drive governance:
> model sliding-window demotion (`DemotionConfig` window=5, threshold=0.7 → `DEPRECATED`) and agent
> safety gating (`SAFETY_THRESHOLDS` → `none | block | suspend`, suspend fires the kill switch). The
> harness MUST let an external agent runtime submit and run evaluations **through** this service /
> the registries, across multiple frameworks, without hand-rolling the contracts.

#### US-E1: Submit Normalized Evaluation Scores

**As an** agent developer, **I want** to submit a batch of named scores for my agent (or a model),
**So that** they reach ACP governance without me learning the ingest contract.

**Acceptance Criteria**:
- [ ] **Given** a list of `{name, value, model_id?, agent_id?}` scores and a `risk_tier`, **When** `EvaluationClient(settings).submit_scores(...)` is called, **Then** the SDK POSTs to `{evaluation_url}/ingest/scores` with the mandatory `X-Tenant-Id` header and an Okta bearer (scope `evaluation.ingest.crud`) and returns the `IngestResult` (`models_submitted`, `agents_submitted`)
- [ ] **Given** unmapped score names, **When** submitted, **Then** the SDK does not fail the batch (server logs-and-skips per schema `1.1.0`); the SDK surfaces which names were accepted
- [ ] **Given** no `X-Tenant-Id` resolvable, **When** `submit_scores` is called, **Then** the SDK raises a typed `ValidationError` before the network call

#### US-E2: Submit Evaluation Evidence Directly to the Registries

**As an** agent developer needing an auditable evidence record, **I want** to submit evaluation
evidence straight to the owning registry, **So that** the canonical record and lifecycle transition
happen even when the eval-api bridge is bypassed.

**Acceptance Criteria**:
- [ ] **Given** agent scores, **When** `submit_agent_evidence(agent_id, suite, scores, evidence_url?, run_id?)` is called, **Then** the SDK POSTs an `EvaluationEvidenceRequest` to `{agent_registry_url}/agents/{id}/evaluation-evidence`
- [ ] **Given** model scores, **When** `submit_model_evaluation(model_id, evaluator, ...)` is called, **Then** the SDK POSTs an `EvaluationRequest` (quality/safety/latency/cost/overall) to `{model_registry_url}/models/{id}/evaluations`
- [ ] **Given** "goodness" dimensions (e.g. `safety_rate`, `hallucination_rate`), **When** the evidence targets safety gating, **Then** the SDK applies the documented goodness→failure-rate polarity conversion (`1 - g`, clamped) so gates cannot invert
- [ ] **Given** a returned lifecycle impact (`none | block | suspend`, or model `APPROVED`/`EVALUATING`/`DEPRECATED`), **When** the registry responds, **Then** the SDK returns that governance outcome to the caller (does not itself enact it)

#### US-E3: Run a Scorer Suite / Score a Trace

**As an** agent developer, **I want** to trigger an ACP scorer suite for a target and trace,
**So that** governed, CMRM-approved metrics run without me packaging evaluators myself.

**Acceptance Criteria**:
- [ ] **Given** `{target_type, target_id, trace_id, metrics[]}` and a `risk_tier`, **When** `run_scorer(...)` is called, **Then** the SDK POSTs to `{evaluation_url}/scorer/run` (scope `evaluation.scorer.crud`) and returns `{score_ids, overall_score, passed}`
- [ ] **Given** a trace id, **When** `score_trace(...)` is called, **Then** the SDK invokes `{evaluation_url}/scorer/score-trace`
- [ ] **Given** a request for the catalog, **When** `list_metrics()` is called, **Then** the SDK GETs `{evaluation_url}/evaluation/metric-library` and returns the metric catalog (tier, library, integration mode) for metric selection

#### US-E4: Pluggable Local Evaluation Frameworks (OSS)

**As an** agent developer, **I want** to run open-source evaluators locally and forward their scores,
**So that** I can use DeepEval / RAGAS / DeepTeam without bespoke plumbing.

**Acceptance Criteria**:
- [ ] **Given** a DeepEval or RAGAS metric result, **When** an `evaluators` adapter maps it, **Then** the SDK normalizes to the ACP score shape and routes it via US-E1/US-E2
- [ ] **Given** a DeepTeam red-team run (offline batch), **When** its findings are submitted, **Then** they map to the recognized safety metrics (`prompt_injection`, `jailbreak`, `pii_leakage`, `toxicity`, `bias`)
- [ ] **Given** an evaluator extra is not installed, **When** its adapter is used, **Then** a clear `RuntimeError` names the exact extra (e.g. `[deepeval]`, `[ragas]`)

#### US-E5: Managed / SaaS Evaluators (Bedrock, Openlayer, Langfuse)

**As an** agent developer, **I want** to use managed evaluators, **So that** I can rely on Bedrock
model evaluation, Openlayer, or Langfuse-as-judge and still land scores in ACP governance.

**Acceptance Criteria**:
- [ ] **Given** an LLM-as-judge evaluation, **When** the SDK requests judging, **Then** it uses the ACP judge path (cross-account Bedrock judge role `acp-eval-judge`, ExternalId, `{"score","reason"}` contract) rather than signing Bedrock directly
- [ ] **Given** scores written to a Langfuse trace (`create_score(trace_id, name, value, comment)` + `model:`/`agent:`/`tenant:` metadata), **When** the ACP bridge polls, **Then** they reach the registries; the SDK provides the trace/score emission helper and the metadata convention
- [ ] **Given** an Openlayer result, **When** forwarded, **Then** the SDK submits it via US-E1 (the server-side HMAC webhook path remains authoritative for SaaS pushes)

#### US-E6: Evaluation as a Continuous / Offline Gate

**As an** agent developer, **I want** to run online, focused, A/B, and regression evaluations,
**So that** governance feedback (demotion, suspend, golden-dataset gate) is continuous.

**Acceptance Criteria**:
- [ ] **Given** an `EvalContext` (`production_monitoring | focused_evaluation | ab_experiment | regression_test`), **When** scores are submitted, **Then** the SDK tags them so ACP routes them correctly
- [ ] **Given** a `run_id`/trace id, **When** the same evaluation is retried, **Then** submission is idempotent (no double-count)
- [ ] **Given** a golden-dataset regression run, **When** the gate result is fetched, **Then** the SDK surfaces `{baseline, pass_rate, passed, version}`

### Track O — Observability & Guardrails

#### US-O1: Emit OpenTelemetry Traces/Metrics to ACP

**As an** operator, **I want** the SDK to emit OTel spans/metrics for every governed call,
**So that** agent activity is correlated in the ACP observability plane.

**Acceptance Criteria**:
- [ ] **Given** telemetry enabled, **When** any client call runs, **Then** the SDK emits an OTel span (correlation id + `agent_id`) and can export to the ACP `/telemetry/ingest` OTLP path
- [ ] **Given** telemetry disabled (default off / sampling configurable), **When** calls run, **Then** no exporter is required and there is no hard OTel dependency in the core install (behind a `[otel]` extra)

#### US-O2: Client-Side Guardrail Pre-Flight Hooks

**As an** agent developer, **I want** optional input/output guardrail hooks that run alongside the
call, **So that** obvious violations fail fast client-side while the gateway stays authoritative.

**Acceptance Criteria**:
- [ ] **Given** registered input/output guardrail callables, **When** a governed call runs, **Then** they execute (parallel-friendly) and a tripwire raises a typed `GuardrailBlockedError` **before**/around egress
- [ ] **Given** the gateway returns/close-frames a guardrail denial, **When** received, **Then** the SDK raises the same typed `GuardrailBlockedError` carrying reason + correlation id (server remains the authority)

### Track P — Multi-Platform Abstraction

#### US-P1: Platform-Neutral Core

**As a** platform owner running two ACP deployments, **I want** the harness concepts factored into a
platform-neutral core with an AWS binding, **So that** the same governed surface extends beyond AWS.

**Acceptance Criteria**:
- [ ] **Given** the SDK, **When** a consumer targets the neutral core, **Then** LLM egress, registration, MCP, A2A, eval, and telemetry are expressed against provider-agnostic interfaces, with AWS (SigV4/AgentCore/Bedrock) as one binding
- [ ] **Given** a second platform binding is added later, **When** wired, **Then** no change to the consumer-facing façade is required (Liskov-substitutable providers)

#### US-P2: Gateway-Side Discovery

**As an** agent developer, **I want** discovery methods for tools/models/agents,
**So that** I can enumerate governed resources without hand-querying each registry.

**Acceptance Criteria**:
- [ ] **Given** `discover_tools()`, `discover_models()`, `discover_agents()`, **When** called, **Then** the SDK returns clearance-filtered, governed resources (server-side filtering unchanged)

#### US-P3: Framework Adapters

**As an** agent developer using an agent framework, **I want** first-class adapters,
**So that** ACP governance drops into Strands / LangChain / LangGraph without glue.

**Acceptance Criteria**:
- [ ] **Given** Strands, **When** the SDK's `ACPToolProvider` is registered, **Then** governed MCP tools are exposed as Strands tools
- [ ] **Given** LangChain/LangGraph, **When** `ACPChatModel` / `ACPToolkit` are used, **Then** LLM + tools route through the ACP gateway with attribution

### Track G — Developer Ergonomics & Agentic Runtime (SDK pull-ups)

> Several capabilities are currently **re-implemented in the sample** (`acp-agentcore-sample`) and
> SHOULD be absorbed into the SDK: the governed tool-calling loop (`run_governed_turn`), the
> MCP↔OpenAI tool adapters (`to_openai_tools` / `tool_result_text`), the direct-SigV4 MCP client, the
> AgentCore HTTP contract scaffold (`/ping` + `/invocations`), and the AgentCore deploy helper.

#### US-G1: Unified `ACPClient` Façade

**As an** agent developer, **I want** one entrypoint exposing `chat/complete`, `run`, `call_tool`,
`send_task`, and `evaluate`, **So that** I don't wire five clients by hand.

**Acceptance Criteria**:
- [ ] **Given** `ACPClient(settings)`, **When** constructed, **Then** it composes the gateway, registry, A2A, MCP, and evaluation clients behind one governed façade with shared auth/telemetry
- [ ] **Given** the façade, **When** a method is called, **Then** behaviour is identical to the underlying client (façade adds no bypass)

#### US-G2: Typed Error Hierarchy

**As an** agent developer, **I want** typed exceptions, **So that** I can branch on governance
outcomes instead of parsing `httpx` status codes.

**Acceptance Criteria**:
- [ ] **Given** a governed response, **When** it denies/limits/blocks, **Then** the SDK raises `PolicyDeniedError` / `RateLimitedError` / `GuardrailBlockedError` / `AuthenticationError` (all subclassing a common `ACPError`) carrying reason + correlation id

#### US-G3: Retry/Backoff + Session & Correlation Propagation

**As an** agent developer, **I want** automatic retry on `429/503` with backoff plus `X-Session-Id`
and correlation-id propagation, **So that** transient failures and tracing are handled for me.

**Acceptance Criteria**:
- [ ] **Given** a `429`/`503` with `Retry-After`, **When** a call fails, **Then** the SDK retries with bounded exponential backoff and honours `Retry-After`
- [ ] **Given** a session, **When** calls are made, **Then** a stable `X-Session-Id` and per-call correlation id are propagated across LLM/MCP/A2A/eval

#### US-G4: Governed Agentic Loop + Tool Adapters

**As an** agent developer, **I want** `run()` / `run_stream()` and the MCP↔OpenAI tool adapters in the
SDK, **So that** the governed tool-calling loop is standard, not copied per project.

**Acceptance Criteria**:
- [ ] **Given** a system prompt, a prompt, and an MCP session, **When** `run(...)` is called, **Then** the SDK lists tools, converts them (`to_openai_tools`), drives the gateway completion with `tool_choice`, executes tool calls via MCP, feeds results back, and returns `{answer, actions, usage}` with a turn cap
- [ ] **Given** the direct-SigV4 MCP path, **When** a consumer needs runtime-direct tools, **Then** the SDK offers a supported direct-SigV4 MCP client at parity with the gateway path

#### US-G5: AgentCore Runtime Scaffold & Deploy Helper

**As an** agent developer, **I want** an AgentCore HTTP contract scaffold and a deploy helper,
**So that** I don't hand-write the `/ping` + `/invocations` app or the ECR/runtime deploy.

**Acceptance Criteria**:
- [ ] **Given** the scaffold, **When** a consumer builds an AgentCore agent, **Then** the SDK provides a Starlette app factory exposing `GET /ping` + `POST /invocations` on `:8080`
- [ ] **Given** the deploy helper, **When** invoked, **Then** it builds/pushes an ARM64 image (ECR scan-on-push) and creates/updates an AgentCore runtime (VPC network mode) from env-driven config

### Track A — Authentication Extensions

#### US-A1: IAM → ACP Token Exchange & API-Key Auth

**As an** agent developer, **I want** AWS IAM identity exchange and API-key auth in addition to Okta
client-credentials, **So that** workloads authenticate with their native identity.

**Acceptance Criteria**:
- [ ] **Given** an AWS execution role, **When** `IamTokenExchangeProvider` is used, **Then** the SDK exchanges the signed identity for an ACP token (RFC 8693-style) via the gateway
- [ ] **Given** an API key, **When** `ApiKeyAuthProvider` is used, **Then** governed calls present the key per the ACP contract
- [ ] **Given** any provider, **When** tenant context exists, **Then** `X-Tenant-Id` is propagated on all governed calls

---

## Roadmap Functional Requirements (Future Deliveries)

| ID | Requirement | Public symbol(s) | Track |
|----|-------------|------------------|-------|
| FR-8 | Evaluation submission to the eval-api ingest path (`POST /ingest/scores`, `X-Tenant-Id`, scope `evaluation.ingest.crud`) | `EvaluationClient.submit_scores` | E |
| FR-9 | Direct-registry evidence (`/agents/{id}/evaluation-evidence`, `/models/{id}/evaluations`) with goodness→failure-rate polarity | `EvaluationClient.submit_agent_evidence` / `submit_model_evaluation` | E |
| FR-10 | Scorer suite runner + metric catalog (`/scorer/run`, `/scorer/score-trace`, `/evaluation/metric-library`) | `EvaluationClient.run_scorer` / `score_trace` / `list_metrics` | E |
| FR-11 | Pluggable evaluator adapters (DeepEval, RAGAS, DeepTeam) behind extras | `evaluators.*` | E |
| FR-12 | Managed evaluators — Bedrock judge (cross-account `acp-eval-judge`), Langfuse trace/score emission, Openlayer forwarding | `EvaluationClient` + `LangfuseBridge` | E |
| FR-13 | `EvalContext` tagging + idempotent `run_id`/trace-id submission | `EvaluationClient` | E |
| FR-14 | OTel span/metric emission with correlation id → ACP `/telemetry/ingest` (behind `[otel]` extra) | telemetry middleware | O |
| FR-15 | Client-side guardrail pre-flight hooks + typed `GuardrailBlockedError` | guardrail hooks | O |
| FR-16 | Platform-neutral core interfaces with an AWS binding | `acp-harness-core` (split) | P |
| FR-17 | Gateway discovery methods | `discover_tools/models/agents` | P |
| FR-18 | Framework adapters (Strands `ACPToolProvider`, LangChain/LangGraph `ACPChatModel`/`ACPToolkit`) | adapters | P |
| FR-19 | Unified `ACPClient` façade | `ACPClient` | G |
| FR-20 | Typed error hierarchy (`ACPError` + subclasses) | errors | G |
| FR-21 | Retry/backoff (429/503) + `X-Session-Id` + correlation-id propagation | HTTP middleware | G |
| FR-22 | Governed agentic loop `run()`/`run_stream()` + MCP↔OpenAI adapters + direct-SigV4 MCP client | `run`, `to_openai_tools`, `tool_result_text` | G |
| FR-23 | AgentCore HTTP scaffold (`/ping`+`/invocations`) + deploy helper (ECR ARM64 + create/update runtime) | scaffold + deploy helper | G |
| FR-24 | IAM→ACP token exchange + API-key auth providers | `IamTokenExchangeProvider`, `ApiKeyAuthProvider` | A |

> **Dependencies at a glance:** Track E and Track O build on the Track G façade + Track A auth
> foundation. SSE streaming (US-14→18 / FR-7) has **no gateway blocker** — the existing AgentGateway
> already serves SSE on `POST /v1/chat/completions` with `stream=true`. Bidirectional WebSocket
> streaming (deferred) remains gated on EACPP-211 + a governance exception. Track P core split is
> a prerequisite for the framework adapters. The evaluation cross-account judge role
> (`acp-eval-judge`) is **already provisioned** by [`acp-aws-service-catalog`](https://bitbucket.sunlifecorp.com/projects/T1KACP/repos/acp-aws-service-catalog/browse); no new catalog role is required for the roadmap (verify-only).

---

## Traceability

| Requirement | D0 Success Criteria | Public symbol |
|-------------|---------------------|---------------|
| US-1, FR-6 | Zero-config onboarding | `ACPSettings` |
| US-2/US-3/US-4, FR-1 | Governed LLM egress | `GatewayClient`, `ChatResult` |
| US-5/US-6/US-7/US-8, FR-2 | Registration + governance attribution | `RegistryClient` |
| US-9, FR-3 | Transparent token management | `OktaAuthProvider`, `OktaCredentials` |
| US-10, FR-5 | Governed MCP tool invocation | `gateway_mcp_session`, `gateway_mcp_url` |
| US-11/US-12, FR-4 | A2A task delegation | `A2AClient` |
| US-13, NFR-1/NFR-3 | Minimal dependency footprint | extras: `aws`, `mcp` |
| US-14/US-15, FR-7 | LLM streaming over SSE *(planned v0.8.0)* | `GatewayClient.stream()` / `stream_sync()`, `ChatChunk` |
| US-16, FR-7 | A2A task streaming over SSE *(planned v0.8.0)* | `A2AClient.send_task_stream()` |
| US-17, FR-7 | MCP streaming progress *(planned v0.8.0)* | `gateway_mcp_session()` (existing, SSE via `mcp` library) |
| US-18, FR-7 | SSE stream lifecycle + typed errors *(planned v0.8.0)* | `StreamDisconnectedError`, `GuardrailBlockedError` |

---

## References

- Source repo: [`acp-harness-sdk`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-harness-sdk/browse) (v0.7.0)
- D0 Discovery: [d0-discovery.md](d0-discovery.md)
- Architecture & Integration Guide: [README.md](README.md)
- AI Gateway D2 Design: [../ai-gateway/d2-design.md](../../ai-gateway/d2-design.md)
- Agent Registry D2 Design: [../agent-registry/d2-design.md](../../agent-registry/d2-design.md)
- MCP Registry D2 Design: [../mcp-registry/d2-design.md](../../mcp-registry/d2-design.md)
- Model Registry D2 Design: [../model-registry/d2-design.md](../../model-registry/d2-design.md)
- Related Epic: [EACPP-211](https://sunlife.atlassian.net/browse/EACPP-211) (AI Gateway)
