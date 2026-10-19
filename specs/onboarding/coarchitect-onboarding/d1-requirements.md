# CoArchitect Onboarding — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **Epic**: see `spec.yaml`
>
> Builds on [D0 Discovery](d0-discovery.md). Scope is the **dev Luminate install** only.

## User Stories

### US-1: Project Owner controls access

**As** Razi Chaudhry, the CoArchitect business owner,
**I want** to be Owner of a CoArchitect project in Luminate,
**so that** I decide who on my team can act in it, without raising a request each time.

**Acceptance Criteria:**
- [x] Razi holds the **Owner** role on project `CoArchitect`, minted by project creation
- [x] Razi can create individual role bindings on the project (`iam.role_binding.create` = ALLOW)
- [ ] Razi has granted at least one binding himself, end to end, in the portal

### US-2: Tech lead can do all development work

**As** Tony Xu, CoArchitect tech lead,
**I want** admin rights on the project,
**so that** I can register, deploy, authorise and credential CoArchitect's agents without
waiting on the Owner or the ACP Product Team.

**Acceptance Criteria:**
- [x] ALLOW on agent/model/MCP create, deployment create, credential generation and
      **access-policy create** at project scope
- [ ] Tony registers and deploys the first agent (D3 T9) and issues its credential (T11)

### US-3: Members can build

**As** Partho Mondal or Anirban Ukil,
**I want** to be a member of the project,
**so that** I can register and update CoArchitect's agents, models and deployments.

**Acceptance Criteria:**
- [x] ALLOW on create of agents, models, MCP servers and deployments in `CoArchitect`
- [x] deny on delete, credential generation, access-policy create and IAM grants — those stay
      with the Owner and the Administrator
- [ ] Both have signed in and see the project (D3 T2)

### US-4: CoArchitect calls its model through the gateway

**As** the CoArchitect workload in its Dev environment,
**I want** to reach an approved Bedrock model through the ACP Dev gateway with my own credential,
**so that** every call is authorised, audited and costed against CoArchitect.

**Acceptance Criteria:**
- [ ] A call returns 200 through `/llm/v1/chat/completions` on the Dev gateway
- [ ] The audit trail shows `gateway.llm.authorize`=allow and `gateway.llm.access`=success for it
- [ ] The trace and usage are attributed to project `CoArchitect`

## Functional Requirements

### FR-1: Tenancy

Folder **Enterprise Architecture** at organization level, holding project **CoArchitect**.
Owner is set by `ProjectService.create(owner=)` — the only supported path; the role-binding
service refuses the Owner role.

### FR-2: Role mapping

| Person | Role | Scope | Why this role |
|---|---|---|---|
| Razi Chaudhry | **Owner** | project | Owns the project and its access |
| Tony Xu | **Administrator** | project | "All development work" needs **access-policy create**, which no per-type Administrator and not Editor carry. Only Owner and Administrator do. |
| Partho Mondal | **Editor** | project | Build without delete, credentials, policy or IAM |
| Anirban Ukil | **Editor** | project | As above |

Grants are to **individuals**, not a group: an Owner can create individual bindings but holds no
`iam.user_group.*`, so a group would route every future joiner back to the ACP Product Team.

### FR-3: Pre-provisioning

A member who has never signed in is pre-created (lowercase email, verified primary
`EmailAddress`) so the binding can exist before first login. Safe only while
`SOCIALACCOUNT_EMAIL_AUTHENTICATION` and `..._AUTO_CONNECT` are both `True` — re-checked
2026-10-01, both `True`.

### FR-4: Baseline read

Every member also holds the dev install's baseline **Viewer @ organization** (applied to all
`@sunlife.com` users on 2026-09-11 as a stopgap — Luminate grants nothing on first login). Without
it a member cannot see the shared, platform-owned models they will write access policies against.

### FR-5: Handover

Portal and gateway addresses come from the devkit registry (`deployments.json`), never derived
from each other, and the gateway is re-probed for **401** on every proxy prefix before the
message is sent.

### FR-6: First governed call

One CoArchitect agent, registered and deployed in `CoArchitect`, calls one approved model via
the Dev gateway with a Luminate-issued client credential, and propagates
`x-luminate-session-id` so the run is correlatable.

## Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Security | Least privilege: Editors hold no delete, credential, policy or IAM rights | Proven by Rego decision |
| NFR-2 | Security | Workload credential never in source control or a literal env file | Vault / Secrets Manager only |
| NFR-3 | Auditability | Every provisioning write goes through the services (audit `rbac_binding_mutation`), never the ORM | 100% |
| NFR-4 | Operability | Provisioning runs in a one-off pod, never inside the serving backend container | Serving pod untouched |
| NFR-5 | Verifiability | Access proven at three levels plus a negative control | Rows, Rego, viewsets |

## Data Model Requirements

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| Folder | `Enterprise Architecture` | parent of project |
| Project | `CoArchitect`, owner, `cost_centre` (T6) | owns every CoArchitect resource |
| RoleBinding | role, grantee (user), scope (project), `scope_tokens` | 1 Owner, 1 Administrator, 2 Editor |

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Partho signs in for the first time | allauth connects the SSO account to the pre-created row; bindings already apply |
| A member sees a button and the action fails | Normal: the portal does not hide actions the user lacks; it is a missing grant, not a bug |
| Editor tries to generate credentials | Denied by design — Owner or Administrator does it |
| Team points a client at the portal host instead of the gateway | `/llm/...` on the portal returns 200 with the SPA index, not a gateway 401 — the tell |

## Constraints

- **Dev install only.** The dev install's `SIT` environment has no public gateway address and its
  `Prod` environment is not production. Only **Dev** is callable from outside the cluster.
- Registered resources cannot move between projects; once deployed they cannot be deleted.

## Capability Gaps

| Capability | What is missing | Classification | Impact on this use case | Escalation |
|---|---|---|---|---|
| CAP-12 | No counter store; nothing debits a quota; no spend dimension | Component change | Degrades — cost visible, not capped | Platform P0, not caused by this use case |
| CAP-18 | No external-producer audit path | Component change | Workaround — only gateway-carried calls are audited | Platform gap register |

| Gap | Interim measure | Removed when |
|---|---|---|
| CAP-12 | Cost reported per project via chargeback; thresholds watched, not enforced | CAP-12 reaches ✅ |

## Traceability

| Requirement | Capability | D0 Success Criteria | D3 Task |
|-------------|-----------|-------------------|---------|
| FR-1, FR-2, FR-3, FR-4 | CAP-05, CAP-07 | SC-1 | T1 |
| US-3 | CAP-05 | SC-2 | T2 |
| FR-5 | CAP-21 | SC-2 | T3 |
| — | all selected | SC-3 | T4 |
| FR-6, US-4 | CAP-01, CAP-02, CAP-06, CAP-08, CAP-18, CAP-20 | SC-4 | T9–T12 |
