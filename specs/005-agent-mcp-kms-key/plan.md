# Plan: Customer-managed KMS key for MCP session table

Spec: ./spec.md

## Design

- Add a symmetric encryption KMS key and descriptive alias in `eu-west-1`, managed by Terraform and dedicated to the MCP session table.
- Enable automatic key rotation, use a 30-day deletion window, and apply `prevent_destroy` so ordinary Terraform plans cannot silently remove the key.
- Configure the existing `aws_dynamodb_table.agent_mcp_sessions` server-side encryption to use the new key ARN. Keep the table resource, name, schema, TTL, and session items unchanged.
- Do not change Lambda behavior, API Gateway routes, or session-table data permissions. DynamoDB performs encryption transparently; the Lambda receives no direct KMS permissions.
- Use the provider's account-delegating default key policy so key permissions remain controllable by scoped IAM policies. DynamoDB service access is through its managed grants. Do not add broad service principals or unrestricted key-use permissions.
- If Terraform refresh or planning fails because the old key cannot be resolved, stop. Do not edit state, delete/recreate the table, or issue direct AWS mutations to bypass the failure. Report the blocker and request a separate recovery decision.

## IAM (least privilege)

| Principal | Action | Resource | Justification |
| --------- | ------ | -------- | ------------- |
| Terraform deployment principal | KMS key administration and grant-management actions required by the approved table-key configuration | The dedicated MCP session key | Create and manage the key, and allow DynamoDB to use it for the table |
| Agent MCP Lambda | Existing `dynamodb:GetItem`, `PutItem`, `UpdateItem`, `DeleteItem` | Existing MCP session table | Preserve session lifecycle access; no direct KMS calls |

No wildcard key-use policy or additional Lambda KMS permissions are planned. Validate the required deployment-principal permissions against the generated plan and AWS provider behavior before implementation is considered complete.

## Terraform changes

- Add the dedicated `aws_kms_key` and `aws_kms_alias` in `infra/agent_mcp.tf` or a focused `infra/agent_mcp_kms.tf`.
- Add `kms_key_arn` to the existing DynamoDB table's `server_side_encryption` block.
- Do not modify `backend.tf`, state resources, the table identity/schema/TTL, Lambda IAM, or any other endpoint.

## Validation

- Run `terraform fmt -recursive`, `terraform init -backend=false`, `terraform validate`, `tflint --chdir=infra`, and `checkov -d infra`.
- Run the existing focused MCP tests and the project pytest suite to check that application/session behavior remains unchanged.
- Generate and inspect the Terraform plan. It must show key and alias creation plus an in-place encryption update for the current table, with no table replacement, data deletion, backend changes, or unrelated resource changes.
- If the current remote table cannot be refreshed or safely updated due to the missing key, stop and report the blocker; do not apply or perform direct AWS changes.
- Never run `terraform apply` or destroy.

## Constitution check

- [x] One Lambda per endpoint: no endpoint or Lambda is added or changed.
- [x] Least-privilege IAM: the Lambda receives no direct KMS access; key use is scoped to this table.
- [x] No secrets in repo: no credentials or key material are stored.
- [x] Log group with retention: existing logging resources remain unchanged.
- [x] Infrastructure as code only: the key and table configuration remain Terraform-managed.
- [x] Human review: inspect the plan; no apply without separate explicit approval.
- [x] State safety: no backend or state resource changes; never edit state to bypass the missing key.

## Risks / alternatives

- **Risk:** Terraform may fail refreshing the existing table because DynamoDB reports the missing key. **Mitigation:** stop at planning and report the exact blocker; do not replace the table or mutate AWS directly.
- **Risk:** A key policy that omits needed DynamoDB grant operations can make table encryption unusable. **Mitigation:** use the provider's account-delegating policy and verify that DynamoDB can manage its table-scoped grants without broad key-use permissions.
- **Risk:** Removing a key would make encrypted data inaccessible. **Mitigation:** enable rotation, configure a 30-day deletion window, and prevent Terraform destruction.
- **Alternative:** Use an AWS-owned key or restore the old customer-managed key. Not selected; the approved spec requests a new customer-managed key.
