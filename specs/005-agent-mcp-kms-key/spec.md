# Spec: Customer-managed KMS key for MCP session table

Status: Draft

## Problem / Why

Terraform reports a KMS `NotFoundException` for the existing `agent_mcp_sessions` DynamoDB table, referencing a customer-managed key ARN that no longer resolves. The table currently enables server-side encryption without declaring a key in its Terraform configuration. Operators need a defined, reviewable recovery that gives the table a valid customer-managed key without silently discarding active session data or changing unrelated infrastructure.

## User stories

- As an operator, I want the MCP session table encrypted with a valid, Terraform-managed customer-managed key so that table encryption does not depend on a missing key.
- As an operator, I want the key dedicated to the MCP session table and protected against accidental loss so that unrelated resources and session data are not affected.
- As an MCP user, I want the existing session table and its records preserved during key recovery so that the change does not silently terminate active sessions.

## API contract

Not applicable. This change affects encryption configuration for the existing DynamoDB table only; it does not change API behavior.

## Acceptance criteria

- AC1: The MCP session table uses a valid customer-managed KMS key in the same AWS account and `eu-west-1` region as the table.
- AC2: The key is managed through Terraform, is dedicated to the MCP session table, and has an identifiable alias.
- AC3: The key's automatic rotation is enabled and its deletion is subject to a recovery window.
- AC4: The recovery plan does not destroy or replace the existing MCP session table, disable TTL, change the table schema, or discard existing session records.
- AC5: The Lambda endpoint retains only the DynamoDB permissions needed for session operations; the change does not grant it broad KMS permissions or access to unrelated keys.
- AC6: The Terraform plan shows the new key and an in-place table encryption update, with no changes to the Terraform backend/state bucket, other tables, routes, or endpoint behavior.
- AC7: If Terraform cannot produce a safe in-place plan because the missing key prevents reading or updating the existing table, implementation stops and reports the required recovery decision; it does not work around the issue by editing state, deleting the table, or applying direct AWS mutations.
- AC8: No Terraform apply or destructive AWS operation occurs without separate explicit user approval.

## Non-functional

- Encryption at rest for MCP session data must remain enabled throughout the approved recovery.
- The key must be scoped to the MCP table and region, and key deletion must not be immediate.
- Existing session expiry, isolation, logging, and API throttling behavior remain unchanged.

## Out of scope

- Restoring or changing the state of the missing KMS key.
- Replacing or deleting the MCP session table or intentionally expiring all its sessions.
- Changes to the Terraform backend, state bucket, other DynamoDB tables, API routes, or Lambda behavior.
- Applying Terraform or performing direct AWS changes.

## Open questions

- None.
