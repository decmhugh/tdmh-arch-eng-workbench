# Tasks: Bearer-token auth for MCP endpoints, plus gateway MCP route

- [ ] T1 Write failing tests for AC1, AC2, AC6, AC7 (`tests/test_mcp_authorizer.py`: missing/malformed header, wrong token, correct token, cache TTL, no token in logs)
- [ ] T2 Write failing tests for AC4, AC5 behaviour (`tests/test_gateway_mcp.py`: SigV4 signing, header/body passthrough, 502 on upstream failure, Authorization header not forwarded or logged)
- [ ] T3 Implement `src/mcp_authorizer/handler.py`
- [ ] T4 Implement `src/gateway_mcp/handler.py`
- [ ] T5 [P] Add `authorizer_id` support to `infra/modules/lambda_endpoint` (variable and route)
- [ ] T6 [P] Add `infra/mcp_auth.tf` (KMS key, secret, authorizer Lambda, permission, API authorizer)
- [ ] T7 Add `infra/gateway_mcp.tf` (IAM policy and `module "gateway_mcp"`)
- [ ] T8 Apply the authorizer to `agent_mcp`; add `/gateway/mcp` throttling and stage `depends_on` in `infra/main.tf`; add outputs
- [ ] T9 Document the VS Code `mcp.json` example and the secret setup command (AC9)
- [ ] T10 Run `terraform fmt`, `validate`, `tflint`, `checkov`, `pytest tests`
- [ ] T11 Review `terraform plan -var-file=env/dev.tfvars` with user; stop before `apply`
- [ ] T12 After approved `apply`: user sets the secret value, then smoke-test 401, 403, and `/gateway/mcp` tool listing from VS Code
