# Model access — who may call which model, where, and for what

The governance question asked directly: *what agents can call what models, what models are available
in what regions, what models can be used per project.* This page answers all three.

## The mechanism

A grant is an `AccessPolicy` binding a **source** to a **target**, scoped to a project.

| Axis | Values |
|---|---|
| **Source** — who may call | `agent`, `application`, **`user`**, **`user_group`**, `mcp_server`, `all_users`, `location`, `environment` |
| **Target** — what may be called | **`model`**, `agent`, `mcp_server`, `location`, `environment` |
| **Region** | Carried by the offering: identity is `(model, provider, region)`, enforced by the `unique_offering_per_region` DB constraint |
| **Project** | Materialized-path scope tokens `<scope_type>:<id>` on the policy |

Default is deny: a caller reaches only the models a policy names.

## Design positions

### Grant to the smallest true thing (MIR-28)

Sources are ordered by how much they over-grant:

```
user_group  ⊂  application / agent  ⊂  all_users
```

- **An agent or application** is the right source when the caller is a system. The grant then
  describes a capability of that system, and survives staff changes.
- **A user group** is the right source when the caller is a person. Membership changes with the
  directory; access follows without a policy edit. This is why human access is granted through
  groups rather than to individuals — a joiner or leaver is a directory event, not a policy change.
- **`all_users`** should not appear on a model target. It is convenient during a pilot and it is
  indistinguishable, afterwards, from having no policy at all.

### Human access flows through the group, billing flows through the project

Stated here as well as in [Attribution](attribution.md) because it is the single place these two
governance axes are most often conflated:

| Question | Authority |
|---|---|
| May this person call this model? | Their **directory group** |
| Who pays for it? | Their **project**, which carries the cost centre |

Using directory groups for both creates two sources of truth for "who pays", with no tiebreak when
they disagree. Keeping them separate means each mechanism answers one question, and every answer has
one owner.

### Region is a residency decision, recorded (MIR-30)

With distributed inference, the consumer's own account and region carry the residency posture.
**Centralized routing means ACP chooses the region on the consumer's behalf**, which makes it a
decision ACP is accountable for.

The offering's `region` names where the call goes, and the gateway serving a workload is itself
per-environment and per-region. MIR-30 requires the region and its residency rationale to be
recorded at onboarding rather than inferred later from a trace.

### Project scoping (MIR-31)

A model restricted to particular work is scoped by the policy's project tokens. This is the right
lever for *"what models can be used per project"*, and it composes with region: a model may be
available in one region for one project and nowhere else.

### Approval status governs availability (MIR-32)

A model that is not approved for a data classification must not be reachable by a workload handling
that data. This is where model governance meets the risk assessment, and it is the reason the
catalogue and the policy store cannot be allowed to drift apart — a model withdrawn from approval
but left reachable is an open path with a closed record.

### Withdrawal is governed (MIR-33)

Removing a model is a caller-affecting change. It needs a migration path and a notification, not a
silent catalogue edit. Callers fail closed, which is correct and also indistinguishable from an
outage if nobody was told.

## What centralization changes here

Less than might be expected, which is the good news of this page.

| | Distributed | Centralized |
|---|---|---|
| Who decides which models exist | Partly the consumer's account | **ACP, entirely** |
| Who decides the region | The consumer | **ACP, on their behalf** |
| Policy mechanism | Same | Same |
| Catalogue | Same | Same |

Centralization concentrates the **decisions**, not the mechanism. The catalogue and policy model do
not change; what changes is that ACP now owns choices — which models, in which regions — that were
previously distributed along with the accounts. That is an accountability shift, and MIR-30 and
MIR-32 exist to make it a recorded one.

## Review

MIR-34 asks for a periodic review in which **a grant with no traffic in the period is challenged**.
The usage ledger makes this cheap: join live policies against `ProjectUsageDaily` and the grants
nobody used are immediately visible. Unused grants are the ordinary way an access model decays, and
this is the one place where the cost work pays a governance dividend rather than the other way
round.
