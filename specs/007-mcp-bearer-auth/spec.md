# Spec: Bearer-token auth for MCP endpoints, plus gateway MCP route

Status: Draft

## Problem / Why

`/agent/mcp` is public and anonymous. The AgentCore gateway (`project1-dev-agent-gateway`) uses `AWS_IAM` auth, which VS Code and most MCP clients cannot sign natively. Both MCP surfaces should be reachable through API Gateway with a simple `Authorization: Bearer <token>` header.

## User stories

- As an MCP client user (e.g. VS Code), I want to call the agent MCP endpoint with a Bearer token so that only authorised callers can use it.
- As an MCP client user, I want the AgentCore gateway tools exposed at an API Gateway MCP URL that accepts a Bearer token, without needing SigV4 signing.
- As an operator, I want the token stored in Secrets Manager (not in code or tfvars) and rotatable without redeploying Lambdas.

## API contract

| Method | Path | Request | Success | Errors |
| ------ | ---- | ------- | ------- | ------ |
| ANY | /agent/mcp | Existing Streamable HTTP MCP contract (spec 003) plus `Authorization: Bearer <token>` | Unchanged from spec 003 | 401 missing/malformed header; 403 invalid token |
| ANY | /gateway/mcp | Streamable HTTP MCP JSON-RPC plus `Authorization: Bearer <token>` | Request is forwarded to the AgentCore gateway MCP endpoint (SigV4-signed by the Lambda's role); gateway response returned unchanged | 401 missing/malformed header; 403 invalid token; 502 gateway failure (no internal details) |

Both routes use the same Lambda authorizer. `/agent/invoke`, the frontend routes, and `/hello` are not changed.

## Acceptance criteria

- AC1: A request to `/agent/mcp` or `/gateway/mcp` without a Bearer header is rejected with 401 and never reaches the backend Lambda.
- AC2: A request with an incorrect token is rejected with 403; comparison is constant-time.
- AC3: A request with the correct token on `/agent/mcp` behaves exactly as in spec 003.
- AC4: An MCP client can initialize against `/gateway/mcp`, list the gateway tools (e.g. `hello` target), and call them.
- AC5: The `/gateway/mcp` Lambda has its own least-privilege role: only `bedrock-agentcore:InvokeGateway` on the specific gateway ARN, plus logs.
- AC6: The token lives in a Secrets Manager secret (KMS-encrypted); Terraform creates the secret container but not its value. Tokens and the Authorization header are never logged.
- AC7: Rotating the secret value takes effect without Terraform changes (authorizer caches the value for at most 5 minutes).
- AC8: Existing demo rate limit (2 rps, burst 5) applies to `/gateway/mcp`.
- AC9: Documentation shows a working VS Code `mcp.json` using `type: "http"` with an `Authorization` header sourced from an input prompt.
- AC10: Authorizer and gateway-proxy handlers have unit tests; `fmt`, `validate`, `tflint`, `checkov` pass.

## Non-functional

- Auth: single shared static Bearer token (no per-user identity, no expiry; rotation is manual).
- Authorizer: API Gateway HTTP API Lambda authorizer, simple-response format, result caching of 5 minutes keyed on the Authorization header.
- Latency: authorizer adds one cached Secrets Manager read; proxy adds one hop to the gateway.
- Python 3.12, one Lambda per endpoint, explicit log groups with retention.

## Out of scope

- Per-user tokens, JWT/Cognito/OIDC, token expiry or automatic rotation.
- Changing the AgentCore gateway's own `AWS_IAM` authorizer.
- Auth on `/agent/invoke`, frontend, or `/hello`.
- Streaming/server-initiated MCP notifications on `/gateway/mcp`.

## Open questions

- None. Decisions recorded: scope = both routes; token type = static secret via Lambda authorizer; new path `/gateway/mcp`.
