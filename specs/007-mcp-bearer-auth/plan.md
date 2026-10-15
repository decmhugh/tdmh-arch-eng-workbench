# Plan: Bearer-token auth for MCP endpoints, plus gateway MCP route

Spec: ./spec.md

## Design

- **Authorizer Lambda** `src/mcp_authorizer/handler.py` (`handler.lambda_handler`, python3.12). Receives the HTTP API v2 simple-response event, reads `Authorization`, requires the `Bearer ` prefix, fetches the shared secret from Secrets Manager (module-level cache, 300 s TTL), compares with `hmac.compare_digest`, returns `{"isAuthorized": bool}`. Not an endpoint, so it is defined directly in `infra/mcp_auth.tf` rather than through the `lambda_endpoint` module.
- **Gateway proxy Lambda** `src/gateway_mcp/handler.py`, route `ANY /gateway/mcp`, via the `lambda_endpoint` module. Forwards the request body and the MCP headers (`content-type`, `accept`, `mcp-session-id`, `mcp-protocol-version`) to `GATEWAY_MCP_URL`, SigV4-signed (service `bedrock-agentcore`) with botocore from the Lambda runtime and `urllib`. Returns status, body and MCP headers unchanged. Upstream or network failures return a generic 502. Never forwards or logs the incoming `Authorization` header.
- **Auth wiring**: one `aws_apigatewayv2_authorizer` (type `REQUEST`, payload 2.0, simple responses, identity source `$request.header.Authorization`, TTL 300 s). The `lambda_endpoint` module gains optional `authorizer_id` (default `null`); when set, the route uses `authorization_type = "CUSTOM"`. It is applied to `agent_mcp` and `gateway_mcp` only.
- **Rate limit**: add a `ANY /gateway/mcp` route_settings block (2 rps, burst 5) in `infra/main.tf`, and add `module.gateway_mcp` to the stage `depends_on`.
- Environment variables:
  - Authorizer: `TOKEN_SECRET_ARN`, `LOG_LEVEL`.
  - Gateway proxy: `GATEWAY_MCP_URL` (from `aws_bedrockagentcore_gateway.agent.gateway_url`), `AWS_REGION` (provided by Lambda), `LOG_LEVEL`.
- Data stores / AWS services: Secrets Manager secret (value set out of band) encrypted by a dedicated KMS key; API Gateway HTTP API authorizer; AgentCore gateway.
- Docs: `docs/architecture-workflow.md` or `README.md` gets the VS Code `mcp.json` example and the `aws secretsmanager put-secret-value` command.

## IAM (least privilege)

| Role | Action | Resource | Justification |
| ---- | ------ | -------- | ------------- |
| authorizer | `secretsmanager:GetSecretValue` | the token secret ARN | Read the shared token |
| authorizer | `kms:Decrypt` | the token KMS key ARN | Secret is CMK-encrypted |
| authorizer | `logs:CreateLogStream`, `logs:PutLogEvents` | its log group | Logging |
| gateway_mcp | `bedrock-agentcore:InvokeGateway` | `aws_bedrockagentcore_gateway.agent.gateway_arn` | Sign and forward to the gateway |
| gateway_mcp | logs (module default) | its log group | Logging |
| API Gateway | `lambda:InvokeFunction` | the authorizer function, source ARN scoped to this API's `authorizers/<id>` | Authorizer invocation |

No `*` actions or resources. `agent_mcp` permissions are unchanged.

## Terraform changes

- New `infra/mcp_auth.tf`: KMS key plus alias (rotation on, `prevent_destroy`), `aws_secretsmanager_secret` (no version, so no value in state or repo), authorizer Lambda (archive zip, role, policy, log group), `aws_lambda_permission`, `aws_apigatewayv2_authorizer`.
- New `infra/gateway_mcp.tf`: IAM policy document and `module "gateway_mcp"`.
- `infra/modules/lambda_endpoint`: add `authorizer_id` variable (default `null`); route sets `authorization_type` and `authorizer_id` conditionally.
- `infra/agent_mcp.tf`: pass `authorizer_id`.
- `infra/main.tf`: throttling block and `depends_on` for `/gateway/mcp`.
- `infra/outputs.tf`: `gateway_mcp_url`, `agent_mcp_url`, `mcp_token_secret_arn`.
- Tests (written first): `tests/test_mcp_authorizer.py`, `tests/test_gateway_mcp.py`.
- Checkov: skip `CKV2_AWS_57` (automatic rotation) on the secret, with the justification that the token is a manually rotated shared secret (spec out of scope).
- Deployment note: after `apply`, the operator sets the secret value out of band. Until then the authorizer fails closed and returns 403.
- `apply` requires explicit user approval after the `plan` review.

## Constitution check

- [x] One Lambda per endpoint (`gateway_mcp` has its own Lambda; the authorizer is a separate non-endpoint function)
- [x] Least-privilege IAM
- [x] No secrets in repo (value set out of band; secret not managed by a Terraform version resource)
- [x] Log group with retention (the module provides one; the authorizer defines its own with `retention_in_days`)
- [x] Test-first, structured JSON logs, no tokens or headers logged

## Risks / alternatives

- Static shared token has no per-user identity or expiry; mitigated by manual rotation and the 5-minute cache.
- The authorizer cache keys on the Authorization header, so a rotated-out token can stay valid for up to 5 minutes (accepted in AC7).
- The proxy is a buffered request/response: no SSE streaming, and the 29 s API Gateway integration limit applies. The spec lists streaming as out of scope.
- Alternative considered: a Cognito/JWT authorizer (no Lambda, per-user), rejected by the user in favour of a static secret.
- Alternative: switching the AgentCore gateway to a JWT authorizer and skipping the proxy. It would need a token issuer and gives no single front door, so it was not chosen.
- Adding the authorizer to `agent_mcp` breaks existing anonymous clients, including any frontend calling `/agent/mcp`; the spec states this is intended.
