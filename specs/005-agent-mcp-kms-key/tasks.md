# Tasks: Customer-managed KMS key for MCP session table

- [x] T1 Add a dedicated Terraform-managed symmetric KMS key and alias for the MCP session table, with automatic rotation, a 30-day deletion window, and destruction protection (AC1-AC3).
- [x] T2 Configure the existing MCP session table to use that key without changing its identity, schema, TTL, or existing records; keep Lambda permissions unchanged (AC1, AC4, AC5).
- [ ] T3 Run Terraform fmt, backend-disabled init and validate, tflint, and checkov; review the key policy and required Terraform deployment permissions for least privilege (AC2, AC3, AC5).
- [ ] T4 Run the focused MCP tests and project pytest suite to verify session behavior remains unchanged (AC4, AC5).
- [ ] T5 Generate and inspect a Terraform plan; require an in-place table encryption update and no replacement, data loss, backend/state, route, or unrelated-resource changes (AC4, AC6, AC8).
- [ ] T6 If refresh or planning is blocked by the missing old key, stop without editing state, replacing the table, or directly mutating AWS; report the blocker and request a recovery decision (AC7, AC8).
