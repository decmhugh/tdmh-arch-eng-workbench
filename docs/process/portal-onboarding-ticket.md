# Ticket template — Onboard a team to the Luminate portal

> Copy this into the D3 task row and the Jira ticket for **the first task of any onboarding
> spec**. Fill every `{placeholder}`; a request missing the *where* or the *why* is bounced
> before any work starts.
>
> The ACP Product Team runs it with the
> [`onboard-team-to-luminate`](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-devkit/browse/.github/skills/onboard-team-to-luminate/SKILL.md)
> skill in `acp-product-devkit`. Worked example:
> [CoArchitect D3 T1](../specs/onboarding/coarchitect-onboarding/d3-tasks.md).

## D3 task row

Paste as **T1**. Every later task — registration, access policy, credential, first call —
depends on it.

```markdown
| **T1** | Onboard the {Team} project team to the Luminate {install} portal. Create folder {Folder} and project {Project} with {Owner} as Owner, grant {Name} {Role} [and …] on the project, pre-provision anyone who has never signed in, and prove the access at row, decision and viewset level with a negative control | Story | 1 | S1 | — |
```

## Jira ticket

**Summary**: `T1: Onboard the {Team} project team to the Luminate {install} portal`
**Type**: Story · **Points**: 1 · **Assignee**: ACP Product Team · **Epic**: the spec's epic

### Request

| Field | Value |
|---|---|
| Install | {dev \| prod} — Luminate *install*, not a workload environment (see note 1) |
| Folder | {Folder} — business area; {exists \| create} |
| Project | {Project} — named after the team or product, never one resource |
| Owner | {Name} `{email}` |
| Why | {One line: what the team will register — agents, models, MCP servers — and the spec link} |

| Person | Email | Role on project | Signed in before? |
|---|---|---|---|
| {Name} | `{email}` | Owner | {yes \| no} |
| {Name} | `{email}` | {Administrator \| Editor \| Viewer \| per-type Administrator} | {yes \| no} |

### Choosing roles

| Ask from the team | Grant | Not |
|---|---|---|
| "Owns it, adds teammates" | **Owner** — only role that grants inside the project | Owner *plus* an Administrator role — Owner already covers it |
| "Does all the development work" | **Administrator** at project scope — the only non-Owner role that can write access policies | the per-type Administrators, which cannot |
| "Builds things" | **Editor** — create and deploy; no delete, credentials, access policy or IAM | |
| "Needs to see it" | **Viewer** | |

Grant to **individuals**. An Owner cannot manage group membership, so a group sends every
future joiner back to the ACP Product Team.

### Steps

1. Confirm the folder, project and environment names exist or are new — ask for exact names,
   never infer from a screenshot.
2. Write the request JSON (the skill's `request.example.json` shape) and keep it in the spec's
   `references/`.
3. Re-check `SOCIALACCOUNT_EMAIL_AUTHENTICATION` and `…_AUTO_CONNECT` are both `True` before
   pre-provisioning anyone who has never signed in.
4. Dry run `provision_team.py`, read the plan, then apply — from a **one-off pod**, not the
   serving backend container.
5. Run `verify_access.py` with a negative control.
6. Render the handover with `onboarding_message.py --verify` and send it.

### Acceptance criteria

- [ ] Folder and project exist; the Owner is shown on the project.
- [ ] One `RoleBinding` per person at **project** scope — none at folder or organization scope.
- [ ] Rego decisions match the role table: Owner/Administrator ALLOW on create, credentials,
      access policy and IAM; Editor ALLOW on create, deny on the rest.
- [ ] The real viewsets, driven as each member, list the project.
- [ ] Negative control (a user with no binding) is denied every write and does not see the project.
- [ ] Handover sent; `--verify` returned 401 on every gateway prefix.
- [ ] Anyone pre-provisioned has a follow-up task to confirm first sign-in hit the same account.

### Evidence to attach

- The applied request JSON
- `provision_team.py` output (ids created, or `EXISTS`)
- `verify_access.py` output — all three levels and the negative control
- The handover message as sent

## Notes

1. **Install vs environment.** The *dev install* is its own cluster with its own portal and
   gateway. The *DEV workload environment* on the prod install is something else. Say which one
   the team got.
2. **Project placement is permanent in practice.** A registered resource cannot move between
   projects, and once deployed cannot be deleted.
3. **Out of scope for this ticket**: registering resources, access policies, credentials and
   production onboarding — each is its own later task.
