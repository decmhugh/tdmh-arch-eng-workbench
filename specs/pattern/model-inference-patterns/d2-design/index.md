# D2 — Design

> **Gate**: D2 | **Status**: Draft | **Epic**: [EACPP-1320](https://sunlife.atlassian.net/browse/EACPP-1320)

The design is split by the question it answers. Read [Topology](topology.md) first — every other page
depends on which shape is chosen.

| Page | Answers |
|---|---|
| [Topology](topology.md) | Where the call executes, and why centralized is the target |
| [Provider portability](provider-portability.md) | Changing provider without changing a workload |
| [Attribution](attribution.md) | Who pays, and how the number reaches finance |
| [Budgets](budgets.md) | How spend is limited, and what a business owner is promised |
| [Model access](model-access.md) | Who may call which model, in which region, for which project |
| [Operations](operations.md) | Running it — reconciliation, review, incident response |
| [Assurance](assurance.md) | The ETAB architecture, design decisions, threats and the ISRA control set |
| [Dependencies](gaps.md) | What the target state requires from the platform, and who owns each |

## The design in one paragraph

Inference executes **in the ACP production workload account, through the gateway serving the
workload's environment and region** — one gateway per environment per region, per
`gateway-environment-strategy` DD-3. The workload names a model and holds no provider credential;
which provider serves it, in which account and which region, are platform decisions resolved through
the catalogue. That indirection is the point: it is what lets Sun Life present **aggregate volume**
to a provider and what makes the **provider replaceable** without touching a single workload.
Aggregating the bill is only safe if it stays decomposable, so attribution runs to a daily ledger at
`(project, entity, user, model, provider)` grain carrying a **cost centre**, reconciled against the
provider invoice before anything is charged, and delivered into the enterprise chargeback pipeline
finance already runs. Spend is bounded by **budgets enforced at the call** — soft-warn, then
hard-cap — bound to a project, team, entity or user, and kept distinct from both the access decision
and the kill path. Model access is a default-deny grant binding a source to a model, scoped by
project and region.

## What is decided here

- **Centralized inference is the target state** — the only shape serving a workload with no cloud
  account, and the one that makes inference commercially negotiable and provider-portable. This
  discharges [`integration-patterns`](../../../platform/integration-patterns/d3-tasks.md) **T16**.
- **Attribution is a precondition of the offer**, not a follow-up — an aggregated bill that cannot
  be decomposed is a liability rather than leverage.
- **The project is the billing unit**; directory groups govern access, projects govern billing.
- **Spend is refused, not reported** — budgets enforce at the call.
- ACP **feeds** the enterprise chargeback pipeline; it does not build a competing finance surface.
- Distributed execution **remains supported** for teams that already have a cloud account.
