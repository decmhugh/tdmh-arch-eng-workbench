# ACP AWS Harness SDK — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: EACPP-TBD

## Problem Statement

Teams building AI agents on AWS Bedrock AgentCore — using any framework (Strands, LangGraph, CrewAI) — have no standardized way to invoke downstream services (MCP Servers, LLMs, A2A agents) through the ACP Central AI Gateway. Today, each consuming team must independently implement:

- OAuth2/JWT token acquisition and refresh against Okta / Azure (Entra)
- Agent configuration retrieval (approved models, tools, A2A permissions) at runtime
- HTTP request construction for the gateway's endpoints
- Prompt dispatch with available tool context for model selection and routing
- SSE stream parsing for LLM and MCP streaming responses
- A2A (Agent-to-Agent) protocol handling for delegating tasks to peer agents
- Tool invocation loop (LLM decides tool → execute via gateway → return result → final LLM pass)
- Retry logic with `Retry-After` header awareness (429/503)
- Session propagation (`X-Session-Id` header management)
- Correlation ID seeding (`x-correlation-id`, `x-traceability-id`)
- Error classification (distinguishing policy denials from rate limits from circuit breaker states)

This results in duplicated code across teams, inconsistent error handling, missed governance headers, and increased onboarding time for new agent developers.

## Opportunity

A thin, boto3-style SDK (`acp-harness-sdk`) gives consuming teams a zero-boilerplate interface to the Central AI Gateway. Teams `pip install`, configure credentials, and call typed methods — no HTTP protocol knowledge required. The SDK is **framework-agnostic** and works with any Python-based agent deployed to AgentCore (Strands, LangGraph, CrewA). All governance enforcement (policy evaluation, rate limiting, kill switches, guardrails, token exchange, routing) remains server-side in the Central AI Gateway, ensuring the SDK cannot bypass controls.

The gateway acts as the **single control point** for all agent interactions — the agent runtime communicates exclusively with the gateway, which mediates access to registries, LLM providers, MCP servers, and peer agents.

**Phase 1 assumption**: Agents are **pre-registered** in the Agent Registry via CI/CD or admin UI before runtime. Self-registration is out of scope for Phase 1.

Key outcomes:
- **Onboarding time** drops from days to hours (configure + call)
- **Governance compliance** is guaranteed (all traffic flows through gateway)
- **Consistency** across all AWS-hosted agents regardless of framework (same auth, retry, session patterns)
- **Streaming support** is native (async iterators for LLM tokens, MCP progress, and A2A task updates)
- **Protocol coverage** is complete — MCP (tool calls), LLM (inference), and A2A (agent-to-agent delegation) all via a single SDK

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| FDES Engineering Team | Implementers | SDK maintainability, test coverage, release cadence |
| Platform Architecture | Reviewers | Architectural alignment with AI Gateway D2, no governance bypass |
| Product Owner | Approver | Business value, adoption metrics, time-to-market |
| AI4Ops / Consumer Teams | Primary consumers | Ease of use, documentation quality, boto3-like familiarity, framework-agnostic |
| Enterprise Governance | Stakeholder | All agent traffic governed — SDK cannot circumvent controls |
| AWS Cloud Platform Team | Stakeholder | AgentCore integration, IAM role bridge compatibility |

## Scope

### In Scope

- Python SDK package (`acp-harness-sdk` on internal SLF Artifactory)
- Auth providers: OAuth2 client credentials, JWT bearer, API Key, AWS IAM → ACP token exchange
- Agent config client: `get_config()` — fetches agent's full configuration (approved models, MCP tools, A2A permissions) from gateway at startup
- MCP client: `call_tool()`, `call_tool_stream()`, `discover_tools()`
- LLM client: `invoke()`, `stream()`, `discover_models()`
- A2A client: `send_task()`, `send_task_stream()`, `discover_agents()`
- Agentic loop support: prompt dispatch with tool context → LLM response / tool decision → tool execution → final LLM pass
- Middleware stack: retry (429/503), session propagation, correlation ID seeding
- SSE streaming parser with typed events (TokenChunk, DoneChunk, ProgressEvent, TaskStatusEvent, ErrorEvent)
- Typed error hierarchy mapping gateway error responses to catchable exceptions
- Configuration hierarchy: explicit params → env vars → AWS Secrets Manager → config file → defaults
- AWS AgentCore environment auto-detection (IAM role, region, agent ID)
- Framework adapters: Strands (`ACPToolProvider`), LangChain/LangGraph (`ACPChatModel`, `ACPToolkit`), generic async/sync interface for custom frameworks
- Sync + async dual-mode interface (httpx-based transport)
- Examples and developer documentation

### Out of Scope

- Agent self-registration (Phase 1 assumes pre-registered agents via CI/CD or admin UI)
- Governance workflows (approval, classification — done via UI/CI/CD)
- Registry write operations (MCP server registration, model registration, tool classification)
- Gateway-side logic (no policy evaluation, no routing, no token exchange in SDK)
- Java, TypeScript, or Rust SDK ports (future phases — Python first)
- CLI companion tool (future phase)
- Direct registry communication (all runtime calls go through AI Gateway)

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Agent config retrieval | SDK fetches full agent config (models, tools, A2A permissions) from gateway | get_config() returns typed AgentConfig in < 3 lines of code |
| MCP tool invocation | SDK constructs valid request, receives typed response | call_tool() → ToolResult in < 5 lines of code |
| LLM invocation with tool context | SDK sends prompt + tool context, handles tool decision loop | invoke() with tools returns final response after tool execution |
| LLM streaming | SDK parses SSE stream into typed async iterator | stream() yields TokenChunk events without manual parsing |
| A2A task delegation | SDK sends task to peer agent, receives typed result | send_task() → TaskResult with status tracking |
| A2A streaming | SDK streams task progress from peer agent | send_task_stream() yields TaskStatusEvent updates |
| Agent discovery | SDK discovers available peer agents (clearance-filtered) | discover_agents() returns routable agent list |
| Auth token management | Token acquired, cached, auto-refreshed transparently | Zero token-related code in consuming agent |
| Retry compliance | SDK retries on 429 with Retry-After, 503 with backoff | No manual retry logic needed |
| Session management | X-Session-Id propagated on subsequent calls | Multi-turn conversations work without explicit session handling |
| Error classification | Gateway errors mapped to typed exceptions | Teams catch PolicyDeniedError, not generic HTTPError |
| Onboarding time | Time from pip install to first successful invocation | < 30 minutes with documentation |
| Adoption | Consumer teams using SDK in production | 3+ teams within 3 months of release |
| Package size | Minimal dependency footprint | ≤ 5 runtime dependencies (httpx, pydantic, etc.) |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|----------------|------|------|
| AI Gateway D2 design stable | ai-gateway | Hard | SDK must align with gateway API contract |
| AI Gateway `POST /invoke` endpoint live | ai-gateway | Hard | SDK is useless without a running gateway |
| AI Gateway agent config endpoint | ai-gateway | Hard | SDK must fetch agent config (models, tools, A2A permissions) from gateway at startup |
| AI Gateway `GET /registry/services` endpoint | ai-gateway | Soft | Discovery can be deferred; services invokable by name |
| Agent Registry `GET /registry/services?type=Agent` endpoint | agent-registry | Soft | Required for `discover_agents()` and A2A routing; agents callable by name as fallback |
| Okta OAuth2 tenant configured for agents | IAM/Security team | Hard | Auth provider needs a token endpoint |
| AWS IAM → ACP token exchange mechanism | ACP Engineering + AWS team | Soft | Fallback: teams use direct OAuth2 |
| IAM cross-account trust (gateway → workload Bedrock) | Cloud Platform + Workload team | Hard | Gateway must AssumeRole into workload account to invoke Bedrock; trust policy required per workload |
| Model Registry stores workload-specific Bedrock endpoints | model-registry | Hard | Gateway resolves model endpoint per workload account, not a shared Bedrock |
| Internal PyPI / Artifactory repository | DevOps | Soft | Distribution mechanism for enterprise |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gateway API changes break SDK | Medium | High | Version SDK to gateway API version; integration tests in CI |
| Teams bypass SDK and call gateway directly | Low | Low | Not a security risk (gateway enforces everything); SDK is convenience |
| AWS IAM → ACP token exchange complexity | Medium | Medium | Support direct OAuth2 as fallback; IAM bridge is Phase 2 |
| SSE streaming edge cases (disconnects, partial events) | Medium | Medium | Robust parser with keep-alive handling; integration test suite |
| Dependency conflicts in consumer environments | Low | Medium | Minimal deps; pin ranges not exact versions |
| SDK adoption resistance ("we'll just use requests") | Low | Medium | Clear value demo; mandatory for supported agent pattern |
| A2A protocol instability (Google A2A spec in flux) | Medium | Medium | Abstract A2A behind typed methods; gateway handles protocol specifics; SDK only constructs `POST /invoke` with target agent |

## Open Questions

- [ ] Should the SDK support synchronous-only mode (no async) for simpler agent scripts?
- [ ] Should the SDK embed OpenTelemetry spans for client-side observability, or defer to the gateway's telemetry?
- [ ] How are workload-specific Bedrock IAM role ARNs provisioned? (Terraform module? Manual per-workload onboarding?)
- [x] ~~Should A2A streaming use SSE (like LLM/MCP) or a separate WebSocket transport?~~
  **Resolved (Sep 2026):** SSE for all paths. WebSocket deferred to a future phase pending a
  concrete bidirectional use case and governance exception sign-off (see D1
  *Deferred — Bidirectional WebSocket Streaming*).
- [ ] Should the SDK manage the full agentic tool loop (LLM → tool decision → execute → final LLM) internally, or expose it as composable steps?
- [ ] What is the agent config refresh strategy? (Fetch once at startup? Poll interval? Gateway push on config change?)

## References

- AI Gateway D2 Design: [specs/ai-gateway/d2-design.md](../../ai-gateway/d2-design.md)
- AI Gateway D1 Requirements: [specs/ai-gateway/d1-requirements.md](../../ai-gateway/d1-requirements.md)
- Agent Registry D2 Design: [specs/agent-registry/d2-design.md](../../agent-registry/d2-design.md)
- MCP Registry D2 Design: [specs/mcp-registry/d2-design.md](../../mcp-registry/d2-design.md)
- Model Registry D2 Design: [specs/model-registry/d2-design.md](../../model-registry/d2-design.md)
- Source Repo: `acp-harness-sdk` (to be created)
- Related Epics: [EACPP-211](https://sunlife.atlassian.net/browse/EACPP-211) (AI Gateway), [EACPP-37](https://sunlife.atlassian.net/browse/EACPP-37) (Agent Registry)
